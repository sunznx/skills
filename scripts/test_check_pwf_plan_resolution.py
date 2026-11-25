import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ProjectKnowledgePaths(unittest.TestCase):
    def test_project_lint_index_is_allowed_but_run_outputs_are_not(self):
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix='.pwf-check-') as directory:
            root = Path(directory)
            skill = root / 'retro-lint'
            skill.mkdir()
            document = skill / 'SKILL.md'
            document.write_text(
                '---\nname: retro-lint\ndescription: Maintain project checks.\n---\n'
                'Read .planning/lint.md and .planning/lint/README.md before changes.\n'
            )
            command = [sys.executable, str(repo / 'scripts/check_pwf_plan_resolution.py'), str(root)]
            accepted = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
            document.write_text(document.read_text() + 'Save this run in .planning/temporary-report/output.md.\n')
            rejected = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(rejected.returncode, 1)
            self.assertIn('.planning/temporary-report is not project knowledge', rejected.stdout)


if __name__ == '__main__':
    unittest.main()
