# CLAUDE.md

This project keeps its agent guidance in [AGENTS.md](AGENTS.md), the cross-tool standard, so
that every agent reads the same instructions. The line below imports it.

@AGENTS.md

## Documentation set

**This file is part of the documentation set**, the markdown files the team owns. The whole
set is reviewed on every pull request and every implementation, and whatever the change affects
is updated in that same PR. Reviewing a file and concluding it needs no change is fine. Not
looking is not.

This file is only a pointer, so it changes rarely — update it when the agent-guidance entry
point itself changes. Check it anyway.

The canonical statement of the rule, with the full file table and the upstream files that are
never edited, is §9.0 of
[docs/project/COSC499-TEAM10-PROJECT-DOCS.md](docs/project/COSC499-TEAM10-PROJECT-DOCS.md),
restated for agents in [AGENTS.md](AGENTS.md) and enforced per file by
[pull_request_template.md](pull_request_template.md).
