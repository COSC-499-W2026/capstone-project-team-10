# Week 4, Ariq

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**7**

- As part of requirement **the course's Weekly Expectations, which grade each merged PR through
  the Part A receipts in every student's weekly log**, the user needs to do **run `/make-pr` on
  a branch, fill in Part A from the diff, open the PR, and have the same Part A committed to
  `docs/logs/<student>/week-<K>.md`**.
- Therefore, I implemented/generated code so that **the four Team 10 students get a PR template
  that opens with Part A, with all 142 placeholders pre-bolded (`pull_request_template.md`),
  a `/make-pr` procedure that fills Part A with evidence on every PR, ticks N/A boxes, and copies
  Part A into their weekly log (`docs/workflows/make-pr.md`), and week 4 log files for each
  student and the team (`docs/logs/`). The instructor and TAs get one Part A per PR, identical in
  the PR description and in the log**.

#### Review and design

- When I reviewed the **generated `pull_request_template.md`** for this functionality, I
  noticed **it was going to carry Part B, the team log, which covers the whole team's week
  rather than one PR**. Therefore, I did **keep Part B out of PRs and put its template in
  `docs/logs/README.md`, for `docs/logs/team/week-<K>.md`**.
- When I reviewed the **generated `docs/workflows/make-pr.md`** for this functionality, I
  noticed **it pointed diagram placeholders at a `docs/architecture.md` that did not exist on
  `main`**. Therefore, I did **point them at `docs/architecture/diagrams/uml.mmd`, `dfd-0.mmd`
  and `dfd-1.mmd` once PR #4 merged, and link to `docs/architecture/README.md` for when to
  redraw instead of restating that rule**.
- When I reviewed the **generated `docs/logs/` layout** for this functionality, I noticed **the
  weekly log files fell under "every markdown file in `docs/`", so the documentation-set rule
  would require rewriting past logs to match later code**. Therefore, I did **exclude
  `docs/logs/<student>/week-<K>.md` and `docs/logs/team/week-<K>.md` from the set in
  `AGENTS.md`, `README.md`, `docs/README.md` and §9.0 of the project docs, keeping
  `docs/logs/README.md` in it**.
- When I reviewed the **generated description of this PR** for this functionality, I noticed
  **its N/A checkboxes were left unticked, which tells a reviewer those items are missing when
  they were checked, and its Part A was a single N/A line, which would leave this graded weekly
  log empty**. Therefore, I did **change the rules in `make-pr.md`, `pull_request_template.md`
  and `docs/logs/README.md` so an N/A box is ticked, a box stays blank only when it was not
  checked or waits on the author, and Part A is filled in on every PR, then refilled this PR's
  description and `docs/logs/ariq/week-4.md`**.
- The PR does not contain any temporary workaround because **the Change checklist, Review
  section and upstream footer are deleted rather than commented out, and every file that
  described them was updated in this PR. A grep of the documentation set for their wording
  returns 0 matches**.
- The PR only contains small functions — **N/A**, the PR adds no functions.
  `git diff --name-only origin/main...HEAD` lists only markdown files.
- By doing **a grep of the documentation set for every phrase that described the removed
  sections, and a read of each rule I added against the files that already stated it**, I
  found that my feature contribution contained **duplicate code, a copy in `make-pr.md` of the
  diagram redraw rule that `docs/architecture/README.md` owns, and dead code, a `make-pr.md`
  line telling agents to leave the removed Reviewer block unticked**. Therefore, I did
  **replace the copy with a link to `docs/architecture/README.md` and delete the line**.

  Now, I can confirm that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`pull_request_template.md`, `docs/workflows/make-pr.md` and
  `docs/logs/`** because **GitHub pre-fills the template on its web form and `/make-pr` appends
  it by hand, `make-pr.md` is the one tool-agnostic procedure that
  `.claude/commands/make-pr.md` points to, and `docs/logs/` already held the team and
  individual logs beside the other course documents**.
- This work belongs in a process in the DFD — **N/A**, the PR changes the team's PR process, not
  brachify. No process in `docs/architecture/diagrams/dfd-1.mmd` moves.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`sh .claude/hooks/session-start.sh` (exit 0, no `UNDOCUMENTED` or `STALE ROW` line),
  `python docs/architecture/build.py --check` (exit 0), and a script confirming that all 142
  Part A placeholders in `pull_request_template.md` are bold** passed. These are repository
  checks run from the shell, not tests in `tests/`.
