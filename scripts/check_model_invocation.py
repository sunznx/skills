#!/usr/bin/env python3
"""Check that every skill can be invoked by the model in Claude and Codex.

Usage: python3 scripts/check_model_invocation.py [SKILLS_DIR]
SKILLS_DIR defaults to this repository's skills/; pass ~/.agents/skills or ~/.claude/skills to check a deployment.
"""

import re
import sys
from pathlib import Path

# Claude refuses the Skill tool for these; Codex skips them for implicit invocation.
CLAUDE_FLAG = re.compile(r"^disable-model-invocation:\s*['\"]?true['\"]?\s*$", re.IGNORECASE)
CODEX_FLAG = re.compile(r"^\s*allow_implicit_invocation:\s*['\"]?false['\"]?\s*$", re.IGNORECASE)


def frontmatter(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    for end, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return lines[1:end]
    return []


def main() -> int:
    skills = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path(__file__).parents[1] / "skills"
    errors = []
    # A leading "*" follows the symlinked skill dirs in ~/.claude/skills; a bare "**" would not.
    skill_files = sorted(skills.glob("*/**/SKILL*.md"))
    codex_files = sorted(skills.glob("*/**/agents/openai.yaml"))
    for path in skill_files:
        if any(CLAUDE_FLAG.match(line) for line in frontmatter(path.read_text(encoding="utf-8"))):
            errors.append(f"{path}: remove `disable-model-invocation: true` from frontmatter")
    for path in codex_files:
        if any(CODEX_FLAG.match(line) for line in path.read_text(encoding="utf-8").splitlines()):
            errors.append(f"{path}: set `allow_implicit_invocation: true`")
    if not skill_files:
        errors.append(f"no SKILL*.md found under {skills}")
    print("\n".join(errors) if errors else f"ok: {skills} ({len(skill_files)} SKILL files, {len(codex_files)} openai.yaml)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
