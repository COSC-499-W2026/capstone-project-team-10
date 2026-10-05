# Week 4, Ehsan

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**8**

- As part of requirement **the team's pull-request gate in `docs/workflows/make-pr.md` and
  `AGENTS.md`, which requires `python docs/architecture/build.py --check` to exit 0 before any
  PR is opened, and the proposal's choice of pytest for automated testing (section 2 of
  `docs/proposal/README.md`)**, the user needs to do **check out `main` on Windows, run
  `python docs/architecture/build.py --check`, see it exit 0 when no diagram has changed, and
  open their pull request**.
- Therefore, I implemented/generated code so that **every Team 10 student on Windows, where
  Git checks text out with CRLF line endings, passes the diagram check on an unchanged
  checkout. `digest()` in `docs/architecture/build.py` now hashes the LF form of each `.mmd`
  source, so a Windows clone and a macOS or Linux clone agree on the same fingerprint. Two
  tests in `tests/tooling/test_architecture_build.py` guard it**.

#### Review and design

- When I reviewed the **generated change to `digest()` and the stale message in
  `docs/architecture/build.py`** for this functionality, I noticed **the message said "its SVG
  is missing or older than the source", which describes a timestamp check, while the code
  compares hashes. Someone debugging a failure would compare file dates and find nothing**.
  Therefore, I did **reword it to "its SVG is missing or its stamp does not match the
  source"**.
- When I reviewed the **generated docstring edit in `docs/architecture/build.py`** for this
  functionality, I noticed **it left one line about 130 characters long, while the rest of the
  docstring wraps at about 95**. Therefore, I did **rewrap it and fold that into the `fix:`
  commit, so the history carries no separate style commit**.
- When I reviewed the **generated commits** for this functionality, I noticed **all six carried
  a `Co-authored-by` trailer naming the agent tool, which `AGENTS.md` and
  `docs/workflows/commit.md` forbid**. Therefore, I did **strip the trailer from every commit
  message before the first push, confirm 0 trailers with `git log --format=%B`, and confirm with
  `git diff` that the code was byte-identical afterwards**.
- When I reviewed the **merge of `main` after PRs #9 to #12 landed**, I noticed **PR #10 had
  added the same pytest setup this PR added (`pytest.ini`, `.vscode/settings.json`), placed
  tooling tests in `tests/tooling/`, and introduced a rule that every function in `tests/` has
  a docstring. That left 11 conflicting hunks in `AGENTS.md`, the project docs,
  `tests/README.md` and `pytest.ini`**. Therefore, I did **take `main`'s side of every
  conflict, drop this PR's duplicate pytest setup and its `tests/architecture/` scope, move the
  test to `tests/tooling/test_architecture_build.py`, turn its comments into docstrings, add it
  to the §8.2 table and the `tests/README.md` tree, and confirm it still fails with the fix
  reverted**.
- When I reviewed the **generated merge commit**, I noticed **it carried the same
  `Co-authored-by` trailer, and the first attempt to strip it with `git filter-branch` also
  rewrote the GitHub-signed merge commits from `main`, so the branch no longer contained
  `main`'s real history**. Therefore, I did **reset before pushing, redo the merge with the
  already-resolved files and finish it with `git merge --continue`, then confirm with
  `git merge-base --is-ancestor origin/main HEAD` that `main` is intact and that the merge
  has no trailer**.
- When I reviewed the **merge of `main` after PR #13 landed**, I noticed **PR #13 had created
  its own `tests/tooling/test_architecture_build.py` for nested diagrams, and its fixture wrote
  the test diagrams with `write_text` and stamped the raw bytes. On Windows that writes CRLF, so
  with this PR's fix the diagrams looked stale, `build.py` tried to render them, and the test
  crashed with `FileNotFoundError` on `npx`. On macOS it passes, which is why it went
  unnoticed**. Therefore, I did **combine both files into one, keep every PR #13 test, and
  write the fixture's diagrams with `newline="\n"` so its stamp is correct on every OS. I ran
  PR #13's tests unchanged against the fix first and watched them fail, then 6 of 6 passed. I
  also merged the two §8.2 table rows for the file into one**.
