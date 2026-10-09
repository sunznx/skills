---
name: setup-matt-pocock-skills
description: "Configure Matt engineering skills: choose the issue tracker, triage labels and domain layout under .planning. Includes a shared missing-only configuration initializer."
disable-model-invocation: true
---

# Setup Matt Pocock's Skills

Scaffold the per-repo configuration that the engineering skills assume:

- **Issue tracker**: where issues live (GitHub by default; local markdown is also supported out of the box)
- **Triage labels**: the strings used for the five canonical triage roles
- **Domain docs**: where `GLOSSARY.md` and ADRs live, and the consumer rules for reading them

Manual setup is prompt-driven: explore, confirm the intended configuration, then write. Dependent skills use the deterministic [missing-only initializer](references/ensure-config.md) directly; that path fills defaults without running this interview or editing steering files.

Use `planning-with-files` to resolve a named, gated plan for manual setup. Bind `PLAN_ID` when multiple plans exist. Project configuration lives in `.planning/issue-tracker.md`, `.planning/triage-labels.md`, and `.planning/domain.md` under the project owning the selected plan. Specs and tickets live under `<PLAN_DIR>`; new ADRs default to the project's `.planning/adr/`, shared across tasks. Preserve existing configuration unless the user explicitly requests a change.

## Shared initialization

Before a dependent skill reads configuration, follow [references/ensure-config.md](references/ensure-config.md). The script preserves existing files and imports a corresponding `docs/agents/` file unchanged when the `.planning/` file is missing. Otherwise it seeds local Markdown tracking, the five standard triage labels and the PWF domain layout. It reports created, preserved and imported paths.

The automatic path writes configuration only. It does not create issues, labels, glossary/ADR documents or modify `AGENTS.md`/`CLAUDE.md`.

## Process

### 1. Explore

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- `git remote -v` and `.git/config`: is this a GitHub repo? Which one?
- `AGENTS.md` and `CLAUDE.md` at the repo root: does either exist? Is there already an `## Agent skills` section in either?
- `GLOSSARY.md` and `GLOSSARY-MAP.md` at the repo root
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

**Section B: Triage label vocabulary.** If `triage` is absent, retain the standard mapping without asking; `to-spec` and `to-tickets` also consume it. Remote label creation is needed only when `triage` is installed and the tracker is GitHub or GitLab.

If it is installed, ask exactly one question:

> Do you want to keep the default triage labels? (recommended: **yes**)

The defaults are the five canonical roles, each label string equal to its name: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. On **yes**, write them as-is. Only if the user says no, usually because their tracker already uses other names (e.g. `bug:triage` for `needs-triage`), collect the overrides so `triage` applies existing labels instead of creating duplicates.

**Section C: Domain docs.** Default to **single-context** (`GLOSSARY.md` at the repo root + new ADRs in the project's `.planning/adr/`; read existing project ADRs too). This fits almost every repo; write it without asking.

Offer **multi-context** (a root `GLOSSARY-MAP.md` pointing to per-context `GLOSSARY.md` files) only when exploration found monorepo signals. Then confirm which layout they want.

### 3. Confirm and edit

Show the user a draft of:

- The `## Agent skills` block to add to whichever of `CLAUDE.md` / `AGENTS.md` is being edited (see step 4 for selection rules)
- The contents of `.planning/issue-tracker.md`, `.planning/domain.md`, and `.planning/triage-labels.md` (all three are available to dependent skills)

Let them edit before writing.

### 4. Write

**Pick the file to edit:**

- If `CLAUDE.md` exists, edit it.
- Else if `AGENTS.md` exists, edit it.
- If neither exists, ask the user which one to create; don't pick for them.

Never create `AGENTS.md` when `CLAUDE.md` already exists (or vice versa); always edit the one that's already there.

If an `## Agent skills` block already exists in the chosen file, update its contents in-place rather than appending a duplicate. Don't overwrite user edits to the surrounding sections.

The block:

```markdown
## Agent skills

### Issue tracker

[one-line summary of where issues are tracked]. See `.planning/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `.planning/triage-labels.md`.

### Domain docs

[one-line summary of layout: "single-context" or "multi-context"]. See `.planning/domain.md`.
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

For "other" issue trackers, write `.planning/issue-tracker.md` from scratch using the user's description.

### 5. Done

Tell the user the setup is complete and which engineering skills will now read from these files. Mention they can edit `.planning/*.md` directly later; re-running this skill is only necessary if they want to switch issue trackers or restart from scratch.
