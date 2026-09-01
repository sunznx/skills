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
        self.assertIn("$planning-with-files", once)
        self.assertNotIn("$pwf", once)

    def test_config_preserves_existing_server_without_duplicate(self) -> None:
        original = '[mcp_servers.serena]\ncommand = "custom"\n'
        result = MODULE.managed_config(original)
        self.assertEqual(result.count("[mcp_servers.serena]"), 1)
        self.assertEqual(result.count("[mcp_servers.semble]"), 1)
        self.assertEqual(result, MODULE.managed_config(result))

    def test_install_leaves_plugin_hooks_to_codex(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hooks = root / ".codex/hooks.json"
            hooks.parent.mkdir(parents=True)
            hooks.write_text('{"hooks":{"UserPromptSubmit":[]}}\n', encoding="utf-8")

            MODULE.install(root)

            self.assertEqual(hooks.read_text(encoding="utf-8"), '{"hooks":{"UserPromptSubmit":[]}}\n')
            self.assertFalse((root / ".codex/hooks").exists())
            self.assertFalse((root / ".agents/skills/pwf").exists())


if __name__ == "__main__":
    unittest.main()
