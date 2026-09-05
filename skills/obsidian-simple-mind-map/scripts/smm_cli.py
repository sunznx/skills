#!/usr/bin/env python3
"""Thin CLI adapter for Obsidian's Simple Mind Map plugin."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path


DEFAULT_VAULT = "obsidian"
DEFAULT_ROOT = Path("/Users/sunx/Dropbox/syncer/apps/obsidian")
LOCKED_COMMANDS = {
    "read",
    "convert-md",
    "save",
    "add-child",
    "add-sibling",
    "set-text",
    "set-link",
    "delete",
}


COMMON_JS = r"""
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const waitPromise = (promise, label, timeout = 20000) => Promise.race([
  promise,
  sleep(timeout).then(() => { throw new Error(`Timed out waiting for ${label}`); })
]);
const waitValue = async (fn, label, timeout = 10000) => {
  const end = Date.now() + timeout;
  while (Date.now() < end) {
    const value = fn();
    if (value) return value;
    await sleep(100);
  }
  throw new Error(`Timed out waiting for ${label}`);
};
const getPlugin = () => {
  const plugin = app.plugins.getPlugin("simple-mind-map");
  if (!plugin) throw new Error("simple-mind-map plugin is not enabled");
  return plugin;
};
const openMindMapLeaves = path => {
  const leaves = [];
  app.workspace.iterateAllLeaves(leaf => {
    if (leaf.view?.file?.path === path && leaf.view?.mindMapAPP) leaves.push(leaf);
  });
  return leaves;
};
const openSmm = async (path, write = false) => {
  getPlugin();
  if (!path.endsWith(".smm.md")) throw new Error("Expected a .smm.md path");
  const file = app.vault.getFileByPath(path);
  if (!file) throw new Error(`File not found in vault: ${path}`);
  const existing = openMindMapLeaves(path);
  if (write && existing.length) {
    throw new Error(`Close the ${existing.length} open Simple Mind Map view(s) before writing: ${path}`);
  }
  const leaf = app.workspace.getLeaf("tab");
  openedLeaves.push(leaf);
  await waitPromise(leaf.openFile(file), `opening ${path}`);
  const view = await waitValue(
    () => leaf.view?.file?.path === path && leaf.view?.mindMapAPP?.$bus && leaf.view,
    `fresh Simple Mind Map view for ${path}`
  );
  if (typeof view.save !== "function" || typeof view.forceSaveAndUpdateImage !== "function") {
    throw new Error("Simple Mind Map save interface is unavailable");
  }
  return { file, leaf, view };
};
const targetNode = async (view, uid) => new Promise((resolve, reject) => {
  let settled = false;
  const finish = node => {
    if (settled) return;
    settled = true;
    node ? resolve(node) : reject(new Error(`Node UID not found: ${uid}`));
  };
  view.mindMapAPP.$bus.$emit("execCommand", "GO_TARGET_NODE", uid, finish);
  setTimeout(() => {
    if (settled) return;
    settled = true;
    reject(new Error(`Timed out locating node UID: ${uid}`));
  }, 2500);
});
const saveView = async (view, file, preview = true) => {
  const before = file.stat?.mtime || 0;
  await sleep(500);
  view.mindMapAPP.$bus.$emit("saveToLocal", true, preview);
  await waitValue(() => file.stat?.mtime > before, `save for ${file.path}`, 20000);
};
const currentData = async view => {
  if (view.getMindMapCurrentDataResolve) throw new Error("Mind map is already saving");
  await new Promise((resolve, reject) => {
    let settled = false;
    const done = () => {
      if (settled) return;
      settled = true;
      resolve();
    };
    view.getMindMapCurrentDataResolve = done;
    view.mindMapAPP.$bus.$emit("getMindMapCurrentData");
    setTimeout(() => {
      if (settled) return;
      settled = true;
      if (view.getMindMapCurrentDataResolve === done) view.getMindMapCurrentDataResolve = null;
      reject(new Error("Plugin did not return current mind-map data"));
    }, 2500);
  });
  const content = view.parsedMindMapData?.metadata?.content;
  if (!content) throw new Error("Current mind-map metadata is empty");
  return JSON.parse(content);
};
const walkNodes = data => {
  const nodes = [];
  const plainText = value => {
    const element = document.createElement("div");
    element.innerHTML = String(value || "");
    return element.textContent || "";
  };
  const walk = (node, parentUid = null, depth = 0, free = false) => {
    if (!node?.data) return;
    nodes.push({
      uid: node.data.uid || null,
      text: node.data.text || "",
      plainText: plainText(node.data.text),
      hyperlink: node.data.hyperlink || "",
      hyperlinkTitle: node.data.hyperlinkTitle || "",
      richText: node.data.richText === true,
      fontFamily: node.data.fontFamily || "",
      parentUid,
      depth,
      childCount: (node.children || []).length,
      free
    });
    (node.children || []).forEach(child => walk(child, node.data.uid || null, depth + 1, free));
  };
  walk(data.root);
  (data.root?.data?.freeNodeTrees || []).forEach(node => walk(node, null, 0, true));
  return nodes;
};
"""


def js_value(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def normalize_path(raw: str, root: Path) -> str:
    path = Path(raw).expanduser()
    if path.is_absolute():
        try:
            path = path.resolve().relative_to(root.resolve())
        except ValueError as error:
            raise SystemExit(f"Absolute path is outside vault root {root}: {raw}") from error
    elif ".." in path.parts:
        raise SystemExit(f"Invalid vault path: {raw}")
    normalized = path.as_posix()
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if not normalized or normalized == ".":
        raise SystemExit(f"Invalid vault path: {raw}")
    return normalized


def lock_path(root: Path) -> Path:
    digest = hashlib.sha256(str(root.resolve()).encode()).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / f"obsidian-simple-mind-map-{digest}.lock"


def clean_result_output(output: str) -> str:
    output = output.strip()
    return output[2:].lstrip() if output.startswith("=>") else output


def run_eval(vault: str, body: str) -> str:
    executable = shutil.which("obsidian")
    if not executable:
        raise SystemExit("Obsidian CLI is not on PATH")

    def invoke(code: str) -> tuple[str, str]:
        result = subprocess.run(
            [executable, "eval", f"vault={vault}", f"code={code}"],
            text=True,
            capture_output=True,
            check=False,
        )
        stderr = "\n".join(
            line
            for line in result.stderr.splitlines()
            if "Unable to find helper app" not in line
        ).strip()
        if result.returncode:
            raise SystemExit(stderr or f"Obsidian CLI exited with code {result.returncode}")
        return clean_result_output(result.stdout), stderr

    operation_id = uuid.uuid4().hex
    key = js_value(operation_id)
    code = f"""
