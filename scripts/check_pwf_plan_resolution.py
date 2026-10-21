#!/usr/bin/env python3
"""Check how skills use Planning with Files.

Each skill states its own convention: select the plan with `planning-with-files`, then keep files in
the three layers below. No skill restates plan resolution or links a shared rule file.

- `.planning/`: project knowledge that outlives any plan (PROJECT_ENTRIES).
- `<PLAN_DIR>/`: the plan's index and handoff files (PLAN_FILES).
- `<PLAN_DIR>/<skill-name>/`: everything a skill produces per run.

Usage: python3 scripts/check_pwf_plan_resolution.py [SKILLS_DIR]
SKILLS_DIR defaults to this repository's skills/; pass ~/.agents/skills to check a deployment.
"""

import re
import sys
from pathlib import Path

# Wording that restates plan resolution locally; each one drifted before.
FORBIDDEN = (
    "pwf-artifact/references",
    "plan-resolution.md",
    "stop rather than choosing one",
    "If multiple plans exist",
    "Bind `PLAN_ID` when multiple plans exist",
    "无法唯一确定计划时",
    "never create one",
    "Ask which task owns the work",
    "若有多个计划且未绑定",
)
# Index files and handoff files that other skills read by fixed path.
PLAN_FILES = {"task_plan.md", "findings.md", "progress.md", "spec.md", "handoff.md", "in-your-own-words.md"}
# Plan subdirectories named by content because several skills read or write them.
SHARED_PLAN_DIRS = {"tickets", "research"}
# Only pwf-artifact saves what the user hands it.
OWNED_PLAN_DIRS = {"artifacts": "pwf-artifact"}
PROJECT_ENTRIES = {"issue-tracker.md", "triage-labels.md", "domain.md", "adr", "out-of-scope", "birdview", ".active_plan"}

PLAN_PATH = re.compile(r"(?:<PLAN_DIR>|\$PLAN_DIR|\$\{PLAN_DIR\})/([^\s`\"')/]+)")
PROJECT_PATH = re.compile(r"(?<![\w>])\.planning/([^\s`\"')/]+)")


def main() -> int:
    skills = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path(__file__).parents[1] / "skills"
    names = {path.name for path in skills.iterdir() if (path / "SKILL.md").is_file()}
    errors = []
    files = sorted(skills.glob("*/**/*.md"))
    for path in files:
        owner = path.relative_to(skills).parts[0]
        if owner == "planning-with-files":
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN:
            if phrase in text:
                errors.append(f"{path}: restates plan resolution ({phrase!r}); say `planning-with-files` selects the plan")
        for entry in PLAN_PATH.findall(text):
            if entry in OWNED_PLAN_DIRS:
                ok = OWNED_PLAN_DIRS[entry] == owner
            else:
                ok = entry in PLAN_FILES or entry in SHARED_PLAN_DIRS or entry in names
            if not ok:
                errors.append(f"{path}: <PLAN_DIR>/{entry} is not a plan file; keep this skill's output in <PLAN_DIR>/{owner}/")
        for entry in PROJECT_PATH.findall(text):
            if entry not in PROJECT_ENTRIES and not entry.startswith(("<", "*")):
                errors.append(f"{path}: .planning/{entry} is not project knowledge; keep it under <PLAN_DIR>/{owner}/")
    print("\n".join(errors) if errors else f"ok: {skills} ({len(files)} files)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
