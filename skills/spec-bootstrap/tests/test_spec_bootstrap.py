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
    def test_ponytail_update_uses_valid_cached_mirror_on_fetch_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            mirror = Path(directory) / "ponytail.git"
            mirror.mkdir()
            failed = mock.Mock(returncode=1, stderr="offline", stdout="")
            valid = mock.Mock(returncode=0)
            with (
                mock.patch.object(MODULE, "mirror_path", return_value=mirror),
                mock.patch.object(MODULE.subprocess, "run", side_effect=[failed, valid]),
                mock.patch("builtins.print") as output,
            ):
                self.assertEqual(MODULE.refresh_ponytail_mirror(), mirror)
            output.assert_called_once()

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
        ponytail = MODULE.project_ponytail_hooks(
            {
                "hooks": {
                    "SessionStart": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": 'node "${CLAUDE_PLUGIN_ROOT}/hooks/ponytail-activate.js"',
                                }
                            ]
                        }
                    ],
                    "UserPromptSubmit": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": 'node "${CLAUDE_PLUGIN_ROOT}/hooks/ponytail-mode-tracker.js"',
                                }
                            ]
                        }
                    ],
                }
            }
        )
        once = MODULE.merge_hooks(existing, upstream, ponytail)
        twice = MODULE.merge_hooks(once, upstream, ponytail)
        text = str(twice)
        self.assertEqual(once, twice)
        self.assertIn("echo keep", text)
        self.assertEqual(len(twice["hooks"]["UserPromptSubmit"]), 3)
        self.assertNotIn("pwf_session_router.py", text)
        official = twice["hooks"]["UserPromptSubmit"][1]["hooks"][0]
        self.assertEqual(official, upstream["hooks"]["UserPromptSubmit"][0]["hooks"][0])
        self.assertEqual(text.count("serena-hooks"), 3)
        self.assertIn("remind --client=codex", text)
        self.assertIn("activate --client=codex", text)
        self.assertIn("cleanup --client=codex", text)
        self.assertNotIn("${CLAUDE_PLUGIN_ROOT}", text)
        self.assertIn(".codex/vendor/ponytail/hooks/ponytail-activate.js", text)

    def test_install_uses_project_skill_and_official_hooks(self) -> None:
        def fake_extract_pwf(_mirror: Path, destination: Path) -> None:
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

        def fake_extract_ponytail(_mirror: Path, destination: Path) -> None:
            hooks = destination / "hooks"
            hooks.mkdir(parents=True)
            (hooks / "ponytail-activate.js").write_text("// activate\n", encoding="utf-8")
            (hooks / "ponytail-mode-tracker.js").write_text("// tracker\n", encoding="utf-8")
            (hooks / "claude-codex-hooks.json").write_text(
                '{"hooks":{"SessionStart":[{"hooks":[{"type":"command",'
                '"command":"node \\\"${CLAUDE_PLUGIN_ROOT}/hooks/ponytail-activate.js\\\""}]}],'
                '"UserPromptSubmit":[{"hooks":[{"type":"command",'
                '"command":"node \\\"${CLAUDE_PLUGIN_ROOT}/hooks/ponytail-mode-tracker.js\\\""}]}]}}\n',
                encoding="utf-8",
            )
            skill = destination / "skills/ponytail"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("project ponytail\n", encoding="utf-8")
            review = destination / "skills/ponytail-review"
            review.mkdir(parents=True)
            (review / "SKILL.md").write_text("project review\n", encoding="utf-8")
            manifest = destination / ".codex-plugin"
            manifest.mkdir(parents=True)
            (manifest / "plugin.json").write_text('{"name":"ponytail"}\n', encoding="utf-8")
            (destination / "LICENSE").write_text("MIT\n", encoding="utf-8")

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
            trellis_hooks = {
                name: root / ".codex/hooks" / name
                for name in (
                    "inject-subagent-context.py",
                    "inject-workflow-state.py",
                    "session-start.py",
                )
            }
            for name, path in trellis_hooks.items():
                path.write_text(f"# trellis {name}\n", encoding="utf-8")
            old_runtime = root / ".codex/skills/planning-with-files/old.txt"
            old_runtime.parent.mkdir(parents=True)
            old_runtime.write_text("old\n", encoding="utf-8")

            old_vendor_skill = root / ".codex/vendor/ponytail/skills/ponytail-old"
            old_vendor_skill.mkdir(parents=True)
            (old_vendor_skill / "SKILL.md").write_text("old\n", encoding="utf-8")
            old_project_skill = root / ".agents/skills/ponytail-old"
            old_project_skill.mkdir(parents=True)
            (old_project_skill / "SKILL.md").write_text("old\n", encoding="utf-8")

            with (
                mock.patch.object(MODULE, "extract_pwf", side_effect=fake_extract_pwf),
                mock.patch.object(MODULE, "extract_ponytail", side_effect=fake_extract_ponytail),
            ):
                MODULE.install(root, Path("/unused-pwf"), Path("/unused-ponytail"))

            self.assertEqual(
                (root / ".agents/skills/planning-with-files/SKILL.md").read_text(encoding="utf-8"),
                "official skill\n",
            )
            self.assertTrue((root / ".codex/hooks/run_sh.py").is_file())
            self.assertTrue((root / ".codex/hooks/plugin_dispatch.py").is_file())
            for name, path in trellis_hooks.items():
                self.assertEqual(path.read_text(encoding="utf-8"), f"# trellis {name}\n")
            for name in ("resolve-plan-dir.sh", "check-complete.sh", "session-catchup.py"):
                self.assertTrue((root / ".codex/skills/planning-with-files/scripts" / name).is_file())
            hooks_text = (root / ".codex/hooks.json").read_text(encoding="utf-8")
            self.assertIn(".codex/hooks/run_sh.py", hooks_text)
            self.assertEqual(hooks_text.count("serena-hooks"), 3)
            self.assertIn(".codex/vendor/ponytail/hooks/ponytail-activate.js", hooks_text)
            self.assertNotIn("${CLAUDE_PLUGIN_ROOT}", hooks_text)
            self.assertEqual(
                (root / ".agents/skills/ponytail/SKILL.md").read_text(encoding="utf-8"),
                "project ponytail\n",
            )
            self.assertTrue((root / ".agents/skills/ponytail-review/SKILL.md").is_file())
            self.assertTrue((root / ".codex/vendor/ponytail/.codex-plugin/plugin.json").is_file())
            self.assertFalse(old_project_skill.exists())
            self.assertFalse(router.exists())
            self.assertFalse(old_runtime.exists())
            for path in old_paths:
                self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
