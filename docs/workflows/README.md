# Workflows

> **This file is part of the documentation set.** See §9.0 of
> [the source of truth](../project/COSC499-TEAM10-PROJECT-DOCS.md). Update it when a workflow
> is added, removed or renamed.

Repeatable procedures for working in this repository, written to be **tool-agnostic**. Any AI
agent, and any person, can follow them directly. Nothing here depends on a particular assistant.

| Workflow | What it does |
|---|---|
| [commit.md](commit.md) | Group changed files into logical commits and make them one at a time |
| [make-pr.md](make-pr.md) | Open a pull request into `main` for the current branch |

## How to run one

**Any agent, or a person:** read the file and follow it. That is the whole mechanism. These are
plain markdown procedures with no tool-specific syntax, so "follow `docs/workflows/commit.md`"
is a complete instruction.

**Claude Code:** type `/commit` or `/make-pr`. The files in
[`.claude/commands/`](../../.claude/commands/) are thin pointers that tell the agent to read and
follow the corresponding file here.

**Other assistants** (Cursor, Codex, Copilot, Aider, and the rest) discover these through
[AGENTS.md](../../AGENTS.md#workflows), the cross-tool standard, which every one of them reads.
If yours supports its own command format, point it at the file here rather than copying the
content, so there stays exactly one source of truth.

## Adding a workflow

1. Write the procedure here as `docs/workflows/<name>.md`. Tool-agnostic, no assistant-specific
   syntax.
2. Add a row to the table above.
3. Add a row to the **Workflows** section of [AGENTS.md](../../AGENTS.md#workflows).
4. Optionally add a pointer in `.claude/commands/<name>.md` so Claude Code users get a slash
   command, and note it in [`.claude/README.md`](../../.claude/README.md).

**Never duplicate the procedure text into a tool's own config.** Pointers only. A rule that
exists in two files will be true in one of them and wrong in the other.
