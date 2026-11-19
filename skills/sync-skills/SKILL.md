---
name: sync-skills
description: Synchronizes skills with upstream sources, ~/.agents/skills, and Claude skills, and manages registered Codex and Claude plugins. Use to check, install, update, add, or remove skills or plugins.
---

# Sync Skills

## Start

Run `git rev-parse --show-toplevel` first:

- If it fails, you are outside a Git worktree. Skip `.mode` initialization.
- In Git, use the reported project root. If `.mode` does not exist there, create it with the single line `autonomous gate`.
- Leave any existing file, directory, or symlink named `.mode` unchanged.

Read the repository's `README.md` and `skills/sources.json` before choosing between synchronization and a local edit.

## Synchronize

```bash
repo="$(cat ~/.config/sync-skills/repo)"
"$repo/sync-skills"
"$repo/sync-skills" <skill-name>
"$repo/sync-skills" plugins
"$repo/sync-skills" plugin <plugin-name>
"$repo/sync-skills" 添加 <skill-name>
"$repo/sync-skills" 删除 <skill-name>
```

- `$sync-skills`: Check upstream sources for all skills, deploy snapshots, and synchronize plugins in `skills/sources.json`.
- `$sync-skills <skill-name>`: Check and deploy just that skill.
- `$sync-skills plugins`: For each plugin's `clients`, update or add its Git marketplace, install or update it, verify that it is enabled, then run its `post_install`. `sources.<client>` may override the source and `post_install` for one client. Restart Claude Code to load an updated plugin.
- `$sync-skills plugin <plugin-name>`: Synchronize just that plugin.
- `添加`: Import from `~/.agents/skills/<skill-name>`. The script looks for upstream provenance in `~/.agents/.skill-lock.json` and treats the skill as local if absent.
- `删除`: Remove the repository and provenance entries, then remove `~/.agents/skills/<skill-name>` after committing.
- For an upstream update, merge the old upstream, local version, and new upstream. Commit a clean merge before deploying it locally.
- If the merge conflicts, inspect `skills/.sync-conflicts.json` and the conflict markers. Do not deploy before resolving and manually committing.
- The upstream Git cache is `~/.agents/cache/sync-skills`.
- If fetching fails, warn and use the local upstream cache if available. Stop if no usable cache exists.
- Every successful invocation ends with `git push`. Do not make an empty commit. If push fails, report it without reverting the commit or local deployment.

## Live mirrors and upstream synchronization

In this environment, syncer mirrors `skills/<skill-name>/` and `~/.agents/skills/<skill-name>/`. Mirroring does not require a commit, deployment command, or manual copy.

- `添加 <skill-name>` tracks an existing local skill and records its provenance; it is not a local deployment command.
- `$sync-skills <skill-name>` checks and merges upstream, updates the snapshot and provenance, and lets the live mirror propagate the files.
- Run the applicable check on skill changes. Update `README.md` and `skills/sources.json` when a name or source changes; mirroring does not update repository metadata.
- A dirty worktree can prevent upstream merges, commits, or pushes without affecting live mirroring.

## Install a plugin

`$sync-skills 安装 <GitHub URL>` requests installation and registration of a Codex plugin; it is not a shell command.

1. Read the upstream README and plugin manifest. Verify the marketplace, plugin name, and required `post_install` steps.
2. Register the Git marketplace plugin in `plugins` in `skills/sources.json`. Set `clients` to the supported subset of `codex` and `claude`. Put any upstream-required companion installer in `post_install`. Do not register bundled Codex or runtime plugins.
3. Run `"$repo/sync-skills" plugin <plugin-name>` for the declared clients.
4. Run `update_readme` to refresh the source index.
5. Commit and push only the changed registry, docs, and scripts. Client marketplaces manage the plugins; do not copy them into `skills/`.

## Synchronize Claude

When the user requests skill or plugin synchronization for Claude:

1. Link each `skills/*` entry to `~/.claude/skills/<name>`. Leave an existing target unchanged.
2. Run `"$repo/sync-skills" plugins` for plugins. Only entries whose `clients` includes `claude` install for Claude. Do not list `claude` for unsupported plugins such as `sol-advisor`.
3. Verify links with `ls -la ~/.claude/skills` and report any skipped targets.
4. Do not change `skills/sources.json` for client setup alone. Update it only when registering or replacing provenance.

## Make a local edit

`$sync-skills 更新 <skill-name> <requirement>` requests an edit to the repository snapshot, not invocation of `./sync-skills 更新 ...`.

1. If the worktree is clean, run `"$repo/sync-skills" <skill-name>` first to check the upstream baseline.
2. Edit `skills/<skill-name>` only within the requested scope.
3. Run the skill's validation or `skill-creator`'s `quick_validate.py`.
4. Update `README.md` and `skills/sources.json` only if the name or source changes.
5. Commit only the requested files, not other worktree changes.
6. Run `"$repo/sync-skills" <skill-name>` after committing to deploy that skill and push to the remote.

After adding, removing, or changing a source, confirm that `README.md` agrees with `skills/sources.json`.
