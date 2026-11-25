---
name: setup-matt-pocock-skills
description: "Configure Matt engineering skills: set up the issue tracker, triage labels, domain layout, and lint guidance under .planning, and link them from AGENTS.override.md. Includes a shared missing-only configuration initializer."
---

# Setup Matt Pocock's Skills

Scaffold the per-repo configuration that the engineering skills assume:

- **Issue tracker**: where issues live (GitHub by default; local markdown is also supported out of the box)
- **Triage labels**: the strings used for the five canonical triage roles
- **Domain docs**: where `GLOSSARY.md` and ADRs live, and the consumer rules for reading them
- **Lint and verification**: where to find the project's checks and retrospective rules

Manual setup is prompt-driven: explore, confirm the intended configuration, then write. Dependent skills use the deterministic [missing-only initializer](references/ensure-config.md) directly; that path fills defaults without running this interview or editing steering files.

Use `planning-with-files` to select or create this task's plan as `<PLAN_DIR>`; when another workflow invokes this skill, use that workflow's selected plan. Log setup in its `progress.md`, and keep per-run drafts and verification records in `<PLAN_DIR>/setup-matt-pocock-skills/`.

Project configuration lives in `.planning/issue-tracker.md`, `.planning/triage-labels.md`, `.planning/domain.md`, and `.planning/lint.md` at the project root. Manual setup writes their summaries and reading pointers to the root `AGENTS.override.md`. Specs and tickets live under each task's `<PLAN_DIR>`; new ADRs default to the project's `.planning/adr/`, shared across tasks. Preserve existing configuration unless the user explicitly requests a change.

## Shared initialization

Before a dependent skill reads configuration, follow [references/ensure-config.md](references/ensure-config.md). The script preserves existing files and imports a corresponding `docs/agents/` file unchanged when the `.planning/` file is missing. Otherwise it seeds the bundled defaults and reports created, preserved and imported paths.

The automatic path writes configuration only. It does not create issues, labels, glossary/ADR documents or modify agent instruction files, including `AGENTS.override.md`.

## Process

