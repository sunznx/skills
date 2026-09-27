---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Use `planning-with-files` to resolve a named, gated plan. If multiple plans exist and `PLAN_ID` is not bound, stop rather than choosing one. Spin up a **background agent** to do the research, so you keep working while it reads. Pass the selected `<PLAN_DIR>` and the research question to that agent.

Its job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it as `<PLAN_DIR>/research/<topic-slug>.md` without overwriting an earlier report. Return the path and a brief summary to the parent agent; the parent records the result in `<PLAN_DIR>/findings.md`.
