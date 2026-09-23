# Relationship Network (DOT, force-directed layout)

**Best for**: unstructured relations — service mesh dependencies, knowledge/entity graphs, correlational groupings
**Avoid when**: the relations are hierarchical or layered (use the default `dot` layout)
**Answers**: which nodes cluster together, which are central, and which are isolated

```dot
graph mesh {
  node [style=filled fillcolor="#eef2fb" color="#5b6b8c" fontcolor="#1f2937"]
  edge [color="#5b6b8c" fontcolor="#676f7e"]
  layout=neato;          // force-directed: position carries meaning (clusters emerge)
  overlap=false;         // let Graphviz remove node overlaps
  splines=true;
  sep="+8";
  node [shape=circle, width=0.6, style=filled, fillcolor="#eef2fb", fontname="Helvetica", fontsize=10];
  edge [penwidth=0.8, len=1.4];

  // Teams that talk to each other cluster together
  "checkout" -- "payments" [weight=3];
  "checkout" -- "inventory" [weight=3];
  "checkout" -- "identity" [weight=2];
  "payments" -- "ledger" [weight=4];
  "payments" -- "fraud" [weight=3];
  "fraud" -- "ledger" [weight=2];
  "inventory" -- "warehouse" [weight=3];
  "warehouse" -- "logistics" [weight=3];
  "identity" -- "directory" [weight=4];
  "identity" -- "support" [weight=1];
  "support" -- "orders-ui" [weight=2];
  "orders-ui" -- "checkout" [weight=3];
  "analytics" -- "ledger" [weight=1];
  "analytics" -- "warehouse" [weight=1];

  // deliberately isolated: no strong ties — visible as an outlier in a force layout
  "legacy-billing" [fillcolor="#dfe5fb"];
}
```

## Key Options

| Syntax | Effect |
|---|---|
| `layout=neato` | Force-directed layout (stress majorization); `fdp`/`sfdp` are related engines for larger graphs |
| `overlap=false` | Removes node overlaps — required for readable force layouts |
| `splines=true` | Curved edges that avoid nodes; with `splines=line` edges are straight segments |
| `weight=N` | Higher weight pulls nodes closer and straightens the edge — use it to express *strength*, not just existence |
| `len=…` | Preferred edge length (neato/fdp) — express "these should be far apart" |
| `sep="+8"` | Minimum separation between node boundaries (additive form) |
| `graph ... _` | `graph` instead of `digraph`: relations here are symmetric; use `digraph` only when direction matters |

## Data Shape

Nodes + weighted undirected edges. In a force layout, **distance is the message**: clusters, hubs and outliers
become visible without any explicit grouping.

## Pitfalls

- ❌ Expecting a deterministic layout → ✅ force layouts are seed-dependent; keep `start=` unset for reproducibility across runs of the same version, and do not hand-tune positions
- ❌ Heavy graphs with no `weight` → ✅ every edge looks equal and no cluster appears; weight the strong ties
- ❌ Reading direction into edges → ✅ use `graph`/`--` when relations are symmetric, otherwise readers assume a flow
- ❌ Using neato for hierarchical data → ✅ layers and ranks are the `dot` engine's job; switching layout is one line (`layout=dot`)

## Alternatives

| Variant | Use instead |
|---|---|
| Hierarchical dependencies | `dependency-graph.md` (`digraph`, default dot layout) |
| Hub-and-spoke centre | `radial-hub-network.md` (`layout=twopi`) |
| Graph with role-based icons | plantuml examples (network/cloud icon families) |

<!-- source: Graphviz layouts (neato/fdp/sfdp) and attributes overlap/sep/weight/len; layout selection verified with @viz-js/viz 3.29 -->
