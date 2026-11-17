# Round input

Use UTF-8 JSON. Start from [the example](../examples/round.json) and adjust it for the current frontier.

| Field | Meaning |
| --- | --- |
| `title` | Nonempty round title. |
| `context` | Optional brief Markdown shared across the entire round, shown before its questions. |
| `questions` | At least one question. |
| `questions[].id` | Unique, stable, nonempty ID for matching answers. |
| `question` | A direct, single-line decision question, displayed as the card heading. Put longer background in its `context`. |
| `questions[].context` | All supporting content for this decision, displayed after its options in the supplied order. |
| `type` | `single` (default), `multi`, or `text`. |
| `options` | Two to six single/multiple-choice options, each with a unique `id` and single-line `label`; omit for text. |
| `recommended` | Recommended option IDs: exactly one for single choice, any valid subset for multiple choice; omit for text. |
| `allowSkip` | Optional boolean enabling explicit deferral. |

Single and multiple choice also accept free text without a selection. The agent determines whether that text resolves the decision. Untouched recommendations are not submitted.

For example, ask `调整目录后，是否接受现有 Go SDK 使用者修改 import？` with choices `保留现有 import，使用者无需修改` and `统一新路径，使用者需要修改`.
Explain the recommendation and any unchanged HTTP/JSON behavior in that question's `context`. Keep the question understandable before the reader reaches that background.

The tool renders through the existing `answer-me-with-html` CLI. The UI adapter supports the native option labels in both the flat am 0.5.11 layout and the card-wrapped am 0.6.1 layout. Choices belong to their nearest question fieldset; nested demo fields remain independent. Incompatible panel/option markup produces a visible error instead of inventing answer mappings.

## Content ownership and preview

Choose an owner for every supporting item before rendering. Material about one decision belongs in that question's `context`, regardless of whether it is text, a recommendation, sources, an image, a diagram, a demo, or an interface example. Only shared round information belongs in the top-level `context`; placing a question-specific item there intentionally renders it before the questions. The tool cannot determine a different owner from its meaning.

Within each question, the tool renders its heading, answer choices when present, and context. Context keeps its authored order. Use level-three or deeper headings for supporting sections. Level-two headings outside code fences create additional renderer panels and violate the one-panel-per-question contract. Put literal protocol or code samples in code fences so their headings, tags, and controls remain examples.

Use the renderer's supported Markdown, image, diagram, SVG, or HTML forms. A placeholder or static figure alone does not create an interactive demo. With `--renderer`, a caller may embed its own prepared demo; preserve the owning question panel, the order of question panels, and the native answer markup. Keep demo IDs distinct. Demo inputs, nested cards, and comments remain supporting content, separate from submitted answers.

Before publishing rich content, inspect the rendered page: each item's nearest top-level question panel must be its intended owner, and the displayed order must match the input. Exercise demo controls and submit test answers when changing an adapter; only the actual answer controls may affect question IDs, selections, or answer text. A page-layout check cannot decide whether the author's chosen owner is semantically correct.

An active wait snapshots its page and UI assets at startup. Shared adapter changes apply to newly started waits; they do not relocate content in a running or saved round. Preserve existing inputs and answers, and use a new round directory for changed content.

## Round files

- `request.json`: input and hash, checked on reopening.
- `questions.md` and `page.html`: rendering source and output.
- `draft.json`: the last acknowledged draft.
- `answers.json`: final submission or cancellation; saved before returning.
- `browser.json`: managed driver, space/page identity, and exact round URL.
- `.waiting`: process lock, released on normal exit and signals; stale locks from exited owners may be recovered.

A saved draft can be restored after interruption. Closing the page attempts a final save, which may fail if the command or network has already stopped. Only an acknowledged save is confirmed durable.

Every answer contains `questionId`, `picked`, `text`, and `skipped`. Submissions also contain `submissionId`; both page and submission are bound to `requestHash`.

The default wait is 1800 seconds; `--timeout` accepts a positive value up to one day, subject to host tool limits. `--no-open` prints the URL for external control and provides no automatic tab closure. With the managed opener, successful submission closes the round page unless `--keep-open` was specified. Cleanup outcomes are emitted before the unchanged final answer result. The server listens only on loopback; it is not remote hosting.
