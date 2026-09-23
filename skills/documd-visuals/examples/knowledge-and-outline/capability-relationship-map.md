# Central Concept Map — Capability Relationships (Infographic)

**Best for**: a small hub-and-spoke relationship picture where one central concept connects to a handful of related capabilities
**Avoid when**: the graph is dense, highly directional, or needs weighted edges and algorithmic layout control
**Answers**: what sits at the center, and which surrounding ideas or services relate to it

```infographic
infographic relation-circle-icon-badge
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
  title Capability Relationship Map
  desc One central capability and the surrounding support domains
  nodes
    - id core
      label Platform Core
      group central
    - id identity
      label Identity
      group support
    - id billing
      label Billing
      group support
    - id search
      label Search
      group support
    - id analytics
      label Analytics
      group support
    - id security
      label Security
      group support
  relations
    - from core
      to identity
    - from core
      to billing
    - from core
      to search
    - from core
      to analytics
    - from core
      to security
```

## Data Shape

Use `nodes` and `relations` when you have one center and a few simple surrounding connections.

## Key Options

| Option | Effect |
|---|---|
| `relation-circle-icon-badge` | Hub-and-spoke relation treatment |
| `nodes` | Declares the entities shown in the map |
| `relations` | Declares which entities connect |
| `group` | Lets the template distinguish the central node from its satellites |

## Pitfalls

- ❌ Large dependency webs → ✅ this family is best for a small conceptual relation map
- ❌ Treating it like a precise architecture graph → ✅ use graph/dot when layout control matters
- ❌ Omitting stable node IDs → ✅ relations should bind to IDs, not only labels

## Alternatives

| Variant | Use instead |
|---|---|
| Directed service dependency graph | `service-dependency-network.md` |
| Explicit network or architecture topology | PlantUML or ECharts graph examples |
| Hierarchical tree | `platform-org-structure.md` |

<!-- source: AntV Infographic template reference (`relation-circle-icon-badge`) + syntax docs for nodes/relations -->