- I wrote tests to cover abnormal situations — **N/A**, the PR has no code for a test to
  exercise.
- I checked that these negative cases involving **a grep of the documentation set for the
  removed wording ("Reviewer block", "signs off", "template requires", "## Change checklist",
  "leave the box unticked", "not logged")** failed as expected, with 0 matches.
- When I reviewed the generated tests — **N/A**, no tests were generated.
- Among these tests, unit and integration tests — **N/A**, none of the checks is a unit or
  integration test. They are shell checks on the repository.
- These tests are included in the directory — **N/A**, nothing was added to `tests/`. The
  checks live in `.claude/hooks/session-start.sh` and `docs/architecture/build.py`.
- This new test PR did not break anything else in the system because **`git diff --name-only
  origin/main...HEAD` lists no file outside markdown, so nothing under `src/` changed and the app
  behaves as before. The app was not run and no screenshot was taken**.

### For PR #**9**

- As part of requirement **§1 Setup of the project docs, which must give every teammate a
  working brachify environment on their own OS, and the proposal's choice of pytest as the
  testing framework (`docs/proposal/README.md`, testing options), which needs pytest
  installed**, the user needs to do **clone the repository on Windows, macOS or Linux, create
  the conda environment from `spec-file.txt` (Windows) or the §1.2 `conda create` command
  (macOS and Linux), and get the same packages on each, `pytest` and `pyinstaller` included**.
- Therefore, I implemented/generated code so that **every Team 10 developer, on any of the
  three operating systems, installs the same nine dependencies (`environment.yml`,
  `spec-file.txt`, the §1.2 command), and any developer or agent adding a dependency follows
  one cross-OS procedure (§1.1 of the project docs, `AGENTS.md`)**.

#### Review and design

- When I reviewed the **generated `environment.yml`** for this functionality, I noticed **it
  never named `pyside6`. Windows only got PySide6 through `matplotlib`, and the `osx-arm64`
  build of `matplotlib` has no Qt dependency, so a Mac environment built from it could not
  start `src/launch.py`**. Therefore, I did **name `pyside6`, `numpy` and `pytest` in
  `environment.yml`, and confirm with a dry-run solve on macOS that it now resolves
  `pyside6` 6.11.2**.
- When I reviewed the **first generated version of `environment.yml` and the §1.2 command**,
  I noticed **every package was pinned to the Windows lockfile's exact version, which meant
  three places to bump on every upgrade, while the goal was the same dependencies on every OS,
  not the same versions**. Therefore, I did **remove every pin except `python=3.12` and
  `pythonocc-core=7.7.2`, and state in §1.1 that versions may differ between operating
  systems**.
- When I reviewed the **generated `spec-file.txt` lines for `pytest`**, I noticed **they were
  not written by `conda list --explicit` on Windows, which is how the file is normally
  regenerated, because I have no Windows machine**. Therefore, I did **solve for `win-64` from
  macOS with all 179 existing packages pinned, confirm none changed and only six were added,
  check each URL returns HTTP 200, and record it as *Not verified* on Windows in §1.3**.
- When I reviewed the **generated proposal to containerise the app with Docker**, I noticed
  **brachify is a desktop GUI with an OpenGL viewport, so a container has no screen to show
  it, and PyInstaller cannot build the Windows `.exe` from a Linux container**. Therefore, I
  did **drop Docker and write the reasons into §1.11 and `AGENTS.md`, with CI named as the one
  case worth reconsidering**.
- When I reviewed the **merge with PR #7**, I noticed **PR #7 had removed the template's
  Change checklist, where the dependency checkbox lived**. Therefore, I did **move the
  cross-OS rule into the existing `spec-file.txt` and `environment.yml` line under Quality of
  the updates**.
- The PR does not contain any temporary workaround because **it changes dependency lists and
  documentation, not code logic. The one step I could not run, creating the environment from
  `spec-file.txt` on Windows, is recorded as *Not verified* in §1.3 rather than worked around**.
- The PR only contains small functions — **N/A**, the PR adds no functions. No `.py` file
  changed.
