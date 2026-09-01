import importlib.util
import json
import os
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
