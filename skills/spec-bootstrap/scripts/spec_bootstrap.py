#!/usr/bin/env python3
"""Install the global Codex agent workflow."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SERENA_SOURCE = "git+https://github.com/oraios/serena"
SERENA_HOOK = f"uvx -p 3.13 --from {SERENA_SOURCE} serena-hooks"
BLOCK_START = "# AGENT-WORKFLOW:START"
BLOCK_END = "# AGENT-WORKFLOW:END"
SERENA_CLIENT = re.compile(r"--client(?:=|\s+)codex(?:\s|$)")
PLUGINS = (
    ("ponytail", "DietrichGebert/ponytail", "ponytail@ponytail"),
    (
        "planning-with-files",
        "OthmanAdi/planning-with-files",
        "planning-with-files@planning-with-files",
    ),
)
SERENA_HOOKS = {
    "PreToolUse": [
        {
            "matcher": "Bash",
            "hooks": [
                {
                    "type": "command",
                    "command": f"{SERENA_HOOK} remind --client=codex",
                }
            ],
        }
    ],
    "SessionStart": [
        {
            "matcher": "startup|resume",
            "hooks": [
                {
                    "type": "command",
                    "command": f"{SERENA_HOOK} activate --client=codex",
                }
            ],
        }
    ],
    "SessionEnd": [
        {
            "hooks": [
                {
                    "type": "command",
                    "command": f"{SERENA_HOOK} cleanup --client=codex",
                }
            ]
        }
    ],
}


class InitError(RuntimeError):
    pass


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def codex_json(*args: str) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["codex", *args, "--json"],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise InitError("未找到 codex CLI，无法安装全局 plugins。") from exc
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise InitError(f"Codex plugin 命令失败：{detail}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise InitError(f"Codex plugin 返回了无效 JSON：{exc}") from exc
    if not isinstance(payload, dict):
        raise InitError("Codex plugin 返回格式不正确。")
    return payload


def ensure_plugins() -> list[str]:
    statuses: list[str] = []
    marketplaces = codex_json("plugin", "marketplace", "list").get("marketplaces", [])
    configured = {
        item.get("name")
        for item in marketplaces
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    for marketplace, source, _plugin in PLUGINS:
        if marketplace in configured:
            statuses.append(f"preserved Codex marketplace {marketplace}")
        else:
            codex_json("plugin", "marketplace", "add", source)
            statuses.append(f"added Codex marketplace {marketplace}")

    installed = codex_json("plugin", "list").get("installed", [])
    enabled = {
        item.get("pluginId")
        for item in installed
        if isinstance(item, dict) and item.get("enabled", True)
    }
    for _marketplace, _source, plugin in PLUGINS:
        if plugin in enabled:
            statuses.append(f"preserved Codex plugin {plugin}")
        else:
            codex_json("plugin", "add", plugin)
            statuses.append(f"installed Codex plugin {plugin}")
    return statuses


def managed_config(existing: str) -> str:
    stripped = re.sub(
        rf"(?:^|\n){re.escape(BLOCK_START)}\n.*?\n{re.escape(BLOCK_END)}(?=\n|$)",
        "",
        existing,
        flags=re.DOTALL,
    ).rstrip()
    sections: list[str] = []
    if not re.search(r"(?m)^\s*\[mcp_servers\.serena\]\s*$", stripped):
        sections.append(
            f"""[mcp_servers.serena]
command = "uvx"
args = [
  "-p", "3.13",
  "--from", "{SERENA_SOURCE}",
  "serena", "start-mcp-server",
  "--project-from-cwd",
  "--context=codex",
  "--language-backend", "LSP",
]
startup_timeout_sec = 120"""
        )
    if not re.search(r"(?m)^\s*\[mcp_servers\.semble\]\s*$", stripped):
        sections.append(
            """[mcp_servers.semble]
command = "uvx"
args = ["--from", "semble[mcp]", "semble"]
startup_timeout_sec = 120"""
        )
    if not sections:
        return stripped + ("\n" if stripped else "")
    block = f"{BLOCK_START}\n" + "\n\n".join(sections) + f"\n{BLOCK_END}"
    return f"{stripped}\n\n{block}\n" if stripped else f"{block}\n"


def is_serena_hook(item: dict[str, Any]) -> bool:
    command = item.get("command", "")
    return isinstance(command, str) and "serena-hooks" in command and bool(SERENA_CLIENT.search(command))


def merge_hooks(existing: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    hooks = dict(existing.get("hooks", {})) if isinstance(existing.get("hooks"), dict) else {}
    for event, groups in list(hooks.items()):
        if not isinstance(groups, list):
            continue
        kept_groups = []
        for group in groups:
            if not isinstance(group, dict):
                kept_groups.append(group)
                continue
            commands = group.get("hooks")
            if not isinstance(commands, list):
                kept_groups.append(group)
                continue
            kept = [item for item in commands if not (isinstance(item, dict) and is_serena_hook(item))]
            if kept:
                copy = dict(group)
                copy["hooks"] = kept
                kept_groups.append(copy)
        hooks[event] = kept_groups

    for event, groups in SERENA_HOOKS.items():
        hooks.setdefault(event, [])
        hooks[event].extend(groups)
    merged["hooks"] = hooks
    return merged


def write_if_changed(path: Path, content: str) -> str:
    current = path.read_text(encoding="utf-8") if path.is_file() else None
    if current == content:
        return "preserved"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "created" if current is None else "updated"


def install_global() -> list[str]:
    statuses = ensure_plugins()
    home = codex_home()

    config = home / "config.toml"
    config_text = config.read_text(encoding="utf-8") if config.is_file() else ""
    statuses.append(f"{write_if_changed(config, managed_config(config_text))} {config}")

    hooks_path = home / "hooks.json"
    try:
        existing_hooks = json.loads(hooks_path.read_text(encoding="utf-8")) if hooks_path.is_file() else {}
    except json.JSONDecodeError as exc:
        raise InitError(f"hooks JSON 格式错误：{exc}") from exc
    hooks_text = json.dumps(merge_hooks(existing_hooks), ensure_ascii=False, indent=2) + "\n"
    statuses.append(f"{write_if_changed(hooks_path, hooks_text)} {hooks_path}")
    return statuses


def main() -> int:
    if len(sys.argv) > 1:
        print("spec-bootstrap: 现在使用全局安装，不接受项目路径。", file=sys.stderr)
        return 1
    try:
        for line in install_global():
            print(line)
        print("next: start a new Codex session and review global plugins and hooks with /hooks")
    except InitError as exc:
        print(f"spec-bootstrap: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
