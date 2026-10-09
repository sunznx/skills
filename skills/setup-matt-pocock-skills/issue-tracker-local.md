# Issue tracker: Local Markdown

Issues and specs live as Markdown files in the selected Planning with Files task directory (`<PLAN_DIR>`). Resolve the named, gated plan first; `<PLAN_DIR>` is the resulting path, not a literal directory name. Configuration is per-project under `.planning/`, while task artifacts belong to that selected plan.

## Conventions

- One task per selected plan: `.planning/<PLAN_ID>/`
- The spec is `<PLAN_DIR>/spec.md`
- Implementation issues are one file per ticket at `<PLAN_DIR>/tickets/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Save the spec to `<PLAN_DIR>/spec.md` or one implementation ticket per file under `<PLAN_DIR>/tickets/`. These files are the tracker; publishing does not create a second copy.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Implementation ticket completion

Work blockers-first. A `Blocked by:` line identifies prerequisite tickets. Resolve each ticket by checking its acceptance criteria, recording test evidence, and setting `Status: done`. A dependent ticket enters the frontier only after its blockers are done and their changes are integrated.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `<PLAN_DIR>/wayfinder/map.md` (the Notes / Decisions-so-far / Fog body).
- **Child ticket**: `<PLAN_DIR>/wayfinder/tickets/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `<PLAN_DIR>/wayfinder/tickets/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.
