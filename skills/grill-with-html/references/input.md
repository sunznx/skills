# Round input

Use UTF-8 JSON. Start from [the example](../examples/round.json) and adjust it for the current frontier.

| Field | Meaning |
| --- | --- |
| `title` | Nonempty round title. |
| `context` | Optional Markdown context. Reserve level-two headings for question panels; use level three or deeper in context. |
| `questions` | At least one question. |
| `questions[].id` | Unique, stable, nonempty ID for matching answers. |
| `question` | Nonempty question on one line; put longer background in its `context`. |
| `type` | `single` (default), `multi`, or `text`. |
| `options` | Two to six single/multiple-choice options, each with a unique `id` and single-line `label`; omit for text. |
| `recommended` | Recommended option IDs: exactly one for single choice, any valid subset for multiple choice; omit for text. |
| `allowSkip` | Optional boolean enabling explicit deferral. |

Single and multiple choice also accept free text without a selection. The agent determines whether that text resolves the decision. Untouched recommendations are not submitted.

The tool renders through the existing `answer-me-with-html` CLI. The current UI adapter was verified against am 0.5.11; incompatible panel/option markup produces a visible error instead of inventing answer mappings.

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
