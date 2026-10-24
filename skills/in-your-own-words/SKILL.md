---
name: in-your-own-words
description: "Restate in your own words what you think the user's goals are and what problem they're trying to solve, as an illustrated HTML page. Use for /in-your-own-words."
---

Restate in your own words what you think the user's goals are and what problem they're trying to solve.

Separate what the user said from what you infer. Name any gap that blocks a confident restatement. Keep it short.

## Illustrated page

Turn the restatement into one HTML page where pictures carry the meaning and text is short captions beside them, so the user can check your understanding at a glance.

- Open with the goal in one sentence.
- Draw the problem: where the user is now, where they want to be, and what stands in the way. Pick the picture that fits — a before/after, a flow of boxes and arrows, or a map of the parts involved.
- Draw what the user said and what you infer in two distinct styles, such as solid versus dashed outlines, and keep a legend on the page.
- Put each blocking gap in a highlighted box, phrased as a question the user can answer.
- Use the user's own words and the real names of files, systems and people from the conversation.
- Make it a single file with inline CSS and inline SVG. If a diagram library is needed, load a pinned version from a CDN. The page works on desktop and mobile, in light and dark mode.

## Planning with Files

1. Use `planning-with-files` to select or create this task's plan as `<PLAN_DIR>`; when another workflow invokes this skill, use that workflow's selected plan.
2. Read `task_plan.md`, the latest entries in `progress.md`, and the parts of `findings.md` that bear on the goal, alongside the conversation.
3. Write the restatement to `<PLAN_DIR>/in-your-own-words.md`, replacing any earlier version; other skills read this file, and the page and the reply are built from it.
4. Create `<PLAN_DIR>/in-your-own-words/` and save the page as `<PLAN_DIR>/in-your-own-words/in-your-own-words-{description}.html`; never overwrite an earlier page. Log both paths with one line in `<PLAN_DIR>/progress.md`, then open the page:

   ```
   Bash(open "<PLAN_DIR>/in-your-own-words/in-your-own-words-{description}.html")
   ```

5. Reply with the short restatement and the page's absolute path.
6. If `planning-with-files` stops to ask for a `PLAN_ID`, restate from the conversation only, write nothing, and end with the question.
