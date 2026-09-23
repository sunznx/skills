# Onboarding Task Progress — Where A New Hire Stands (Infographic)

**Best for**: a welcome page that shows a new hire which setup tasks are finished
**Avoid when**: the checklist has dependencies that must be explained (use a sequence)
**Answers**: how far through onboarding someone is, at a glance

```infographic
infographic list-row-circular-progress
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
  title Week One Setup — Alex
  desc Progress as of Friday morning
  lists
    - label Accounts and SSO
      desc Complete
    - label Development environment
      desc Complete
    - label First pull request
      desc In review
    - label Team introductions
      desc Scheduled
    - label Product deep dive
      desc Not started
```

## Data Shape

`lists` where each item is one task and `desc` carries the status word. The structure draws progress
rings, so keep statuses to a small vocabulary (Complete / In review / Scheduled / Not started).

## Key Options

| Option | Effect |
|---|---|
| `infographic list-row-circular-progress` | Row layout with progress rings per item |
| `list-grid-circular-progress` | Grid variant; better for long task names |
| `list-grid-done-list` | Pure check-list look when progress percentages are meaningless |

## Pitfalls

- ❌ Numeric percentages invented per task → ✅ use status words unless a real percentage exists
- ❌ Twenty tasks → ✅ show the current week; the rest belongs in the HR system
- ❌ Using it for team-wide tracking → ✅ this is a personal view, one box per new hire

## Alternatives

| Variant | Use instead |
|---|---|
| Company-wide goal progress | `sustainability-goals-progress.md` |
| Onboarding as a journey with stages | `customer-onboarding-journey.md` |
| Task list grouped by owner | `onboarding-milestone-grid.md` |

<!-- source: AntV Infographic syntax docs + template list (`list-row-circular-progress`) -->
