#!/usr/bin/env python3
"""Thin CLI adapter for Obsidian's Simple Mind Map plugin."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_VAULT = "obsidian"
DEFAULT_ROOT = Path("/Users/sunx/Dropbox/syncer/apps/obsidian")


COMMON_JS = r"""
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
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
const findOpenLeaf = path => {
  let found = null;
  app.workspace.iterateAllLeaves(leaf => {
    if (!found && leaf.view?.file?.path === path && leaf.view?.mindMapAPP) found = leaf;
  });
  return found;
};
const openSmm = async path => {
  getPlugin();
  if (!path.endsWith(".smm.md")) throw new Error("Expected a .smm.md path");
  const file = app.vault.getFileByPath(path);
  if (!file) throw new Error(`File not found in vault: ${path}`);
  let leaf = findOpenLeaf(path);
  if (!leaf) {
    leaf = app.workspace.getLeaf("tab");
    await leaf.openFile(file);
  }
  const view = await waitValue(
    () => leaf.view?.mindMapAPP?.$bus && leaf.view,
    "Simple Mind Map view"
  );
  if (typeof view.save !== "function" || typeof view.forceSaveAndUpdateImage !== "function") {
    throw new Error("Simple Mind Map save interface is unavailable");
  }
  return { file, leaf, view };
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
    normalized = path.as_posix().lstrip("./")
    if not normalized or normalized.startswith("../"):
        raise SystemExit(f"Invalid vault path: {raw}")
    return normalized


def clean_result_output(output: str) -> str:
    output = output.strip()
    return output[2:].lstrip() if output.startswith("=>") else output


def run_eval(vault: str, body: str) -> str:
    executable = shutil.which("obsidian")
    if not executable:
        raise SystemExit("Obsidian CLI is not on PATH")
    code = (
        f"(async()=>{{try{{{COMMON_JS}\n{body}}}catch(error){{"
        "return JSON.stringify({__smm_error__: error?.stack || String(error)});}})()"
    )
    result = subprocess.run(
        [executable, "eval", f"vault={vault}", f"code={code}"],
        text=True,
        capture_output=True,
        check=False,
    )
    stderr = "\n".join(
        line for line in result.stderr.splitlines() if "Unable to find helper app" not in line
    ).strip()
    output = clean_result_output(result.stdout)
    if result.returncode or not output:
        detail = stderr or "Obsidian returned no result; make sure the app is running"
        raise SystemExit(detail)
    try:
        payload = json.loads(output)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict) and payload.get("__smm_error__"):
        raise SystemExit(payload["__smm_error__"])
    if stderr:
        print(stderr, file=sys.stderr)
    return output


def wait_for_write(path: Path, before: int, timeout: float = 20) -> None:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if path.exists() and path.stat().st_mtime_ns > before:
            return
        time.sleep(0.1)
    raise SystemExit(f"Plugin did not save the file within {timeout:g}s: {path}")


def probe(vault: str) -> str:
    return run_eval(
        vault,
        """
const plugin = getPlugin();
return JSON.stringify({
  ok: true,
  plugin: plugin.manifest?.id,
  version: plugin.manifest?.version,
  markdownTransform: typeof plugin._mdToMindmapData === "function"
});
""",
    )


def read_map(vault: str, path: str) -> str:
    return run_eval(
        vault,
        f"""
const {{ view }} = await openSmm({js_value(path)});
const data = await currentData(view);
return JSON.stringify({{path: {js_value(path)}, layout: data.layout, theme: data.theme, nodes: walkNodes(data)}});
""",
    )


