#!/usr/bin/env python3
"""Install the global Codex agent workflow."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


PLUGINS = (
    (
        "planning-with-files",
        "OthmanAdi/planning-with-files",
        "planning-with-files@planning-with-files",
    ),
)


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
            codex_json("plugin", "marketplace", "upgrade", marketplace)
            statuses.append(f"updated Codex marketplace {marketplace}")
        else:
            codex_json("plugin", "marketplace", "add", source)
            statuses.append(f"added Codex marketplace {marketplace}")

    marketplaces = codex_json("plugin", "marketplace", "list").get("marketplaces", [])
    planning = next(
        (
            item
            for item in marketplaces
            if isinstance(item, dict) and item.get("name") == "planning-with-files"
        ),
        None,
    )
    root = planning.get("root") if planning else None
    if not isinstance(root, str):
        raise InitError("未找到 Planning with Files marketplace checkout。")

    manifest_path = Path(root) / ".codex-plugin" / "plugin.json"
    try:
        original_manifest = manifest_path.read_bytes()
        manifest = json.loads(original_manifest)
    except FileNotFoundError as exc:
        raise InitError(f"未找到 Planning with Files plugin manifest：{manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise InitError(f"Planning with Files plugin manifest JSON 格式错误：{exc}") from exc

    manifest["commands"] = []
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    cache = codex_home() / "plugins" / "cache" / "planning-with-files"
    if cache.exists():
        shutil.rmtree(cache)
        statuses.append(f"removed {cache}")
    else:
        statuses.append(f"preserved {cache}")

    try:
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
    finally:
        manifest_path.write_bytes(original_manifest)
        statuses.append(f"restored {manifest_path}")
    return statuses


def install_global() -> list[str]:
    return ensure_plugins()


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
