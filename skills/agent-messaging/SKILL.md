---
name: agent-messaging
description: 向一个或多个 agent 发送任务，默认异步通知；支持当前协作树、Codex TUI session 和 Herdr，也能新开 Herdr tab 启动指定类型的 agent 再交接任务。用户要求联系、通知、委派任务给其他 agent、新开 tab 交接或等待其结果时使用。
---

# Agent Messaging

把每个目标当作一次独立投递。优先使用当前运行环境的原生 agent 协作工具，只说明直接投递流程，不增加额外消息层或配置。

## 选择模式

- `notify`：默认模式。异步投递，发送成功后立即继续，不在本次调用中等待；消息中必须要求接收方在任务 `completed`、`failed` 或 `blocked` 后通知发送方。
- `request`：投递后等待接收方回复。只有用户明确说“等待”“等回复”“拿到结果”或指定 `request` 时使用。
- 用户没有指定模式或语义不明确时使用 `notify`。
- 需要等待时按 agent 身份匹配回复。同一目标同时只保留一个未完成任务。

## 原生工具优先

使用当前运行环境提供的 agent 通信能力。不要仅因为目标也能被 Herdr 找到就跳过原生工具。用户明确要求新开 Herdr tab 或新会话时，按[新开 Herdr tab](#新开-herdr-tab)处理，不经过本节。

在 Codex 中：

1. 对 `notify` 和 `request` 都使用 `followup_task` 投递任务。`send_message` 不会唤醒空闲 agent，不用它发起新任务。
2. `notify` 在任务末尾追加：`这是 notify 模式；处理完成、失败或阻塞后，请用原生通信工具通知发送方。` 所有目标得到 `delivered` 或 `queued` 后结束本次发送，不调用 `wait_agent`。
3. `request` 先向所有目标投递，再使用较长超时的 `wait_agent` 收集回复。回复可以乱序到达；按发送方身份从待处理目标中移除。
4. 接收方处理结束后，使用 `send_message` 向原生 sender metadata 中的发送方回传简短结果，并标明 `completed`、`failed` 或 `blocked`。

原生消息依赖平台自带的 sender metadata 识别发送方，不要在正文中重复包装发送方信息。

## Codex TUI session

当 `followup_task` 明确返回目标不在当前协作树，且目标是 Codex session UUID 或准确名称时，`notify` 先尝试 Codex CLI 自带的消息队列，再考虑 Herdr：

1. 运行 `codex queue --help`，确认当前 CLI 支持该命令。
2. 在消息末尾追加：`这是 notify 模式；处理完成、失败或阻塞后，请通知发送方。`
3. 异步投递，不启动或恢复另一个 TUI：

```bash
codex queue --thread "$target" --message "$message"
```

命令退出码为 0 且输出包含 `Queued message` 时记为 `queued`，立即结束该目标的发送，不调用 `wait_agent`，也不回退到 Herdr。非零退出属于明确失败，可以继续 Herdr 回退；超时或结果含糊时停止，避免重复投递。

`codex queue` 没有等待指定 session 回复的接口，只用于 `notify`。`request` 仍使用可匹配回复的原生协作工具；原生投递明确失败后再尝试 Herdr。

## 多目标投递

- 每个目标单独调用一次，不使用广播。
- 先完成 fan-out，再在 `request` 模式下 fan-in；不要等待第一个目标结束后才给下一个目标发送。
- 分别记录每个目标使用的通道和状态。单个目标失败不抹掉其他目标的成功结果。
- 每个目标独立决定通道，因此同一批任务可以同时包含原生协作、Codex TUI queue 和 Herdr。

## 只在明确失败时回退

按以下规则解释原生投递结果：

- `delivered` 或 `queued`：投递成功。不要回退。
- 工具不可用、目标不在当前协作树、目标属于其他运行环境：明确失败；符合条件的 `notify` 先尝试 Codex TUI queue，其余情况尝试 Herdr。
- 超时、中断或结果含糊：投递状态不确定。停止并报告，不要回退，避免同一任务被执行两次。

## Herdr 回退

只有命中明确失败时才执行本节。

1. 检查 `HERDR_ENV=1`。若不成立，报告 Herdr 不可用并停止；不要从 Herdr 外部控制其他 session。
2. 运行 `herdr --help` 确认当前 CLI，再直接使用用户给出的目标作为 agent 名称或 pane ID。
3. 用 `herdr agent get <target>` 检查目标：
   - `idle` 或 `done`：可以发送。
   - `working`：先用 `herdr agent wait <target> --timeout 300000` 等待稳定状态，再检查一次。
   - `blocked`：读取状态并报告，不替接收方回答审批或问题。
   - `unknown` 或无法解析目标：停止并报告。
4. 用 `herdr agent get "$HERDR_PANE_ID"` 读取当前发送方的 agent 名称；没有名称时使用当前 pane ID。
5. 保持用户任务正文不变，只在末尾追加一句：`发送方：<sender>。处理完后通知发送方。`

`notify` 不等待：

```bash
herdr agent prompt <target> '<message>\n\n发送方：<sender>。处理完后通知发送方。'
```

`request` 等待并读取结果：

```bash
herdr agent prompt <target> '<message>\n\n发送方：<sender>。处理完后通知发送方。' --wait --timeout 300000
herdr agent read <target> --source recent-unwrapped --lines 120
```

Herdr 的 `notify` 接收方完成后，应调用本 skill 把结果发回 `<sender>`。发送方不会在原调用中等待这条回报。

## 新开 Herdr tab

用户明确要求新开 tab、新开会话，或要在某个目录新起一个 agent 时，走本节。这是用户指定的布局，不是投递失败后的回退，所以不先试原生工具。目标目录里没有可用的 agent、用户也没要求新开时，报告并询问是否新开 tab，不要自行新开。

参数：

- 目标目录：绝对路径，必填。
- agent 类型：`--kind`，默认 `claude`。可用的值见 `herdr agent` 输出的 `kinds`。
- agent 名：匹配 `[a-z][a-z0-9_-]{0,31}`，并且在 live agent 中唯一。按目录和任务起一个短名，例如 `nas-handoff`。
- tab label：默认用 agent 名。
- env：可选，`--env KEY=VALUE` 可重复。目标目录和当前在同一个项目时，传 `PLAN_ID=<PLAN_ID>`，让新会话沿用同一个计划。
- 模式：`notify`（默认）或 `request`，规则同[选择模式](#选择模式)。

步骤：

1. 检查 `HERDR_ENV=1`。不成立就报告 Herdr 不可用并停止。
2. 选 workspace。`herdr workspace list` 不返回 cwd，所以用 `herdr pane list` 找 cwd 等于目标目录或在它下面的 pane，取这些 pane 的 `workspace_id`：
   - 只有一个 workspace：用它。
   - 有多个：用 label 等于目录名的那个。仍不唯一就问用户。
   - 一个都没有：问用户是新建 workspace，还是放进某个现有 workspace。用户选新建时运行 `herdr workspace create --cwd <目标目录> --label <label> --no-focus`，用返回的 `.result.root_pane.pane_id` 直接做第 4 步，跳过第 3 步。
3. 建 tab，从返回的 `.result.tab.tab_id` 和 `.result.root_pane.pane_id` 取 tab 和 pane：

```bash
herdr tab create --workspace <ws> --cwd <目标目录> --label <label> [--env KEY=VALUE ...] --no-focus
```

4. 在新 pane 里启动 agent。返回的 `.result.type` 为 `agent_started`，并且 `.result.agent.interactive_ready` 为 `true`，才算启动成功：

```bash
herdr agent start <agent名> --kind <kind> --pane <pane_id> --timeout 90000
```

   - 返回 `agent_not_ready`：agent 停在启动时的审批或问题界面。用 `herdr agent read <pane_id> --source recent-unwrapped --lines 40` 读出界面并报告，不替它回答。
   - 其他失败或超时：先运行一次 `herdr agent get <pane_id>`。pane 上已经是这个 agent 并且状态为 `idle` 时继续；否则停止并报告 tab ID。不重建 tab，不重复 start，避免同一个任务被执行两次。这个 tab 留给用户处理。

5. 投递任务。交接内容超过几段，或用户说要 handoff 时，先用 `handoff` skill 写 `<PLAN_DIR>/handoff.md`，prompt 里只写一句目标和这个文件的绝对路径。sender 和末尾那句话按[Herdr 回退](#herdr-回退)第 4、5 步处理，命令也用那里的 `notify` 或 `request` 写法，目标是新的 agent 名。
6. `notify` 模式下确认对方已接手。`herdr agent prompt` 成功只说明文字已经提交，不说明 agent 开始干活。运行 `herdr agent wait <agent名> --until working --timeout 60000`，确认状态变成 `working`。没等到时用 `herdr agent read <agent名> --source recent-unwrapped --lines 15` 查看它在做什么，再如实报告。

返回结果时，额外报告 tab ID、pane ID 和 agent 名，通道记为 `herdr-new-tab`。多目标时每个目标各建一个 tab。

改动本节后，在 Herdr 里运行 [`scripts/e2e-herdr-new-tab.sh`](scripts/e2e-herdr-new-tab.sh) `[kind ...]`（默认 `claude`）。脚本在 `scratch` workspace 走一遍第 3 到第 6 步，读到回执后关掉测试 tab，不留残余；`HERDR_ENV` 不为 `1` 时跳过。

## 本地文件兜底

当一个目标没有任何适用通道成功，且所有适用通道都已明确失败或不可用时，把原始消息正文写入本地 Markdown 文件；这只是保留待投递内容，不算发送成功。

1. 从任务生成简短的文件名安全标题 `$title`；不得包含路径分隔符，且不得为 `.` 或 `..`。
2. 创建唯一临时目录：

```bash
mktemp -d "${TMPDIR:-/tmp}/agent-messaging-XXXXXX"
```

3. 将原始消息正文原样写入返回目录下的 `$title.md`。
4. 向用户报告绝对路径，并明确标记该目标为 `not_delivered`。

多目标任务仍按目标独立兜底。超时、中断或结果含糊不属于明确失败，沿用停止投递的规则，避免用户根据文件再次转发后产生重复执行。

## 返回结果

向用户按目标简要报告：投递通道、是否已投递、是否仍在等待，以及最终的 `completed`、`failed`、`blocked` 或 `not_delivered` 状态。本地兜底时附文件绝对路径。部分成功时保留每个目标的真实结果，不把整批任务合并成单一状态。