(()=>{{
  const key = {key};
  const operations = globalThis.__smmCliOperations ||= {{}};
  operations[key] = {{status: "running"}};
  (async()=>{{
    const openedLeaves = [];
    try {{
      {COMMON_JS}
      {body}
    }} finally {{
      openedLeaves.forEach(leaf => {{ try {{ leaf.detach(); }} catch {{}} }});
    }}
  }})().then(
    result => operations[key] = {{status: "done", result}},
    error => operations[key] = {{status: "error", error: error?.stack || String(error)}}
  );
  return JSON.stringify({{status: "started"}});
}})()
"""
    output, stderr = invoke(code)
    if output and json.loads(output).get("status") != "started":
        raise SystemExit(f"Unexpected Obsidian launch response: {output}")
    deadline = time.monotonic() + 120
    poll_code = f"""
(()=>{{
  const operations = globalThis.__smmCliOperations || {{}};
  const operation = operations[{key}];
  if (!operation) return JSON.stringify({{status: "missing"}});
  if (operation.status !== "running") delete operations[{key}];
  return JSON.stringify(operation);
}})()
"""
    while time.monotonic() < deadline:
        time.sleep(0.1)
        polled, poll_stderr = invoke(poll_code)
        stderr = poll_stderr or stderr
        if not polled:
            continue
        payload = json.loads(polled)
        if payload["status"] == "running":
            continue
        if payload["status"] == "error":
            raise SystemExit(payload["error"])
        if payload["status"] == "done":
            if stderr:
                print(stderr, file=sys.stderr)
            result = payload.get("result")
            return result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
        raise SystemExit("Obsidian lost the queued mind-map operation")
    raise SystemExit("Timed out waiting for the queued Obsidian operation")


def wait_for_write(path: Path, before: int, timeout: float = 20) -> None:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if path.exists() and path.stat().st_mtime_ns > before:
            return
        time.sleep(0.1)
    raise SystemExit(f"Plugin did not save the file within {timeout:g}s: {path}")


def probe(vault: str, root: Path) -> str:
    output = run_eval(
        vault,
        """
