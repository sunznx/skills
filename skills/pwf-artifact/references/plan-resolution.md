# Plan resolution

Shared rule for every skill that keeps its work in a Planning with Files plan. Skills link here instead of restating it. The scripts below live in the installed `planning-with-files` skill's `scripts/` directory (a plugin install exposes them under `${CLAUDE_PLUGIN_ROOT}/scripts/`); run them from the project root.

1. **Bound.** `PLAN_ID` is set, or the user named a plan: resolve it with `PLAN_ID=<id> sh scripts/resolve-plan-dir.sh` and use that directory. A selector that resolves to nothing is a stop: correct it with the user; do not fall back to another plan or create a replacement.
2. **Ambiguous.** Existing plans clearly belong to this task, but you cannot tell which one: stop and ask the user for the `PLAN_ID`.
3. **New.** No existing plan matches this task: run `sh scripts/init-session.sh --gated "<task name>"`, take the `PLAN_ID=<id>` line it prints, and continue in that plan.

Match by task, not by count. Seventy unrelated plans still mean rule 3. List plans with `sh scripts/set-active-plan.sh --list`, then match the task against each plan's directory name and the goal at the top of its `task_plan.md` (case-insensitive substring; the heading may be `## Goal`, `## 目标`, or the file's first heading). `PWF_PLAN_AMBIGUOUS_V1` from `resolve-plan-dir.sh --check-ambiguity` only says more than one plan exists; it does not pick rule 2. The shared `.active_plan` pointer is not a session binding.

`PLAN_ID` set inside a tool subprocess does not reach the host's hooks. After choosing or creating a plan, pass `PLAN_ID=<id>` (and `PWF_PLAN_ROOT=<project root>` when the shell runs elsewhere) on every command that resolves it. For hook injection, tell the user to `export PLAN_ID=<id>` and restart the session.

Gated is the default mode for new plans. Never reinitialize an existing plan to change its mode, and preserve other plans and legacy project-root planning files.
