---
name: agent-messaging
description: Delivers tasks or replies to existing agents using native messaging, Codex TUI queue, or Herdr. Use when the user wants to contact an identified agent or wait for its reply.
---

# Agent Messaging

## Recipients

Deliver only to existing agents. To assign work to an existing main agent in another session, the user must explicitly request cross-session assignment or designate the collaborator for this task. Resolve the intended recipient before sending. If the recipient is unclear, ask instead of picking one. A failed delivery does not authorize starting an agent or opening a session.

## Choose a mode

- **`notify` (default):** Deliver asynchronously and continue without waiting. Ask the recipient to report when the task is `completed`, `failed`, or `blocked`.
- **`request`:** Deliver and wait only when the user explicitly asks to wait, get a reply, or receive the result, or selects `request`.
- In `request` mode, match replies by agent identity. Keep only one outstanding task per recipient.

## Prefer native messaging

Use the current runtime's messaging tools first. A recipient being reachable through Herdr is not a reason to bypass native delivery.

In Codex:

1. Use `followup_task` to deliver tasks in either mode. `send_message` does not wake an idle agent and is not a task dispatch tool.
2. For `notify`, append: `This is a notify request. Use native messaging to report when the task is completed, failed, or blocked.` Once every recipient returns `delivered` or `queued`, continue without calling `wait_agent`.
3. For `request`, dispatch to all recipients first, then collect replies with a longer `wait_agent` timeout. Replies may arrive out of order. Remove each sender from the pending set when its reply arrives.
4. When you finish an incoming task, use `send_message` to send a brief result to the sender in the platform's sender metadata. Include `completed`, `failed`, or `blocked`. Do not duplicate the sender metadata in the message body.

## Codex TUI session

If `followup_task` definitively reports that the recipient is outside the current collaboration tree and the user supplied a Codex session UUID or exact name, try the Codex CLI queue before Herdr for `notify`.

1. Run `codex queue --help` to check that the installed CLI supports it.
2. Append: `This is a notify request. Report when the task is completed, failed, or blocked.`
3. Queue the message without launching or resuming the other TUI:

```bash
codex queue --thread "$target" --message "$message"
```

An exit code of 0 plus `Queued message` means `queued`. Do not wait or fall back. A nonzero exit is a definite failure and permits the Herdr fallback. Stop on a timeout or ambiguous result to avoid duplicate delivery.

`codex queue` supports `notify` only. For `request`, use native tools that can match replies and try Herdr only after a definite failure.

## Multiple recipients

Send once per recipient; do not broadcast. In `request` mode, send to every recipient before waiting for any reply. Record the channel and status separately for each recipient, even if another delivery fails.

## When to fall back

- **Delivered or queued:** Stop for that recipient. Do not fall back.
- **Definite failure:** The native tool is unavailable, or the recipient is outside the current tree or uses another runtime. For eligible `notify` requests, try the Codex TUI queue first. Otherwise try Herdr.
- **Uncertain delivery:** A timeout, interruption, or ambiguous result may mean the task was delivered. Stop, report uncertainty, and do not retry using another channel.

## Herdr delivery

Use Herdr after a definite native delivery failure, or directly when Herdr has already been selected to reach the existing recipient.

1. Confirm `HERDR_ENV=1`. Otherwise report that Herdr is unavailable and stop. Do not control sessions from outside Herdr.
2. Run `herdr --help`. Use the recipient's name or pane ID from the request.
3. Check `herdr agent get <target>`:
   - `idle` or `done`: Proceed.
   - `working`: Run `herdr agent wait <target> --timeout 300000`, then check the status once more.
   - `blocked`: Report the status. Do not answer requests or approvals for the recipient.
   - `unknown` or unresolved: Stop and report.
4. Run `herdr agent get "$HERDR_PANE_ID"` to read your sender name. Use your pane ID if no name is set.
5. Keep the task body unchanged and append the return address and callback request: `发送方：<sender>。处理完后通知发送方。`

For `notify`, send without waiting:

```bash
herdr agent prompt <target> '<message>\n\n发送方：<sender>。处理完后通知发送方。'
```

For `request`, wait and read the result:

```bash
herdr agent prompt <target> '<message>\n\n发送方：<sender>。处理完后通知发送方。' --wait --timeout 300000
herdr agent read <target> --source recent-unwrapped --lines 120
```

After completing a Herdr `notify` task, use this delivery flow to return the result to `<sender>`. The original sender does not wait in its original call.

## Local file fallback

If every applicable channel is unavailable or has definitively failed for a recipient, save the original message as Markdown. Saving does not count as delivery. Do not use this fallback after a timeout, interruption, or ambiguous result.

1. Choose a short, filename-safe `$title` for the task. Reject path separators, `.` and `..`.
2. Create a unique temporary directory:

```bash
mktemp -d "${TMPDIR:-/tmp}/agent-messaging-XXXXXX"
```

3. Save the original message unchanged as `$title.md` in that directory.
4. Report the absolute path and mark the recipient `not_delivered`.

## Report delivery

For each recipient, report the channel, whether delivery succeeded, whether you are waiting, and the final state if known: `completed`, `failed`, `blocked`, or `not_delivered`. Include the absolute path for any saved message. Report partial success per recipient.
