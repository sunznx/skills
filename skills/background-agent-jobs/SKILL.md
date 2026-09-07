---
name: background-agent-jobs
description: 管理异步后台 subagent job 的启动、互斥写范围和状态回报。当用户要求 bg/background/subagent 异步执行且主 agent 继续当前对话时使用；不用于一次性消息投递或同步等待结果。
---

# Background Agent Jobs

把后台工作作为有稳定身份的 job 管理。投递与回传通道遵循 `$agent-messaging`；本 skill 只补充生命周期、去重和写入互斥，不复制其通道细节。

## 启动

1. 在投递前分配稳定 `job_id`。优先使用用户给出的 ID；否则使用可传给 subagent 的原生 task ID 或唯一短标签。整个生命周期保持不变。
2. 写清目标、输入、输出、验收、允许副作用和 `write_scope`。后台 agent 的首个动作必须通过原生通信工具向 sender 发送 `status=running`，并说明当前阶段。
3. 使用原生 multi-agent 能力按 `$agent-messaging` 的 `notify` 模式投递一次。得到 `delivered` 或 `queued` 后，主 agent 立即继续当前对话，不调用等待工具，也不轮询状态。
4. 投递超时或结果含糊时保留“状态未知”，不重试或切换通道；先确认原任务不存在，才允许再次投递。

## 状态事件

后台 agent 只在状态或命名阶段真实变化时主动通知 sender；进展无变化时不发心跳。状态流转为：

```text
running <-> blocked -> completed | failed
```

每条通知都包含：

- `job_id`、`status`、当前阶段；
- 一句进展和可核对的证据；
- `blocked`：阻塞条件、已尝试事项和恢复所需输入；
- `completed` / `failed`：产物、验证结果和遗留风险。

终态只发送一次。解除阻塞后发送新的 `running` 事件。主 agent 以 `(job_id, status, stage)` 去重，同一事件只向当前对话转发一次。

## 去重与写入互斥

- 投递前检查已有原生 task。目标与 `write_scope` 相同的活跃 job 直接复用其身份；排队中的 job 不再投递。
- 同一仓库默认只有一个写入 job。只有明确列出互不相交的文件集合时才并发；清单、锁文件、生成物、索引和共享文档都算重叠写点。
- 写范围重叠时排队，并在前一 job 进入终态且工作树稳定后再启动。无法确认现有 job 状态时保持单一执行者，不创建替代 job。
- 只读 job 可以并行，但不得把发现阶段悄然升级为写入。

## 完成标准

主 agent 已继续对话，且后台 job 的每次真实状态变化都由 subagent 主动送达；终态通知足以定位产物、复现验证并判断剩余风险。
