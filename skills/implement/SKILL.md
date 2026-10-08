---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Use `planning-with-files` to resolve the named, gated plan. If multiple plans exist and `PLAN_ID` is not bound, stop rather than choosing one. Read its `spec.md` or `tickets/` first when present; record test commands, results, and the final commit in `<PLAN_DIR>/progress.md`.

If the user passes a ticket reference, fetch it from the issue tracker and state its title before starting. If the reference is ambiguous, ask.

Call the Skill tool with "tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, call the Skill tool with "code-review" to review the work with the same `PLAN_ID` and `<PLAN_DIR>`.

Commit your work to the current branch.
