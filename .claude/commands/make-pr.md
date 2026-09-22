Read [docs/workflows/make-pr.md](../../docs/workflows/make-pr.md) and follow it exactly.

That file is the canonical, tool-agnostic procedure and is the single source of truth for how
this repository opens pull requests. This command is only a pointer to it, so that Claude Code,
other AI agents, and people all follow the same rules.

Do not follow a remembered version of the procedure. Read the file. In particular it covers two
things that are easy to get wrong: the PR must target this fork rather than upstream, and the
contents of `pull_request_template.md` must be appended to the body by hand.
