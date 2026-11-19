---
name: obsidian-simple-mind-map
description: Creates, reads, and edits Simple Mind Map .smm.md files in Obsidian. Use to convert Markdown, edit nodes by UID, set links, or refresh previews. Not for images or XMind files.
---

# Obsidian Simple Mind Map

Use `scripts/smm_cli.py` to call the installed `simple-mind-map` plugin. The plugin owns the format, compression, index, and preview. Use the CLI for reads and writes. Use incremental commands for an existing map so its styles, links, and positions survive. Do not edit Base64 metadata directly.

## Before you begin

Obsidian must be running with its CLI enabled and the plugin enabled in the target vault. Set `SMM_CLI` to the absolute path of this skill's `scripts/smm_cli.py`:

```bash
SMM_CLI="/Users/sunx/Dropbox/syncer/.agents/skills/obsidian-simple-mind-map/scripts/smm_cli.py"
python3 "$SMM_CLI" probe
```

The default vault is `obsidian` at `/Users/sunx/Dropbox/syncer/apps/obsidian`. For another vault, pass `--vault NAME --vault-root /absolute/path` on each command. The options may go before or after the subcommand.

Check that `probe` returns the intended `vaultRoot`; the CLI stops on a mismatch. Before converting Markdown, also check that `markdownTransform` is `true`. Every command other than `self-test` probes automatically.

## Create a map

Write the Markdown to the vault, then convert it:

```bash
python3 "$SMM_CLI" convert-md "notes/path/topic.md" --delete-source
```

Use `--delete-source` only for temporary Markdown you created for this conversion. Once conversion starts, the CLI deletes that source on success or failure. Omit the flag when converting a user's existing document.

Use the returned `path`. The plugin picks a new name if one already exists. New nodes use Obsidian's `textFontFamily` or the theme's `--font-text`. Verify the new map and confirm any temporary source was removed.

## Find and edit nodes

```bash
python3 "$SMM_CLI" read "notes/path/topic.smm.md"
```

Address nodes by the returned `uid` and display their `plainText`. If the user supplied only text, look up every match. Continue for one match; for several, show the candidate UIDs and parents and ask which to use.

```bash
python3 "$SMM_CLI" add-child FILE PARENT_UID "New node"
python3 "$SMM_CLI" add-subtree FILE PARENT_UID '{"text":"New branch","children":[{"text":"Child node"}]}'
python3 "$SMM_CLI" add-sibling FILE NODE_UID "Sibling node"
python3 "$SMM_CLI" set-text FILE NODE_UID "New text"
python3 "$SMM_CLI" set-link FILE NODE_UID URL "Link title"
python3 "$SMM_CLI" delete FILE NODE_UID
```

Replace `FILE` and the UIDs. Use `add-child` for one node and `add-subtree` for a group with parent-child relations. Run independent edits one at a time. A subtree is a single JSON tree; each node has a nonempty `text` and optional `children`. The plugin assigns UIDs.

The CLI waits for the change, saves it, and reads it back. Check any returned new UID. Read again to locate nodes, verify several edits, or diagnose partial success. Check both text and parent links.

Links are stored in `hyperlink` and `hyperlinkTitle`, one per node, not in the Markdown body:

```bash
python3 "$SMM_CLI" set-link FILE NODE_UID "https://example.com" "Website"
python3 "$SMM_CLI" set-link FILE NODE_UID "notes/work/lessons.md" "[[Lessons]]"
```

For internal links, use a vault-relative URL and an Obsidian internal link as the title. Read back `hyperlink`, `hyperlinkTitle`, and `richText: true`. Do not embed link syntax in node `text`.

## Save and recover from errors

Edits refresh the preview by default. Use `--no-preview` only if the user accepts a stale preview. To save or refresh the preview separately:

```bash
python3 "$SMM_CLI" save FILE
```

The CLI polls its operation internally. If it is briefly silent, wait for the current process instead of replaying the write. It has no separate `status` command and does not expose the operation ID. After an error, timeout, or interruption, run `read` before retrying to check for partial success. Keep the original error. Silence does not prove that Obsidian is stopped.

## Limits

- Prefer vault-relative paths. Preserve leading dots and reject `..` segments. An absolute path must be inside `--vault-root`.
- `set-text` writes plain text. The root cannot be deleted or given siblings. Existing free nodes can only be read or deleted.
- Inspect the plugin API before extending the CLI for rich text, images, creating or moving free nodes, themes, or layouts.
- Commands that open views run under a per-vault lock; `probe` and `self-test` do not take it. Keep this entry point to prevent concurrent writes. The CLI can briefly switch the active tab and trigger an existing map save or refresh, even when using a separate leaf.

For initialization, saving, CLI polling, or plugin integration work, read [Plugin integration and verification](references/plugin-integration.md). Routine commands do not need those details.