const plugin = getPlugin();
return JSON.stringify({
  ok: true,
  plugin: plugin.manifest?.id,
  version: plugin.manifest?.version,
  markdownTransform: typeof plugin._mdToMindmapData === "function",
  vaultRoot: app.vault.adapter.getBasePath?.() || app.vault.adapter.basePath || ""
});
""",
    )
    actual = json.loads(output).get("vaultRoot")
    if not actual or Path(actual).resolve() != root.resolve():
        raise SystemExit(f"Vault root mismatch: CLI {actual!r}, --vault-root {str(root.resolve())!r}")
    return output


def read_map(vault: str, path: str) -> str:
    return run_eval(
        vault,
        f"""
const {{ view }} = await openSmm({js_value(path)});
const data = await currentData(view);
return JSON.stringify({{path: {js_value(path)}, layout: data.layout, theme: data.theme, nodes: walkNodes(data)}});
""",
    )


def apply_default_font(vault: str, root: Path, path: str) -> dict[str, object]:
    file_path = root / path
    before_write = file_path.stat().st_mtime_ns
    output = run_eval(
        vault,
        f"""
const {{ file, view }} = await openSmm({js_value(path)}, true);
const configuredFont = app.vault.config?.textFontFamily?.trim();
const fontFamily = configuredFont || getComputedStyle(document.body).getPropertyValue("--font-text").trim();
if (!fontFamily) throw new Error("Obsidian default text font is unavailable");
const nodes = walkNodes(await currentData(view));
const bus = view.mindMapAPP.$bus;
for (const item of nodes) {{
  const node = await targetNode(view, item.uid);
  bus.$emit("execCommand", "SET_NODE_STYLE", node, "fontFamily", fontFamily);
}}
await saveView(view, file, true);
return JSON.stringify({{fontFamily, nodeCount: nodes.length}});
""",
    )
    wait_for_write(file_path, before_write)
    nodes = json.loads(read_map(vault, path))["nodes"]
    result = json.loads(output)
    if any(node["fontFamily"] != result["fontFamily"] for node in nodes):
        raise SystemExit("Default-font verification failed")
    return result


def convert_md(vault: str, root: Path, path: str, delete_source: bool = False) -> str:
    source = root / path
    try:
        pattern = f"{source.stem}*.smm.md"
        before = set(source.parent.glob(pattern))
        run_eval(
            vault,
            f"""