- By doing **a grep of the documentation set for the wording of the removed pins (`6.8.1`,
  `3.10.9`, `same version`, `pinned command`) after removing them**, I found that my feature
  contribution contained **dead code, stale lines in §4.7, §7.4, §7.5, §9.0, `AGENTS.md` and
  the PR template that still described pinned versions, and duplicate code, the full
  dependency procedure about to be written into three files**. Therefore, I did **rewrite each
  stale line, and keep the procedure in §1.1 only, with `AGENTS.md` and the template pointing
  to it**.

  Now, I can confirm that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`environment.yml`, `spec-file.txt` and §1 of
  `docs/project/COSC499-TEAM10-PROJECT-DOCS.md`** because **conda reads the first two
  directly, and §1 Setup is where the section map in §9.2 sends any dependency or environment
  change**.
- This work belongs in a process in the DFD — **N/A**, the PR changes the development
  environment, not brachify. No process in `docs/architecture/diagrams/dfd-1.mmd` moves.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **creating a Mac
  environment from the §1.2 command (PySide6 6.11.2, matplotlib 3.11.2, reportlab 5.0.1,
  pyinstaller 6.22.3, pytest 9.1.1, pydicom 3.0.2, numpy 1.26.4 on Python 3.12.14), launching
  the app natively from it until it logged `main window initialization complete`, a dry-run
  solve of `environment.yml` on macOS, and `conda search` finding `pythonocc-core` 7.7.2 for
  `win-64`, `osx-arm64`, `osx-64` and `linux-64`** passed. These are environment checks run
  from the shell, not tests in `tests/`.
- I wrote tests to cover abnormal situations involving **the blank line and comment added to
  `spec-file.txt`, parsed with conda's own reader (`conda.cli.common.specs_from_url`), which
  skipped both and returned all 185 package URLs** and they passed.
- I checked that these negative cases involving **the Mac environment created before this PR,
  where `import pytest` and `import PyInstaller` both failed with `ModuleNotFoundError`**
  failed as expected.
- When I reviewed the generated tests — **N/A**, no tests were generated. The first tests are
  in the next PR, which builds on this one.
- Among these tests, unit and integration tests — **N/A**, none of the checks is a unit or
  integration test. They are environment checks run from the shell.
- These tests are included in the directory — **N/A**, nothing was added to `tests/`.
- This new test PR did not break anything else in the system because **the app launched
  natively in the new environment and initialised the 3D viewport. DICOM import and the
  Export tab were not exercised, and no screenshot was taken. `python -m pytest` on this
  branch reports the same 36 collection errors as on `main`, all inside the vendored
  `agent-skills/anti-slop-py/`, because no `pytest.ini` exists yet. The next PR adds it**.

### For PR #**10**

- As part of requirement **the proposal's choice of pytest as the testing framework
  (`docs/proposal/README.md`, testing options), and the rule in `AGENTS.md` that the first
  change adding a test must also configure the runner**, the user needs to do **run
  `python -m pytest` from the repository root and see the build's hidden imports checked,
  then run `python build_executable.py` on Windows and get pydicom 3's encoder modules
  bundled into `brachify.exe`**.
- Therefore, I implemented/generated code so that **Team 10 developers get a working test
  runner (`pytest.ini`, `.vscode/settings.json`), a build whose hidden imports name modules
  that exist (`HIDDEN_IMPORTS` in `build_executable.py`), and a test that fails if one ever
  stops existing (`tests/tooling/test_build_executable.py`)**.

#### Review and design

- When I reviewed the **generated `build_executable.py`** for this functionality, I noticed
  **its hidden imports `pydicom.encoders.gdcm` and `pydicom.encoders.pylibjpeg` do not exist
  in pydicom 3.0.2. A trial PyInstaller build on macOS logged `ERROR: Hidden import
  'pydicom.encoders.gdcm' not found` and the same for `pylibjpeg`, then exited 0**.
  Therefore, I did **point both at `pydicom.pixels.encoders.*`, where pydicom 3 keeps them.
  The trial build then analysed both with no error**.
- When I reviewed the **restructured `build_executable.py`**, I noticed **it builds the same
  `--hidden-import` arguments as before, so the only reason for the change is that a test
  needs to read the list**. Therefore, I did **keep the `HIDDEN_IMPORTS` list, so the test can
  import it rather than parse the file, and leave every other PyInstaller argument as it was**.
- When I reviewed the **generated tests in `tests/tooling/`**, I noticed **their purpose was
  written as single-line `#` comments, which a reader skims past and which repeated what the
  code already showed**. Therefore, I did **move each explanation into a docstring, delete the
  `#` comments, and add the rule to `AGENTS.md`, `tests/README.md` and the PR template**.
