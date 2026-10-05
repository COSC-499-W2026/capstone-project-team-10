# Week 4, Team

_Team log. Part B, written once for the whole team, covering everyone's merged work this week.
The template is in [docs/logs/README.md](../README.md#team-log-part-b)._

**Authors:** Ariq Muldi (`ariqmuldi`), Ehsan (`ebabar5`), Ahab Masud Siddiqui (`Ayyhab`),
Gilles Fricker (`Writable04`).

**PRs covered:** the nine PRs merged into `main` between 2026-09-29 and 2026-10-04. Every number
below was taken from GitHub or from `main` at commit `901bce9`, and the PR receipts are in each
author's `docs/logs/<student>/week-4.md`.

| PR | Author | What it did | Files | Lines changed | Approved by |
|---|---|---|---|---|---|
| [#4](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/4) | Ahab | UML, DFD level 0 and level 1, `build.py`, zoomable viewer | 14 | 583 | Ehsan, Ariq |
| [#7](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/7) | Ariq | Part A receipts in the PR template, `/make-pr`, weekly logs | 15 | 738 | Ahab, Gilles |
| [#8](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/8) | Ehsan | `build.py --check` passes on Windows CRLF checkouts | 6 | 215 | Ariq, Gilles |
| [#9](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/9) | Ariq | Same dependencies on Windows, macOS and Linux | 7 | 299 | Ehsan, Ahab |
| [#10](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/10) | Ariq | `pytest.ini`, first tests, pydicom hidden-import fix | 9 | 280 | Ahab, Ehsan |
| [#11](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/11) | Ariq | Session-start hook kept at LF so it runs on Windows | 9 | 202 | Ahab, Ehsan |
| [#12](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/12) | Ahab | Layered system architecture diagram with a drift check | 12 | 404 | Ariq, Gilles |
| [#13](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/13) | Gilles | Projected-framework UML and DFDs, nested diagram folders | 22 | 503 | Ariq, Ehsan |
| [#14](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/14) | Ehsan | UML and DFDs corrected against the code, Windows build fixes | 13 | 426 | Gilles, Ariq |

## Part B: What Our Team Added and How the Changes Satisfy Software Engineering Principles

- This week, we decided to focus on **preparing to build on brachify rather than changing it
  yet. That meant one conda environment for Windows, macOS and Linux, a working pytest runner
  with the first tests, diagrams of the app as it exists (UML, DFD level 0 and level 1, a layered
  system architecture) and of the framework the proposal describes (milestone 1 FR-SV-01–07 and
  FR-CN-01–20), and a pull request process that produces the course's Part A receipts** with the
  goal of **every member being able to set up, test and understand the code base on their own
  OS, so that next week's first `src/` features can be written test-first and reviewed against
  an accurate picture of the system**.
- The work was distributed so that **Ariq** focused on **the team process and the test
  foundation. That was Part A in the PR template, `/make-pr` and the weekly logs (#7), the same
  nine dependencies on all three OSes (#9), `pytest.ini` and the first tests, with a fix to the
  build's pydicom hidden imports (#10), and keeping the session-start hook at LF so it runs on
  Windows (#11)**, **Ehsan** focused on **making the diagram tooling work on Windows, the OS
  brachify ships on. That was `build.py --check` failing on CRLF checkouts (#8), and correcting
  the UML and both DFDs against the code while fixing `npx` and the drift check's path output on
  Windows (#14)**, **Ahab** focused on **diagrams of the existing app: the UML, DFD level 0, DFD
  level 1, `build.py` and the zoomable viewer (#4), then the layered system architecture diagram
  with a drift check against `src/` (#12)**, and **Gilles** focused on **the projected
  framework: UML and DFDs for the proposal's scope, kept apart from the existing ones in
  `projected-framework/`, with the build finding diagrams in both folders (#13)**. Every member
  also reviewed: each of the nine PRs has two approving reviews from teammates other than its
  author. We considered alternative workload distributions such as **TODO (team): the
  alternatives we discussed are not recorded in any PR or log. Fill this in before submitting,
  or delete this sentence**.
- Based on **checks run on `main` at `901bce9` and the receipts in each PR**:
  - **`python -m pytest -q` went from no configured runner to 20 passing tests. Observed on
    macOS on 2026-10-04. Ehsan's #14 receipt reports the suite passing on Windows, 17 of 17,
    with the 3 PyInstaller tests ignored because that machine has no conda environment**
  - **each PR that adds tests (#8, #10, #11, #12, #13, #14) records in its testing receipt the
    tests failing before the fix, or with the fix reverted on purpose**
  - **`python docs/architecture/build.py --check` exits 0 over seven diagrams. Observed on macOS
    on 2026-10-04, and reported on Windows in #14's receipt**
  - **a macOS environment built from the §1.2 command launched the app as far as `main window
    initialization complete` (#9's receipt)**
  - **all nine PRs merged with two teammate approvals each, and every member has a week-4 log
    with a Part A for each of their PRs**

  we met this goal because **each part of the goal now has a check that passes. Setup has one
  dependency list, and the app launched from it on macOS. Testing has a runner and 20 tests that
  were shown to fail when broken. Understanding has seven diagrams, checked against `src/` by the
  drift test and against the code by the line references in #14. Process has Part A in every PR
  and log.** Limits on this claim:
  - **No PR changed `src/`, so no application behaviour is new or tested yet. All 719 lines of
    Python changed this week are tooling and tests.**
  - **The Windows environment from `spec-file.txt`, the app's DICOM import and the Export tab
    were not exercised this week. The diagrams are *Reasoned from code*, not checked against a
    running app.**
  - **PR size is an exception this week, and we are stating it openly. 4 of 9 PRs (#8 to #11)
    are under 10 files. 7 of 9 are under 500 lines: #7 has 738, and #13 has 503, with six of
    its 22 files being renames with no changed lines. None is under 3 files or 200 lines. This
    was the week we got to know the codebase and wrote down how it works and how the team works
    in it, so 2,259 of the 3,650 changed lines (62%) are markdown, and 294 more are generated SVG
    or `viewer.html`. From next week, PRs carry `src/` and `tests/` code and are held to the
    size limits.**
- By doing **a trial merge of #9 with #8 while reviewing #9**, **Ehsan** found that the code base
  contained **similar logic implemented multiple times: #8 and #10 each added the same pytest
  setup (`pytest.ini` and the `.vscode/settings.json` fix), each with its own test folder**.
  Therefore, **Ehsan** did **drop #8's copy when merging `main`, keep #10's setup, and move #8's
  tests into `tests/tooling/test_architecture_build.py`, so the runner is configured in one
  place**.
  - By doing **a run of #13's tests on Windows after merging #13 into #8**, **Ehsan** found that
    the code base contained **a change in one component that required changes elsewhere. #8 made
    `digest()` hash the LF form of each diagram, but #13's test fixture wrote its diagrams with
    the platform's line endings. On Windows the diagrams therefore looked stale and the test
    crashed on `npx`. On macOS it passed**. Therefore, **Ehsan** did **merge the two test files
    into one and write the fixture's diagrams with `newline="\n"`. Ehsan ran #13's tests unchanged
    against the fix, watched them fail, and then saw all 6 pass**.
  - By doing **a review of the generated `drift()` in `docs/architecture/build.py`**, **Ahab**
    found that the code base contained **a change in one component that required changes
    elsewhere. `drift()` listed the packages `("dicom", "mesh", "pdf")` by hand, so a new
    package in `src/classes/` would also need an edit to `build.py`. Without that edit, the new
    package's files were never checked**. Therefore, **Ahab** did **derive the packages from the
    folders under `src/classes/` and add `test_drift_names_each_file_in_a_new_package`, which
    failed first**.
  - By doing **a grep of the documentation set for every rule #7 restated**, **Ariq** found that
    the code base contained **similar logic implemented multiple times: `make-pr.md` carried a
    copy of the diagram redraw rule that `docs/architecture/README.md` owns, so the two could
    drift apart**. Therefore, **Ariq** did **replace the copy with a link to
    `docs/architecture/README.md`**.
  - By doing **the layer-by-layer reading of `src/` behind the system architecture diagram
    (#12)**, **Ahab** found that the code base contained **many dependencies between modules in
    the upstream app. Views reach other views by index and reach the models through
    `get_app().window`, and `Export_View` reads the cylinder, channel and tandem models directly
    and runs the boolean cut itself**. Therefore, **Ahab** did **record in
    `docs/architecture/README.md` that the drawn layering is the intended direction of
    dependency, not one the code enforces. §4.3 and §7.6 of the project docs already warn
    against reordering the views. The code was left as it is, because no PR this week changed
    `src/`**.

  Now, the team can confirm that **the tooling and tests added this week** do not contain any of
  the following. **This does not cover the upstream `src/` coupling in the last item, which
  is still there**:
  - similar logic implemented multiple times
  - many dependencies between modules
  - changes in one component require changes elsewhere
- With everyone's newly merged work for this week, the system DFD looks like **the updated
  diagrams below. There were no DFDs before #4 this week.**

  ![DFD level 0 at 901bce9](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/901bce9/docs/architecture/diagrams/existing-framework/dfd-0.svg)

  ![DFD level 1 at 901bce9](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/901bce9/docs/architecture/diagrams/existing-framework/dfd-1.svg)

  The specific changes include **the following:**
  - **#4 (Ahab) drew the first DFD level 0 and level 1 from `src/`.**
  - **#13 (Gilles) moved both, unchanged, into `existing-framework/`, and added separate
    projected DFDs in `projected-framework/` for the proposal's scope.**
  - **#14 (Ehsan) corrected the existing DFDs to match the code:**
    - **a config JSON input to DFD level 0 and to Import (`import_view.py` line 27)**
    - **Tandem now takes the tandem channel from Channels and the length and diameter from
      Cylinder (`tandem_model.py` lines 317 to 318)**
    - **Export reads the plan for the PDF (`export_view.py` line 119)**
    - **Export's output is labelled with the data it writes, `STL or STEP`, instead of the
      operation `boolean cut`, because a DFD flow carries data**

  We considered alternative data flows such as **the following:**
  - **#14's first draft fed Tandem from the "Plan and settings" store. It was rejected because
    `TandemModel` gets those values from `ChannelsModel.tandem_changed` and
    `CylinderModel.values_changed`.**
  - **Drawing the viewport as a sixth process. It was rejected because the viewport only paints
    shapes and transforms no data. That path is shown in the UML.**
  - **Adding the proposal's intended design, which Gilles suggested in a review of #4. #4 kept
    its DFDs to the current system, and #13 drew the proposed flows separately in
    `projected-framework/`, so that a reader never confuses what is built with what is
    proposed.**
- With everyone's newly merged work for this week, the system architecture diagram looks like
  **the new diagram below, added in #12. #13 and #14 did not change it.**

  ![System architecture at 901bce9](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/901bce9/docs/architecture/diagrams/system-architecture.svg)

  The specific changes include **the following:**
  - **The diagram is new: external actors and files above five layers (presentation,
    application state, domain services, libraries, local storage), joined by seven labelled
    edges.**
  - **The modules of `dicom`, `mesh`, `pdf` and `settings` are named on per-package lines, which
    `build.py --check` compares against `src/`. A PR that adds a module now fails until the
    diagram names it.**
  - **It was added because the instructor asked for a system architecture design and Part B
    reports one each week. The UML shows which class owns which, not layers or external files.**

  We considered alternative architectural components **such as these:**
  - **One node per module with about 40 edges. It was rejected after three rounds of redrawing,
    because the render stacked each layer into a tall column with edges crossing the page. The
    per-module detail moved into the package lines that `drift()` checks.**
  - **Reusing the UML as the architecture diagram, which `make-pr.md` pointed to before #12. It
    was rejected because the UML does not show layers or the files the app reads and writes.**

  We considered alternative dependencies **such as these:**
  - **Relying on `matplotlib` to bring in PySide6 (#9). It was rejected because the `osx-arm64`
    `matplotlib` build has no Qt dependency, so a Mac environment could not start the app. We
    now name `pyside6` explicitly.**
  - **Pinning every package to the Windows lockfile's versions (#9). It was rejected in favour
    of pinning only `python=3.12` and `pythonocc-core=7.7.2`, since full pins meant three places
    to bump on every upgrade.**
  - **Docker (#9). It was rejected because brachify is a desktop GUI that needs a screen and
    OpenGL, and the `.exe` can only be built on Windows.**
  - **`shell=True` or a hardcoded `npx.cmd` for the diagram build (#14). Both were rejected in
    favour of `shutil.which`, which finds the right program on every OS without an OS check.**
- We changed our collaboration process so that **every PR carries the course's Part A in its
  description. `/make-pr` fills it in from the diff with evidence (`docs/workflows/make-pr.md`),
  and commits the same text to the author's `docs/logs/<student>/week-<K>.md` on the PR branch.
  A checkbox that does not apply is ticked N/A, and Part B stays out of PRs, in this file (#7).
  Separately, a PR that adds a module to `src/` now fails `build.py --check` until the system
  architecture diagram names it (#12)**. The reason we did this is because **the course grades
  only merged PRs, through their Part A receipts. Keeping the receipt identical in the PR and the
  log means reviewers check the same text the instructor grades, and a log reaches `main` only
  when its PR merges**. We considered alternatives **such as these:**
  - **Putting Part B in the PR template. It was rejected while #7 was being written, because
    Part B covers the whole team's week, not one PR.**
  - **Committing the individual logs on their own branch. We kept them on each PR's branch,
    because a log on its own branch can describe a PR that never merges.**
- We did not amend the team contract this week. **No commit has touched `docs/contract/` since
  2026-09-27.**
