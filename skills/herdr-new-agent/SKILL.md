---
name: herdr-new-agent
description: 在 Herdr 中新开 tab 并启动 agent，默认继承当前 agent 类型、workspace 和工作目录。用户要求用 Herdr 新开 agent、tab 或会话时使用；仅向已有 agent 发消息走 agent-messaging。
---

# Herdr New Agent

把用户的新建请求落实为一个可接受输入的 agent。默认在当前 workspace 新开 tab，保留用户焦点；用户指定 agent 类型、workspace 或目录时分别覆盖对应默认值。

## 确定调用方和参数

先确认当前在 Herdr 中，再读取实际 CLI 与调用方：

```bash
test "${HERDR_ENV:-}" = 1
herdr --help
herdr agent
herdr tab
herdr agent get "$HERDR_PANE_ID"
```

逐条运行；`herdr agent` 和 `herdr tab` 只打印命令组帮助，可能以状态 2 退出，不用 `&&` 把后续命令接在它们后面。`HERDR_ENV` 不为 `1`、调用方 pane 无法解析或没有可识别的 agent 时，停止并报告原始错误，避免控制 UI 聚焦的其他窗口。

从 `agent get` 的 JSON 结果填写本次参数：

- `agent_kind`：默认取 `.result.agent.agent` 对应的程序类型，例如 Codex → `codex`、Claude → `claude`。以 `herdr agent` 的 `kinds` 为准；不能对应时先澄清类型。`name` 和 `display_agent` 不作为类型。用户明确指定时使用指定类型。
- `target_workspace`：默认取 `.result.agent.workspace_id`。用户指定 workspace 时，运行 `herdr workspace list`，按 ID 或唯一的准确名称解析；有歧义时澄清。目录不同只影响 cwd，不据此重新选择 workspace。
- `target_cwd`：默认用当前 `$PWD`；用户指定时解析为存在的绝对目录。
- `agent_name`：按任务取短名，匹配 `[a-z][a-z0-9_-]{0,31}`；用 `herdr agent list` 检查 live 名称唯一。tab label 默认同名。

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
