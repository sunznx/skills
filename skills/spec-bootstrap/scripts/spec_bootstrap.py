#!/usr/bin/env python3
"""Install the project-local agent coding workflow."""

from __future__ import annotations

import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any


PWF_URL = "https://github.com/OthmanAdi/planning-with-files.git"
BLOCK_START = "# AGENT-WORKFLOW:START"
BLOCK_END = "# AGENT-WORKFLOW:END"
AGENTS_BLOCK_START = "<!-- agent-workflow:start -->"
AGENTS_BLOCK_END = "<!-- agent-workflow:end -->"
PWF_HANDLER = re.compile(
    r"\.codex[/\\]hooks[/\\](?:pwf_session_router\.py|run_sh\.py|pre_tool_use\.py|post_tool_use\.py|permission_request\.py|stop\.py)"
)


class InitError(RuntimeError):
    pass


def replace_block(text: str, start: str, end: str, block: str) -> str:
    pattern = re.compile(rf"(?:^|\n){re.escape(start)}\n.*?\n{re.escape(end)}(?=\n|$)", re.DOTALL)
    clean = pattern.sub("", text).rstrip()
    return f"{clean}\n\n{block.rstrip()}\n" if clean else f"{block.rstrip()}\n"


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
            """[mcp_servers.serena]
command = "uvx"
args = [
  "-p", "3.13",
  "--from", "git+https://github.com/oraios/serena",
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


def managed_agents(existing: str) -> str:
    lines = existing.splitlines()
    if lines and lines[0].strip() == "@AGENTS.md":
        remainder = "\n".join(lines[1:]).lstrip()
    else:
        remainder = existing.strip()
    block = f"""{AGENTS_BLOCK_START}
## Agent 编码工作流

