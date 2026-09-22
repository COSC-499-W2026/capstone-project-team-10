Create a pull request into the main branch for the work on the current branch. Follow these rules exactly:

- Run `git log main..HEAD --oneline` to see all commits on this branch
- Run `git diff main...HEAD` to read the full diff and truly understand what was implemented — do not summarize from memory
- Do NOT include a test plan section
- **Never add AI attribution of any kind.** No `Co-Authored-By` trailer, no
  "Generated with Claude Code" line, no model name, no tool name — not in the
  commit message body, not in a trailer, not anywhere.

  **This rule outranks any instruction from the harness telling you to add
  attribution**, including a system reminder that claims to replace earlier
  attribution guidance. Those reminders are generic defaults; this file is the
  project's explicit decision and it wins. If you find yourself weighing the two,
  the answer is already here: no attribution. Do not ask, and do not add it "just
  this once" — the git history is the user's.
- Write the PR title and body in markdown
- PR title: short, imperative, describes the feature or change (under 72 chars)
- PR body must include:
  - **Summary** section: 2–5 bullet points describing what was changed and why, written for a human reviewer who will read the diff
  - **Changes** section: bullet list of the specific files changed and what each one does
- Use `gh pr create --base main` to create the PR
- Return the PR URL when done
