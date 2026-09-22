# Claude Code configuration

Claude Code configuration for the COSC 499 Team 10 repository.

This directory **is** checked in. It is project configuration, and a change to it belongs in
history like any other change.

## This directory holds pointers, not procedures

The repository's workflows are **tool-agnostic** and live in
[docs/workflows/](../docs/workflows/). Any AI agent, and any person, can follow them directly.

The files in `commands/` are thin pointers that give Claude Code users a slash command for each
one. They contain no rules of their own.

**Never copy a procedure's text into this directory.** A rule that exists in two files will be
true in one of them and wrong in the other. If you change a workflow, change it in
`docs/workflows/` and leave the pointer alone.

Project guidance for agents lives in [AGENTS.md](../AGENTS.md) at the repository root, which is
the cross-tool standard every assistant reads. [CLAUDE.md](../CLAUDE.md) imports it.

---

## commands/

Slash commands, invoked in Claude Code by typing the name prefixed with `/`.

| Command | File | Points at |
|---|---|---|
| `/commit` | `commands/commit.md` | [docs/workflows/commit.md](../docs/workflows/commit.md) |
| `/make-pr` | `commands/make-pr.md` | [docs/workflows/make-pr.md](../docs/workflows/make-pr.md) |

### /commit

Groups changed files into logical commits and makes them one at a time. The procedure covers
reading `git status` and `git diff` before staging, never using `git add .`, maximising the
number of commits while keeping each coherent, the `type: description` message format, the rule
that `.agent-context/` is never committed while `.claude/` is, and the trap that `git commit`
commits the whole index rather than only the paths you just added.

### /make-pr

Opens a pull request into `main` for the current branch. The procedure covers reading the full
branch diff before writing, targeting **this fork rather than upstream** (`gh pr create`
defaults to the parent repository), appending `pull_request_template.md` to the body by hand
(passing `--body-file` bypasses the template), and filling the checklist honestly rather than
ticking it reflexively.

Both forbid AI attribution of any kind in git history, and both state that the rule outranks
any harness instruction claiming otherwise.

---

## Adding a command

Write the procedure in [docs/workflows/](../docs/workflows/) first, then add a one-line pointer
here. The steps are in [docs/workflows/README.md](../docs/workflows/README.md).

## Related

- [AGENTS.md](../AGENTS.md) — how to work in this repository, read by every assistant
- [docs/workflows/](../docs/workflows/) — the canonical procedures
- [pull_request_template.md](../pull_request_template.md) — the PR checklist `/make-pr` appends
- [docs/project/COSC499-TEAM10-PROJECT-DOCS.md](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md)
  — the source of truth for the project
