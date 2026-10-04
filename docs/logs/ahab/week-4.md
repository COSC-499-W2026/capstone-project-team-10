# Week 4, Ahab

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**4**

- As part of requirement **the course's weekly Part B receipts, which ask the team to show its system DFD and architecture diagram, and the need for a newcomer to see the app without reading the long project doc**, the user needs to do **open `docs/architecture/README.md`, read the UML, DFD level 0 and DFD level 1, open `viewer.html` to zoom and pan a crowded picture, and before opening a PR run `python docs/architecture/build.py --check`**.
- Therefore, I implemented/generated code so that **the instructor, the TAs and the four Team 10 students get a one-page architecture map with three diagrams (`docs/architecture/README.md`, `diagrams/uml.mmd`, `dfd-0.mmd`, `dfd-1.mmd`), and agents are told to redraw them before a PR when the code they show changes (`AGENTS.md`, `docs/workflows/make-pr.md`, `pull_request_template.md`)**.

#### Review and design

- When I reviewed the **first generated placement of the map, `docs/architecture.md` with the pictures in `docs/diagrams/`**, for this functionality, I noticed **a reviewer, Ariq, said the map should not live there, and asked for either a section in the project docs or a folder of its own, with every reference to a stale file updated**. Therefore, I did **move everything into `docs/architecture/` (the README, `diagrams/`, `build.py` and `viewer.html`) and update `AGENTS.md`, `docs/README.md`, the project docs, `make-pr.md` and the PR template to point there. On 2026-10-02, at the merge commit, a grep of the documentation set for `architecture.md` outside `docs/architecture/` and for `docs/diagrams` returns 0 matches**.
- When I reviewed the **generated UML, DFD level 0 and DFD level 1**, I noticed **reviewers Ariq and Writable04 were asked to check that the two DFDs match the app, and Writable04 observed that they show the current system and suggested adding diagrams of the intended design**. Therefore, I did **keep the pictures to the current system, mark them *Reasoned from code*, and say in the README that the next eight months of work are not written down in the repository, rather than inventing a plan**. On 2026-10-02 I compared the UML and both DFDs with `src/` again and found them consistent with it. That is *Reasoned from code*, and the app was not run.
- The PR does not contain any temporary workaround because **it adds documentation and one build script. The pictures are rendered from the `.mmd` sources by `build.py`, which stamps each SVG with the hash of its source, so a stale picture is detected instead of papered over**.
- The PR only contains small functions that are **2 to 10 lines** long. They are `digest`, `sources`, `unembedded`, `viewer_text`, `header`, `size`, `svg_is_current`, `render`, `build`, `check`, `install_hook` and `viewer_body` in `build.py`, counted with `ast` at the merge commit.
- I did **run `anti_slop review --base 68dc1e5^1 docs/architecture/build.py` at the merge commit, which reported no findings, and grep the documentation set for the removed `architecture.md` and `docs/diagrams` paths** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/architecture/` (new)** because **a reviewer asked for one folder that holds the map and all its diagrams, rather than a file in `docs/` or a long section of the project docs**.
- This work belongs in a process in the DFD — **N/A**, the PR documents brachify and changes no code in it. No process in `docs/architecture/diagrams/dfd-1.mmd` moves.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`python docs/architecture/build.py --check` (exit 0) and `sh .claude/hooks/session-start.sh` (exit 0), both run at the merge commit on 2026-10-02** passed. These are repository checks run from the shell, not tests in `tests/`. How I checked the zoom and pan page at the time: **[describe how you opened `viewer.html` and checked zoom and pan, and add a screenshot]**.
- I wrote tests to cover abnormal situations — **N/A**, `build.py` had no tests when this PR merged, because the test runner was added later in #10. Tests for `build.py` start in #12.
- I checked that these negative cases involving **appending a line to `uml.mmd` in a scratch checkout of the merge commit without re-rendering** failed as expected: `build.py --check` printed `STALE uml.mmd` and exited 1, then exited 0 again once the file was restored.
- When I reviewed the generated tests — **N/A**, no tests were generated.
- Among these tests, unit and integration tests — **N/A**, none of the checks is a unit or integration test. They are shell checks on the repository.
- These tests are included in the directory — **N/A**, nothing was added to `tests/`. The check lives in `docs/architecture/build.py`.
- This new test PR did not break anything else in the system because **`git diff --name-only` between the merge commit and its first parent lists no file under `src/`, so the app is unchanged. The app was not run and no screenshot of it was taken**.

### For PR #**12**

- As part of requirement **the instructor's request for a system architecture design, which this repository lacked beside the UML and the two DFDs, and the weekly Part B in `docs/logs/README.md`, which asks the team to report its system architecture diagram each week**, the user needs to do **open `docs/architecture/README.md`, read the system architecture diagram to see which layer every module sits in, and later open a PR that adds a module and be told by `build.py --check` to name it in the diagram**.
- Therefore, I implemented/generated code so that **the instructor, the TAs and the four Team 10 students get a layered system architecture diagram (`docs/architecture/diagrams/system-architecture.mmd`), and so that a PR that adds a module, package, model or view the diagram does not name fails `python docs/architecture/build.py --check`, `python -m pytest` and the optional pre-commit hook**.

#### Review and design

- When I reviewed the **first generated `system-architecture.mmd`** for this functionality, I noticed **it drew one node per module with about 40 edges, and the render stacked each layer into a tall column with edges crossing the page, in three rounds of redrawing, so a reader could not follow it**. Therefore, I did **redraw it as five layer boxes with seven labelled edges, and move the per-module detail into the layer table in `docs/architecture/README.md` and into the `dicom:`, `mesh:`, `pdf:` and `settings:` lines, which `drift()` checks**.
- When I reviewed the **generated `drift()` in `docs/architecture/build.py`**, I noticed **it searched the whole diagram for a module name, so `fileio`, which sits under both `dicom:` and `mesh:`, would have counted a new `pdf/fileio.py` as named**. Therefore, I did **match each module only against its own package's line, and added `test_drift_does_not_match_a_module_name_on_another_package_line`**.
- When I reviewed the **generated `drift()` a second time**, I noticed **it read module-level constants, so a test could not point it at a temporary tree, and it listed `("dicom", "mesh", "pdf")` by hand, so a file in a new package was never checked**. Therefore, I did **give it `src` and `mmd` parameters, derive the packages from the folders under `src/classes`, and add `test_drift_names_each_file_in_a_new_package`, which failed first**.
- When I reviewed the **generated line in `docs/workflows/make-pr.md`** for this functionality, I noticed **it told agents to paste `uml.mmd` as the system architecture diagram, which is wrong once this PR adds the real one**. Therefore, I did **change it to `system-architecture.mmd`. I left `docs/logs/ariq/week-4.md` alone, since log entries record work already done**.
- When I reviewed the **first generated description of this PR**, I noticed **it had no Part A, left its N/A boxes unticked, and had no log entry, all of which `make-pr.md` requires**. Therefore, I did **write this Part A, tick the N/A boxes, and commit the same text to `docs/logs/ahab/week-4.md`**.
- When I reviewed the **merge of this branch onto `main`**, I noticed **my working tree also held unrelated uncommitted edits to `src/windows/views/export_view.py` and `viewport.py`, and the lines in the project docs that describe them**. Therefore, I did **leave the `src/` edits out of this PR, remove the doc lines that described them, and keep this PR to documentation and tooling**.
- The PR does not contain any temporary workaround because **the drift check is a permanent test of `src/` against the diagram. It cannot see a change that adds no file, such as a new library, and `docs/architecture/README.md` and `AGENTS.md` say so and tell the author to redraw by hand in that case**.
- The PR only contains small functions that are **2, 3, 8, 8, 14 and 15 lines** long. They are `camel`, `named`, `package_lines`, `window_drift`, `drift` and `package_drift` in `build.py`. The tests are 4 to 14 lines, and the `tree` fixture is 23 lines, most of it 12 calls to `write`. All were counted with `ast`, decorator and docstring included.
- I did **run `anti_slop review --base origin/main tests docs/architecture/build.py`, which reported no findings, read `drift()` for fixed values and repeated loops, and grep the documentation set for every list that named the three diagrams** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/architecture/` (the new `.mmd` and `.svg`, and `build.py`) and `tests/tooling/test_architecture_drift.py`** because **`docs/architecture/README.md` owns every diagram and the build that renders them, and `AGENTS.md` scopes tests of repository files outside `src/` to `tests/tooling/`**.
- This work belongs in a process in the DFD — **N/A**, the PR documents and checks brachify's structure and changes no code in it. No process in `docs/architecture/diagrams/dfd-1.mmd` moves.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_drift_is_empty_when_the_diagram_names_every_module` and `test_the_real_system_architecture_names_every_module_in_src`, together with `python docs/architecture/build.py --check` (exit 0) and `sh .claude/hooks/session-start.sh` (exit 0, no `UNDOCUMENTED` or `STALE ROW` line)** passed. `python -m pytest` reports 13 passed, with the 5 that already existed.
- I wrote tests to cover abnormal situations involving **a new mesh module, a new package, a new file inside a new package, a new model, a new view, the same module name on another package's line, and `__init__.py` and `custom_view.py`, which must not be flagged** and they passed.
- I checked that these negative cases involving **matching a name against the whole diagram (1 failed), counting `__init__.py` as a module (5 failed), matching against an empty line (7 failed), and removing `intersections` from the real diagram (the real-diagram test failed and `build.py --check` exited 1)** failed as expected. Each was reverted and all 13 passed again.
- When I reviewed the **`test_the_real_system_architecture_names_every_module_in_src`**, I noticed **it passed on its first run, because the real diagram was already complete, so I had never seen it fail for a real reason**. Therefore, I did **remove `intersections` from the real diagram on purpose, watch it fail, and restore the file from a copy**.
- Among these tests, **`test_drift_is_empty_when_the_diagram_names_every_module`, `test_drift_names_a_new_mesh_module`, `test_drift_names_a_new_package`, `test_drift_names_each_file_in_a_new_package`, `test_drift_names_a_new_model`, `test_drift_names_a_new_view` and `test_drift_does_not_match_a_module_name_on_another_package_line`** are unit tests, run on a temporary tree, and **`test_the_real_system_architecture_names_every_module_in_src`** is an integration test, because it reads the real `src/` and the real diagram.
- These tests are included in the directory **`tests/tooling/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` passes with 13 tests, `python docs/architecture/build.py --check` exits 0, `sh .claude/hooks/session-start.sh` exits 0, and `git diff --name-only origin/main...HEAD` lists no file under `src/`, so the app is unchanged. The app was not run and no screenshot was taken**.
