#!/usr/bin/env python3
"""Bind one Codex session to one isolated Planning with Files plan."""

from __future__ import annotations

import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


PWF_PROMPT = re.compile(r"^\s*\$pwf(?:\s+(.+?))?\s*$", re.DOTALL)
SAFE_PLAN_ID = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._-]*$")
SAFE_SESSION_KEY = re.compile(r"^[0-9a-f]{64}$")
PLAN_ID_LINE = re.compile(r"^PLAN_ID=([A-Za-z0-9_][A-Za-z0-9._-]*)$", re.MULTILINE)


def read_payload(raw: str) -> dict[str, Any]:
    try:
        value = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def atomic_write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(value)
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def restore_file(path: Path, existed: bool, content: bytes) -> None:
    if existed:
        path.write_bytes(content)
    else:
        path.unlink(missing_ok=True)


def validate_plan(root: Path, plan_id: str) -> Path | None:
    if not SAFE_PLAN_ID.fullmatch(plan_id):
        return None
    plan_dir = root / ".planning" / plan_id
    required = ("task_plan.md", "findings.md", "progress.md")
    if plan_dir.is_dir() and all((plan_dir / name).is_file() for name in required):
        return plan_dir.resolve()
    return None


def mapped_plan(root: Path, key: str) -> tuple[str, Path] | None:
    mapping = root / ".planning" / "sessions" / f"{key}.plan"
    try:
        plan_id = mapping.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    plan_dir = validate_plan(root, plan_id)
    return (plan_id, plan_dir) if plan_dir else None


def create_and_bind(root: Path, key: str, task: str) -> tuple[str, Path]:
    init_script = root / ".codex" / "skills" / "planning-with-files" / "scripts" / "init-session.sh"
    if not init_script.is_file():
        raise RuntimeError("找不到项目内 Planning with Files，请先运行 $spec-bootstrap。")

    planning = root / ".planning"
    planning.mkdir(parents=True, exist_ok=True)
    active = planning / ".active_plan"
    lock_path = planning / ".pwf-init.lock"

    with lock_path.open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        existed = active.exists()
        previous = active.read_bytes() if existed else b""
        try:
            result = subprocess.run(
                ["sh", str(init_script), task],
                cwd=root,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )
            if result.returncode:
                detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
                raise RuntimeError(f"创建计划失败：{detail}")
            match = PLAN_ID_LINE.search(result.stdout)
            if not match:
                raise RuntimeError("创建计划后没有获得有效 plan id。")
            plan_id = match.group(1)
            plan_dir = validate_plan(root, plan_id)
            if plan_dir is None:
                raise RuntimeError("创建出的计划目录不完整。")
            sessions = planning / "sessions"
            atomic_write(sessions / f"{key}.plan", f"{plan_id}\n")
            atomic_write(sessions / f"{key}.attached", "attached\n")
            return plan_id, plan_dir
        finally:
            restore_file(active, existed, previous)


def merge_context(stdout: str, event: str | None, context: str) -> str:
    try:
        result = json.loads(stdout) if stdout.strip() else {}
    except json.JSONDecodeError:
        result = {}
    if not isinstance(result, dict):
        result = {}

    if event in {"SessionStart", "UserPromptSubmit"}:
        specific = result.setdefault("hookSpecificOutput", {})
        if not isinstance(specific, dict):
            specific = {}
            result["hookSpecificOutput"] = specific
        specific["hookEventName"] = event
        existing = specific.get("additionalContext", "")
        specific["additionalContext"] = f"{context}\n{existing}".rstrip()
        return json.dumps(result, ensure_ascii=True) + "\n"

    return stdout


def event_for(handler_args: list[str], payload: dict[str, Any]) -> str | None:
    if handler_args[:2] == ["run_sh.py", "session-start.sh"]:
        return "SessionStart"
    if handler_args[:2] == ["run_sh.py", "user-prompt-submit.sh"]:
        return "UserPromptSubmit"
    event = payload.get("hook_event_name")
    return event if isinstance(event, str) else None


def load_adapter(hook_dir: Path):
    sys.path.insert(0, str(hook_dir))
    import codex_hook_adapter  # type: ignore

    return codex_hook_adapter


def bind_from_skill(arguments: list[str]) -> int:
    if len(arguments) < 2:
        print("pwf-session: bind requires a session key and task name", file=sys.stderr)
        return 2
    key, task = arguments[0], " ".join(arguments[1:]).strip()
    if not SAFE_SESSION_KEY.fullmatch(key) or not task:
        print("pwf-session: invalid session key or empty task name", file=sys.stderr)
        return 2
    root = Path.cwd().resolve()
    try:
        _, plan_dir = create_and_bind(root, key, task)
    except (OSError, RuntimeError) as exc:
        print(f"pwf-session: {exc}", file=sys.stderr)
        return 1
    print(f"[pwf-session] PWF_PLAN_DIR={plan_dir}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        return 0
    if sys.argv[1] == "bind":
        return bind_from_skill(sys.argv[2:])

    raw = sys.stdin.read()
    payload = read_payload(raw)
    hook_dir = Path(__file__).resolve().parent
    adapter = load_adapter(hook_dir)
    root = adapter.canonical_project(adapter.cwd_from_payload(payload))
    event = event_for(sys.argv[1:], payload)
    session_id = adapter.session_id_from_payload(payload)
    context = ""
    plan: tuple[str, Path] | None = None
    key: str | None = None
    if root is not None and session_id:
        key = adapter.state_key("codex", root, session_id)

    prompt = payload.get("prompt", "")
    match = PWF_PROMPT.fullmatch(prompt) if isinstance(prompt, str) else None
    if match and event == "UserPromptSubmit":
        task = (match.group(1) or "").strip()
        if root is None:
            context = "[pwf-session] 无法确定项目根目录，未创建计划。"
        elif not session_id:
            context = "[pwf-session] 本次 hook 没有 session_id，未创建计划。"
        elif not task:
            context = "[pwf-session] 请使用 $pwf <任务名>。"
        else:
            try:
                if not key:
                    raise RuntimeError("无法生成 session key。")
                plan = create_and_bind(root, key, task)
            except (OSError, RuntimeError) as exc:
                context = f"[pwf-session] {exc}"

    if root is not None and plan is None and key:
        plan = mapped_plan(root, key)

    env = os.environ.copy()
    if plan:
        env["PLAN_ID"] = plan[0]
        context = f"[pwf-session] PWF_PLAN_DIR={plan[1]}"
    elif not context and event == "UserPromptSubmit" and key:
        # Codex represents an invoked skill as a structured UserInput::Skill.
        # Current UserPromptSubmit payloads omit that item, so the skill uses
        # this opaque key to complete the binding without exposing session IDs.
        context = f"[pwf-session] PWF_SESSION_KEY={key}"

    handler = hook_dir / sys.argv[1]
    if not handler.is_file():
        if context and event:
            sys.stdout.write(merge_context("", event, context))
        return 0

    result = subprocess.run(
        [sys.executable, str(handler), *sys.argv[2:]],
        input=raw,
        cwd=root or Path.cwd(),
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.stderr:
        sys.stderr.write(result.stderr)
    if context and event:
        sys.stdout.write(merge_context(result.stdout, event, context))
    else:
        sys.stdout.write(result.stdout)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
