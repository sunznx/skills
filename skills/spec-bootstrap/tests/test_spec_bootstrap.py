from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "scripts" / "spec_bootstrap.py"
SPEC = importlib.util.spec_from_file_location("spec_bootstrap", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class SpecBootstrapTest(unittest.TestCase):
    def test_uvx_tools_are_prepared_first(self) -> None:
        completed = MODULE.subprocess.CompletedProcess([], 0, "", "")
        with mock.patch.object(MODULE.subprocess, "run", return_value=completed) as run:
            statuses = MODULE.prepare_uvx_tools()
        self.assertEqual(statuses, ["prepared uvx tool Semble", "prepared uvx tool Serena"])
        self.assertEqual(
            [call.args[0] for call in run.call_args_list],
            [command for _name, command in MODULE.UVX_TOOLS],
        )

    def test_config_preserves_existing_server_without_duplicate(self) -> None:
        original = '[mcp_servers.serena]\ncommand = "custom"\n'
        result = MODULE.managed_config(original)
        self.assertEqual(result.count("[mcp_servers.serena]"), 1)
        self.assertEqual(result.count("[mcp_servers.semble]"), 1)
        self.assertEqual(result, MODULE.managed_config(result))

    def test_hook_merge_preserves_other_hooks_and_is_idempotent(self) -> None:
        existing = {
            "hooks": {
                "SessionStart": [
                    {"hooks": [{"type": "command", "command": "echo keep"}]},
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "serena-hooks activate --client=codex",
                            }
                        ]
                    },
                ]
            }
        }
        once = MODULE.merge_hooks(existing)
        twice = MODULE.merge_hooks(once)
        text = json.dumps(twice)
        self.assertEqual(once, twice)
        self.assertIn("echo keep", text)
        self.assertEqual(text.count("serena-hooks"), 3)
        self.assertIn("remind --client=codex", text)
        self.assertIn("activate --client=codex", text)
        self.assertIn("cleanup --client=codex", text)

    def test_plugins_are_installed_globally(self) -> None:
        responses = [
            {"marketplaces": [{"name": "ponytail"}]},
            {},
            {"installed": [{"pluginId": "ponytail@ponytail", "enabled": True}]},
            {},
        ]
        with mock.patch.object(MODULE, "codex_json", side_effect=responses) as codex:
            statuses = MODULE.ensure_plugins()
        self.assertIn("preserved Codex marketplace ponytail", statuses)
        self.assertIn("added Codex marketplace planning-with-files", statuses)
        self.assertIn("preserved Codex plugin ponytail@ponytail", statuses)
        self.assertIn("installed Codex plugin planning-with-files@planning-with-files", statuses)
        self.assertEqual(
            codex.call_args_list,
            [
                mock.call("plugin", "marketplace", "list"),
                mock.call("plugin", "marketplace", "add", "OthmanAdi/planning-with-files"),
                mock.call("plugin", "list"),
                mock.call("plugin", "add", "planning-with-files@planning-with-files"),
            ],
        )

    def test_install_writes_only_global_codex_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "codex-home"
            home.mkdir()
            (home / "config.toml").write_text("[features]\nhooks = true\n", encoding="utf-8")
            (home / "hooks.json").write_text(
                '{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"echo keep"}]}]}}\n',
                encoding="utf-8",
            )
            with (
                mock.patch.dict(os.environ, {"CODEX_HOME": str(home)}),
                mock.patch.object(MODULE, "prepare_uvx_tools", return_value=["uvx ok"]),
                mock.patch.object(MODULE, "ensure_plugins", return_value=["plugins ok"]),
            ):
                statuses = MODULE.install_global()
            self.assertEqual(statuses[:2], ["uvx ok", "plugins ok"])
            config = (home / "config.toml").read_text(encoding="utf-8")
            self.assertIn("[mcp_servers.serena]", config)
            self.assertIn("[mcp_servers.semble]", config)
            hooks = (home / "hooks.json").read_text(encoding="utf-8")
            self.assertIn("echo keep", hooks)
            self.assertEqual(hooks.count("serena-hooks"), 3)
            self.assertEqual(sorted(path.name for path in home.iterdir()), ["config.toml", "hooks.json"])


if __name__ == "__main__":
    unittest.main()
