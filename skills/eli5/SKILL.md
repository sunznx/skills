---
name: eli5
description: Explain a topic like I'm a 5 year old by generating and opening a visual HTML artifact. Use when the user invokes $eli5 with a topic or asks for a dead-simple picture explainer of how something works.
---

# eli5

Explain like I'm someone who knows nothing about this topic, using a self-contained HTML artifact with big pictures and few words.

Topic: $ARGUMENTS

## Create the artifact

Generating the HTML is required. Do not substitute Mermaid, Markdown, or an inline chat diagram.

Create `ARTIFACT_DIR` once per run. Ignore `PLAN_ID` and `.active_plan`.

```bash
if [ -n "${PWF_PLAN_DIR:-}" ] && [ "${PWF_PLAN_DIR#/}" != "$PWF_PLAN_DIR" ]; then
  ARTIFACT_PARENT="$PWF_PLAN_DIR/artifacts"
else
  ARTIFACT_PARENT="${TMPDIR:-/tmp}"
fi
mkdir -p "$ARTIFACT_PARENT"
ARTIFACT_DIR="$(mktemp -d "$ARTIFACT_PARENT/eli5-XXXXXXXX")"
```

Write the complete explainer to `$ARTIFACT_DIR/index.html`, then read the file back and confirm it is non-empty HTML.

## Open the artifact

After the HTML is complete:

Read and follow the available `chrome:control-chrome` skill. Use `🧒eli5` as the Chrome session name, open the absolute `file://` URL for `$ARTIFACT_DIR/index.html`, and verify that the page loaded.

If a higher-priority runtime rule or permission prevents file creation or GUI opening, report the blocking reason and stop. Never silently return a different artifact format.

Return the absolute HTML path to the user.
