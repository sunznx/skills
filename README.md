# Skills

这个仓库存放我正在使用的 skills。外部更新会经过三方合并，因此仓库里的差异化修改可以保留。

## 使用

```bash
./sync-skills
./sync-skills 添加 <skill-name>
./sync-skills 删除 <skill-name>
```

- 无参数调用会直接对比全部上游；有更新时合并并 commit。
- `添加` 从 `~/.agents/skills` 导入指定 skill，并更新来源目录。
- `删除` 从仓库、来源目录和 `~/.agents/skills` 移除指定 skill。
- 没有冲突时，仓库清单会同步到 `~/.agents/skills`。
- 上游 Git 缓存保存在 `~/.agents/cache/sync-skills`。

出现合并冲突时，脚本会留下冲突标记并停止 commit 和本机同步。

<!-- skill-catalog:start -->
## Skill 来源目录

| 本仓库 skill | 外部来源 | 外部 skill 路径 | 管理方式 |
| --- | --- | --- | --- |
| `agent-messaging` | 本地维护，暂无外部 Git 来源 | — | 本地维护 |
| `code-simplification` | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | `skills/code-simplification/SKILL.md` | 三方合并 |
| `codebase-design` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/codebase-design/SKILL.md` | 三方合并 |
| `cua-driver` | 本机链接 /Users/sunx/.cua-driver/skills/cua-driver，仓库保留快照但不覆盖该链接 | — | 仅仓库维护 |
| `diagram-design` | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | `skills/diagram-design/SKILL.md` | 三方合并 |
| `domain-modeling` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/domain-modeling/SKILL.md` | 三方合并 |
| `eli5` | [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) | `eli5/skills/eli5/SKILL.md` | 三方合并 |
| `herdr` | [herdrdev/herdr](https://github.com/herdrdev/herdr) | `skills/herdr/SKILL.md` | 三方合并 |
| `human-context-rebuild` | [lycfyi/yskills](https://github.com/lycfyi/yskills) | `skills/human-context-rebuild/SKILL.md` | 三方合并 |
| `improve-codebase-architecture` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/improve-codebase-architecture/SKILL.md` | 三方合并 |
| `karpathy-guidelines` | [CezarDrumea/andrej-karpathy-skills](https://github.com/CezarDrumea/andrej-karpathy-skills) | `skills/karpathy-guidelines/SKILL.md` | 三方合并 |
| `lark-doc` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-doc/SKILL.md` | 三方合并 |
| `lark-shared` | [larksuite/cli](https://github.com/larksuite/cli) | `skills/lark-shared/SKILL.md` | 三方合并 |
| `manage-taskboard` | 本地维护，暂无外部 Git 来源 | — | 本地维护 |
| `opencli-adapter-author` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-adapter-author/SKILL.md` | 三方合并 |
| `opencli-autofix` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-autofix/SKILL.md` | 三方合并 |
| `opencli-browser` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-browser/SKILL.md` | 三方合并 |
| `opencli-browser-sitemap` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-browser-sitemap/SKILL.md` | 三方合并 |
| `opencli-sitemap-author` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-sitemap-author/SKILL.md` | 三方合并 |
| `opencli-usage` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/opencli-usage/SKILL.md` | 三方合并 |
| `prototype` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/prototype/SKILL.md` | 三方合并 |
| `ra-人话` | [Pluviobyte/rnskill](https://github.com/Pluviobyte/rnskill) | `skills/ra-人话/SKILL.md` | 三方合并 |
| `resolve-merge-conflicts` | [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills) | `.agents/skills/resolve-merge-conflicts/SKILL.md` | 三方合并 |
| `skill-doctor` | [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills) | `.agents/skills/skill-doctor/SKILL.md` | 三方合并 |
| `smart-search` | [jackwener/opencli](https://github.com/jackwener/opencli) | `skills/smart-search/SKILL.md` | 三方合并 |
| `sync-skills` | 本仓库维护的同步 skill | — | 本地维护 |
| `update-skill` | [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills) | `.agents/skills/update-skill/SKILL.md` | 三方合并 |
| `wait-what` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/productivity/wait-what/SKILL.md` | 三方合并 |
| `whats-next` | [lycfyi/yskills](https://github.com/lycfyi/yskills) | `skills/whats-next/SKILL.md` | 三方合并 |
| `writing-for-agents` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/productivity/writing-for-agents/SKILL.md` | 三方合并 |
<!-- skill-catalog:end -->