- The PR does not contain any temporary workaround because **the line endings are normalised
  inside `digest()`, the one function that computes the hash for both rendering and checking,
  so the fix holds whatever a clone's `core.autocrlf` setting is. I considered adding a
  `.gitattributes` rule (`*.mmd text eol=lf`) instead, but that only changes files after a
  re-checkout and leaves the check fragile on any clone that overrides it**.
- The PR only contains small functions that are **3 to 10 lines** long, docstrings included.
  Counted with `ast`: `digest` 3 lines, `load_build_module` 9, `write_diagram` 9,
  `test_svg_is_current_when_source_is_checked_out_with_crlf` 10,
  `test_svg_is_stale_when_source_text_changed` 9.
- I did **read the full diff from `main`, run the anti-slop linter on `src`, `tests`, `utils`
  and `docs/architecture` (no findings), and confirm that `digest()` is still the only place the
  hash is computed, with `svg_is_current()` and `render()` both calling it** to ensure that my
  feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities

  The SHA-256 literal in `test_architecture_build.py` is the test's expected value, derived
  outside the code under test from the exact bytes named in the comment beside it. It is not a
  hardcoded value in production code.
- This work is written in **`docs/architecture/build.py` and two tests added to
  `tests/tooling/test_architecture_build.py`, which PR #13 also uses for its own tests** because **`build.py` owns the render and the
  check, and `tests/README.md` scopes tests of repository files outside `src/`, including
  `docs/architecture/build.py`, to `tests/tooling/`**.
