---
name: update-global-agent-md
description: Creates or updates cross-project agent instructions. Use for global AGENTS.md, global AGENTS.override.md, or lasting personal preferences. Default to Codex home unless the user specifies another client or file.
---

# Update global agent instructions

Keep cross-project preferences in the global entry point. Leave project rules in their projects.

## Workflow

1. **Read the writing rules.** Use `writing-for-agents`. For each lasting preference, check whether it holds in another stack or repository. Route project-only constraints to `update-agents-md` and one-task exceptions to the task record.
2. **Locate the effective entry point.** Use the requested client or file. Otherwise use Codex. List candidates with the read-only command below and inspect only those paths and their symlink targets:

   ```bash
   python3 - <<'PY'
   import os
   from pathlib import Path
   root = Path(os.environ.get('CODEX_HOME') or '~/.codex').expanduser().resolve()
   for name in ('AGENTS.override.md', 'AGENTS.md'):
       path = root / name
       print(f'{path} -> {path.resolve()}')
   PY
   ```

   Check nonempty candidates and precedence in the [Codex AGENTS.md documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md). Use `openai-docs` if Codex behavior is unclear and verify other clients separately. Record the client, config root, absolute target, and real file. The Codex filename is `AGENTS.md` even though the skill name uses `agent`.
3. **Choose the layer.** Edit the specified file and report shadowing. To change the active policy, edit the effective file; if none exists in Codex home, create `AGENTS.md`. For a temporary global exception, use `AGENTS.override.md` in the same directory and name the active and restore conditions. If the replaced baseline still applies, name its real path and say to follow its unchanged rules. Check for loops and keep global and project rules distinct.
4. **Edit the preference.** Read the complete target and applicable baseline. If the real file is in Git, check its status and diff. Preserve unrelated rules, existing edits, and symlink structure. Keep only necessary machine paths under their applicable conditions. Put commands, stacks, and repository conventions in the project. Put reusable procedures behind conditional skill pointers. Edit only the requested client's entry point.
5. **Walk through different projects.** Cold-read the result and its required pointers. For each changed rule, walk through two projects with different stacks and one non-Git directory. Confirm the trigger, action, and ownership of project commands. Check override entry, the nonmatching case, and restoration. Existing overrides should revert only this change. Run safe read-only commands, label simulations and unverified cases, fix failures, and inspect the final diff.

## Report

Report the client, absolute paths, cross-project behavior, and verification results. Distinguish writing, manual reading, and automatic loading. A walkthrough checks paths and instructions, not Codex discovery in a new session. Explain how to restore a temporary override.
