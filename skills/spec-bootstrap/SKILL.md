---
name: spec-bootstrap
description: 全局安装 Codex 编码工作流，配置 Ponytail、Planning with Files、Serena 和 Semble。用户调用 $spec-bootstrap 或要求安装该全局工作流时使用。
---

# spec-bootstrap

运行：

```bash
python3 "$SKILL_ROOT/scripts/spec_bootstrap.py"
```

该命令不接收项目路径，也不修改项目文件。脚本会：

- 通过 Codex marketplace 全局安装 Ponytail plugin；
- 通过 Codex marketplace 全局安装 Planning with Files plugin；
- 将 Serena 和 Semble MCP 合并到 `~/.codex/config.toml`；
- 将 Serena 的 activate、remind 和 cleanup hooks 合并到 `~/.codex/hooks.json`；
- 保留其他全局配置和 hooks。

Ponytail 与 Planning with Files 的 skills 和 lifecycle hooks 由各自的 plugin 提供，不再复制到项目。完成后报告脚本输出，并提醒用户在新的 Codex session 中通过 `/hooks` 检查和信任全局 hooks。如果失败，原样报告错误，不要改成项目级安装。
