---
name: agent-messaging
description: 向一个或多个 agent 发送任务，默认等待回复；支持当前协作树、Codex TUI session 和 Herdr。用户要求联系、通知、委派任务给其他 agent 或等待其结果时使用。
---

# Agent Messaging

把每个目标当作一次独立投递。优先使用当前运行环境的原生 agent 协作工具，只说明直接投递流程，不增加额外消息层或配置。

## 选择模式

- `notify`：异步投递。发送成功后立即继续，不在本次调用中等待；消息中必须要求接收方在任务 `completed`、`failed` 或 `blocked` 后通知发送方。
- `request`：投递后等待接收方回复。用户明确说“等待”“等回复”“拿到结果”等，或没有指定模式时使用。
- 只有用户明确说“异步”“不用等”“发送后继续”或指定 `notify` 时，才使用 `notify`。语义不明确时默认使用 `request`。
- 需要等待时按 agent 身份匹配回复。同一目标同时只保留一个未完成任务。

## 原生工具优先

使用当前运行环境提供的 agent 通信能力。不要仅因为目标也能被 Herdr 找到就跳过原生工具。

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

## 返回结果

向用户按目标简要报告：投递通道、是否已投递、是否仍在等待，以及最终的 `completed`、`failed` 或 `blocked` 状态。部分成功时保留每个目标的真实结果，不把整批任务合并成单一状态。
