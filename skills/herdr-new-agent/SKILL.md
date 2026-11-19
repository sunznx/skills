---
name: herdr-new-agent
description: 在 Herdr 中新开 tab 并启动 agent，默认继承当前 agent 类型、workspace 和工作目录。用户要求用 Herdr 新开 agent、tab 或会话时使用；仅向已有 agent 发消息走 agent-messaging。
---

# Herdr New Agent

把用户的新建请求落实为一个可接受输入的 agent。默认在当前 workspace 新开 tab，保留用户焦点；用户指定 agent 类型、workspace 或目录时分别覆盖对应默认值。

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

用户明确要求新建 workspace 时，先从 `herdr workspace` 核对语法，再运行：

```bash
herdr workspace create --cwd "$target_cwd" --label "$workspace_label" --no-focus
```

取返回的 `.result.workspace.workspace_id`、`.result.tab.tab_id` 和 `.result.root_pane.pane_id`；它已自带 tab 和空闲 shell pane，直接进入启动步骤。

## 新建 tab 并启动

在选定的现有 workspace 中创建一个 tab：

```bash
herdr tab create --workspace "$target_workspace" --cwd "$target_cwd" --label "$agent_name" --no-focus
```

从返回的 `.result.tab.tab_id` 和 `.result.root_pane.pane_id` 记录 `tab_id`、`pane_id`，立即在这个新 shell pane 启动：

```bash
herdr agent start "$agent_name" --kind "$agent_kind" --pane "$pane_id" --timeout 60000
```

用户要求的环境变量通过 `tab create --env KEY=VALUE` 传入；用户要求的 agent 原生参数放在 `agent start` 的 `--` 后。启动流程只做参数解析、新建与启动；用户附带的调研或旧任务恢复由启动后的目标 agent 执行。

## 验证并交付

返回 `.result.type = agent_started` 且 `.result.agent.interactive_ready = true` 才算启动成功。核对返回的 workspace、pane 和 agent 类型符合本次参数，报告 agent 名、类型、workspace ID、tab ID、pane ID 和 cwd。

- `agent_not_ready`：用 `herdr agent read "$pane_id" --source recent-unwrapped --lines 40` 查看启动审批或问题，报告给用户处理。
- 失败、超时或结果不确定：保留已返回的 ID，先用 `herdr agent get "$pane_id"` 和 `agent read` 检查是否已经启动；只有身份符合且 `interactive_ready` 为 `true` 才报告可用。状态无法确认时停止，保留新 tab，不重复创建或启动。
- 创建 tab 本身超时且未返回 ID：运行 `herdr tab list --workspace "$target_workspace"`，按本次唯一 label 检查，再检查对应 pane；无法确认时报告不确定，不重放创建命令。

用户只要求启动时，到此完成。附带任务时，启动成功后使用 `agent-messaging` 的 Herdr 投递流程发送任务并确认接手，沿用用户指定的等待方式；启动成功和任务已接手分别报告。

If caller lookup failed, do not look up the stale pane again during task delivery. Give the new agent an independently known reply destination. For a Codex caller with an active `CODEX_THREAD_ID`, pass that ID and use the Codex queue reply path in `agent-messaging`. If no reply destination is known, have the agent report in its new tab and include the tab and pane IDs in your handoff.