### 1. Explore

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- `git remote -v` and `.git/config`: is this a GitHub repo? Which one?
- `AGENTS.override.md`, `AGENTS.md`, and `CLAUDE.md` at the repo root: read existing rules and any `## Agent skills` sections before drafting the override update.
- Root `GLOSSARY.md`, `GLOSSARY.zh-CN.md`, and `GLOSSARY-MAP.md`, plus any glossaries linked by the map. Read any existing pair using the [bilingual glossary rules](domain.md#bilingual-glossaries). Check for legacy `CONTEXT.md` and `CONTEXT-MAP.md`. Offer to rename a legacy file only if it would not replace an existing glossary or map, and update the references in `.planning/domain.md` if approved.
- `.planning/adr/`, `docs/adr/` and any `src/*/docs/adr/` directories
- `.planning/` and legacy `docs/agents/`: does configuration already exist? Read it before proposing changes.
- the selected `<PLAN_DIR>`: check existing `spec.md`, `tickets/`, and `wayfinder/` artifacts
- Is the `triage` skill installed? (a `triage` skill folder alongside this one, or `triage` in your available skills.) This decides whether remote label creation is needed. The local label mapping is always available to `to-spec` and `to-tickets`.
- Monorepo signals: a `pnpm-workspace.yaml`, a `workspaces` field in `package.json`, or a populated `packages/*` with its own `src/`. These are present only in a genuinely large multi-package repo; their absence means single-context, which is almost every repo.

### 2. Present findings and ask

Summarise what's present and what's missing. Then take the sections in order. One section, one answer, then the next.

Lead each section with the recommended answer so the user can accept it in a word. Give a one-line explainer only when the choice genuinely branches; skip the section entirely when exploration already settled it (Section B when `triage` isn't installed, Section C when there's no monorepo).

**Section A: Issue tracker.**

> Explainer: The "issue tracker" is where issues live for this repo. Skills like `to-tickets`, `triage`, and `to-spec` read from and write to it. They need to know whether to call `gh issue create`, write a Markdown file under `<PLAN_DIR>/tickets/`, or follow some other workflow you describe. Pick the place you actually track work for this repo.

Default posture: these skills were designed for GitHub. If a `git remote` points at GitHub, propose that. If a `git remote` points at GitLab (`gitlab.com` or a self-hosted host), propose GitLab. Otherwise (or if the user prefers), offer:

- **GitHub**: issues live in the repo's GitHub Issues (uses the `gh` CLI)
- **GitLab**: issues live in the repo's GitLab Issues (uses the [`glab`](https://gitlab.com/gitlab-org/cli) CLI)
- **Local markdown**: implementation tickets live under `<PLAN_DIR>/tickets/` and decision maps under `<PLAN_DIR>/wayfinder/` (good for solo projects or repos without a remote)
- **Other** (Jira, Linear, etc.): ask the user to describe the workflow in one paragraph; the skill will record it as freeform prose

Record the choice in `.planning/issue-tracker.md`. The GitHub and GitLab templates carry a "PRs as a request surface" flag, defaulted **off**. Leave it off and don't raise it: a user who wants external PRs in the triage queue can flip the flag in the file later.

A GitHub or GitLab tracker needs a reachable repo. When the user picks one and no `git remote` points at that host, get the repo URL from them and wire it up (`git init` if needed, `git remote add origin <url>`) before going further. Done when `gh repo view` / `glab repo view` prints the project from inside this directory; if it can't, stop and tell the user what's missing.

**Section B: Triage label vocabulary.** If `triage` is absent, retain the standard mapping without asking; `to-spec` and `to-tickets` also consume it. Remote label creation is needed only when `triage` is installed and the tracker is GitHub or GitLab.

If it is installed, ask exactly one question:

> Do you want to keep the default triage labels? (recommended: **yes**)

The defaults are the five canonical roles, each label string equal to its name: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. On **yes**, write them as-is. Only if the user says no, usually because their tracker already uses other names (e.g. `bug:triage` for `needs-triage`), collect the overrides so `triage` applies existing labels instead of creating duplicates.

**Section C: Domain docs.** Keep an existing layout. Otherwise default to **single-context**: root glossaries and new ADRs in `.planning/adr/`. `GLOSSARY.md` and `GLOSSARY.zh-CN.md` can coexist as a pair. Read existing project ADRs too. Write the layout without asking when there is no layout choice to make.

Offer a new **multi-context** layout only when exploration found monorepo signals. Confirm the layout with the user. `GLOSSARY-MAP.md` remains the root index; each context can have the same glossary pair.

### 3. Confirm and edit

Show the user a draft of:

- The `## Agent skills` block to add or update in the project root's `AGENTS.override.md`, including any baseline-reading instruction needed when creating it
- The contents of `.planning/issue-tracker.md`, `.planning/domain.md`, `.planning/triage-labels.md`, and `.planning/lint.md`

Let them edit before writing.

### 4. Write

**Write the configuration index to `AGENTS.override.md`.** Use `update-agents-override-md` to create or update that file at the project root. This destination applies whether `CLAUDE.md` or `AGENTS.md` exists. Leave those files intact.

Preserve existing override rules and its instruction to read the same-directory `AGENTS.md`. When creating an override beside an existing `AGENTS.md`, include an explicit instruction to read that file and follow its rules except where the override changes them. Keep one baseline-reading pointer.

If an `## Agent skills` block already exists in `AGENTS.override.md`, update it in place rather than appending a duplicate. Preserve user edits outside the block. Keep full configuration in `.planning/`; the override contains only summaries and reading pointers.

The block:

```markdown
## Agent skills

### Issue tracker

[one-line summary of where issues are tracked]. See `.planning/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `.planning/triage-labels.md`.

### Domain docs

[one-line summary of layout: "single-context" or "multi-context"]. See `.planning/domain.md`.

### Lint and verification

Before changing code, read `.planning/lint.md` for the project's checks.
```

Include the label mapping and its pointer even without `triage`; preserve any existing custom mapping.

When `triage` is installed and the chosen tracker is GitHub or GitLab, create each approved configured label the tracker lacks (`gh label create` / `glab label create`).

For missing configuration, seed the selected templates through the shared script (`<CHOSEN_TRACKER>` is `local`, `github`, or `gitlab`):

```bash
python3 "<SETUP_SKILL_DIR>/scripts/ensure-config.py" --project-root "<PROJECT_ROOT>" --tracker "<CHOSEN_TRACKER>"
```

This preserves existing files, including imported legacy configuration. Apply only the revisions approved in step 3 to existing configuration; rerunning the script never changes the tracker. Use the seed templates in this skill folder as a starting point:

- [issue-tracker-github.md](./issue-tracker-github.md): GitHub issue tracker
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md): GitLab issue tracker
- [issue-tracker-local.md](./issue-tracker-local.md): local-markdown issue tracker
- [triage-labels.md](./triage-labels.md): label mapping
- [domain.md](./domain.md): domain doc consumer rules + layout
- [lint.md](./lint.md): project checks and the retrospective index

For "other" issue trackers, first write `.planning/issue-tracker.md` using the user's description. Then run the initializer with `--tracker local` to fill the other missing files.

### 5. Done

Tell the user which configuration files were created or updated, that their index is in `AGENTS.override.md`, and which engineering skills read them. Mention they can edit `.planning/*.md` directly later; re-running this skill is only necessary if they want to switch issue trackers or restart from scratch.
