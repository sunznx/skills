---
name: say-back
description: 用自己的话复述用户当前任务的目标和试图解决的问题，并保存到当前 Planning with Files 任务目录。用户要求确认理解或调用 $say-back 时使用。
---

# Say Back

结合当前对话与 Planning with Files 的任务文件，向用户复述：

- **目标**：用户希望达成什么结果。
- **问题**：用户试图解决什么问题。

区分用户明确说过的内容与自己的推断；信息不足时指出缺口。保持简短。

使用 `planning-with-files` 的 `resolve-plan-dir.sh` 解析当前 `PLAN_ID` 和 `PWF_PLAN_ROOT`，读取所选计划的 `task_plan.md`、`findings.md` 和 `progress.md`。没有计划时按项目规则用 `init-session.sh --gated` 新建；多个计划且未绑定 `PLAN_ID` 时，请用户指定，不能猜测。将复述写入 `<PLAN_DIR>/say-back.md`，并在 `<PLAN_DIR>/progress.md` 记录文件路径。对话中的复述与文件内容保持一致。