- This work belongs in a process in the DFD — **N/A**, the PR changes the team's diagram
  tooling, not brachify. No process in
  `docs/architecture/diagrams/existing-framework/dfd-1.mmd` moves.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_svg_is_current_when_source_is_checked_out_with_crlf`, and
  `python docs/architecture/build.py --check` run on this Windows checkout (exit 0)** passed.
- I wrote tests to cover abnormal situations involving **a diagram whose source text really
  changed (`test_svg_is_stale_when_source_text_changed`), which must still be reported stale**
  and they passed.
- I checked that these negative cases involving **the CRLF test run before the fix (failed with
  `assert False is True`), the CRLF test run with `digest()` reverted to raw bytes (failed
  again, also after the move to `tests/tooling/` and after combining it with PR #13's file),
  and `--check` on an unedited `main` before the fix (exit 1, all three diagrams reported
  stale on 2026-10-01, all four on 2026-10-04)** failed as expected.
- When I reviewed the **`test_svg_is_stale_when_source_text_changed`**, I noticed **it passed
  the first time it ran, because it guards behaviour that already worked, and a test that never
  fails proves nothing on its own**. Therefore, I did **keep it as a guard against an
  over-broad fix, since a `digest()` or `svg_is_current()` that reported every diagram current
  would turn it red, and say so in this receipt**.
- Among these tests, **`test_svg_is_current_when_source_is_checked_out_with_crlf` and
  `test_svg_is_stale_when_source_text_changed`** are unit tests and integration tests are not
  required because **`svg_is_current()` only reads two files and compares a hash. The real
  `--check` run on the repository's own diagrams covers the end-to-end path**.
- These tests are included in the directory
  **`tests/tooling/test_architecture_build.py`**.
- This new test PR did not break anything else in the system because **after merging `main`
  at PR #13, on Windows, `test_architecture_build.py` (6 passed, PR #13's four cases
  included) and `test_line_endings.py` (2 passed) passed, `--check` exited 0 with the diagrams
  in their new subfolders, `sh .claude/hooks/session-start.sh` exited 0 with no flags, and
  the anti-slop review reported no findings. `test_architecture_drift.py` fails 5 of 8 on
  this Windows machine, and the same 5 fail on a clean checkout of `main`, so this PR did
  not cause it. Those five tests assert the whole message. `package_drift` and
  `window_drift` build it by putting a `pathlib.Path` from `relative_to()` into an
  f-string, and on Windows that path prints with `\`. The tests expect `/`, as in
  `src/classes/mesh/intersections.py is not on the 'mesh:' line`. The check found the
  right file. The three that pass expect either an empty list
  (`test_drift_is_empty_when_the_diagram_names_every_module`,
  `test_the_real_system_architecture_names_every_module_in_src`) or a message typed with
  `/` in the source (`test_drift_names_a_new_package`). PR #14 prints the paths with
  `.as_posix()`. `test_build_executable.py` was not collected, because PyInstaller is not
  installed outside conda on this machine. Nothing under `src/` changed, so the app behaves as
  before. The app was not run and no screenshot was taken**.

### For PR #**14**

- As part of requirement **the course's Part A Backend receipts, which require the Level 0 and
  Level 1 DFDs and take them from `docs/architecture/diagrams/existing-framework/`, and the
  team's pull-request gate in `docs/workflows/make-pr.md`, which requires the diagrams to be
  redrawn when a signal, a model or an export input or output changes and
  `python docs/architecture/build.py --check` to exit 0**, the user needs to do **open
  `docs/architecture/README.md`, read the UML and the two DFDs as a true picture of which class
  creates each model, which signals connect them, and what Import reads and Export writes, and,
  on Windows, edit a `.mmd` and run `python docs/architecture/build.py` to redraw it**.
- Therefore, I implemented/generated code so that **a teammate reading the architecture docs,
  and every Team 10 student on Windows, gets diagrams that match the code. The UML now shows
  `MainWindow.initModels()` creating the five models (`main_window.py` lines 177 to 181) and
  the canvas (line 193), where it used to show `NavigationModel` owning the models and
  `DisplayModel` owning the canvas. It draws `values_changed` and `tandem_changed`
  (`main_window.py` 184 to 185, `tandem_model.py` 317 to 318) and `shapes_changed` (line 201)
  as dashed arrows. DFD level 1 adds the config JSON import (`import_view.py` line 27), the
  tandem channel and cylinder flows into Tandem, and the plan Export reads for the PDF
  (`export_view.py` line 119), and labels Export's output `STL or STEP` instead of the
  operation `boolean cut`. DFD level 0 adds the config JSON input. `build.py` now renders on
  Windows, and its drift check reports the same forward-slash paths on every OS**.

#### Review and design

- When I reviewed the **generated first draft of `dfd-1.mmd`** for this functionality, I
  noticed **it sent the tandem channel and cylinder into Tandem from the "Plan and settings"
  store. In the code they come from the other models: `TandemModel` connects to
  `ChannelsModel.tandem_changed` and `CylinderModel.values_changed` (`tandem_model.py` lines
  317 to 318), and `update_cylinder` reads the cylinder's length and diameter**. Therefore, I
  did **draw them as two flows from process 3 and process 2 into process 4, which is also what
  the UML's dashed arrows show, and re-rendered**.
- When I reviewed the **rendered UML**, I noticed **the arrow from `MainWindow` to
  `TandemModel` runs just under the `AppSignals` box, so at a glance it could look like it
  starts there**. Therefore, I did **try declaring the `AppSignals` and `Values` relations
  last. Mermaid produced an identical layout, so I reverted it to keep the diff small. The
  arrow visibly leaves `MainWindow`, and `AppSignals` has its own arrow from
  `RadiotherapyApp`**.
- When I reviewed the **generated first commit**, I noticed **it carried a `Co-authored-by`
  trailer naming the agent tool, which `AGENTS.md` and `docs/workflows/commit.md` forbid**.
  Therefore, I did **strip it from this PR's five commits only, before pushing, confirm 0
  trailers with `git log --format=%B`, and confirm with `git merge-base --is-ancestor` that
  #8's head is untouched underneath**.
- When I reviewed the **§8.2 table in the project docs**, I noticed **it had no blank line
  before "Run them from the repository root", so GitHub renders that sentence as a table row**.
  Therefore, I did **add the blank line**.
- The PR does not contain any temporary workaround because **`npx()` resolves the program the
  same way a terminal does, through `shutil.which`, so it finds `npx.cmd` on Windows and `npx`
  elsewhere with no OS branch. I considered `shell=True`, but that routes the command through
  `cmd.exe`, and this repository's own path contains a space (`cs assignments`), which would
  need quoting. I also considered hard-coding `npx.cmd` on Windows, which would add an OS
  check for something the standard library already handles. `.as_posix()` is the documented
  way to print a path with forward slashes, so the messages no longer depend on the OS**.
- The PR only contains small functions that are **6 to 15 lines** long, docstrings included.
  Counted with `ast`: `npx` 6 lines, `render` 7, `window_drift` 8,
  `test_npx_names_a_program_this_machine_can_start` 10, and `package_drift` 15, an existing
  function where I changed one line.
- I did **read the full diff from `main`, run the anti-slop linter on `src`, `tests`, `utils`
  and `docs/architecture` (no findings), and confirm that `render()` is the only place that
  starts `npx` and calls `npx()`, and that the two drift functions are the only places that
  print a source path** to ensure that my feature contribution does not contain any of the
  following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/architecture/build.py`, the three sources in
  `docs/architecture/diagrams/existing-framework/` with their rendered SVGs, and a test in
  `tests/tooling/test_architecture_build.py`** because **`docs/architecture/README.md` owns
  every diagram and the build that renders them, a person edits only the `.mmd` files and
  `build.py` derives the SVGs, and `tests/README.md` scopes tests of
  `docs/architecture/build.py` to `tests/tooling/`**.
