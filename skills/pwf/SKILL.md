---
name: pwf
description: 为当前 Codex session 创建并绑定独立的 Planning with Files 计划。仅在用户调用 $pwf 并提供任务名时使用。
---

# pwf

任务名：`$ARGUMENTS`

项目 hook 通常会在本 skill 开始前创建计划，并在上下文中注入：

```text
[pwf-session] PWF_PLAN_DIR=/absolute/path/to/.planning/<plan-id>
```

如果上下文只有 `PWF_SESSION_KEY`，说明 Codex 的 hook payload 没有包含 skill 调用。此时运行项目 router 完成绑定：

```text
python3 .codex/hooks/pwf_session_router.py bind '<PWF_SESSION_KEY>' '<任务名>'
```

使用上下文中的原值和 `$ARGUMENTS` 作为独立参数，不要拼接 shell。命令成功后会返回 `PWF_PLAN_DIR`。

1. 不要猜测路径，也不要让用户设置 `PLAN_ID` 或 `.active_plan`。
2. 读取并遵循项目内 `.codex/skills/planning-with-files/SKILL.md`。
3. 在 `PWF_PLAN_DIR` 中维护 `task_plan.md`、`findings.md` 和 `progress.md`。
4. 以 `task_plan.md` 为权威计划；每次改变步骤或状态时，用 `update_plan` 完整镜像当前计划。
5. 如果上下文没有 `PWF_PLAN_DIR` 或 `PWF_SESSION_KEY`，停止并说明项目尚未安装 router，或本次 session 绑定失败。不要退回共享计划。
