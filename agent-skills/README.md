# agent-skills

> **This file is part of the documentation set**, the markdown files the team owns.
> The whole set is reviewed on every pull request and updated in the same PR when affected. Update this file
> whenever a skill is added, removed, updated to a new upstream version, or used differently.
> See §9.0 of [the source of truth](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md).
>
> This README is the only file here that is ours. Everything inside a skill's folder is
> vendored from upstream as-is and is **not** in the documentation set. Do not edit it to fit
> this repository. Put repository-specific rules in the table below or in `AGENTS.md`, which
> wins where it is stricter.

Skills vendored into this repository so that **every** AI agent can read them, whatever tool
runs it. Each skill is a folder holding a `SKILL.md`. Section "Session start" of
[AGENTS.md](../AGENTS.md#session-start) requires every agent to find each `SKILL.md` here and
read it in full before its first reply of a session, and in Claude Code the
[session-start hook](../.claude/hooks/session-start.sh) lists them automatically. Both find
skills by **searching this folder**, not by reading the table below. A skill dropped in here is
found by the next session even if nobody updates this file, but it is found as **undocumented**:
the hook marks it `UNDOCUMENTED`, and `AGENTS.md` tells every agent not to follow its procedure
until it has a row here, and to add that row in the current change after asking how it is used.
A row whose `SKILL.md` is gone is marked `STALE ROW`. Run `sh .claude/hooks/session-start.sh`
to check by hand.

| Skill | `SKILL.md` | Upstream | Version | Licence | Used here as |
|---|---|---|---|---|---|
| `test-driven-development` | [superpowers-tdd/SKILL.md](superpowers-tdd/SKILL.md) | [obra/superpowers](https://github.com/obra/superpowers), `skills/test-driven-development/` | 6.4.2 | MIT, [superpowers-tdd/LICENSE](superpowers-tdd/LICENSE) | **mandatory for every session**, see step 1 of Session start. Claude Code users with the superpowers plugin invoke the plugin's copy instead, and this one is for every other agent. |
| `install-anti-slop-py` | [anti-slop-py/skills/install-anti-slop-py/SKILL.md](anti-slop-py/skills/install-anti-slop-py/SKILL.md) | [TinyFrontier/anti-slop-py](https://github.com/TinyFrontier/anti-slop-py) | commit `86ea16d` | MIT, [anti-slop-py/LICENSE](anti-slop-py/LICENSE) | known to every agent, **deliberately not run**. Run it only when the team asks. The linter itself runs from [anti-slop-py/src/](anti-slop-py/src/), see Anti-slop in `AGENTS.md`. |

## Adding a skill

Do all of this in the same pull request.

1. Add the skill as a folder here, holding its `SKILL.md` and anything it references, copied
   unchanged from upstream. Include upstream's licence file. Do not vendor a skill whose
   licence does not allow redistribution.
2. Read every file you are adding before committing it. A skill is instructions that every
   agent in this repository will follow.
3. Add a row to the table above: name, path, upstream, the exact version or commit, licence,
   and how it is used here. If agents should know it but not run it, say so in the last
   column, as `install-anti-slop-py` does.
4. Check that the session-start hook lists it: `sh .claude/hooks/session-start.sh`. Nothing in
   the hook or in `AGENTS.md` needs to change for that.
5. If every session must load it regardless of the task, as with `test-driven-development`,
   also give it a step in Session start in [AGENTS.md](../AGENTS.md#session-start) and a box in
   the **Agent skills** section of [pull_request_template.md](../pull_request_template.md).
6. Optionally, to put it in Claude Code's skill list, add a pointer under
   [.claude/skills/](../.claude/skills/), as [.claude/README.md](../.claude/README.md)
   describes.
7. Review the rest of the documentation set as usual. The skill may change a rule stated
   elsewhere.

## Updating or removing a skill

- **Updating.** Copy the new upstream files over the old ones unchanged, read the diff, and
  update the version in the table. The copy of `test-driven-development` does not update when
  the plugin does: to refresh it, copy `SKILL.md` and `writing-good-tests.md` from the plugin's
  `skills/test-driven-development/`.
- **Removing.** Delete the folder and its row, and its `.claude/skills/` pointer if it has one.
  Search the documentation set for the skill's name and fix every mention. If it had its own
  step in Session start or a box in the pull request template, remove those too.
