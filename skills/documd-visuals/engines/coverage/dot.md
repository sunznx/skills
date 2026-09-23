# dot coverage ledger

> Generated from `catalog/scenarios.json` plus the curated unit table for this engine.
> Runtime: `@viz-js/viz` 3.30.0 (WASM, bundles Graphviz). Last generated: 2026-09-22.

**Units** record what this engine does with each unit of its official documentation — kept, or
excluded with the reason. **Examples by goal** is collected from the catalog, so every link below is
resolvable from this file.

## Layout engines (9 available, 8 usable)

| `layout=` | Disposition | Use for |
|---|---|---|
| `dot` (default) | kept | ranked / layered graphs, the default reading |
| `neato` | kept | force-directed; `dependencies-and-relations/relationship-network-neato.md` |
| `fdp` | kept | force-directed, larger graphs |
| `sfdp` | kept | large graphs |
| `circo` | kept | circular arrangements |
| `twopi` | kept | radial networks; `network-topology/radial-hub-network.md` |
| `osage` | kept | cluster packing |
| `patchwork` | kept | treemap-style tiling |
| `nop` | excluded | does no layout at all |

> Verified: the `layout` attribute is read from the source and **takes precedence** over any engine
> parameter; all eight engines produce different coordinates for the same input.

## Attributes (~130 official → ~30 documented)

| Group | Kept | Excluded |
|---|---|---|
| Layout | `layout` `rankdir` `ranksep` `nodesep` `minlen` `weight` | — |
| Rank control | `rank` (in subgraph) `constraint` `newrank` | `TBbalance` (niche) |
| Clusters | `subgraph cluster_*` `clusterrank` `compound` + `lhead`/`ltail` `pencolor` `bgcolor` `style=filled` | — |
| Node geometry | `shape` `fixedsize` `width` `height` `margin` `peripheries` | `regular` `orientation` `sides` `skew` `distortion` (query attrs.html when needed) |
| Style | all 8 node `style` values · `penwidth` `color` `fillcolor` `fontcolor` `fontsize` `colorscheme` | `bgcolor="a:b"` gradients (kept out of examples — theme-dependent) |
| Edges | `dir` `arrowhead` `arrowtail` `headlabel` `taillabel` `xlabel` `headport`/`tailport` `splines` `radius` `concentrate` | `samehead` (unverified) |
| Text | escString `\N` `\E` `\G` · `\n` `\l` `\r` · UTF-8 and emoji | `charset` (UTF-8 is the default) |
| Export | `class` `stylesheet` `id` `href` `tooltip` | kept as T2 — only meaningful in SVG output |
| Physics | — | `overlap` `sep` `mode` `model` `Damping` `maxiter` `start` `root` `mindist` `oneblock` `repulsiveforce` — only apply to `neato`/`fdp`/`sfdp`; look them up instead of memorising |

## Node shapes

| Group | Disposition |
|---|---|
| Polygons (~60) | kept: `box` `rect` `square` `ellipse` `circle` `point` `diamond` `trapezium` `parallelogram` `house` `hexagon` `cylinder` `note` `tab` `folder` `box3d` `component` `doublecircle` `Mdiamond` `Mcircle` `star` `underline` `plaintext` `plain` `none` |
| `record` / `Mrecord` | kept for simple field lists — officially superseded by HTML-like labels, and adjacent same-rank records have known port issues |
| **HTML-like labels** | **kept — the recommended route** for any structured node: `<TABLE>` `<TR>` `<TD>` `<FONT>` `<B>` `<HR/>`, cell `BGCOLOR` `COLSPAN` `PORT` `ALIGN` `CELLBORDER` `ROUNDED`. Works under the SVG renderer. `planning-and-roadmap/work-breakdown-structure.md` |
| Molecular-biology shapes (20) | excluded — no applicable scenario |
| User-defined PostScript / bitmap shapes | excluded — needs local files, unavailable offline |

## Gallery scenarios (~45 official)

| Kept as examples | Reference only (no example) |
|---|---|
| git-style branch graph, build dependency, cluster grouping, family tree, finite state machine, data structures / parse tree, ER model, network device relations, radial network, clustered architecture | SDH network map, Linux kernel map, pprof CPU profile, neural network, world dynamics, philosophers, transparency — too domain-specific or too large to be a useful template |

## Implementation boundaries

| Item | Fact |
|---|---|
| Background | forced to `transparent` by the renderer |
| Dark theme | font/line colours are injected as **prefixed** defaults — explicit properties in your source still win |
| External resources | `image=`, `shapefile=`, `<IMG SRC>` only accept local paths → unreliable offline; use PlantUML stencils for icons |
| Emoji / UTF-8 labels | verified working |

## Examples by goal

7 examples across 3 goal domains.

### [dependencies-and-relations](../../goals/dependencies-and-relations.md)

| Scenario | Tier | Example |
|---|---|---|
| dependency graph | T2 | [dependency-graph.md](../../examples/dependencies-and-relations/dependency-graph.md)<br>[clustered-architecture.md](../../examples/dependencies-and-relations/clustered-architecture.md) |
| causal tree | T2 | [fishbone-causal-tree.md](../../examples/dependencies-and-relations/fishbone-causal-tree.md) |
| relationship network | T2 | [relationship-network-neato.md](../../examples/dependencies-and-relations/relationship-network-neato.md) |
| tabular nodes | T2 | [table-node-structures.md](../../examples/dependencies-and-relations/table-node-structures.md) |

### [network-topology](../../goals/network-topology.md)

| Scenario | Tier | Example |
|---|---|---|
| radial network | T2 | [radial-hub-network.md](../../examples/network-topology/radial-hub-network.md) |

### [theme-and-tone](../../goals/theme-and-tone.md)

| Scenario | Tier | Example |
|---|---|---|
| print handout graph | T2 | [print-handout-graph.md](../../examples/theme-and-tone/print-handout-graph.md) |

## Counts

| | |
|---|---|
| Examples using this engine | 7 |
| Goal domains reached | 3 |
| Scenarios | 6 |
| T0 scenarios | 0 |

## Sources

- Engine reference: [`../dot.md`](../dot.md)
- Catalog: [`../../catalog/scenarios.md`](../../catalog/scenarios.md)
