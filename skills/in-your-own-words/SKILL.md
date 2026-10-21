---
name: in-your-own-words
description: "Restate in your own words what you think the user's goals are and what problem they're trying to solve. Use for /in-your-own-words."
---

Restate in your own words what you think the user's goals are and what problem they're trying to solve.

Separate what the user said from what you infer. Name any gap that blocks a confident restatement. Keep it short.

## Planning with Files

1. Use `planning-with-files` to select or create this task's plan as `<PLAN_DIR>`; when another workflow invokes this skill, use that workflow's selected plan.
2. Read `task_plan.md`, the latest entries in `progress.md`, and the parts of `findings.md` that bear on the goal, alongside the conversation.
3. Write the restatement to `<PLAN_DIR>/in-your-own-words.md`, replacing any earlier version, and log its path with one line in `<PLAN_DIR>/progress.md`. The file and the reply say the same thing.
4. If `planning-with-files` stops to ask for a `PLAN_ID`, restate from the conversation only, write nothing, and end with the question.
