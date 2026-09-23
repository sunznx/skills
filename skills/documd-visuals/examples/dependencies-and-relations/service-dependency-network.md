# Relation Network — Service Dependencies (Infographic)

**Best for**: a small labeled dependency or concept network where the audience benefits from a pre-styled relational map rather than a low-level graph grammar
**Avoid when**: the network is large, weighted, or needs algorithmic layout control (use graph/dot)
**Answers**: which services depend on which others, and where the central connectors sit

```infographic
infographic relation-network-simple-circle-node
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
  title Service Dependency Network
  desc Core runtime dependencies around the order path
  nodes
    - id gateway
      label Gateway
      group edge
    - id auth
      label Identity
      group core
    - id catalog
      label Catalog
      group core
    - id orders
      label Orders
      group core
    - id billing
      label Billing
      group supporting
    - id warehouse
      label Warehouse
      group supporting
  relations
    - from gateway
      to auth
      label auth
    - from gateway
      to catalog
      label browse
    - from gateway
      to orders
      label checkout
    - from orders
      to billing
      label charge
    - from orders
      to warehouse
      label fulfil
```

## Data Shape

Use `nodes` plus `relations`. Nodes should have stable `id` values; relations connect them with `from` and `to`, and may carry a short `label`.

## Key Options

| Option | Effect |
|---|---|
| `relation-network-simple-circle-node` | A compact network layout with simple node styling |
| `nodes` | Declares the entities in the network |
| `relations` | Declares the connections between nodes |
| `group` | Lets the template visually distinguish node categories |

## Pitfalls

- ❌ Treating this as a precise architecture topology → ✅ it is a high-level relation map, not a protocol diagram
- ❌ Too many nodes → ✅ relation templates saturate quickly; keep them small and conceptual
- ❌ Omitting stable IDs → ✅ relation edges should bind to node IDs, not only display labels

## Alternatives

| Variant | Use instead |
|---|---|
| Rich dependency graph with layout control | `graph-platform-dependencies.md` or DOT |
| Ordered process flow | `product-roadmap-sequence.md` or PlantUML flow examples |
| Layered system structure | PlantUML or HTML architecture overviews |

<!-- source: AntV Infographic syntax docs (`nodes` + `relations`) + template list (`relation-network-simple-circle-node`) -->