---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask up to three frontier questions per round, starting with those that unblock the most decisions. Keep the rest pending. Number each question and give your recommended answer, then wait for the user's answers.

## Human-readable questions

Write for the person answering, using their language and familiar terms.

- Start with a concrete situation: what the person would see or do,
  and what changes depending on their choice.
- Ask for one decision per question. Give each independent choice
  its own question.
- Use everyday words. When a technical term is necessary, explain
  it briefly where it first appears.
- Include enough context to answer without reopening code, plans,
  or earlier messages. Keep that context to one or two short sentences.
- For a bounded decision, offer two or three distinct options and
  describe each option's practical consequence. Leave room for a
  different answer. Use an open question when the possible answers
  are not yet understood.
- Recommend one option and explain why it fits the user's stated
  goal. Make any assumption behind the recommendation explicit.

Format a round like so:

```
❓ **Q1 — <short title in everyday language>**

<Concrete situation and the single decision to make.>

A. <Option and its practical consequence>
B. <Option and its practical consequence>

➡️ 推荐 A：<reason tied to the user's goal>.

---

<Next independent question, if needed.>
```

Let the user reply briefly, such as “Q1 A，Q2 B”, or explain their
own preference. For a specific question, “yes” accepts the
recommended answer.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent with a fresh context window to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask other ready questions within the round's limit. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

## Plan and artifacts

Before the first round, use `planning-with-files` to select or create this task's plan as `<PLAN_DIR>`; when another workflow (such as `grill-with-docs`) invokes this skill, use that workflow's selected plan. After each round, append every decision the user settled, with their answer and the branch it unblocks, to the selected plan's `findings.md`, and log the round in `progress.md`. When the user confirms the shared understanding, record it in `findings.md` too. Recording is not acting on it.
