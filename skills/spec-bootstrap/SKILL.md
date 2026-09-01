---
name: spec-bootstrap
description: 初始化项目的编码工作流，安装 session 隔离的 Planning with Files、Serena、Semble 和项目规则。用户调用 $spec-bootstrap 或要求初始化该工作流时使用。
---

# spec-bootstrap

目标项目：`$ARGUMENTS`，未提供时使用当前目录。

运行：

```bash
python3 "$SKILL_ROOT/scripts/spec_bootstrap.py" "<目标路径>"
```

没有目标路径时省略最后一个参数。

脚本会：

- 检查并更新 Planning with Files mirror；
- 安装项目级 Planning with Files、`$pwf` 和 Codex hooks；
- 将 Serena 与 Semble 写入项目 `.codex/config.toml`；
- 保留已有 `AGENTS.md`；不存在时创建空文件；
- 维护 `AGENTS.override.md` 中本工作流的区块；
- 缺少 `.sembleignore` 时创建它。

保留这些文件中不属于本工作流的现有内容。完成后报告脚本输出，并提醒用户在新的 Codex session 中通过 `/hooks` 检查和信任项目 hooks。如果失败，原样报告错误，不要手工补做一套不同流程。
