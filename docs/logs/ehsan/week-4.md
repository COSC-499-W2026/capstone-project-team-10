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
  source, so a Windows clone and a macOS or Linux clone agree on the same fingerprint. The
  team also gets the repository's first pytest setup (`pytest.ini`, `.vscode/settings.json`
  pointed at `tests`) and its first tests (`tests/architecture/test_build.py`)**.

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
- The PR does not contain any temporary workaround because **the line endings are normalised
  inside `digest()`, the one function that computes the hash for both rendering and checking,
  so the fix holds whatever a clone's `core.autocrlf` setting is. I considered adding a
  `.gitattributes` rule (`*.mmd text eol=lf`) instead, but that only changes files after a
  re-checkout and leaves the check fragile on any clone that overrides it**.
- The PR only contains small functions that are **3 to 6 lines** long. Counted with `ast`:
  `digest` 3 lines, `write_diagram` 5, `test_svg_is_current_when_source_is_checked_out_with_crlf`
  6, `test_svg_is_stale_when_source_text_changed` 4.
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

  The SHA-256 literal in `test_build.py` is the test's expected value, derived outside the code
  under test from the exact bytes named in the comment beside it. It is not a hardcoded value in
  production code.
- This work is written in **`docs/architecture/build.py` and the new
  `tests/architecture/test_build.py`** because **`build.py` owns the render and the check, and
  `tests/` is scoped by subfolder to the code it covers. The new `tests/architecture/` scope is
  recorded in `tests/README.md` and `AGENTS.md`**.
- This work belongs in a process in the DFD — **N/A**, the PR changes the team's diagram
  tooling, not brachify. No process in `docs/architecture/diagrams/dfd-1.mmd` moves.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_svg_is_current_when_source_is_checked_out_with_crlf`, and
  `python docs/architecture/build.py --check` run on this Windows checkout (exit 0)** passed.
- I wrote tests to cover abnormal situations involving **a diagram whose source text really
  changed (`test_svg_is_stale_when_source_text_changed`), which must still be reported stale**
  and they passed.
- I checked that these negative cases involving **the CRLF test run before the fix (failed with
  `assert False is True`), the CRLF test run with `digest()` reverted to raw bytes (failed
  again), and `--check` on an unedited `main` before the fix (exit 1, all three diagrams
  reported stale)** failed as expected.
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
  **`tests/architecture/test_build.py`**.
- This new test PR did not break anything else in the system because **after merging the
  latest `main`, `python -m pytest` passed (2 passed), `--check` exited 0,
  `sh .claude/hooks/session-start.sh` exited 0 with no flags, and the anti-slop review reported
  no findings. Nothing under `src/` changed, so the app behaves as before. The app was not run
  and no screenshot was taken**.
