# Data Structure / Table Nodes (DOT, HTML-like labels)

**Best for**: showing structure *inside* nodes — records, structs, memory layouts, request/response schemas
**Avoid when**: plain boxes are enough (use a dependency graph) or you need an ER diagram with cardinalities
**Answers**: what each node contains, field by field, and where the links attach

```dot
digraph structs {
  node [style=filled fillcolor="#eef2fb" color="#5b6b8c" fontcolor="#1f2937"]
  edge [color="#5b6b8c" fontcolor="#676f7e"]
  rankdir=LR;
  node [shape=plaintext, fontname="Helvetica", fontsize=11];

  // HTML-like label: the label is a table, so the node size is driven by the content
  header [label=<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" BGCOLOR="#ffffff" COLOR="#2b66c4">
      <TR><TD BGCOLOR="#eef2fb"><B>TCP Header</B></TD></TR>
      <TR><TD PORT="src">src port</TD></TR>
      <TR><TD PORT="dst">dst port</TD></TR>
      <TR><TD PORT="seq">sequence number</TD></TR>
      <TR><TD PORT="ack">acknowledgment</TD></TR>
      <TR><TD PORT="flags">flags (9 bits)</TD></TR>
    </TABLE>>
  ];

  payload [label=<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" BGCOLOR="#ffffff" COLOR="#0f9b9b">
      <TR><TD BGCOLOR="#dfe5fb"><B>Payload</B></TD></TR>
      <TR><TD>application data</TD></TR>
      <TR><TD>length: variable</TD></TR>
    </TABLE>>
  ];

  connections [label=<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" BGCOLOR="#ffffff" COLOR="#7048e8">
      <TR>
        <TD ROWSPAN="2" BGCOLOR="#6b7280">Connection<br/>state</TD>
        <TD PORT="established">ESTABLISHED</TD>
      </TR>
      <TR>
        <TD>TIME_WAIT</TD>
      </TR>
    </TABLE>>
  ];

  // ports let an edge attach to a specific cell instead of the node centre
  header:flags -> connections:established [label="after handshake", fontsize=10];
  header:seq -> payload [label="carries", fontsize=10];
}
```

## Key Options

| Syntax | Effect |
|---|---|
| `label=< … >` | **HTML-like label** (angle brackets, not quotes) — the label is parsed as a mini-HTML table |
| `shape=plaintext` / `shape=plain` | `plain` = `none` + `width=0 height=0 margin=0`, so the node is exactly the table |
| `<TABLE BORDER CELLBORDER CELLSPACING CELLPADDING>` | Table borders, cell borders, spacing and padding — the same names as HTML |
| `<TD BGCOLOR="…" ALIGN="…" VALIGN="…" COLSPAN="…" ROWSPAN="…">` | Per-cell styling and spanning |
| `<TD PORT="name">` + `node:port -> …` | Connect an edge to a specific cell |
| `<B> <I> <U> <BR/> <FONT POINT-SIZE="…">` | Inline formatting (available with the SVG renderer) |

## Data Shape

Each node is a small table; edges attach to **ports**. This is the only way in DOT to express "field-level" or
"cell-level" connections — which is why it is worth the verbosity.

## Pitfalls

- ❌ Quoting the label (`label="<TABLE>…"`) → ✅ HTML labels need `label=< … >` without quotes
- ❌ Raw `&`, `<`, `>` inside cell text → ✅ escape as `&amp;`, `&lt;`, `&gt;`
- ❌ Wrapping the table in `<FONT>`/`<B>` with a leading space → ✅ that is a documented syntax error
- ❌ Forgetting `margin=0` → ✅ with `shape=plain`, edges stop being clipped to an invisible box

## Alternatives

| Variant | Use instead |
|---|---|
| Plain boxes and arrows | `dependency-graph.md` |
| Record syntax shorthand | `shape=record label="<f0>a|<f1>b"` (simpler, fewer styling options) |
| Entity relationships with cardinality | `entity-relationships-crows-foot.md` (plantuml IE) |

<!-- source: Graphviz node shapes documentation (record-based and HTML-like labels), verified with @viz-js/viz 3.29 (Graphviz 15.1.1) -->
