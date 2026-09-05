# Skills

这个仓库存放我正在使用的 skills。外部更新会经过三方合并，因此仓库里的差异化修改可以保留。

## 使用

```bash
./sync-skills                    # 检查并更新全部外部 skills
./sync-skills <skill-name>       # 只检查并同步指定 skill
./sync-skills plugins            # 更新清单中的全部 Git marketplace plugins
./sync-skills plugin <name>      # 只更新指定 plugin
./sync-skills 添加 <skill-name>  # 从 ~/.agents/skills 导入一个 skill
./sync-skills 删除 <skill-name>  # 从仓库和本机删除一个 skill
```

- 无参数调用会直接对比全部上游；有更新时合并并 commit。
- 指定 skill 时，只对比该 skill 的上游，并只同步它的仓库快照到本机。
- `plugins` 更新 `skills/sources.json` 中登记的 Git marketplace，并重新安装对应 plugin；无参数调用也会在 skills 同步后执行此步骤。
- plugin 的 `post_install` 若存在，会在安装验证通过后从 plugin 根目录执行。
- 清单只维护用户配置的 Git marketplace plugins；Codex 内置和 runtime plugins 仍由 Codex 管理。
- `添加` 从 `~/.agents/skills` 导入指定 skill，并更新来源目录。
- `删除` 从仓库、来源目录和 `~/.agents/skills` 移除指定 skill。
- 没有冲突时，仓库清单会同步到 `~/.agents/skills`。
- 上游 Git 缓存保存在 `~/.agents/cache/sync-skills`。
- 成功调用后会提交本次同步产生的改动并执行 `git push`；没有改动时不创建空 commit。

出现合并冲突时，脚本会留下冲突标记并停止 commit 和本机同步。

在 agent 对话中，`更新` 表示本地修改 skill，而不是 shell 子命令：

```text
$sync-skills
$sync-skills agent-messaging
$sync-skills 更新 agent-messaging 加入某个功能
$sync-skills 更新 agent-messaging 删除某个功能
```

<!-- skill-catalog:start -->
## Skill 来源目录

