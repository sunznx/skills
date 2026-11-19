---
name: recall
description: Reconstructs recent work from Planning with Files and checks it against Git, highlighting drift. Use before starting or resuming work after a gap.
argument-hint: "Topic, PLAN_ID, or date range (optional)"
---

# Recall

Rebuild the work context from PWF plans, verify their claims against Git, and report the current state. The plan is the record; Git is the current state. Lead with discrepancies.

1. Choose the right workflow. Use `human-context-rebuild` for lost context within the current conversation, `handoff` for a handoff document, and `in-your-own-words` to restate the user's goal. Use this skill to recover and verify plan state.
2. Select plans under `.planning/<id>/` with the `planning-with-files` scripts from the project root:
   - If `PLAN_ID` or `PWF_PLAN_ROOT` is set, use `resolve-plan-dir.sh` and read only the selected plan.
   - Without a pin, use `set-active-plan.sh --list`. If the user supplied a topic, match it case-insensitively as a substring of the plan directory name and the goal near the top of `task_plan.md` (for example, `## Goal` or `## 目标`; otherwise the first heading). With no topic, select plans with incomplete phases and those whose `task_plan.md` changed in the past seven days.
   - If the user says all, include all plans.

   Tell the user which plans you selected in their language, then continue. Reapply selection if they correct the scope.
3. For each selected `<PLAN_DIR>/`, read all of `task_plan.md`, recent entries at the end of `progress.md`, and sections of `findings.md` about remaining phases or decisions. Read `handoff.md` and `in-your-own-words.md` if present. For other files, inspect names only.
4. Compare the plans with `git status --short`, `git diff --stat`, and `git log --oneline --since="<date> 00:00"`. Use the earliest selected plan's directory date, or its `task_plan.md` modification date if undated. Include midnight so Git does not omit earlier commits that day. When `gh` is available and a plan mentions a PR, run `gh pr view <N>`. Check each cited file, branch, commit, and PR against the results. Read a diff only when needed. Attribute a change to a plan by what it does, not just its path. Mark other uncommitted changes as unattributed. Each phase must map to an evidence row and label.
5. Follow the report contract below. Apply `unslop` and write in the user's language.
6. If exactly one plan is in scope, save the report to `<PLAN_DIR>/recall/recall.html`. Use `recall-2.html`, `recall-3.html`, and so on rather than overwriting. Keep the four report sections in order. Make evidence labels visible and drift the most prominent. Use a standalone HTML file with inline CSS, no external resources, and support for desktop, mobile, light, and dark modes. Record the path in `progress.md`, open it with `open`, and report the absolute path. Report drift without editing `task_plan.md` unless the user decides to update it.

Before reading requested session history or external systems such as issues or chat, name the source and date range and obtain approval. Known session roots are `~/.claude/projects/<project-path-with-slashes-replaced-by-hyphens>/` for Claude Code and `~/.codex/sessions/` for Codex. Route external sources through `why`.

## Report contract

Use four sections in order: overview, evidence, issues, and next step. Translate the headings and labels into the user's language when needed.

- **Overview:** At most five points on the goal and current state. List unattributed uncommitted changes separately so they can be isolated before committing.
- **Evidence:** Start each row with a status label: `[Committed <sha>]`, `[Merged #N]`, `[PR #N open]`, `[Verified, not committed]`, `[In progress]`, `[Not started]`, `[Reverted <sha>]`, `[No Git artifact]`, or `[Drift: <one sentence>]`. Use `[No Git artifact]` for research or comparisons that do not change the repository. Drift includes disagreement between plan and Git, contradictory phase markers inside the plan, and conclusions superseded by later work. With one plan, use a row per phase. With several, use a row per plan and split it when phase labels differ.
- **Issues:** At most five points from the Errors table, repeated failures in progress, or risks found during verification. Include what the next session needs to avoid repeating a failure.
- **Next step:** One action from `## Next Step`, or the first incomplete phase or open decision. Confirm it against Git. If multiple plans are unpinned, name the `PLAN_ID=<id>` to set.

Cite plan and file paths, commit SHAs, and PR numbers.
