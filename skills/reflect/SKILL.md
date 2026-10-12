---
name: reflect
description: Spawn three parallel review subagents over this session, surface learnings, and route each to a concrete edit on an existing skill. Use when the user says reflect.
disable-model-invocation: true
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

## When to invoke

Invoke when the user says "reflect" or "/reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## Process

### 1. Write the session digest

Reviewers work from a digest of this conversation, written from your own context: the user's requests and corrections (quoted verbatim), the skills you loaded, the commands that failed or were retried, and the moments the user handed you context you could have fetched yourself. If the host names a transcript file for this session, pass that path too.

### 2. Spawn three reviewers in parallel

Spawn the three reviewers as subagents in a single message. If the host cannot spawn subagents, run each lens yourself in order.

| Lens | Prompt template |
|---|---|
| Judgment | `references/judgment-reviewer.md` |
| Tooling | `references/tooling-reviewer.md` |
| Divergent | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the digest (and transcript path, if any) where marked.

### 3. Synthesize

Spawn one synthesizer subagent with `references/synthesizer.md` verbatim, each reviewer's full output inlined where marked. The synthesizer returns a structured Accepted / Rejected / Backlog list.

### 4. Structural enforcement check

Sanity-check the synthesizer's Accepted list. For any item that would be enforced more reliably by a lint rule, script, metadata flag, or runtime check, move it from Accepted to Backlog. Rank enforcement by the levels in [`../correct/SKILL.md`](../correct/SKILL.md).

### 5. Apply

Before applying any Accepted edit, present the synthesizer's full Accepted/Rejected/Backlog output to the user and wait for explicit approval. The user picks which subset to apply and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

Backlog items wait for the user too: file each one where the user says, or leave it in the summary.

For each approved Accepted item, follow the Routing field exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): parent does directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): hand to the host's skill-creation skill (for example `skill-creator`), follow **writing-for-agents**, and run its draft / test / iterate loop.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): hand to the skill-creation skill and run its description-optimization loop.
- `new skill: <kebab-name>`: hand creation to the skill-creation skill so the new skill takes its standard shape.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done. Skip this step if it doesn't.

### 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog: `<title>`, with where it was filed or `unfiled`. One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.
