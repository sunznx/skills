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

## 拆分与启动

1. 列出子任务的目标、预期产物、依赖和可写文件。按独立问题或互不重叠的模块拆分；存在前置依赖的任务等前置结果返回后再启动。一个独立问题用一个 subagent 即可。
2. 用当前平台的原生 subagent 工具并发启动所有已就绪任务，遵守平台当前可用并发额度；额度不足时将剩余任务排队，槽位释放后继续。每个委派传递本任务的授权范围和其余约束，说明职责、上下文、输出格式和验证要求，记录“子任务 → 任务 ID → 状态 → 产物”的对应关系。
3. 调研任务优先只读，要求返回结论、一手证据或代码路径，以及未确认项。需要写入时分配互不重叠的文件，告知每个 subagent 它并非独占工作树，保留他人改动；已有后台任务写入同一文件时，等它结束后再启动。主 agent 同样遵守写入归属。
4. 启动状态无法确认时，先用平台原生状态工具核实；仍无法核实时报告未知并保留该任务记录，确认未启动后才重试。

## 继续与收敛

启动后主 agent 继续对话或推进不依赖调研结果的工作。通过平台原生完成通知接收结果；确实需要等待时用平台的等待工具，避免反复轮询。

每个 subagent 完成或受阻时，更新对应记录并回报产物、验证结果或阻塞原因。一个任务失败时，保留其他任务的有效结果，按失败原因决定定向重试或由主 agent 接手。

主 agent 汇总证据，核对冲突结论并完成最终验证；主任务依赖某份调研时，接收该结果后再继续依赖步骤。后台任务仅启动成功不算主任务完成。用户撤销后台执行时停止相关任务，由主 agent 继续剩余工作。