- When I reviewed **how pytest runs from the repository root**, I noticed **with no
  configuration it collected the vendored linter in `agent-skills/` and reported 36
  collection errors**. Therefore, I did **set `testpaths = tests` in `pytest.ini`, so only the
  team's tests run**.
- The PR does not contain any temporary workaround because **the fix names the modules where
  pydicom 3 keeps them, with no suppression or fallback, and the test keeps the list honest
  from now on**.
- The PR only contains small functions that are **11 lines** long. That is
  `test_hidden_import_exists_in_the_environment`, counted with its decorator and docstring,
  and `build_executable.py` has no functions.
- I did **run `anti_slop review --base main src tests utils build_executable.py`, which
  reported no findings, and check that the only module-level value added, `HIDDEN_IMPORTS`,
  is read by both the build and the test** to ensure that my feature contribution does not
  contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`build_executable.py` (existing), `pytest.ini` (new, at the root)
  and `tests/tooling/test_build_executable.py` (new)** because **pytest reads its
  configuration from the root, and `AGENTS.md` scopes tests of repository files outside
  `src/` to `tests/tooling/`**.
- This work belongs in a process in the DFD — **N/A**, the PR changes the build and the test
  runner, not brachify. No process in `docs/architecture/diagrams/dfd-1.mmd` moves.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_hidden_import_exists_in_the_environment` for `OCC`, `pydicom.pixels.encoders.gdcm`
  and `pydicom.pixels.encoders.pylibjpeg`** passed. `python -m pytest` reports 3 passed.
- I wrote tests to cover abnormal situations — **N/A**, the test has one input, a module name,
  and the only abnormal input is a missing module, which is the negative case below.
- I checked that these negative cases involving **the old names `pydicom.encoders.gdcm` and
  `pydicom.encoders.pylibjpeg`, put back on this branch on purpose,** failed as expected: 2
  failed with `ModuleNotFoundError`, 1 passed, and all 3 passed again once the fix was
  restored.
- When I reviewed the **`test_hidden_import_exists_in_the_environment`**, I noticed **its
  first run errored at collection with `AttributeError: module 'build_executable' has no
  attribute 'HIDDEN_IMPORTS'`, a failure for the wrong reason**. Therefore, I did **extract
  the list first without changing the build, so the test then failed for the right reason, on
  the two missing modules, before the fix**.
- Among these tests, **`test_hidden_import_exists_in_the_environment`** are unit tests and
  integration tests are not required because **the build's integration, a full PyInstaller
  run, takes minutes and was run by hand on macOS instead, and the test checks the one input
  the build depends on**.
- These tests are included in the directory **`tests/tooling/`**.
- This new test PR did not break anything else in the system because **`python -m pytest`
  passes with 3 tests, `python docs/architecture/build.py --check` exits 0, and the trial
  PyInstaller build on macOS exits 0 with no hidden-import error. A Windows `.exe` build was
  not run and no screenshot was taken**.

### For PR #**11**

- As part of requirement **Session start in `AGENTS.md`, which the session-start hook must
  print at the start of every Claude Code session, on Windows as well as macOS and Linux**,
  the user needs to do **clone the repository on Windows with Git for Windows, open it in
  Claude Code, and get the session-start steps printed, or run the hook by hand from
  PowerShell with `& "$env:ProgramFiles\Git\bin\sh.exe" .claude/hooks/session-start.sh`**.
- Therefore, I implemented/generated code so that **Team 10 developers on Windows get the
  hook checked out with LF line endings (`.gitattributes`), a test that fails if any tracked
  shell script loses that (`tests/tooling/test_line_endings.py`), and docs for running it by
  hand from every shell (§1.10, `AGENTS.md`, `.claude/README.md`, `make-pr.md`)**.

#### Review and design

- When I reviewed the **generated plan to rewrite the hook in Python** for this
  functionality, I noticed **no single Python command name works on every OS. This Mac has no
  `python` on `PATH`, only `python3`, and a conda environment on Windows has `python` but no
  `python3`, so a Python hook would need the same shell to pick an interpreter**. Therefore, I
  did **keep the `sh` script and fix what actually breaks it on Windows, the CRLF checkout**.
- When I reviewed the **generated wording "Windows users need Git Bash or WSL"**, I noticed
  **it overstated the requirement. Git Bash comes with Git for Windows, which is how Windows
  users get `git` at all, and Claude Code uses it for hooks**. Therefore, I did **list Git for
  Windows as the Windows prerequisite in §1.1, and say that only Windows without it, where
  Claude Code falls back to PowerShell, is unsupported**.
- When I reviewed the **generated advice for fixing an existing CRLF clone**, I noticed **it
  ran `git reset --hard`, which throws away a teammate's uncommitted work**. Therefore, I did
  **replace it with deleting the one script and running
  `git checkout -- .claude/hooks/session-start.sh`**.
- When I reviewed the **generated `test_shell_script_is_checked_out_with_lf_on_every_os`**, I
  noticed **it runs once per tracked script, so if the script list came back empty it would
  run zero times and pass without checking anything**. Therefore, I did **add
  `test_session_start_hook_is_a_tracked_shell_script` as a guard**.
- The PR does not contain any temporary workaround because **`.gitattributes` is git's
  standard, permanent way to fix a file's line endings on every clone, and Windows without
  Git for Windows is documented as unsupported rather than patched around**.
- The PR only contains small functions that are **10, 7 and 15 lines** long:
  `tracked_shell_scripts`, `test_session_start_hook_is_a_tracked_shell_script` and
  `test_shell_script_is_checked_out_with_lf_on_every_os`, each counted with its decorator and
  docstring.
- I did **run `anti_slop review --base main src tests utils build_executable.py`, which
  reported no findings, and keep the git call that lists scripts in one helper used by both
  the guard and the parametrized test** to ensure that my feature contribution does not
  contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`.gitattributes` (new, at the root) and
  `tests/tooling/test_line_endings.py` (new)** because **git reads `.gitattributes` from the
  repository root, and `AGENTS.md` scopes tests of repository files outside `src/` to
  `tests/tooling/`**.
- This work belongs in a process in the DFD — **N/A**, the PR changes how the repository is
  checked out, not brachify. No process in `docs/architecture/diagrams/dfd-1.mmd` moves.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_session_start_hook_is_a_tracked_shell_script` and
  `test_shell_script_is_checked_out_with_lf_on_every_os[.claude/hooks/session-start.sh]`**
  passed. `python -m pytest` reports 5 passed, with #10's 3.
