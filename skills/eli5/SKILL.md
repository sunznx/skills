---
name: eli5
description: Explain a topic like I'm a 5 year old by generating and opening a visual HTML artifact. Use when the user invokes $eli5 with a topic or asks for a dead-simple picture explainer of how something works.
---

# eli5

Explain like I'm someone who knows nothing about this topic, using a self-contained HTML artifact with big pictures and few words.

Topic: $ARGUMENTS

## Create the artifact

Generating the HTML is required. Do not substitute Mermaid, Markdown, or an inline chat diagram.

Resolve `PROJECT_ROOT` in this order:

1. Use the absolute `$PWF_PLAN_ROOT` when it names an existing directory.
2. Otherwise use the current Git repository root.
3. Without a project root, leave `PROJECT_ROOT` unset.

Resolve `ARTIFACT_PARENT` in this order:

1. Without `PROJECT_ROOT`, use `${TMPDIR:-/tmp}`.
2. When `$PLAN_ID` names an existing `$PROJECT_ROOT/.planning/$PLAN_ID` directory, use its `artifacts` subdirectory.
3. When `$PROJECT_ROOT/.active_plan` names an existing `.planning/<plan>` directory, use its `artifacts` subdirectory.
4. Otherwise use `$PROJECT_ROOT/.planning`.

Accept a plan name only when it is one path segment and does not contain `..`.

Create a fresh directory for every run:

```bash
ARTIFACT_DIR="$(mktemp -d "$ARTIFACT_PARENT/eli5-XXXXXXXX")"
```

Create `$ARTIFACT_PARENT` first when needed. Write the complete explainer to `$ARTIFACT_DIR/index.html`, then read the file back and confirm it is non-empty HTML.

## Open the artifact

After the HTML is complete:

1. Prefer `chrome:control-chrome`. Open the absolute `file://` URL and verify that the page loaded.
2. If Chrome control is unavailable or rejects the local file, run `open "$ARTIFACT_DIR/index.html"` on macOS and check that the command succeeds.

If a higher-priority runtime rule or permission prevents file creation or GUI opening, report the blocking reason and stop. Never silently return a different artifact format.

Return the absolute HTML path to the user.
