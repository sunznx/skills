# Plugin integration and verification

Read this when troubleshooting, changing the CLI, or adding capabilities. For routine commands, see `smm_cli.py --help`.

## Verified integration

Local `probe` confirmed `simple-mind-map` version `0.2.7` and Markdown conversion support. Edits use the `execCommand`, `getMindMapCurrentData`, and `saveToLocal` events. Conversion uses the plugin's new-conversion menu item. After an upgrade, check the source, interfaces, and observed behavior again.

`probe` checks that the plugin is enabled, reports its version and conversion capabilities, and verifies the vault root. It does not prove compatibility with every edit or event. During edits, the CLI also checks the view's save interface and waits for a plugin instance.

## Views and initialization

Each operation opens a separate leaf, checks the path, activates it temporarily, then closes it and restores the previous leaf. A process file lock serializes reads and writes in the same vault.

Even `read` activates a temporary leaf. The plugin's `_handleActiveChange` calls `save()` when the old map loses focus. When restoring a hidden map, it calls `_checkForExternalChanges()` and then `setViewData()`. A read can therefore save or refresh another open map. Separate leaves and the vault lock do not isolate these tab-switch effects.

In 0.2.7, `_initializeMindMap` gives each Vue root a separate `$bus`. A refresh alone does not prove a write to the wrong file. Verify file contents and UI side effects independently.

`read` uses parsed data from a fresh leaf and does not need rendering. Edits and saves need the internal `mindMap` instance:

- A background window may not fire `ResizeObserver`. The CLI attempts view initialization once the editor has dimensions.
- The plugin's `initMindMap()` returns when the container has zero dimensions. While waiting, the CLI calls it for a sized but uninitialized component and checks again for readiness.
- On timeout, inspect the editor size and whether the plugin component exists. Keep the original error; do not bypass the plugin to edit file data.

Node edits use the native `execCommand` and plugin-generated UIDs. For one node, the CLI waits for the new UID, its text, and its parent. For a subtree, it also checks node count, persisted text, and parent links. Saving calls `saveToLocal`, waits for a newer modification time, then reads back the result.

## Asynchronous operations and retries

`run_eval` tracks each operation ID in `app.__smmCliOperations` and polls after launch. States include `running`, `done`, and `error`; an absent record returns `missing`. The CLI exposes neither the ID nor a separate status command.

Polling is read-only and may be retried after a CLI crash. If launch fails, the CLI checks the same operation ID and resumes polling if the record exists. The current code retries launch when the record is missing or the lookup returns empty output. Empty output does not prove the operation was never queued, so that branch can duplicate work. Do not replay writes at the agent layer. A missing record or polling failure does not prove the file is unchanged. A write holds the lock until read-back verification or error exit.

`js_value()` encodes values passed to Obsidian `eval` as ASCII JSON escapes, preventing CLI chunk decoding from splitting CJK characters. Result JSON can still display them directly.

## Failure modes

- No output while waiting: Check for another CLI holding the vault lock. The `flock` wait has no timeout. An outer 60-second limit can kill a normally queued command; do not repeat the write on that basis.
- `GPU process isn't usable. Goodbye.` was observed in a live conversion and indicates an Obsidian/Electron CLI process failure. A separate `probe` cannot establish whether a previous write ran.
- Other maps refresh: Check tab switching and verify file contents separately before concluding that a write crossed files.

The total polling deadline in `run_eval` does not bound each `subprocess.run`. A subprocess hang is an unverified risk, not an established cause.

## Links

`set-link` calls `SET_NODE_HYPERLINK` to set `hyperlink` and `hyperlinkTitle`, then `SET_NODE_DATA` to set `richText: true`. External links use full URLs. The plugin hands non-web vault paths to Obsidian and supports hover previews. These are clickable references, not embedded contents.

## Verification

Run from the skill directory:

```bash
python3 scripts/smm_cli.py --help
python3 scripts/smm_cli.py self-test
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/smm_cli.py probe
```

`self-test` is offline. Unit tests replace the CLI process boundary to verify async queueing and retries; they do not establish rendering compatibility with the plugin.

To verify live conversion and subtree insertion:

```bash
python3 tests/e2e_add_subtree.py
```

The test creates a temporary directory in the default vault, converts a map with the plugin, inserts 25 nodes, reads back their UIDs and parent links, and cleans up. It uses the default vault and root. Update the test configuration for another vault. Ensure the CLI and plugin are ready before running it.