- I wrote tests to cover abnormal situations involving **no tracked shell scripts at all,
  which would make the parametrized test run zero times.
  `test_session_start_hook_is_a_tracked_shell_script` covers it** and they passed.
- I checked that these negative cases involving **removing `.gitattributes` on this branch on
  purpose, so `git check-attr eol` answers `unspecified`,** failed as expected: 1 failed, 4
  passed, and all 5 passed again once it was restored.
- When I reviewed the **`test_shell_script_is_checked_out_with_lf_on_every_os`**, I noticed
  **a check of the script's bytes would pass on macOS whether or not `.gitattributes` existed,
  since the file is LF here already, so it could never fail on the machine it was written
  on**. Therefore, I did **assert on git's `eol` attribute instead, which is what decides the
  Windows checkout and which fails on any OS when the rule is missing**.
- Among these tests, **`test_session_start_hook_is_a_tracked_shell_script` and
  `test_shell_script_is_checked_out_with_lf_on_every_os`** are integration tests and unit
  tests are not required because **both test what git does with the repository, through
  `git ls-files` and `git check-attr`, and there is no logic of ours to test apart from
  git**.
- These tests are included in the directory **`tests/tooling/`**.
- This new test PR did not break anything else in the system because **`python -m pytest`
  passes with 5 tests, `sh .claude/hooks/session-start.sh` exits 0 with no `UNDOCUMENTED` or
  `STALE ROW` line, and `python docs/architecture/build.py --check` exits 0. Adding
  `.gitattributes` did not change the hook's bytes on macOS (`git status` showed no
  renormalised file). The hook was not run on Windows, and no screenshot was taken**.

### For PR #**15**

- As part of requirement **the course's Weekly Expectations, Part B, which asks for one team
  log per week in `logs/team/week-K.md`, on a `weekly-logs` branch, naming its authors and
  covering everyone's merged work**, the user needs to do **open `docs/logs/team/week-4.md` and
  audit the team's week: the goal, who did what, whether the goal was met and on what
  evidence, what the team found in the code base, the current DFD and system architecture
  diagram, and how the team's process changed**.
