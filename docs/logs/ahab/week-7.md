# Week 7, Ahab

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**118**

- As part of requirement **FR-CN-02, move a needle, and FR-CN-07, edits reach the export and the PDF**, the user needs
  to do **double-click Applicator3, type X 6, Y -4, Z 3, press OK, then export**.
- Therefore, I implemented/generated code so that **physicists can move any needle but the tandem from its plan position, with the DICOM points untouched**.

#### Backend

- The system adopts a **stateful** approach to state management because **a move must outlast later Applies**. This method is done by **`NeedleChannel.set_translation`, rebuilding `points` from the untouched `points_raw`**. Benefits for using this approach include **the shape, `get_points()` and the PDF follow one owner**. Possible risks include **a move reaching the next plan, and NaN reaching OpenCASCADE**.
  - To mitigate **both**, we implemented **new channels on import, and `ValueError` for NaN or infinity**.
- The system architecture diagram consists of the following major components: **External, Presentation, Application state, Domain services, Libraries and Local storage**. This
  structure has low coupling because **the view moves channels only through `ChannelsModel`**. This
  structure has high cohesion because **`NeedleChannel` alone derives points**. This design is
  scalable because **rotation can join `set_translation`**.

  **[System architecture (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74590f7c41937d2d609813ef1f05dde740700771/docs/architecture/diagrams/system-architecture.svg)**
- The Level 0 DFD consists of the following major components: **medical physicist, treatment
  planning system, brachify and printer or CAD**. **A moved needle comes out in the STL and PDF**

  **[DFD level 0 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74590f7c41937d2d609813ef1f05dde740700771/docs/architecture/diagrams/existing-framework/dfd-0.svg)**
- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem and Export**. **Channels takes X, Y and Z and moves the needle, and Export cuts it there**. **NaN, infinity or the tandem raises `ValueError` and the earlier move stays**.

  **[DFD level 1 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74590f7c41937d2d609813ef1f05dde740700771/docs/architecture/diagrams/existing-framework/dfd-1.svg)**
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **FR-CN-02 → `test_moving_a_channel_shifts_every_point_and_leaves_the_dicom_points`; FR-CN-07 → `test_a_move_reaches_the_pdf_points_and_the_3d_shape`**
- Not applicable: **architectural pattern (unchanged), database (none), data processing
  (unchanged), backend API (none), test coverage (no coverage tool)**.

#### Frontend

- The frontend adopts accessibility principle **WCAG 1.4.1, colour is not the only cue**. The aspects that demonstrate this principle in the system include **a moved row is underlined, and its tooltip says how far it moved (screenshot 1)**.
- Not applicable: **data caching (none), restricted pages (no logins), design components (plain Qt widgets), usability evaluation (none run), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **`NeedleChannel.get_rotation` method** for this functionality, I noticed **it read `points[0]`, so a move would turn the tandem**. Therefore, I did **read `points_raw`, with `test_moving_a_channel_keeps_the_tandems_rotation_source`**.
- The PR does not contain any temporary workaround because **moves have no limit by the team's decision, and the PDF gap that leaves is recorded in §7.14**.
- The PR only contains small functions that are **at most 15 lines in `src/` and 30 in the tests** long.
- I did **`anti_slop review --base main src tests utils` (two `no-shape-in-symbol-names` warnings, ignored per AGENTS.md rule 6)** to ensure that my feature contribution does
  not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`channels_view.py`, `channels_model.py` and `channel.py`** because **the view asks, the model validates, and the channel computes points**.
- This work belongs in **3 Channels** in the DFD because **it places each needle before Export**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_moving_a_channel_shifts_every_point_and_leaves_the_dicom_points` and `test_a_move_reaches_the_pdf_points_and_the_3d_shape` (15 passed)** passed.
- I wrote tests to cover abnormal situations involving **NaN or infinity, an unknown channel, the tandem, a moved channel set as the tandem, Cancel and a new plan** and they passed.
- I checked that these negative cases involving **six deliberate breaks (`get_rotation` on moved points, a stale shape, no underline, no `set_tandem` guard, Set as Tandem left on for a moved channel, no Double click to move hint)** failed as expected.
- Among these tests, **`test_the_popup_is_filled_with_the_current_move_and_reset_zeroes_it`** is a unit test and **the other thirteen** are integration tests.
- These tests are included in the directory **`tests/views/test_move_channel.py`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (260 passed), `build.py --check` and `session-start.sh` (exit 0), and brachify run on macOS with Ex1, driven by a script, then a PDF and an STL exported with the move (screenshot 1)**.

  ![1, Ex1 on macOS, Applicator3 moved by X 6, Y -4, Z 3 mm: top view before and after, the popup, and the underlined row](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/74590f7c41937d2d609813ef1f05dde740700771/docs/logs/ahab/screenshots/week-7/pr-118-1-move-channel.png)

- Not applicable: **generated-test review (no problem found)**.
