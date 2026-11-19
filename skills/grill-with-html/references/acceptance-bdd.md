# Write BDD acceptance for plan review

Write one scenario per behavior a reviewer can accept or reject independently. Give each scenario a stable ID so the plan, test, and evidence can refer to the same behavior. Use the reviewer's language. A BDD runner is optional.

## Write the scenario

- **System and actors:** Name the system under test and the actor that initiates the behavior. Name external systems only when they supply a fixture or an observation. Share this information above the scenarios when it applies to all of them.
- **Given:** Describe a reproducible setup. Name the environment, fixture identities, starting state, relevant configuration or clock, and the baseline used for comparisons. For a failure case, say how to induce or reproduce the fault. Keep setup out of the trigger.
- **When:** Name the action or event that exercises the behavior. Combine inseparable actions when the behavior depends on their sequence. Do not turn every click, command, or polling step into a scenario.
- **Then:** Write a separate observable assertion for each required effect or invariant. For each assertion, identify where to read it and what counts as success. Use a bounded observation or a controlled clock for claims such as ‘no new events’. Use a before-and-after identity or a separate control fixture to check that an unrelated object did not change. A status label alone does not establish runtime, persistence, or data-path behavior.
- **Verification:** Give the test identifier and how to run it, or the manual entry point and observation. Name the output to retain. If the check is not available yet, label it proposed and name the missing prerequisite. Do not invent a command or imply that a mock or a demo checks the real integration.

Group normal behavior, failure and recovery, and cleanup when each is in scope. Split two behaviors when they have different triggers, expected outcomes, or evidence. For example, check pause and resume separately: the absence of a new event and the first event on resume can fail independently. Keep assertions from one trigger together. Separate stopping a runtime from deleting its record if they have different effects.

## Record evidence separately from expectations

| Status | What to record |
| --- | --- |
| Pending | The planned verification and evidence to capture. No result is claimed for the target environment. |
| Partial | Link the evidence and name which assertions and environment it covers. List what remains pending. |
| Pass or fail | Link a receipt for this scenario and environment. Include the actual observations and name any failed assertions. |
| Blocked | Name the missing prerequisite and the assertions it blocks. Preserve evidence from independent checks. |

A receipt identifies the build or revision, environment, fixture or run ID, execution entry point, and the observed values or artifacts. A source that reports a result without an accessible receipt can inform the plan. Attribute the report and leave the target check pending. Report local and target environments separately. A rendered BDD page verifies presentation only.

## Give each component one job

| Content | Owns | Reference it instead of repeating |
| --- | --- | --- |
| `state` | State names and allowed transitions, including the event that moves the system between states. | BDD refers to the relevant starting state or transition. It covers what the transition means in use, such as which runtime, record, or stream is preserved. |
| `api` | HTTP method or RPC name, path, parameters, request and response fields, and error contract. | BDD refers to the named operation and the values needed to identify the fixture or judge an outcome. Leave field catalogs and schemas in `api`. Use an interface name that exists, or label a proposed contract. |
| BDD | Setup, trigger, observable assertions, verification entry, and evidence for each behavior. | A state diagram or a successful API response alone is not acceptance evidence. Omit either component if it adds no reference the reviewer needs. |

## Render the example

[Device and heartbeat acceptance](../examples/device-heartbeat-bdd.md) is a portable plan excerpt. Its observation windows are proposed test-fixture settings, not production guarantees. Its verification entries are manual surfaces, not fabricated Cloud commands.

- **Standalone:** From this repository, run `node skills/answer-me-with-html/scripts/am.mjs render skills/grill-with-html/examples/device-heartbeat-bdd.md -o /tmp/device-heartbeat-bdd.html --no-open`. With installed skills, resolve both paths from their actual directories.
- **Final grilling round:** Copy the Markdown below `## 设备与心跳` into the final question's `reviewPlan`. Keep its level-three and level-four headings. Omit the example's frontmatter and level-two panel heading. Use [the round input rules](input.md#content-ownership-and-preview) and the normal `ask.mjs` command. The form puts approval choices after the plan; the plan should not contain its own `ask` block.
