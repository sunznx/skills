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
    def test_only_planning_plugin_installs_without_migrated_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "codex-home"
            marketplace = root / "planning-with-files"
            manifest = marketplace / ".codex-plugin" / "plugin.json"
            manifest.parent.mkdir(parents=True)
            original_manifest = b'{"name":"planning-with-files"}\n'
            manifest.write_bytes(original_manifest)
            cache = home / "plugins" / "cache" / "planning-with-files"
            (cache / "stale").mkdir(parents=True)
            responses = [
                {"marketplaces": []},
                {},
                {
                    "marketplaces": [
                        {"name": "planning-with-files", "root": str(marketplace)}
                    ]
                },
                {"installed": []},
                {},
            ]
            with (
                mock.patch.dict(os.environ, {"CODEX_HOME": str(home)}),
                mock.patch.object(MODULE, "codex_json", side_effect=responses) as codex_json,
            ):
                statuses = MODULE.ensure_plugins()

            self.assertEqual(manifest.read_bytes(), original_manifest)
            self.assertFalse(cache.exists())
            self.assertIn("added Codex marketplace planning-with-files", statuses)
            self.assertIn(
                "installed Codex plugin planning-with-files@planning-with-files",
                statuses,
            )
            self.assertFalse(any("ponytail" in str(call) for call in codex_json.call_args_list))
            self.assertTrue(any(status.startswith("restored ") for status in statuses))

    def test_install_preserves_global_config_and_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "codex-home"
            home.mkdir()
            original = {
                "config.toml": b'[features]\nhooks = true\n[mcp_servers.keep]\ncommand = "keep"\n',
                "hooks.json": b'{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"echo keep"}]}]}}\n',
            }
            for name, content in original.items():
                (home / name).write_bytes(content)
            with (
                mock.patch.dict(os.environ, {"CODEX_HOME": str(home)}),
                mock.patch.object(MODULE, "ensure_plugins", return_value=["plugins ok"]) as plugins,
                mock.patch.object(MODULE.subprocess, "run", side_effect=AssertionError("unexpected tool installation")),
            ):
                statuses = MODULE.install_global()
            plugins.assert_called_once_with()
            self.assertEqual(statuses, ["plugins ok"])
            self.assertEqual({path.name: path.read_bytes() for path in home.iterdir()}, original)

    def test_install_does_not_create_mcp_or_hook_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "codex-home"
            with (
                mock.patch.dict(os.environ, {"CODEX_HOME": str(home)}),
                mock.patch.object(MODULE, "ensure_plugins", return_value=["plugins ok"]) as plugins,
                mock.patch.object(MODULE.subprocess, "run", side_effect=AssertionError("unexpected tool installation")),
            ):
                self.assertEqual(MODULE.install_global(), ["plugins ok"])
            plugins.assert_called_once_with()
            self.assertFalse(home.exists())


if __name__ == "__main__":
    unittest.main()
