---
name: implement-spec
description: "Implement the result of /to-spec and /to-tickets in code."
disable-model-invocation: true
---

You have been provided a spec. This spec should have tickets associated with it, describing how to implement the spec.

Use `planning-with-files` to resolve the named, gated plan. If multiple plans exist and `PLAN_ID` is not bound, stop rather than choosing one. Read `<PLAN_DIR>/spec.md` and `<PLAN_DIR>/tickets/` first when present; fetch linked spec or tickets when those files are absent. Read `.planning/issue-tracker.md`; if it is missing, report the missing path and stop. Read `.planning/domain.md` when present.

The tracker configuration defines how work is resolved, including local ticket files. Record ticket state, integration commits, test commands and results, and the final commit or PR URL in `<PLAN_DIR>/progress.md`.

The goal is the entire spec implemented on a single **integration branch**, with every ticket resolved the way the issue tracker closes work.

The tickets are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tickets which are ready to be grabbed.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers. Give every subagent the same `PLAN_ID`, the absolute `<PLAN_DIR>`, and `PWF_PLAN_ROOT` pointing to the project that owns the plan, even when it runs in a separate worktree. The orchestrator owns the shared planning files; workers report through their own ledgers or assigned files.

**Implementer subagents** should be run in the background where possible for maximum concurrency.

## Steps

1. Read the spec and tickets to understand the task graph and acceptance criteria. Validate that blockers exist and the graph has no cycles. If the spec has no tickets, ask the user to run `/to-tickets` before scheduling implementation.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Save its markdown notes under `<PLAN_DIR>/research/`, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Create the integration branch from the agreed base and record its starting commit as the fixed point for review. If the issue tracker closes work through PRs, or the user asks for one, open a draft PR after the first integration in step 5 (a branch with no commits ahead of its base can't open one), marked as closing the spec and tickets. Follow the repository's PR template and keep the PR in draft until step 8.

4. Use **implementer subagents** to implement each ticket, each in its own worktree on its own branch. Each implementer subagent:
   - receives ownership of its ticket and affected files, knows other agents are working in the codebase, and preserves their edits;
   - confirms its worktree is based on the current integration branch before starting; if it has existing work on another base, preserves that work and rebases onto the integration branch;
   - uses `/tdd` at the spec's agreed seams to build the ticket, runs typechecking and focused tests regularly, and verifies user-visible behavior with the project's repeatable E2E scenario when available;
   - commits only its ticket changes and rebases onto the latest integration branch tip before reporting done, with acceptance evidence and commit references.

5. Once an **implementer subagent** completes, integrate its work with a **merger subagent**. Serialize integrations: synchronize the latest integration branch, rebase the ticket branch onto it, run the relevant checks, then fast-forward the integration branch. Resolve conflicts with `/resolving-merge-conflicts`; preserve unfinished worktrees until resolved. After each rebase or conflict resolution, check `git status` and `git stash list`; identify each stash's purpose and drop only confirmed obsolete entries.

6. Advance the **frontier** only when blocker changes are integrated and their relevant checks pass. Kick off **implementer subagents** for newly available tickets. This allows for maximum concurrency.

7. Once all tickets are integrated, run the full test suite once on the integration branch and record the results. Use `/code-review` from the fixed point recorded in step 3 with the same `PLAN_ID` and `<PLAN_DIR>`. Fix the issues raised in a single **implementer subagent**, integrate those fixes through step 5, and verify the affected behavior before completing review.

8. If a draft PR exists, refresh its description, retain the tracker closing references, and mark it ready for review after checks and review pass. Report that tracker closure is pending merge. Otherwise, resolve each ticket the way the issue tracker closes work, updating local ticket files when they are the tracker, and report the integration branch.

9. Clean up only **implementer subagent** worktrees whose changes are integrated and whose working trees are clean. Preserve any unfinished worktree and report its path and remaining work.
