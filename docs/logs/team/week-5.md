# Week 5, Team

_Team log. Part B, written once for the whole team, covering everyone's merged work this week.
The template is in [docs/logs/README.md](../README.md#team-log-part-b)._

**Authors:** Ahab Masud Siddiqui (`Ayyhab`).

**PRs covered:** the 10 PRs that reached `main` from 2026-10-05 to 2026-10-11, Pacific time, and
#21. Ehsan's #28 was still open at 23:40 on 2026-10-11, so it belongs to week 6. Numbers are from
GitHub and from `main` at `e3cc2ae`. The receipts are in each author's
`docs/logs/<student>/week-5.md`. #20, #23 and #25 are test PRs that merged into their parent's
branch and reached `main` with it. #21 merged into #20's branch 8 seconds after #20 had merged,
so its fix is not on `main`.

| PR | Author | What it did | Files | Lines changed | Approved by |
|---|---|---|---|---|---|
| [#17](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/17) | Ariq | "Keep Part A minimal" rule in `/make-pr` | 7 | 123 | Ehsan, Gilles |
| [#18](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/18) | Ariq | Init guide to the inherited code, bugs §7.7 to §7.9 | 8 | 5,509 | Ahab |
| [#19](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/19) | Ariq | Channels list keeps its current item on the selected channel | 15 | 462 | Ahab |
| [#20](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/20) | Ariq | Tests for #19 after a tab switch or viewport pick | 7 | 282 | Ahab |
| [#21](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/21) | Ariq | Black Channels spin box arrows in macOS dark mode (not on `main`) | 9 | 241 | Ahab |
| [#22](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/22) | Ahab | Export tab disabled until a cylinder exists | 17 | 628 | Ariq |
| [#23](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/23) | Ahab | Tests for #22 before and after a cylinder exists | 7 | 261 | Ariq |
| [#24](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/24) | Ahab | Cylinder dimensions shown in mm or cm | 20 | 689 | Ariq |
| [#25](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/25) | Ahab | Tests for #24's display units and mm geometry | 6 | 280 | Ariq |
| [#26](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/26) | Ehsan | `DicomData.reset()` clears `central_axis_flag`, with two tests | 7 | 160 | Gilles, Ariq |
| [#27](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/27) | Gilles | Validated RTSTRUCT structure decoding | 11 | 624 | Ariq |

## Part B: What Our Team Added and How the Changes Satisfy Software Engineering Principles

- This week, we decided to focus on **the first test-first changes to `src/`, split across the
  proposal's two requirement groups: FR-CN, the cylinders, needles and templates, and FR-SV,
  visualising the organs and tumour** with the goal of **every member merging tested `src/` code
  in PRs within 10 files and 500 lines, as our week 4 log planned**.
- The work was distributed so that **Ariq** focused on **FR-CN in the Channels tab: the list
  following the selected channel (#19, tests #20) and spin box arrows in dark mode (#21, not on
  `main`), plus the minimal Part A rule (#17) and the init guide (#18)**, **Ahab** focused on
  **FR-CN in the Cylinder and Export tabs: Export disabled until a cylinder exists (#22, tests
  #23) and mm or cm display units (#24, tests #25)**, **Ehsan** focused on **FR-SV-01: no field
  of one patient's import survives into the next (#26)**, and **Gilles** focused on **FR-SV-01
  and FR-SV-03: decoding and classifying RTSTRUCT organs and tumours, with no GUI caller yet
  (#27)**. We considered alternative workload distributions such as **none that we recorded.
  Splitting by requirement group kept each pair in its own part of `src/`: `src/windows/` and
  `src/settings/` for FR-CN, `src/classes/dicom/` for FR-SV**.
- Based on **GitHub and `main` at `e3cc2ae`**:
  - **all four members merged tested `src/` code into `main` (Ariq #19 and #20, Ahab #22 to #25,
    Ehsan #26, Gilles #27), and each author's receipt records at least one new test failing
    before the fix or with it deliberately broken**
  - **`python -m pytest` went from 20 passed (observed 2026-10-10 at `559a382`) to 63 passed
    (observed 2026-10-11 at `e3cc2ae`)**
  - **of the 10 PRs on `main`, 5 are within 10 files and 500 lines, 2 are under 200 lines, and
    none is under 3 files. #18 (5,509 lines), #19 (15 files), #22 (17 files, 628 lines), #24 (20
    files, 689 lines) and #27 (11 files, 624 lines) are over**

  we did not meet this goal due to the following challenges encountered: **the code goal was met,
  but the size goal was not. #19, #22 and #24 were already 12, 14 and 17 files before their test
  PRs merged into them, mostly documentation and screenshots, because each PR updates the
  documentation it affects. #18 and #27 were each one large change: a 5,073-line guide, and a new
  reader with its 24 tests. #21 merged into a branch that had already merged, so it missed
  `main`**. Our plan for next week will be **creating custom needles (FR-CN-01, and FR-CN-14,
  defining a needle by points or by angles), merging Ehsan's #28 (config loading tests),
  re-opening #21 against `main`, and splitting each feature into smaller PRs, so that its code,
  tests and documentation stay within 10 files and 500 lines**.
- By doing **a new test comparing `DicomData.reset()` with `__init__` (#26)**, **Ehsan** found
  that the code base contained **changes in one component requiring changes elsewhere: every
  field `__init__` declares must be repeated in `reset()`, and `reset()` had missed
  `central_axis_flag`**. Therefore, **Ehsan** did **add it to `reset()` and keep the test, which
  names any field the two disagree on**.
  - By doing **a review of the config reset path for #24**, **Ahab** found that the code base
    contained **changes in one component requiring changes elsewhere: `settings/reset.py` wrote
    mm straight into the Cylinder spin boxes, which would read them as cm**. Therefore, **Ahab**
    did **route every update through `CylinderView.set_dimensions_mm` (`reset.py` line 21), with
    the conversion owned by `LengthField`**.
  - By doing **a review of #19**, **Ahab** found that the code base contained **similar logic
    implemented multiple times: the list's current item and `ChannelsModel`'s selection held the
    same state, and a pick in the 3D viewport updated only the model, so Disable and Set as
    Tandem acted on another channel**. Therefore, **Ariq** did **set the list's current row from
    the model, or `-1`, in `action_update_settings`, tested in #20**.
  - By doing **a timed run of the suite after adding the `fresh_window` fixture (#23)**,
    **Ahab** found that the code base contained **many dependencies between modules: the app
    singleton's signals outlive each window, so a later Apply rebuilt an earlier window's 13
    channels too (26.5 s became 40.6 s)**. Therefore, **Ahab** did **disconnect each window's
    three app-signal slots after its test**.

  Now, the team can confirm that **the code merged this week, checked by the reviews above,**
  does not contain any of the following, **except two open items: `structures.py` and
  `fileio.py` both read `ROIContourSequence`, which is left until FR-SV connects the reader to
  Import, and the views still link through `get_app().signals` (#23)**:
  - similar logic implemented multiple times
  - many dependencies between modules
  - changes in one component require changes elsewhere
- With everyone's newly merged work for this week, the system DFD looks like **the same diagrams
  as week 4. No DFD source changed: #27's reader has no caller yet, so no data flows through it,
  and the other PRs change what the views show, not what moves between processes**.

  ![DFD level 0 at e3cc2ae](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/e3cc2ae/docs/architecture/diagrams/existing-framework/dfd-0.svg)

  ![DFD level 1 at e3cc2ae](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/e3cc2ae/docs/architecture/diagrams/existing-framework/dfd-1.svg)

  The specific changes include **none**. We considered alternative data flows such as **decoding
  structures in the background, which #27 deferred until the reader has a GUI caller, and
  updating global state as each structure decodes, which #27 rejected because it would expose
  partially decoded data**.
- With everyone's newly merged work for this week, the system architecture diagram looks like
  **the updated diagram below**.

  ![System architecture at e3cc2ae](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/e3cc2ae/docs/architecture/diagrams/system-architecture.svg)

  The specific changes include **`structures` on the `dicom:` line as a standalone ROI reader,
  added by Gilles in #27 because `build.py --check` fails on a module the diagram does not name.
  Ahab's #22 also added `CylinderModel ..> MainWindow : values_changed` to the UML, because the
  Export button now waits for that signal**. We considered alternative architectural components
  **in #27: bare dictionaries instead of frozen `Structure` and `Contour` dataclasses, rejected
  because they lose the named fields, and joining records by position instead of by ROI number,
  rejected because it fails on shuffled records**. We considered alternative dependencies
  **none, because no PR this week added or removed one. `environment.yml` and `spec-file.txt`
  did not change, and #27's reader imports only pydicom and the standard library**.
- We changed our collaboration process so that **Part A is minimal (#17), a fix and its tests go
  in stacked PRs (#19 and #20, #22 and #23, #24 and #25), and a GUI regression run is committed
  as screenshots beside the author's log (#19, #22)**. The reason we did this is because **week 4
  took a mark from two logs for length, #19's description split its tests out to stay under the
  size limits, and the course's regression receipt asks for a screenshot as proof**. We
  considered alternatives **such as one PR per fix with its tests. Stacking did not keep the
  parents under 10 files either (#19 was 12 before #20 merged into it), and #21, merged into a
  branch that had already merged, never reached `main`. So next week each test PR targets `main`
  once its parent merges**.
- We did not amend the team contract this week. **No commit has touched `docs/contract/` since
  `a7879b5` on 2026-09-25.**
