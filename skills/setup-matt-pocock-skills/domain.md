# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **Domain glossaries**: apply the bilingual glossary rules below at the project root, or for each relevant context in the root `GLOSSARY-MAP.md` if it exists.
- **`.planning/adr/`** at the project root: the default destination for new ADRs, shared across tasks. Also read existing ADRs in `docs/adr/` and relevant `src/<context>/docs/adr/` directories. Preserve a project's explicitly configured ADR location. When the session already has a selected PWF plan, record changed glossary and ADR paths in it.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

## Bilingual glossaries

Honor an explicit project convention for glossary paths or languages. Otherwise use these rules per context:

- Read both `GLOSSARY.md` and `GLOSSARY.zh-CN.md` when they exist. They describe the same domain. Use `GLOSSARY.md` for the canonical meaning and `GLOSSARY.zh-CN.md` for Simplified Chinese wording. If definitions disagree, surface the difference before editing.
- If only one file exists, read and maintain that file. Setup does not create a missing companion.
- When an agreed term changes in a bilingual pair, update both files together so their definitions stay aligned. If neither file exists and a glossary is needed, create `GLOSSARY.md` unless the project or user specifies otherwise.

With `GLOSSARY-MAP.md`, look for the pair in the directory of each linked glossary. Follow custom glossary filenames in the map as written.

## File structure

Single-context repo (showing both files; either may exist on its own):

```
/
├── GLOSSARY.md
├── GLOSSARY.zh-CN.md
├── .planning/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

Multi-context repo (each context may have a bilingual pair):

```
/
├── GLOSSARY-MAP.md
├── .planning/adr/
│   ├── 0001-system-decision.md     ← system-wide decisions
│   ├── ordering/                  ← context-specific decisions
│   └── billing/
└── src/
    ├── ordering/
    │   ├── GLOSSARY.md
    │   └── GLOSSARY.zh-CN.md
    └── billing/
        └── GLOSSARY.md
```

## Use the glossary's vocabulary

Use the glossary's term when naming domain concepts in issues, proposals, hypotheses, and tests. Use the wording for the output language when both glossaries exist.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders), but worth reopening because…_
