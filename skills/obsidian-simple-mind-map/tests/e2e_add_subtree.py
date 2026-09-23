#!/usr/bin/env python3
"""Live Obsidian check: insert 25 nodes into an existing mind map."""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path("/Users/sunx/Dropbox/syncer/apps/obsidian")
CLI = Path(__file__).parents[1] / "scripts/smm_cli.py"


def cli(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(CLI), *args], text=True, capture_output=True, check=False, timeout=60
    )
    if result.returncode:
        raise RuntimeError(f"{' '.join(args)} failed: {result.stderr or result.stdout}")
    return json.loads(result.stdout)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="smm-batch-e2e-", dir=ROOT) as directory:
        source = Path(directory) / "source.md"
        source.write_text("# Root\n")
        source_path = source.relative_to(ROOT).as_posix()
        converted = cli("convert-md", source_path)
        path = converted["path"]
        before = cli("read", path)["nodes"]
        parent_uid = before[0]["uid"]
        tree = {
            "text": "Batch root",
            "children": [
                {"text": "Leaf", "children": [{"text": f"Detail {index}"}]}
                for index in range(12)
            ],
        }
        start = time.monotonic()
        result = cli("add-subtree", path, parent_uid, json.dumps(tree))
        elapsed = time.monotonic() - start
        after = {node["uid"]: node for node in cli("read", path)["nodes"]}
        created = result["nodes"]
        assert len(created) == 25
        assert len(after) == len(before) + 25
        assert all(node["uid"] in after for node in before)
        assert created[0]["text"] == "Batch root"
        assert created[0]["parentUid"] == parent_uid
        for index in range(12):
            leaf, detail = created[2 * index + 1 : 2 * index + 3]
            assert leaf["text"] == "Leaf" and leaf["parentUid"] == created[0]["uid"]
            assert detail["text"] == f"Detail {index}" and detail["parentUid"] == leaf["uid"]
        for node in created:
            actual = after[node["uid"]]
            assert actual["parentUid"] == node["parentUid"]
            assert actual["plainText"] == node["text"]
        print(json.dumps({"ok": True, "nodes": len(created), "seconds": round(elapsed, 2)}))


if __name__ == "__main__":
    main()
