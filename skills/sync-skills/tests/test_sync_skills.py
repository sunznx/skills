import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts/sync_skills.py"
SPEC = importlib.util.spec_from_file_location("sync_skills", SCRIPT)
sync_skills = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(sync_skills)


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def init_repo(repo: Path, skills: dict[str, str]) -> None:
    for name, content in skills.items():
        path = repo / "skills" / name
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(content)
    manifest = {
        "version": 1,
        "skills": [
            {"name": name, "managed": False, "note": "test"}
            for name in sorted(skills)
        ],
    }
    (repo / "skills/sources.json").write_text(json.dumps(manifest) + "\n")
    (repo / "README.md").write_text(
        "<!-- skill-catalog:start -->\n<!-- skill-catalog:end -->\n"
    )
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "test")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")


class SyncSkillsTests(unittest.TestCase):
    def test_parse_plugin_commands(self) -> None:
        self.assertEqual(sync_skills.parse_command(["plugins"]), ("plugins", None))
        self.assertEqual(
            sync_skills.parse_command(["plugin", "sol-advisor"]),
            ("plugins", "sol-advisor"),
        )

    def test_sync_plugin_updates_marketplace_and_runs_post_install(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            plugin_root = Path(temp) / "plugin"
            script = plugin_root / "scripts/install-agents.sh"
            script.parent.mkdir(parents=True)
            script.write_text("#!/bin/sh\n")
            manifest = {
                "plugins": [{
                    "name": "sol-advisor",
                    "marketplace": "sol-advisor",
                    "source": "DannyMac180/sol-advisor",
                    "url": "https://github.com/DannyMac180/sol-advisor.git",
                    "ref": "main",
                    "post_install": "scripts/install-agents.sh",
                }],
            }
            calls: list[tuple[str, ...]] = []

            def fake_run(*args: str, **_kwargs: object) -> subprocess.CompletedProcess:
                calls.append(args)
                if args == ("codex", "plugin", "marketplace", "list"):
                    stdout = "MARKETPLACE ROOT\nsol-advisor /tmp/sol-advisor\n"
                elif args == ("codex", "plugin", "list", "--json"):
                    stdout = json.dumps({"installed": [{
                        "pluginId": "sol-advisor@sol-advisor",
                        "installed": True,
                        "enabled": True,
                        "source": {"path": str(plugin_root)},
                    }]})
                else:
                    stdout = "{}"
                return subprocess.CompletedProcess(args, 0, stdout, "")

            with patch.object(sync_skills, "run", side_effect=fake_run):
                sync_skills.sync_plugins(manifest, push=False)

            self.assertIn(
                ("codex", "plugin", "marketplace", "upgrade", "sol-advisor", "--json"),
                calls,
            )
            self.assertIn(
                ("codex", "plugin", "add", "sol-advisor@sol-advisor", "--json"),
                calls,
            )
            self.assertIn(("sh", str(script)), calls)

    def test_sync_plugin_suppresses_commands_and_preserves_old_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            marketplace = root / "marketplace"
            manifest_path = marketplace / ".codex-plugin/plugin.json"
            manifest_path.parent.mkdir(parents=True)
            original_manifest = b'{"name":"planning-with-files","commands":"./commands"}\n'
            manifest_path.write_bytes(original_manifest)
            old_cache = root / "cache/3.15.0"
            old_hook = old_cache / "hooks/pre_tool_use.py"
            old_hook.parent.mkdir(parents=True)
            old_hook.write_text("# hook\n")
            migrated = old_cache / ".codex-plugin/migrated-command-skills/source-command-plan"
            migrated.mkdir(parents=True)
            new_cache = root / "cache/3.16.0"
            plugin = {
                "name": "planning-with-files",
                "marketplace": "planning-with-files",
                "source": "OthmanAdi/planning-with-files",
                "url": "https://github.com/OthmanAdi/planning-with-files.git",
                "suppress_commands": True,
            }
            list_calls = 0

            def fake_run(*args: str, **_kwargs: object) -> subprocess.CompletedProcess:
                nonlocal list_calls
                if args == ("codex", "plugin", "marketplace", "list"):
                    stdout = "MARKETPLACE ROOT\nplanning-with-files /tmp/pwf\n"
                elif args == ("codex", "plugin", "marketplace", "list", "--json"):
                    stdout = json.dumps({"marketplaces": [{
                        "name": "planning-with-files",
                        "root": str(marketplace),
                    }]})
                elif args == ("codex", "plugin", "list", "--json"):
                    cache = old_cache if list_calls == 0 else new_cache
                    list_calls += 1
                    stdout = json.dumps({"installed": [{
                        "pluginId": "planning-with-files@planning-with-files",
                        "installed": True,
                        "enabled": True,
                        "source": {"path": str(cache)},
                    }]})
                elif args == (
                    "codex", "plugin", "add",
                    "planning-with-files@planning-with-files", "--json",
                ):
                    self.assertEqual(json.loads(manifest_path.read_text())["commands"], [])
                    shutil.rmtree(old_cache)
                    new_cache.mkdir(parents=True)
                    stdout = "{}"
                else:
                    stdout = "{}"
                return subprocess.CompletedProcess(args, 0, stdout, "")

            with patch.object(sync_skills, "run", side_effect=fake_run):
                sync_skills.sync_plugins({"plugins": [plugin]}, push=False)

            self.assertEqual(manifest_path.read_bytes(), original_manifest)
            self.assertTrue(old_hook.is_file())
            self.assertFalse((old_cache / ".codex-plugin/migrated-command-skills").exists())

    def test_add_does_not_overwrite_another_local_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            local = root / "local"
            repo.mkdir()
            init_repo(repo, {"a": "repo-a\n"})
            (local / "a").mkdir(parents=True)
            (local / "a/SKILL.md").write_text("local-a\n")
            (local / "b").mkdir()
            (local / "b/SKILL.md").write_text("new-b\n")
            env = {
                "SYNC_SKILLS_REPO": str(repo),
                "SYNC_SKILLS_LOCAL_DIR": str(local),
                "SYNC_SKILLS_CONFIG": str(root / "config"),
            }
            with patch.dict(os.environ, env), patch.object(sync_skills, "push_repo"):
                sync_skills.add_skill("b")
            self.assertEqual((local / "a/SKILL.md").read_text(), "local-a\n")

    def test_remove_does_not_overwrite_another_local_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            local = root / "local"
            repo.mkdir()
            init_repo(repo, {"a": "repo-a\n", "b": "repo-b\n"})
            (local / "a").mkdir(parents=True)
            (local / "a/SKILL.md").write_text("local-a\n")
            (local / "b").mkdir()
            (local / "b/SKILL.md").write_text("local-b\n")
            env = {
                "SYNC_SKILLS_REPO": str(repo),
                "SYNC_SKILLS_LOCAL_DIR": str(local),
                "SYNC_SKILLS_CONFIG": str(root / "config"),
            }
            with patch.dict(os.environ, env), patch.object(sync_skills, "push_repo"):
                sync_skills.remove_skill("b")
            self.assertEqual((local / "a/SKILL.md").read_text(), "local-a\n")
            self.assertFalse((local / "b").exists())

    def test_tracked_symlink_is_not_deployed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            local = root / "skills"
            target = root / "external"
            local.mkdir()
            target.mkdir()
            (target / "SKILL.md").write_text("demo\n")
            source = local / "demo"
            source.symlink_to(target, target_is_directory=True)
            lock = {
                "skills": {
                    "demo": {
                        "sourceType": "github",
                        "source": "owner/repo",
                        "sourceUrl": "https://example.com/owner/repo.git",
                        "skillPath": "skills/demo/SKILL.md",
                        "skillFolderHash": "a" * 40,
                    }
                }
            }
            (root / ".skill-lock.json").write_text(json.dumps(lock))
            entry = sync_skills.manifest_entry_for_add(local, "demo", source)
            self.assertIs(entry.get("deploy"), False)
            self.assertTrue(source.is_symlink())

    def test_missing_skill_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            with self.assertRaisesRegex(sync_skills.SyncError, "缺少 SKILL.md"):
                sync_skills.require_skill_snapshot(path, "demo")

    def test_missing_base_tree_is_fetched_from_shallow_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            upstream = root / "upstream"
            upstream.mkdir()
            git(upstream, "init", "-q")
            git(upstream, "config", "user.name", "test")
            git(upstream, "config", "user.email", "test@example.com")
            skill = upstream / "skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text("base\n")
            git(upstream, "add", ".")
            git(upstream, "commit", "-q", "-m", "base")
            base_tree = git(upstream, "rev-parse", "HEAD:skill")
            (skill / "SKILL.md").write_text("latest\n")
            git(upstream, "commit", "-q", "-am", "latest")

            mirror = root / "mirror"
            git(root, "clone", "-q", "--depth", "1", upstream.as_uri(), str(mirror))
            missing = subprocess.run(
                ["git", "cat-file", "-e", f"{base_tree}^{{tree}}"],
                cwd=mirror,
                capture_output=True,
            )
            self.assertNotEqual(missing.returncode, 0)
            sync_skills.ensure_base_tree(mirror, base_tree)
            git(mirror, "cat-file", "-e", f"{base_tree}^{{tree}}")


if __name__ == "__main__":
    unittest.main()
