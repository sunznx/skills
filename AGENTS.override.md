@AGENTS.md

# 项目规则

- 修改同步逻辑前读取 `skills/sync-skills/SKILL.md`。
- 外部更新使用三方合并，保留已提交的本地差异；存在冲突时暂停 commit 和本机部署。
- skill 或 plugin 发生变更时，调用 `$mindmap` 更新仓库根目录 `skills.smm.md`。
- `skills.smm.md` 发生变更时，同步到 `/Users/sunx/Dropbox/syncer/apps/obsidian/notes/skills/skills.smm.md`。
