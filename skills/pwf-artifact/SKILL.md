---
name: pwf-artifact
description: Saves a user-selected conversation artifact in the active Planning with Files task directory.
argument-hint: "Content or file path to save"
---

# PWF Artifact

Save only the text, code, diagram, or existing file the user selected. Recover the complete artifact from the conversation. If the reference is ambiguous, ask which artifact to save.

1. Use `planning-with-files` to select or create `<PLAN_DIR>`. Reuse the caller's selected plan when invoked from another workflow.
2. Save the artifact under `<PLAN_DIR>/artifacts/`. Honor a requested filename or format. Otherwise choose a short name and a format:
   - Documents, reports, and edited prose: use one standalone `.html` file with inline styles, no external resources, light and dark modes, a narrow layout, and horizontal scrolling for wide tables.
   - Code: use the extension for its language.
   - Existing files: preserve the extension and original bytes.

   Keep the target inside this directory. Add a numeric suffix instead of overwriting an existing filename. Reuse the path if the artifact is already in the active plan directory.
3. Record the path and purpose in `<PLAN_DIR>/progress.md`. Verify the saved content against the original. For HTML, open it with `open`. Return the final absolute path.
