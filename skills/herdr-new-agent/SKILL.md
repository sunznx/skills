---
name: herdr-new-agent
description: Opens a Herdr tab and starts an agent, inheriting the caller's agent kind, workspace, and working directory by default. Use when the user asks for a new Herdr agent, tab, or session.
---

# Herdr New Agent

Create a new agent that can accept input. By default, open a tab in the caller's workspace without stealing focus. Apply any requested agent kind, workspace, or directory instead of the corresponding default.

## Resolve the caller and launch arguments

Confirm that the session is in Herdr and inspect the installed CLI:

```bash
test "${HERDR_ENV:-}" = 1
herdr --help
herdr agent
herdr tab
herdr pane current --current
```

Run the commands individually. Stop if `HERDR_ENV` is not `1`. The `herdr agent` and `herdr tab` help commands may exit with status 2.

If the pane lookup succeeds, record `.result.pane.pane_id` as `caller_pane_id`, along with `terminal_id` and `workspace_id`:

```bash
herdr agent get "$caller_pane_id"
```

Use the caller for defaults only after the live agent record matches all three nonempty IDs. A moved pane may resolve an old alias, so use the IDs returned by the pane lookup. If the live IDs disagree, resolve them again and stop if they still disagree.

If Herdr returns `pane_not_found` or the resolved pane has no agent (`agent_not_found`), proceed when both the agent kind and the destination are explicit. A prior user choice for the same work counts. Resolve an existing workspace against `herdr workspace list` by ID or unique exact label. An explicit request to create a workspace also supplies the destination. Ask only for any missing choice. Do not guess from stale environment IDs, UI focus, the working directory, or another agent. For other lookup errors, report the error before creating anything.

- `agent_kind`: Use the user-specified kind or map the verified caller's `.result.agent.agent` to a kind listed by `herdr agent`. Use the program type field.
- `target_workspace`: Use the user-specified workspace resolved against the live list or inherit the verified caller's workspace. Ask on ambiguous matches. Changing cwd does not change the workspace.
- `target_cwd`: Default to `$PWD`. Resolve a user-specified directory to an existing absolute path.
- `agent_name`: Choose a name matching `[a-z][a-z0-9_-]{0,31}`. Confirm it is free in `herdr agent list`. Use it as the default tab label.

If the user explicitly requests a new workspace, check `herdr workspace` syntax first, then run:

```bash
herdr workspace create --cwd "$target_cwd" --label "$workspace_label" --no-focus
```

Record `.result.workspace.workspace_id`, `.result.tab.tab_id`, and `.result.root_pane.pane_id`. The workspace already includes a tab and an idle shell pane. Use that pane for the launch step.

## Open the tab and start the agent

To use an existing workspace, create a tab:

```bash
herdr tab create --workspace "$target_workspace" --cwd "$target_cwd" --label "$agent_name" --no-focus
```

Record `.result.tab.tab_id` and `.result.root_pane.pane_id` as `tab_id` and `pane_id`. Then start the agent in that shell pane:

```bash
herdr agent start "$agent_name" --kind "$agent_kind" --pane "$pane_id" --timeout 60000
```

Pass user-requested environment variables through `tab create --env KEY=VALUE`. Pass program arguments after `--` in `agent start`. The new agent, not the caller, handles any accompanying research or resumed work.

## Verify and report

Count the launch as successful only when `.result.type` is `agent_started` and `.result.agent.interactive_ready` is `true`. Check the returned workspace, pane, and kind. Report the agent name, kind, workspace ID, tab ID, pane ID, and cwd.

- `agent_not_ready`: Use `herdr agent read "$pane_id" --source recent-unwrapped --lines 40` to identify a startup question or approval. Report it for the user to handle.
- Failed, timed-out, or ambiguous launch: Keep any returned IDs. Check `herdr agent get "$pane_id"` and `agent read` before retrying. Report ready only if the identity matches and `interactive_ready` is `true`. If still uncertain, keep the tab and do not repeat creation or launch.
- Tab creation times out without an ID: Use `herdr tab list --workspace "$target_workspace"` to find the unique label, then check its pane. If uncertain, report that and do not repeat creation.

If the user requested only a launch, stop after verification. If they included a task, use the Herdr delivery flow in `agent-messaging` after the agent is ready. Confirm it took the task, honor the requested wait mode, and report launch and task acceptance separately.

If caller lookup failed, do not look up the stale pane again during task delivery. Give the new agent an independently known reply destination. For a Codex caller with an active `CODEX_THREAD_ID`, pass that ID and use the Codex queue reply path in `agent-messaging`. If no reply destination is known, have the agent report in its new tab and include the tab and pane IDs in your handoff.
