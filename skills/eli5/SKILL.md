---
name: eli5
description: Explain a topic like I'm a 5 year old. Use when the user types /eli5 <topic> or asks for a dead-simple picture explainer of how something works.
---

# eli5

Explain like I'm someone who knows nothing about this topic, using a HTML artifact with big pictures and few words.

Topic: $ARGUMENTS

## Plan and artifacts

Before writing the HTML, use `planning-with-files` to resolve this task's named, gated plan through [plan resolution](../pwf-artifact/references/plan-resolution.md). Use the selected absolute plan directory as `<PLAN_DIR>` and keep its `PLAN_ID`. When another workflow invokes this skill, use that workflow's selected plan.

Create `<PLAN_DIR>/eli5/` and save the explainer as `<PLAN_DIR>/eli5/eli5-{description}.html`; never overwrite an earlier one. Record its path and the one-line takeaway in the selected plan's `findings.md` and `progress.md`, then open it for the user:

```
Bash(open "<PLAN_DIR>/eli5/eli5-{description}.html")
```
