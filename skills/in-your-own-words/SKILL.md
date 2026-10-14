---
name: in-your-own-words
description: "Restate in your own words what you think the user's goals are and what problem they're trying to solve. Use for /in-your-own-words."
disable-model-invocation: true
---

Restate in your own words what you think the user's goals are and what problem they're trying to solve.

Separate what the user said from what you infer. Name any gap that blocks a confident restatement. Keep it short.

## Planning with Files

1. Resolve the plan with `planning-with-files`'s `resolve-plan-dir.sh` (`PLAN_ID` or `PWF_PLAN_ROOT`). Use only an existing `.planning/<PLAN_ID>/`; never create one.
2. With a plan, read `task_plan.md`, the latest entries in `progress.md`, and the parts of `findings.md` that bear on the goal, alongside the conversation.
3. Write the restatement to `<PLAN_DIR>/in-your-own-words.md`, replacing any earlier version, and log its path with one line in `<PLAN_DIR>/progress.md`. The file and the reply say the same thing.
4. No unique plan: restate from the conversation only, write nothing, and end with one line naming the `PLAN_ID=<id>` to set if the user wants it saved.
