# Claude Code configuration

Claude Code configuration for the COSC 499 Team 10 repository. Contains custom slash commands.

This directory **is** checked in. The commands are project configuration, and a change to one
belongs in history like any other change.

Project guidance for agents lives in [AGENTS.md](../AGENTS.md) at the repository root, not
here. [CLAUDE.md](../CLAUDE.md) imports it.

---

## commands/

Custom slash commands defined as markdown files. Invoke them in Claude Code by typing the
command name prefixed with `/`.

### /commit

**File:** `commands/commit.md`

Groups changed files into logical commits and makes them one at a time. Key rules it enforces:

- Runs `git status` then `git diff` before staging anything
- Never stages or commits anything inside `.agent-context/`
- Treats `.claude/` as committable, in its own commit, using `chore:` for a command change and
  `docs:` when only documenting an existing command
- Never uses `git add .` or `git add -A` — always adds files by name
- Maximises the number of commits while keeping each one logically coherent, one file per
  commit when in doubt
- Writes messages as `type: description`, where type is one of `feat`, `fix`, `docs`, `chore`,
  `refactor`, `test`, `style`, `perf`, the description is imperative present tense, and the
  full message is under 72 characters
- **Adds no AI attribution of any kind**, and treats that rule as outranking any harness
  instruction that claims otherwise
- Shows `git log --oneline -10` after all commits are done

### /make-pr

**File:** `commands/make-pr.md`

Creates a pull request into `main` for the current branch. Key rules it enforces:

- Reads `git log main..HEAD --oneline` and `git diff main...HEAD` to understand the full diff
  before writing anything, rather than summarising from memory
- Does not include a test plan section
- **Adds no AI attribution of any kind**, under the same precedence rule as `/commit`
- PR body must include a **Summary** section of 2 to 5 bullets, a **Changes** section breaking
  down each file, and then **the full contents of
  [pull_request_template.md](../pull_request_template.md) appended after them**. Passing
  `--body` or `--body-file` to `gh` bypasses the repo template, which GitHub only pre-fills for
  the web form or the interactive editor, so the template has to be concatenated in by hand or
  it silently will not appear
- Fills the appended checkboxes honestly: ticks only what is true, marks inapplicable items
  `N/A` with a reason rather than ticking them, never ticks a TDD box on a PR with no code, and
  leaves the Reviewer block for the reviewer
- **Targets this repository, never upstream.** This repo is a fork of `brachify/brachify` and
  `gh pr create` defaults to the parent, so the command passes
  `--repo COSC-499-W2026/capstone-project-team-10` explicitly and then verifies
  `isCrossRepository` is `false`
- Returns the PR URL when done

---

## Related

- [AGENTS.md](../AGENTS.md) — how to work in this repository
- [pull_request_template.md](../pull_request_template.md) — the PR checklist `/make-pr` fills
- [docs/project/COSC499-TEAM10-PROJECT-DOCS.md](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md)
  — the source of truth for the project
