---
name: why
description: "Use for 'why does X work this way', 'why we picked Y', design rationale, regressions, postmortems, or data-backed thresholds. Returns a cited read on decisions and tradeoffs. Use how for runtime behavior."
---

# Why

Answer from the record, not the code: read the commits and PR discussions that introduced the target and each later change, and other sources if the trail is thin. Cite what the authors wrote, mark your own inferences as inferences, and say what the record does not answer.

## Plan and artifacts

Use `planning-with-files` to select or create this task's plan as `<PLAN_DIR>`; when another workflow (such as `explain`) invokes this skill, use that workflow's selected plan. After presenting, save the presented read as a page, `<PLAN_DIR>/why/<topic-slug>.html`, without overwriting an earlier one. Keep its sections, text and order, and keep what was found visibly apart from what is inferred. Make it a single file with inline CSS and no external resources; show code, commands and file trees in monospace that scrolls sideways rather than wrapping; it works on desktop and mobile, in light and dark mode. Open it with `open`, give its absolute path, and record that path, the confidence summary, and any Preserve / Change / Avoid / Risk constraints in the selected plan's `findings.md`; log the run in `progress.md`. Only the main agent updates the plan.
