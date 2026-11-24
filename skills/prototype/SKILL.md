---
name: prototype
description: Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Select the plan and artifact directory

Before building, use `planning-with-files` to select or create a plan. Reuse the calling workflow's plan when it supplies one. Keep its `PLAN_ID` and absolute `<PLAN_DIR>` when resuming or handing off.

Put each prototype in `<PLAN_DIR>/prototype/<slug>/`. Reuse that directory when iterating on the same question; use a new slug for another prototype and add a numeric suffix if the path is taken. Keep all prototype source, fixtures, launch files, and evidence inside that directory. Read the app for context without adding prototype files to its source tree.

## Pick a branch

Identify which question is being answered, using the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a single shareable HTML file (free-play buttons plus tabbed guided walkthroughs) that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
- **"What should this look like?"** → [UI.md](UI.md). Build several structurally different UI variants in one isolated preview, switchable via a URL search parameter and a floating bar.

The two branches produce very different artifacts, so getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user isn't reachable, default to whichever branch better matches the surrounding code (a backend module → logic; a page or component → UI) and state the assumption at the top of the prototype.

## Rules that apply to both

1. **Label the prototype.** Show the question and mark the preview as non-production.
2. **Make it easy to run.** Open the HTML entry directly, or provide one command for a local preview that runs from the prototype directory.
3. **Keep state in memory by default.** If the question is about persistence, use a disposable local file or a scratch database scoped to the prototype. Keep local data in the prototype directory.
4. **Skip the polish.** No tests, no error handling beyond what makes the prototype _runnable_, no abstractions. The point is to learn something fast.
5. **Surface the state.** After every action (logic) or on every variant switch (UI), print or render the full relevant state so the user can see what changed.
6. **Verify and record.** Launch the actual preview and exercise the interaction that answers the question. Record the question, verdict, and any open decision in the plan's `findings.md`. Record the artifact path, exact launch command or URL, and observed result in `progress.md`. If user feedback is still needed, say what remains open. Keep the prototype in the plan for review; implement the accepted decision separately.
