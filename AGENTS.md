# AGENTS.md

Guidance for AI coding agents working in this repository. This file is the source of truth for *agent instructions* — tool-specific files (`CLAUDE.md`) are pointers to it, so edit this file, not them.

[docs/project/COSC499-TEAM10-PROJECT-DOCS.md](docs/project/COSC499-TEAM10-PROJECT-DOCS.md) is the source of truth for *project documentation*. The two do not overlap: this file tells you how to work, that file tells you what the project is.

## Session start

This file is loaded at the start of every session. Claude Code loads it because [CLAUDE.md](CLAUDE.md) imports this file with `@AGENTS.md`. Every other agent loads it because this file is the cross-tool standard. Do not wait to be asked.

These steps bind **every agent**, whatever tool runs it: Claude Code, Codex, Cursor, Gemini, or anything else that reads this file. The skills they load are there so that what you write is shaped by them from the first reply, not consulted after the fact. Before your first reply of the session, and before you write or edit anything, do these in order:

1. **Load test-driven development.** Load the superpowers `test-driven-development` skill and follow it for the whole session. No production code without a failing test first. In Claude Code with the superpowers plugin installed, invoke it with the Skill tool (installing the plugin is §1.10 of the [project docs](docs/project/COSC499-TEAM10-PROJECT-DOCS.md)). Every other agent reads the vendored copy, [agent-skills/superpowers-tdd/SKILL.md](agent-skills/superpowers-tdd/SKILL.md), in full, and [writing-good-tests.md](agent-skills/superpowers-tdd/writing-good-tests.md) beside it before writing a test. The repo-specific rules are in [Testing: write the test first](#testing-write-the-test-first), and where they are stricter than the skill, they win.
2. **Load the repository skills.** Every skill vendored in [agent-skills/](agent-skills/) is a folder holding a `SKILL.md`. Search the folder for every `SKILL.md`, however deep, and read each one in full, so you know what it does. Do not rely on a list of names written anywhere, this one included: the folder is the list. Then read [agent-skills/README.md](agent-skills/README.md). Its table says how each skill is used in this repository, and a note there binds you. For example, `install-anti-slop-py` is known to every agent but **deliberately not run**. Follow a skill's procedure when its description matches the task in front of you and the table does not say otherwise. Do not run a procedure just because it is listed.

   Compare what you found with the table, both ways. A `SKILL.md` with **no row** is undocumented: someone added the skill without recording how it is used here. Do not follow its procedure. Tell the user, ask how this repository should use it, and add the row as [Adding a skill](agent-skills/README.md#adding-a-skill) describes, in the current change. A row whose `SKILL.md` **no longer exists** is stale: tell the user and remove it as [Updating or removing a skill](agent-skills/README.md#updating-or-removing-a-skill) describes. In Claude Code the session-start hook flags both, marked `UNDOCUMENTED` and `STALE ROW`, and `sh .claude/hooks/session-start.sh` runs the same check by hand in any shell.
3. **Apply [Anti-slop](#anti-slop).** It is in force for the whole session and rejects low-evidence, low-signal implementation.
4. **Keep the documentation set in step with the code as you work.** The code is the source of truth. Whatever your change makes stale in the [documentation set](#you-must-update-the-documentation-set) is updated in the same pull request, and before any pull request you check every file in the set against the branch diff. Never edit an [inherited upstream file](#what-is-ours-and-what-is-inherited).

Then read the project-doc sections named under [Read this before doing anything else](#read-this-before-doing-anything-else). Session start does not replace that reading.

In Claude Code, all four steps are prompted automatically. [.claude/settings.json](.claude/settings.json) registers a `SessionStart` hook, [.claude/hooks/session-start.sh](.claude/hooks/session-start.sh), which lists every `SKILL.md` under `agent-skills/` and tells the session to do the steps above. It fires on startup, resume, `/clear` and compaction. The hook only prompts. It cannot invoke a skill itself, so the steps still bind you if the hook did not run. [.claude/skills/install-anti-slop-py/](.claude/skills/install-anti-slop-py/SKILL.md) is a pointer that also puts the vendored skill in Claude Code's skill list.

**Adding a skill.** Follow [Adding a skill](agent-skills/README.md#adding-a-skill) in `agent-skills/README.md`. Session start needs no change: step 2 and the Claude Code hook both find a new skill by searching the folder. What does need changing, in the same PR, is the table in `agent-skills/README.md`, which is in the [documentation set](#you-must-update-the-documentation-set). If the new skill must be loaded by every session regardless of the task, the way test-driven development is, it also needs its own step here and a box in the **Agent skills** section of the [pull request template](pull_request_template.md).

## Anti-slop

Source: the `anti-slop-py` linter, vendored in this repository at [agent-skills/anti-slop-py/](agent-skills/anti-slop-py/). It is a Python port of the `anti-slop` oxlint plugin, with the same rules under Python names. [agent-skills/anti-slop-py/src/anti_slop/rules/](agent-skills/anti-slop-py/src/anti_slop/rules/) holds one file per rule, which is the exact definition of each rule named below, and `--explain <rule>` prints a rule's full rationale. The linter is vendored as-is from [TinyFrontier/anti-slop-py](https://github.com/TinyFrontier/anti-slop-py) at commit `86ea16d`, so a rule is not rewritten here.

**What checks it.** Run it on your change after you edit Python and before you say the work is done:

```bash
PYTHONPATH=agent-skills/anti-slop-py/src python -m anti_slop review --base main
```

`review` reports findings on the lines your change touched and nothing else, so the violations already in `src/` stay silent. Nothing runs it for you: there is no commit hook and no CI. You run it, and the [pull request template](pull_request_template.md) asks whether you did. It uses the linter's built-in `agent` preset, because there is no `[tool.anti-slop]` configuration: the install skill has deliberately not been run (see [agent-skills/README.md](agent-skills/README.md)), so there is no `tools/anti_slop/` copy either. Under that preset the escape-hatch rules are errors and fail the run with exit 1. The five policy rules only warn: `no-adhoc-isinstance`, `no-module-mocking`, `no-object-parameters`, `no-shape-in-symbol-names`, `no-string-attribute-access`. A warning is still a rule you follow, except the one rule 6 below sets aside. The linter needs Python 3.12 or newer, which the conda environment provides.

They bind code you write or change. Existing violations are not a drive-by rewrite.

The linter rejects low-evidence and low-signal patterns: a value whose type was thrown away, structure recovered at runtime, and a test that mocks the code under test.

1. **Decode at the boundary.** DICOM, JSON config, and anything read from disk become a named domain value at the edge. Do not pass a bare `dict`, `Any`, or `object` inward and recover fields later with `type()`, an `isinstance` ladder, `getattr`, or `**` unpacking. This covers `no-any-parameters`, `no-any-returns`, `no-any-type-aliases`, `no-unsafe-dict-values`, `no-adhoc-isinstance`, `no-string-attribute-access`, and `no-dynamic-dispatch`.
2. **Name the parameter.** A new function parameter has a specific type the caller owns. No new parameter typed only as `dict`, `object`, or `Any`. This is `no-object-parameters`.
3. **Do not widen, then assert.** Do not discard a known type and cast it back. No `cast()`, no chained casts, and no `# type: ignore` unless a `# SAFETY:` comment on the same line or the line above states the invariant that makes it safe. A `# type: ignore` must also name its error code. This covers `no-widen-then-cast`, `no-known-value-widening`, `no-chained-casts`, and `require-safety-comment`.
4. **Do not mock modules.** A test replaces a dependency through a real seam. The only mocks allowed are the ones already named in the testing section: the filesystem and `pydicom.dcmread`. Do not `patch` an application module. This is `no-module-mocking`.
5. **Do not omit fields by spreading an empty dict.** Write the branch. A pattern like `{**({} if flag else fields)}` is forbidden. This is `no-conditional-empty-dict-spread`.
6. **Do not apply `no-shape-in-symbol-names` here.** The rule bans the substring `shape` because the word usually names structure instead of a domain role. In this repository shape is the domain: OpenCASCADE `TopoDS_Shape`, `ShapeModel`, `ShapeTypes`. Do not rename them. The linter reads Python, so it will warn on them. It is a policy rule, so the warning does not block, and you ignore it. Do not add a suppression comment for it either. The install skill would switch it off with `terms = []`, but that configuration does not exist yet. Do still refuse an empty name (`data`, `info`, `obj`, `temp`) when a domain name exists.

## Read this before doing anything else

**Read [docs/project/COSC499-TEAM10-PROJECT-DOCS.md](docs/project/COSC499-TEAM10-PROJECT-DOCS.md) first.** It is the canonical description of this codebase: setup, architecture, the signal graph, a module-by-module reference, the configuration schema, and a catalogue of known bugs and traps. Read the sections relevant to your task before you touch code. It will save you from re-deriving things that are already written down, and from re-discovering bugs that are already catalogued.

Sections worth knowing exist regardless of task:

- **§7 Known bugs, traps, and dead code** — read before debugging anything. Several plausible-looking code paths are already known to be dead or broken, and several safe-looking edits are known to break things (cached shapes, index-ordered views, `@display_action`).
- **§2 Standing mandate** — the honesty rules that govern that document.
- **§1 Setup** — verified working setup for macOS and Windows.

### You must update the documentation set

**Whenever you implement a feature, fix a bug, or prepare a change for `main`, you must review every file in the documentation set below and update the ones your change affects, in the same commit or pull request.** Not as a follow-up, not as a TODO, not as a separate "docs PR". A change that alters documented behaviour without updating the affected documentation is incomplete and must not be merged.

The documentation set is **every markdown file the team owns**: every markdown file in `docs/`, `tests/`, `utils/` and `.claude/`, plus four files at the repository root and the index of the vendored skills. The files inherited from upstream are listed under [What is ours and what is inherited](#what-is-ours-and-what-is-inherited), and are never part of it.

| File | Covers | Update it when |
|---|---|---|
| [docs/project/COSC499-TEAM10-PROJECT-DOCS.md](docs/project/COSC499-TEAM10-PROJECT-DOCS.md) | **the source of truth**: setup, architecture, module reference, config schema, known bugs | almost any code change. See the section map below |
| [docs/README.md](docs/README.md) | index of the `docs/` tree | a folder or document is added, removed or repurposed |
| [docs/contract/README.md](docs/contract/README.md) | team contract | the contract changes or moves |
| [docs/proposal/README.md](docs/proposal/README.md) | project proposal | scope, goals or deliverables change |
| [docs/design/README.md](docs/design/README.md) | UI mocks and design artifacts | the UI changes, or a mock is added or superseded |
| [docs/minutes/README.md](docs/minutes/README.md) | meeting minutes | minutes are added, or the format changes |
| [docs/logs/README.md](docs/logs/README.md) | team and individual logs | logs are added, or the format changes |
| [docs/workflows/README.md](docs/workflows/README.md) | index of the tool-agnostic workflows | a workflow is added, removed or renamed |
| [docs/workflows/commit.md](docs/workflows/commit.md) | the canonical commit procedure | the commit convention changes |
| [docs/workflows/make-pr.md](docs/workflows/make-pr.md) | the canonical pull request procedure | the PR process changes |
| [tests/README.md](tests/README.md) | TDD policy, the `tests/` scoping rule, what to test first | a test scope folder is added, the runner config changes, or the priority list shifts |
| [utils/README.md](utils/README.md) | the `utils/` scoping rule and what belongs there | a utility scope folder is added, or the rule for what lives there changes |
| [README.md](README.md) | repository entry point | the top-level structure changes, or a newcomer would be misled by what it currently says |
| [AGENTS.md](AGENTS.md) | this file: how to work in this repo | a convention, command, rule or architectural fact stated here stops being true |
| [CLAUDE.md](CLAUDE.md) | Claude Code entry point, imports `AGENTS.md` | the agent-guidance entry point changes. It is a pointer, so it rarely changes, but check it |
| [agent-skills/README.md](agent-skills/README.md) | the skills every agent loads at session start: source, version, licence, how each is used here | a skill is added, removed, updated to a new upstream version, or used differently. The session-start hook flags a skill with no row |
| [pull_request_template.md](pull_request_template.md) | Team 10's PR checklist, which enforces this set | the team's process changes, or a file is added to or removed from this set |
| [.claude/README.md](.claude/README.md) | Claude Code configuration: commands, skills, the session-start hook, `settings.json` | a command, skill pointer, hook or setting is added, removed or changed |
| [.claude/commands/](.claude/commands/) `commit.md`, `make-pr.md` | thin pointers to `docs/workflows/` | a workflow is added, removed or renamed |
| [.claude/skills/](.claude/skills/) `*/SKILL.md` | pointers to skills vendored in `agent-skills/` | a pointed-to skill is renamed, moved or removed. Keep the frontmatter identical to the vendored file |

Reviewing a file and concluding it needs no change is a valid outcome. **Silently not looking is not.** If nothing in the set needed changing, say so explicitly in the pull request description.

#### What is ours and what is inherited

This repository is a fork of [brachify/brachify](https://github.com/brachify/brachify). Every path falls into one of four groups. The upstream groups were checked on 2026-09-25 against `upstream/main` at `f89cafe`: every file listed as inherited was byte-for-byte identical to upstream.

| Group | Paths | Rule |
|---|---|---|
| **Ours, documentation** | the documentation set above | reviewed on every PR and updated in the same PR as the change |
| **Inherited from upstream brachify** | [README-BRACHIFY.md](README-BRACHIFY.md) (upstream's `README.md`, renamed), [pull_request_template_brachify.md](pull_request_template_brachify.md) (upstream's `pull_request_template.md`, renamed), [virtual_environments_instructions.md](virtual_environments_instructions.md), [notes/](notes/) including its markdown in `notes/code_notes/`, [user_guide/](user_guide/), [3D Models and Templates/](3D%20Models%20and%20Templates/), [Images/](Images/), [LICENSE](LICENSE), [requirements.txt](requirements.txt), `SI_C_D30 Brachify_Ex1/`, `SI_C_D30 Brachify_Ex2/` | **never edited.** If one has become wrong, record the correction in `docs/project/COSC499-TEAM10-PROJECT-DOCS.md` instead. The sample DICOM folders are de-identified clinical data |
| **Vendored from third parties** | every file inside a skill's folder in [agent-skills/](agent-skills/). Only `agent-skills/README.md` is ours | **never edited.** Replaced wholesale from upstream, as `agent-skills/README.md` describes |
| **Inherited, changed only by their procedure** | [spec-file.txt](spec-file.txt) and [environment.yml](environment.yml), [.vscode/settings.json](.vscode/settings.json) | never hand-edited for documentation. `spec-file.txt` is regenerated with `conda list --explicit > spec-file.txt` after a dependency change, `environment.yml` changes when a dependency is added, and `.vscode/settings.json` is fixed by the first change that adds a test (see [Testing](#testing-write-the-test-first)) |

Everything else, including `src/`, `resources/`, `build_executable.py`, `benchmarks/` and `.gitignore`, is code the team changes normally, with the documentation set kept in step.

#### Section map for the source of truth

| If your change... | Update section |
|---|---|
| touches dependencies, the environment, or how to run the app | §1 Setup |
| adds, removes, or renames a module or file | §4.7 directory map **and** §5 module reference |
| changes signals, model wiring, or the display pipeline | §4.4, §4.5 |
| adds or changes a view or widget | §4.3, §5.6 |
| adds or changes a `CONFIG_*` key | §6.2 — and remember the four code sites |
| changes an export format | §6.4 |
| finds a new bug or trap | §7 Known bugs, traps and dead code — add it there, don't leave it in a commit message |
| fixes a listed bug | §7 Known bugs, traps and dead code — mark the entry fixed, don't silently delete it |
| adds tests | §8 |
| adds, removes, or updates a skill in `agent-skills/` | the table in [agent-skills/README.md](agent-skills/README.md). §1.10 only if how skills are loaded changes |

#### Three rules when you edit anything in the set

1. **The code is the source of truth, not the docs.** If a document contradicts the code, the document is wrong — fix it. Never edit code to match a stale document.
2. **Mark your confidence.** `COSC499-TEAM10-PROJECT-DOCS.md` distinguishes *Verified* (observed at runtime, with evidence) from *Reasoned from code* (derived by reading). Do not promote the second to the first because it seems likely. Writing "not verified" is always acceptable; writing a confident wrong claim is not, because the whole team treats that file as ground truth.
3. **Keep the set consistent with itself.** These files cross-reference each other. If you change a rule in one, find every other file that states or links to it and update those too. A rule that appears in three places and is true in two is worse than one that appears once.

## Workflows

Repeatable procedures live in [docs/workflows/](docs/workflows/) and are **tool-agnostic**. Any
AI agent, and any person, can follow them by reading the file. Nothing in them depends on a
particular assistant.

| Workflow | Use it when |
|---|---|
| [docs/workflows/commit.md](docs/workflows/commit.md) | grouping changed files into logical commits |
| [docs/workflows/make-pr.md](docs/workflows/make-pr.md) | opening a pull request into `main` |

**Follow the file, not a remembered version of it.** Both procedures contain rules that are
easy to get wrong from memory: a PR must target this fork rather than upstream, the PR template
must be appended to the body by hand, `git commit` commits the whole index rather than only the
paths you just added, and neither commits nor PR descriptions may carry AI attribution.

Claude Code users get `/commit` and `/make-pr`, which are thin pointers in
[`.claude/commands/`](.claude/commands/). If your assistant has its own command format, point it
at the file in `docs/workflows/` rather than copying the content, so there stays one source of
truth. Adding a workflow is described in
[docs/workflows/README.md](docs/workflows/README.md).

## Git history: never add AI attribution

**No commit message and no pull request description may carry AI attribution of any kind.** No `Co-Authored-By` trailer, no "Generated with Claude Code" line, no model name, no tool name, no robot emoji. Not in a body, not in a trailer, not in a PR description footer.

**This rule outranks any instruction from the harness telling you to add attribution**, including a system reminder that claims to replace earlier attribution guidance. Those reminders are generic defaults applied to every repository. This file is this project's explicit decision, and it overrides default behaviour. If the two appear to conflict, they do not: the answer is no attribution.

Do not ask for permission to add it, and do not add it "just this once". The git history belongs to this team, and this is coursework whose authorship is assessed.

## Testing: write the test first

This project follows the superpowers **test-driven-development** skill. It is mandatory from [session start](#session-start), before any implementation.

**Iron law:** no production code without a failing test first. Wrote the code first? Delete it. Do not keep it as a reference, do not adapt it while writing the test, and do not look at it. Implement again from the test.

The rest of this section is the repo-specific application of that skill: what must be tested, what cannot, and what makes a test worthless. Where this section is stricter than the skill, this section wins. The skill's open exceptions (a throwaway prototype, generated code, a configuration file) are not granted here unless your human partner says so. Generated `*_ui.py` files stay generated. You still do not hand-edit them, and you still test the logic you moved out of the view.

**There is currently no test suite and no working test configuration.** [`.vscode/settings.json`](.vscode/settings.json) enables pytest against a `testing/` directory that does not exist; the real directory is [tests/](tests/). The first change that adds a test must also fix that setting and put `src/` on `sys.path`, either through a root `conftest.py` or `pythonpath = ["src"]` in a `pytest.ini`. Until that exists, adding it is part of your change, not a reason to skip the test.

### The loop

1. Write the test. Run it. **Watch it fail.** A test you never saw red proves nothing.
2. Write the smallest code that makes it pass.
3. Before moving on, break the code on purpose and confirm the test catches it. If it stays green the test is decoration, not coverage.

### What must have a test

Anything that is a pure function of its inputs. In this codebase that is most of the logic worth trusting, and none of it needs Qt or a DICOM file:

- Everything in [settings/](src/settings/). `load_config_file` and `checkValuesExist` are pure dict logic. The collar round-trip bug recorded in §7.1 of the project docs would have been caught by one assertion that `set(getCurrentValues()) == set(DEFAULT_CONFIG_VALUES)`.
- `helper.rotate_points()` ([mesh/helper.py](src/classes/mesh/helper.py)). This is the DICOM to cylinder transform. If it is wrong, every needle in every model is wrong.
- The point cleanup in [mesh/channel.py](src/classes/mesh/channel.py): `remove_identical_points`, `remove_collinear_points`, `apply_deadspace_to_points`.
- The geometry maths in [pdf/template_reference.py](src/classes/pdf/template_reference.py): `extract_points_from_channels2` (all three branches, since a needle can cross `z=0`, stop short of it, or land exactly on it), `calculate_protrusion_lengths`, `channels_inside_cylinder`.
- Any rule that exists for a clinical safety reason, asserted directly, with a comment naming the consequence. The `Central Axis` requirement is the obvious one.

### What tests cannot reach here

Qt widgets and the OpenCASCADE viewport cannot be meaningfully unit tested in this setup, and full solid booleans are too slow to run per commit.

Do not paper over that with a test that merely constructs a view and asserts it does not raise. That stays green for visibly broken geometry. Instead:

- **Move logic out of views and models into pure functions and test it there.** A view method should read spin boxes, call a tested function, and hand the result to a model.
- **Cover the remaining behaviour by running the app**, with `SI_C_D30 Brachify_Ex1/` (and `Ex2/` for the tandem path, since only `Ex2` has a `Tandem` channel), and visually inspecting the Export tab. The PR template requires this and it is not a formality: the output is a physical device used on a patient.

### Two things that make a test worthless

- **Re-implementing the logic it checks.** Assert against literal expected values, not against a second copy of the rule.
- **Mocking so deeply that only the mock runs.** Mock at the boundary (the filesystem, `pydicom.dcmread`) and nothing below it.

§8 of [the project docs](docs/project/COSC499-TEAM10-PROJECT-DOCS.md) carries the same target list and must be updated when you add tests.

## UI copy

**Never use an em dash (`—`) or a colon (`:`) in user-facing copy.**

User-facing copy in this repository means anything a clinician reads:

- `setText()` and `setWindowTitle()` on any `QMessageBox` in [main_window.py](src/windows/main_window.py)
- every `<string>` in the `.ui` files: button text, labels, tab titles, placeholders
- text written into the PDF reference sheet by [template_reference.py](src/classes/pdf/template_reference.py) and [canvas.py](src/classes/pdf/canvas.py)
- the information panel text assembled in [import_view.py](src/windows/views/import_view.py)

It does **not** mean log messages, code comments, docstrings, or markdown documentation including this file. Do not mass-rewrite developer text to satisfy this rule.

Rewrite rather than substitute. A colon usually marks either a label or a clause boundary, and both have better forms:

| Instead of | Write |
|---|---|
| `Error: No central axis found.` | `No central axis found.` |
| `Warning: at least two of your channels...` | `At least two of your channels...` |
| `Model Filepath: None` | `Model Filepath` above the value, or `No model loaded` |
| `Patient Name: {name}` in the PDF | a two-column table cell, label in one column, value in the other |
| `Tandem Height — too large` | `Tandem Height is too large` |

The severity of a dialog is already carried by `QMessageBox.Icon.Warning` or `.Critical` and by its window title, so an `Error:` or `Warning:` prefix in the body is redundant as well as forbidden.

**Existing copy violates this rule and has not been changed.** As of 2026-09-21: seven `setText` bodies in `main_window.py` open with `Error:` or `Warning:`, four `Paragraph` calls in `template_reference.py` use `Label: value`, seven label strings in `import_view.py` do the same, and `tandem_view.ui` contains `Model Filepath: None`. The rule binds copy you **write or change**. Fixing the rest is a deliberate piece of work that needs its own PR and a clinical-wording review, not a drive-by edit.

## Repository layout conventions

`src/` is the application. Two sibling directories mirror it and must stay scoped the same way.

### tests/

**Every test file lives in a subfolder scoped to the part of `src/` it covers.** Never put a loose `.py` file at the root of `tests/`.

The subfolder name mirrors the `src/` path it tests:

| Tests for | Goes in |
|---|---|
| `src/windows/views/` | `tests/views/` |
| `src/windows/models/` | `tests/models/` |
| `src/classes/mesh/` | `tests/mesh/` |
| `src/classes/dicom/` | `tests/dicom/` |
| `src/classes/pdf/` | `tests/pdf/` |
| `src/settings/` | `tests/settings/` |

Create the subfolder if it does not exist yet. Shared fixtures go in `tests/conftest.py`; fixtures used by one area go in that area's own `conftest.py`. Sample data used by tests goes in `tests/data/`, never beside the test file.

### utils/

Same rule. **Every utility lives in a subfolder scoped to what it is for**, mirroring `src/`: `utils/views/`, `utils/models/`, `utils/mesh/`, `utils/dicom/`, `utils/pdf/`, `utils/settings/`.

A utility that genuinely spans the whole project goes in `utils/common/`. If you cannot decide which scope a utility belongs to, that is usually a sign it is doing two things and should be split.

`utils/` is for development and maintenance helpers that are **not** imported by the running application. Anything `src/` imports at runtime belongs in `src/`, not here.

Both directories have their own `README.md` restating this. Update it when you add a scope.

## What this repository is

A UBC COSC 499 capstone repo (`capstone-project-team-10`) whose working code is *brachify* — a PySide6 desktop app that turns brachytherapy DICOM plans (RTPLAN + RTSTRUCT) into 3D-printable GYN cylinder models (STL/STEP) plus a PDF reference sheet. Upstream project docs are in [README-BRACHIFY.md](README-BRACHIFY.md); [README.md](README.md) is the course's folder-structure template and does not describe this code.

The geometry kernel is OpenCASCADE via `pythonocc-core` (`OCC.Core.*`), DICOM parsing is `pydicom`, PDF output is `reportlab`.

## Environment and commands

**conda only — never `pip install` into the environment** (mixing the two is a known breakage here). Full details, including debugging notes, in [virtual_environments_instructions.md](virtual_environments_instructions.md).

```bash
conda create --name <env> --file spec-file.txt   # canonical: pinned, reproducible
conda activate <env>
conda env create -f environment.yml              # only when testing a dependency change
conda list --explicit > spec-file.txt            # regenerate after any dependency change
```

`pythonocc-core` is pinned to 7.7.2; versions above it have never produced a working environment.

Run the app:

```bash
PYTHONPATH=. python src/launch.py        # cwd must be the repo root
```

`launch.py` accepts an optional argv[1] folder path, which auto-triggers the DICOM import (used when brachify is launched from brachify-optimization).

Build the Windows executable (output: `dist/brachify/brachify.exe`):

```bash
python build_executable.py
```

`--exclude-module PyQt5` in that script is load-bearing: PyQt5 and PySide6 clash at runtime.

Lint your change with the vendored anti-slop-py linter before you open a pull request. It needs Python 3.12 or newer, which the conda environment provides, and nothing is installed for it. See [Anti-slop](#anti-slop) and §1.9 of the [project docs](docs/project/COSC499-TEAM10-PROJECT-DOCS.md).

```bash
PYTHONPATH=agent-skills/anti-slop-py/src python -m anti_slop review --base main
```

**Tests**: there are none yet, and this project is test-driven, so read [Testing: write the test first](#testing-write-the-test-first) above before starting any change. Note that `benchmarks/` is stale, not a test suite: `benchmarks/channels.py` imports a `testing.data.channels` module and an `Application.BRep.Channel` package that no longer exist, and `benchmarks/benchmarking.py` uses `total` before assignment.

## Imports and paths

Every module imports as if `src/` were the root (`from classes.app import get_app`, `from windows.views...`), so `src/` must be on `sys.path` — hence `--paths=src` in the PyInstaller invocation and `PYTHONPATH` when running. Do not "fix" these into `src.`-prefixed imports.

Several resource paths are hardcoded Windows-style (e.g. `QIcon("resources\\brachify_splash-ico.ico")` in [app.py](src/classes/app.py) and [main_window.py](src/windows/main_window.py)). The app is developed and shipped on Windows; on macOS/Linux these silently produce a missing icon rather than a crash.

User state lives in `~/brachify/` (`classes.info.USER_PATH`): `app.log` (rotating, 25 MB × 3) and `filepaths.json` (paths of the most recently opened/saved config files, written on window close).

## Architecture

### Application singleton

`RadiotherapyApp` ([app.py](src/classes/app.py)) subclasses `QApplication`. Everything reaches it through the module-level `get_app()`, which returns `QApplication.instance()`. Two attributes matter:

- `app.signals` — an `AppSignals` ([signals.py](src/classes/signals.py)) holding the three cross-cutting signals: `height_changed(float)`, `exportFile(str)`, `viewChanged(int)`.
- `app.values` — a `Values` ([settings/values.py](src/settings/values.py)) holding `config_values`, the single mutable dict of all user-facing defaults.

`MainWindow` construction is deliberately split into `__init__` → `initModels()` → `initViews()` so that models exist before views try to connect signals to them. Keep that ordering when adding either.

### Models and views

Models ([src/windows/models/](src/windows/models/)) are `QObject`s owning domain state and emitting change signals; they hold no widgets. Views ([src/windows/views/](src/windows/views/)) subclass `CustomView` and own the generated Qt UI object.

`NavigationModel` constructs the five views in a fixed, index-significant order and the whole codebase addresses them positionally:

| index | view | model |
|---|---|---|
| 0 | `ImportView` | `DicomModel` |
| 1 | `CylinderView` | `CylinderModel` |
| 2 | `ChannelsView` | `ChannelsModel` |
| 3 | `TandemView` | `TandemModel` |
| 4 | `Export_View` | — |

Cross-view mutation is done by index — `get_app().window.navigationmodel.views[3].ui.sb_tandem_height.setMaximum(...)`. Reordering `NavigationModel.views` breaks call sites scattered across [settings/reset.py](src/settings/reset.py), the views, and `main_window.py`.

Views get lifecycle callbacks `on_open()` / `on_close()` from `NavigationModel.set_page`; `on_open` is typically where a view installs its own `materials` dict on the display model.

### The display pipeline

3D rendering flows one way:

```
model computes an OCC TopoDS_Shape
  → wrapped in ShapeModel(label, shape, ShapeTypes.*)
  → DisplayModel.add_shape(s)          # dict keyed by label; enabled=False removes
  → DisplayModel.update()              # assigns materials by ShapeTypes, emits shapes_changed
  → OrbitCameraViewer3d.update_display  # the pythonocc canvas
```

Any view method that changes geometry must be decorated with `@display_action` ([custom_view.py](src/windows/views/custom_view.py)), which calls `displaymodel.update()` in a `finally` block. Forgetting it means the model changes but the viewport does not repaint.

`ShapeTypes` (CYLINDER / CHANNEL / TANDEM / SELECTED / EXPORT) is a colour/material key, not a type hierarchy; each view supplies its own `materials` mapping so the same shape renders differently per tab.

### Geometry

[src/classes/mesh/](src/classes/mesh/) holds the OCC construction code, one concern per module: `cylinder.py` (`BrachyCylinder`, base collar, notch), `channel.py` (`NeedleChannel`, `rounded_channel` swept pipes, point cleanup), `tandem.py` (`Tandem`, 2D wire → sweep), `notch.py`, `intersections.py`, and `helper.py` (face/vector/plane utilities shared by all of them).

`BrachyCylinder.shape()` caches into `self._shape`; mutators must clear that cache or the viewport shows stale geometry.

Height changes are propagated as an **offset**, not an absolute: `CylinderView.action_apply_settings` emits `height_changed(length - model.starting_length)`, and channels/tandem shift themselves by that delta. Original DICOM needle points are never mutated — `starting_length` is captured at import time and is the fixed reference.

The final export is a boolean: channels and tandem are `BRepAlgoAPI_Cut` out of the cylinder ([export_view.py](src/windows/views/export_view.py)).

### DICOM import

`read_dicom_folder` ([dicom/fileio.py](src/classes/dicom/fileio.py)) globs `**/*.dcm`, picks the first RTPLAN and first RTSTRUCT, then branches on `rp_dataset.Manufacturer` into `load_varian_dicom_data` or `load_nucletron_dicom_data`. The two vendors store channel geometry differently and have parallel `load_central_axis_*` / `load_channels_*` implementations — a fix in one usually needs the mirror fix in the other.

Everything is flattened into a single `DicomData` bag ([dicom/data.py](src/classes/dicom/data.py)), which has no `__slots__`: **any field added to `__init__` must also be added to `reset()`**, or it leaks across imports.

A structure named exactly `"Central Axis"` is mandatory — it defines the cylinder axis and tip direction. Its absence surfaces via `MainWindow.no_central_axis_or_cylinder_outline()`.

`DicomModel.update(data)` emits `values_changed`, which fans out to `CylinderModel.load_data` and `ChannelsModel.load_data`.

### Configuration

`DEFAULT_CONFIG_VALUES` ([settings/defaults.py](src/settings/defaults.py)) is the schema: a flat `CONFIG_*` → number dict. Adding a setting touches four places — `defaults.py`, `settings/reset.py` (`resetAllValues` to push it into a spin box, `getCurrentValues` to read it back), and the owning view's `__init__`.

Config loading is lenient by design: `load_config_file` keeps any key that is present and numeric, falls back to defaults/previous values for the rest, and reports both lists through `config_keys_loaded` so `createConfigMessageText` can tell the user exactly what was and was not loaded. Unknown keys in a user's JSON are preserved but ignored.

### Qt UI files

[src/windows/ui/](src/windows/ui/) holds `.ui` files (edited in Qt Designer) and their generated `*_ui.py` counterparts. **The `*_ui.py` files are generated — do not hand-edit them.** Regenerate with:

```bash
pyside6-uic src/windows/ui/<name>.ui -o src/windows/ui/<name>_ui.py
```

Widget styling is currently applied as inline `setStyleSheet` strings in `main_window.py` (the `change_color_*` methods, one near-duplicate per nav button). [src/windows/palettes.py](src/windows/palettes.py) and [notes/style guide.txt](notes/style%20guide.txt) exist but the nav buttons do not use them.

## Sample data

`SI_C_D30 Brachify_Ex1/` and `SI_C_D30 Brachify_Ex2/` each contain a complete RP/RS/RD DICOM triple suitable for exercising the import path.

## Developer notes

[notes/](notes/) contains short upstream how-tos worth checking before changing the relevant area: `gui.txt` (the Qt Designer → view → action → signal workflow), `deployment.txt` (the exe build), `display.txt` and `background_color.txt` (pythonocc display customization), `optimizations.txt` (`BOPAlgo_Builder` for parallel fuses).

## Review process

Two templates, for two different destinations:

- [pull_request_template.md](pull_request_template.md) — **Team 10's**, used for PRs into this fork's `main`. It carries the documentation gate described above: the reviewer explicitly checks that `docs/project/COSC499-TEAM10-PROJECT-DOCS.md` matches what the code now does. If you are opening a PR here, fill this one in.
- [pull_request_template_brachify.md](pull_request_template_brachify.md) — upstream brachify's original process, preserved unchanged for PRs going back to the `upstream` remote: merge main into the feature branch → self-review → assign a peer reviewer (who also merges main and *runs* the code) → fix → reviewer approves → assign Michael Kudla → Michael reviews, approves, and merges.

Because the printed cylinder is a physical device used on a patient, "the reviewer runs the code" is a real requirement in both flows, not a formality. Geometry changes must be visually inspected in the Export tab.
