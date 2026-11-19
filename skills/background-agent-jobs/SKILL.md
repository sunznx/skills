---
name: background-agent-jobs
description: Runs independent task slices asynchronously with the current platform's native subagents. Use when the user explicitly authorizes subagents for the current task, including by invoking background-agent-jobs or agent-messaging to perform a concrete task.
---

# Background Agent Jobs

## Triggers and authorization

Use native subagents only when the user explicitly authorizes them for the current task. An explicit user invocation of `background-agent-jobs` or `agent-messaging` to perform a concrete task counts as permission. Merely loading, mentioning, reading, or editing either skill, or receiving a research or time-consuming task, does not authorize delegation.

Record the authorization and its scope. It applies only to the current task, including follow-up turns and resumed work, and ends when the task is completed or cancelled or the user revokes permission.

After authorization, look for independently verifiable slices, such as separate lines of evidence in research or separate modules in a longer task. Handle quick lookups and small edits directly when delegation adds no value. Do not start a second worker for a slice already assigned to a recipient.

Follow narrower project and tool constraints. If no suitable native subagent tool is available, do the work in the current agent and report the limitation. Do not substitute a separate CLI process, worktree, or main session.

## Plan and dispatch

1. For each slice, list the objective, deliverable, prerequisites, and writable files. Split by independent question or nonoverlapping module. Wait for prerequisites before dispatch. Assign one subagent per independent slice.
2. Start ready slices concurrently with the platform's native subagent tool, within its current limit. Queue the rest and dispatch as slots free up. Pass the authorized scope, constraints, responsibilities, context, output format, and verification requirements. Record the task ID, status, and deliverable for each slice.
3. Prefer read-only research. Ask for conclusions, primary evidence or source paths, and open questions. For writes, allocate nonoverlapping files and tell each subagent to preserve other worktree changes. Wait for an existing task to finish before assigning another writer to its files. The main agent follows the same write boundaries.
4. If dispatch is uncertain, check native status. Report and record an unknown result if you cannot resolve it. Retry only after confirming that dispatch did not start.

## Collect and verify

Continue with work or discussion that does not depend on the dispatched tasks. Receive results through native completion notices. Use the platform's wait tool only when blocked; do not poll.

Update the record when a subagent completes or is blocked. Report its result, verification, or blocker. If a slice fails, keep the other results and either retry that slice or take it over, depending on the cause.

Reconcile conflicting evidence and run final verification in the main agent. Wait for required results before starting dependent work. A successful dispatch is not a completed task. If the user revokes permission, stop the affected jobs and continue the remaining work directly.
