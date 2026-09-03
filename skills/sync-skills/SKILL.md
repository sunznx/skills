---
name: sync-skills
description: 同步本仓库与外部 skill 上游、~/.agents/skills 和已登记的 Codex plugins。用户要求检查、安装或更新 skills/plugins，以及添加、删除仓库中的 skill 时使用。
---

# Sync Skills

先读取仓库根目录 `README.md` 和 `skills/sources.json`，再判断用户要同步还是本地修改 skill。

## 同步

```bash
repo="$(cat ~/.config/sync-skills/repo)"
"$repo/sync-skills"
"$repo/sync-skills" <skill-name>
"$repo/sync-skills" plugins
"$repo/sync-skills" plugin <plugin-name>
"$repo/sync-skills" 添加 <skill-name>
"$repo/sync-skills" 删除 <skill-name>
```

- `$sync-skills`：运行无参数命令，对比全部 skill 上游、部署快照，再同步 `skills/sources.json` 中登记的 plugins。
- `$sync-skills <skill-name>`：只对比并只部署指定 skill。
- `$sync-skills plugins`：更新全部登记的 Git marketplaces，重新安装对应 plugins，并执行声明的 `post_install`。
- `$sync-skills plugin <plugin-name>`：只同步指定 plugin。
- `添加` 从 `~/.agents/skills/<skill-name>` 导入。脚本会读取 `~/.agents/.skill-lock.json` 记录外部来源；没有来源记录时按本地 skill 管理。
- `删除` 会删除仓库目录和来源目录，commit 成功后再删除 `~/.agents/skills/<skill-name>`。
- 上游有更新时使用旧上游、本地版本和新上游做三方合并。合并成功后自动 commit，再同步本机目录。
- 出现冲突时检查 `skills/.sync-conflicts.json` 和文件内的冲突标记。解决冲突并手动 commit 前，不同步本机目录。
- 上游 Git 缓存统一写入 `~/.agents/cache/sync-skills`。
- 拉取上游失败但本地镜像可用时，警告后继续使用缓存并部署；没有可用镜像时停止。
- 每次成功调用最后都执行 `git push`。没有改动时不创建空 commit；push 失败时报告错误，但不要撤销已经完成的 commit 或本机同步。

## 安装 plugin

`$sync-skills 安装 <GitHub URL>` 表示安装并登记 Codex plugin，不是 shell 子命令。

1. 读取上游 README 和 plugin manifest，确认 marketplace、plugin 名称及必要的安装后脚本。
2. 使用 `codex plugin marketplace add` 和 `codex plugin add` 安装；执行上游明确要求的 companion installer。
3. 将用户配置的 Git marketplace plugin 写入 `skills/sources.json` 的 `plugins`；Codex 内置和 runtime plugins 不登记。
4. 运行 `update_readme` 更新来源目录，再用 `"$repo/sync-skills" plugin <plugin-name>` 验证。
5. 只提交本次涉及的清单、文档或脚本，并 push。Plugin 保持由 Codex marketplace 管理，不复制进 `skills/`。

## 本地更新 skill

`$sync-skills 更新 <skill-name> <需求>` 表示修改仓库快照，不是执行 `./sync-skills 更新 ...`。

1. 工作树干净时，先运行 `"$repo/sync-skills" <skill-name>`，确保目标基于最新上游。
2. 按需求编辑 `skills/<skill-name>`；“加入某个功能”和“删除某个功能”都只做明确要求的最小改动。
3. 使用 skill 自带校验或 `skill-creator` 的 `quick_validate.py` 验证。
4. 仅在名称或来源变化时更新 `README.md` 和 `skills/sources.json`；普通内容修改不改目录记录。
5. 只提交本次修改的目标文件，不带入其他 working tree 改动。
6. 提交后运行 `"$repo/sync-skills" <skill-name>`，只把该 skill 部署到 `~/.agents/skills`，并 push 到远端。

每次添加、删除或更换来源后，确认 `README.md` 与 `skills/sources.json` 一致。
