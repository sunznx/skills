---
name: eli5
description: Explain a topic like I'm a 5 year old. Use when the user types /eli5 <topic> or asks for a dead-simple picture explainer of how something works.
---

# eli5

Explain like I'm someone who knows nothing about this topic, using a HTML artifact with big pictures and few words.

Topic: $ARGUMENTS

## Choose the artifact directory

First check the runtime context for a current Trellis task. If the context does not say, and the current git repository contains `.trellis/scripts/task.py`, use `python3 ./.trellis/scripts/task.py current --json` from the repository root. Resolve the task directory to an absolute path and assign it to `TASK_DIR`.

Create a fresh directory for every run. When a current Trellis task exists:

```bash
ARTIFACT_DIR="$(mktemp -d "$TASK_DIR/eli5-XXXXXXXX")"
```

Otherwise:

```bash
ARTIFACT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/eli5-XXXXXXXX")"
```

Write the self-contained explainer to `$ARTIFACT_DIR/index.html`.

## Open the artifact

After the HTML is complete, use `chrome:control-chrome`. Name the Chrome session `eli5`, open the absolute `file://` URL for `$ARTIFACT_DIR/index.html`, and verify that the page loaded in Chrome's `eli5` group.

Return the absolute HTML path to the user.
