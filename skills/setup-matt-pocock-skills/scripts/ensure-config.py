#!/usr/bin/env python3
"""Create missing Matt workflow configuration, preserving existing choices."""

import argparse
import json
import os
from pathlib import Path
import tempfile


SKILL_ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ("issue-tracker.md", "triage-labels.md", "domain.md")


def exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def ensure_config(project_root: Path, tracker: str) -> dict:
    root = project_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"Project root must be a directory: {root}")
    planning = root / ".planning"
    if exists(planning) and not planning.is_dir():
        raise ValueError(f"Configuration directory is not a directory: {planning}")

    report = {"created": [], "preserved": [], "imported": []}
    pending = []
    for name in CONFIGS:
        target = planning / name
        relative = f".planning/{name}"
        if exists(target):
            if not target.is_file():
                raise ValueError(f"Existing configuration is not a file: {target}")
            report["preserved"].append(relative)
            continue
        legacy = root / "docs" / "agents" / name
        if exists(legacy):
            if not legacy.is_file():
                raise ValueError(f"Legacy configuration is not a file: {legacy}")
            content = legacy.read_bytes()
            imported = True
        else:
            template = f"issue-tracker-{tracker}.md" if name == "issue-tracker.md" else name
            content = (SKILL_ROOT / template).read_bytes()
            imported = False
        pending.append((target, relative, content, imported))

    if pending:
        planning.mkdir(exist_ok=True)
    for target, relative, content, imported in pending:
        with tempfile.NamedTemporaryFile(dir=planning, prefix=".matt-config-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        try:
            try:
                os.link(temporary, target)
            except FileExistsError:
                if not target.is_file():
                    raise ValueError(f"Existing configuration is not a file: {target}")
                report["preserved"].append(relative)
            else:
                report["created"].append(relative)
                if imported:
                    report["imported"].append(relative)
        finally:
            temporary.unlink()
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True, help="Existing project owning .planning (PWF_PLAN_ROOT).")
    parser.add_argument("--tracker", choices=("local", "github", "gitlab"), default="local", help="Template for a missing tracker config; existing and legacy configs take precedence.")
    args = parser.parse_args()
    try:
        report = ensure_config(args.project_root, args.tracker)
    except (OSError, ValueError) as error:
        parser.exit(1, f"ensure-config: {error}\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
