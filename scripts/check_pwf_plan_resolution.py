#!/usr/bin/env python3
"""Check that skills share one Planning with Files plan-resolution rule.

Usage: python3 scripts/check_pwf_plan_resolution.py [SKILLS_DIR]
SKILLS_DIR defaults to this repository's skills/; pass ~/.agents/skills to check a deployment.
"""

import sys
from pathlib import Path

SHARED = Path("pwf-artifact/references/plan-resolution.md")
# Wording that restates the rule locally; each one drifted from the shared rule before.
FORBIDDEN = (
    "stop rather than choosing one",
    "If multiple plans exist",
    "Bind `PLAN_ID` when multiple plans exist",
    "无法唯一确定计划时",
    "never create one",
    "Ask which task owns the work",
    "若有多个计划且未绑定",
)
# Skills that read an existing plan and survey several when none is bound.
READ_ONLY = {"recall"}


def main() -> int:
    skills = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path(__file__).parents[1] / "skills"
    errors = []
    if not (skills / SHARED).is_file():
        errors.append(f"missing shared rule: {skills / SHARED}")
    for path in sorted(skills.glob("*/**/*.md")):
        if path.parts[len(skills.parts)] == "planning-with-files" or path == skills / SHARED:
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN:
            if phrase in text:
                errors.append(f"{path}: restates plan resolution ({phrase!r}); link {SHARED} instead")
    for path in sorted(skills.glob("*/SKILL*.md")):
        name = path.parent.name
        if name == "planning-with-files" or name in READ_ONLY:
            continue
        text = path.read_text(encoding="utf-8")
        link = "references/plan-resolution.md" if name == SHARED.parts[0] else f"../{SHARED}"
        if "planning-with-files" in text and link not in text:
            errors.append(f"{path}: uses planning-with-files without linking ../{SHARED}")
    print("\n".join(errors) if errors else f"ok: {skills}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
