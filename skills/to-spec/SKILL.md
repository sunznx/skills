---
name: to-spec
description: "Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis of what you've already discussed."
---

Synthesize the spec from the current conversation and codebase. Record gaps as open decisions without interviewing the user.

Use `planning-with-files` to select or create this task's plan as `<PLAN_DIR>`; when another workflow invokes this skill, use that workflow's selected plan. Before reading Matt configuration, follow [shared configuration initialization](../setup-matt-pocock-skills/references/ensure-config.md). Read `.planning/issue-tracker.md` and `.planning/triage-labels.md`. Read `.planning/domain.md` when present.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

2. Invoke [BDD synthesis](../bdd/SKILL.md#synthesis-for-specs-and-tickets) in the selected plan for confirmed business rules. Put the linked scenario IDs under BDD Acceptance and unsettled rules under Open Decisions.

3. Sketch the highest public seams at which to verify the feature. Prefer existing seams and keep the number small. Record any seam decisions that need confirmation under Open Decisions.

4. Write the spec using the template below to `<PLAN_DIR>/spec.md` and publish it with `ready-for-agent` in the configured tracker's format. For a remote issue, use the [BDD reference format](../bdd/SKILL.md#referencing-scenarios) for scenario links and record the issue URL in the plan. Keep the spec and issue in sync when revising them.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## BDD Acceptance

- [<Scenario ID>](<relative scenario path>) — <behavior title>

Omit this section when there are no agreed scenarios.

## Open Decisions

List unresolved rules or test seams. Omit this section when there are none.

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.

</spec-template>