- This work belongs in a process in the DFD — **N/A**, the PR corrects the diagrams and the
  team's diagram tooling. No brachify process moves. The processes in
  `docs/architecture/diagrams/existing-framework/dfd-1.mmd` are the same five tabs, with the
  flows between them corrected.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_npx_names_a_program_this_machine_can_start`, all 8 tests in
  `tests/tooling/test_architecture_drift.py` on Windows, and running
  `python docs/architecture/build.py` on this Windows checkout, which rendered the three
  changed diagrams, followed by `--check` (exit 0 for all seven diagrams)** passed.
- I wrote tests to cover abnormal situations involving **a module, package, model or view
  that `system-architecture.mmd` does not name. Those are the existing drift tests from #12,
  which this PR makes pass on Windows rather than adds** and they passed.
- I checked that these negative cases involving **the `npx` test before the fix (failed with
  `FileNotFoundError`), the drift tests before the fix (5 of 8 failed on backslash paths),
  `.as_posix()` removed again on purpose (5 failed), and `npx()` made to return the bare name
  `"npx"` again on purpose (1 failed)** failed as expected.
- When I reviewed the **`test_npx_names_a_program_this_machine_can_start`**, I noticed **it
  starts `npx --version` rather than a full render, so it does not prove a diagram renders**.
  Therefore, I did **keep it that way, because a render downloads mermaid-cli and takes about
  a minute, and cover the full render by running `build.py` on Windows, which rendered the
  three diagrams in this PR**.
- Among these tests, **the 8 drift tests in `test_architecture_drift.py`** are unit tests and
  **`test_npx_names_a_program_this_machine_can_start`, which starts the real `npx` through the
  operating system,** are integration tests.
- These tests are included in the directory **`tests/tooling/`, in
  `test_architecture_build.py` and `test_architecture_drift.py`**.
- This new test PR did not break anything else in the system because **on Windows,
  `python -m pytest --ignore=tests/tooling/test_build_executable.py` passed 17 of 17,
  `--check` exited 0, `sh .claude/hooks/session-start.sh` exited 0 with no flags, and the
  anti-slop review reported no findings. `test_build_executable.py` was not collected,
  because PyInstaller is only in the conda environment, which this machine does not have. I
  opened the rendered UML and DFD level 1 in a browser and checked every arrow and label
  against the code. Nothing under `src/` changed, so the app behaves as before. The app was
  not run**.
