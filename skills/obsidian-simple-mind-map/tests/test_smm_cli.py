import importlib.util
import json
import re
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts/smm_cli.py"
SPEC = importlib.util.spec_from_file_location("smm_cli", SCRIPT)
smm_cli = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(smm_cli)


class FakeObsidian:
    """Models the operation table the launch code keeps inside Obsidian."""

    def __init__(self, launch_failures: list[str], poll_failures: int = 0) -> None:
        # Each entry decides one launch: "queued" crashes after queuing the
        # operation, "lost" crashes before it, "ok" succeeds.
        self.launch_failures = launch_failures
        self.poll_failures = poll_failures
        self.operations: dict[str, dict] = {}
        self.launches = 0

    def run(self, args: list[str], **_kwargs: object) -> subprocess.CompletedProcess:
        code = args[-1].removeprefix("code=")
        if 'status: "running"' in code:
            self.launches += 1
            key = re.search(r'const key = "([0-9a-f]+)"', code).group(1)
            outcome = self.launch_failures.pop(0) if self.launch_failures else "ok"
            if outcome != "lost":
                self.operations[key] = {"status": "done", "result": "RESULT"}
            if outcome == "ok":
                return subprocess.CompletedProcess(args, 0, '{"status":"started"}', "")
            return subprocess.CompletedProcess(args, 1, "", "GPU process isn't usable")
        if self.poll_failures:
            self.poll_failures -= 1
            return subprocess.CompletedProcess(args, 1, "", "GPU process isn't usable")
        key = re.search(r'operations\["([0-9a-f]+)"\]', code).group(1)
        return subprocess.CompletedProcess(
            args, 0, json.dumps(self.operations.get(key, {"status": "missing"})), ""
        )


class RunEvalTests(unittest.TestCase):
    def run_eval(self, fake: FakeObsidian) -> str:
        with (
            patch.object(smm_cli.shutil, "which", return_value="/usr/local/bin/obsidian"),
            patch.object(smm_cli.subprocess, "run", side_effect=fake.run),
            patch.object(smm_cli.time, "sleep"),
        ):
            return smm_cli.run_eval("vault", "return 1;")

    def test_crash_after_queue_does_not_relaunch(self) -> None:
        fake = FakeObsidian(["queued"])
        self.assertEqual(self.run_eval(fake), "RESULT")
        self.assertEqual(fake.launches, 1)

    def test_crash_before_queue_relaunches(self) -> None:
        fake = FakeObsidian(["lost"])
        self.assertEqual(self.run_eval(fake), "RESULT")
        self.assertEqual(fake.launches, 2)

    def test_poll_crashes_are_retried(self) -> None:
        fake = FakeObsidian([], poll_failures=5)
        self.assertEqual(self.run_eval(fake), "RESULT")

    def test_repeated_launch_loss_fails(self) -> None:
        fake = FakeObsidian(["lost", "lost", "lost"])
        with self.assertRaises(SystemExit):
            self.run_eval(fake)
        self.assertEqual(fake.launches, 3)


if __name__ == "__main__":
    unittest.main()
