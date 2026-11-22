# Skills 仓库

- `skills/sources.json` 是 skill 来源和上游基线的机器可读清单。
- `README.md` 的 Skill 来源目录是对应的人类可读清单；添加、删除或更换来源时一起更新。
- 技能同步、添加和删除只处理来源清单、仓库快照及登记的客户端。仓库 skill 变更后，核对 `~/.agents/skills` 和 `~/.claude/skills` 同名条目的来源，再更新仓库管理的副本。

## Skill language

Write new or substantially revised skill instructions, frontmatter descriptions, and supporting references in English. Preserve necessary Chinese trigger phrases, user-facing examples, and verbatim source material. User-facing output follows the language required by the task.
