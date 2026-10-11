# Documentation

Project documentation for COSC 499 capstone team 10.

## Start here

**[project/COSC499-TEAM10-PROJECT-DOCS.md](project/COSC499-TEAM10-PROJECT-DOCS.md) is the
source of truth for this project.**

Setup (Windows, macOS and Linux, all installing the same dependencies), architecture, a module-by-module reference, the configuration
schema, and a catalogue of known bugs and traps. Read it before working on the code. When any
other document disagrees with it, that document is out of date — and when it disagrees with the
code, **the code wins and the file must be corrected.**

It is maintained under a standing rule: it must be derived from reading the source, and every
claim is marked either *Verified* (observed at runtime) or *Reasoned from code*. See its §2.

**New to the code? Read [project/COSC499-BRACHIFY-INIT-DOCS.md](project/COSC499-BRACHIFY-INIT-DOCS.md)
alongside it.** The init guide walks through every folder and file of the code as it came from
upstream, before Team 10 changed `src/`, assuming no background. It uses real values from the two
sample plans, with drawings of the model. It is a baseline: it is not rewritten when the code
changes, so a section that a change makes out of date carries a note pointing to the new
documentation.

## Contents

| Folder | Contents |
|---|---|
| [project/](project/) | **Project documentation — the source of truth.** Setup, architecture, module reference, config schema, known bugs. Also the init guide, a plain-language walkthrough of the inherited code. |
| [architecture/](architecture/README.md) | **The architecture map.** System architecture, UML, DFD level 0, DFD level 1, the build that renders them, a zoom page, what Team 10 has added, the known gaps in the existing code, and separate projected diagrams based on the proposal. |
| [contract/](contract/) | Team contract |
| [proposal/](proposal/) | Project proposal |
| [design/](design/) | UI mocks and design artifacts |
| [minutes/](minutes/) | Minutes from team meetings |
| [logs/](logs/) | Weekly individual logs (Part A, written by `/make-pr`) and team logs (Part B) |
| [workflows/](workflows/) | **Tool-agnostic procedures** any AI agent or person can follow: how to commit, how to open a PR |

## Keeping it current

**Every markdown file the team owns forms the documentation set**, listed in §9.0 of
[the source of truth](project/COSC499-TEAM10-PROJECT-DOCS.md). The weekly log entries in
[logs/](logs/) are the exception, since they record past work. **The whole set is reviewed on
every pull request and every implementation, and whatever the change affects is updated in
that same PR** — never as a follow-up, never as a separate docs PR. Files inherited from
upstream *brachify* are never edited; §9.0 lists those too.

Reviewing a file and concluding it needs no change is fine. Not looking is not. If nothing in
the set needed changing, the PR description must say so.

The [pull request template](../pull_request_template.md) turns this into a per-file checklist
the author fills in on every PR. [AGENTS.md](../AGENTS.md) carries the same rule for AI agents, and §9.0
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
| [virtual_environments_instructions.md](../virtual_environments_instructions.md) | Upstream conda guide. Windows-centric — see §1.2 of the project docs for macOS and Linux, and §1.1 for adding a dependency. |
| [notes/](../notes/) | Short upstream developer notes (Qt Designer workflow, exe build, pythonocc display tips) |
| [../README.md](../README.md) | The course's folder-structure template. Does not describe this code. |
