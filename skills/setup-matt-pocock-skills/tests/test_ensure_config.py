import json
import os
from contextlib import ExitStack
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ensure-config.py"
CONFIGS = ("issue-tracker.md", "triage-labels.md", "domain.md")


class EnsureConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project with spaces"
        self.project.mkdir()

    def run_cli(self, *extra, root=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--project-root", str(root or self.project), *extra],
            cwd=self.temp.name,
            env={**os.environ, "PATH": ""},
            text=True,
            capture_output=True,
        )

    def test_defaults_work_without_tracker_tools_or_a_git_repository(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(set(report["created"]), {f".planning/{n}" for n in CONFIGS})
        tracker = (self.project / ".planning/issue-tracker.md").read_text()
        self.assertIn("Local Markdown", tracker)
        self.assertIn("<PLAN_DIR>/tickets/", tracker)
        self.assertIn("<PLAN_DIR>/wayfinder/", tracker)
        self.assertNotIn(".scratch/", tracker)
        domain = (self.project / ".planning/domain.md").read_text()
        self.assertIn(".planning/adr/", domain)
        self.assertNotIn("<PLAN_DIR>/adr/", domain)
        self.assertEqual({p.name for p in self.project.iterdir()}, {".planning"})
        self.assertEqual({p.name for p in (self.project / ".planning").iterdir()}, set(CONFIGS))

    def test_repeated_runs_preserve_custom_configuration_bytes_and_mtime(self):
        self.assertEqual(self.run_cli().returncode, 0)
        paths = [self.project / ".planning" / n for n in CONFIGS]
        for p in paths:
            p.write_bytes(b"custom tracker and paths\r\n\xe4\xbf\x9d\xe7\x95\x99\n")
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths}
        result = self.run_cli("--tracker", "github")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["created"], [])
        self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths})

    def test_partial_config_preserves_tracker_and_fills_only_missing_files(self):
        planning = self.project / ".planning"
        planning.mkdir()
        tracker = planning / "issue-tracker.md"
        tracker.write_text("# Issue tracker: Linear\nUse the configured MCP.\n")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(tracker.read_text(), "# Issue tracker: Linear\nUse the configured MCP.\n")
        self.assertEqual(set(json.loads(result.stdout)["created"]), {
            ".planning/triage-labels.md", ".planning/domain.md"
        })

    def test_legacy_configs_are_carried_forward_without_changing_them(self):
        legacy = self.project / "docs/agents"
        legacy.mkdir(parents=True)
        for name in CONFIGS:
            (legacy / name).write_bytes(f"existing {name}\r\n".encode())
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in CONFIGS:
            self.assertEqual((self.project / ".planning" / name).read_bytes(), (legacy / name).read_bytes())
        self.assertEqual(len(json.loads(result.stdout)["imported"]), 3)

    def test_explicit_remote_choice_seeds_template_without_running_remote_commands(self):
        for tracker in ("github", "gitlab"):
            root = self.project / tracker
            root.mkdir()
            result = self.run_cli("--tracker", tracker, root=root)
            self.assertEqual(result.returncode, 0, result.stderr)
            text = (root / ".planning/issue-tracker.md").read_text()
            self.assertIn("GitHub" if tracker == "github" else "GitLab", text)
            self.assertEqual({p.name for p in root.iterdir()}, {".planning"})

    def test_invalid_destinations_fail_before_creating_other_configs(self):
        planning = self.project / ".planning"
        planning.mkdir()
        (planning / "domain.md").mkdir()
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((planning / "issue-tracker.md").exists())
        self.assertFalse((planning / "triage-labels.md").exists())
        missing = self.project / "missing-root"
        result = self.run_cli(root=missing)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(missing.exists())

    def test_concurrent_runs_preserve_the_same_complete_configuration(self):
        command = [sys.executable, str(SCRIPT), "--project-root", str(self.project)]
        with ExitStack() as stack:
            processes = [stack.enter_context(subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )) for _ in range(4)]
            results = [p.communicate(timeout=15) for p in processes]
            for p, (stdout, stderr) in zip(processes, results):
                self.assertEqual(p.returncode, 0, stderr)
                json.loads(stdout)
        self.assertEqual({p.name for p in (self.project / ".planning").iterdir()}, set(CONFIGS))
        self.assertTrue((self.project / ".planning/issue-tracker.md").read_text().startswith("# Issue tracker: Local Markdown"))


if __name__ == "__main__":
    unittest.main()