const plugin = getPlugin();
const path = {js_value(path)};
if (!path.endsWith(".md") || path.endsWith(".smm.md")) throw new Error("Expected a Markdown source path");
const file = app.vault.getFileByPath(path);
if (!file) throw new Error(`File not found in vault: ${{path}}`);
const leavesBefore = new Set();
app.workspace.iterateAllLeaves(leaf => leavesBefore.add(leaf));
const leaf = app.workspace.getLeaf("tab");
openedLeaves.push(leaf);
await waitPromise(leaf.openFile(file), `opening ${{path}}`);
const view = await waitValue(
  () => leaf.view?.file?.path === path && typeof leaf.view?.onPaneMenu === "function" && leaf.view,
  `fresh Markdown view for ${{path}}`
);
const items = [];
let menu;
menu = new Proxy({{}}, {{get: (_target, key) => {{
  if (key === "addItem") return callback => {{
    const state = {{}};
    let item;
    item = new Proxy(state, {{get: (target, method) => {{
      if (method === "setTitle") return value => (target.title = value, item);
      if (method === "onClick") return value => (target.click = value, item);
      return () => item;
    }}}});
    callback(item);
    items.push(state);
    return menu;
  }};
  return () => menu;
}}}});
view.onPaneMenu(menu, "more-options");
const convertItem = items.find(item => item.title === plugin._t("action.changeToMindMapFile"));
if (!convertItem?.click) throw new Error("Convert to mind map menu action is unavailable");
const existingModals = new Set(document.querySelectorAll(".modal-container"));
const converting = convertItem.click();
const modal = await waitValue(() => [...document.querySelectorAll(".modal-container")].find(container =>
  !existingModals.has(container) && [...container.querySelectorAll("button")].some(button =>
    button.textContent?.trim() === plugin._t("action.createConvert")
  )
), "Create convert modal");
const createButton = [...modal.querySelectorAll("button")].find(button =>
  button.textContent?.trim() === plugin._t("action.createConvert")
);
createButton.click();
await waitPromise(converting, `conversion of ${{path}}`);
await sleep(300);
const slash = path.lastIndexOf("/");
const directory = slash < 0 ? "" : path.slice(0, slash + 1);
const stem = path.slice(slash + 1, -3);
app.workspace.iterateAllLeaves(candidate => {{
  const candidatePath = candidate.view?.file?.path || "";
  if (!leavesBefore.has(candidate) && !openedLeaves.includes(candidate) &&
      candidatePath.startsWith(directory + stem) && candidatePath.endsWith(".smm.md")) {{
    openedLeaves.push(candidate);
  }}
}});
return JSON.stringify({{completed: true}});
""",
        )
        end = time.monotonic() + 20
        while time.monotonic() < end:
            created = [
                item
                for item in source.parent.glob(pattern)
                if item not in before and item.stat().st_size
            ]
            if len(created) == 1:
                converted_path = created[0].relative_to(root).as_posix()
                font = apply_default_font(vault, root, converted_path)
                return json.dumps(
                    {
                        "source": path,
                        "sourceDeleted": delete_source,
                        "path": converted_path,
                        **font,
                    },
                    ensure_ascii=False,
                )
            time.sleep(0.1)
        raise SystemExit(f"Plugin did not create a converted .smm.md file within 20s: {source}")
    finally:
        if delete_source:
            source.unlink(missing_ok=True)


def edit_map(
    vault: str, root: Path, path: str, action: str, uid: str, text: str | None, preview: bool
) -> str:
    file_path = root / path
    before_nodes = json.loads(read_map(vault, path))["nodes"]
    before_by_uid = {node["uid"]: node for node in before_nodes}
    target = before_by_uid.get(uid)
    if not target:
        raise SystemExit(f"Node UID not found: {uid}")
    if target["free"] and action != "delete":
        raise SystemExit("Free-node editing is not supported")
    if action == "delete" and target["parentUid"] is None and not target["free"]:
        raise SystemExit("Refusing to delete the root node")
    if action == "add-sibling" and target["parentUid"] is None:
        raise SystemExit("The root node cannot have a sibling")
    before_write = file_path.stat().st_mtime_ns
    run_eval(
        vault,
        f"""