| 本仓库 skill | 外部来源 | 外部 skill 路径 | 管理方式 |
| --- | --- | --- | --- |
| `agent-messaging` | 本地维护，暂无外部 Git 来源 | — | 本地维护 |
| `alibabacloud-cli-guidance` | [aliyun/alibabacloud-aiops-skills](https://github.com/aliyun/alibabacloud-aiops-skills) | `skills/developertools/solutions/alibabacloud-cli-guidance/SKILL.md` | 三方合并 |
| `archify` | [tt-a1i/archify](https://github.com/tt-a1i/archify) | `archify/SKILL.md` | 三方合并 |
| `bpmn` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `bpmn/SKILL.md` | 三方合并 |
| `canvas` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `canvas/SKILL.md` | 三方合并 |
| `cloud` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `cloud/SKILL.md` | 三方合并 |
| `codebase-design` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/codebase-design/SKILL.md` | 三方合并 |
| `cua-driver` | 本机链接 ~/.cua-driver/skills/cua-driver，仓库保留快照但不覆盖该链接 | — | 仅仓库维护 |
| `data-analytics` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `data-analytics/SKILL.md` | 三方合并 |
| `diagram-design` | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | `skills/diagram-design/SKILL.md` | 三方合并 |
| `domain-modeling` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/domain-modeling/SKILL.md` | 三方合并 |
| `ego-browser` | [citrolabs/ego-lite](https://github.com/citrolabs/ego-lite) | `skills/ego-browser/SKILL.md` | 三方合并（仅仓库） |
| `eli5` | [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) | `eli5/skills/eli5/SKILL.md` | 三方合并 |
| `graphviz` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `graphviz/SKILL.md` | 三方合并 |
| `grill-with-docs` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/grill-with-docs/SKILL.md` | 三方合并 |
| `human-context-rebuild` | [lycfyi/yskills](https://github.com/lycfyi/yskills) | `skills/human-context-rebuild/SKILL.md` | 三方合并 |
| `improve-codebase-architecture` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/improve-codebase-architecture/SKILL.md` | 三方合并 |
| `infocard` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `infocard/SKILL.md` | 三方合并 |
| `infographic` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `infographic/SKILL.md` | 三方合并 |
| `iot` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `iot/SKILL.md` | 三方合并 |
| `lark-doc` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-doc/SKILL.md` | 三方合并 |
| `lark-shared` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-shared/SKILL.md` | 三方合并 |
| `mindmap` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `mindmap/SKILL.md` | 三方合并 |
| `network` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `network/SKILL.md` | 三方合并 |
| `obsidian-simple-mind-map` | 本地维护，暂无外部 Git 来源 | — | 本地维护 |
| `opencli-adapter-author` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-adapter-author/SKILL.md` | 三方合并 |
| `opencli-autofix` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-autofix/SKILL.md` | 三方合并 |
| `opencli-browser` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-browser/SKILL.md` | 三方合并 |
| `opencli-browser-sitemap` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-browser-sitemap/SKILL.md` | 三方合并 |
| `opencli-sitemap-author` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-sitemap-author/SKILL.md` | 三方合并 |
| `opencli-usage` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-usage/SKILL.md` | 三方合并 |
| `planning-with-files` | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | `.agents/skills/planning-with-files/SKILL.md` | 三方合并（仅仓库） |
| `prototype` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/prototype/SKILL.md` | 三方合并 |
| `pwf-eli5` | 本地维护，绑定 planning-with-files 任务生成 HTML | — | 本地维护 |
| `pwf-show-me` | 本地维护，绑定 planning-with-files 任务生成可视化 HTML | — | 本地维护 |
| `ra-人话` | [Pluviobyte/rnskill](https://github.com/Pluviobyte/rnskill) | `skills/ra-人话/SKILL.md` | 三方合并 |
| `resolve-merge-conflicts` | [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills) | `.agents/skills/resolve-merge-conflicts/SKILL.md` | 三方合并 |
| `security` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `security/SKILL.md` | 三方合并 |
| `show-me` | [humanlayer/skills](https://github.com/humanlayer/skills) | `plugins/show-me/skills/show-me/SKILL.md` | 三方合并 |
| `skill-doctor` | [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills) | `.agents/skills/skill-doctor/SKILL.md` | 三方合并 |
| `smart-search` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/smart-search/SKILL.md` | 三方合并 |
| `spec-bootstrap` | 本地维护，安装项目级 Ponytail、PWF skill 与官方 hooks，并配置 Serena、Semble | — | 本地维护 |
| `sync-skills` | 本仓库维护的同步 skill | — | 本地维护 |
| `uml` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `uml/SKILL.md` | 三方合并 |
| `update-skill` | [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills) | `.agents/skills/update-skill/SKILL.md` | 三方合并 |
| `vega` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `vega/SKILL.md` | 三方合并 |
| `wait-what` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/productivity/wait-what/SKILL.md` | 三方合并 |
| `wayfinder` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/wayfinder/SKILL.md` | 三方合并 |
| `whats-next` | [lycfyi/yskills](https://github.com/lycfyi/yskills) | `skills/whats-next/SKILL.md` | 三方合并 |
| `writing-for-agents` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/productivity/writing-for-agents/SKILL.md` | 三方合并 |

## Plugin 来源目录

| Plugin | Marketplace | 外部来源 | Commands | 安装后命令 |
| --- | --- | --- | --- | --- |
| `planning-with-files` | `planning-with-files` | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 禁用迁移 | — |
| `ponytail` | `ponytail` | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | 默认 | — |
| `sol-advisor` | `sol-advisor` | [DannyMac180/sol-advisor](https://github.com/DannyMac180/sol-advisor) | 默认 | `scripts/install-agents.sh` |
<!-- skill-catalog:end -->
