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
| `background-agent-jobs` | 本地维护，暂无外部 Git 来源 | — | 本地维护 |
| `birdview` | [Qiuner/birdview](https://github.com/Qiuner/birdview) | `SKILL.md` | 三方合并 |
| `code-review` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/code-review/SKILL.md` | 三方合并 |
| `codebase-design` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/codebase-design/SKILL.md` | 三方合并 |
| `correct` | [cursor/plugins](https://github.com/cursor/plugins) | `pstack/skills/correct/SKILL.md` | 三方合并 |
| `create-formal-verification-skill` | [cursor/plugins](https://github.com/cursor/plugins) | `pstack/skills/create-formal-verification-skill/SKILL.md` | 三方合并 |
| `cua-driver` | 本机链接 ~/.cua-driver/skills/cua-driver，仓库保留快照但不覆盖该链接 | — | 仅仓库维护 |
| `diagnosing-bugs` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/diagnosing-bugs/SKILL.md` | 三方合并 |
| `diagram-design` | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | `skills/diagram-design/SKILL.md` | 三方合并 |
| `documd-visuals` | [markdown-viewer/skills](https://github.com/markdown-viewer/skills) | `documd-visuals/SKILL.md` | 三方合并 |
| `domain-modeling` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/domain-modeling/SKILL.md` | 三方合并 |
| `ego-browser` | [citrolabs/ego-lite](https://github.com/citrolabs/ego-lite) | `skills/ego-browser/SKILL.md` | 三方合并（仅仓库） |
| `eli5` | [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) | `eli5/skills/eli5/SKILL.md` | 三方合并 |
| `explain` | [cursor/plugins](https://github.com/cursor/plugins) | `pstack/skills/teach/SKILL.md` | 三方合并 |
| `grill-with-docs` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/grill-with-docs/SKILL.md` | 三方合并 |
| `grilling` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/productivity/grilling/SKILL.md` | 三方合并 |
| `handoff` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/productivity/handoff/SKILL.md` | 三方合并 |
| `how` | [cursor/plugins](https://github.com/cursor/plugins) | `pstack/skills/how/SKILL.md` | 三方合并 |
| `human-context-rebuild` | [lycfyi/yskills](https://github.com/lycfyi/yskills) | `skills/human-context-rebuild/SKILL.md` | 三方合并 |
| `implement` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/implement/SKILL.md` | 三方合并 |
| `implement-spec` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/implement-spec/SKILL.md` | 三方合并 |
| `improve-codebase-architecture` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/improve-codebase-architecture/SKILL.md` | 三方合并 |
| `in-your-own-words` | [cursor/plugins](https://github.com/cursor/plugins) | `pstack/skills/in-your-own-words/SKILL.md` | 三方合并 |
| `lark-doc` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-doc/SKILL.md` | 三方合并 |
| `lark-shared` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-shared/SKILL.md` | 三方合并 |
| `obsidian-simple-mind-map` | 本地维护，暂无外部 Git 来源 | — | 本地维护 |
| `opencli-adapter-author` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-adapter-author/SKILL.md` | 三方合并 |
| `opencli-autofix` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-autofix/SKILL.md` | 三方合并 |
| `opencli-browser` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-browser/SKILL.md` | 三方合并 |
| `opencli-usage` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-usage/SKILL.md` | 三方合并 |
| `planning-with-files` | [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | `.agents/skills/planning-with-files/SKILL.md` | 三方合并（仅仓库） |
| `prototype` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/prototype/SKILL.md` | 三方合并 |
| `pwf-artifact` | 本地维护，显式保存 PWF 任务产物 | — | 本地维护 |
| `recall` | 本地维护，从 PWF 计划和 git 现状重建工作上下文并报告漂移 | — | 本地维护 |
| `reflect` | [cursor/plugins](https://github.com/cursor/plugins) | `pstack/skills/reflect/SKILL.md` | 三方合并 |
| `research` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/research/SKILL.md` | 三方合并 |
| `retro` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/retro/SKILL.md` | 三方合并 |
| `setup-matt-pocock-skills` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/setup-matt-pocock-skills/SKILL.md` | 三方合并 |
| `show-me` | [humanlayer/skills](https://github.com/humanlayer/skills) | `plugins/show-me/skills/show-me/SKILL.md` | 三方合并 |
| `skill-doctor` | [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills) | `.agents/skills/skill-doctor/SKILL.md` | 三方合并 |
| `smart-search` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/smart-search/SKILL.md` | 三方合并 |
| `spec-bootstrap` | 本地维护，全局安装 Planning with Files plugin 与 lifecycle hooks | — | 本地维护 |
| `statechart` | [cursor/plugins](https://github.com/cursor/plugins) | `pstack/skills/statechart/SKILL.md` | 三方合并 |
| `sync-skills` | 本仓库维护的同步 skill | — | 本地维护 |
| `tdd` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/tdd/SKILL.md` | 三方合并 |
| `teach` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/productivity/teach/SKILL.md` | 三方合并 |
| `technical-writing` | [cursor/plugins](https://github.com/cursor/plugins) | `pstack/skills/technical-writing/SKILL.md` | 三方合并 |
| `thermo-nuclear-code-quality-review` | [cursor/plugins](https://github.com/cursor/plugins) | `cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md` | 三方合并 |
| `to-spec` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/to-spec/SKILL.md` | 三方合并 |
| `to-tickets` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/to-tickets/SKILL.md` | 三方合并 |
| `triage` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/triage/SKILL.md` | 三方合并 |
| `unslop` | [cursor/plugins](https://github.com/cursor/plugins) | `pstack/skills/unslop/SKILL.md` | 三方合并 |
| `update-skill` | [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills) | `.agents/skills/update-skill/SKILL.md` | 三方合并 |
| `visual-pr` | [humanlayer/skills](https://github.com/humanlayer/skills) | `plugins/visual-pr/skills/visual-pr/SKILL.md` | 三方合并 |
| `wait-what` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/productivity/wait-what/SKILL.md` | 三方合并 |
| `wayfinder` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/wayfinder/SKILL.md` | 三方合并 |
| `what-did-i-get-done` | [cursor/plugins](https://github.com/cursor/plugins) | `cursor-team-kit/skills/what-did-i-get-done/SKILL.md` | 三方合并 |
| `whats-next` | [lycfyi/yskills](https://github.com/lycfyi/yskills) | `skills/whats-next/SKILL.md` | 三方合并 |
| `why` | [cursor/plugins](https://github.com/cursor/plugins) | `pstack/skills/why/SKILL.md` | 三方合并 |
| `wizard` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/wizard/SKILL.md` | 三方合并 |
| `writing-for-agents` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/productivity/writing-for-agents/SKILL.md` | 三方合并 |

## Plugin 来源目录

| Plugin | Marketplace | 外部来源 | Clients | 安装后命令 |
| --- | --- | --- | --- | --- |
| `planning-with-files` | `planning-with-files` | codex: [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files)<br>claude: [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) | codex, claude | — |
<!-- skill-catalog:end -->
