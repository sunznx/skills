---
name: update-agents-override-md
description: Creates or updates a directory's AGENTS.override.md. Use for directory exceptions, local overrides, or a same-directory AGENTS.md that is shadowed. Global overrides have a separate workflow.
---

# Update directory overrides

Limit the exception to the directory that needs it. Preserve the baseline that still applies there.

## Workflow

1. **Read the writing rules.** Use `writing-for-agents`. Identify the behavior the exception changes, its directory, and its duration. For temporary exceptions, name the restore condition. For a permanent project convention, prefer `update-agents-md` on the governing baseline.
2. **Locate the override.** Use the specified directory or the current directory. The filename is `AGENTS.override.md`. Run `git rev-parse --show-toplevel` to find project boundaries. Read the target, same-directory `AGENTS.md`, and global and ancestor instructions. In Git, inspect `git status --short`, `git diff -- PATH`, and relevant descendant overrides. Record the absolute path, actual loading chain, and existing edits. Resolve symlinks and confirm scope before editing.
3. **Check replacement semantics.** According to the [Codex AGENTS.md documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md), Codex selects one instruction file per directory: a nonempty override takes precedence over the baseline. Ancestor files remain in the chain. The two same-directory files are not automatically merged. If behavior is uncertain, use `openai-docs` for Codex and official references for other clients. Identify the replaced file, retained ancestors, and descendants with their own rules.
4. **Write the exception.** Specify its condition, replacement action, and completion criteria. To retain a same-directory baseline, explicitly tell the agent to read the real `AGENTS.md` path and follow rules not replaced here. Identify the replaced rules. Verify the read step; do not assume the client imports both files. Use conditional pointers for branch-only material and check for loops. Leave ancestor rules with their owners and preserve unrelated rules and edits.
5. **Walk through entry and exit.** Cold-read the result and check when the exception matches, when it does not, and how to restore the baseline. Resolve baseline pointers and check that each conflict yields one action and every retained constraint still has a source. Run safe read-only checks and mark the rest as a walkthrough. For a temporary override, document removal of a newly created override or reversal of only this change in an existing file. Apply edits already authorized; describe future restoration without performing it early.

## Report

Give the path, replaced rules, retained baselines, restore condition, and walkthrough results. Inspect the target diff. If auto-discovery needs verification, have the user check the source in a new session in the target directory and distinguish that from the checks already run.