- 复杂任务使用 `$planning-with-files` 创建和维护项目计划。
- 以 `task_plan.md` 为权威，并用 `update_plan` 完整镜像步骤和状态。
- 每个 session 开始时使用 Serena 激活当前项目并读取初始指引；若 hook 已完成则不要重复。
- 使用 Serena 做符号级代码阅读、定位和修改；使用 Semble 做自然语言或概念搜索。
- Semble 返回路径和行号后直接阅读目标代码，不要对同一内容重复搜索；仅在需要全仓精确字面量匹配时使用文本搜索。
- 开始代码工作前先读取本文件，并继续遵循本区块之外的项目规则。
{AGENTS_BLOCK_END}"""
    body = replace_block(remainder, AGENTS_BLOCK_START, AGENTS_BLOCK_END, block)
    return "@AGENTS.md\n\n" + body.lstrip()


def is_pwf_hook(item: dict[str, Any]) -> bool:
    command = item.get("command", "")
    return isinstance(command, str) and bool(PWF_HANDLER.search(command))


def merge_hooks(existing: dict[str, Any], upstream: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    hooks = dict(existing.get("hooks", {})) if isinstance(existing.get("hooks"), dict) else {}
    upstream_hooks = upstream.get("hooks", {})
    if not isinstance(upstream_hooks, dict):
        raise InitError("上游 .codex/hooks.json 格式不正确。")

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
            kept = [item for item in commands if not (isinstance(item, dict) and is_pwf_hook(item))]
            if kept:
                copy = dict(group)
                copy["hooks"] = kept
                kept_groups.append(copy)
        hooks[event] = kept_groups

    for event, groups in upstream_hooks.items():
        if not isinstance(groups, list):
            continue
        hooks.setdefault(event, [])
        hooks[event].extend(groups)

    merged["hooks"] = hooks
    return merged


def mirror_path() -> Path:
    digest = hashlib.sha256(PWF_URL.encode()).hexdigest()[:16]
    return Path.home() / ".agents" / "cache" / "sync-skills" / "repos" / f"{digest}.git"


def sync_repo_path() -> Path:
    config = Path.home() / ".config" / "sync-skills" / "repo"
    try:
        value = config.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise InitError(f"无法读取 {config}: {exc}") from exc
    repo = Path(value).expanduser().resolve()
    if not (repo / "sync-skills").is_file():
        raise InitError(f"sync-skills 仓库无效：{repo}")
    return repo


def refresh_mirror(repo: Path) -> Path:
    result = subprocess.run(
        [str(repo / "sync-skills"), "planning-with-files"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise InitError(f"Planning with Files 同步失败：{detail}")
    mirror = mirror_path()
    check = subprocess.run(
        ["git", f"--git-dir={mirror}", "rev-parse", "--verify", "HEAD"],
        capture_output=True,
        check=False,
    )
    if check.returncode:
        raise InitError(f"Planning with Files mirror 无效：{mirror}")
    return mirror


def extract_upstream(mirror: Path, destination: Path) -> None:
    paths = [".agents/skills/planning-with-files", ".codex/hooks", ".codex/hooks.json"]
    result = subprocess.run(
        ["git", f"--git-dir={mirror}", "archive", "HEAD", *paths],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise InitError(result.stderr.decode(errors="replace").strip() or "无法读取 Planning with Files mirror。")
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as archive:
        root = destination.resolve()
        for member in archive.getmembers():
            target = (destination / member.name).resolve()
            try:
                target.relative_to(root)
            except ValueError as exc:
                raise InitError(f"上游 archive 包含不安全路径：{member.name}") from exc
        archive.extractall(destination)


def copy_tree(source: Path, destination: Path) -> None:
    remove_path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)


def remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def write_if_changed(path: Path, content: str) -> str:
    current = path.read_text(encoding="utf-8") if path.is_file() else None
    if current == content:
        return "preserved"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "created" if current is None else "updated"


def ensure_empty_file(path: Path) -> str:
    if path.exists() or path.is_symlink():
        return "preserved"
    path.touch()
    return "created"


def install(target: Path, mirror: Path) -> list[str]:
    target = target.expanduser().resolve()
    if not target.is_dir():
        raise InitError(f"目标目录不存在：{target}")

    statuses: list[str] = []
    with tempfile.TemporaryDirectory() as temp_name:
        extracted = Path(temp_name)
        extract_upstream(mirror, extracted)
        copy_tree(
            extracted / ".agents/skills/planning-with-files",
            target / ".agents/skills/planning-with-files",
        )

        remove_path(target / ".codex/skills/planning-with-files")
        remove_path(target / ".agents/skills/pwf")

        copy_tree(extracted / ".codex/hooks", target / ".codex/hooks")

        hooks_path = target / ".codex/hooks.json"
        try:
            existing_hooks = json.loads(hooks_path.read_text(encoding="utf-8")) if hooks_path.is_file() else {}
            upstream_hooks = json.loads((extracted / ".codex/hooks.json").read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise InitError(f"hooks JSON 格式错误：{exc}") from exc
        hooks_text = json.dumps(merge_hooks(existing_hooks, upstream_hooks), ensure_ascii=False, indent=2) + "\n"
        statuses.append(f"{write_if_changed(hooks_path, hooks_text)} {hooks_path}")

    config = target / ".codex/config.toml"
    config_text = config.read_text(encoding="utf-8") if config.is_file() else ""
    statuses.append(f"{write_if_changed(config, managed_config(config_text))} {config}")

    base_agents = target / "AGENTS.md"
    statuses.append(f"{ensure_empty_file(base_agents)} {base_agents}")

    agents = target / "AGENTS.override.md"
    agents_text = agents.read_text(encoding="utf-8") if agents.is_file() else ""
    statuses.append(f"{write_if_changed(agents, managed_agents(agents_text))} {agents}")

    sembleignore = target / ".sembleignore"
    if sembleignore.exists():
        statuses.append(f"preserved {sembleignore}")
    else:
        sembleignore.write_text(".git/\nnode_modules/\n.planning/\n", encoding="utf-8")
        statuses.append(f"created {sembleignore}")

    statuses.insert(0, f"installed project Planning with Files skill and official hooks in {target}")
    return statuses


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else Path.cwd()
    try:
        repo = sync_repo_path()
        mirror = refresh_mirror(repo)
        for line in install(target, mirror):
            print(line)
        print("next: start a new Codex session and review project hooks with /hooks")
    except InitError as exc:
        print(f"spec-bootstrap: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
