# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **Domain glossary**: apply the selection rules below at the project root, or for each relevant context in the root `GLOSSARY-MAP.md` if it exists.
- **`.planning/adr/`** at the project root: the default destination for new ADRs, shared across tasks. Also read existing ADRs in `docs/adr/` and relevant `src/<context>/docs/adr/` directories. Preserve a project's explicitly configured ADR location. When the session already has a selected PWF plan, record changed glossary and ADR paths in it.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

## Glossary selection

Honor an explicit project convention for glossary paths or language. Otherwise choose one existing file per context:

- For Simplified Chinese work, prefer `GLOSSARY.zh-CN.md` and fall back to `GLOSSARY.md`.
- For other languages or when no language is requested, prefer `GLOSSARY.md` and fall back to `GLOSSARY.zh-CN.md`.

With `GLOSSARY-MAP.md`, use the directory of each linked glossary for this lookup. Follow custom glossary filenames in the map as written. When updating terms, edit the selected file; do not create or synchronize a translation automatically. If neither file exists and a new glossary is needed, use `GLOSSARY.md` unless the project or user specifies otherwise.

## File structure

Single-context repo (either glossary filename may be used):

```
/
├── GLOSSARY.md
├── .planning/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

Multi-context repo (the map can link either glossary filename):

```
/
├── GLOSSARY-MAP.md
├── .planning/adr/
│   ├── 0001-system-decision.md     ← system-wide decisions
│   ├── ordering/                  ← context-specific decisions
│   └── billing/
└── src/
    ├── ordering/
    │   └── GLOSSARY.md
    └── billing/
        └── GLOSSARY.md
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term from the selected glossary. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders), but worth reopening because…_
