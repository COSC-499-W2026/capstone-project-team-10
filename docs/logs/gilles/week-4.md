# Week 4, Gilles

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**13**

- As part of requirement **the course architecture deliverable, supporting milestone 1 FR-SV-01–07 and FR-CN-01–20 and the corresponding milestone 2 controls**, the user needs to do **open the architecture README, distinguish implemented behaviour from proposed responsibilities, and inspect both sets of diagrams in the shared viewer**.
- Therefore, I implemented/generated code so that **the team can review projected UML and DFDs alongside existing diagrams, and the build validates diagrams inside either framework folder. This PR does not implement the proposed clinical features**.

#### Review and design

- When I reviewed the **framework-folder moves and `docs/architecture/build.py`**, I noticed **non-recursive discovery omitted the relocated sources, viewer links still used the old paths, and the README linked to a nonexistent projected README**. Therefore, I did **recursive discovery, relative-path viewer and embedding checks, regenerated the viewer, and corrected the README links; the four regression cases failed before the fix**.
- The PR does not contain any temporary workaround because **one existing build command now discovers both framework folders; no duplicated builder or manually edited viewer is needed**.
- The PR only contains small functions that are **2 lines (`sources`), 10 lines (`viewer_body`) and 7 lines (`unembedded`) for the modified build functions. The new fixture is 22 lines and the two test functions are 12 and 20 lines, counted with Python AST from `def` through the final statement, including docstrings** long.
- I did **review the three changed build functions, compare the existing diagrams byte-for-byte with main, run the real CLI on isolated fixture trees, and run anti-slop review with no findings** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values unrelated to the documented directory layout
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/architecture/` and `tests/tooling/test_architecture_build.py` because architecture artifacts and their existing builder belong together, while repository-tooling tests belong in the tooling scope**.
- This work belongs in **N/A, no running-application DFD process changes. The projected DFD introduces proposed structures, templates, edit history, design checks and scene review responsibilities; these remain design documentation**.

#### Testing receipts

- The functionality works correctly because the happy path test **`test_build_links_both_nested_diagrams` passed. The full conda-environment `python -m pytest -q` run reported 17 passed. The architecture build and `--check` also exited 0, and all seven generated viewer image paths resolved to parseable SVGs**.
- I wrote tests to cover abnormal situations involving **`test_check_rejects_invalid_nested_diagram[missing]`, `[stale]` and `[unembedded]`**, and they passed.
- I checked that these negative cases involving **a deleted SVG, changed source with an old SVG, and an absent README embed each made the actual `--check` CLI exit 1, as expected. Reverting recursive discovery deliberately made all four new cases fail again; restoring the fix returned them to green**.
- When I reviewed the **new CLI tests**, I noticed **a check of source text alone would not catch a broken generated viewer**. Therefore, I did **subprocess builds against temporary directory trees, asserted concrete viewer URLs, and checked exit codes for invalid inputs, without mocking the builder**.
- Among these tests, **the existing architecture drift tests** are unit tests and **the four new architecture build cases and existing tooling boundary checks** are integration tests.
- These tests are included in the directory **`tests/tooling/`; the four new cases are in `test_architecture_build.py`**.
- This new test PR did not break anything else in the system because **the full suite passed all 17 tests after installing the already-declared pytest and PyInstaller dependencies missing from the local conda environment. Initial collection failed on missing PyInstaller and passed after installation. `git diff --check`, the session-start hook and the architecture check passed. No application code changed; a GUI regression run and screenshot are N/A for this documentation/tooling change and were not performed. Windows execution and visual browser review were not performed**.

---
