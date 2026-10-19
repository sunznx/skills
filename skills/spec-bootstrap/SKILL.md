---
name: spec-bootstrap
description: 全局安装 Codex 编码工作流，配置 Planning with Files plugin 和 lifecycle hooks。用户调用 $spec-bootstrap 或要求安装该全局工作流时使用。
---

# spec-bootstrap

运行：

```bash
python3 "$SKILL_ROOT/scripts/spec_bootstrap.py"
```

脚本会：

- 通过 Codex marketplace 全局安装 Planning with Files plugin；
- 安装 Planning with Files 时临时向 marketplace manifest 写入 `"commands": []`，清理旧 cache 后重新生成 plugin cache，完成后还原 manifest，避免生成重复的 `source-command-*` skills；
- 保留现有全局配置和 hooks。

Planning with Files 的 skills 和 lifecycle hooks 由其 plugin 提供。完成后报告脚本输出，并提醒用户在新的 Codex session 中通过 `/hooks` 检查和信任全局 hooks。如果失败，原样报告错误。
