# Stakeholder Circle Wheel — Who Sits Around The Decision (Infographic)

**Best for**: showing the stakeholder ring around a decision, where each party hands off to the next
**Avoid when**: the connections are one-directional dependencies (use a dependency graph)
**Answers**: who is involved, and how the conversation moves around the circle

```infographic
infographic relation-circle-circular-progress
theme
  colorPrimary #2b66c4
  palette
    - #2b66c4
    - #2f9e44
    - #f3a33c
    - #d1242f
    - #7048e8
    - #0f9b9b
    - #c16f8a
    - #7c5a3d
data
  title Launch Decision Circle
  desc Each link names what is handed over
  nodes
    - id product
      label Product
    - id design
      label Design
    - id engineering
      label Engineering
    - id security
      label Security
    - id support
      label Support
  relations
    - from product
      to design
      label scope
    - from design
      to engineering
      label flows
    - from engineering
      to security
      label threat model
    - from security
      to support
      label runbook gaps
    - from support
      to product
      label field feedback
```

## Data Shape

`nodes` plus `relations` that form a **closed ring** — this structure arranges nodes on a circle, so a broken
chain looks like a mistake. Edge labels state what travels between parties.

## Key Options

| Option | Effect |
|---|---|
| `infographic relation-circle-circular-progress` | Circle layout with progress-style nodes |
| `relation-circle-icon-badge` | Icon badges — good when teams have symbols |
| `relation-network-*` | Use for non-circular topologies |

## Pitfalls

- ❌ A ring that is really a chain → ✅ if it does not loop, use a sequence or dagre layout
- ❌ Unlabelled edges → ✅ the handover artefact is the useful information
- ❌ Nine nodes → ✅ six is the practical maximum around a 900×600 circle

## Alternatives

| Variant | Use instead |
|---|---|
| Concept relationship map | `capability-relationship-map.md` |
| Platform dependency topology | `platform-dependency-graph.md` |
| Escalation ladder | `incident-escalation-path.md` |

<!-- source: AntV Infographic syntax docs + template list (`relation-circle-circular-progress`) -->
