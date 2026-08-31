---
name: sync-skills
description: 同步本仓库与外部上游及 ~/.agents/skills。用户要求检查或更新 skills，以及添加、删除仓库中的 skill 时使用。
---

# Sync Skills

先读取仓库根目录 `README.md` 和 `skills/sources.json`，再按用户的调用方式执行：

```bash
repo="$(cat ~/.config/sync-skills/repo)"
"$repo/sync-skills"
"$repo/sync-skills" 添加 <skill-name>
"$repo/sync-skills" 删除 <skill-name>
```

- 无参数调用直接对比全部上游。没有更新时继续使用仓库版本，并同步到 `~/.agents/skills`。
- `添加` 从 `~/.agents/skills/<skill-name>` 导入。脚本会读取 `~/.agents/.skill-lock.json` 记录外部来源；没有来源记录时按本地 skill 管理。
- `删除` 会删除仓库目录和来源目录，commit 成功后再删除 `~/.agents/skills/<skill-name>`。
- 上游有更新时使用旧上游、本地版本和新上游做三方合并。合并成功后自动 commit，再同步本机目录。
- 出现冲突时检查 `skills/.sync-conflicts.json` 和文件内的冲突标记。解决冲突并手动 commit 前，不同步本机目录。

每次添加、删除或更换来源后，确认 `README.md` 与 `skills/sources.json` 一致。
