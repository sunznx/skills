from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "scripts" / "spec_bootstrap.py"
SPEC = importlib.util.spec_from_file_location("spec_bootstrap", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class InitWorkflowTest(unittest.TestCase):
    def test_ponytail_is_installed_only_when_missing(self) -> None:
        with mock.patch.object(MODULE, "codex_json") as command:
            command.side_effect = [
                {"marketplaces": []},
                {"name": "ponytail"},
                {"installed": []},
                {"pluginId": MODULE.PONYTAIL_PLUGIN},
            ]
            self.assertEqual(
                MODULE.ensure_ponytail(),
                [
                    "added Codex marketplace ponytail",
                    "installed Codex plugin ponytail@ponytail",
                ],
            )
            self.assertEqual(
                command.call_args_list,
                [
                    mock.call("plugin", "marketplace", "list"),
                    mock.call("plugin", "marketplace", "add", MODULE.PONYTAIL_SOURCE),
                    mock.call("plugin", "list"),
                    mock.call("plugin", "add", MODULE.PONYTAIL_PLUGIN),
                ],
            )

        with mock.patch.object(MODULE, "codex_json") as command:
            command.side_effect = [
                {"marketplaces": [{"name": MODULE.PONYTAIL_MARKETPLACE}]},
                {"installed": [{"pluginId": MODULE.PONYTAIL_PLUGIN, "enabled": True}]},
            ]
            self.assertEqual(
                MODULE.ensure_ponytail(),
                [
                    "preserved Codex marketplace ponytail",
                    "preserved Codex plugin ponytail@ponytail",
                ],
            )

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
        self.assertIn("`task_plan.md`", once)
        self.assertIn("`update_plan`", once)
        self.assertIn("使用 Semble 做自然语言或概念搜索", once)
        self.assertIn("仅在需要全仓精确字面量匹配时使用文本搜索", once)
        self.assertNotIn("$planning-with-files", once)
        self.assertNotIn("Serena", once)
        self.assertNotIn("开始代码工作前先读取本文件", once)

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
                ],
                "SessionStart": [
                    {"hooks": [{"type": "command", "command": "serena-hooks activate --client=codex"}]}
                ],
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
        self.assertNotIn("pwf_session_router.py", text)
        official = twice["hooks"]["UserPromptSubmit"][1]["hooks"][0]
        self.assertEqual(official, upstream["hooks"]["UserPromptSubmit"][0]["hooks"][0])
        self.assertEqual(text.count("serena-hooks"), 3)
        self.assertIn("remind --client=codex", text)
        self.assertIn("activate --client=codex", text)
        self.assertIn("cleanup --client=codex", text)

    def test_install_uses_project_skill_and_official_hooks(self) -> None:
        def fake_extract(_mirror: Path, destination: Path) -> None:
            skill = destination / ".agents/skills/planning-with-files"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("official skill\n", encoding="utf-8")

            runtime = destination / ".codex/skills/planning-with-files"
            scripts = runtime / "scripts"
            scripts.mkdir(parents=True)
            (runtime / "SKILL.md").write_text("official runtime skill\n", encoding="utf-8")
            for name in ("resolve-plan-dir.sh", "check-complete.sh", "session-catchup.py"):
                (scripts / name).write_text(f"# {name}\n", encoding="utf-8")

            hooks = destination / ".codex/hooks"
            hooks.mkdir(parents=True)
            (hooks / "run_sh.py").write_text("# official hook\n", encoding="utf-8")
            (hooks / "plugin_dispatch.py").write_text("# official dispatch\n", encoding="utf-8")
            (destination / ".codex/hooks.json").write_text(
                '{"hooks":{"UserPromptSubmit":[{"hooks":[{"type":"command",'
                '"command":"python3 .codex/hooks/run_sh.py user-prompt-submit.sh"}]}]}}\n',
                encoding="utf-8",
            )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_paths = [
                root / ".agents/skills/pwf",
            ]
            for path in old_paths:
                path.mkdir(parents=True)
            router = root / ".codex/hooks/pwf_session_router.py"
            router.parent.mkdir(parents=True)
            router.write_text("old router\n", encoding="utf-8")
            old_runtime = root / ".codex/skills/planning-with-files/old.txt"
            old_runtime.parent.mkdir(parents=True)
            old_runtime.write_text("old\n", encoding="utf-8")

            with mock.patch.object(MODULE, "extract_upstream", side_effect=fake_extract):
                MODULE.install(root, Path("/unused-mirror"))

            self.assertEqual(
                (root / ".agents/skills/planning-with-files/SKILL.md").read_text(encoding="utf-8"),
                "official skill\n",
            )
            self.assertTrue((root / ".codex/hooks/run_sh.py").is_file())
            self.assertTrue((root / ".codex/hooks/plugin_dispatch.py").is_file())
            for name in ("resolve-plan-dir.sh", "check-complete.sh", "session-catchup.py"):
                self.assertTrue((root / ".codex/skills/planning-with-files/scripts" / name).is_file())
            hooks_text = (root / ".codex/hooks.json").read_text(encoding="utf-8")
            self.assertIn(".codex/hooks/run_sh.py", hooks_text)
            self.assertEqual(hooks_text.count("serena-hooks"), 3)
            self.assertFalse(router.exists())
            self.assertFalse(old_runtime.exists())
            for path in old_paths:
                self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
