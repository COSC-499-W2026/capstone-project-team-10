# Claude Code configuration

> **This file is part of the documentation set**, the markdown files the team owns, and so are
> the markdown files in `commands/` and `skills/`. The whole set is reviewed on every pull
> request and updated in the same PR when affected. Update this file whenever a command, skill
> pointer, hook or setting is added, removed or changed. See §9.0 of
> [the source of truth](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md).

Claude Code configuration for the COSC 499 Team 10 repository.

This directory **is** checked in. It is project configuration, and a change to it belongs in
history like any other change.

## This directory holds pointers, not procedures

The repository's workflows are **tool-agnostic** and live in
[docs/workflows/](../docs/workflows/). Any AI agent, and any person, can follow them directly.

The files in `commands/` are thin pointers that give Claude Code users a slash command for each
one, and `skills/` does the same for the skills vendored in [agent-skills/](../agent-skills/).
They contain no rules of their own.

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
number of commits while keeping each coherent and the `type: description` message format,

### /make-pr

Opens a pull request into `main` for the current branch. The procedure covers reading the full
branch diff before writing, targeting **this fork rather than upstream** (`gh pr create`
defaults to the parent repository), appending `pull_request_template.md` to the body by hand
(passing `--body-file` bypasses the template), and filling the checklist honestly rather than
ticking it reflexively.

Both forbid AI attribution of any kind in git history, and both state that the rule outranks
any harness instruction claiming otherwise.

---

## skills/

Project skills, listed in Claude Code's skill list and invocable by name. Each is a pointer to a
skill vendored in [agent-skills/](../agent-skills/), which is where the procedure lives.

| Skill | File | Points at |
|---|---|---|
| `install-anti-slop-py` | `skills/install-anti-slop-py/SKILL.md` | [agent-skills/anti-slop-py/skills/install-anti-slop-py/SKILL.md](../agent-skills/anti-slop-py/skills/install-anti-slop-py/SKILL.md) |

A pointer repeats the skill's `name` and `description` frontmatter, because Claude Code reads
those from this directory to decide when the skill applies. Keep them identical to the vendored
file. The body is ours: a pointer normally says to read and follow the vendored `SKILL.md`, but
follow what the agent-skills table says about the skill. `install-anti-slop-py` has deliberately
not been run in this repository, so its pointer's body tells the agent not to install anything,
to use the linter already vendored, and to read the install procedure only if the user
explicitly asks to install and confirms. Claude Code loads a skill whenever its description
matches, so a pointer that said "follow it exactly" would run the install uninvited. See
Session start in [AGENTS.md](../AGENTS.md#session-start).

---

## hooks/

| Hook | File | Runs |
|---|---|---|
| `SessionStart` | `hooks/session-start.sh` | on startup, resume, `/clear` and compaction |

`session-start.sh` prints the steps of Session start in [AGENTS.md](../AGENTS.md#session-start),
and Claude Code adds that output to the session's context before the first reply. It tells the
session to invoke the superpowers `test-driven-development` skill, and lists every `SKILL.md`
under `agent-skills/` by reading each one's frontmatter, so a skill added there needs no change
here. It flags a skill with no row in `agent-skills/README.md` as `UNDOCUMENTED`, and a row
whose `SKILL.md` is gone as `STALE ROW`, and it reminds the session to keep the documentation
set in step with the code. It prompts only. A hook cannot invoke a skill itself. The rules it prompts for live in
`AGENTS.md`. Change them there, and change this script only if the steps themselves change.

It is POSIX `sh`, run as `sh "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh"`. If it cannot
enter the project directory, or that directory has no `AGENTS.md` and `agent-skills/`, it prints
the reason to stderr and exits 1, rather than printing nothing and looking like a clean start.
Verified on macOS on 2026-09-25 by running the script directly, including both failure cases. Not verified on Windows, where Claude
Code needs Git Bash to run it.

---

## settings.json

Shared project settings, applied to everyone who trusts the folder. It holds three keys.
`extraKnownMarketplaces` and `enabledPlugins` register the superpowers plugin marketplace and
enable the plugin for this project. `hooks` registers the `SessionStart` hook above. It sets no
permissions or environment variables, and should stay that way unless the team decides
otherwise.

Enabling a plugin here does not install it. Each person installs it once. The command, and what
you are trusting when you run it, are in §1.10 of the
[project docs](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md), not here, so there is one copy.

---

## Adding a command

Write the procedure in [docs/workflows/](../docs/workflows/) first, then add a one-line pointer
here. The steps are in [docs/workflows/README.md](../docs/workflows/README.md).

## Adding a skill

Vendor the skill as a folder under [agent-skills/](../agent-skills/) with its `SKILL.md`. The
session-start hook finds it on the next session with no change here. To also put it in Claude
Code's skill list, add a pointer under `skills/` with the same frontmatter, and a row to the
table above.

## Related

- [AGENTS.md](../AGENTS.md) — how to work in this repository, read by every assistant
- [docs/workflows/](../docs/workflows/) — the canonical procedures
- [pull_request_template.md](../pull_request_template.md) — the PR checklist `/make-pr` appends
- [docs/project/COSC499-TEAM10-PROJECT-DOCS.md](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md)
  — the source of truth for the project