def convert_md(vault: str, root: Path, path: str) -> str:
    source = root / path
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
setTimeout(async () => {{
  const leaf = app.workspace.getLeaf("tab");
  await leaf.openFile(file);
  const view = await waitValue(() => typeof leaf.view?.onPaneMenu === "function" && leaf.view, "Markdown view");
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
  const converting = convertItem.click();
  const createButton = await waitValue(() => [...document.querySelectorAll(".modal-container button")].find(button =>
    button.textContent?.trim() === plugin._t("action.createConvert")
  ), "Create convert button");
  createButton.click();
  await converting;
}}, 200);
return JSON.stringify({{scheduled: true}});
""",
    )
    end = time.monotonic() + 20
    while time.monotonic() < end:
        created = [item for item in source.parent.glob(pattern) if item not in before and item.stat().st_size]
        if len(created) == 1:
            return json.dumps(
                {"source": path, "path": created[0].relative_to(root).as_posix()}, ensure_ascii=False
            )
        time.sleep(0.1)
    raise SystemExit(f"Plugin did not create a converted .smm.md file within 20s: {source}")


def edit_map(
    vault: str, root: Path, path: str, action: str, uid: str, text: str | None, preview: bool
) -> str:
    file_path = root / path
    before_nodes = json.loads(read_map(vault, path))["nodes"]
    before_by_uid = {node["uid"]: node for node in before_nodes}
    target = before_by_uid.get(uid)
    if not target:
        raise SystemExit(f"Node UID not found: {uid}")
    if target["free"]:
        raise SystemExit("Free-node editing is not supported")
    if action == "delete" and target["parentUid"] is None:
        raise SystemExit("Refusing to delete the root node")
    if action == "add-sibling" and target["parentUid"] is None:
        raise SystemExit("The root node cannot have a sibling")
    before_write = file_path.stat().st_mtime_ns
    run_eval(
        vault,
        f"""
const {{ view }} = await openSmm({js_value(path)});
const action = {js_value(action)};
const uid = {js_value(uid)};
const text = {js_value(text)};
setTimeout(() => view.mindMapAPP.$bus.$emit("execCommand", "GO_TARGET_NODE", uid, node => {{
    const bus = view.mindMapAPP.$bus;
    if (action === "set-text") bus.$emit("execCommand", "SET_NODE_TEXT", node, text, false);
    else if (action === "delete") bus.$emit("execCommand", "REMOVE_NODE", [node]);
    else if (action === "add-child") bus.$emit("execCommand", "INSERT_CHILD_NODE", false, [node], {{text}});
    else if (action === "add-sibling") bus.$emit("execCommand", "INSERT_NODE", false, [node], {{text}});
    setTimeout(() => bus.$emit("saveToLocal", true, {js_value(preview)}), 500);
  }}), 200);
return JSON.stringify({{scheduled: true}});
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


def save_map(vault: str, root: Path, path: str) -> str:
    file_path = root / path
    before_write = file_path.stat().st_mtime_ns
    output = run_eval(
        vault,
        f"""
const {{ file, view }} = await openSmm({js_value(path)});
setTimeout(() => view.mindMapAPP.$bus.$emit("saveToLocal", true, true), 500);
return JSON.stringify({{path: {js_value(path)}, saved: true, previewUpdated: true}});
""",
    )
    wait_for_write(file_path, before_write)
    return output


def self_test(root: Path) -> str:
    expected = "notes/投资/脑图.smm.md"
    assert normalize_path(str(root / expected), root) == expected
    assert normalize_path(expected, root) == expected
    assert js_value("新节点") == '"新节点"'
    assert "getMindMapCurrentData" in COMMON_JS
    assert clean_result_output('=> {"ok":true}') == '{"ok":true}'
    return json.dumps({"ok": True, "tests": 5})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", default=DEFAULT_VAULT)
    parser.add_argument("--vault-root", type=Path, default=DEFAULT_ROOT)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("probe")
    sub.add_parser("self-test")
    for name in ("read", "convert-md", "save"):
        command = sub.add_parser(name)
        command.add_argument("path")
    for name in ("add-child", "add-sibling", "set-text"):
        command = sub.add_parser(name)
        command.add_argument("path")
        command.add_argument("uid")
        command.add_argument("text")
        command.add_argument("--no-preview", action="store_true")
    command = sub.add_parser("delete")
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
    if args.command == "probe":
        print(probe(args.vault))
        return
    path = normalize_path(args.path, root)
    if args.command == "read":
        output = read_map(args.vault, path)
    elif args.command == "convert-md":
        output = convert_md(args.vault, root, path)
    elif args.command == "save":
        output = save_map(args.vault, root, path)
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
