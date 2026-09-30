Read [docs/workflows/make-pr.md](../../docs/workflows/make-pr.md) and follow it exactly.

That file is the canonical, tool-agnostic procedure and is the single source of truth for how
this repository opens pull requests. This command is only a pointer to it, so that Claude Code,
other AI agents, and people all follow the same rules.

Do not follow a remembered version of the procedure. Read the file. In particular it covers
four things that are easy to get wrong: the PR must target this fork rather than upstream, the
contents of `pull_request_template.md` must be appended to the body by hand, the Part A
receipts must be filled with bold answers backed by evidence, never with a claim about
something that did not happen, and the same Part A must be written into the student's weekly
log in `docs/logs/` and kept identical to the PR description.
