---
name: visual-pr
description: Only use when the user explicitly invokes this skill by name.
---

# Describe a Pull Request

Create or update the pull request for the current task with a concise description that helps a reviewer understand why the change exists and the shape of the implementation.

## Plan and artifacts

Before gathering task context, use `planning-with-files` to select or create this task's plan as `<PLAN_DIR>`; when another workflow invokes this skill, use that workflow's selected plan. Keep its absolute directory and `PLAN_ID`. Use that same plan for the PR description and any supporting visuals.

## Workflow

1. Read the description template:

   `Read({SKILLBASE}/references/pr_description_template.md)`

2. Identify or create the pull request:
   - Check the current branch for a PR with `gh pr view --json url,number,title,state,baseRefName,headRefName 2>/dev/null`.
   - If no PR exists, inspect `git status --short --branch` and the commits on the current branch.
   - Commit task-related changes when needed, push the branch with an upstream, and create a PR for it. Follow the repository's git safety protocol.
   - Ask the user to select a PR only when the current branch has no relevant work and there is no safe current-branch PR to create.

3. Gather only the context needed to explain the change:
   - Read the ticket and any relevant task artifacts.
   - Read the complete PR diff and enough surrounding code to understand behavior and ownership.
   - Use `gh pr view` to collect PR metadata and changed files.
   - Read `{SKILLBASE}/references/show-me.md` for the visual-outline conventions used in the PR body.

4. Write the PR description using the template:
   - Keep **Why the change** to exactly one sentence.
   - Keep **Special things to note** to 1-3 bullets. Prioritize reviewer warnings, migrations, compatibility constraints, deliberate omissions, or surprising decisions. Write `- None.` when there are no special considerations.
   - Make **Change outline** a compact, `/show-me`-inspired structural view rather than prose or a file-by-file changelog.
   - Include only the views that help explain this PR:
     - SQL table and endpoint contract changes, plus pseudocode for business logic.
     - key data structure / type changes
     - A shallow file tree showing changed responsibilities.
     - React component tree changes, including important hooks, state, and package boundaries.
     - Call-tree, call-stack, control-flow, or data-flow changes.
   - Prefer `diff` blocks when showing changes to an existing shape. Show the complete target shape when most of it is new or diff notation would obscure ownership or order.
   - Keep each view focused on what a reviewer needs. Omit categories that did not change.
   - Optional: include ticket URLs or related plan/document URLs in the header when available; otherwise omit the header.

5. Save and publish the description:
   - Create `<PLAN_DIR>/visual-pr/pr-{number}/` and save the description as `<PLAN_DIR>/visual-pr/pr-{number}/pr-description.md`.
   - Use that saved absolute filename as `{output-path}` in `gh pr edit {number} --body-file "{output-path}"`.
   - Confirm the update succeeded.
   - The Markdown file is the PR body that GitHub renders. For the user to read locally, build `<PLAN_DIR>/visual-pr/pr-{number}/pr-description.html` from it:
     - Keep the same sections, text, and order. Add nothing beyond the description.
     - Open with the PR number and title, linked to the PR URL.
     - Color the added and removed lines in each `diff` block. Show other code blocks in monospace that scrolls sideways rather than wrapping.
     - Make it a single file with inline CSS and no external resources. It works on desktop and mobile, in light and dark mode.
     - Rebuild it whenever the Markdown file changes, then open it:

       ```
       Bash(open "<PLAN_DIR>/visual-pr/pr-{number}/pr-description.html")
       ```

   - Record the PR URL, both saved paths, and the outcome in the selected plan's `findings.md` and `progress.md`.

6. Report completion:
   - Read `{SKILLBASE}/references/describe_pr_final_answer.md`.
   - Respond using that final answer template with the PR URL, local file links to the saved description and its page, the selected plan, and a concise list of changed files.

Always read and follow `{SKILLBASE}/references/pr_description_template.md`. Do not expand the PR body beyond that template.

Write as one human talking to another: avoid jargon and slang, and use simple, coherent, concise language.
