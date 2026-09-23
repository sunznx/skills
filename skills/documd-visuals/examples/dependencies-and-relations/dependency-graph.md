# Module Dependency Graph (DOT)

**Best for**: showing who depends on whom across modules, packages or services — and where the cycles are
**Avoid when**: you need data flow or call ordering (use a sequence diagram) or an architecture overview with icons
**Answers**: the dependency direction, the layering, and any accidental cycles

```dot
digraph deps {
  node [style=filled fillcolor="#eef2fb" color="#5b6b8c" fontcolor="#1f2937"]
  edge [color="#5b6b8c" fontcolor="#676f7e"]
  rankdir=LR;
  node [shape=box, style=rounded, fontname="Helvetica"];
  edge [arrowsize=0.7];

  subgraph cluster_app {
    label="application";
    style=rounded;
    "checkout-api"; "admin-api";
  }

  subgraph cluster_domain {
    label="domain";
    style=rounded;
    "orders"; "payments"; "inventory";
  }

  subgraph cluster_infra {
    label="infrastructure";
    style=rounded;
    "db"; "queue"; "cache";
  }

  // application may depend on domain, domain may depend on infrastructure —
  // the reverse edges below are the ones worth reviewing
  "checkout-api" -> "orders";
  "checkout-api" -> "payments";
  "admin-api" -> "orders";
  "admin-api" -> "inventory";

  "orders" -> "db";
  "orders" -> "queue";
  "payments" -> "queue";
  "inventory" -> "db";
  "inventory" -> "cache";

  // cycle: orders -> inventory -> orders (marked so reviewers see it immediately)
  "orders" -> "inventory" [color="#d1242f", penwidth=2, label="cycle"];

  // infrastructure reaching back into domain code is an architecture smell
  "queue" -> "orders" [style=dashed, color="#d1242f", label="callback"];
}
```

## Key Options

| Syntax | Effect |
|---|---|
| `digraph name { … }` | Directed graph — dependencies have a direction; use `graph` only for undirected relations |
| `rankdir=LR` | Left-to-right layering; use `TB` for dependency trees that read top-down |
| `subgraph cluster_<name> { … }` | **Cluster name must start with `cluster_`**, otherwise no box is drawn |
| `subgraph cluster_x { label="…"; style=rounded; }` | Cluster label and border style |
| `[color=…, penwidth=2]` | Highlight the problem edges (cycles, back-references) instead of colouring everything |
| `[style=dashed]` | Asynchronous or callback edges |

## Data Shape

A **layered digraph**: consumers on the left (or top), infrastructure on the right (or bottom). Every edge that
points "backwards" against the layering is a design finding — colour those, not the normal ones.

## Pitfalls

- ❌ `subgraph backend { }` without the `cluster_` prefix → ✅ no box is drawn; rename to `cluster_backend`
- ❌ Missing semicolons after statements → ✅ DOT tolerates some omissions, but stick to `;` for predictable output
- ❌ Colouring every node → ✅ colour only anomalies; a rainbow graph hides the finding you want to communicate
- ❌ Drawing one giant graph → ✅ split by concern if the label count exceeds ~40 nodes

## Alternatives

| Variant | Use instead |
|---|---|
| Runtime call ordering | A sequence diagram (`api-interaction-sequence.md`) |
| Physical/network relations | `network-topology-enterprise.md` |
| Unstructured relationship networks | `relationship-network-neato.md` (force-directed) |

<!-- source: Graphviz DOT attribute reference + dot gallery (directed graphs: bazel, go-package, ninja) -->
