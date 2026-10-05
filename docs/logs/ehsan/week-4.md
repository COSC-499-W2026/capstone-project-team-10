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
  the anti-slop review reported no findings. `test_architecture_drift.py` fails 5 of 8 with
  backslash paths in its messages, identically on a clean checkout of `main`, so this PR did
  not cause it. `test_build_executable.py` was not collected, because PyInstaller is not
  installed outside conda on this machine. Nothing under `src/` changed, so the app behaves as
  before. The app was not run and no screenshot was taken**.
