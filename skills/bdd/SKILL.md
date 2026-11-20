---
name: bdd
description: Turns business rules and user stories into verifiable Given/When/Then scenarios. Use to discover missing acceptance decisions, draft or review Markdown scenarios, or track BDD acceptance in Planning with Files (PWF).
---

# BDD

Use examples to agree on behavior before treating a scenario as an acceptance criterion. Use Markdown (`.md`) by default. A test runner is optional.

## 0. Select the work plan

Use `planning-with-files` to select or create this task's plan as `<PLAN_DIR>`. When another workflow invokes BDD, reuse its selected plan. On resume, follow the acceptance links in `task_plan.md` before drafting more scenarios.

## 1. Discover the rule

- Read the requested change, accepted requirements, and relevant existing scenarios or public tests. Reuse domain terms. Keep **current behavior** distinct from **intended behavior**; a test of the former does not settle the latter when the feature is changing.
- Identify the actor, the rule, and a concrete example for the normal path. Add a boundary, denial, or failure example when its result distinguishes plausible rules. Ask the smallest question that would resolve each material gap. For example: "Does a link expire at exactly 24 hours, or only after 24 hours?"
- Keep confirmed rules, proposed rules, and open questions separate. Draft the settled scenarios without waiting for unrelated answers. Leave disputed expectations out of agreed scenarios and executable tests.

## 2. Formulate scenarios

- Give each scenario a stable ID and a title that names one independently reviewable behavior. Keep the ID across edits and use it in review and verification. Keep one business trigger per scenario. Use `And` for related setup or effects of that trigger; split when a different trigger or starting state changes which rule applies.
- **Given** sets up reproducible state. Name only the actor, data, permissions, or clock values that affect the result. **When** states the business action or event. **Then** names observable outcomes and their expected values. Use the domain's language rather than selectors, private methods, or storage details.
- In review mode, name each affected scenario and the ambiguity, overlap, missing case, or unobservable result. Show the smallest rewrite that fixes it. If the correct rewrite depends on a product decision, ask rather than choosing it.
- Write scenarios and open decisions in the reviewer's language. Keep unresolved decisions separate from agreed scenarios.

## 3. Map to verification

- For each agreed scenario, name the existing test or the manual entry point and the observation that would prove the result. Mark proposed checks as such and report a result only after running or observing the check in the stated environment.
- If asked to automate, use the project's existing test stack unless a new runner is explicitly requested. Verify the behavior at its public boundary. For a bug with an obvious, cheap local test path or an explicit request for test-first or regression testing, follow the `tdd` skill.

## 4. Persist decisions, scenarios, and evidence

- `findings.md`: Record confirmed rules and open decisions separately. Link each decision to the affected scenario IDs. A proposed answer or skipped question does not settle a rule.
- Acceptance scenarios: Save each scenario as its own `<PLAN_DIR>/bdd/<scenario-name>.md`. Use the title without the ID as the filename, preserving its language and replacing only characters disallowed in filenames, including path separators. If the path already belongs to another scenario, use a more specific title rather than overwriting. Keep the scenario ID, Given/When/Then, and planned verification in the file. Link to each scenario by ID from `task_plan.md`. When a title changes, rename the file, update the current plan's links, and retain the ID.
- `progress.md`: Record each agreed scenario's verification status by ID and target environment. After a check runs, record the test command or manual entry point, actual result, and evidence link when available. If not run or blocked, name the missing check or prerequisite. Advance the applicable PWF phase only when its acceptance obligations are met; a PWF format or completion check does not verify product behavior.

Reference: [Cucumber BDD practices](https://cucumber.io/docs/bdd/).
