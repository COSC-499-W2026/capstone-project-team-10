# COSC 499 — Team 10 — Project Documentation

**This file is the source of truth for project documentation.**

Every other document in this repository is either upstream material we inherited, course
scaffolding, or a pointer back here. The one long companion,
[COSC499-BRACHIFY-INIT-DOCS.md](COSC499-BRACHIFY-INIT-DOCS.md), explains the code as inherited
from upstream for a newcomer, and is a baseline rather than a reference (§9.0). When any two
documents disagree, this one wins — and when this one disagrees with the code, **the code wins
and this file must be corrected**.

| | |
|---|---|
| Project | *brachify* — 3D-printable brachytherapy cylinder generator |
| Course | COSC 499, UBC Okanagan (Capstone) |
| Repository | `COSC-499-W2026/capstone-project-team-10` |
| Upstream | `brachify/brachify` (configured as the `upstream` remote) |
| Last full code audit | 2026-09-21 |
| Audit scope | Every hand-written source file read end to end; see §2 |

---

## Table of contents

1. [Setup](#1-setup)
2. [Standing mandate for this document](#2-standing-mandate-for-this-document)
3. [What this project is](#3-what-this-project-is)
4. [Architecture](#4-architecture)
5. [Module reference](#5-module-reference)
6. [Data and configuration reference](#6-data-and-configuration-reference)
7. [Known bugs, traps, and dead code](#7-known-bugs-traps-and-dead-code)
8. [Testing](#8-testing)
9. [Maintaining this document](#9-maintaining-this-document)
10. [Glossary](#10-glossary)

---

## 1. Setup

### 1.1 Prerequisites

- **conda.** The project is conda-only. **Never run `pip install` into the environment** —
  mixing conda and pip is a known, documented breakage here
  ([virtual_environments_instructions.md](../../virtual_environments_instructions.md)).
- Python 3.12 (3.11 also works upstream).
- Git. On Windows, install **Git for Windows**, which brings Git Bash with it. Claude Code
  runs the session-start hook through Git Bash (§1.10).
- Node, **optional**. Only redrawing the architecture diagrams needs it
  ([docs/architecture/README.md](../architecture/README.md)). `build.py --check`, which runs
  on every pull request, is plain Python and does not.

`pythonocc-core` is pinned to **7.7.2**. Upstream has never produced a working environment
above that version. Do not bump it casually.

**Windows, macOS and Linux install the same dependencies.** Every package the app, the tests
or the build imports directly is listed by name on every OS. The *versions* may differ between
them, and that is accepted. The list is written in three places that must agree:

| Where | Used by | Versions |
|---|---|---|
| [spec-file.txt](../../spec-file.txt) | Windows (§1.3) | every package locked to an exact build |
| the `conda create` command in §1.2 | macOS and Linux | newest available when you run it |
| [environment.yml](../../environment.yml) | `conda env create -f environment.yml`, on any OS | newest available when you run it |

| Package | Why it is listed |
|---|---|
| `python=3.12` | the interpreter. Pinned to 3.12 everywhere (the Windows lockfile has 3.12.2) |
| `pythonocc-core=7.7.2` | the geometry kernel. The one hard version pin, see above |
| `pyside6` | the Qt GUI |
| `matplotlib` | the PDF reference sheet plots |
| `numpy` | geometry and DICOM maths |
| `reportlab` | the PDF reference sheet |
| `pydicom` | DICOM import |
| `pyinstaller` | building the `.exe` (§1.7), and the hidden-import test (§8.2) |
| `pytest` | the test suite (§8.2) |

**A dependency is added for Windows, macOS and Linux together, or not at all.** Never add one
for a single OS. In the same pull request:

1. **Check that conda-forge builds it for every platform the team uses.** A package missing
   on any one of them is not added. Raise it with the team instead.

   ```bash
   for p in win-64 osx-arm64 osx-64 linux-64; do
     conda search -q --override-channels -c conda-forge <package> --platform $p | tail -1
   done
   ```

   Each line must print a version. A `noarch` package shows up for all four.
2. **Add it by name, without a version, to all three places** in the first table above, and
   give it a row in the second table saying why it is needed. Name only `python` and
   `pythonocc-core` with a version. Pinning anything else is a deliberate decision for the
   team, not a default.
3. **Install it in your own environment** with `conda install -c conda-forge <package>`, never
   `pip`. Then run the app and `python -m pytest`.
4. **Regenerate `spec-file.txt` on Windows** with `conda list --explicit > spec-file.txt`. With
   no Windows machine, solve for Windows from your own OS as §1.3 describes, and mark it
   *Not verified* there and in the pull request.
5. **Say in the pull request which operating systems you actually ran it on.** The others
   are *Not verified* until a teammate on that OS runs it.

Removing a dependency is the same change in reverse: take it out of all three places and the
second table, and regenerate `spec-file.txt`.

### 1.2 macOS setup — verified working

> Verified on 2026-09-21: macOS (Darwin 25.6.0), Apple Silicon (arm64), Python 3.12.
> The app launches, the Qt window opens, and the OpenCASCADE 3D viewport initialises.

> Unpinned command with `pyinstaller` and `pytest` verified on 2026-10-01: macOS (Darwin 25.6.0),
> Apple Silicon. It installed PySide6 6.11.2, matplotlib 3.11.2, reportlab 5.0.1, pyinstaller
> 6.22.3, pytest 9.1.1, pydicom 3.0.2 and numpy 1.26.4 on Python 3.12.14. In it the test suite
> passed, and the app launched natively, completed main window initialisation and initialised
> the viewport. DICOM import and the Export tab were not exercised in that run.

`spec-file.txt` **will not work on macOS.** Its line 3 reads `# platform: win-64` and most of
its 185 pinned package URLs are Windows binaries.

**PySide6 must be named explicitly on macOS.** On Windows, conda-forge's `matplotlib`
meta-package depends on `pyside6 >=6.7.2`, which is why PySide6 appeared in the Windows
lockfile without being requested. The `osx-arm64` build of `matplotlib` has no Qt dependency,
so a Mac environment that does not name `pyside6` has no PySide6 and `src/launch.py` dies on
its first import. `environment.yml` did not name it until 2026-09-30. It does now. The command
below names every package in §1.1:

```bash
# 1. Install a conda. Miniforge defaults to conda-forge, which is the only channel
#    shipping pythonocc-core, and avoids the Anaconda commercial-repo terms that the
#    `defaults` channels in environment.yml would pull you into.
brew install --cask miniforge
conda init zsh
# open a new terminal here

# 2. Create the environment with the same dependencies as spec-file.txt (§1.1).
conda create -n brachify -c conda-forge \
  python=3.12 \
  pythonocc-core=7.7.2 \
  pyside6 \
  matplotlib \
  numpy \
  reportlab \
  pydicom \
  pyinstaller \
  pytest

# 3. Run, from the repository root
conda activate brachify
python src/launch.py
```

The versions this installs are whatever is newest that day, so they can differ from Windows
and from a teammate's Mac. On 2026-09-30 a Mac environment had PySide6 6.11.2, matplotlib
3.11.2 and reportlab 5.0.1, against 6.8.1, 3.10.9 and 4.5.1 in `spec-file.txt`. That is
expected. An environment created before 2026-09-30 has no `pytest` or `pyinstaller`. Add them
with `conda install -n brachify -c conda-forge pytest pyinstaller`, or recreate it with the
command above. `pyinstaller` is listed so the build's hidden imports can be tested (§8.2). The
`.exe` itself is still built only on Windows (§1.7).

**Linux.** Use the same `conda create` command. Install Miniforge with its Linux installer
instead of Homebrew, and run `conda init` for your shell. `pythonocc-core` 7.7.2 is built for
`linux-64` on conda-forge (*Verified* 2026-09-30 with `conda search --platform linux-64`).
*Not verified:* creating the environment or running the app on Linux.

### 1.3 Windows setup — the upstream-supported path

```bash
conda create --name brachify --file spec-file.txt
conda activate brachify
python src/launch.py
```

`spec-file.txt` is the canonical, fully pinned lockfile. Prefer it on Windows.

The six `pytest` lines at the end of `spec-file.txt` (`iniconfig`, `pluggy`, `pygments`,
`tomli`, `exceptiongroup`, `pytest`) were not written by `conda list --explicit` on Windows.
They were solved from macOS on 2026-09-30 with `CONDA_SUBDIR=win-64 conda create --dry-run`,
pinning all 179 existing packages. The solve kept every one of them unchanged and added only
those six, and each URL returned HTTP 200. *Not verified:* creating the environment from this
file on a Windows machine. The next Windows teammate to do so should confirm it, and may
regenerate the file there.

To do the same for a new dependency from macOS or Linux, turn every URL in `spec-file.txt`
into a `name==version=build` pin, add the new package, and ask conda for a Windows solve:

```bash
grep '^https' spec-file.txt | sed -E 's#.*/##; s#\.(conda|tar\.bz2)$##' \
  | awk -F- '{b=$NF; v=$(NF-1); n=$1; for(i=2;i<NF-1;i++) n=n"-"$i; print n"=="v"="b}' > win-pins.txt
echo "<package>" >> win-pins.txt
CONDA_SUBDIR=win-64 conda create -n win-dryrun --dry-run --json --override-channels \
  -c conda-forge -c https://repo.anaconda.com/pkgs/main -c https://repo.anaconda.com/pkgs/msys2 \
  --file win-pins.txt > win-solve.json
```

In `win-solve.json`, `actions.LINK` lists every package. Every pinned one must come back
unchanged. For each new one, its URL is `<base_url>/<platform>/<dist_name>.conda`. Check that
each URL returns HTTP 200, append them to `spec-file.txt` after the existing lines, and then
delete `win-pins.txt` and `win-solve.json`.

### 1.4 Running

```bash
cd <repo root>
python src/launch.py
```

**Run from the repository root, not from inside `src/`.** Python puts `src/` on `sys.path`
itself (it is the script's directory), but several resource paths resolve relative to the
current working directory.

`launch.py` accepts an optional `argv[1]` folder path; this exists so the separate
*brachify-optimization* tool can launch straight into a plan. **It does not import the plan by
itself.** It opens the same folder picker that *Import Dicom* opens, already showing that
folder, and the user still has to choose it; cancelling imports nothing. *Reasoned from code
and from the message of commit `3013845`* ("Open file dialog box immediately on launch…"); not
run with a screen. Corrected 2026-10-02; this section previously said it auto-triggers the
import.

### 1.5 First-run behaviour you must not mistake for a hang

The first launch in a fresh environment takes **roughly a minute** with no output. Measured on
the verification run:

```
11:31:25  Config filename is None. Using defaults instead.
11:32:20  Starting main window initialization      <-- 55 s gap
11:32:23  main window initialization complete
```

That gap is the cold `import OCC` — Python byte-compiling pythonocc's very large wrapper
package for the first time. The `__pycache__` persists, so later launches are far quicker.
**Do not Ctrl-C it.** It looks hung and is not.

Startup failures are silent by design, which compounds the confusion:
[`app.py`](../../src/classes/app.py) wraps the whole GUI construction in `try/except`, logs
`critical`, and returns `False`; `main()` then simply returns. No window, no dialog, no
traceback on screen. **The log is the only place failures surface:**

```bash
tail -f ~/brachify/app.log
```

Keep that open in a second pane while developing.

### 1.6 Sample data

Two complete DICOM triples (RP + RS + RD) ship in the repository:

| Folder | Manufacturer | Channels | Notable |
|---|---|---|---|
| `SI_C_D30 Brachify_Ex1/` | Varian Medical Systems | 13 | `Central Axis` + `Applicator2..13` |
| `SI_C_D30 Brachify_Ex2/` | Varian Medical Systems | 14 | Also has a channel labelled `Tandem` — use this one to exercise the tandem path |

The two are **one plan saved twice**, not two patients. Ex2 adds the `Tandem` channel; the
needles' points are the same in both, and the RS files hold the same 42 structures under the
same name and ID (*Verified*; see chapters 6 and 7 of
[COSC499-BRACHIFY-INIT-DOCS.md](COSC499-BRACHIFY-INIT-DOCS.md#74-how-ex2-differs-from-ex1)). So
Ex2 covers everything Ex1 does, plus the tandem. Ex1 is still the only sample with no tandem.

Both exercise the **Varian** import branch only. We have **no sample data for the Nucletron /
Elekta Oncentra branch**, which is roughly half of [`dicom/fileio.py`](../../src/classes/dicom/fileio.py)
and is therefore completely unexercised by anything in this repository.

### 1.7 Building the Windows executable

```bash
python build_executable.py     # output: dist/brachify/brachify.exe
```

`--exclude-module PyQt5` in that script is load-bearing: PyQt5 and PySide6 clash at runtime.

Its hidden imports are listed in `HIDDEN_IMPORTS`, and
[tests/tooling/test_build_executable.py](../../tests/tooling/test_build_executable.py) fails
if one of them cannot be imported. PyInstaller only logs `ERROR: Hidden import ... not found`
for a missing one and still builds, exit 0 (§7.4).

### 1.8 IDE

Point VS Code at the environment interpreter (`Cmd+Shift+P` → *Python: Select Interpreter*)
so the existing [.vscode/launch.json](../../.vscode/launch.json) "Launch.py" configuration
works. On the verified macOS setup that path is:

```
/opt/homebrew/Caskroom/miniforge/base/envs/brachify/bin/python3.12
```

With that interpreter selected, VS Code's Testing panel finds the suite, because
[.vscode/settings.json](../../.vscode/settings.json) points pytest at `tests` and
[pytest.ini](../../pytest.ini) sets the import paths (§8.2). *Reasoned from the settings, not
verified in VS Code.*

### 1.9 Lint tooling

> Verified on 2026-09-25: macOS (Darwin 25.6.0), Python 3.14.0 (system) and 3.12 (Homebrew).
> Not verified on Windows.

The anti-slop rules in [AGENTS.md](../../AGENTS.md#anti-slop) are checked by
**anti-slop-py**, a zero-dependency Python linter vendored at
[agent-skills/anti-slop-py/](../../agent-skills/anti-slop-py/) from
[TinyFrontier/anti-slop-py](https://github.com/TinyFrontier/anti-slop-py) at commit `86ea16d`.
`src/anti_slop/` is the package, `src/anti_slop/rules/` holds one file per rule, and
`skills/install-anti-slop-py/` is its install skill (§1.10). It is a port of the `anti-slop`
oxlint plugin, which this repository carried until 2026-09-25 with a Node toolchain (oxlint,
oxfmt, and a lefthook pre-commit hook). All of that was removed, because oxlint cannot read
Python. The app does not need any of this.

```bash
PYTHONPATH=agent-skills/anti-slop-py/src python -m anti_slop review --base main src tests utils   # lint a branch
PYTHONPATH=agent-skills/anti-slop-py/src python -m anti_slop --explain no-any-parameters
```

**Nothing runs it automatically.** There is no commit hook and no CI. Agents run it because
[AGENTS.md](../../AGENTS.md#anti-slop) tells them to, the
[make-pr workflow](../workflows/make-pr.md) runs it before a PR is opened, and the
[pull request template](../../pull_request_template.md) asks whether it was run.

**Not installed, on purpose.** The linter's install skill would copy it to `tools/anti_slop/`
and add a `[tool.anti-slop]` table to a `pyproject.toml`. That has not been done. The
repository has no `pyproject.toml`, so every run uses the linter's built-in defaults, and
running it means putting `agent-skills/anti-slop-py/src` on `PYTHONPATH`. It needs Python 3.12
or newer. The Windows lockfile pins Python 3.12.2, and macOS gets the newest 3.12 (§1.1).

**What it checks.** `review --base <ref>` reports findings only on lines changed since the
merge base with `<ref>`, including uncommitted and untracked files. The violations already in
`src/` stay silent until someone edits those lines. The paths `src tests utils` limit the run
to the team's Python. Without them it also walks the vendored linter: on the branch that
vendored it, `review --base main` reported 68 policy warnings, all inside `agent-skills/`
(*Verified* 2026-09-25), and with the paths it reported none. `review` judges with the linter's `agent`
preset: the ten escape-hatch rules are errors (exit 1), and the five policy rules
(`no-adhoc-isinstance`, `no-module-mocking`, `no-object-parameters`,
`no-shape-in-symbol-names`, `no-string-attribute-access`) are warnings that do not fail the
run. `no-shape-in-symbol-names` therefore warns on `ShapeModel` and `TopoDS_Shape` without
failing. AGENTS.md says to ignore that warning. A full run with no `review`
(`python -m anti_slop src/`) puts every rule at `error` and reports everything in the tree.

- *Verified:* on 2026-09-25, `review --base HEAD` on a probe file with an `Any` parameter and
  an uncommented `cast` exits 1 with both findings, and a `Shape…` class name in the same file
  is reported as a warning. `review` on an untouched `src/launch.py` reports nothing, exit 0.
- *Not verified:* Windows.

### 1.10 Agent skills, the session-start hook, and the superpowers plugin

Section "Session start" of [AGENTS.md](../../AGENTS.md#session-start) requires every agent,
in any tool, to load the superpowers `test-driven-development` skill and read every skill in
[agent-skills/](../../agent-skills/) before its first reply. Its step 5 also requires reading
this document, the rest of the documentation set, and every hand-written file under `src/` and
`tests/`, and saying in that first reply what was read and what was skipped. That is the §2
mandate applied to every session. What each skill is, and where it
came from, and how each is used here, is in [agent-skills/README.md](../../agent-skills/README.md).
This section deliberately does not list them, so it does not go stale when one is added. The
folder is the list: agents find skills by searching it for `SKILL.md`, and so does the hook
below. Adding a skill is described in that README and needs no change to this section.

**The session-start hook.** In Claude Code, [.claude/settings.json](../../.claude/settings.json)
registers a `SessionStart` hook, [.claude/hooks/session-start.sh](../../.claude/hooks/session-start.sh).
It prints those steps and a list of every `SKILL.md` under `agent-skills/`, found by searching,
and Claude Code adds the output to the session's context on startup, resume, `/clear` and
compaction. It only prompts. It cannot invoke a skill. Other tools have no equivalent hook
here and rely on reading `AGENTS.md`. If it cannot enter the project directory, or the
directory is not the repository root, it prints the reason to stderr and exits 1.

- *Verified:* on 2026-09-25 on macOS, the script prints both skills with their frontmatter
  descriptions, from the repository root and from another directory with
  `CLAUDE_PROJECT_DIR` set, exit 0. With `CLAUDE_PROJECT_DIR` set to a missing directory, and
  to an existing directory that is not the repository, it prints the reason and exits 1.
- *Not verified:* that Claude Code fires it in a fresh session (it needs a new session after
  the settings change), and Windows.

**On Windows, Linux and macOS.** The hook is POSIX `sh`. On macOS and Linux, Claude Code runs
hook commands with `sh`. On Windows it runs them with Git Bash, which comes with Git for
Windows (§1.1). Without Git for Windows it falls back to PowerShell, where `sh` does not exist
and the hook fails with a visible error. That case is not supported. (All of this is *from the
Claude Code docs, not tested here*.) The likeliest breakage on Windows was line endings. Git
for Windows defaults to `core.autocrlf=true`, which would check the script out with CRLF, and
`sh` then fails on `\r`. [.gitattributes](../../.gitattributes) now forces `eol=lf` for every
`*.sh`, and
[tests/tooling/test_line_endings.py](../../tests/tooling/test_line_endings.py) fails if a
tracked shell script loses that attribute (*Verified* 2026-09-30 on macOS, including removing
`.gitattributes` to watch it fail). To run the check by hand:

```bash
sh .claude/hooks/session-start.sh                                # macOS, Linux, Git Bash
```

```powershell
& "$env:ProgramFiles\Git\bin\sh.exe" .claude/hooks/session-start.sh   # Windows PowerShell
```

A clone made on Windows before `.gitattributes` existed keeps its CRLF copy until the file is
checked out again. Delete the script and run `git checkout -- .claude/hooks/session-start.sh`.

**The superpowers plugin.** The same file registers the `superpowers-marketplace`
marketplace and enables the `superpowers` plugin for this project. A Claude Code user needs it
installed for step 1 of Session start. Without it, the session falls back to the vendored copy. Claude Code applies it once
you accept the trust dialog for the folder. The plugin is **not** installed for you. It comes
from an external repository, and Claude Code does not download plugin code from a cloned
repository on its own. Until you install it, Claude Code reports the plugin as not installed
and shows the command.

Install it once, from any terminal:

```bash
claude plugin install superpowers@superpowers-marketplace
```

Inside a session, `/plugin install superpowers@superpowers-marketplace` does the same. After
that it loads in every session.

**What you are trusting.** The plugin is fetched from `https://github.com/obra/superpowers.git`
with no pinned commit, and it ships a `SessionStart` hook that runs a script on your machine at
the start of each session. This repository cannot pin the plugin commit: a marketplace source
takes a `ref` but not a `sha`, and the plugin's own pin lives in its author's catalog.

`.claude/settings.json` deliberately sets no `ref` on the marketplace, because one would not
pin the plugin. On 2026-09-25 the marketplace repository had one tag, `v1.0.12`, dated
2026-01-31, whose catalog lists superpowers 4.1.1. At that tag and at `main` alike, the
catalog's `superpowers` source is the bare URL above with no `ref`, so a `ref` on the
marketplace would pin an old catalog while the plugin code still came from superpowers'
default branch (*Verified* by reading both catalogs, *Reasoned* for what the installer then
fetches). The superpowers skill that must stay stable, `test-driven-development`, is instead
vendored at a known version in `agent-skills/superpowers-tdd/` (6.4.2).

- *Verified:* in the local copy of the marketplace catalog, the `superpowers` entry (6.3.0) has
  an unpinned external URL source, the plugin ships that hook, and the marketplace name
  `superpowers-marketplace` matches the one in `.claude/settings.json`.
- *From the Claude Code docs, not tested here:* that the marketplace is added on folder trust
  without a further prompt, that a plugin from an external source is not installed until each
  person installs it (Claude Code v2.1.195 and later), and that third-party marketplaces do not
  auto-update by default. Nobody has yet opened this repository on a fresh machine to observe it.

### 1.11 Why there is no Docker setup

Containerising brachify for development was considered on 2026-09-30 and rejected. The
reasons, so the question does not have to be reopened from scratch:

1. **brachify is a desktop GUI, and a container has no screen.** It is a PySide6 window with
   an OpenGL viewport (§4.5), not a web server, so there is no port to open in a browser.
   Started with `docker compose up`, Qt finds no display and exits. Showing the window takes
   one of two workarounds, and neither suits a team on macOS and Windows:
   - **A virtual display streamed to the browser** (Xvfb plus noVNC at `localhost:6080`). It
     is the same Qt program, but the viewport renders in software with no GPU. Camera drags
     lag, the file dialogs browse the container's filesystem instead of yours, and the
     widgets take Linux styling rather than what clinicians see on Windows.
   - **The host's display over X11** (XQuartz on macOS, an X server on Windows). The window
     is native, but the OpenCASCADE viewport needs OpenGL forwarded over X11, which XQuartz
     does not do reliably. That would leave the viewport, the core of the app, broken.
2. **Docker cannot build the product.** What ships is a Windows `.exe` built by PyInstaller
   (§1.7), and PyInstaller only builds for the operating system it runs on. A Linux container
   cannot produce the `.exe`, so a production image would have nothing to ship.
3. **conda already provides the reproducible environment.** `pytest`, the anti-slop linter
   (§1.9) and `build.py --check` all run headless inside the conda environment, and every
   operating system installs the same dependencies from it (§1.1). An image would be a second
   environment holding the same packages, kept in step by hand. The only tool missing from
   conda is Node, needed only to redraw the diagrams (§1.1), which is too rare to justify an
   image.

What was done instead: Windows, macOS and Linux install the same dependency list (§1.1), and
the session-start hook was made safe on Windows (§1.10).

**When to reconsider.** If the team adds CI, a Linux container that runs `python -m pytest`
and the anti-slop linter on every pull request could be worth it, because neither needs a
screen. That would be a CI image, not a way to run the app.

*Reasoned from the architecture and the tools' documented behaviour, not tested here.* The
noVNC and XQuartz workarounds were not tried.

---

## 2. Standing mandate for this document

This document exists because of the following instruction. It is reproduced **verbatim** and
stands as the permanent rule for anyone — human or AI — who edits this file:

> Ok so I want you to please understand this repo and read everything in detail, not just the
> documentation and other files, but also the code, which is obviously the source of truth.
> Read absoutely everything so that you can understand everything about this codebase. Please
> be honest about this and actually do it (yes, do it again).

### What this means in practice

1. **The code is the source of truth, not the docs.** Upstream's README, the User Manual, and
   the `notes/` directory describe intent. They are frequently out of date. Where a document
   and the code disagree, believe the code and fix the document.
2. **Read, do not skim.** Do not describe a module you have not opened. Do not infer a
   module's behaviour from its name or its imports.
3. **Be honest about coverage.** If a file was skimmed rather than read, or a claim is
   reasoned from the source rather than observed at runtime, say so *in the text*. This
   document uses two explicit markers:
   - *Verified* — observed at runtime during an audit, with the evidence noted.
   - *Reasoned from code* — derived by reading, not executed or clicked through.
4. **No invented certainty.** "I don't know" and "not verified" are acceptable entries. A
   confident wrong statement in this file is worse than a gap, because the whole team and
   every AI agent treats this file as ground truth.

### Coverage of the 2026-09-21 audit

Read end to end: every hand-written `.py` file under `src/` and `benchmarks/` (~4,400 LOC
including all 806 lines of `template_reference.py`); all six `.ui` XML files (corrected from "seven" on 2026-10-02); `README.md`,
`README-BRACHIFY.md`, `virtual_environments_instructions.md`, every file in `notes/`;
`environment.yml`, `requirements.txt`, `spec-file.txt`, `build_executable.py`, `LICENSE`,
`.gitignore`, `.vscode/*`; the full text of `user_guide/Brachify User Manual.docx`; and the
headers of both sample DICOM sets.

Not read in full, and why:
- The six generated `src/windows/ui/*_ui.py` files. Their complete widget inventory was
  extracted from the `.ui` XML they are generated from, which is equivalent and
  authoritative. They must never be hand-edited (§5.6).
- `3D Models and Templates/*.SLDPRT|.STL|.pdf|.docx` — binary CAD and Office assets that no
  code reads. Read for
  [COSC499-BRACHIFY-INIT-DOCS.md](COSC499-BRACHIFY-INIT-DOCS.md#1-3d-models-and-templates):
  the two Word documents are the physicist's cylinder dimensions and the printed-cylinder QA
  checklist, and six of the dimensions' seven numbers match `DEFAULT_CONFIG_VALUES`.
- `.vs/brachify/v17/.wsuo` — a Visual Studio binary user-state blob, committed by accident
  upstream.
- `src/windows - Shortcut.lnk` — a Windows shortcut, committed by accident upstream.

---

## 3. What this project is

### 3.1 Clinical purpose

*brachify* is a Windows desktop application written by **Michael Kudla, PhD** (BC Cancer) for
medical physicists doing **interstitial gynaecological (GYN) brachytherapy**.

The workflow it serves:

1. A clinician plans a treatment in their Treatment Planning System (TPS) — Varian
   BrachyVision or Elekta Oncentra — placing needles around and through a vaginal cylinder
   applicator.
2. They export the plan as DICOM: an **RTPLAN** (`RP*.dcm`) file and its associated
   **RTSTRUCT** (`RS*.dcm`) file.
3. brachify reads those, reconstructs the needle geometry in 3D, and generates a
   **patient-specific, 3D-printable cylinder** with each needle channel bored through it,
   optionally a curved tandem channel, an orientation notch, and an optional base collar.
4. It exports **STL** (for printing) or **STEP** (for CAD), plus a **PDF reference sheet**
   giving each channel's number, interstitial length, and position on a cross-section diagram.

The printed cylinder is a physical medical device used on a patient. Geometry bugs have
clinical consequences. This is the reason the upstream review process
(§[pull_request_template_brachify.md](../../pull_request_template_brachify.md)) requires a
reviewer to actually *run* the code, and requires Michael's sign-off before merge.

### 3.2 The hard clinical precondition

**The DICOM plan must contain a channel labelled exactly `Central Axis`.**

That channel defines the cylinder's central axis and tip direction; every other needle is
rotated and translated into cylinder-local coordinates relative to it. Its tip must sit at the
tip of the cylinder and its dwell times must be zero (it is not part of the printed model).

**The code matches the label more loosely than "exactly", and differently per vendor.** The
manual's rule above is the one planners must follow; this is what the code accepts:

| Vendor | Matches | Consequence |
|---|---|---|
| Varian | the first channel whose label, ignoring case, **contains** `central axis` or `centralaxis` | a dose-carrying needle labelled, say, `Central Axis Needle` can be taken as the axis (*Verified*) |
| Nucletron / Oncentra | a structure whose `ROIName`, ignoring case, **is** `central axis` or `centralaxis` | exact, apart from case. *Reasoned from code*; there is no Oncentra sample (§1.6) |

Nothing reads the dwell times, so a Central Axis with dwell time is not caught: both samples
give it 222.8 s (*Verified*).

If it is absent, brachify falls back to a structure whose `ROIObservationLabel` contains
`"surface"`. If that is also absent, the import aborts with
`MainWindow.no_central_axis_or_cylinder_outline()`. On the Oncentra path the fallback places
the cylinder but loads no needle (§7.9).

A tandem channel is optional. If present it supplies the tandem's rotation angle. The match is
a substring too: any channel whose label contains `tandem`, ignoring case, is set as the tandem
at import ([`channels_model.py:66-67`](../../src/windows/models/channels_model.py#L66-L67)). When
several match, the last one wins, since each match replaces the one before. *Reasoned from
code.*

### 3.3 Repository provenance

This repository is a **fork of `brachify/brachify`**. The `upstream` remote still points there.
Essentially all code was written by the upstream authors.

Team 10's contribution as of the last audit consists of README edits, the course folder
scaffolding (`docs/`, `tests/`, `utils/`), and this documentation set. The first change to
`src/` came on 2026-10-08, a fix to the Channels view's list selection (§7.6). Later changes,
on 2026-10-10, keep the Export tab disabled until a cylinder exists (§7.6) and add the
Cylinder tab's mm/cm display selector (§5.6). Geometry and configuration remain in mm.
The standalone RTSTRUCT reader `classes/dicom/structures.py` and its tests (§5.3, §8)
were added on 2026-10-11. Folder import now calls `load_structures` so
`DicomData.structures` holds that decode, or `None` on failure (§5.3). On 2026-10-15,
importing a plan stopped keeping channels disabled in the previous plan (§7.10), the collar
settings began to round-trip through config files, and *Generate Tandem* stopped dropping
settings (§7.1). `ChannelsModel` began keeping a channel's own
diameter through the Channels tab's Apply (FR-CN-08, §5.5). It is not yet reachable from the GUI.

### 3.4 Licence — read this before publishing anything

brachify is licensed under **Business Source License 1.1**, *not* an open-source licence, and
**it never converts to one** (`Change Date: None`).

Permitted: internal use (including inside a for-profit organisation), forking for personal,
academic, research or non-commercial purposes, and distributing modified versions **for free
under these same terms**.

Not permitted without a separate commercial licence: selling or sublicensing brachify or any
fork as a standalone product or service, or bundling it into a commercial product or SaaS
offering.

Academic capstone use is squarely within the grant. Do not publish derivative work under a
permissive licence, and do not strip the `LICENSE` file.

---

## 4. Architecture

The pictures (system architecture, UML, DFD level 0, DFD level 1) live in [docs/architecture/](../architecture/README.md),
which also says when they must be redrawn. This section is the prose reference behind them.

*Reasoned from the proposal:* `diagrams/projected-framework/` holds planned UML and DFD
responsibilities for structure review, editing, templates, history and validation. They
are not implemented application behaviour. The existing UML and DFD sources now live in
`diagrams/existing-framework/`; `system-architecture.mmd` stays directly in `diagrams/`.
The build discovers both folders recursively and generates the shared viewer.

### 4.1 Technology stack

| Concern | Library |
|---|---|
| GUI toolkit | PySide6 (Qt 6) |
| Geometry kernel | OpenCASCADE via `pythonocc-core` 7.7.2 (`OCC.Core.*`, `OCC.Extend.*`) |
| DICOM parsing | `pydicom` |
| PDF generation | `reportlab` |
| Diagram rendering | `matplotlib` |
| Numerics | `numpy` |
| Packaging | PyInstaller (Windows only) |
| Repository tooling | anti-slop-py (Python, vendored, run by hand, §1.9) |

### 4.2 Startup sequence

```
src/launch.py  main()
  └─ RadiotherapyApp(argv)                    # QApplication subclass
       ├─ AppSignals()                        # app.signals
       └─ Values()                            # app.values — reads ~/brachify/filepaths.json,
                                              #   then the last-used config JSON, else defaults
  └─ app.gui()
       ├─ MainWindow()                        # builds Ui_MainWindow, wires nav buttons
       ├─ MainWindow.initModels()             # models first...
       ├─ MainWindow.initViews()              # ...then views, which connect to them
       │    ├─ OrbitCameraViewer3d()          # the OCC canvas widget
       │    └─ NavigationModel()              # constructs the 5 views in fixed order
       └─ showWithCanvas()                    # resize -1px, show, resize back (canvas fit hack)
  └─ app.exec()                               # Qt event loop
```

The `__init__` → `initModels()` → `initViews()` split is deliberate: models must exist before
views try to connect signals to them. **Preserve that ordering when adding either.**

### 4.3 The five views are addressed by index

`NavigationModel.views` is a plain list, and the entire codebase reaches across views
positionally — e.g. `get_app().window.navigationmodel.views[3].ui.sb_tandem_height.setMaximum(...)`.

| Index | View class | File | Primary model |
|---|---|---|---|
| 0 | `ImportView` | [import_view.py](../../src/windows/views/import_view.py) | `DicomModel` |
| 1 | `CylinderView` | [cylinder_view.py](../../src/windows/views/cylinder_view.py) | `CylinderModel` |
| 2 | `ChannelsView` | [channels_view.py](../../src/windows/views/channels_view.py) | `ChannelsModel` |
| 3 | `TandemView` | [tandem_view.py](../../src/windows/views/tandem_view.py) | `TandemModel` |
| 4 | `Export_View` | [export_view.py](../../src/windows/views/export_view.py) | — (composes all) |

**Reordering this list breaks call sites scattered across `settings/reset.py`, every view, and
`main_window.py`.** There is no symbolic lookup. Treat the order as frozen.

The Cylinder view's Units selector changes its seven length controls between mm and cm
(§5.6). It does not apply the design. *Verified* by the offscreen unit-switch case.

### 4.4 Signal graph

Three application-wide signals live on `AppSignals` ([signals.py](../../src/classes/signals.py)):

| Signal | Emitted by | Received by |
|---|---|---|
| `viewChanged(int)` | the five nav buttons in `MainWindow.__init__` | `NavigationModel.set_page` |
| `height_changed(float)` | `CylinderView.action_apply_settings`, offset in mm regardless of display unit | `ChannelsModel.update_height_offset`, `TandemModel.update_height_offset` |
| `exportFile(str)` | *nobody* | *nobody* — declared and unused |

Model-to-model wiring, all established in `MainWindow.initModels()` / `TandemModel.__init__`:

```
DicomModel.values_changed(DicomData)
    ├─→ CylinderModel.load_data
    └─→ ChannelsModel.load_data

ChannelsModel.tandem_changed(NeedleChannel) ─→ TandemModel.set_tandem_channel
CylinderModel.values_changed(BrachyCylinder) ─→ TandemModel.update_cylinder
                                             ├─→ CylinderView.action_update_settings
                                             └─→ MainWindow.enable_export_view
DisplayModel.shapes_changed(list, bool)      ─→ OrbitCameraViewer3d.update_display
OrbitCameraViewer3d.sig_topods_selected(list) ─→ ChannelsView.action_set_selected_shapes
                                                 (connected on_open, disconnected on_close)
```

### 4.5 The display pipeline

Rendering is strictly one-way:

```
model computes an OCC TopoDS_Shape
  → wrapped in ShapeModel(label, shape, ShapeTypes.*)
  → DisplayModel.add_shape(s)           # dict keyed by label; enabled=False deletes the entry
  → DisplayModel.update()               # assigns materials by ShapeTypes, emits shapes_changed
  → OrbitCameraViewer3d.update_display  # RemoveAll, DisplayShape each, Repaint, FitAll
```

Any view method that mutates geometry **must** be decorated with `@display_action`
([custom_view.py](../../src/windows/views/custom_view.py)), which calls `displaymodel.update()`
in a `finally` block. Omit it and the model changes while the viewport silently does not
repaint.

`ShapeTypes` (`CYLINDER` / `CHANNEL` / `TANDEM` / `SELECTED` / `EXPORT`) is a **material key,
not a type hierarchy**. Each view installs its own `materials` dict in `on_open()`, which is
how the same cylinder renders opaque-grey on one tab and translucent-teal on another.

### 4.6 Coordinate conventions

- The generated model lives in **cylinder-local coordinates**: base at the origin `(0,0,0)`,
  axis along `+Z`, tip at `z = length`.
- DICOM points arrive in patient coordinates and are transformed at import by
  `helper.rotate_points` (Rodrigues' rotation), aligning the central-axis vector to `+Z`, then
  translated so the cylinder base sits at the origin.
- **Original DICOM needle points are never mutated.** Cylinder length changes propagate as a
  *delta*: `CylinderView` emits `height_changed(length - model.starting_length)`, where
  `starting_length` is captured at import time. Channels and tandem shift themselves by that
  offset. This is why `NeedleChannel` keeps both `points` and `_offset` and applies the offset
  only in `get_points()` / `shape()`.
- In the PDF cross-section diagram the view is **from the base looking up**, so the y-axis is
  drawn negated: `Anterior` is `-y`, `Posterior` is `+y`.

### 4.7 Directory map

```
.
├── AGENTS.md                  AI agent instructions (cross-tool standard)
├── CLAUDE.md                  pointer to AGENTS.md
├── pull_request_template.md   Team 10 PR template
├── pull_request_template_brachify.md   upstream's original PR process
├── README.md                  course scaffolding template
├── README-BRACHIFY.md         upstream project README
├── LICENSE                    BSL 1.1
├── environment.yml            conda spec, the same dependency list as every OS (§1.1)
├── spec-file.txt              pinned conda lockfile — WINDOWS ONLY
├── requirements.txt           STALE, unused — do not use (§7.4)
├── build_executable.py        PyInstaller wrapper, HIDDEN_IMPORTS tested (§1.7)
├── pytest.ini                 test runner config, puts src/ and the root on sys.path (§8.2)
├── .gitattributes             keeps *.sh at LF line endings on Windows (§1.10)
├── agent-skills/              skills every agent reads at session start (§1.10)
│   ├── README.md              the skill list: upstream, version, licence, how used
│   └── <skill>/               one folder per skill, vendored as-is
├── .claude/                   Claude Code config: commands, skills, SessionStart hook
├── docs/                      course documentation
│   ├── architecture/          system architecture, existing/projected UML and DFD sources, SVGs, build.py, README
│   ├── contract/ proposal/ design/ minutes/   course documents, README only
│   ├── logs/                  weekly individual (Part A) and team (Part B) logs
│   ├── project/               ← this document, and COSC499-BRACHIFY-INIT-DOCS.md (the
│   │                            plain-language guide to the code as inherited)
│   └── workflows/             tool-agnostic procedures (commit, make-pr)
├── tests/                     tooling tests, RTSTRUCT reader and DicomData tests, main window tests in windows/, Channels and Cylinder units tests in views/ (§8)
├── utils/                     README only
├── notes/                     upstream developer notes
├── benchmarks/                dead code (§7.4)
├── resources/                 splash image and icon
├── user_guide/                Brachify User Manual.docx
├── Images/                    README screenshots
├── 3D Models and Templates/   collet models and drawings, cylinder dimensions, QA checklist
├── SI_C_D30 Brachify_Ex1/     sample Varian DICOM
├── SI_C_D30 Brachify_Ex2/     sample Varian DICOM (has a Tandem channel)
└── src/
    ├── launch.py
    ├── classes/
    │   ├── app.py             RadiotherapyApp, get_app()
    │   ├── info.py            APP_NAME, paths
    │   ├── logger.py          rotating file + stderr logging
    │   ├── signals.py         AppSignals
    │   ├── dicom/             data.py (DicomData), fileio.py (vendor readers), structures.py (ROI reader), load_structures.py
    │   ├── mesh/              cylinder, channel, tandem, notch, helper, intersections, fileio
    │   └── pdf/               template_reference.py, canvas.py
    ├── settings/              defaults.py, load.py, values.py, reset.py
    └── windows/
        ├── main_window.py     MainWindow + every QMessageBox dialog
        ├── palettes.py        colour definitions (unused)
        ├── length_field.py    LengthField and LengthUnit, mm-backed Cylinder controls
        ├── models/            six QObject models
        ├── views/             five views + custom_view.py + viewport.py
        └── ui/                .ui sources, generated *_ui.py, arrows/ PNGs and generated arrows_rc.py
```

---

## 5. Module reference

### 5.1 Entry point and application singleton

**[`src/launch.py`](../../src/launch.py)** — builds `RadiotherapyApp`, calls `gui()`, closes the
PyInstaller splash screen if present (`pyi_splash` exists only in frozen Windows builds, so the
import is wrapped in a bare `except`), optionally opens the folder picker at `argv[1]` (it does
not import by itself, §1.4), then enters the event loop.

**[`src/classes/app.py`](../../src/classes/app.py)** — `RadiotherapyApp(QApplication)`.
Module-level `get_app()` returns `QApplication.instance()` and is how **every** module reaches
global state. Two attributes matter: `app.signals` (`AppSignals`) and `app.values` (`Values`).

**[`src/classes/info.py`](../../src/classes/info.py)** — `APP_NAME = "brachify"`, version
constants, and paths. Note `USER_PATH = ~/brachify`. There is a latent typo:
`VERION_MINOR` (missing `S`), and `APP_VERSION` is the string `"alpha"` rather than a number,
so `VERSION_MAJOR`/`VERION_MINOR` are effectively unused.

**[`src/classes/logger.py`](../../src/classes/logger.py)** — a `Brachify` child logger at DEBUG,
`propagate = False`, with a rotating file handler (`~/brachify/app.log`, 25 MB × 3 backups) and
a stderr stream handler. Creates `~/brachify/` at import time if missing.

### 5.2 Settings and configuration

**[`settings/defaults.py`](../../src/settings/defaults.py)** — `DEFAULT_CONFIG_VALUES`, the
schema: a flat `CONFIG_*` → number dict, 25 keys. Full table in §6.2. It also holds
`MINIMUM_CHANNEL_DIAMETER_MM` (0.3), the narrowest channel `ChannelsModel` accepts as a
channel's own diameter, the same value as the Channels Diameter box's minimum in
`channels_view.ui`. It is not a `CONFIG_*` key.

**[`settings/load.py`](../../src/settings/load.py)** — `load_config_file()` is lenient by
design. It keeps any key present in the user's JSON whose value is `int` or `float` and not
`true` or `false` (checked by `is_config_number()`), falls back
to defaults (or the previous values, on a mid-session import) for the rest, and returns a
two-list `config_keys_loaded` of `[loaded, missing]` so the UI can tell the user exactly what
was and was not applied. Unknown keys in a user's JSON are preserved but never used.

**[`settings/values.py`](../../src/settings/values.py)** — `Values` holds `config_values` (the
single mutable dict every other module reads), the two most-recent config file paths read from
`~/brachify/filepaths.json`, and `createConfigMessageText()` which formats the human-readable
"what loaded" report shown in the Import tab.

**[`settings/reset.py`](../../src/settings/reset.py)** — the two halves of config round-tripping:
- `resetAllValues(dict)` pushes a config dict **into** every spin box and then applies it. It
  writes cylinder dimensions through `CylinderView.set_dimensions_mm`, so the current
  display unit does not change the meaning of an imported mm value. It
  handles the three tandem states explicitly (absent / generated / imported), because a
  generated tandem must be regenerated while an imported one must not be touched. Since
  2026-10-15 it also fills the two collar boxes (§7.1).
- `getCurrentValues()` reads the current state **back out** into a dict. Since 2026-10-15 it
  returns every key, 25 since the notch and tip settings. The collar's two come from the live settings,
  which *Apply Settings* writes (§7.1), and the notch's five from the cylinder's
  `notch_settings`.

### 5.3 DICOM ingest

**[`dicom/structures.py`](../../src/classes/dicom/structures.py)** — standalone
`read_structures(dataset: pydicom.dataset.Dataset) -> tuple[Structure, ...]`.
It joins RTSTRUCT definitions, contours and observations by ROI number and preserves every
contour in immutable `Structure` and `Contour` dataclasses. Names need not be unique.
Colours are RGB integers in 0..255 (neutral grey when absent). GTV/CTV/PTV map to the
`TUMOUR` display category, ORGAN to `ORGAN`, and other or absent types to `OTHER`;
the original interpreted type is retained. Planning target volumes are not all tumour tissue.

The reader retains patient-coordinate millimetres and each ROI's frame-of-reference UID.
It accepts POINT, OPEN_PLANAR, OPEN_NONPLANAR, CLOSED_PLANAR and CLOSEDPLANAR_XOR,
retaining their semantics. Geometry-free ROIs have an empty contour tuple. It rejects
missing required metadata, duplicate identifiers/records, orphan references, invalid RGB,
point-count mismatches, nonfinite coordinates, and mixed XOR/non-XOR contours through
`StructureReadError`. A failure returns no partial result and does not mutate the input.
Multiple observation records for one ROI are currently rejected as ambiguous.

No coordinate transformation, frame matching, polygon planarity or self-intersection
validation, surface reconstruction, display controls or structure-list GUI is implemented
here. As of 2026-10-15, both vendor readers call
[`load_structures`](../../src/classes/dicom/load_structures.py) after reading the RTSTRUCT, so
`DicomData.structures` holds the decode result (or `None` on `StructureReadError`). Example
after `pydicom.dcmread` has loaded an RTSTRUCT:

```python
from classes.dicom.structures import read_structures
structures = read_structures(rs_dataset)
```

*Verified 2026-10-11 on macOS:* both bundled sample RTSTRUCTs decode into 42 ROIs and
152 contours each. This is a headless reader check, not a GUI or clinical validation.
Synthetic tests are in `tests/dicom/test_structures.py`; Nucletron data remains unverified.

**[`dicom/data.py`](../../src/classes/dicom/data.py)** — `DicomData`, a flat mutable bag of 22
fields, including `structures` (a `tuple[Structure, ...]` from `read_structures`, or `None`).
There is a comment in the file stating the rule explicitly: **any field added to
`__init__` must also be added to `reset()`**. Keep the rule, but know how narrow the leak is:
every import builds a **new** `DicomData`, so a field missing from `reset()` only survives an
import that fails partway and leaves the old object in place (*Reasoned from code*; see [10.4 of the init guide](COSC499-BRACHIFY-INIT-DOCS.md#104-datapy-the-form-brachify-fills-in)).
`central_axis_flag` violated this until 2026-10-10. `reset()` now clears it, and
[tests/dicom/test_data.py](../../tests/dicom/test_data.py) fails, naming the field, if any
field in `__init__` is missing from `reset()`.

**[`dicom/fileio.py`](../../src/classes/dicom/fileio.py)** — the vendor readers. `read_dicom_folder()`
globs `**/*.dcm`, takes the **first** file that parses as RTPLAN and the **first** that parses
as RTSTRUCT, then branches on `rp_dataset.Manufacturer`. After each branch reads the RTSTRUCT,
it calls [`load_structures`](../../src/classes/dicom/load_structures.py), which fills
`data.structures` via `read_structures`, or sets it to `None` on `StructureReadError` without
aborting needle or cylinder loading (*Reasoned from code*; guarded by
[tests/dicom/test_load_structures.py](../../tests/dicom/test_load_structures.py)):

| Manufacturer string | Reader |
|---|---|
| `"Varian Medical Systems"` | `load_varian_dicom_data` |
| `"Nucletron"` | `load_nucletron_dicom_data` |
| anything else | falls through — raises `UnboundLocalError` (§7.2) |

The two branches are near-parallel and must usually be fixed in tandem:
`load_central_axis_varian` / `load_central_axis_nucletron`, `load_channels_varian` /
`load_channels_nucletron`.

Vendor differences that matter:
- **Varian** stores channel contour geometry in the RTSTRUCT's `ROIContourSequence`. The
  contours arrive ordered by ROI number while the label/number lists are ordered by channel
  number, so `load_channels_varian` explicitly re-sorts them into alignment. Getting this wrong
  silently mislabels every needle.
- **Nucletron / Oncentra** stores it in a **private tag `(300f,1000)`** inside the RTPLAN.
  Sometimes that tag's contents are raw binary, in which case the reader falls back to manual
  `read_sequence()` parsing with implicit VR, little-endian, and the dataset's own encoding.

Both branches strip the central-axis channel out of the channel lists after using it, and both
handle single-point "anchor" channels by deleting them and warning the user — with different
warning dialogs (`single_point_pop_up_Varian` vs `..._Nucleatron`) because the two systems
label anchors differently.

`module-level global method_found` is used as a success flag across functions. It is reset at
the top of each loader so that importing two folders in a row behaves correctly.

### 5.4 Geometry

All under [`src/classes/mesh/`](../../src/classes/mesh/), one concern per module.

**`cylinder.py`** — `BrachyCylinder`. `shape()` builds a `BRepPrimAPI_MakeCylinder`, then for
a dome tip calls `add_dome()`, which finds the highest planar face by walking a
`TopExp_Explorer` and fillets that top edge into a half-sphere. A flat tip skips `add_dome()`.
It then optionally fuses a base collar (`add_base`) and fuses the orientation notch
(`add_notch`) unless the notch is off. Since 2026-10-15 the tip is `TipShape.DOME` or
`TipShape.FLAT`, read once in `__init__` by `tip_shape_from_config()` from
`CONFIG_CYLINDER_FLAT_TIP` (§6.2). The defaults still build the dome. **`shape()` reads a cache but never writes one.** It returns `self._shape` when
one is stored, and otherwise rebuilds the solid without storing it. Only the three setters,
`setDiameter`, `setLength` and `enableBase`, clear `_shape`, rebuild and store the result
(*Verified* for the init guide: after calling `shape()` on a new cylinder, `_shape` was still
empty). So **every mutator must clear the cache and rebuild it**, as those three do, or
`shape()` keeps returning the old solid. A new cylinder rebuilds on every call until a setter
runs, and the collar is read from the live settings at the moment of that rebuild (§7.1).
Corrected 2026-10-02; this section previously said `shape()` caches into `self._shape`.

**`channel.py`** — `NeedleChannel` plus `rounded_channel()`, the single most intricate function
in the codebase. It:
1. applies the dead-space offset to the tip,
2. adds the cylinder height offset,
3. truncates coordinates to 5 decimals (*not* rounds — a documented workaround for an OCC
   fusion bug),
4. removes identical and near-collinear points,
5. builds a cone tip, then fuses one `BRepPrimAPI_MakeCylinder` per segment and one
   `BRepPrimAPI_MakeSphere` per interior vertex,
6. optionally widens the channel at the base for post-print threading,
7. extends the channel out of the cylinder base.

Steps 5–6 are wrapped in a **three-tier fallback ladder** (`fix1` / `fix2` / `fix3`) because
OCC's boolean fuse intermittently emits warnings on degenerate geometry: `fix1` nudges the
radius by 0.001 mm; `fix2` retries at 4, 3 and 2 decimal places; `fix3` jitters each coordinate
by ±0.01 mm in turn. If all three fail the user gets a warning or error dialog. This ladder is
the reason the User Manual tells clinicians to *visually re-inspect every channel* after
changing any value.

**`tandem.py`** — `Tandem`. Two distinct shape methods, easily confused:
- `generate_shape()` — the **cut-out** subtracted from the cylinder. Built by intersecting a
  swept tandem profile with a cylinder-shaped envelope (`BRepAlgoAPI_Common`), so the tandem
  channel stops at the cylinder surface. The envelope reaches `height_offset` past a dome,
  10 mm. Since 2026-10-15 `height_offset` is a property: for a flat tip
  (`CONFIG_CYLINDER_FLAT_TIP`, read in `__init__`) it grows to `√(R² + (R + 1)²) − R + 1` when
  that exceeds 10, so the envelope still contains the flat top's corners (§7.11).
- `tandem_shape()` — the **visual preview** of the physical tandem tool, shown in the Export
  tab when *Show Tandem* is ticked. Not exported.

Both work in 2D (`gp_Pnt2d`, `Geom2d_*`), find bend/exit points by curve intersection, lift to
3D, and sweep with `BRepFill_PipeShell`. `Tandem.__init__` has a `try/except` around
`get_app()` supplying hardcoded fallback values, so the module can be run standalone
(`python src/classes/mesh/tandem.py`) to visualise a tandem without launching brachify.

**`notch.py`** — `CylinderNotch`, a small box standing out of the cylinder wall from `Z=0`,
marking orientation for the person inserting the applicator. Since 2026-10-15 its size and
position come from `NotchSettings`, a frozen dataclass of `enabled`, `angle`, `width`, `depth`
and `height`, which `notch_settings_from_config()` reads from the five `CONFIG_NOTCH_*` keys
(§6.2) and raises `KeyError` on a missing one. `angle` is in degrees clockwise from Anterior as
the reference sheet draws it, so the model rotation is `(angle − 90) mod 360`, and the default 0
gives the 270° every cylinder had before. The box starts 0.2 mm inside the wall (`WALL_OVERLAP`)
so it fuses, so its radial size is `depth + 0.2`. `BrachyCylinder.__init__` reads the settings
from the live config once, `shape()` builds the notch only when `enabled`, and with a collar the
notch sits on the collar's outer wall and its height is capped at the collar height. The
defaults reproduce the old notch and cylinder exactly (*Verified* by `tests/mesh/`). The
Cylinder tab's notch controls set them (§5.6). The reference sheet still draws the notch at
the top whatever its angle.

**`helper.py`** — shared utilities: `face_is_plane`, `geom_plane_from_face`, face sorting by Z,
`get_vector` / `get_direction` / `get_magnitude`, `extend_bottom_face` (prisms the lowest face
down through `z=0` so an imported tandem always reaches the cylinder base), and
`rotate_points()`, the Rodrigues rotation used for the DICOM→cylinder transform.

**`intersections.py`** — `are_colliding()` via `BRepAlgoAPI_Section`. Defined, but **not called
anywhere**. Collision detection between needles is not currently performed.

**`fileio.py`** (mesh) — `read_3d_file` (STEP only; anything else raises and shows a dialog) and
`write_3d_file` (STL binary with `linear_deflection=0.5`, `angular_deflection=0.3`; or STEP
AP203).

### 5.5 Models

All in [`src/windows/models/`](../../src/windows/models/). `QObject`s owning domain state and
emitting change signals. They hold no widgets.

| Model | Owns | Notes |
|---|---|---|
| `DicomModel` | a `DicomData` | thin; `update()` swaps the bag and emits |
| `CylinderModel` | a `BrachyCylinder`, `starting_length` | `cylinder` is `None` until a DICOM import or a manual *Apply Settings* |
| `ChannelsModel` | `{label: NeedleChannel}`, selection, disabled set, own diameters | the tandem channel is auto-disabled when set. `load_data` starts every other channel enabled (§7.10) and clears own diameters. `set_channel_diameter` gives one channel a diameter that `set_diameter`, the Channels tab's Apply, keeps. Unknown labels raise `KeyError` before the override map changes. Clearing uses `NeedleChannel.default_diameter()`, the live config value used by newly imported channels. Below 0.3 mm, or NaN, it raises `ValueError`: a NaN diameter reaching the geometry crashes OpenCASCADE (exit 139, *Verified* 2026-10-15 by removing the check under test) |
| `TandemModel` | `_base_shape`, `_display_shape`, offsets, rotation | the most stateful; see below |
| `DisplayModel` | `{label: ShapeModel}`, materials | `add_shape` with `enabled=False` **deletes** the entry |
| `NavigationModel` | the five views | not a `QObject`; plain class |

`TandemModel` deserves attention. It distinguishes **imported** from **generated** tandems
(`is_shape_imported`) and tracks two independent vertical offsets:
- `height_offset` — automatic, follows cylinder length changes.
- `mesh_offset` — manual, the *Height Offset* spin box, applies to imported tandems only.

Its `_generate_tandem()` implements an unusual error-recovery algorithm, documented in a long
docstring in the file: it applies each spin-box value one at a time, rebuilding the shape after
each; any value that throws is recorded, reverted in the UI, but *left in place internally* in
case a later value fixes it. Survivors at the end trigger per-field error dialogs. The effect
is that an invalid tandem parameter reverts itself rather than blocking the user.

`ShapeModel` ([shape_model.py](../../src/windows/models/shape_model.py)) is the transport
object between models and the viewport: `label`, `shape`, `type`, plus `selected` /
`transparent` / `enabled` flags and a `material` dict.

### 5.6 Views and the Qt UI layer

[`src/windows/ui/`](../../src/windows/ui/) holds `.ui` files (Qt Designer XML) and their
generated `*_ui.py` counterparts.

> **The `*_ui.py` files are generated. Never hand-edit them.** They carry a
> `WARNING! All changes made in this file will be lost when recompiling UI file!` banner and
> were produced by Qt User Interface Compiler: `main_window_ui.py` by 6.5.2, the other five
> by 6.8.1. All six match their `.ui` files (*Verified* by regenerating them for the init guide).

Regenerate after editing a `.ui`:

```bash
pyside6-uic src/windows/ui/<name>.ui -o src/windows/ui/<name>_ui.py
```

`arrows_rc.py` is generated the same way, from `arrows.qrc` and the two black 14×14 PNGs in
`ui/arrows/`, and is never hand-edited either. `ChannelsView` imports it, which registers the
images as `:/arrows/spin_up.png` and `:/arrows/spin_down.png` for its spin box stylesheet. The
images are compiled into Python because PyInstaller bundles imported modules but not the
`resources/` folder (§7.5). After changing an image or the `.qrc`:

```bash
pyside6-rcc src/windows/ui/arrows.qrc -o src/windows/ui/arrows_rc.py
```

The full workflow — Designer → `.ui` → `uic` → hand-written `*_view.py` → register in
`NavigationModel` → connect signals to `action_*` methods → decorate with `@display_action` —
is documented upstream in [notes/gui.txt](../../notes/gui.txt).

Complete control inventory, extracted from the `.ui` sources:

**Import** (`import_view.ui`) — `btn_import_folder` "Import Dicom", `btn_config_file`
"Import Config File", `info_area` (QTextEdit, the information panel).

**Cylinder** (`cylinder_view.ui`)

| Widget | Label | Range |
|---|---|---|
| `combobox_units` | Units | mm or cm, starts in mm, not saved |
| `spinbox_diameter` | Cylinder Diameter | 0–99.99 mm or 0–9.999 cm |
| `spinbox_length` | Cylinder Length | 60–300 mm or 6–30 cm |
| `spinbox_base_thickness` | Collar Thickness | 0–99 mm or 0–9.9 cm |
| `spinbox_base_height` | Collar Height | 0–99 mm or 0–9.9 cm |
| `cb_add_base` | Add Collar | checkbox |
| `cb_add_notch` | Add Notch | checkbox, on by default. Unticked, it greys out the four notch fields |
| `spinbox_notch_angle` | Notch Angle | 0–359.9°, wraps, clockwise from Anterior on the sheet |
| `spinbox_notch_width` | Notch Width | 0.5–10 mm or 0.05–1 cm |
| `spinbox_notch_depth` | Notch Depth | 0.5–5 mm or 0.05–0.5 cm |
| `spinbox_notch_height` | Notch Height | 1–60 mm or 0.1–6 cm |
| `combobox_tip` | Tip Shape | Dome or Flat, the `TipShape` values. Not affected by Units |
| `btn_apply_settings` | Apply Settings | |

The notch ranges are Team 10's choice, added 2026-10-15. No clinical document sets them.
*Tip Shape* was added the same day, below the notch rows. `set_tip` fills it from the model or a
config, and Apply writes `CONFIG_CYLINDER_FLAT_TIP`.

**[`windows/length_field.py`](../../src/windows/length_field.py)** — `LengthUnit` names mm
and cm; each `LengthField` owns one `QDoubleSpinBox` and an exact mm value. User edits
convert to mm. Programmatic updates and unit switches block widget signals, preserving
precision even when the displayed value rounds. Diameter has 2 decimal places in mm and
3 in cm; length, collar and notch height have 0 in mm and 1 in cm, and notch width and depth
1 in mm and 2 in cm. Steps are 1 mm or 0.1 cm, and 0.1 mm or 0.01 cm for notch width and
depth.

`CylinderView.set_dimensions_mm` receives model and config dimensions; Apply reads the
four fields' mm values, including the length offset sent to Channels and Tandem. Changing
the selector preserves pending edits and does not apply geometry or change live settings.
The selector affects only these controls, seven since the notch fields were added
(2026-10-15). `set_notch_settings` fills the notch controls from the model or a config, the way
`set_dimensions_mm` fills the dimensions. *Verified* 2026-10-10 by eight offscreen
integration cases, watched failing before implementation. Ahab supplied a GUI screenshot
showing 3.125, 17.3, 0.3 and 1.2 cm with Add Collar selected, and terminal output
showing Ex1 import and a 13 mm height offset on Apply. The original image was not saved;
Ex2/tandem GUI regression was not verified. The stacked test PR supplies the cases.

**Channels** (`channels_view.ui`)

| Widget | Label | Range |
|---|---|---|
| `spinbox_diameter` | Channels Diameter | min 0.3, 3 dp |
| `sb_needle_length` | Dead Space | max 350, 3 dp |
| `sb_threading_dept` | Threading Depth | max 350, 3 dp — note the `dept` typo in the name |
| `sb_threading_diameter` | Threading Diameter | max 350, 3 dp |
| `listwidget_channels` | Channels | |
| `btn_set_tandem` | Set as Tandem / Clear Tandem | text toggles |
| `btn_enable` | Disable / Enable | text toggles |

**Tandem** (`tandem_view.ui`) — a `QTabWidget` (`ab`) with two sub-tabs.

*Import sub-tab:* `btn_import`, `btn_clear_import`, `sb_height_offset` (−100 – 100),
`tandem_rotation` (−360 – 360), `btn_apply_import`, `label_5` (shows the model file path).

*Generate sub-tab:* `sb_tandem_height` (10 – 500), `sp_channel_diameter` (min 0.5),
`sp_stopper_diameter` (min 0.5), `sp_bend_angle`, `sb_bend_radius` (10 – 1000),
`sb_threading_depth` (max 350), `sb_threading_diameter` (max 350), `tandem_rotation_2`
(−360 – 360), `btn_apply` "Generate Tandem", `btn_clear_generate`.

Note there are **two separate rotation spin boxes** (`tandem_rotation` on Import,
`tandem_rotation_2` on Generate) kept manually in sync — every write to one writes the other.

**Export** (`export_view.ui`) — `cb_tandem_shown`, `cb_collet_preview_reference_sheet`,
`sb_needle_collet_od`, `sb_tandem_collet_outer_od`, `sb_tandem_collet_inner_od`,
`btn_export_mesh`, `btn_export_template_reference`, `btn_export_shapes`,
`btn_export_current_config`.

**Main window** (`main_window.ui`) — `display_view_widget` (hosts the OCC canvas),
`top_menu_bar` with the five nav buttons, and `viewswidget` (`QStackedWidget`) with
`page_import` … `page_export`.

The Export nav button starts disabled and drawn grey. `MainWindow.enable_export_view` turns it on
the first time `CylinderModel.values_changed` fires, which happens on an import and on the
Cylinder tab's *Apply Settings* (§7.6).

Styling for the nav buttons is **two stylesheet strings** in `main_window.py`:
`NAV_BUTTON_STYLE` for every tab not on screen, with a grey `:disabled` rule, and
`SELECTED_NAV_BUTTON_STYLE` for the one on screen. Each of the five near-identical
`change_color_*` methods rewrites all five buttons with them on every tab click, so a style set
on one button anywhere else is lost on the next click.
[`palettes.py`](../../src/windows/palettes.py) exists but the nav buttons do not use it. The five
methods are still the most obvious refactor target in the UI layer.
([notes/style guide.txt](../../notes/style%20guide.txt) is about Python naming, `lower_case`
functions and `CapWords` classes, not colours.)

### 5.7 The 3D viewport

[`views/viewport.py`](../../src/windows/views/viewport.py) — `qtBaseViewer` sets
`WA_PaintOnScreen`, `WA_NativeWindow` and `WA_NoSystemBackground`, then `OrbitCameraViewer3d`
hands `int(self.winId())` to pythonocc's `OCCViewer.Viewer3d().Create()`.

Mouse bindings, which are non-standard and worth knowing:

| Input | Action |
|---|---|
| Left click | select shape (emits `sig_topods_selected`) |
| **Right** drag | rotate |
| Middle drag | pan |
| Wheel | zoom (fixed 2.0× / 0.5× per notch) |

> *Verified 2026-09-21:* this native-handle handoff works on macOS arm64. `lsof` on the running
> process confirmed `OpenGL`, `QtGui`, `QtWidgets` and the full OpenCASCADE `libTK*` set
> loaded, and the viewport rendered. This was the main porting risk and it is resolved.

### 5.8 PDF reference sheet

[`pdf/template_reference.py`](../../src/classes/pdf/template_reference.py) (806 lines) and
[`pdf/canvas.py`](../../src/classes/pdf/canvas.py).

`generate_pdf()` produces a reportlab document: header, patient/plan identifiers, since
2026-10-15 a two-column cylinder table built by `cylinder_rows()` (diameter, length, tip,
notch, collar, in mm, with no colons), a table of channels, and a matplotlib cross-section
diagram. It is not always one page: with Ex1's 12 channels the diagram moves to page 2, on
`main` before the cylinder table as well as after (*Verified* 2026-10-15 by rendering both).

The substantive computation is **interstitial length** — how far each needle protrudes beyond
the cylinder surface:

1. `channels_inside_cylinder()` keeps only channels whose `z=0` point lies within the cylinder
   radius.
2. `extract_points_from_channels2()` normalises every needle to terminate exactly at `z = 0`,
   interpolating the crossing point if the needle passes through, or dropping a perpendicular
   if it stops short.
3. `add_deadspace()` extends a **copy** of each needle tip outward by `CONFIG_DEADSPACE`.
4. `get_all_interstitial_lengths()` builds a dense point cloud of the cylinder surface
   (straight wall + hemispherical dome, 0.1 mm spacing) and finds where each needle's first
   segment crosses it, within a 0.25 mm tolerance. Since 2026-10-15, for a flat tip
   (`TipShape.FLAT`, §5.4) the wall runs the full length and `flat_top_points()` covers the
   top at `z = length` with a 0.1 mm grid and the rim ring, instead of the dome.

`save_points_diagram()` draws the cross-section: one circle per channel with its channel
number, the tandem marked `<n>T`, a dashed line showing tandem rotation (generated tandems
only), the orientation notch as a rectangle, `Anterior`/`Posterior` labels, and — if *Show
Collet Spacings* is ticked — dashed collet rings coloured **green** when clear and **red** when
they overlap another collet. It writes `basemap.png` **next to the PDF**, as a side effect.

Since 2026-10-15 the notch is drawn by `notch_outline()`, the part standing out of the circle,
`width` wide and `depth` deep, turned clockwise from the top by the notch angle, and not at all
when the notch is off. It is drawn on the cylinder's circle even when a collar puts the real
notch on the collar's wall, because the diagram does not draw the collar. `label_distance()`
places *Anterior* and *Posterior* 1.5 beyond the notch's depth, so the rectangle no longer
covers *Anterior*, as it did before. *Verified* 2026-10-15 by rendering Ex1's sheet with the
default notch and with a 4 mm notch at 90°, and by `tests/pdf/`.

`FooterCanvas` in `canvas.py` subclasses `reportlab.pdfgen.canvas.Canvas` to stamp "Page x of
y" and an export timestamp on every page.

After building, the module opens the PDF in the OS viewer: `os.startfile` on Windows (falling
back to `subprocess.Popen(['start', ...], shell=True)`), `subprocess.Popen(['open', ...])` on
posix. macOS is handled correctly here.

There are two near-duplicate implementations of the cylinder point cloud and surface
intersection — one pair inside `get_all_interstitial_lengths` in this file, another at module
scope in [`mesh/channel.py`](../../src/classes/mesh/channel.py). The `template_reference.py`
copy is the better one (it pre-filters the cloud by z-range for speed). The `channel.py` copies
appear unused. See §7.4.

---

## 6. Data and configuration reference

### 6.1 DICOM input requirements

A single folder containing at least:

- one **RTPLAN** (`RP*.dcm`) whose `ApplicationSetupSequence[0].ChannelSequence` is non-empty,
- one **RTSTRUCT** (`RS*.dcm`).

An RTDOSE (`RD*.dcm`) may be present and is ignored. Files are discovered recursively
(`**/*.dcm`) and the **first** match of each modality wins — a folder containing two plans
gives undefined results.

Plan authoring requirements (from the User Manual, both vendors):

- A straight needle labelled **`Central Axis`**, placed as accurately as possible along the
  cylinder axis, tip at the cylinder tip, **dwell times set to zero**. The code matches the
  label more loosely than this and never reads dwell times (§3.2).
- No intersecting needles. Nothing in the code checks this.
- Oncentra only: the manual asks for the Central Axis to be channel number 1. Nothing in the
  code checks the channel number.
- Optionally a needle labelled **`Tandem`** to orient the tandem. Also matched as a substring
  (§3.2).
- A central needle that delivers dose needs a label that does not contain `Central Axis`
  (§3.2).
- Oncentra only: *Tip End* must be selected under Applicator Properties, and using implant
  models requires a licence that is not enabled by default.

### 6.2 Configuration keys

`DEFAULT_CONFIG_VALUES` — 25 keys, all numeric, all millimetres unless noted.
The Cylinder mm/cm selector changes display only and adds no config key (§5.6).

| Key | Default | Meaning | Round-trips? |
|---|---|---|---|
| `CONFIG_CYLINDER_DIAMETER` | 30.0 | cylinder outer diameter | yes |
| `CONFIG_CYLINDER_LENGTH` | 160.0 | cylinder length | yes |
| `CONFIG_CYLINDER_FLAT_TIP` | 0 | 1 for a flat tip, 0 for the half-sphere dome (§5.4) | yes. Apply writes it, a config import fills *Tip Shape* |
| `CONFIG_CHANNELS_DIAMETER` | 2.7 | needle channel diameter (all channels) | yes |
| `CONFIG_DEADSPACE` | 6.0 | needle dead space at the tip | yes |
| `CONFIG_CHANNELS_THREADING_DEPTH` | 5.0 | channel threading depth; 0 disables | yes |
| `CONFIG_CHANNELS_THREADING_DIAMETER` | 3.17 | channel diameter at base; 0 disables | yes |
| `CONFIG_TANDEM_TIP_HEIGHT` | 170.0 | tandem height | yes |
| `CONFIG_TANDEM_CHANNEL_DIAMETER` | 3.8 | tandem channel diameter | yes |
| `CONFIG_TANDEM_STOPPER_DIAMETER` | 5.0 | tandem stopper diameter | yes |
| `CONFIG_TANDEM_TIP_ANGLE` | 30 | tandem bend angle (degrees) | yes |
| `CONFIG_TANDEM_BEND_RADIUS` | 35.0 | tandem bend radius | yes |
| `CONFIG_TANDEM_ROTATION` | 0.0 | tandem rotation about Z (degrees) | yes |
| `CONFIG_TANDEM_THREADING_DEPTH` | 7.0 | tandem threading depth; 0 disables | yes |
| `CONFIG_TANDEM_THREADING_DIAMETER` | 5.0 | tandem diameter at base; 0 disables | yes |
| `CONFIG_NEEDLE_COLLET_OUTER_DIAMETER` | 5.0 | needle collet tolerance ring (PDF only) | yes |
| `CONFIG_TANDEM_COLLET_OUTER_DIAMETER_INNER` | 5.0 | tandem collet inner ring (PDF only) | yes |
| `CONFIG_TANDEM_COLLET_OUTER_DIAMETER_OUTER` | 8.0 | tandem collet outer ring (PDF only) | yes |
| `CONFIG_BASE_HEIGHT` | 0.0 | collar height; 0 disables the collar | yes, since 2026-10-15 (§7.1) |
| `CONFIG_BASE_THICKNESS` | 0.0 | collar wall thickness; 0 disables the collar | yes, since 2026-10-15 (§7.1) |
| `CONFIG_NOTCH_ENABLED` | 1 | 1 adds the orientation notch, 0 leaves it off (§5.4) | yes. Apply writes it, a config import fills the Cylinder tab's control |
| `CONFIG_NOTCH_ANGLE` | 0.0 | notch position, degrees clockwise from Anterior as the sheet draws it | as above |
| `CONFIG_NOTCH_WIDTH` | 2.0 | notch width | as above |
| `CONFIG_NOTCH_DEPTH` | 1.8 | how far the notch stands out of the wall | as above |
| `CONFIG_NOTCH_HEIGHT` | 10.0 | notch height from the base, capped at the collar height | as above |

**Where the physical defaults come from.** `3D Models and Templates/Values for Cylinders
(1).docx` lists the physicist's cylinder dimensions, and six of them match the defaults above
exactly: needle thread diameter 3.17, needle channel 2.7, tandem channel 3.8, tandem tap 5.0,
tandem thread depth 7, cylinder length 160. One does not. The document gives **needle thread
depth 4.5 mm**, and `CONFIG_CHANNELS_THREADING_DEPTH` defaults to **5.0**. *Verified* by
reading both. Which value is correct is **not verified**. Ask the physicist before changing
either. The collet defaults also match the collet models in that folder: the needle collet body
is 5 mm across, and the tandem collet head is 8 mm. The QA checklist in the same folder adds
0.6 cm to interstitial lengths for plastic needles, which is the 6.0 of `CONFIG_DEADSPACE`.
Chapter 1 of [the init guide](COSC499-BRACHIFY-INIT-DOCS.md#1-3d-models-and-templates) has the full comparison.

Adding a setting touches **four** places: `settings/defaults.py`, `resetAllValues()` and
`getCurrentValues()` in `settings/reset.py`, and the owning view's `__init__`.

### 6.3 User state on disk

`~/brachify/` (`classes.info.USER_PATH`, created at logger import):

| File | Written by | Contents |
|---|---|---|
| `app.log` | `logger.py` | rotating, 25 MB × 3 backups |
| `filepaths.json` | `MainWindow.closeEvent` | `most_recently_opened_config_file`, `most_recently_saved_config_file` |

`most_recently_saved_config_file` is stored but never read — it is reserved for future use.

### 6.4 Export formats

| Button | Format | Produced by |
|---|---|---|
| Export Mesh | `.stl` (binary) or `.step`/`.stp` | `_final_mesh()` — booleans cut out of the cylinder |
| Export Shape(s) | `.step`/`.stp` | `_final_shape()` — a `TopoDS_Compound` keeping parts separate |
| Export Reference Sheet | `.pdf` (+ `basemap.png` alongside), with the cylinder table since 2026-10-15 | `template_reference.generate_pdf` |
| Export Current Settings as Config | `.json` | `getCurrentValues()`, every key since 2026-10-15 (§7.1) |

### 6.5 The User Manual against the code

[`user_guide/Brachify User Manual.docx`](../../user_guide/Brachify%20User%20Manual.docx) is the
clinician's guide. It is inherited from upstream and never edited (§9.0), so where it has drifted
from the code, the difference is recorded here. Its full text was checked against the code for
the init guide ([chapter 19](COSC499-BRACHIFY-INIT-DOCS.md#19-user_guide)). Its screenshots were not compared
with the current UI.

**Where the manual is wrong or incomplete.** *Reasoned from code* unless marked.

| The manual says | The code does |
|---|---|
| §1–2: the central axis must be labelled `Central Axis`, and a dose-delivering central needle needs a different label | The code matches `Central Axis` as a substring on Varian plans, so a "different" label that contains the phrase still matches (§3.2). *Verified* |
| §1–2: give the Central Axis zero dwell time | Nothing reads the dwell times. Both samples give it 222.8 s (§3.2). *Verified* |
| §2: give the Oncentra central axis channel number 1 | Neither reader checks the channel number. It is matched by name only (§3.2) |
| §1–2: ensure no needles intersect | Nothing checks this. `are_colliding()` is never called (§7.4) |
| 4.4: a selected channel changes from blue to purple | On the Channels tab a channel is teal, `[0.2, 0.55, 0.55]`, and a selected one is blue, `[0.2, 0.2, 0.7]` ([channels_view.py:15-18](../../src/windows/views/channels_view.py#L15-L18)). *Verified* |
| 4.4: describes *Set as Tandem*, not what *Clear Tandem* does | *Clear Tandem* on the Channels tab does nothing (§7.8) |
| 4.4: lists *Dead Space* in the layout, but never explains it | `CONFIG_DEADSPACE` extends each needle tip outward, in the model and in the interstitial lengths (§5.4, §5.8) |
| 4.3: Collar Thickness "changes the diameter of the collar" | It is the collar's wall thickness. The collar's diameter is the cylinder diameter plus twice the thickness (`outer_radius = radius1 + base_thickness`, [cylinder.py:136](../../src/classes/mesh/cylinder.py#L136)) |
| 4.6: the Export tab shows the orientation notch removed from the cylinder | The notch is fused on as a raised bar (§5.4). `_final_mesh()` cuts out only channels and tandem ([export_view.py:202-210](../../src/windows/views/export_view.py#L202-L210)). *Verified* |
| 4.6: Export Mesh saves an STL | The save dialog offers STL or STEP ([export_view.py:69](../../src/windows/views/export_view.py#L69), §6.4) |
| 4.5: refers to "Section 4.5 Channels" | Channels is §4.4 of the manual |

**Confirmed against the code.** After a DICOM import the app switches to the Export tab
([import_view.py:142](../../src/windows/views/import_view.py#L142)). The Export tab's labels
match `export_view.ui` exactly. *Show Tandem* is disabled when there is no tandem. The mouse
controls match §5.7. An imported tandem must be STEP (§5.4).

**Only in the manual.** These are not repeated here, because they are for clinicians, not
developers. Read the manual for them:
- installing a release build from `github.com/brachify/brachify-release` (not checked),
- the click-by-click TPS export steps for BrachyVision and Oncentra, with screenshots,
- that an imported tandem's origin must be at the base of the cylinder, `(0,0,0)`, and that
  rotation 0° keeps its STEP-file direction, while a generated tandem at 0° points along +x,
- that *Generate Tandem* replaces any existing tandem, imported or generated, and that each tab's
  *Apply* button must be pressed or the change is not kept.

---

## 7. Known bugs, traps, and dead code

Everything here was found by reading the code during the 2026-09-21 audit, unless its entry
gives a later date. §7.7 to §7.9 were found between 2026-09-29 and 2026-10-02, while writing
[COSC499-BRACHIFY-INIT-DOCS.md](COSC499-BRACHIFY-INIT-DOCS.md) (the init guide), by reading the code and by running
brachify's own code headless on copies of the sample folders. They sit at the end so the existing
section numbers, which other files cite, stay stable. An entry that has since been fixed says
**Fixed** with the date and stays listed. Severity is our judgement, not upstream's.

### 7.1 HIGH — the collar is never saved to, or loaded from, a settings file

**Fixed 2026-10-15.** `getCurrentValues()` now returns both collar keys, read from the live
settings that *Apply Settings* writes, and `resetAllValues()` fills the two collar boxes before
it applies. `TandemView.action_set_tandem()` now merges the snapshot into the live settings
with `config_values.update(getCurrentValues())` instead of replacing them, so *Generate Tandem*
cannot drop a key the snapshot leaves out. *Verified* 2026-10-15 on macOS by four tests in
`tests/views/`, each watched failing before the fix: every default key is in the snapshot, an
applied 3 mm × 10 mm collar is exported, a 4 mm × 12 mm collar loaded from a config fills the
boxes, and a setting the snapshot does not list survives *Generate Tandem*. Not changed: the
*Add Collar* tick box is not a setting, so a config file still cannot turn the collar on or
off (*Reasoned from code*). The text below is the bug as it was.

*Corrected 2026-10-02.* The 2026-09-21 audit described this as the collar disappearing after
*Generate Tandem*. Running the real tabs headless on `SI_C_D30 Brachify_Ex2/` for the init guide
showed that it does not, in that sequence. The bug is real, but it lives in the settings file.
See [17.4 of the init guide](COSC499-BRACHIFY-INIT-DOCS.md#174-cylinder_viewpy-the-cylinder-tab)
and [13.6](COSC499-BRACHIFY-INIT-DOCS.md#136-resetpy-into-the-boxes-and-back-out) there.

`getCurrentValues()` ([settings/reset.py](../../src/settings/reset.py)) returns **17 of the 19**
config keys. It omits `CONFIG_BASE_HEIGHT` and `CONFIG_BASE_THICKNESS`. *Verified.* Two things
follow.

**1. The settings file loses the collar.** *Verified* for the export and the import:

- *Export Current Settings as Config* writes `getCurrentValues()`, so the file has no collar.
- *Import Config File* of such a file reports both collar keys as not found and keeps the
  current values (`load_config_file`), and `resetAllValues()` does not touch the collar spin
  boxes either. A collar typed into a config file by hand is therefore not shown in the boxes.
- So collar geometry cannot be saved or shared through a config file at all. A clinician who
  reopens a saved configuration gets whatever collar the app had before, which is usually none.

**2. *Generate Tandem* drops the collar keys from the live settings, but the cylinder keeps its
collar.** `TandemView.action_set_tandem()` ([tandem_view.py:59](../../src/windows/views/tandem_view.py))
ends with `get_app().values.config_values = getCurrentValues()`, replacing the whole live dict
with the 17-key version. `BrachyCylinder.shape()` reads the collar from the live dict with a
default of `0.0`, and `add_base()` does nothing when either is zero. But `shape()` returns the
solid the last setter stored (§5.4), so the cylinder already built keeps its collar, and the next
*Apply Settings* writes both keys back from the spin boxes before it rebuilds. *Verified*:

| Step | Live collar keys | Cylinder volume | Collar |
|---|---|---|---|
| tick *Add Collar*, thickness 3, height 10, *Apply* | 10, 3 | 112,709.4 mm³ | there |
| *Generate Tandem* | **missing** | 112,709.4 mm³ | still there |
| the Export tab's solid | missing | 100,198.9 mm³, collar and tandem hole | still there |
| length 150, *Apply* | 10, 3 again | 105,640.8 mm³ | there |

The latent risk: any rebuild that calls a setter between *Generate Tandem* and the next *Apply*
would build with no collar. No such path was found in the app (*Reasoned from code*; the only
other `setLength` caller, `CylinderModel.update_height_offset`, is never connected, §7.9). Not
checked: every path, in the GUI.

Suggested fix, test first: add both keys to the `current_values` dict in `getCurrentValues()`,
push them into the spin boxes in `resetAllValues()`, and change `tandem_view.py:59` to
`config_values.update(getCurrentValues())` so a partial snapshot can never drop keys again.

### 7.2 MEDIUM — unsupported TPS vendor raises an unhandled `UnboundLocalError`

`read_dicom_folder()` ([dicom/fileio.py](../../src/classes/dicom/fileio.py)):

```python
if manufacturer == "Varian Medical Systems":
    data = load_varian_dicom_data(rp_file, rs_file)
if manufacturer == "Nucletron":
    data = load_nucletron_dicom_data(rp_file, rs_file)
else:
    pass
return data
```

Any other manufacturer leaves `data` unbound. The caller in
[import_view.py](../../src/windows/views/import_view.py) catches it with a bare `except` and
logs `"Empty folder selected."` — a misleading message for what is actually an unsupported
vendor. Note also that the second `if` should be `elif`; as written, a Varian plan evaluates
the Nucletron test too (harmlessly, but it is clearly not what was meant).

### 7.3 MEDIUM — `create_point()` can return `None`, then gets indexed

[`mesh/channel.py`](../../src/classes/mesh/channel.py):

```python
check = [0, 1]
try:
    check = create_point(p1, p2, radius)
except:
    pass
if (check[1]):
```

`create_point()` returns a 2-tuple on its `else` branch but **falls off the end returning
`None`** when `length < TIP_LENGTH` (2.5 mm). In that case `check` becomes `None` and `check[1]`
raises `TypeError` outside any handler. A plan whose first two needle points are closer than
2.5 mm apart would hit this.

Separately, the `except` branch a few lines later calls `fix2(p1, p2, radius)` while `fix2()`
is defined to take **no** arguments — a `TypeError` inside an already-failing path.

### 7.4 LOW — dead code and stale files

| Item | Problem |
|---|---|
| `get_cylinder_from_dicom()` in `dicom/fileio.py` | never called; passes `tip=`/`base=` to a `BrachyCylinder.__init__` that accepts neither — would raise `TypeError` |
| `benchmarks/benchmarking.py` | `total` used before assignment → `NameError` |
| `benchmarks/channels.py` | imports `Application.BRep.Channel` and `testing.data.channels`, neither of which exists; contains a hardcoded `C://Users//nsmel//...` path |
| `requirements.txt` | unused and stale — typo `matlplotlib`, and every pin disagrees with `spec-file.txt` (PySide6 6.9.3 vs 6.8.1, pydicom 2.4.3 vs 3.0.2, pyinstaller 6.0.0 vs 6.20.0). It has no `pytest`. **Do not use it.** The dependency list is in §1.1 |
| **Fixed 2026-09-30.** `build_executable.py` hidden imports `pydicom.encoders.gdcm` and `pydicom.encoders.pylibjpeg` | found 2026-09-30. pydicom 3, the version pinned since the lockfile was made, moved both modules to `pydicom.pixels.encoders.*`. PyInstaller logged `ERROR: Hidden import 'pydicom.encoders.gdcm' not found` (and the same for `pylibjpeg`) and built anyway with exit 0 (*Verified* 2026-09-30 by a trial build on macOS). Both now name `pydicom.pixels.encoders.*`, the trial build analyses them with no error, and `tests/tooling/test_build_executable.py` guards the list. Probably harmless before the fix, since the app never decodes pixel data (*Reasoned from code*). *Not verified:* a Windows `.exe` build |
| `intersections.are_colliding()` | defined, never called — needle collision detection is not performed |
| `AppSignals.exportFile` | declared, never emitted, never connected |
| `DicomData.central_axis_flag` | set in `__init__`, never read. **Fixed 2026-10-10:** it was missing from `reset()`. `reset()` now clears it, guarded by `tests/dicom/test_data.py`. *Verified*: the test failed naming `central_axis_flag` before the fix |
| `add_notch(z_offset=...)` | the parameter is computed and passed but the translation is commented out, so the notch is always at `z=0` even with a collar |
| `generate_cylinder_points` / `get_surface_intersection` / `get_interstitial_length` in `mesh/channel.py` | duplicated (worse) copies of the `template_reference.py` versions; unused |
| `.vs/brachify/v17/.wsuo`, `src/windows - Shortcut.lnk` | Windows-only artifacts committed by accident |
| `3D Models and Templates/readme.txt` | lists "3D Models of Wrenches" and "Template Cylinders - Multi channel and Universal", but the folder holds neither. It has four collet parts (`.SLDPRT`, three with `.STL`), two collet drawings (`.pdf`), `Values for Cylinders (1).docx` and `3D Printed Cylinder QA.docx` (*Verified*). The readme is inherited from upstream, so it is not edited |
| `notes/deployment.txt`, `notes/background_color.txt` | stale. The first gives the old `pydicom.encoders.*` hidden imports; the second says to add a `background.png` that does not exist ([4.2 of the init guide](COSC499-BRACHIFY-INIT-DOCS.md#42-where-the-notes-have-gone-stale)). Inherited, so not edited |
| further unused functions | `extract_points_from_channels`, `get_last_xy_points`, `get_point_at_z0` (would crash if called) and `index_before_negative_point` in `template_reference.py`; `make_arc`, `make_point`, `make_cylinder`, `make_curved_pipe`, `show_cylinder`, `make_thru_shape` in `tandem.py`; `remove_shapes`, `set_shape_colour`, `set_shape_visibility` in `display_model.py`; `DrawBox` in `viewport.py`; `explore_rp_rs` in `dicom/fileio.py`; `src/windows/palettes.py` as a whole. `calculate_protrusion_lengths` is called but its result is never used. *Reasoned from code* |
| `.gitignore`, lines 177 and 179 | leftover merge-conflict markers, `=======` and `>>>>>>> main`, around a `files` entry. Git reads each marker as an ignore pattern. Inherited from upstream, whose `.gitignore` carries the same lines (*Verified* 2026-09-25 against `upstream/main` at `f89cafe`). Harmless today, since no file is named after a marker, but delete both lines when someone next edits `.gitignore` |

### 7.5 LOW — cross-platform rough edges

- `QIcon("resources\\brachify_splash-ico.ico")` in
  [app.py](../../src/classes/app.py) and [main_window.py](../../src/windows/main_window.py) uses
  a Windows path separator. On macOS/Linux this silently yields a null icon. Cosmetic.
- `spec-file.txt` is `win-64` only (§1.2). macOS and Linux install the same dependencies
  from the command in §1.2, but nothing locks their versions, so they can differ from
  Windows (§1.1).
- **Fixed 2026-10-08 on the Channels tab only: spin box arrows were invisible on macOS in dark
  mode.** Each spin box's stylesheet paints its field white, but in dark mode macOS still
  draws the native up and down arrows white, for a dark background, so they vanish.
  `ChannelsView` now sets a stylesheet that draws its four spin boxes' arrows from black
  images (§5.6), and leaves the rest of the app, the file dialogs included, in the OS colour
  scheme. *Verified* 2026-10-08 on macOS in dark mode by rendering the Channels spin box, and
  by `test_channels_spin_box_arrows_are_black`. *Verified* again 2026-10-13 after merging
  `main`, in the app itself on macOS in dark mode (the native `cocoa` platform): with Ex1
  imported through *Import Dicom* and the Channels tab open, `QWidget.grab()` of all four
  spin boxes gave a darkest pixel of 39 in the up arrow and 1 in the down arrow. The 3D
  viewport was not captured. *Still open:* the spin boxes on the Cylinder,
  Tandem and Export tabs have the same invisible arrows in macOS dark mode. *Not verified:*
  Windows, where the images replace the native arrows too.

### 7.6 Traps that are not bugs — know these before editing

- **Fixed 2026-10-08 in PR #19: the Channels list kept a channel highlighted after leaving
  the tab.**
  Select a channel in the Channels tab, go to another tab and come back. `on_close` cleared
  `ChannelsModel.selected_channels`, so the viewport drew no channel as selected, but nothing
  cleared the `QListWidget`, which still showed the channel highlighted and still held it as
  its current item. Because Qt emits `currentItemChanged` only when the current item changes,
  clicking that channel again did nothing until a different one was clicked first.
  **Fixed 2026-10-10 in PR #19, the same drift after a viewport pick.** Click Applicator2 in
  the list, pick Applicator3 in the viewport, then click Applicator2 in the list again.
  `ChannelsModel.set_selected_shapes` moved the model to Applicator3, and the view highlighted
  it with `setSelected`, but the list's current item stayed Applicator2. The second click
  emitted nothing, so the model stayed on Applicator3, and Disable and Set as Tandem acted on
  a channel other than the one highlighted. `ChannelsView.action_update_settings` now sets
  the list's current row to the model's selected channel, or to `-1` when there is none,
  inside a `QSignalBlocker`, so the list follows the model however the selection changed.
  That also covers a viewport click on empty space (*Reasoned from code*, not tested).
  *Verified* by the four tests in `tests/views/test_channels_view.py`: the two tab-switch
  tests failed before the first fix, and the two viewport-pick tests failed on the code before
  the second. *Verified* 2026-10-10 on Ex1 on macOS by clicking through both in the
  running app.
- **Import `classes.mesh.cylinder` only after the `QApplication` exists.**
  `BrachyCylinder.__init__` takes `diameter=get_app().values.config_values.get(...)` as a
  default argument, and Python evaluates that once, when the module is imported. Before the
  app is constructed, `get_app()` returns `None` and the import raises `AttributeError:
  'NoneType' object has no attribute 'values'`. The app never meets this, because `app.gui()`
  imports the windows after the app exists, but a test or script that imports the mesh,
  DICOM or window modules first will. *Verified* 2026-10-08 while writing
  `tests/views/conftest.py`.
- **OpenCASCADE's viewer cannot start without a display.** Running the full `app.gui()` with
  `QT_QPA_PLATFORM=offscreen` exits 139, a segfault, during `MainWindow.initViews()`. A headless
  test must create `OrbitCameraViewer3d` and never call `InitDriver()` or show it, as
  `tests/views/conftest.py` does. *Verified* 2026-10-08 on macOS.

- **Fixed 2026-10-04: diagrams in subfolders were skipped by the architecture build.**
  Moving UML and DFD sources into `existing-framework/` left broken viewer links;
  the old non-recursive discovery also missed stale projected diagrams. The build now
  discovers nested sources and retains relative paths in viewer links and embedding
  checks. *Verified* by four regression cases in `tests/tooling/test_architecture_build.py`,
  watched failing before the fix and again after deliberately reverting discovery.

- **Fixed 2026-10-10: clicking Export before any cylinder existed broke navigation.**
  `NavigationModel.set_page` records the new page before calling `on_open`, and
  `Export_View._final_mesh` then raised `AttributeError` on the missing cylinder. The app
  believed it was on Export while the screen still showed the previous tab, and a second click
  on Export did nothing. The Export button is now disabled, and drawn grey, until
  `CylinderModel.values_changed` fires (§5.6). Its highlight no longer waits for a DICOM import,
  so opening Export after *Apply Settings* alone highlights it too, and the
  `ImportView.dicom_file_opened` flag that guarded it is gone. *Verified* 2026-10-10 on macOS,
  headless: before the fix the click left `current_page` at 4 with the Import page showing;
  after it the button is disabled, and *Apply Settings* or importing Ex1 enables it. Guarded by
  [tests/windows/test_main_window.py](../../tests/windows/test_main_window.py).
- **A new way to make a cylinder must go through `CylinderModel`.** The Export tab is enabled
  by `CylinderModel.values_changed`, which `load_data` and `update_cylinder` emit. Code that
  assigns `cylindermodel.cylinder` directly leaves Export disabled.
- **`BrachyCylinder.shape()` returns a stored solid but never stores one.** Only the three
  setters store `self._shape`. A new mutator must clear it and rebuild it, as they do, or the
  viewport and the export keep the old solid (§5.4).
- **`BrachyCylinder`'s default diameter is fixed when the module is imported.** The default
  argument reads `CONFIG_CYLINDER_DIAMETER` once, so a later settings change never reaches it.
  Every caller passes a diameter today. *Reasoned from code.*
- **The default Tandem Height (170) is taller than the default cylinder (160).** `Tandem()`
  with its defaults fails to build (*Verified*). The app avoids it only because import caps the
  Tandem Height spin box at the cylinder length. A test or new code calling `Tandem()` must pass
  a height.
- **The Varian Central Axis match is a substring match** (§3.2). Do not label a dose-carrying
  needle with a name that contains `Central Axis`.
- **`NavigationModel.views` order is frozen** (§4.3). It is indexed positionally everywhere.
- **`@display_action` is mandatory** on any view method that changes geometry (§4.5).
- **`DicomData.__init__` and `reset()` must stay in sync** (§5.3). A missing field only leaks
  after an import that fails partway, since each import builds a new `DicomData`.
  `tests/dicom/test_data.py` fails if they drift apart.
- **Adding a config key touches four places** (§6.2).
- **`*_ui.py` files are generated** — edit the `.ui` and re-run `pyside6-uic` (§5.6).
- **Cylinder spin box values are in the selected display unit.** Use the seven
  `LengthField.millimetres` values for Apply, and `set_dimensions_mm` and `set_notch_settings` for model/config
  updates. Writing mm directly to a widget while cm is selected scales the device by ten.
  Reading a rounded display on a unit switch loses precision. *Verified* by the offscreen
  configuration and repeated-switch cases (§5.6).
- **The two tandem rotation spin boxes** must be written together (§5.6).
- **Varian and Nucletron readers are parallel** — a fix in one usually needs a mirror fix
  (§5.3).
- **Bare `except:` is pervasive.** When debugging, expect failures to be swallowed; add a
  temporary `log.exception()` rather than trusting the absence of an error message.
- **Fixed 2026-09-25: the anti-slop plugin did not lint the Python app.** It was an oxlint
  plugin, and oxlint reads only JavaScript and TypeScript, so a passing hook said nothing
  about `src/`. The related trap, that `npx oxlint` exits 1 with nothing to lint, went with
  it. The plugin was replaced by anti-slop-py, which reads Python (§1.9).
- **A clean `anti_slop review` covers only the lines you changed.** It hides every existing
  finding in untouched lines, and it lets the five policy rules through as warnings. It is
  not a statement that `src/` is clean (§1.9). Verified 2026-09-25.
- **Fixed 2026-10-01: `docs/architecture/build.py --check` failed on every Windows clone.**
  It hashed each `.mmd` as raw bytes, and Git on Windows (`core.autocrlf=true`, the default)
  checks text out with CRLF line endings, so the hash never matched the stamp written on an LF
  checkout. On an unedited `main` it reported every diagram stale and exited 1, which
  blocked the pull-request gate, and re-rendering would only have moved the failure to LF
  clones. `digest()` now hashes the LF form. *Verified* on Windows: before the fix `--check`
  exited 1 on a clean checkout (three diagrams on 2026-10-01, all four on 2026-10-04 once
  `system-architecture.mmd` existed), after it exited 0. Guarded by
  [tests/tooling/test_architecture_build.py](../../tests/tooling/test_architecture_build.py).
- **Fixed 2026-10-04: `docs/architecture/build.py` could not render a diagram on Windows.**
  `render()` started mermaid-cli as the bare name `npx`. On Windows npx is `npx.cmd`, which
  `subprocess` does not find by name, so every render raised `FileNotFoundError` even with Node
  installed, and no Windows clone could redraw a diagram. `npx()` now resolves the full path
  with `shutil.which`, and exits with a message when Node is missing. *Verified* on Windows: the
  new test in `test_architecture_build.py` failed with `FileNotFoundError` before the fix and
  passed after it, and `build.py` then rendered three diagrams.
- **Fixed 2026-10-04: the drift check reported backslash paths on Windows.** `package_drift`
  and `window_drift` printed `relative_to()` paths with the OS separator, so the same missing
  module read `src\classes\mesh\...` on Windows and `src/classes/mesh/...` elsewhere, and 5 of
  the 8 tests in `test_architecture_drift.py` failed on every Windows clone, `main` included.
  Both now print `.as_posix()`. *Verified* on Windows: 5 failed before, all 8 passed after.
- **Config import can leave `ChannelsModel.diameter` stale.** Import replaces the config before
  Apply compares it with the spin box, so the model can retain its startup diameter while new
  channels use the imported setting. Clearing an own diameter now uses
  `NeedleChannel.default_diameter()`, matching newly imported channels. The wider config-import
  synchronization issue remains: `getCurrentValues()` still reads the cached model diameter.
  *Reasoned from code*; the regression loads 3 mm, imports Ex1 and clears a 4 mm override.
- **A channel's own diameter is not in the PDF or a config file.** `save_points_diagram` draws
  every channel circle, and its collet rings, at `CONFIG_CHANNELS_DIAMETER`, and
  `getCurrentValues()` writes only the global diameter. The 3D export is correct, because it
  cuts `channel.shape()`, so a reference sheet checked against a cylinder printed with own
  diameters disagrees with it. FR-CN-07 is the follow-up. *Reasoned from code*.


### 7.7 MEDIUM — a tandem channel's rotation is measured from `(1, 0)`, not the axis

*Verified* on a changed copy of `SI_C_D30 Brachify_Ex2/`, 2026-09-29 to 2026-10-02; not seen in
the GUI.

`NeedleChannel.get_rotation()` ([mesh/channel.py:152-158](../../src/classes/mesh/channel.py#L152-L158))
gives the angle that *Set as Tandem*, and a channel labelled `Tandem` at import, write into the
tandem rotation. Its comment says it measures "using 0,0". The code measures from `(1, 0)`:

```python
v1 = [1.0, 0.0, self.points[0][2]]
v2 = self.points[0]
angle = math.atan2(v2[1] - v1[1], v2[0] - v1[0]) * (180 / 3.14159)
```

That is `atan2(y, x - 1)`, where `points[0]` is the tip in cylinder-local coordinates, whose
axis is `x = y = 0` (§4.6). With Ex2's tandem tip moved 6 mm to one side, the tandem was aimed at
**32.7°**, while the tip's true direction from the axis is **30.0°**
([10.8 of the init guide](COSC499-BRACHIFY-INIT-DOCS.md#108-what-happens-if-a-value-in-the-file-changes)).
Evaluating the formula directly, *Reasoned from code*:

| Tip `(x, y)` | Code gives | Angle from the axis | Error |
|---|---|---|---|
| (10, 0) | 0.0° | 0.0° | 0 |
| (5, 5) | 51.3° | 45.0° | +6.3° |
| (0, 10) | 95.7° | 90.0° | +5.7° |
| (2, 2) | 63.4° | 45.0° | +18.4° |

The error is zero when the tip lies on the +x axis beyond `x = 1`, and grows as the tip nears
the cylinder axis (a tip at `(0.5, 0)` gives 180°), which is where a
tandem tip usually sits. The generated tandem then points away from the planned channel. The
unchanged samples cannot show it, because Ex2's tandem tip lies on the +x axis. Not yet checked:
that the offset is not deliberate. Fix it test first: `get_rotation()` is pure maths and a good
first test for `tests/mesh/`. Inspect the result in the Export tab.

### 7.8 LOW — *Clear Tandem* on the Channels tab does nothing

*Reasoned from code, 2026-09-29; not reproduced in the GUI.*

When the selected channel is the tandem, `btn_set_tandem` reads *Clear Tandem*
([channels_view.py:161](../../src/windows/views/channels_view.py#L161)). Pressing it calls
`action_set_tandem()` ([channels_view.py:71-106](../../src/windows/views/channels_view.py#L71-L106)),
whose only call to `ChannelsModel.set_tandem()` runs when the selected channel is **not**
already the tandem:

```python
label = None
if channel_label != data.tandem_channel:
    label = channel_label
    model.set_tandem(label)
```

So pressing *Clear Tandem* leaves `data.tandem_channel` unchanged. The channel stays the
tandem, stays disabled, and the button keeps its label. The method then only rewrites the two
rotation spin boxes. The Tandem tab's own *Clear Tandem* buttons are separate and are not
affected. The User Manual does not describe this button's clear action, so what it should do is
not written down anywhere either (§6.5). Confirm the behaviour in the running app before fixing.

**The same button also reads *Clear Tandem* when no channel is selected and the plan has no
tandem.** Found 2026-10-10. `ChannelsModel.is_channel_tandem(None)` compares
`None == data.tandem_channel`, which is true for a plan with no tandem, such as Ex1. The button
is disabled in that state, because `action_update_settings` enables it only while a channel is
selected, so only its label is wrong. *Verified* 2026-10-10 on Ex1 on macOS: after leaving the
Channels tab and coming back, the disabled button read *Clear Tandem*. It predates the
Channels list fix in §7.6, since leaving the tab already emptied the selection.

### 7.9 Further bugs found while writing the init guide

Each row links to the init guide section with the evidence. *Verified* means brachify's own code
was run headless and the result observed; nothing here was seen in the GUI.

| Severity | Where | Problem | How sure |
|---|---|---|---|
| MEDIUM | holes in `SI_C_D30 Brachify_Ex2/` | two pairs of base holes overlap: Applicator10 and 11 by 0.07 mm, Applicator5 and 6 by 0.04 mm, and several walls are under 0.25 mm. At Tandem Height 120 the tandem hole also meets needle holes. Nothing warns, because `are_colliding()` is never called (§7.4). See [11.10](COSC499-BRACHIFY-INIT-DOCS.md#1110-what-happens-if-a-setting-changes) and [11.7](COSC499-BRACHIFY-INIT-DOCS.md#117-tandempy-the-tandem) | *Verified* |
| MEDIUM | `TandemModel`, the tandem rebuild | when every try fails, as when the cylinder is shortened below the Tandem Height after a tandem exists, the rebuild ends with `cannot access local variable 'shape'`. Generating at Tandem Height 170 or 300 on Ex2's 160 mm cylinder showed five error messages first. The spin box's cap is updated only after the cylinder changes. See [15.8](COSC499-BRACHIFY-INIT-DOCS.md#158-tandem_modelpy-the-tandem) and [17.9](COSC499-BRACHIFY-INIT-DOCS.md#179-what-happens-if-something-here-changes) | *Verified* for the failure; *Reasoned from code* that the old tandem stays |
| MEDIUM | `load_nucletron_dicom_data`, no Central Axis | the `surface` fallback places the cylinder, then loads **no needle**, because `center_index` is never set. The failure is logged with the wrong cause and nothing appears on screen. See [10.6](COSC499-BRACHIFY-INIT-DOCS.md#106-elekta-oncentra-files) | *Reasoned from code*; no Oncentra sample |
| MEDIUM | `load_nucletron_dicom_data`, needle order | a structure with no points is skipped, which shifts every later needle's points onto the wrong channel by one place. The comment says an empty placeholder is added, but that line is commented out. The reader also assumes the structures are already in plan order and never re-sorts. See [10.6](COSC499-BRACHIFY-INIT-DOCS.md#106-elekta-oncentra-files) | *Reasoned from code*; no Oncentra sample |
| LOW | both readers, one-point anchors | removing one single-point "anchor" channel is correct; a second one deletes the wrong entries and shifts every later needle's name and number. The code's own comment says it works for one only. Varian warns on the first anchor, Oncentra on the second. See [10.5](COSC499-BRACHIFY-INIT-DOCS.md#105-fileiopy-how-the-form-gets-filled) | *Reasoned from code* |
| LOW | `getCurrentValues()` | crashes with `'NoneType' object has no attribute 'diameter'` if no cylinder exists yet, so *Export Current Settings as Config* before an import or *Apply* wrote nothing. Unreachable from the app since 2026-10-10, because the Export tab stays disabled until a cylinder exists (§7.6). See [13.6](COSC499-BRACHIFY-INIT-DOCS.md#136-resetpy-into-the-boxes-and-back-out) | *Verified* |
| LOW | `OrbitCameraViewer3d.keyPressEvent` | any key press in the 3D view raises `AttributeError: 'OrbitCameraViewer3d' object has no attribute '_key_map'`; Qt prints it and carries on. See [17.8](COSC499-BRACHIFY-INIT-DOCS.md#178-viewportpy-the-3d-view) | *Verified* |
| LOW | `mesh/fileio.py:54` | the write-failure path runs `from src.classes.logger import log`, while every other file imports `classes.logger`. In the `.exe` there is no `src` package, so the handler itself fails and hides the original error. See [11.8](COSC499-BRACHIFY-INIT-DOCS.md#118-helperpy-intersectionspy-and-fileiopy) | *Reasoned from code* |
| LOW | STL export | writing Ex2's model printed "6 faces have been skipped due to null triangulation" from OpenCASCADE, which can leave gaps in the STL. Which faces, and whether slicers mind, is not checked. See [11.8](COSC499-BRACHIFY-INIT-DOCS.md#118-helperpy-intersectionspy-and-fileiopy) | *Verified* for the message |
| LOW | `launch.py`, start-up failure | if `RadiotherapyApp(argv)` fails, the handler calls `input(...)`, which fails in the `.exe` with no terminal, then carries on and crashes with `'NoneType' object has no attribute 'setApplicationName'`. See [8.3](COSC499-BRACHIFY-INIT-DOCS.md#83-when-starting-fails) | *Reasoned from code* |
| LOW | `ChannelsModel.set_selected_channels` | the test for "is this a position number?" is never true, so selecting by number stores `(0,)`, which matches no needle. The app only passes labels today. See [15.7](COSC499-BRACHIFY-INIT-DOCS.md#157-channels_modelpy-the-needles) | *Verified* |
| LOW | `CylinderModel.update_height_offset` | its comment says it is connected to `height_changed`; it is not. If it were, it would set the cylinder's **length** to the offset. See [15.6](COSC499-BRACHIFY-INIT-DOCS.md#156-cylinder_modelpy-the-cylinder) | *Reasoned from code* |
| LOW | `DisplayModel` | `add_shape(enabled=False)` for a label never added raises `KeyError`; `update()` with an `EXPORT` shape under the default material table crashes. Neither happens in the app today. See [15.4](COSC499-BRACHIFY-INIT-DOCS.md#154-display_modelpy-what-the-3d-view-shows) | *Verified* |
| LOW | `palettes.py` | `dark` is a `@staticmethod` and `light` is not, so `Palettes().light(window)` would pass the wrong argument. Nothing calls either. See [14.4](COSC499-BRACHIFY-INIT-DOCS.md#144-palettespy-two-themes-nothing-uses) | *Reasoned from code* |
| LOW | `main_window.ui` | six colours are written `rgba(240, 245, 250)`, with no alpha, so Qt prints `Specified color with alpha value but no alpha given` on every start. It also asks for an icon from a Qt resource file that is not in the repository. See [18.6](COSC499-BRACHIFY-INIT-DOCS.md#186-colours-and-other-text-in-the-design-files) | *Verified* for the warning |
| LOW | the 3D view | every redraw zooms to fit, so after *Apply* or a selection any zoom the user set is lost. See [17.8](COSC499-BRACHIFY-INIT-DOCS.md#178-viewportpy-the-3d-view) | *Reasoned from code* |
| LOW | spin box limits | **Changed 2026-10-10:** Cylinder length and collar now use `QDoubleSpinBox`, with whole mm or tenths of cm displayed. `LengthField` retains exact mm settings through display rounding (§5.6); finer user editing remains limited by display precision. *Cylinder Diameter* allows 0 and *Bend Angle* allows 99.99°, because no limits were set. See [18.3](COSC499-BRACHIFY-INIT-DOCS.md#183-what-each-design-file-contains) | *Verified* from the `.ui` files |
| MEDIUM | `checkValuesExist`, a JSON `true` or `false` | **Fixed 2026-10-11.** A setting written as `true` was reported loaded and used as 1, because Python treats `True` as the int 1, so a cylinder diameter of `true` became 1 mm with no warning. `is_config_number()` now rejects `bool`, so the default is used and the key is reported missing, guarded by `tests/settings/test_load.py`. Negative and zero values still load. See [13.5](COSC499-BRACHIFY-INIT-DOCS.md#135-loadpy-reading-a-settings-file) | *Verified*: the test failed with `assert True == 30.0` before the fix |

### 7.10 HIGH — a channel disabled in one plan stayed disabled in the next

**Fixed 2026-10-15 in PR #43.** `ChannelsModel.load_data` reset the selection and the channels
but not `disabled_channels`. A channel disabled in one plan therefore stayed disabled in the next
plan imported, if that plan had a channel with the same label. Ex1 and Ex2 both label their
needles `Applicator2` to `Applicator13`. The carried-over channel was not drawn, and was missing
from `get_visible_channels()`, which the Export cut and the PDF both use, so the printed cylinder
had no hole for a needle the plan contains, and nothing on screen said so. *Verified* 2026-10-15
offscreen on macOS: with Applicator4 disabled in Ex1, importing Ex2 through the calls
`ImportView` makes left Ex2's Applicator4 disabled, out of `get_visible_channels()` and out of
`DisplayModel.shapes`. `load_data` now empties `disabled_channels` before building the channels,
so only a plan's tandem channel starts disabled. `test_loading_a_plan_enables_every_channel_again`
in `tests/views/test_channels_view.py` covers it.

### 7.11 HIGH — a flat tip was not followed by the PDF maths or the tandem

**Fixed 2026-10-15, both halves.** The tandem half: `Tandem.height_offset` grows for a flat tip
(§5.4). *Verified*: with a flat-tipped 90 mm cylinder, an 80° bend and Tandem Height 100, the
dome-sized envelope trimmed away 133.4 mm³ of cut-out inside the cylinder, and after the fix
none. A probe of 48 builds (diameters 30, 45, 60 and 90 mm, bends of 30°, 60° and 80°, Tandem
Height 100 and 130, bend radius 15 and 35, each with a dome and a flat tip) found cut-out
trimmed away only from flat tips at 60 and 90 mm before the fix, up to 133.4 mm³, and none
after. The text below is the bug as it was.

*Reasoned from code, 2026-10-15.* `CONFIG_CYLINDER_FLAT_TIP` builds a flat-topped cylinder
(§5.4). **The reference sheet's half is fixed, 2026-10-15:** interstitial lengths used to be
measured against a dome point cloud whatever the tip, and now follow it (§5.8, *Verified* by
`tests/pdf/`). Still open: the generated tandem's cut-out is trimmed by a dome
outline 10 mm larger than the cylinder, centred 1 mm below the dome's centre. A flat top's corners leave it once
√(R² + (R + 1)²) > R + 10, a diameter above about 45 mm, which could leave the tandem hole closed. Only a config file can set a
flat tip until the Cylinder tab gains the control. The tandem fix is the next change in the
same stack of pull requests.

---

## 8. Testing

### 8.1 Policy

**This project follows test-driven development**, including the superpowers iron law: no
production code without a failing test first. Code written before its test is deleted and
rewritten from the test. Every agent loads the superpowers `test-driven-development` skill at
session start (§1.10). The full rules, including the anti-slop rules, live in
[AGENTS.md](../../AGENTS.md#session-start) and
[AGENTS.md](../../AGENTS.md#testing-write-the-test-first). They are enforced by the
[pull request template](../../pull_request_template.md): write the test, watch it fail, make
it pass, then break the code on purpose to confirm the test catches it.

Test files are **scoped by subfolder** mirroring `src/` — `tests/mesh/`, `tests/dicom/`,
`tests/views/`, `tests/settings/`, and so on. Tests of repository files outside `src/`
(`build_executable.py`, `.gitattributes`, `docs/architecture/build.py`) go in `tests/tooling/`. Nothing sits loose at the
root of `tests/`. Every function in `tests/` has a docstring saying what it checks, how it
fails, and why that matters
([AGENTS.md](../../AGENTS.md#every-function-in-tests-explains-itself)). See
[tests/README.md](../../tests/README.md). `utils/` follows the same scoping rule; see
[utils/README.md](../../utils/README.md).

### 8.2 Current state

*Verified 2026-10-11 on macOS after merging main into the structure-reader branch:*
`python -m pytest -q` passed all 63 tests. The anti-slop review against `origin/main`
reported no findings, and the architecture check passed. No manual GUI run was performed
for this documentation conflict resolution.

*Verified 2026-10-11 on macOS before merging main:* 44 tests passed, including 24
RTSTRUCT reader cases. Reader tests were run red before implementation; deliberate
mutations dropping later contours and accepting nonfinite coordinates were caught,
then restored. The anti-slop review reported no findings. No GUI or Windows run was
performed for the standalone reader change.

[tests/dicom/test_structures.py](../../tests/dicom/test_structures.py) covers the
standalone RTSTRUCT reader (§5.3), alongside the application tests below.

**`DicomData` is tested in `tests/dicom/`, the main window's Export tab in `tests/windows/`,
and the Channels view and Cylinder display units in `tests/views/`.**
[tests/dicom/test_data.py](../../tests/dicom/test_data.py), added 2026-10-10, checks that a new
`DicomData` starts empty and that `reset()` clears every field `__init__` declares. The first
tests of `src/`, added 2026-10-08, test the Channels view's list selection. The main window
tests in [tests/windows/](../../tests/windows/) were added 2026-10-10. The pure functions in
§8.3 still have none.

For Cylinder display units, the real offscreen window,
models and controls exercise startup, all four cm displays, scaled steps and limits,
pending edits, mm Apply and exported config dimensions, config reset before/after a
cylinder exists, and Ex1 import with a 10 mm needle offset. The native canvas is never
initialised.

*Verified* 2026-10-10: all eight new cases failed before implementation; 28 suite cases
passed afterwards. Three deliberate breaks (cm scale, Apply conversion, rounded mm
cache) each failed the relevant assertions. No application module is mocked.

**Config loading is tested in `tests/settings/`.** `test_load.py`, added 2026-10-11, loads real
JSON files from a temporary folder: a file with one key, a file that is not valid JSON, and a
`true` dimension.

Both view test files share the one QApplication from the `units_app` fixture in
[tests/views/conftest.py](../../tests/views/conftest.py), which isolates HOME/USERPROFILE.
`channels_window` and `cylinder_window` build their windows on it. Qt allows one QApplication
per process, so a fixture that constructed its own would fail in whichever file ran second.
`brachify_app` in [tests/windows/conftest.py](../../tests/windows/conftest.py) follows the same
rule: whichever of the two session fixtures runs first starts the app, and the other reuses it.

Repository tooling tests, first added 2026-09-30, live in
[tests/tooling/](../../tests/tooling/). Every test file, and what makes it fail:

| Test | Fails when |
|---|---|
| `dicom/test_data.py` | a new `DicomData` starts with a field that is not `None`, or `reset()` leaves a field `__init__` declares holding the previous import's value (§5.3) |
| `dicom/test_load_structures.py` | `load_structures` does not store decoded ROIs on `DicomData.structures`, or a failed decode leaves a previous value instead of `None` (§5.3) |
| `views/test_channels_view.py` | after a channel is selected and the Channels tab is left and reopened, the list still highlights it or holds it as the current item, or clicking it again does not select it in `ChannelsModel`. Or, after a channel is picked in the viewport, the list does not highlight only that channel, or clicking the channel clicked before the pick does not select it (§7.6). Also fails if an arrow of a Channels spin box is drawn lighter than black (§7.5), or if a channel disabled before a plan is loaded is still disabled, or missing from `get_visible_channels`, afterwards (§7.10). Or a channel's own diameter is overwritten by the Channels tab's Apply, survives being cleared or a new plan, or accepts less than 0.3 mm or NaN (§5.5). Also checks that clearing after config import matches untouched channels and unknown labels leave no override (§7.6) |
| `views/test_cylinder_view.py` | display conversion, mm model/config dimensions, precision preservation, scaled limits or imported needle offsets regress, or a config snapshot leaves out a default key or the collar, or a config import does not fill the collar boxes (§7.1), or a notch control is not applied, does not grey out, ignores the units, or is not filled by a config import, or *Tip Shape* is not applied or not filled by a config import (§5.6) |
| `mesh/test_notch.py` | the default `NotchSettings` move or resize the notch, sheet angle 90 does not land on +x, width, depth or height is ignored, or a config key is misread or a missing one is guessed (§5.4) |
| `mesh/test_cylinder.py` | the default cylinder's volume or extents change, a disabled notch is still fused on, the angle setting is ignored, or the notch height ignores its setting or the collar cap, or a flat tip still builds the dome (§5.4) |
| `mesh/test_tandem.py` | the default dome tandem cut-out's volume changes, or a flat-tipped 90 mm cylinder's tandem cut-out is trimmed inside the cylinder (§7.11) |
| `pdf/test_template_reference.py` | an interstitial length past a dome, past a flat top, or out of a flat-tipped cylinder's wall near its top differs from the hand-worked length, or the notch is drawn in the wrong place, size or turn, or drawn when off, or the labels overlap it, or the cylinder table misreports a value (§5.8) |
| `views/test_tandem_view.py` | *Generate Tandem* drops a live setting that `getCurrentValues()` does not list (§7.1) |
| `settings/test_load.py` | a config file's keys are not loaded, missing keys are not filled from the defaults and reported, an unreadable file is counted as loaded, or `true` is accepted as a dimension (§7.9) |
| `test_architecture_build.py` | nested diagrams are omitted from the viewer, or missing, stale or unembedded nested SVGs pass the CLI check, or `build.py` reads an unchanged diagram checked out with CRLF line endings as stale, or an edited diagram as current, or the `npx` it renders with cannot be started (§7.6) |
| `test_build_executable.py` | a module in `build_executable.HIDDEN_IMPORTS` cannot be imported (§7.4) |
| `test_line_endings.py` | a tracked `*.sh` would not be checked out with LF, or the session-start hook is no longer tracked (§1.10) |
| `test_architecture_drift.py` | a module, package, model or view in `src/` is not named in `docs/architecture/diagrams/system-architecture.mmd`, which is also what `build.py --check` reports |
| `windows/test_main_window.py` | clicking Export before a cylinder exists leaves the Import page, the disabled Export button looks like an enabled one, or *Apply Settings* alone or an Ex1 import does not make Export usable and highlighted (§7.6) |

The `windows/` tests drive the real `MainWindow`, models and five views offscreen, through the
`fresh_window` fixture in [tests/windows/conftest.py](../../tests/windows/conftest.py). The 3D
canvas is created but never initialised, because OpenCASCADE's viewer segfaults without a
display, and `HOME` points at a temporary folder so `~/brachify` is never touched. Two traps
shape it. The mesh modules can only be imported after the app exists, because
`BrachyCylinder.__init__` calls `get_app()` in a default argument. And the app's signals
outlive every window, so a second window in the same run also drives the first one's
navigation and models unless the fixture disconnects them, which it does after each test.

Run them from the repository root, in the conda environment:

```bash
python -m pytest
```

- *Verified* 2026-09-30 on macOS: 5 passed. Each test was watched failing before its fix, and
  failing again when the fix was reverted on purpose.
- *Verified* 2026-10-02 on macOS: 13 passed, with `test_architecture_drift.py` added. The drift
  check itself was written before its tests, which the test-first rule forbids. The tests were
  then written against a `drift(src, mmd)` signature the code did not have yet and watched
  failing (6 of 7 red). The 8th test, for files inside a new package, was red first and then
  fixed. Two deliberate breaks of the check, and one stale diagram, were each caught.
- *Verified* 2026-10-04 on macOS: 17 passed, including four nested-diagram CLI cases.
  `python docs/architecture/build.py --check` also passed for all seven diagrams.
- *Verified* 2026-10-04 on Windows, outside conda: 17 passed with
  `--ignore=tests/tooling/test_build_executable.py`, which needs PyInstaller from the conda
  environment. Before the two Windows fixes in §7.6, 5 of the drift tests failed here and the
  `npx` test failed with `FileNotFoundError`. `build.py` rendered on Windows and `--check`
  exited 0 for all seven diagrams.
- *Verified* 2026-10-08 on macOS, in an environment made with the §1.2 command: 22
  passed in about 18 seconds. Both `test_channels_view.py` tests were watched failing before
  the fix, the second also when run alone, and failing again when the fix was replaced with
  `clearSelection()` alone. Their `channels_window` fixture in
  [tests/views/conftest.py](../../tests/views/conftest.py) builds the real window, models and
  views offscreen with the canvas never initialised (§7.6), points `HOME` at a temporary
  folder so the developer's `~/brachify` config is not loaded, and imports
  `SI_C_D30 Brachify_Ex1/`. *Not verified:* Windows.
- *Verified* 2026-10-08 on macOS: 23 passed, with `test_channels_spin_box_arrows_are_black`
  added. It failed before the fix with the headless Fusion style's grey arrows (darkest
  pixel 94 of 255), passed on PySide6 6.11.2 and 6.8.1, and failed again (85) when the
  `arrows_rc` import was removed. The arrows come from the stylesheet's images, so the test
  sees what every platform draws. *Verified* again 2026-10-13 after merging `main`: 64
  passed, the five Channels view tests also passed on PySide6 6.8.1, and the arrows test
  still failed with no stylesheet (94) and with no `arrows_rc` import (85).
- *Verified* 2026-10-10 on macOS: 24 passed, with two viewport-pick tests added to
  `test_channels_view.py`. They send the pick through the canvas's real `sig_topods_selected`
  signal. Both were watched failing on the code before the viewport-pick fix, and three of the
  four view tests failed when the fix was broken on purpose to never find the selected row.
  *Not verified:* Windows.
- *Verified* 2026-10-10 on Windows, outside conda: 19 passed with the same `--ignore`,
  including the two `DicomData` tests. `data.py` imports nothing, so they need no conda
  package. The `reset()` test failed naming `central_axis_flag` before the fix, and naming
  `operator` when that line was removed from `reset()` on purpose.
- *Verified* 2026-10-15 on Windows, with only `pydicom` in a throwaway venv (not the conda
  app env): `tests/dicom/test_data.py` and `test_load_structures.py` passed 4 of 4. Both
  `load_structures` cases failed when the attach was broken on purpose (empty tuple, and
  leaving a previous value on `StructureReadError`). Loading Ex1's RTSTRUCT through
  `load_structures` produced 42 structures, matching §5.3.
- *Verified* 2026-10-10 on macOS: 25 passed, with `windows/test_main_window.py` added. Its five
  tests were written before the fix. Three were red on `main`, and the other two, which
  describe behaviour the fix must keep, went red once Export was disabled and before it was
  re-enabled. Four deliberate breaks of the fix were each caught.
- *Verified* 2026-10-11 on macOS, after merging `main` into the Channels fix branch: 34
  passed. `test_cylinder_view.py` and `test_channels_view.py` also passed, 12 of 12, when run
  in that order. With the two branches' fixtures kept side by side, that order failed all four
  Channels tests with a `RuntimeError` from the QApplication singleton, which is why
  `channels_window` now builds on `units_app`. *Not verified:* Windows.
- *Verified* 2026-10-11 on macOS, after merging `main` into the Export tab branch: 39 passed.
  `tests/windows` and `tests/views` also passed, 17 of 17, run in either order, so
  `brachify_app` and `units_app` share the one QApplication whichever starts it.
  *Not verified:* Windows.
- *Verified* 2026-10-11 on Windows, outside conda: 20 passed with `test_build_executable.py`
  and `tests/views/` ignored, since `tests/views/` needs PySide6. The `true` test failed with
  `assert True == 30.0` before the fix and again when the `bool` check was removed on purpose.
  The partial-file test failed with `assert 0 == 1` when a file needed two keys to count.
- *Verified* 2026-10-15 on macOS: 65 passed, with
  `test_loading_a_plan_enables_every_channel_again` added to `test_channels_view.py`. It failed
  with `assert not True` before the fix, and again when the fix line was removed on purpose.
  *Not verified:* Windows.
- *Verified* 2026-10-15 on macOS: 70 passed, with four own-diameter tests (five cases) added to
  `test_channels_view.py`. All five failed with `AttributeError` before `set_channel_diameter`
  existed. Four deliberate breaks were each caught: Apply ignoring an own diameter, a clear that
  keeps the width, a reload that keeps own diameters, and NaN let through, which crashed the run
  with exit 139. *Not verified:* Windows.
- *Verified* 2026-10-15 on macOS after Ariq's PR #59 review: 73 passed. A real 3 mm config
  load followed by Ex1 import and clearing a 4 mm override now returns to 3 mm; the old code
  returned 2.7 mm. Unknown and unselected labels raise `KeyError` without changing overrides.
  Both regressions failed before the fix and under deliberate reversions. The shared Apply
  test restores the global model width as well as config, and fresh windows restore the
  previous app window on teardown. Native viewport and Windows were not rerun.
- *Verified* 2026-10-15 on macOS: 68 passed, with three collar round-trip tests added to
  `test_cylinder_view.py` and `test_tandem_view.py` added. All four failed before the fix
  (§7.1): two missing collar keys, collar boxes left at 0, and the extra setting dropped.
  *Not verified:* Windows.
- *Verified* 2026-10-15 on macOS: 79 passed, with `tests/mesh/` added for the notch settings.
  The literals in the default tests were measured on `main` first: volume 109,599.266 mm³, the
  notch from y −16.8 to −14.8 mm. The new-behaviour tests failed first, and flipping the angle
  conversion's sign and always fusing the notch were each caught. `mesh_app` in
  `tests/mesh/conftest.py` reuses the one QApplication, like the other fixtures. It moved the
  same day to [tests/conftest.py](../../tests/conftest.py) as `geometry_app`, when
  `tests/pdf/` needed it too. *Not verified:* Windows.
- *Verified* 2026-10-15 on macOS: 97 passed, with six reference-sheet tests added to
  `pdf/test_template_reference.py`. All six failed before `notch_outline`, `label_distance` and
  `cylinder_rows` existed, and turning the notch counterclockwise failed the 90° test.
  *Not verified:* Windows.
- *Verified* 2026-10-15 on macOS: 91 passed, with two *Tip Shape* tests added to
  `test_cylinder_view.py`. Both failed before the control existed, and removing the tip line
  from `resetAllValues()` failed the config import test. *Not verified:* Windows.
- *Verified* 2026-10-15 on macOS: 89 passed, with `mesh/test_tandem.py` added. The dome
  cut-out's literal, 3,875.268 mm³, was measured before the fix. The flat-tip test failed at
  133.387 mm³ before it, and again when the outline was kept at 10 mm. *Not verified:* Windows.
- *Verified* 2026-10-15 on macOS: 87 passed, with `tests/pdf/test_template_reference.py`
  added. A needle 10 mm off the axis, tip at z 180, measures 23.82 mm past the dome
  (145 + √(15² − 10²) = 156.18) and 20 mm past a flat top. The flat-top test failed at 23.81
  before the fix, and stopping the flat-tip wall where a dome begins failed the wall test.
  *Not verified:* Windows.
- *Verified* 2026-10-15 on macOS: 84 passed, with the flat-tip test added to
  `mesh/test_cylinder.py`. Its literal, π × 15² × 160 = 113,097.336 mm³, was worked by hand. It
  failed at 109,563.044 before the tip setting existed, and again when the dome was always
  built. *Not verified:* Windows.
- *Verified* 2026-10-15 on macOS: 83 passed, with four notch-control tests added to
  `test_cylinder_view.py` in their own test PR. All four failed before the controls existed,
  and removing the notch line from `resetAllValues()` failed the config import test.
  *Not verified:* Windows.
- [pytest.ini](../../pytest.ini) sets `testpaths = tests` and `pythonpath = src .`, so modules
  import as though `src/` were the root and `build_executable` imports from the root.
  [`.vscode/settings.json`](../../.vscode/settings.json) now points pytest at `tests`.
- `benchmarks/` is dead (§7.4) and is not a test suite.
- There is no `.github/` directory, no CI of any kind, and no git hook. Tests and the
  anti-slop linter (§1.9) are run by hand. `agent-skills/anti-slop-py/.github/` is upstream's
  CI, vendored with the linter, and GitHub does not run it from there.

### 8.3 Highest-value targets

In rough order — all are pure functions with no Qt or OCC dependency
and can be tested without launching the app:

1. `helper.rotate_points()` — the DICOM→cylinder transform; wrong here means every needle is
   wrong.
2. `settings/load.load_config_file()` and `checkValuesExist()` — pure dict logic, and the
   round-trip bug in §7.1 would have been caught by a single test asserting
   `set(getCurrentValues()) == set(DEFAULT_CONFIG_VALUES)`.
3. `channel.remove_identical_points()` / `remove_collinear_points()` / `apply_deadspace_to_points()`.
4. `template_reference.extract_points_from_channels2()` — the `z=0` normalisation, with its
   three branches (crosses / stops short / lands exactly).
5. `template_reference.calculate_protrusion_lengths()`.

---

## 9. Maintaining this document

### 9.0 This file is part of a documentation set

**The whole documentation set is updated in the same pull request as the change it describes.**
It is never a follow-up task and never a separate "docs PR".

The set is **every markdown file the team owns**: every markdown file in `docs/`, `tests/`,
`utils/` and `.claude/`, plus four files at the repository root and the index of the vendored
skills. Files inherited from upstream are never part of it (see below). Nor are the weekly log
entries, `docs/logs/<student>/week-<K>.md` and `docs/logs/team/week-<K>.md`: they record work
already done and are never rewritten to match later code. `docs/logs/README.md` stays in.

| File | Covers |
|---|---|
| `docs/project/COSC499-TEAM10-PROJECT-DOCS.md` | this file, the source of truth |
| [docs/project/COSC499-BRACHIFY-INIT-DOCS.md](COSC499-BRACHIFY-INIT-DOCS.md) | the init guide: a plain-language walkthrough of the code **as inherited from upstream**, before Team 10 changed `src/`. It is a baseline, so it is never rewritten to match new code. When a change makes one of its sections out of date, add a short note to that section saying so and pointing to where the new behaviour is documented. Where it and this file disagree, this file wins, and the code wins over both |
| [docs/README.md](../README.md) | index of the `docs/` tree |
| [docs/architecture/README.md](../architecture/README.md) | System architecture, UML, DFD level 0, DFD level 1, Team 10's additions, and the proposed project framework. That README owns when to redraw and how. |
| [docs/contract/README.md](../contract/README.md) | team contract |
| [docs/proposal/README.md](../proposal/README.md) | project proposal |
| [docs/design/README.md](../design/README.md) | UI mocks and design artifacts |
| [docs/minutes/README.md](../minutes/README.md) | meeting minutes |
| [docs/logs/README.md](../logs/README.md) | weekly log layout, Part A sync with PRs, Part B template |
| [docs/workflows/README.md](../workflows/README.md) | index of the tool-agnostic workflows |
| [docs/workflows/commit.md](../workflows/commit.md) | the canonical commit procedure |
| [docs/workflows/make-pr.md](../workflows/make-pr.md) | the canonical pull request procedure, including the weekly log entry |
| [tests/README.md](../../tests/README.md) | TDD policy, `tests/` scoping rule, what to test first |
| [utils/README.md](../../utils/README.md) | `utils/` scoping rule and what belongs there |
| [README.md](../../README.md) | repository entry point |
| [AGENTS.md](../../AGENTS.md) | how to work in this repo |
| [CLAUDE.md](../../CLAUDE.md) | agent entry point, imports `AGENTS.md` |
| [agent-skills/README.md](../../agent-skills/README.md) | the skills every agent loads at session start |
| [pull_request_template.md](../../pull_request_template.md) | Team 10's PR template: the course's Part A receipts, and the checklists that enforce this set |
| [.claude/README.md](../../.claude/README.md) | Claude Code configuration: commands, skills, session-start hook |
| [.claude/commands/](../../.claude/commands/) `commit.md`, `make-pr.md` | pointers to `docs/workflows/` |
| [.claude/skills/](../../.claude/skills/) `*/SKILL.md` | pointers to skills vendored in `agent-skills/` |

Reviewing a file and concluding it needs no change is a valid outcome. **Silently not looking
is not.** If nothing in the set needed changing, say so explicitly in the pull request.

**What is ours and what is inherited.** This repository is a fork of
[brachify/brachify](https://github.com/brachify/brachify). The full classification, with the
rule for each group, is in [AGENTS.md](../../AGENTS.md#what-is-ours-and-what-is-inherited). In
short:

- **Inherited from upstream brachify, never edited:** `README-BRACHIFY.md` (upstream's
  `README.md`, renamed), `pull_request_template_brachify.md` (upstream's
  `pull_request_template.md`, renamed), `virtual_environments_instructions.md`, `notes/`
  (including its markdown in `notes/code_notes/`), `user_guide/`, `3D Models and Templates/`,
  `Images/`, `LICENSE`, `requirements.txt`, and the two `SI_C_D30 Brachify_Ex*/` sample
  folders. If one of them has become wrong, record the correction here instead of rewriting
  upstream's file.
- **Vendored from third parties, never edited:** every file inside a skill's folder in
  `agent-skills/`. Only `agent-skills/README.md` is ours.
- **Inherited, changed only by their procedure:** `spec-file.txt` and `environment.yml` (a
  dependency change, with the same dependency list as §1.1), and `.vscode/settings.json`
  (pointed at `tests` on 2026-09-30 by the change that added the first tests, §8.2).

*Verified* on 2026-09-25: every file listed as inherited was byte-for-byte identical to
`upstream/main` at `f89cafe`, and the two renamed files are identical to upstream's originals.

The set cross-references itself. **If you change a rule stated in more than one file, update
every copy.** A rule that appears in three places and is true in two is worse than one that
appears once.

[AGENTS.md](../../AGENTS.md) carries the same table for AI agents, and the
[pull request template](../../pull_request_template.md) turns it into a per-file checklist the
author fills in on every PR.

### 9.1 When this file specifically must be updated

Beyond the set-wide rule above, update **this** document when you:

- add, remove, or rename a module, view, model, or config key;
- change the startup sequence, the signal graph, or the display pipeline;
- change the DICOM contract (new vendor, new required structure name, changed field);
- change setup, dependencies, or the environment in any way;
- fix anything listed in §7 — move it out of "known bugs", do not just delete the entry;
- discover a new bug or trap — add it to §7 rather than leaving it in a PR comment;
- add tests — update §8.

### 9.2 Which section to touch

| Change | Section |
|---|---|
| dependency, environment, run command | §1 Setup. A dependency follows the procedure in §1.1, for Windows, macOS and Linux together |
| new module or file | §4.7 directory map **and** §5 module reference |
| new/changed signal or model wiring | §4.4, and the diagrams in [docs/architecture/](../architecture/README.md) |
| new/changed view or widget | §4.3, §5.6 |
| new/changed config key | §6.2 (and remember the four code sites) |
| new/changed export format | §6.4 |
| bug found or fixed | §7 |
| anything that makes a section of the init guide out of date | a short note in that section of [COSC499-BRACHIFY-INIT-DOCS.md](COSC499-BRACHIFY-INIT-DOCS.md), pointing here; the section itself is not rewritten |
| test added | §8, and every function in it has a docstring ([AGENTS.md](../../AGENTS.md#every-function-in-tests-explains-itself)) |
| skill added, removed, or updated in `agent-skills/` | the table in `agent-skills/README.md`; §1.10 only if how skills load changes |

### 9.3 Rules for edits

1. Obey the standing mandate in §2 — read the code, do not guess.
2. Mark claims *Verified* or *Reasoned from code*. Do not silently promote the second to the
   first.
3. Update the **Last full code audit** date in the header only after an actual full re-read,
   not after a small edit.
4. Keep file references as relative markdown links so they stay clickable from GitHub and from
   an IDE.
5. If you remove a §7 entry because it was fixed, note the fix — a reader should be able to see
   that the trap once existed.

### 9.4 Related files

| File | Role |
|---|---|
| [AGENTS.md](../../AGENTS.md) | instructions for AI agents; points here for project context |
| [CLAUDE.md](../../CLAUDE.md) | Claude Code entry point; imports `AGENTS.md` |
| [agent-skills/](../../agent-skills/) | skills every agent reads at session start, including the anti-slop-py linter behind the anti-slop rules in `AGENTS.md` (§1.9, §1.10) |
| [pull_request_template.md](../../pull_request_template.md) | Team 10 PR template: the course's Part A receipts, then the update-this-doc gate |
| [pull_request_template_brachify.md](../../pull_request_template_brachify.md) | upstream's original review process, preserved |
| [docs/README.md](../README.md) | index of the `docs/` tree |
| [COSC499-BRACHIFY-INIT-DOCS.md](COSC499-BRACHIFY-INIT-DOCS.md) | the init guide: the inherited code explained from scratch, with worked examples on the sample data. Read it first, then this file |
| [README-BRACHIFY.md](../../README-BRACHIFY.md) | upstream project README (user-facing) |
| [virtual_environments_instructions.md](../../virtual_environments_instructions.md) | upstream conda guide (Windows-centric) |
| [notes/](../../notes/) | upstream developer notes |
| [user_guide/Brachify User Manual.docx](../../user_guide/Brachify%20User%20Manual.docx) | end-user manual; authoritative on clinical workflow. Where it differs from the code, see §6.5 |

---

## 10. Glossary

| Term | Meaning |
|---|---|
| **Brachytherapy** | Radiotherapy delivering a sealed radioactive source inside or next to the treatment volume. |
| **Interstitial** | Needles passing *through* tissue, as opposed to sitting in a body cavity. The "interstitial length" is how far a needle protrudes past the cylinder surface into tissue. |
| **Applicator / cylinder** | The physical device inserted into the patient. brachify generates a printable, patient-specific one. |
| **Tandem** | A curved central channel, typically for a uterine source. Either generated parametrically or imported as a STEP model. |
| **Channel** | One needle path. Each becomes a bored hole in the printed cylinder. |
| **Central Axis** | The mandatory reference channel defining the cylinder axis (§3.2). The manual says to label it exactly `Central Axis`; Varian plans are matched on a label that contains it. |
| **Dead space** | Distance from the needle tip to the first dwell position; extends the tip in interstitial length calculations. |
| **Collet** | A small printed insert holding a needle at the cylinder base. Models in `3D Models and Templates/`; the PDF draws tolerance rings for them. |
| **Notch** | Small raised marker fused to the cylinder wall at `z=0` indicating orientation. |
| **Collar / base** | Optional ring around the cylinder base (`CONFIG_BASE_*`). Called "base" in code, "Collar" in the UI. |
| **TPS** | Treatment Planning System — Varian BrachyVision or Elekta Oncentra. |
| **RTPLAN / RTSTRUCT / RTDOSE** | DICOM radiotherapy modalities. brachify reads the first two, ignores the third. |
| **ROI** | Region of Interest — a DICOM structure identifier. |
| **OCC / OpenCASCADE** | The B-rep CAD kernel, reached through `pythonocc-core`. |
| **B-rep** | Boundary representation — solids described by faces/edges/vertices rather than meshes. |
| **TopoDS_Shape** | The OCC base type for all geometry. |
| **Dwell time** | How long the source sits at a position. Must be zero for `Central Axis`, though nothing in the code checks it (§3.2). |
