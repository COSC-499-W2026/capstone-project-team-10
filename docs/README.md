# Documentation

Project documentation for COSC 499 capstone team 10.

## Start here

**[project/COSC499-TEAM10-PROJECT-DOCS.md](project/COSC499-TEAM10-PROJECT-DOCS.md) is the
source of truth for this project.**

Setup (macOS and Windows), architecture, a module-by-module reference, the configuration
schema, and a catalogue of known bugs and traps. Read it before working on the code. When any
other document disagrees with it, that document is out of date — and when it disagrees with the
code, **the code wins and the file must be corrected.**

It is maintained under a standing rule: it must be derived from reading the source, and every
claim is marked either *Verified* (observed at runtime) or *Reasoned from code*. See its §2.

## Contents

| Folder | Contents |
|---|---|
| [project/](project/) | **Project documentation — the source of truth.** Setup, architecture, module reference, config schema, known bugs. |
| [contract/](contract/) | Team contract |
| [proposal/](proposal/) | Project proposal |
| [design/](design/) | UI mocks and design artifacts |
| [minutes/](minutes/) | Minutes from team meetings |
| [logs/](logs/) | Team and individual logs |

## Keeping it current

**Every markdown file in `docs/`, `tests/` and `utils/`, plus the root-level
[README.md](../README.md), [AGENTS.md](../AGENTS.md) and [CLAUDE.md](../CLAUDE.md), forms the
documentation set. The whole set is reviewed on every pull request and every implementation,
and whatever the change affects is updated in that same PR** — never as a follow-up, never as a
separate docs PR.

Reviewing a file and concluding it needs no change is fine. Not looking is not. If nothing in
the set needed changing, the PR description must say so.

The [pull request template](../pull_request_template.md) turns this into a per-file checklist
the reviewer signs off. [AGENTS.md](../AGENTS.md) carries the same rule for AI agents, and §9.0
of [the source of truth](project/COSC499-TEAM10-PROJECT-DOCS.md) is the canonical statement of
it.

The set cross-references itself, so if you change a rule stated in more than one file, update
every copy.

## Other documentation in this repository

These are inherited from upstream *brachify* and are useful but not authoritative:

| File | Role |
|---|---|
| [README-BRACHIFY.md](../README-BRACHIFY.md) | Upstream project README — user-facing overview and screenshots |
| [user_guide/Brachify User Manual.docx](../user_guide/Brachify%20User%20Manual.docx) | End-user manual. Authoritative on **clinical workflow and treatment-plan requirements**. |
| [virtual_environments_instructions.md](../virtual_environments_instructions.md) | Upstream conda guide. Windows-centric — see §1.2 of the project docs for macOS. |
| [notes/](../notes/) | Short upstream developer notes (Qt Designer workflow, exe build, pythonocc display tips) |
| [../README.md](../README.md) | The course's folder-structure template. Does not describe this code. |
