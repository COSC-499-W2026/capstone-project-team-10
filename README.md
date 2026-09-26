# Project-Starter
Please use the provided folder structure for your project. You are free to organize any additional internal folder structure as required by the project. 

```
.
├── docs                    # Documentation files
│   ├── contract            # Team contract
│   ├── proposal            # Project proposal 
│   ├── design              # UI mocks
│   ├── minutes             # Minutes from team meetings
│   ├── logs                # Team and individual Logs
│   └── ...          
├── src                     # Source files (alternatively `app`)
├── tests                   # Automated tests 
├── utils                   # Utility files
└── README.md
```

Please use a branching workflow, and once an item is ready, do remember to issue a PR, review, and merge it into the master branch.
Be sure to keep your docs and README.md up-to-date.

## Documentation

**[docs/project/COSC499-TEAM10-PROJECT-DOCS.md](docs/project/COSC499-TEAM10-PROJECT-DOCS.md) is
the source of truth for this project.** Setup, architecture, module reference, configuration
schema, and known bugs. Read it before working on the code.

The section above this one is the course's folder-structure template and does not describe the
application. The application is *brachify*; see
[README-BRACHIFY.md](README-BRACHIFY.md) for the user-facing overview.

### Keeping documentation current

**Every markdown file the team owns forms the documentation set: every markdown file in
[docs/](docs/), [tests/](tests/), [utils/](utils/) and [.claude/](.claude/), plus this README,
[AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md),
[pull_request_template.md](pull_request_template.md) and
[agent-skills/README.md](agent-skills/README.md). The whole set is reviewed on every pull
request and every implementation, and whatever the change affects is updated in that same PR**
— never as a follow-up, never as a separate docs PR. The code is the source of truth: where a
document disagrees with it, the document is wrong.

Files inherited from upstream *brachify* are **never** edited: `README-BRACHIFY.md`,
`pull_request_template_brachify.md`, `virtual_environments_instructions.md`, `notes/`,
`user_guide/`, `3D Models and Templates/`, `Images/`, `LICENSE`, `requirements.txt` and the
sample DICOM folders. The full classification is in
[AGENTS.md](AGENTS.md#what-is-ours-and-what-is-inherited).

Reviewing a file and concluding it needs no change is fine. Not looking is not. If nothing in
the set needed changing, the PR description must say so.

[pull_request_template.md](pull_request_template.md) turns this into a per-file checklist the
reviewer signs off. [AGENTS.md](AGENTS.md) carries the same rule for AI agents. §9.0 of the
source of truth is the canonical statement of it.

## Team Contract

The team contract for Team 10 lives here:
[Team 10 Contract](https://docs.google.com/document/d/1ftXKwOM9rbiUOhMnXEU4DUBSXVl1Yzyb3JICByf4UcE/edit?usp=sharing)
