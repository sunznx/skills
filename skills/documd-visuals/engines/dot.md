# dot

> Graphviz layout engine — ranked, force-directed, circular and radial arrangements.
> Runtime: `@viz-js/viz` 3.29 (WASM, bundles Graphviz 15.1.1).

## Scope

- **Automatic layout for relationship graphs**: dependency, call graph, impact analysis, hierarchy, causal
  tree, state machine, org tree, family tree.
- **Table-shaped nodes** via HTML-like labels — the recommended way to put structured data in a node.
- **Eight layout engines selectable from inside the source** with the `layout` attribute (verified: all eight
  produce different coordinates). `nop` is excluded because it does no layout.

| Want | `layout=` |
|---|---|
| Layered / ranked (default) | `dot` |
| Force-directed, organic | `neato` · `fdp` |
| Large graphs | `sfdp` |
| Circular | `circo` |
| Radial (spokes from a centre) | `twopi` |
| Cluster packing | `osage` |
| Treemap-style tiling | `patchwork` |

## Fit

- Choose `dot` when the graph **has no icons** and the layout should be computed: rank order, edge routing,
  cluster containment.
- Choose PlantUML when you need brand/device icons, UML semantics, or a fixed canvas.
- `dot` beats PlantUML for causality chains, dependency trees and anything where `rankdir` + `constraint`
  control the reading order.

## Useful attributes (~30 of ~130)

| Group | Attributes |
|---|---|
| Layout | `layout` · `rankdir` (TB/BT/LR/RL) · `ranksep` · `nodesep` · `minlen` · `weight` |
| Rank control | `rank=same\|min\|source\|max\|sink` (in a subgraph) · `constraint=false` (draw a back edge) · `newrank` |
| Clusters | `subgraph cluster_*` · `clusterrank` · `compound` + `lhead`/`ltail` · `pencolor` · `bgcolor` · `style=filled` |
| Node shape | `shape` · `fixedsize` · `width` · `height` · `margin` · `peripheries` |
| Style | `style` (8 node values: `filled` `invisible` `rounded` `dashed` `dotted` `solid` `bold` `diagonals`) · `penwidth` · `color` · `fillcolor` · `fontcolor` · `fontsize` |
| Edges | `dir` · `arrowhead` · `arrowtail` · `headlabel` · `taillabel` · `xlabel` · `headport`/`tailport` · `splines` · `radius` · `concentrate` |
| Text | escString `\N` `\E` `\G` · `\n` `\l` `\r` line breaks · UTF-8 and emoji |

### Shapes worth knowing

- Polygon family: `box` `ellipse` `circle` `diamond` `cylinder` (storage) `note` `folder` `box3d`
  `component` `house` `hexagon` `parallelogram` `trapezium` `doublecircle` `point`.
- `plain` / `plaintext` — no outline, no margin: **the standard partner for HTML-like labels**.
- `record` / `Mrecord` — field syntax `label="<f0> a|<f1> b"`. Officially superseded by HTML-like labels;
  use it only for simple field lists.
- **HTML-like labels** — `label=<…>` with `<TABLE>`, `<TR>`, `<TD>`, `<B>`, `<FONT>`, `<HR/>`, plus cell
  attributes (`COLSPAN`, `BGCOLOR`, `CELLBORDER`, `PORT`, `ALIGN`, `ROUNDED`). Fully available under the SVG
  renderer.

## Styling

Colour comes from the chosen theme — pick one in [`../styles/palette.md`](../styles/palette.md), then
copy that theme's attribute block (for example
[`../styles/themes/default.md`](../styles/themes/default.md)). Graphviz gives no help
here: its default output carries no fill at all and strokes in the keyword `black`, so an unstyled
graph reads as "not part of the set".

- `node [style=filled fillcolor=… color=… fontcolor=…]` once at the top, `edge [color=…]` beside it.
- `fillcolor` is ignored unless `style=filled` is in effect — the block sets it; a per-node
  override relies on it.
- Categories: one override statement per category (`B [fillcolor=… color=…]`) using the palette's
  `tint-*` / `shade-*` pair. Never a raw colour per node.
- Never set `bgcolor` (the graph stays transparent) and never set fonts.

## Constraints

- **No external resources**: `image=`, `shapefile=`, `<IMG SRC>` only accept local paths — not usable on an
  offline export path. For icons, use PlantUML stencils.
- Custom (PostScript / bitmap) node shapes: not supported here.
- The renderer forces a transparent background and injects default font/line colours for dark themes; those
  are **prefixed** to your source, so properties you write explicitly still win.
- Interactive attributes (`URL`, `tooltip`, `target`) only matter in SVG output; treat them as decorative.
- `~130` attributes exist — the rest are physics parameters for `neato`/`fdp`/`sfdp` or write-only/debug
  attributes. Look them up in `attrs.html` when needed rather than memorising.

## Anti-patterns

| ❌ Don't | ✅ Do |
|---|---|
| Icons via `image=` | PlantUML stencils |
| Drawing a UML class diagram by hand in `dot` | PlantUML `class` — it knows UML semantics |
| Leaving the layout engine implicit for non-layered graphs | Set `layout=` explicitly inside the source |
| Long unstructured labels | HTML-like `<TABLE>` labels for any node with more than two facts |
| `record` shapes with ports on the same rank | HTML-like labels; record ports have known issues |
| Dozens of leaf nodes with no clusters | Wrap related nodes in `subgraph cluster_*` and label the cluster |

## Sources

- Coverage ledger — layouts, attributes, shapes and gallery scenarios, kept or excluded with a reason:
  [`coverage/dot.md`](coverage/dot.md)
- Attributes: <https://graphviz.org/doc/info/attrs.html> · Shapes: <https://graphviz.org/doc/info/shapes.html>
- Arrows: <https://graphviz.org/doc/info/arrows.html> · Language: <https://graphviz.org/doc/info/lang.html>
- Layouts: <https://graphviz.org/docs/layouts/> · Gallery: <https://graphviz.org/gallery/>
- Implemented boundary: `src/renderers/dot-renderer.ts` (background/theme injection only)
