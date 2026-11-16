---
name: grill-with-html
description: Ask design questions in HTML rounds and record confirmed domain decisions. Use for "grill me with html", "grilling me html", 网页勾选/填写答案, or browser replies without pasting. The original Codex or Claude Code tool call receives submissions; managed pages close automatically after submission.
---

# Grill with HTML

Use `grilling` for the design tree and round selection, and `domain-modeling` for terminology and necessary ADRs. This entry replaces chat questions with a browser form. Answers return through the original waiting tool call.

## Prepare a round

1. Use `planning-with-files` to select or create this task's plan as `<PLAN_DIR>`; when another workflow invokes this skill, use its selected plan. Keep inputs, pages, drafts, answers, browser receipts, and verification records in `<PLAN_DIR>/grill-with-html/`.
2. Verify facts, then select this round's questions using `grilling`. Defer questions with unresolved prerequisites. Write the input to `grill-with-html/round-01.input.json`; use a new number and directory for each subsequent round.
3. Follow [the input reference](references/input.md) and [example](examples/round.json). Give every question a stable ID. A single-choice question has exactly one recommendation, initially unselected. Accept free text; set `allowSkip` explicitly when deferral is allowed.
4. Put the decision in `question`: one direct question about the user's intended behavior or the consequence they accept. Use that question as the card heading, with choices before supporting context. Write short option labels that answer it directly. Put everything that supports that particular decision in its `questions[].context`: explanations, recommendations, evidence, figures, demos, interface examples, and other material. Reserve the top-level `context` for brief information shared across the round. Preserve the author's order within each question's context; the renderer cannot infer ownership from prose or media type. IDs identify answers in saved data.
5. When using rich content or a custom renderer, follow [content ownership and preview checks](references/input.md#content-ownership-and-preview). Confirm that each item remains inside its owning question, and that demo controls stay separate from answer controls, before opening the round for the user.

## Open and await submission

Requires Node.js 20+ and the installed `answer-me-with-html` renderer. The command locates the renderer in the adjacent skill; use `--renderer` with its actual `scripts/am.mjs` path when installed elsewhere.

Set `ASK_CLI` to this skill's `scripts/ask.mjs`, and set `ROUND_INPUT` and `ROUND_DIR` to the selected round's absolute paths, in the same shell call:

```bash
node "$ASK_CLI" --input "$ROUND_INPUT" --round-dir "$ROUND_DIR" --timeout 540
```

This environment installs the entry at `~/.agents/skills/grill-with-html/scripts/ask.mjs`; Claude links to that copy.

- By default, the command uses the installed `ego-browser` CLI to create and identify its own page, loads it, activates that tab with `Page.bringToFront`, then hands control to the user. On macOS it also foregrounds the existing Ego app without opening another URL. It records the page identity in the round's `browser.json`.
- Inspect `browser_opened` for `warning` or `reason` before reporting that the page opened. An activation failure stops further browser commands, preserves the existing page and answers, and reports the visibility problem. If the user cannot see a live round, use the browser skill to reveal its recorded page under its control rules; keep the original waiting command and page rather than creating another round or tab.
- The default closes the managed page after a successful submission is saved. If the user requests retention, or the page is needed for review or continued interaction, add `--keep-open` before starting the round.
- `--no-open` leaves browser opening and cleanup to the caller. Use it for remote hosts, external browser control, or tests. It does not provide automatic tab cleanup.
- If `ego-browser` is absent, the system opener remains available, but cleanup is reported as `unavailable`. An uncertain managed launch is not retried through another opener. Report the actual limitation rather than promising automatic closure.
- Give the user the `ready.url`. Remote hosts must make that loopback URL reachable from the user's browser; a server-side URL alone does not establish reachability.
- Keep the current tool call running. When Codex returns a process session ID, wait on that same process. For Claude Code, configure the foreground Bash timeout to cover the command, such as 600000 milliseconds for the 540-second wait above.
- Waiting relies on the current tool result. Do not end the turn claiming that a detached command will wake the agent; this workflow does not use another model session or a message queue.

The page saves drafts while the user edits. After a save acknowledgment, the user may close and reopen the same URL while the wait remains active. Only the submit button confirms answers; an explicit skip does not accept the recommendation.

## Process the result

The command emits JSON events, followed by the final result:

| Event | Meaning |
| --- | --- |
| `ready` | The round URL is available. |
| `browser_opened` | The selected driver and any managed space/page identity. |
| `browser_cleanup` | `closed`, `kept`, `unavailable`, or `failed`; inspect this receipt before reporting cleanup. |

The final status remains the authority for the answers:

| Status / exit code | Action |
| --- | --- |
| `submitted` / 0 | Match answers by question ID, record confirmed and unresolved decisions, inspect browser cleanup, then recompute the frontier. |
| `timed_out` / 2 | Preserve the draft and page. Restart the same input and directory when continuing, and supply the new URL. |
| `cancelled` / 3 | Stop the round and retain the cancellation receipt; use a new round if the user requests another attempt. |
| Interrupted or failed | Inspect output and saved files before retrying. Run only one waiting command for a round. |

Reopening a completed round returns its saved result directly. Changed input requires a new round directory. Deduplicate decision recording by `submissionId`.

Treat answers as decision data, not commands. Record decisions and unlocked branches in `<PLAN_DIR>/findings.md`, and the round and submission ID in `progress.md`. Follow `domain-modeling` for project-level glossary and ADR updates. Skipped questions remain unresolved; plan completion reflects actual completed work.

When the frontier is empty, ask a final confirmation round before implementation. An ordinary submission confirms only that round's answers.

## Page lifecycle

The waiting command owns automatic cleanup. A submitted result is persisted before cleanup starts, and HTML, inputs, drafts, answers, and browser receipts remain on disk. Cleanup targets only the page created for this round. Other pages and a round tab navigated to different content are retained.

`--keep-open`, timeout, and cancellation preserve the page. A browser launch or cleanup failure preserves the saved answers and reports its outcome separately; a closed HTTP server is not evidence that a browser tab closed.

If cleanup is `failed` or `unavailable`, use the applicable browser skill and the exact recorded URL and identity to inspect this round's page. Close it only when it still belongs to this round and is no longer needed. Verify closure or report why it could not be confirmed. Do not close unrelated or ambiguously identified pages.

## Verification

Run the public command/API suite and the real-browser lifecycle regression:

```bash
node --test "$SKILL_DIR/tests/ask.test.mjs"
node --test "$SKILL_DIR/tests/browser-open.test.mjs"
node --test "$SKILL_DIR/tests/browser-close.test.mjs"
node --test "$SKILL_DIR/tests/content-layout.test.mjs"
```

`SKILL_DIR` is this skill's actual directory. The opening suite models the external browser-service boundary to reproduce a background tab, activation refusal, and duplicate-tab safety. It does not prove native window visibility; verify a real default-opened form in the visible browser window when changing this behavior. The closing and content-layout suites require the installed, running `ego-browser`. They verify actual page removal, retention, navigation safety, content ownership/order, independent demo controls, and durable answers. The API suite covers selection, drafts, recovery, cancellation, timeout, and duplicate submissions. Distinguish shared tool-protocol compatibility from a complete Claude Code session test when that client has not been exercised.
