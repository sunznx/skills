# Sustainability Goals Progress — Commitments With Rings (Infographic)

**Best for**: a public or internal page showing progress against sustainability commitments
**Avoid when**: commitments are measured in different units that need a table
**Answers**: each goal, its target year, and how far the organisation has moved

```infographic
infographic list-grid-circular-progress
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
  title Climate Commitments
  desc Progress against 2030 targets
  lists
    - label Renewable electricity
      desc 92% of target
    - label Fleet electrification
      desc 48% of target
    - label Water intensity
      desc 74% of target
    - label Supplier disclosure
      desc 31% of target
```

## Data Shape

`lists` where `desc` states progress as a share of the target, not an absolute number. The ring visualises the
share, so the label should name the *goal*, not the metric.

## Key Options

| Option | Effect |
|---|---|
| `infographic list-grid-circular-progress` | Rings with labels beneath — reads as a scoreboard |
| `list-grid-progress-card` | Bar form; easier when values differ in magnitude |
| `list-grid-badge-card` | Drop the ring and keep the text if progress is qualitative |

## Pitfalls

- ❌ Baseline missing → ✅ "% of target" means nothing without the baseline year; state it in the title
- ❌ Overstating progress → ✅ disclose method in the surrounding text, not the diagram
- ❌ Eight commitments → ✅ pick the ones with governance; the rest are marketing claims

## Alternatives

| Variant | Use instead |
|---|---|
| Goal progress inside one team | `onboarding-task-progress.md` |
| Adoption trend over time | `feature-adoption-trend.md` |
| Company-wide metric board | `leadership-metric-board.md` |

<!-- source: AntV Infographic syntax docs + template list (`list-grid-circular-progress`) -->
