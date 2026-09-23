# Work Breakdown Structure (engine gap — use the alternatives below)

**Best for**: deliverables and ownership in a strict hierarchy — **but not with `@startwbs` in this engine**
**Avoid when**: you need free-form idea exploration (use `topic-mindmap.md`)
**Answers**: what the work is made of and who owns each part

> ⚠️ **Engine limitation (verified 2026-09-21)**: `@startwbs … @endwbs` **parses without error but renders an empty
> diagram**. Use one of the two supported forms below instead.

## Option A — hierarchy as a mind map (recommended)

```plantuml
@startmindmap
title Platform Programme — Work Breakdown

* Platform Programme
** 1. Discovery
*** 1.1 Current-state assessment
*** 1.2 Stakeholder interviews
*** 1.3 Target architecture draft
** 2. Core Platform
*** 2.1 Identity and access
**** 2.1.1 SSO integration
**** 2.1.2 Role model
*** 2.2 Service runtime
**** 2.2.1 Container platform
**** 2.2.2 CI/CD pipelines
*** 2.3 Data layer
**** 2.3.1 Schema migration
**** 2.3.2 Reconciliation tooling
** 3. Adoption
*** 3.1 Migration playbook
*** 3.2 Team enablement
*** 3.3 Support model
** 4. Governance
*** 4.1 Architecture review board
*** 4.2 Security and compliance sign-off
*** 4.3 Cost reporting
@endmindmap
```

## Option B — hierarchy as a Graphviz tree (when you need boxed, top-down layout)

```dot
digraph WBS {
  node [style=filled fillcolor="#eef2fb" color="#5b6b8c" fontcolor="#1f2937"]
  edge [color="#5b6b8c" fontcolor="#676f7e"]
  rankdir=TB;
  node [shape=box, style=rounded, fontname="Helvetica"];

  programme [label="Platform Programme"];
  d1 [label="1. Discovery"]; c1 [label="2. Core Platform"];
  a1 [label="3. Adoption"]; g1 [label="4. Governance"];
  programme -> {d1 c1 a1 g1};

  d1 -> {d11 [label="1.1 Assessment"]; d12 [label="1.2 Interviews"]; d13 [label="1.3 Target architecture"]};
  c1 -> {c11 [label="2.1 Identity"]; c12 [label="2.2 Runtime"]; c13 [label="2.3 Data"]};
  c11 -> {c111 [label="2.1.1 SSO"]; c112 [label="2.1.2 Roles"]};
  a1 -> {a11 [label="3.1 Playbook"]; a12 [label="3.2 Enablement"]; a13 [label="3.3 Support"]};
  g1 -> {g11 [label="4.1 Review board"]; g12 [label="4.2 Sign-off"]; g13 [label="4.3 Cost"]};
}
```

## Key Options

| Syntax | Where it applies | Effect |
|---|---|---|
| `*` / `**` / `***` / `****` | mind map | Depth levels — indentation is expressed by asterisk count, not spaces |
| `left side` | mind map | Move the following branches to the left half |
| `rankdir=TB` + `->` chains | Graphviz | Top-down tree |
| `node [shape=box, style=rounded]` | Graphviz | Boxed nodes read as deliverables rather than concepts |
| WBS numbering in the text | both | Number the nodes (`2.1.1`) so reviews can cite them |

## Data Shape

A pure tree, 3–4 levels deep. Each leaf should be a deliverable someone can own; if a leaf is an activity, the
structure has drifted from WBS into a project plan.

## Pitfalls

- ❌ Writing `@startwbs` → ✅ it renders empty in this engine; use Option A or B above
- ❌ Leaves that are activities ("run tests") → ✅ leaves are deliverables/artefacts
- ❌ Unnumbered nodes → ✅ WBS numbering is what makes the structure citable in plans and reviews
- ❌ More than four levels → ✅ deeper than four means it belongs in a separate sub-structure

## Alternatives

| Variant | Use instead |
|---|---|
| Org chart with team names | Option B (Graphviz tree), or a mind map using `left side` |
| Free-form topic decomposition | `topic-mindmap.md` |
| Dated plan | `release-gantt-plan.md` |

<!-- source: gap verified via documd (342 B blank SVG), confirmed by draw-uml-dev fixtures/svg-generated/creole/036.svg (342 B) vs official baseline (4535 B) -->