const {{ file, view }} = await openSmm({js_value(path)}, true);
const action = {js_value(action)};
const uid = {js_value(uid)};
const text = {js_value(text)};
const node = await targetNode(view, uid);
const bus = view.mindMapAPP.$bus;
if (action === "set-text") bus.$emit("execCommand", "SET_NODE_TEXT", node, text, false);
else if (action === "delete") bus.$emit("execCommand", "REMOVE_NODE", [node]);
else if (action === "add-child") bus.$emit("execCommand", "INSERT_CHILD_NODE", false, [node], {{text}});
else if (action === "add-sibling") bus.$emit("execCommand", "INSERT_NODE", false, [node], {{text}});
await saveView(view, file, {js_value(preview)});
return JSON.stringify({{completed: true}});
""",
    )
    wait_for_write(file_path, before_write)
    after_nodes = json.loads(read_map(vault, path))["nodes"]
    after_by_uid = {node["uid"]: node for node in after_nodes}
    new_nodes = [node for node in after_nodes if node["uid"] not in before_by_uid]
    if action == "delete" and uid in after_by_uid:
        raise SystemExit("Delete verification failed")
    if action == "set-text" and after_by_uid.get(uid, {}).get("plainText") != text:
        raise SystemExit("Text verification failed")
    if action in {"add-child", "add-sibling"} and len(new_nodes) != 1:
        raise SystemExit("Could not identify exactly one new node")
    new_node = new_nodes[0] if new_nodes else None
    expected_parent = uid if action == "add-child" else target["parentUid"]
    if new_node and new_node["parentUid"] != expected_parent:
        raise SystemExit("New-node parent verification failed")
    return json.dumps(
        {"path": path, "action": action, "uid": uid, "newNode": new_node}, ensure_ascii=False
    )


def set_link(
    vault: str, root: Path, path: str, uid: str, url: str, title: str, preview: bool
) -> str:
    file_path = root / path
    before_nodes = json.loads(read_map(vault, path))["nodes"]
    before_by_uid = {node["uid"]: node for node in before_nodes}
    target = before_by_uid.get(uid)
    if not target:
        raise SystemExit(f"Node UID not found: {uid}")
    if target["free"]:
        raise SystemExit("Free-node editing is not supported")
    before_write = file_path.stat().st_mtime_ns
    run_eval(
        vault,
        f"""
const {{ file, view }} = await openSmm({js_value(path)}, true);
const uid = {js_value(uid)};
const url = {js_value(url)};
const title = {js_value(title)};
const node = await targetNode(view, uid);
const bus = view.mindMapAPP.$bus;
bus.$emit("execCommand", "SET_NODE_HYPERLINK", node, url, title);
bus.$emit("execCommand", "SET_NODE_DATA", node, {{richText: true}});
await saveView(view, file, {js_value(preview)});
return JSON.stringify({{completed: true}});
""",
    )
    wait_for_write(file_path, before_write)
    after_nodes = json.loads(read_map(vault, path))["nodes"]
    after = {node["uid"]: node for node in after_nodes}.get(uid)
    if (
        not after
        or after.get("hyperlink") != url
        or after.get("hyperlinkTitle") != title
        or not after.get("richText")
    ):
        raise SystemExit("Hyperlink verification failed")
    return json.dumps(
        {"path": path, "action": "set-link", "uid": uid, "node": after}, ensure_ascii=False
    )


def save_map(vault: str, root: Path, path: str) -> str:
    file_path = root / path
    before_write = file_path.stat().st_mtime_ns
    output = run_eval(
        vault,
        f"""
