# Platform Dependency Graph — Services With Icon Nodes (Infographic)

**Best for**: a topology view where services are recognisable by icon rather than name alone
**Avoid when**: an acyclic flow with conditions is needed (use the dagre layout)
**Answers**: which services talk to which, and where the shared foundations sit

```infographic
infographic relation-network-icon-badge
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
  title Service Dependencies — Core Platform
  desc Icons mark the infrastructure layer
  nodes
    - id gateway
      label API Gateway
      icon mdi/door-open
    - id auth
      label Identity
      icon mdi/shield-account
    - id events
      label Event Bus
      icon mdi/source-branch
    - id warehouse
      label Warehouse
      icon mdi/database
    - id billing
      label Billing
      icon mdi/receipt-text
  relations
    - from gateway
      to auth
    - from gateway
      to billing
    - from billing
      to events
    - from events
      to warehouse
```

## Data Shape

`nodes` with `id`, `label`, and an `icon`; `relations` as plain edges (this layout does not label edges well —
put the protocol in the surrounding text).

## Key Options

| Option | Effect |
|---|---|
| `infographic relation-network-icon-badge` | Icon badges for each service |
| `relation-network-simple-circle-node` | Plain circles; best when names are long |
| `relation-dagre-flow` design block | Use for directed flows with ranked ordering |

## Pitfalls

- ❌ Every edge labelled → ✅ this layout crowds quickly; label only the critical path
- ❌ Icons that repeat → ✅ distinct icons make the network scannable
- ❌ Showing all services → ✅ pick the dependency chain being discussed

## Alternatives

| Variant | Use instead |
|---|---|
| Direct dependency chain | `service-dependency-network.md` |
| Escalation with conditions | `incident-escalation-path.md` |
| Capability relationships | `capability-relationship-map.md` |

<!-- source: AntV Infographic syntax docs + template list (`relation-network-icon-badge`) -->
