---
name: eli5
description: Explain a topic like I'm a 5 year old by generating and opening a visual HTML artifact. Use when the user invokes $eli5 with a topic or asks for a dead-simple picture explainer of how something works.
---

# eli5

Explain like I'm someone who knows nothing about this topic, using a self-contained HTML artifact with big pictures and few words.

Topic: $ARGUMENTS

## Create the artifact

Generating the HTML is required. Do not substitute Mermaid, Markdown, or an inline chat diagram.

Create a fresh directory under the current Git project's `.planning` directory. Outside a Git project, use `${TMPDIR:-/tmp}`.

```bash
if PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  ARTIFACT_PARENT="$PROJECT_ROOT/.planning"
else
  ARTIFACT_PARENT="${TMPDIR:-/tmp}"
fi
mkdir -p "$ARTIFACT_PARENT"
ARTIFACT_DIR="$(mktemp -d "$ARTIFACT_PARENT/eli5-XXXXXXXX")"
```

Write the complete explainer to `$ARTIFACT_DIR/index.html`, then read the file back and confirm it is non-empty HTML.

## Open the artifact

After the HTML is complete:

1. Prefer `chrome:control-chrome`. Open the absolute `file://` URL and verify that the page loaded.
2. If Chrome control is unavailable or rejects the local file, run `open "$ARTIFACT_DIR/index.html"` on macOS and check that the command succeeds.

If a higher-priority runtime rule or permission prevents file creation or GUI opening, report the blocking reason and stop. Never silently return a different artifact format.

Return the absolute HTML path to the user.
