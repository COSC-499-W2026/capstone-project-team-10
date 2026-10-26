Read [docs/workflows/make-weekly-log.md](../../docs/workflows/make-weekly-log.md) and follow it exactly.

Arguments: `$ARGUMENTS`. The first is the week number, which names
`docs/logs/team/week-<N>.md`. The rest are the PRs the log covers, as numbers or as
`https://github.com/COSC-499-W2026/capstone-project-team-10/pull/<id>` URLs. If either is
missing, ask for it.

That file is the canonical, tool-agnostic procedure and is the single source of truth for how
this repository writes the team's weekly log, Part B. This command is only a pointer to it, so
that Claude Code, other AI agents, and people all follow the same rules.

Do not follow a remembered version of the procedure. Read the file. In particular, it has the
agent gather the evidence and then ask the user clarifying questions before writing anything,
and it records every comment the grader has made on a team log, so that the next one does not
lose marks for the same reason.
