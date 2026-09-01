---
name: sync-skills
description: 同步本仓库与外部上游及 ~/.agents/skills。用户要求检查或更新 skills，以及添加、删除仓库中的 skill 时使用。
---

# Sync Skills

先读取仓库根目录 `README.md` 和 `skills/sources.json`，再判断用户要同步还是本地修改 skill。

## 同步

```bash
repo="$(cat ~/.config/sync-skills/repo)"
"$repo/sync-skills"
"$repo/sync-skills" <skill-name>
"$repo/sync-skills" 添加 <skill-name>
"$repo/sync-skills" 删除 <skill-name>
```

- `$sync-skills`：运行无参数命令，对比全部上游，再把全部可部署快照同步到 `~/.agents/skills`。
- `$sync-skills <skill-name>`：只对比并只部署指定 skill。
- `添加` 从 `~/.agents/skills/<skill-name>` 导入。脚本会读取 `~/.agents/.skill-lock.json` 记录外部来源；没有来源记录时按本地 skill 管理。
- `删除` 会删除仓库目录和来源目录，commit 成功后再删除 `~/.agents/skills/<skill-name>`。
- 上游有更新时使用旧上游、本地版本和新上游做三方合并。合并成功后自动 commit，再同步本机目录。
- 出现冲突时检查 `skills/.sync-conflicts.json` 和文件内的冲突标记。解决冲突并手动 commit 前，不同步本机目录。
- 上游 Git 缓存统一写入 `~/.agents/cache/sync-skills`。
- 每次成功调用最后都执行 `git push`。没有改动时不创建空 commit；push 失败时报告错误，但不要撤销已经完成的 commit 或本机同步。

## 本地更新 skill

`$sync-skills 更新 <skill-name> <需求>` 表示修改仓库快照，不是执行 `./sync-skills 更新 ...`。

1. 工作树干净时，先运行 `"$repo/sync-skills" <skill-name>`，确保目标基于最新上游。
2. 按需求编辑 `skills/<skill-name>`；“加入某个功能”和“删除某个功能”都只做明确要求的最小改动。
3. 使用 skill 自带校验或 `skill-creator` 的 `quick_validate.py` 验证。
4. 仅在名称或来源变化时更新 `README.md` 和 `skills/sources.json`；普通内容修改不改目录记录。
5. 只提交本次修改的目标文件，不带入其他 working tree 改动。
6. 提交后运行 `"$repo/sync-skills" <skill-name>`，只把该 skill 部署到 `~/.agents/skills`，并 push 到远端。

每次添加、删除或更换来源后，确认 `README.md` 与 `skills/sources.json` 一致。
