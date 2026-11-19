---
name: bdd
description: Turns business rules and user stories into verifiable Given/When/Then scenarios. Use to discover missing acceptance decisions, draft or review BDD scenarios, or write Gherkin `.feature` files.
---

# BDD

Use examples to agree on behavior before treating a scenario as an acceptance criterion. Gherkin records the agreement; a runner is optional.

## 1. Discover the rule

- Read the requested change, accepted requirements, and relevant existing scenarios or public tests. Reuse domain terms. Keep **current behavior** distinct from **intended behavior**; a test of the former does not settle the latter when the feature is changing.
- Identify the actor, the rule, and a concrete example for the normal path. Add a boundary, denial, or failure example when its result distinguishes plausible rules. Ask the smallest question that would resolve each material gap. For example: "Does a link expire at exactly 24 hours, or only after 24 hours?"
- Keep confirmed rules, proposed rules, and open questions separate. Draft the settled scenarios without waiting for unrelated answers. Leave disputed expectations out of agreed scenarios and executable tests.

## 2. Formulate scenarios

- Give each scenario a title that names one independently reviewable behavior. Keep one business trigger per scenario. Use `And` for related setup or effects of that trigger; split when a different trigger or starting state changes which rule applies.
- **Given** sets up reproducible state. Name only the actor, data, permissions, or clock values that affect the result. **When** states the business action or event. **Then** names observable outcomes and their expected values. Use the domain's language rather than selectors, private methods, or storage details.
- In review mode, name each affected scenario and the ambiguity, overlap, missing case, or unobservable result. Show the smallest rewrite that fixes it. If the correct rewrite depends on a product decision, ask rather than choosing it.
- Return scenarios and open decisions in the reviewer's language. Use Markdown for discussion or acceptance review. When asked for `.feature` files, use the project's Gherkin dialect, grouping, and tags; keep unresolved decisions in the accompanying notes. Use `Scenario Outline` only when rows exercise the same rule with the same step structure. See the [Gherkin reference](https://cucumber.io/docs/gherkin/reference/) for syntax.

## 3. Map to verification

- For each agreed scenario, name the existing test or the manual entry point and the observation that would prove the result. Mark proposed checks as such and report a result only after running or observing the check in the stated environment.
- If asked to automate, reuse the project's runner and step definitions where they fit. If the project has no Gherkin runner, use its existing test stack unless a new runner is explicitly requested. Use `tdd` to implement the check at the public boundary where the result is observable.

References: [Cucumber BDD practices](https://cucumber.io/docs/bdd/) and [Writing better Gherkin](https://cucumber.io/docs/bdd/better-gherkin/).
