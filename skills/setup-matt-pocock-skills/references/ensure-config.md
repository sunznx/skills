# Ensure Matt configuration

Shared prerequisite for Matt skills that read project configuration. Use the script directly; it does not invoke the manual setup interview.

1. Resolve the named, gated Planning with Files plan first. Use the same `PLAN_ID`. Set `<PROJECT_ROOT>` to `PWF_PLAN_ROOT` when supplied, otherwise to the project owning the selected `<PLAN_DIR>`; a ticket worktree may belong to a different root. All `.planning/` configuration paths in the calling skill are relative to this project root.
2. Locate this installed `setup-matt-pocock-skills` directory from the reference path or available installation metadata. If the support skill is missing, report the dependency and stop; keep the default-generation logic in this one place.
3. Run:

```bash
python3 "<SETUP_SKILL_DIR>/scripts/ensure-config.py" --project-root "<PROJECT_ROOT>"
```

4. Read the JSON report. Tell the user which defaults were created or which legacy configurations were imported, then read the resulting `.planning/issue-tracker.md`, `.planning/triage-labels.md`, and `.planning/domain.md` as the calling skill requires. A failed command stops initialization; report its error.

Existing configuration wins, byte-for-byte. A missing file first imports the same-named legacy `docs/agents/` file unchanged; otherwise it uses the bundled local-tracker, triage-label, or domain template. New local tickets use `<PLAN_DIR>/tickets/`, decision maps use `<PLAN_DIR>/wayfinder/`, and new ADRs use `<PLAN_DIR>/adr/`. Legacy configuration retains its explicit paths until manually revised.

The script creates only the three project-level configuration files. It does not create a PWF plan, task artifacts, glossary/ADR documents, remote issues/labels or steering files. It does not infer a tracker from git remotes. Run manual `setup-matt-pocock-skills` to choose a different tracker or domain layout. Its `--tracker` option selects a template for a missing file only.
