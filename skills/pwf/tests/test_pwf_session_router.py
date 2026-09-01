from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROUTER = Path(__file__).parents[1] / "scripts" / "pwf_session_router.py"


class RouterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        hooks = self.root / ".codex" / "hooks"
        hooks.mkdir(parents=True)
        (hooks / "pwf_session_router.py").write_bytes(ROUTER.read_bytes())
        (hooks / "codex_hook_adapter.py").write_text(
            textwrap.dedent(
                """
                import hashlib
                from pathlib import Path
                def cwd_from_payload(payload): return Path(payload.get("cwd", "."))
                def canonical_project(root): return root.resolve()
                def session_id_from_payload(payload): return payload.get("session_id")
                def state_key(host, root, session_id):
                    return hashlib.sha256(f"{host}:{root.resolve()}:{session_id}".encode()).hexdigest()
                """
            ),
            encoding="utf-8",
        )
        (hooks / "run_sh.py").write_text(
            textwrap.dedent(
                """
                import json, os, sys
                payload = json.load(sys.stdin)
                event = "UserPromptSubmit" if sys.argv[1] == "user-prompt-submit.sh" else "SessionStart"
                print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": "child PLAN_ID=" + os.environ.get("PLAN_ID", "")}}))
                """
            ),
            encoding="utf-8",
        )
        init = self.root / ".codex" / "skills" / "planning-with-files" / "scripts" / "init-session.sh"
        init.parent.mkdir(parents=True)
        init.write_text(
            textwrap.dedent(
                """#!/bin/sh
                mkdir -p .planning
                base="2026-09-01-test"
                plan="$base"
                n=2
                while [ -d ".planning/$plan" ]; do plan="$base-$n"; n=$((n+1)); done
                mkdir -p ".planning/$plan"
                touch ".planning/$plan/task_plan.md" ".planning/$plan/findings.md" ".planning/$plan/progress.md"
                printf '%s\n' "$plan" > .planning/.active_plan
                printf 'PLAN_ID=%s\n' "$plan"
                """
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def call(self, session: str, prompt: str, script: str = "user-prompt-submit.sh") -> dict:
        payload = {"cwd": str(self.root), "session_id": session, "prompt": prompt}
        result = subprocess.run(
            [sys.executable, str(self.root / ".codex/hooks/pwf_session_router.py"), "run_sh.py", script],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(result.stdout)

    def context(self, result: dict) -> str:
        return result["hookSpecificOutput"]["additionalContext"]

    def test_creates_binding_and_restores_active_pointer(self) -> None:
        active = self.root / ".planning" / ".active_plan"
        active.parent.mkdir()
        active.write_text("old-plan\n", encoding="utf-8")

        context = self.context(self.call("session-a", "$pwf build api"))

        self.assertIn("PWF_PLAN_DIR=", context)
        self.assertIn("child PLAN_ID=2026-09-01-test", context)
        self.assertEqual(active.read_text(encoding="utf-8"), "old-plan\n")
        sessions = self.root / ".planning" / "sessions"
        self.assertEqual(len(list(sessions.glob("*.plan"))), 1)
        self.assertEqual(len(list(sessions.glob("*.attached"))), 1)

    def test_sessions_get_distinct_plans_and_resume_their_mapping(self) -> None:
        first = self.context(self.call("session-a", "$pwf first"))
        second = self.context(self.call("session-b", "$pwf second"))
        resumed = self.context(self.call("session-a", "continue"))

        self.assertIn("2026-09-01-test\n", first)
        self.assertIn("2026-09-01-test-2\n", second)
        self.assertIn("2026-09-01-test\n", resumed)

    def test_missing_task_does_not_create_plan(self) -> None:
        context = self.context(self.call("session-a", "$pwf"))
        self.assertIn("请使用 $pwf <任务名>", context)
        self.assertFalse(list((self.root / ".planning").glob("*/task_plan.md")))

    def test_skill_can_bind_with_injected_opaque_key(self) -> None:
        context = self.context(self.call("session-a", ""))
        key = context.split("PWF_SESSION_KEY=", 1)[1].splitlines()[0]
        result = subprocess.run(
            [sys.executable, str(self.root / ".codex/hooks/pwf_session_router.py"), "bind", key, "fallback task"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        resumed = self.context(self.call("session-a", "continue"))
        self.assertIn("PWF_PLAN_DIR=", result.stdout)
        self.assertIn("PWF_PLAN_DIR=", resumed)


if __name__ == "__main__":
    unittest.main()
