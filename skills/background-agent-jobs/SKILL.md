---
name: background-agent-jobs
description: 用当前平台的原生 subagent 异步执行任务。用户要求后台执行、主 agent 继续对话时使用。
---

# Background Agent Jobs

1. 明确任务、预期产物和可写文件。若已有后台任务写入同一文件，等它结束再启动；只读任务可并行。
2. 用当前平台的原生工具创建后台 subagent，记录返回的任务 ID。不要用消息投递或另开终端代跑；无法确认是否启动时，报告状态未知，不重复启动。
3. 启动成功后主 agent 继续对话，不等待或轮询。subagent 完成或受阻时，通过平台原生回报说明产物、验证结果或阻塞原因；主 agent 将结果告知用户。
