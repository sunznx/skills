#!/usr/bin/env python3
"""Install the project-local agent coding workflow."""

from __future__ import annotations

import re
import sys
from pathlib import Path


BLOCK_START = "# AGENT-WORKFLOW:START"
BLOCK_END = "# AGENT-WORKFLOW:END"
AGENTS_BLOCK_START = "<!-- agent-workflow:start -->"
AGENTS_BLOCK_END = "<!-- agent-workflow:end -->"


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

- 复杂任务使用 `$planning-with-files` 创建和维护计划；Planning with Files hooks 由已安装 plugin 的 `hooks/codex-hooks.json` 提供。
- 以 `task_plan.md` 为权威，并用 `update_plan` 完整镜像步骤和状态。
- 阅读、搜索和定位代码时优先使用 Serena 与 Semble，再按需使用文本搜索。
- 开始代码工作前先读取本文件，并继续遵循本区块之外的项目规则。
{AGENTS_BLOCK_END}"""
    body = replace_block(remainder, AGENTS_BLOCK_START, AGENTS_BLOCK_END, block)
    return "@AGENTS.md\n\n" + body.lstrip()


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


def install(target: Path) -> list[str]:
    target = target.expanduser().resolve()
    if not target.is_dir():
        raise InitError(f"目标目录不存在：{target}")

    statuses: list[str] = []
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

    statuses.insert(0, f"configured agent workflow in {target}")
    return statuses


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else Path.cwd()
    try:
        for line in install(target):
            print(line)
        print("next: ensure the planning-with-files plugin is enabled, then start a new Codex session and review hooks with /hooks")
    except InitError as exc:
        print(f"spec-bootstrap: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
