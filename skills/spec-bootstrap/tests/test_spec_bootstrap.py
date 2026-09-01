from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "spec_bootstrap.py"
SPEC = importlib.util.spec_from_file_location("spec_bootstrap", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class InitWorkflowTest(unittest.TestCase):
    def test_agents_file_is_created_empty_or_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "AGENTS.md"
            self.assertEqual(MODULE.ensure_empty_file(path), "created")
            self.assertEqual(path.read_bytes(), b"")
            path.write_text("keep\n", encoding="utf-8")
            self.assertEqual(MODULE.ensure_empty_file(path), "preserved")
            self.assertEqual(path.read_text(encoding="utf-8"), "keep\n")

    def test_agents_first_line_and_idempotent_block(self) -> None:
        original = "# Project rule\n\nKeep this.\n"
        once = MODULE.managed_agents(original)
        twice = MODULE.managed_agents(once)
        self.assertEqual(once, twice)
        self.assertEqual(once.splitlines()[0], "@AGENTS.md")
        self.assertIn("Keep this.", once)
        self.assertEqual(once.count(MODULE.AGENTS_BLOCK_START), 1)

    def test_config_preserves_existing_server_without_duplicate(self) -> None:
        original = '[mcp_servers.serena]\ncommand = "custom"\n'
        result = MODULE.managed_config(original)
        self.assertEqual(result.count("[mcp_servers.serena]"), 1)
        self.assertEqual(result.count("[mcp_servers.semble]"), 1)
        self.assertEqual(result, MODULE.managed_config(result))

    def test_hook_merge_preserves_other_hooks_and_is_idempotent(self) -> None:
        existing = {
            "hooks": {
                "UserPromptSubmit": [
                    {"hooks": [{"type": "command", "command": "echo keep"}]},
                    {"hooks": [{"type": "command", "command": "python3 .codex/hooks/pwf_session_router.py run_sh.py user-prompt-submit.sh"}]},
                ]
            }
        }
        upstream = {
            "hooks": {
                "UserPromptSubmit": [
                    {"hooks": [{"type": "command", "command": "python3 .codex/hooks/run_sh.py user-prompt-submit.sh 2>/dev/null || true"}]}
                ]
            }
        }
        once = MODULE.merge_hooks(existing, upstream)
        twice = MODULE.merge_hooks(once, upstream)
        text = str(twice)
        self.assertEqual(once, twice)
        self.assertIn("echo keep", text)
        self.assertEqual(len(twice["hooks"]["UserPromptSubmit"]), 2)
        self.assertEqual(text.count("pwf_session_router.py"), 2)  # POSIX + Windows


if __name__ == "__main__":
    unittest.main()
