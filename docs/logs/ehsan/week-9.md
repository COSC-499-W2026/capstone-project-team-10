# Week 9, Ehsan

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

## Stack #234 to #236, at a glance

Three stacked PRs for Hide all. Each is based on the one below it, closes its own issue, and should be retargeted to main once its parent merges. A row's counts are that PR's own diff only. This PR is first; #235 and #236 follow on stacked branches.

| PR | On | Closes | What this PR adds | Own diff (files, lines) | New tests | Suite after |
|---|---|---|---|---|---|---|
| [#234](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/234) | `main` | #150 | Hide all button | see PR files | 3 | hide-all tests 3 passed; full suite on Windows earlier 419 passed, 8 failed |

### Shared by every PR in this stack

- Code quality checklist: **`PYTHONPATH=agent-skills/anti-slop-py/src python -m anti_slop review --base main src tests utils` reported no findings. `python docs/architecture/build.py --check` exited 0. `sh .claude/hooks/session-start.sh` exited 0 with no UNDOCUMENTED or STALE ROW line.**
- Not applicable: **database (none), backend API (none), security sanitization, privacy sanitization, encryption, access controls (no network or logins), restricted pages (no logins), usability evaluation (none run), test coverage (no coverage tool)**.

### For PR #**234** (1 of 3, on main)

- As part of requirement **FR-SV-03**, the user needs to do **open Structures, click Hide all, then check one organ again**.
- Therefore, I implemented/generated code so that **the medical physicist clears every listed structure in one click and can show one organ again**.

#### Backend

- The system uses **`StructuresModel.hide_all`** because **visibility is already the set of requested ROI numbers**. Benefits for using this pattern include **the existing `changed` signal refreshes the list and the preview**. Possible risks include **a surface that finishes after the click showing the organ again**.
  - To mitigate **a late surface coming back**, we rely on **`presentations()` returning only ROIs still in `visible`**. A finishing `_accept_surface` may still fill `_outlines` for a hidden ROI; that cache is unused until the organ is shown again. `test_hide_all_clears_surface_mode_presentations` covers Surface mode.
  - We considered alternative solutions such as **a new signal, which the list and the viewport would both have to learn**.
- The system architecture diagram consists of the following major components: **presentation, application state, domain services, libraries, local storage**. This structure has low coupling because **Hide all adds no signal and no file**. This structure has high cohesion because **requested visibility stays on `StructuresModel`**. This design is scalable because **a later Show all can fill the same set**. [system architecture](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/main/docs/architecture/diagrams/system-architecture.svg)
- The system uses **synchronous data processing** because **the click runs on the GUI thread**. This method is done by **`hide_all` clearing `visible`, clearing the highlight, and emitting `changed` only when something was visible**. Benefits for using this approach include **the checkboxes update in the same turn as the click**. Possible risks include **a pending reconstruction still running**.
  - To mitigate **that result redrawing a hidden organ**, we rely on **the same `presentations()` filter**.
  - We considered alternative solutions such as **cancelling the worker, which `clear` already cannot do for the task in flight**.
- The system adopts a **stateful** approach to state management because **`visible` is the list of organs the preview may draw**. This method is done by **`visible.clear()`**. Benefits for using this approach include **a later `set_visible` shows one organ without reloading the plan**. Possible risks include **dropping the surface cache**.
  - To mitigate **rebuilding a mesh the physicist will show again**, we implemented **leaving `_surfaces` and `unavailable` in place**.
  - We considered alternative solutions such as **calling `clear`, which would drop the plan**.
- The Level 0 DFD consists of the following major components: **treatment planning system, medical physicist, printer, brachify**. **Hide all is another physicist input on the existing structures edge. The label is updated in the next PR of this stack.** [DFD level 0](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/main/docs/architecture/diagrams/existing-framework/dfd-0.svg)
- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem, Export, Structures preview**. **Happy path: Hide all empties requested visibility and the preview draws no anatomy. Failure path: a mismatched frame stays in `unavailable` and its row stays disabled.** [DFD level 1](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/main/docs/architecture/diagrams/existing-framework/dfd-1.svg)
- Not applicable: **traceability matrix (FR-SV not complete)**.

#### Frontend

- The frontend is designed using **PySide6** with design components for **a Hide all `QPushButton` above the structure list**. Therefore, changing the design of **that button** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **the rows still come from `structure_list_rows`**. The button starts disabled and stays disabled whenever `visible` is empty.
- Not applicable: **data caching (no backend fetch), accessibility (no new principle adopted)**.

#### Review and design

- When I reviewed the **Structures controls** for this functionality, I noticed **Change colour already sits above the list, so the October button placement would have landed in front of it**. Therefore, I did **put Hide all under Change colour**.
- The PR does not contain any temporary workaround because **`hide_all` clears the existing `visible` set and uses `changed`**.
- The PR only contains small functions that are about **12 lines** long (`hide_all`).
- Code quality checklist: **see Shared**.
- This work is written in **`structures_model.py` and `structures_view.py`** because **visibility is model state and the button is the Structures control**.
- This work belongs in **Structures preview** in the DFD because **anatomy stays display-only and Export is unchanged**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_hide_all_clears_listed_organs_and_one_can_return`, `test_hide_all_clears_surface_mode_presentations`, and `test_hide_all_does_nothing_when_nothing_is_visible` (3 new)** passed.
- I wrote tests to cover abnormal situations involving **a structure from another frame staying disabled (`unavailable` still contains `frame`)** and they passed.
- I checked that these negative cases involving **`hide_all` emitting `changed` without `visible.clear()` (bladder and rectum stayed in `presentations()`)** failed as expected.
- Among these tests, **the three Hide all cases** are integration tests and unit tests are not required because **the failure is the button not clearing the model the list shows**.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest tests/views/test_structure_display.py -k hide_all -q` on this Windows machine is 3 passed. An earlier full `python -m pytest` on this Windows branch was 419 passed, 8 failed. The 8 named below are Windows layout and Structures-highlight failures on this machine; a macOS review of the same branch saw 424 passed, 3 failed, with two of those also failing on main.** The eight Windows names: `test_the_default_dome_tandem_cut_out_is_unchanged`, `test_channels_settings_keep_their_height_in_the_default_window`, `test_cylinder_spin_boxes_keep_their_height_in_the_default_window`, `test_the_cylinder_tab_never_scrolls_sideways_in_the_default_window`, `test_generate_spin_boxes_keep_their_height_in_the_default_window`, `test_the_tandem_tab_never_scrolls_sideways_in_the_default_window`, `test_toggling_checkbox_does_not_drop_highlight`, and `test_click_after_keyboard_navigation_can_rehighlight`. Evidence: [before](screenshots/week-9/pr-234-1-hide-all-before.png), [after Hide all](screenshots/week-9/pr-234-2-hide-all-after.png), [pytest hide-all](screenshots/week-9/pr-234-3-pytest-hide-all.png).
- Not applicable: **generated-test review (no generated test)**.
