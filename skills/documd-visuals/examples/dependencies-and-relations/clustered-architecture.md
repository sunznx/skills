# Clustered Architecture with Cluster-to-Cluster Edges (DOT)

**Best for**: architecture overviews where edges should connect *groups* rather than individual boxes
**Avoid when**: the reader needs service icons (use a PlantUML cloud/network example)
**Answers**: how bounded contexts or planes relate, without drawing every internal edge

```dot
digraph arch {
  node [style=filled fillcolor="#eef2fb" color="#5b6b8c" fontcolor="#1f2937"]
  edge [color="#5b6b8c" fontcolor="#676f7e"]
  compound=true;              // required for lhead/ltail (cluster-to-cluster edges)
  rankdir=TB;
  graph [fontname="Helvetica", nodesep=0.5, ranksep=0.8];
  node [shape=box, style="rounded,filled", fillcolor="#eef2fb", fontname="Helvetica"];
  edge [arrowsize=0.7, fontname="Helvetica", fontsize=10];

  subgraph cluster_edge {
    label="Edge plane";
    style="rounded,filled"; fillcolor="#dfe5fb";
    "CDN"; "WAF"; "API Gateway";
  }

  subgraph cluster_core {
    label="Core services";
    style="rounded,filled"; fillcolor="#676f7e";
    "Identity"; "Orders"; "Payments"; "Inventory";
  }

  subgraph cluster_data {
    label="Data plane";
    style="rounded,filled"; fillcolor="#6b7280";
    "Orders DB"; "Event Stream"; "Search Index";
  }

  subgraph cluster_ops {
    label="Ops";
    style="rounded,filled"; fillcolor="#5b6b8c";
    "Metrics"; "Logs"; "Secrets";
  }

  // internal edges (kept minimal on purpose)
  "CDN" -> "WAF" -> "API Gateway";
  "Identity" -> "Orders";
  "Orders" -> "Payments";
  "Payments" -> "Orders DB";
  "Orders" -> "Event Stream";
  "Inventory" -> "Search Index";
  "Secrets" -> "Payments";

  // plane-to-plane edges: clipped to the cluster boundary via ltail/lhead
  "API Gateway" -> "Orders" [ltail=cluster_edge, lhead=cluster_core, label="authenticated traffic"];
  "Orders"       -> "Event Stream" [ltail=cluster_core, lhead=cluster_data, label="domain events"];
  "Payments"     -> "Metrics" [ltail=cluster_core, lhead=cluster_ops, style=dashed, label="telemetry"];
  "Identity"     -> "Secrets" [ltail=cluster_core, lhead=cluster_ops, style=dashed, label="credentials"];
}
```

## Key Options

| Syntax | Effect |
|---|---|
| `compound=true` | **Required** before `lhead` / `ltail` have any effect |
| `ltail=cluster_x` / `lhead=cluster_y` | Clips the edge to the cluster boundary — the edge then reads as "plane to plane" |
| `subgraph cluster_* { style="rounded,filled"; fillcolor=… }` | Filled cluster boxes; colour by plane, not by node |
| `nodesep` / `ranksep` | Spacing between nodes in a rank / between ranks — the two knobs that fix cramped layouts |
| `graph [fontname=…]` plus per-object fonts | Keep fonts consistent across graph, nodes and edges |

## Data Shape

Clusters = **planes or bounded contexts**; internal edges = the few relationships worth showing inside a plane;
`lhead`/`ltail` edges = the cross-plane contract. Reader question: "what are the planes and how do they talk".

## Pitfalls

- ❌ Using `lhead`/`ltail` without `compound=true` → ✅ they are silently ignored; the edge will attach to the node
- ❌ Drawing every internal call → ✅ show the 1–3 edges per plane that define the plane's role
- ❌ Cross-plane edges landed on a random node → ✅ use `ltail`/`lhead` so the edge speaks about the group
- ❌ Different fill for every cluster with no meaning → ✅ three planes maximum in practice; colour *is* the grouping

## Alternatives

| Variant | Use instead |
|---|---|
| Vendor icons for cloud services | `aws-serverless-architecture.md` (plantuml + awslib or mxgraph icons) |
| Deployment/zone topology | `runtime-deployment-topology.md` |
| Dependency direction analysis | `dependency-graph.md` |

<!-- source: Graphviz `compound` + `lhead`/`ltail` attributes (dot only), verified with @viz-js/viz (Graphviz 15.1.1) -->