const {{ file, view }} = await openSmm({js_value(path)}, true);
await saveView(view, file, true);
return JSON.stringify({{path: {js_value(path)}, saved: true, previewUpdated: true}});
""",
    )
    wait_for_write(file_path, before_write)
    return output


def self_test(root: Path) -> str:
    expected = "notes/投资/脑图.smm.md"
    assert normalize_path(str(root / expected), root) == expected
    assert normalize_path(expected, root) == expected
    assert normalize_path(".hidden/map.smm.md", root) == ".hidden/map.smm.md"
    for invalid in ("../map.smm.md", "notes/../map.smm.md"):
        try:
            normalize_path(invalid, root)
        except SystemExit:
            pass
        else:
            raise AssertionError(f"Unsafe path accepted: {invalid}")
    assert js_value("新节点") == '"新节点"'
    assert "read" in LOCKED_COMMANDS
    assert lock_path(root) == lock_path(root)
    assert lock_path(root) != lock_path(root / "other")
    with lock_path(root).open("a") as first_lock, lock_path(root).open("a") as second_lock:
        fcntl.flock(first_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            fcntl.flock(second_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            pass
        else:
            raise AssertionError("Vault lock is not exclusive")
    assert "getMindMapCurrentData" in COMMON_JS
    assert clean_result_output('=> {"ok":true}') == '{"ok":true}'
    parser = build_parser()
    for argv in (
        ["--vault-root", str(root), "read", expected],
        ["read", expected, "--vault-root", str(root)],
    ):
        parsed = parser.parse_args(argv)
        assert parsed.vault_root == root
    parsed = parser.parse_args(["convert-md", "temporary.md", "--delete-source"])
    assert parsed.delete_source
    return json.dumps({"ok": True, "tests": 15})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", default=DEFAULT_VAULT)
    parser.add_argument("--vault-root", type=Path, default=DEFAULT_ROOT)
    sub = parser.add_subparsers(dest="command", required=True)

    def add_runtime_options(command: argparse.ArgumentParser) -> None:
        # Keep the options on the root parser for the documented
        # `--vault-root ... read FILE` form, and accept them after the
        # subcommand too. SUPPRESS prevents a subparser default from
        # overwriting a value parsed by the root parser.
        command.add_argument("--vault", default=argparse.SUPPRESS)
        command.add_argument("--vault-root", type=Path, default=argparse.SUPPRESS)

    command = sub.add_parser("probe")
    add_runtime_options(command)
    command = sub.add_parser("self-test")
    add_runtime_options(command)
    for name in ("read", "save"):
        command = sub.add_parser(name)
        add_runtime_options(command)
        command.add_argument("path")
    command = sub.add_parser("convert-md")
    add_runtime_options(command)
    command.add_argument("path")
    command.add_argument("--delete-source", action="store_true")
    for name in ("add-child", "add-sibling", "set-text"):
        command = sub.add_parser(name)
        add_runtime_options(command)
        command.add_argument("path")
        command.add_argument("uid")
        command.add_argument("text")
        command.add_argument("--no-preview", action="store_true")
    command = sub.add_parser("set-link")
    add_runtime_options(command)
    command.add_argument("path")
    command.add_argument("uid")
    command.add_argument("url")
    command.add_argument("title")
    command.add_argument("--no-preview", action="store_true")
    command = sub.add_parser("delete")
    add_runtime_options(command)
    command.add_argument("path")
    command.add_argument("uid")
    command.add_argument("--no-preview", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    root = args.vault_root.expanduser()
    if args.command == "self-test":
        print(self_test(root))
        return
    probe_output = probe(args.vault, root)
    if args.command == "probe":
        print(probe_output)
        return
    lock_file = None
    if args.command in LOCKED_COMMANDS:
        lock_file = lock_path(root).open("a")
        fcntl.flock(lock_file, fcntl.LOCK_EX)
    path = normalize_path(args.path, root)
    if args.command == "read":
        output = read_map(args.vault, path)
    elif args.command == "convert-md":
        output = convert_md(args.vault, root, path, args.delete_source)
    elif args.command == "save":
        output = save_map(args.vault, root, path)
    else:
        if args.command == "set-link":
            output = set_link(
                args.vault, root, path, args.uid, args.url, args.title, not args.no_preview
            )
        else:
            output = edit_map(
                args.vault,
                root,
                path,
                args.command,
                args.uid,
                getattr(args, "text", None),
                not args.no_preview,
            )
    print(output)


if __name__ == "__main__":
    main()
