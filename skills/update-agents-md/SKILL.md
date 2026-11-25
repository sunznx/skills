---
name: update-agents-md
description: Creates or updates project and subdirectory AGENTS.md files. Use to record durable project conventions or revise a specified AGENTS.md. Directory overrides and global instructions have separate workflows.
---

# Update project AGENTS.md

Put durable conventions in the directory they govern. A new reader should be able to find the rule, carry it out, and tell when the work is complete.

## Workflow

1. **Read the writing rules.** Use `writing-for-agents` for pointers, information hierarchy, completion criteria, and pruning. Identify the requested behavior and the existing constraints that must remain. Keep one-task progress and temporary decisions in the task record.
2. **Resolve the target at invocation.** Capture the working directory when the skill is invoked. For “this project” or an unspecified target, run `git -C "<invocation directory>" rev-parse --show-toplevel` and use that worktree root's `AGENTS.md`. Outside Git, use `AGENTS.md` in the invocation directory. Use a different file or a module's `AGENTS.md` when the user targets it. Record the absolute path and scope. In Git, check `git status --short` and `git diff -- PATH` in the target worktree before editing. Read the existing file and treat existing edits as the baseline.
3. **Require explicit scope for cross-repository edits.** For each other repository or worktree, edit only when the user explicitly identifies the target and authorizes the change there. Earlier reads or edits, where a rule originated, and documents linked from the rule are context. Keep the invocation target when those references lead elsewhere. Resolve symlinks before writing and confirm that the resolved file is within the authorized scope.
4. **Check which files load.** Read global instructions and known instruction files from the project root to the target directory, and relevant descendant overrides. See the [Codex AGENTS.md documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md); use `openai-docs` if the Codex setup is unclear, and verify other clients separately. If a nonempty same-directory `AGENTS.override.md` shadows the requested file, keep an explicitly requested `AGENTS.md` target and report the shadowing. Use `update-agents-override-md` when the goal is to change the active instructions. Name the files actually read in the target branch, not just the file you found.
5. **Edit from evidence.** Use `rg` inside Git worktrees to locate implementation, configuration, and docs. Outside them, read known paths only. Check the actual commands, paths, and entry points before writing. Ask about intent only when the environment cannot answer. Change the relevant text and preserve unrelated constraints and existing edits. Link a fact visible in one command or file with the condition for looking it up. Inline constraints needed for every task. Include the documentation criteria below for feature-module development rules.
6. **Follow the result.** Read the finished file and its required references as if starting a real task. Check each changed rule's trigger, action, and completion criteria. Run safe read-only commands. Walk through side effects with examples and say what was not executed. Check a matching and a nonmatching case, link targets, and preserved constraints. Fix failures, repeat the affected walkthrough, and inspect the target diff.

### Example: MinisCloud Home Repo

Invoking `$update-agents-md` in the MinisCloud Home Repo with “更新到本项目” targets the Home Repo's `AGENTS.md`. Use that target even after reading or editing Cloud, or when the rule comes from or links to Cloud. The later request “删除 cloud 中的说明” authorizes removing the duplicate from Cloud's `AGENTS.md`. NAS, Client, and older worktrees each require their own explicit edit scope.

## Documentation and knowledge base

Include related technical docs and beginner-facing knowledge-base articles in the completion criteria for feature-module development. Update them when adding, changing, or removing the feature.

- Locate existing docs, the knowledge base, navigation, and check commands. Use their real entry points. Follow project documentation rules; leave only triggers, pointers, and completion criteria in `AGENTS.md`. Identify a missing knowledge base rather than treating technical docs as a user guide. Creating the first guide and directory belongs to the feature's documentation work.
- Technical docs describe interfaces, configuration, behavior, and limits. Organize the knowledge base around user tasks. Include supported screens, requirements, permissions, entry points, steps, visible results, and common failures. State data effects and recovery before a consequential step.
- Verify names, buttons, and capabilities against the implementation. Separate shipped, planned, and unverified behavior. Preserve the project's localized editions, navigation, and link conventions.
- Report the changed pages and checks actually run. For an internal change, give the concrete reason the knowledge base did not need an update. List required but unfinished docs as unfinished.

## Report

Report the target path, scope, behavior changes, and walkthrough results. Distinguish a written file from one a client loaded. Current-session walkthroughs do not prove automatic reload; Codex normally discovers instructions when starting a session. Name any shadowing, unverified client behavior, or skipped validation.
