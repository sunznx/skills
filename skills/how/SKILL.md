---
name: how
description: "Use for \"how does X work\", code walkthroughs before changing something, and placement / ownership / layering questions (\"where should this live\", \"which package owns this\", \"is this the right layer\"). Explains subsystem architecture, runtime flow, onboarding mental models. Use why for motivation."
---

# How

Explore the codebase to answer "how does X work?" questions.

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

## 1. Explain

Use one read-only exploration and explanation pass. Delegate only when the task permits subagents; otherwise perform it in the current agent. Give it the user's question and this brief:

> You are writing an architectural explanation for a senior engineer. Explore the codebase and write an explanation that a senior engineer unfamiliar with this area could read and walk away with a solid mental model. They should understand the architecture well enough to start working in it confidently. You have read-only access to the codebase.

## 2. Present

Present the subagent's output. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.

## Plan and artifacts

Use `planning-with-files` to select or create this task's plan as `<PLAN_DIR>`; when another workflow (such as `explain`) invokes this skill, use that workflow's selected plan. After presenting, save the presented explanation as a page, `<PLAN_DIR>/how/<topic-slug>.html`, without overwriting an earlier one. Keep its sections, text and order. Make it a single file with inline CSS and no external resources; show code, commands and file trees in monospace that scrolls sideways rather than wrapping; it works on desktop and mobile, in light and dark mode. Open it with `open`, give its absolute path, and record that path and a one-line takeaway in the selected plan's `findings.md` and `progress.md`. Keep any delegated evidence gathering read-only; only the main agent updates the plan.


Use the retained `references/explainer-prompt.md` as the output guide; omit its explorer-findings placeholders when gathering evidence directly.
