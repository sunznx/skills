---
name: update-agents-md
description: Creates or updates project and subdirectory AGENTS.md files. Use to record durable project conventions or revise a specified AGENTS.md. Directory overrides and global instructions have separate workflows.
---

# Update project AGENTS.md

Put durable conventions in the directory they govern. A new reader should be able to find the rule, carry it out, and tell when the work is complete.

## Workflow

1. **Read the writing rules.** Use `writing-for-agents` for pointers, information hierarchy, completion criteria, and pruning. Identify the requested behavior and the existing constraints that must remain. Keep one-task progress and temporary decisions in the task record.
2. **Locate the scope.** Use the requested path. Otherwise run `git rev-parse --show-toplevel` and use the repository root's `AGENTS.md`, or the current directory outside Git. Put module-only rules in that module. Record the absolute path and scope and read the existing text. In Git, check `git status --short` and `git diff -- PATH` first. Treat existing edits as the baseline.
3. **Check which files load.** Read global instructions and known instruction files from the project root to the target directory, and relevant descendant overrides. See the [Codex AGENTS.md documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md); use `openai-docs` if the Codex setup is unclear, and verify other clients separately. If a nonempty same-directory `AGENTS.override.md` shadows the requested file, keep an explicitly requested `AGENTS.md` target and report the shadowing. Use `update-agents-override-md` when the goal is to change the active instructions. Name the files actually read in the target branch, not just the file you found.
4. **Edit from evidence.** Use `rg` inside Git worktrees to locate implementation, configuration, and docs. Outside them, read known paths only. Check the actual commands, paths, and entry points before writing. Ask about intent only when the environment cannot answer. Change the relevant text and preserve unrelated constraints and existing edits. Link a fact visible in one command or file with the condition for looking it up. Inline constraints needed for every task. Include the documentation criteria below for feature-module development rules. Resolve a symlink before editing and clarify ownership if its target is out of scope.
5. **Follow the result.** Read the finished file and its required references as if starting a real task. Check each changed rule's trigger, action, and completion criteria. Run safe read-only commands. Walk through side effects with examples and say what was not executed. Check a matching and a nonmatching case, link targets, and preserved constraints. Fix failures, repeat the affected walkthrough, and inspect the target diff.

## Documentation and knowledge base

Include related technical docs and beginner-facing knowledge-base articles in the completion criteria for feature-module development. Update them when adding, changing, or removing the feature.

- Locate existing docs, the knowledge base, navigation, and check commands. Use their real entry points. Follow project documentation rules; leave only triggers, pointers, and completion criteria in `AGENTS.md`. Identify a missing knowledge base rather than treating technical docs as a user guide. Creating the first guide and directory belongs to the feature's documentation work.
- Technical docs describe interfaces, configuration, behavior, and limits. Organize the knowledge base around user tasks. Include supported screens, requirements, permissions, entry points, steps, visible results, and common failures. State data effects and recovery before a consequential step.
- Verify names, buttons, and capabilities against the implementation. Separate shipped, planned, and unverified behavior. Preserve the project's localized editions, navigation, and link conventions.
- Report the changed pages and checks actually run. For an internal change, give the concrete reason the knowledge base did not need an update. List required but unfinished docs as unfinished.

## Report

Report the target path, scope, behavior changes, and walkthrough results. Distinguish a written file from one a client loaded. Current-session walkthroughs do not prove automatic reload; Codex normally discovers instructions when starting a session. Name any shadowing, unverified client behavior, or skipped validation.
