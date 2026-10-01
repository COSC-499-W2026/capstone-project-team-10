Read [docs/workflows/make-pr.md](../../docs/workflows/make-pr.md) and follow it exactly.

That file is the canonical, tool-agnostic procedure and is the single source of truth for how
this repository opens pull requests. This command is only a pointer to it, so that Claude Code,
other AI agents, and people all follow the same rules.

Do not follow a remembered version of the procedure. Read the file. In particular it covers
five things that are easy to get wrong: the PR must target this fork rather than upstream, the
contents of `pull_request_template.md` must be appended to the body by hand, Part A must always
be filled in, on every PR, with bold answers backed by evidence and never with a claim about
something that did not happen, the same Part A must be written into the student's weekly log in
`docs/logs/` and kept identical to the PR description, and a box that does not apply is ticked
with **N/A**, not left blank.
