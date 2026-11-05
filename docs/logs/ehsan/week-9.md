# Week 9, Ehsan

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

## Stack #234 to #236, at a glance

Three stacked PRs for Hide all. Each is based on the one below it, closes its own issue, and should be retargeted to main once its parent merges. A row's counts are that PR's own diff only.

| PR | On | Closes | What this PR adds | Own diff (files, lines) | New tests | Suite after |
|---|---|---|---|---|---|---|
| [#234](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/234) | `main` | #150 | Hide all button | 8, +156/−5 | 1 | 419 passed, 8 failed |
| [#235](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/235) | #234 | #232 | Hide all on the DFD and UML | 9, +38/−15 | 0 | inherited |
| [#236](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/236) | #235 | #233 | Hide all on the system architecture | 3, +23/−4 | 0 | inherited |

### Shared by every PR in this stack

- Code quality checklist: **`PYTHONPATH=agent-skills/anti-slop-py/src python -m anti_slop review --base main src tests utils` reported no findings. `python docs/architecture/build.py --check` exited 0. `sh .claude/hooks/session-start.sh` exited 0 with no UNDOCUMENTED or STALE ROW line.**
- Not applicable: **database (none), backend API (none), security sanitization, privacy sanitization, encryption, access controls (no network or logins), restricted pages (no logins), usability evaluation (none run), test coverage (no coverage tool)**.

### For PR #**234** (1 of 3, on main)

- As part of requirement **FR-SV-03**, the user needs to do **open Structures, click Hide all, then check one organ again**.
- Therefore, I implemented/generated code so that **the medical physicist clears every listed structure in one click and can show one organ again**.

#### Backend

- The system uses **`StructuresModel.hide_all`** because **visibility is already the set of requested ROI numbers**. Benefits for using this pattern include **the existing `changed` signal refreshes the list and the preview**. Possible risks include **a surface that finishes after the click showing the organ again**.
  - To mitigate **a late surface coming back**, we implemented **`_accept_surface` attaching a mesh only while the ROI is still in `visible`**.
  - We considered alternative solutions such as **a new signal, which the list and the viewport would both have to learn**.
- The system architecture diagram consists of the following major components: **presentation, application state, domain services, libraries, local storage**. This structure has low coupling because **Hide all adds no signal and no file**. This structure has high cohesion because **requested visibility stays on `StructuresModel`**. This design is scalable because **a later Show all can fill the same set**. [system architecture](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/main/docs/architecture/diagrams/system-architecture.svg)
- The system uses **synchronous data processing** because **the click runs on the GUI thread**. This method is done by **`hide_all` clearing `visible` and emitting `changed`**. Benefits for using this approach include **the checkboxes update in the same turn as the click**. Possible risks include **a pending reconstruction still running**.
  - To mitigate **that result redrawing a hidden organ**, we implemented **the same `visible` check `_accept_surface` already uses**.
  - We considered alternative solutions such as **cancelling the worker, which `clear` already cannot do for the task in flight**.
- The system adopts a **stateful** approach to state management because **`visible` is the list of organs the preview may draw**. This method is done by **`visible.clear()`**. Benefits for using this approach include **a later `set_visible` shows one organ without reloading the plan**. Possible risks include **dropping the surface cache**.
  - To mitigate **rebuilding a mesh the physicist will show again**, we implemented **leaving `_surfaces` and `unavailable` in place**.
  - We considered alternative solutions such as **calling `clear`, which would drop the plan**.
- The Level 0 DFD consists of the following major components: **treatment planning system, medical physicist, printer, brachify**. **Hide all is another physicist input on the existing structures edge. The label is updated in the next PR of this stack.** [DFD level 0](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/main/docs/architecture/diagrams/existing-framework/dfd-0.svg)
- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem, Export, Structures preview**. **Happy path: Hide all empties requested visibility and the preview draws no anatomy. Failure path: a mismatched frame stays in `unavailable` and its row stays disabled.** [DFD level 1](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/main/docs/architecture/diagrams/existing-framework/dfd-1.svg)
- Not applicable: **traceability matrix (FR-SV not complete)**.

#### Frontend

- The frontend is designed using **PySide6** with design components for **a Hide all `QPushButton` above the structure list**. Therefore, changing the design of **that button** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **the rows still come from `structure_list_rows`**.
- Not applicable: **data caching (no backend fetch), accessibility (no new principle adopted)**.

#### Review and design

- When I reviewed the **Structures controls** for this functionality, I noticed **Change colour already sits above the list, so the October button placement would have landed in front of it**. Therefore, I did **put Hide all under Change colour**.
- The PR does not contain any temporary workaround because **`hide_all` clears the existing `visible` set and uses `changed`**.
- The PR only contains small functions that are **8 lines** long (`hide_all`).
- Code quality checklist: **see Shared**.
- This work is written in **`structures_model.py` and `structures_view.py`** because **visibility is model state and the button is the Structures control**.
- This work belongs in **Structures preview** in the DFD because **anatomy stays display-only and Export is unchanged**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_hide_all_clears_listed_organs_and_one_can_return` (1 new; the file already held the other structure-display tests)** passed.
- I wrote tests to cover abnormal situations involving **a structure from another frame staying disabled (`unavailable` still contains `frame`)** and they passed.
- I checked that these negative cases involving **`hide_all` emitting `changed` without `visible.clear()` (bladder and rectum stayed in `presentations()`)** failed as expected.
- Among these tests, **`test_hide_all_clears_listed_organs_and_one_can_return`** are integration tests and unit tests are not required because **the failure is the button not clearing the model the list shows**.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` on this branch is 419 passed, 8 failed. The new test passed. The 8 are pre-existing on main: `test_the_default_dome_tandem_cut_out_is_unchanged`, `test_channels_settings_keep_their_height_in_the_default_window`, `test_cylinder_spin_boxes_keep_their_height_in_the_default_window`, `test_the_cylinder_tab_never_scrolls_sideways_in_the_default_window`, `test_generate_spin_boxes_keep_their_height_in_the_default_window`, `test_the_tandem_tab_never_scrolls_sideways_in_the_default_window`, `test_toggling_checkbox_does_not_drop_highlight`, and `test_click_after_keyboard_navigation_can_rehighlight`. [author: attach a screenshot of the pytest summary and the Hide all button]**
- Not applicable: **generated-test review (no generated test)**.

### For PR #**235** (2 of 3, on #234)

- As part of requirement **FR-SV-03**, the user needs to do **read the flow pictures and see Hide all as an input to brachify**.
- Therefore, I implemented/generated code so that **the DFD and UML name Hide all on the existing structures path**.

#### Review and design

- When I reviewed the **DFD and UML labels** for this functionality, I noticed **they named visibility, mode, opacity, and highlight, and not Hide all**. Therefore, I did **add Hide all on those three edges and render the pictures**.
- Code quality checklist: **see Shared**.
- This work is written in **`docs/architecture/`** because **that folder owns the pictures and the rule for when they change**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`python docs/architecture/build.py --check` (exit 0) and the three `.mmd` labels containing `Hide all`** passed.
- This new test PR did not break anything else in the system because **the diff against `feat/structures-hide-all` is documentation only, and `--check` exited 0**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no code, the check is `build.py --check`)**.

### For PR #**236** (3 of 3, on #235)

- As part of requirement **FR-SV-03**, the user needs to do **read the system architecture and see Hide all among the Structures controls**.
- Therefore, I implemented/generated code so that **the presentation layer names Hide all**.

#### Review and design

- When I reviewed the **presentation-layer box** for this functionality, I noticed **it named Surface, Outlines, Both, opacity, and row highlight, and not Hide all**. Therefore, I did **add Hide all to that line and render the picture**.
- Code quality checklist: **see Shared**.
- This work is written in **`docs/architecture/diagrams/system-architecture.mmd`** because **that picture is the layer map, and `--check` compares it with `src/`**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`python docs/architecture/build.py --check` (exit 0) and the presentation-layer line containing `Hide all`** passed.
- This new test PR did not break anything else in the system because **the diff against #235 is the system architecture picture only, and `--check` exited 0**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no code, the check is `build.py --check`)**.
