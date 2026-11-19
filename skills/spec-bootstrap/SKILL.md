---
name: spec-bootstrap
description: Installs the global Codex coding workflow, including the Planning with Files plugin and lifecycle hooks. Use when the user invokes $spec-bootstrap or asks to install this workflow globally.
---

# spec-bootstrap

Run:

```bash
python3 "$SKILL_ROOT/scripts/spec_bootstrap.py"
```

The script:

- Installs the Planning with Files plugin globally through the Codex marketplace.
- Temporarily sets `"commands": []` in the marketplace manifest, clears the old cache, regenerates the plugin cache, then restores the manifest. This prevents duplicate `source-command-*` skills.
- Preserves existing global configuration and hooks.

The plugin supplies the skills and lifecycle hooks. Report the script result and ask the user to review and trust the global hooks with `/hooks` in a new Codex session. If installation fails, report the original error.
