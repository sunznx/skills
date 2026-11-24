---
name: to-tickets
description: Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker (edges as text in one file per ticket locally, or native blocking links on a real tracker).
---

# To Tickets

Break a plan, spec, or conversation into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it.

Use `planning-with-files` to select or create this task's plan as `<PLAN_DIR>`; when another workflow invokes this skill, use that workflow's selected plan. Before reading Matt configuration, follow [shared configuration initialization](../setup-matt-pocock-skills/references/ensure-config.md). Read `.planning/issue-tracker.md` and `.planning/triage-labels.md`. Read `.planning/domain.md` when present.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a spec path, an issue number or URL) as an argument, fetch it and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Invoke [BDD synthesis](../bdd/SKILL.md#synthesis-for-specs-and-tickets) in the selected plan. When starting from a spec, resolve the scenario IDs it references through the plan's scenario index. When starting from a plan or conversation, reuse indexed scenarios and add any missing scenarios for confirmed behavior. Bring unresolved references and open BDD decisions that affect a slice into the breakdown review.

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first

</vertical-slice-rules>

Give each ticket its **blocking edges**: the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

Map each applicable BDD scenario to the ticket that delivers or verifies it. For each mapping, record the scenario reference, target environment, test command or manual entry point, and evidence to capture. A scenario can appear in multiple tickets for distinct environments. Flag missing verification details for the breakdown review. Use ordinary acceptance criteria for work without a BDD scenario.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change (rename a column, retype a shared symbol) whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket; green is promised only there.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work
- **BDD acceptance**, when applicable: scenario IDs and target environments

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct: does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Iterate until the user approves the breakdown.

### 5. Save and publish the tickets

Write each approved ticket to `<PLAN_DIR>/tickets/<NN>-<slug>.md` in dependency order, using the per-ticket template below. Then publish according to `.planning/issue-tracker.md`:

- **Local files** → the files in `<PLAN_DIR>/tickets/` are the tracker. Each "Blocked by" lists the numbers/titles it depends on; keep one ticket per file.
- **A real issue tracker (GitHub, Linear, …)** → publish one issue per ticket from those files in dependency order (blockers first) so each ticket's blocking edges can reference real identifiers. Use the platform's native blocking / sub-issue relationship where it has one; otherwise set each issue's "Blocked by" to the blocking issues. If the source was an existing issue, make each ticket its sub-issue using the tracker doc's operation. Apply the `ready-for-agent` triage label unless instructed otherwise. Record published issue URLs beside the corresponding local ticket paths in the plan; keep both copies in sync when revising a ticket.

Use the [BDD reference format](../bdd/SKILL.md#referencing-scenarios) for each destination. Check a BDD acceptance item only when observed evidence satisfies the scenario in the ticket's target environment. Record actual verification in the selected plan's `progress.md` using BDD's evidence convention.

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

Do NOT close or modify any parent issue.

<local-ticket-template>

# <NN>: <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer implementation list.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None (can start immediately)".

**Status:** ready-for-agent

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

## BDD Acceptance

- [ ] <Scenario reference> — <target environment> — <verification entry point> — <evidence to capture>

</local-ticket-template>

<issue-template>

## Parent

A reference to the parent issue on the tracker (if the source was an existing issue, otherwise omit this section).

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective, not layer-by-layer implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## BDD Acceptance

- [ ] <Scenario reference> — <target environment> — <verification entry point> — <evidence to capture>

## Blocked by

- A reference to each blocking ticket, or "None (can start immediately)". Omit this section when blockers were set as native edges.

</issue-template>

Omit the BDD Acceptance section when the ticket has no scenario mapping.

In either form, avoid implementation file paths or code snippets: they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.
