---
name: spec-bootstrap
description: 初始化项目的编码工作流，安装 Ponytail Codex plugin、项目级 Planning with Files skill、官方 hooks、Serena、Semble 和项目规则。用户调用 $spec-bootstrap 或要求初始化该工作流时使用。
---

# spec-bootstrap

目标项目：`$ARGUMENTS`，未提供时使用当前目录。

运行：

```bash
python3 "$SKILL_ROOT/scripts/spec_bootstrap.py" "<目标路径>"
```

没有目标路径时省略最后一个参数。

脚本会：

- 通过官方 marketplace 安装 `ponytail@ponytail` Codex plugin；
- 检查并更新 Planning with Files mirror；
- 安装项目级 Planning with Files skill、hook runtime skill，并完整复制上游官方 `.codex/hooks/`；
- 将 Serena 的 activate、remind 和 cleanup hooks 合并到项目 `.codex/hooks.json`；
- 将 Serena 与 Semble 写入项目 `.codex/config.toml`；
- 保留已有 `AGENTS.md`；不存在时创建空文件；
- 维护 `AGENTS.override.md` 中本工作流的区块；
- 缺少 `.sembleignore` 时创建它。

Ponytail 按官方方式配置 `DietrichGebert/ponytail` marketplace，并且仅在缺失时安装。保留项目文件中不属于本工作流的现有内容。Planning with Files 的 hook 注册合并自上游 `.codex/hooks.json`，hook scripts 和 `.codex/skills/planning-with-files/` runtime skill 原样来自上游；不添加自定义 router 或改写官方脚本。Serena hooks 使用与 MCP 相同的 `uvx` 来源运行。完成后报告脚本输出，并提醒用户在新的 Codex session 中通过 `/hooks` 检查和信任 Ponytail 与项目 hooks。如果失败，原样报告错误，不要手工补做一套不同流程。
