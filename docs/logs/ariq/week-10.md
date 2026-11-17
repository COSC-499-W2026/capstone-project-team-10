# Week 10, Ariq

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

## Stack #256 to #262, at a glance

Six stacked PRs that make the test suite fast enough to keep growing: every test file passes on its own and in its own home folder, the files run in parallel, a quick loop leaves out the tests that build a window, and the channel solids are built once and reused, with the geometry pinned first.  Each PR is based on the one above it and closes its own issue.
A row's counts are **that PR's own diff only**, as GitHub shows it against its parent.

| PR | On | Closes | What this PR adds | Own diff (files, lines) | New tests | Suite after |
|---|---|---|---|---|---|---|
| [#256](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/256) | `main` | #251 | Every test file passes alone: five viewport tests get a window, §7.22 fixed | 9, +104/−8 | 0 | 585 |
| [#262](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/262) | #256 | #261 | Each test run gets its own home, so the suite no longer uses or deletes the real `~/brachify`; §7.26 | 6, +92/−2 | 1 | 586 |

The suite had 585 tests on `main` before the stack (`22ac6a8`).

### Shared by every PR in this stack

Stated once here instead of in each section.

- **Code quality checklist.** For each PR, I did **`anti_slop review --base <parent branch>` (no findings) and a read of that PR's own diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- **Regression checks.** Every PR's regression receipt also includes **`build.py --check` and `session-start.sh`, both exit 0**. Each section gives only its own `python -m pytest` result.
- **Run on macOS only.** **Every run in this stack was on a 10-core Apple Silicon Mac. Windows and Linux are *Not verified***.


### For PR #**256** (1 of 6, on `main`)

- As part of requirement **issue #251, tests that pass in any order**, the user needs to do **run one test file alone, or the suite split across parallel workers, and get the same result as the full serial run**.
- Therefore, I implemented/generated code so that **every test file passes on its own, for the developers who run the suite**.

#### Review and design

- When I reviewed the **generated fix for the five viewport tests** for this functionality, I noticed **that giving the shared `viewport_module` fixture a window would build one for all 44 tests in the three files**. Therefore, I did **add `cylinder_window` to only the five tests that build an `OrbitCameraViewer3d`**.
- The PR does not contain any temporary workaround because **the tests use the existing `cylinder_window`, and the app fixtures set `window` to `None` as `units_app` already did**.
- The PR only contains small functions that are **19 to 30 lines (the changed tests and fixtures, docstrings included)** long.
- Code quality checklist: **see Shared**.
- This work is written in **`tests/conftest.py`, `tests/windows/conftest.py` and the three viewport test files** because **each fix sits in the fixture or test that had the order dependence**.
- Not applicable: **DFD process (no application code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **the three viewport files alone (44 passed), `tests/mesh/test_tandem.py` with `test_tandem_template_controls.py` (36 passed), and each of the 48 test files run alone (48 of 48 exit 0)** passed.
- I checked that these negative cases involving **the same runs on `main` (5 failed with `'NoneType' object has no attribute 'collisionmodel'`, and 29 errors with `'RadiotherapyApp' object has no attribute 'window'`)** failed as expected.
- These tests are included in the directory **`tests/`, `tests/windows/` and `tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest`, 585 passed (585 on `main`, 0 new; screenshot 1)**.

  ![1, python -m pytest on test/order-independent-fixtures, the three viewport files alone 44 passed and the suite 585 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/3f454b9dd7d6b3ad55d10c2db3f4e66b54797b11/docs/logs/ariq/screenshots/week-10/pr-256-1-pytest-585.png)
- Not applicable: **abnormal cases (fixtures only), generated-test review (no problem beyond the one above), unit and integration tests (no new tests)**.

### For PR #**262** (2 of 6, on #256)

- As part of requirement **issue #261, test runs that never touch the developer's files**, the user needs to do **run the suite, serially or in parallel, and keep their own `~/brachify` templates, log and last config untouched**.
- Therefore, I implemented/generated code so that **each test run, and each parallel worker, uses its own temporary home before brachify is imported, for the developers who run the suite**.

#### Review and design

- When I reviewed the **generated `pytest_configure` hook** for this functionality, I noticed **that the session fixtures already redirect HOME, but only after collection, when test modules such as `test_remove_custom_needle.py` have already imported brachify and fixed `USER_PATH`**. Therefore, I did **set HOME and USERPROFILE in `pytest_configure`, which runs before collection, and leave the fixtures as they were**.
- The PR does not contain any temporary workaround because **pytest runs `pytest_configure` once per process before importing any test module, so every worker gets its own folder**.
- The PR only contains small functions that are **10 lines (test) and 16 lines (hook, docstring included)** long.
- Code quality checklist: **see Shared**.
- This work is written in **`tests/conftest.py` and new `tests/tooling/test_test_home.py`** because **only the root conftest runs before every test module is collected**.
- Not applicable: **DFD process (no application code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_brachify_user_folder_is_inside_the_temporary_folder` (1 new; 1 in the file; screenshot 1)** passed.
- I checked that these negative cases involving **the same test before the hook, which failed with `USER_PATH` at the real home, `/Users/<name>/brachify`** failed as expected.
- Among these tests, **`test_brachify_user_folder_is_inside_the_temporary_folder`** are unit tests and integration tests are not required because **it reads one module constant**.
- These tests are included in the directory **`tests/tooling/`**.
- This new test PR did not break anything else in the system because **`python -m pytest`, 586 passed (585 after #256), with the real `~/brachify/app.log` unchanged (screenshot 1)**.

  ![1, on test/isolated-test-home, test_test_home.py 1 passed and python -m pytest 586 passed, with the real ~/brachify/app.log time the same before and after](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/72c8e3caa35b215cec7e342111f351a073c2abcf/docs/logs/ariq/screenshots/week-10/pr-262-1-pytest-586.png)
- Not applicable: **abnormal cases (one fixed path), generated-test review (no problem found)**.
