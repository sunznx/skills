---
name: retro-lint
description: Turns repeatable mistakes from a session retrospective into native project checks and records evidence, commands, and scope under .planning/lint/. Use to implement retrospective findings or enforce a correction. For discussion alone, propose checks without changing files.
---

# Retro Lint

Make retrospective rules discoverable in `.planning/lint/README.md` and enforce them with executable checks in the project's existing stack. Do not introduce a general-purpose lint engine.

## Gather evidence and select checks

1. Use the user-specified session, or the current session if none is specified. Reuse any candidate findings from `retro` and fill the evidence gaps. Keep the actual correction, relevant paths or diff, consequences, and existing fix. Separate observed facts, recommendations, and user decisions. Follow the active authorization and search boundaries for other local session logs.
2. Use `git rev-parse --show-toplevel` to find the owning repository. Read its instructions, check configuration, build commands, hooks, and CI. Handle separate repositories independently. Outside Git, use the project directory specified by the user; ask if it is unknown, and inspect only known paths. Check `.planning/lint/README.md` for existing coverage.
3. Remove the structural cause first, then consider types, native lint, or a behavior test. Repair a disconnected or broken check at its existing entry point. If an equivalent check already works, update the index instead of duplicating it. Ask before expanding the scope of an architecture change.
4. Enforce a correction when it occurs a second time. Enforce a first occurrence when the detection boundary and impact are clear. Keep judgment calls as recommendations and explain when reliable detection is not possible. For discussion, read-only review, or a request for candidates, report here without creating files or checks.

## Implement and prove

1. Read and follow `tdd` before adding a check. Prefer existing tools or installed dependencies and record what they cover. Use the native parser for syntax and dependencies. Use text matching only when the rule is defined by the text itself.
2. Put new standalone rules, verification examples, and a short rationale under `.planning/lint/<rule-name>/`. Keep native rules or tests at the path required by their tools and link to the sole implementation from the index. Organize by mistake class, not by session.
3. Reduce a real failure to a minimal violating example. Confirm the selected check fails for the intended reason. Implement or connect the check, then verify that it rejects the violation and accepts both a valid example and the real fix. Use native rule-test tools when available. Do not test wording or index-only edits, or block legitimate alternatives to match one past example.
4. Report the rule ID, location, cause, and concrete fix. Use the project's exception mechanism to scope exceptions and record the reason. Do not disable the rule globally to hide failures.
5. Connect the check to existing commands, hooks, and CI where applicable. Run the affected checks. Confirm whether `.planning/lint/` is ignored and whether CI receives the implementation and fixtures. Do not force-add ignored files. If the rule runs locally only, state that limit and propose a versioned home.

## Maintain the index

Create or update `.planning/lint/README.md` only when there is a check to record. Include:

- Project root and the exact verified command.
- Rule ID, intent, and applicable files or modules.
- Relative links to the sole implementation, verification example, and short rationale. Record the real error, mechanism, and fix without copying the conversation or sensitive data.
- Observed status: locally verified, connected to native commands, and configured in hooks or CI. Do not claim remote CI verification without observing it.

Keep valid entries and remove obsolete checks and index entries when types or architecture replace them. If no candidate can be enforced, explain why without creating an empty directory.

Read the index and applicable rules before later code changes. Run the affected checks after editing. A broken command or link is a finding, not a pass.

Reuse the project's existing instructions. If they need to mention the index, use `update-agents-md` to add only when to read it and what to run. Keep the rules themselves in one place.

## Report

Order mistake classes by severity. Give the evidence, selected mechanism, and reason for choosing it. Name the index, failing and passing examples, command, and unverified scope. Distinguish local files, versioned changes, and CI execution. Documentation alone is not enforcement.