- Therefore, I implemented/generated code so that **the instructor and TAs get the week 4 Part
  B, with each claim traced to a PR, a command run on `main` at `901bce9`, or a receipt in a
  member's `docs/logs/<student>/week-4.md`. The four Team 10 students get a team log that names
  all of them as authors and covers PRs #4 and #7 to #14**.

#### Review and design

- When I reviewed the **first PR data the agent collected** for this functionality, I noticed
  **`gh pr view 7` to `14` had resolved to the upstream `brachify/brachify` repository and
  returned a different project's 2024 tandem PRs, because `gh` defaults to a fork's parent**.
  Therefore, I did **re-fetch every PR with `--repo COSC-499-W2026/capstone-project-team-10`,
  and take each author, file count, line count and approver from that output**.
- When I reviewed the **generated "met the goal" receipt**, I noticed **it said every test had
  been shown red in its PR's receipt. #8's `test_svg_is_stale_when_source_text_changed` passed
  on its first run, as Ehsan's receipt says**. Therefore, I did **narrow it to "each PR that
  adds tests records tests failing before the fix, or with the fix reverted", which is true of
  #8, #10, #11, #12, #13 and #14**.
- When I reviewed the **generated closing line of the code-base receipt**, I noticed **"the
  team can confirm that the code base does not contain many dependencies between modules" is
  false. Ahab's #12 records in `docs/architecture/README.md` that views reach each other by
  index and that `Export_View` reads three models directly, and no PR changed `src/`**.
  Therefore, I did **limit the confirmation to the tooling and tests added this week, and keep
  the upstream coupling as a finding that is still there**.
- When I reviewed the **generated DFD alternatives**, I noticed **they said Gilles had proposed
  showing the intended flows in the same DFDs. Ahab's #4 receipt says Gilles suggested adding
  diagrams of the intended design, not mixing them in**. Therefore, I did **reword it to what
  Gilles suggested, and say that #13 drew those flows separately**.
- When I reviewed the **generated prose about teammates**, I noticed **it used "he" and "his"
  for Ehsan and Gilles, whose pronouns nobody had stated**. Therefore, I did **replace both with
  names. A grep for gendered pronouns in the file returns 0 matches**.
- When I reviewed the **receipt on alternative workload distributions**, I noticed **no PR,
  review or log records what the team discussed, so any answer would be invented**.
  Therefore, I did **leave a bold TODO for the team instead of filling it in**.
- The PR does not contain any temporary workaround because **it adds no code logic. It
  replaces the `_Not written yet._` line in one markdown file with the week's Part B. The one
  open item, the TODO above, is marked in bold where it sits rather than hidden**.
- The PR only contains small functions — **N/A**, the PR adds no functions.
  `git diff --name-only main...HEAD` lists only `docs/logs/team/week-4.md`.
