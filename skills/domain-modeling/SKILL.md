---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a GLOSSARY.md, or recording or editing an ADR.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline: challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `GLOSSARY.md` for vocabulary is not this skill: that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

Domain documents are project knowledge, so this skill needs no plan of its own. Before reading Matt configuration, follow [shared configuration initialization](../setup-matt-pocock-skills/references/ensure-config.md). Read `.planning/domain.md` and use the [glossary selection rules](../setup-matt-pocock-skills/domain.md#glossary-selection) when the project has no explicit glossary policy. Unless the project configuration or calling skill specifies another ADR directory, use `.planning/adr/` at the project root, shared across tasks. Record paths to changed glossaries and ADRs in the selected plan, if any.

## File structure

Most repos have a single context:

```
/
├── GLOSSARY.md
├── .planning/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `GLOSSARY-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── GLOSSARY-MAP.md
├── .planning/
│   └── adr/
│       ├── 0001-system-decision.md  ← system-wide decisions
│       ├── ordering/                ← context-specific decisions
│       └── billing/
└── src/
    ├── ordering/
    │   └── GLOSSARY.md
    └── billing/
        └── GLOSSARY.md
```

Create files lazily. When the first term is resolved, use the selected glossary; create one only if no glossary exists for that context. Create the ADR directory only when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user's wording conflicts with the selected glossary, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

### Update the selected glossary inline

When a term is resolved, update the selected glossary on the spot. Use [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md) for either filename.

Keep implementation details and decisions out of the glossary.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).