- I did **take every number from a script over `gh pr view --repo ...` output, not from
  memory. That covers the files, lines, markdown share, generated share and approvers. I also
  pinned the three embedded diagrams to commit `901bce9`, so the log keeps showing the week 4
  versions when the diagrams change later, and linked each PR's own receipts rather than
  copying them** to ensure that my feature contribution does not contain any of the
  following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/logs/team/week-4.md` (existing, created empty by #7), on the
  `weekly-logs` branch** because **`docs/logs/README.md` puts one team log per week in
  `docs/logs/team/`, and the course asks for logs on a `weekly-logs` branch, kept separate from
  code**.
- This work belongs in a process in the DFD — **N/A**, the PR is the team's weekly log, not
  brachify. No process in `docs/architecture/diagrams/existing-framework/dfd-1.mmd` moves.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`python -m pytest
  -q` (20 passed), `python docs/architecture/build.py --check` (exit 0), `sh
  .claude/hooks/session-start.sh` (exit 0, no `UNDOCUMENTED` or `STALE ROW` line), and `curl`
  on the three embedded diagram URLs (HTTP 200 each), all run on this branch on macOS on
  2026-10-04** passed. These are repository checks run from the shell, not tests in `tests/`.
- I wrote tests to cover abnormal situations — **N/A**, the PR has no code for a test to
  exercise.
- I checked that these negative cases involving **a grep for unfilled `**[` placeholders and a
  grep for gendered pronouns in `docs/logs/team/week-4.md`** failed as expected, with 0
  matches each.
- When I reviewed the generated tests — **N/A**, no tests were generated.
- Among these tests, unit and integration tests — **N/A**, none of the checks is a unit or
  integration test. They are shell checks on the repository.
- These tests are included in the directory — **N/A**, nothing was added to `tests/`.
- This new test PR did not break anything else in the system because **`git diff --name-only
  main...HEAD` lists only `docs/logs/team/week-4.md`, so nothing under `src/` changed and the
  suite passes as on `main` (20 passed). The app was not run and no screenshot was taken**.

### For PR #**16**

- As part of requirement **the course's Weekly Expectations, Part B, which asks for one team
  log per week in `logs/team/week-K.md`, on a `weekly-logs` branch, naming its authors**, the
  user needs to do **open `docs/logs/team/week-4.md`, see every author named in full, and read
  each receipt as an answer, with no placeholder left for the team**.
- Therefore, I implemented/generated code so that **the instructor and TAs get a week 4 team
  log with Ehsan Babar named in full beside the other three authors, and with no unanswered
  TODO in the workload receipt**.

#### Review and design

- When I reviewed the **team log as merged in #15** for this functionality, I noticed **it
  still carried two items that #15's description had asked the team to settle before merging:
  Ehsan was named without a surname, and the workload receipt ended in a bold "TODO (team)"
  that a grader would read as an unanswered receipt. #15 was merged before either was
  settled**. Therefore, I did **add "Babar" to the authors line, and delete the workload
  sentence, because the team discussed it and decided that no alternative distribution applied
  this week. Writing one in would have been a claim about a discussion that did not happen**.
- When I reviewed the **bullet after the deletion**, I noticed **it had to end on a complete
  sentence and not leave a dangling clause**. Therefore, I did **end it at "each of the nine PRs
  has two approving reviews from teammates other than its author.", which is unchanged from
  #15**.
- When I reviewed **my #15 section in `docs/logs/ariq/week-4.md`**, I noticed **it says I left
  a bold TODO, which is no longer true of the file**. Therefore, I did **leave that section
  unchanged, because `docs/logs/README.md` says log entries record work already done, and
  record the follow-up in this section instead**.
- The PR does not contain any temporary workaround because **it removes the only placeholder
  in the team log rather than deferring it. A grep for `TODO` and for unfilled `**[`
  placeholders in `docs/logs/team/week-4.md` returns 0 matches each**.
- The PR only contains small functions — **N/A**, the PR adds no functions.
  `git diff --name-only origin/main...HEAD` lists only markdown files in `docs/logs/`.
- I did **read the full diff from `origin/main`, which is one changed line on authors and three
  deleted lines on the workload sentence, and grep the file for `TODO`, unfilled placeholders
  and gendered pronouns (0 matches each)** to ensure that my feature contribution does not
  contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/logs/team/week-4.md` (existing), on the `weekly-logs`
  branch** because **it corrects the team log that #15 added there, and the course asks for
  logs on a `weekly-logs` branch, kept separate from code**.
- This work belongs in a process in the DFD — **N/A**, the PR is the team's weekly log, not
  brachify. No process in `docs/architecture/diagrams/existing-framework/dfd-1.mmd` moves.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`python -m pytest
  -q` (20 passed), `python docs/architecture/build.py --check` (exit 0) and `sh
  .claude/hooks/session-start.sh` (exit 0, no `UNDOCUMENTED` or `STALE ROW` line), all run on
  this branch on macOS on 2026-10-04** passed. These are repository checks run from the shell,
  not tests in `tests/`.
- I wrote tests to cover abnormal situations — **N/A**, the PR has no code for a test to
  exercise.
- I checked that these negative cases involving **a grep of `docs/logs/team/week-4.md` for
  `TODO`, for unfilled `**[` placeholders and for gendered pronouns** failed as expected, with
  0 matches each.
- When I reviewed the generated tests — **N/A**, no tests were generated.
- Among these tests, unit and integration tests — **N/A**, none of the checks is a unit or
  integration test. They are shell checks on the repository.
- These tests are included in the directory — **N/A**, nothing was added to `tests/`.
- This new test PR did not break anything else in the system because **`git diff --name-only
  origin/main...HEAD` lists only the two log files, so nothing under `src/` changed and the
  suite passes as on `main` (20 passed). The app was not run and no screenshot was taken**.
