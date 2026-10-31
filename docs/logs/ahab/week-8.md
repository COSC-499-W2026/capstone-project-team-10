# Week 8, Ahab

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

## Stack #184 to #195, at a glance

| PR | On | Closes | Adds | Own diff | New tests | Suite after |
|---|---|---|---|---|---|---|
| #184 | main | #112 | the straight custom applicator, its form and button | 9 files, 499 lines | 20 | 321 passed, 17 failed |
| #194 | #184 | #112 | the bend, with Bend radius, Theta and Phi | 8 files, 233 lines | 12 | 333 passed, 17 failed |
| #195 | #194 | #112 | Remove Applicator for custom applicators | 8 files, 395 lines | 7 | 340 passed, 17 failed |

The 17 failures are in `test_structure_surfaces.py` and `test_structure_display.py`, and are the same in every PR, since `scipy` and `skimage` are not in this conda env.

### Shared by every PR in this stack

- The code quality checklist, for every PR in the stack: **no hardcoded values, duplicate code, dead code, unnecessary function calls, excessive conditional logic, deep nesting, high cyclomatic complexity, or classes, modules and functions with many unrelated responsibilities, checked with `anti_slop review --base <parent branch> src tests utils` and a line-by-line read of each diff**.
- Checks run on every PR: **`python docs/architecture/build.py --check` and `sh .claude/hooks/session-start.sh`, both exit 0**.
- Not applicable to any PR in the stack: **security, privacy, encryption, access controls (typed numbers, nothing stored); database, data processing, state management, backend API (unchanged or none); data caching, restricted pages, design components, usability evaluation; test coverage (no tool)**.

### For PR #**184**

- As part of requirement **FR-CN-01, create custom needles, and FR-CN-07, they reach the 3D export and the PDF**, the user needs to do **import Ex1, press Add Applicator..., type a name, a start on the base and two lengths, press OK, then export the STL and the PDF**.
- Therefore, I implemented/generated code so that **medical physicists can add a straight custom applicator that is listed, drawn, cut and put on the sheet like a plan needle**.

#### Data Modeling and Integrity

- This data **`CustomNeedleSpec`** is modeled as **a frozen dataclass of floats** because **the dialog, model and builder share one value that cannot change on the way**. We considered alternative models such as **a dict, which anti-slop bans for inward values**.
- This data **`CustomNeedleSpec`** uses the input validation to ensure it adheres to **finite numbers, lengths above 0 mm, Length 1 at most the cylinder length, a start within the radius less the needle radius, and a name not blank or repeated**.
- Not applicable: **security, privacy, encryption, access controls (typed numbers, nothing stored)**.

#### Backend

- The system architecture diagram consists of the following major components: **External, Presentation, Application state, Domain services, Libraries and Local storage**. This structure has low coupling because **the dialog reaches the rules only through `ChannelsModel.custom_needle_error`**. This structure has high cohesion because **`custom_needle_points` alone turns numbers into points**. This design is scalable because **the bend adds fields to the spec and one step to the builder**.

  **[System architecture (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74b0d97b3381c4d7ecc1b4e2d9eedef3d0c3734b/docs/architecture/diagrams/system-architecture.svg)**
- The Level 0 DFD consists of the following major components: **medical physicist, treatment planning system, brachify and printer or CAD**. **A typed needle comes out in the STL and the PDF**.

  **[DFD level 0 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74b0d97b3381c4d7ecc1b4e2d9eedef3d0c3734b/docs/architecture/diagrams/existing-framework/dfd-0.svg)**
- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem and Export**. **Channels takes the numbers, ChannelsModel builds the points and the channel, and Export cuts it**. **A start 50 mm out raises `CustomNeedleError` and the dialog stays open showing the text (screenshot 1, panel 3)**.

  **[DFD level 1 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74b0d97b3381c4d7ecc1b4e2d9eedef3d0c3734b/docs/architecture/diagrams/existing-framework/dfd-1.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-01 → `test_the_points_run_from_the_tissue_end_down_to_the_base`, `test_add_applicator_offers_the_first_free_name_and_adds_a_row_and_cancel_adds_nothing`; FR-CN-07 → `test_the_export_cut_removes_the_new_needle_from_the_cylinder`, `test_the_reference_sheet_lists_the_new_applicator_with_its_own_number`**
- Not applicable: **architectural pattern, database, data processing, state management, backend API (unchanged or none), test coverage (no tool)**.

#### Frontend

- The frontend adopts accessibility principle **WCAG 3.3.1, Error Identification**. The aspects that demonstrate this principle in the system include **a refused start is explained in words under the fields, with no colour needed (screenshot 1, panel 3)**.
- Not applicable: **data caching, restricted pages, design components, usability evaluation, traceability matrix (in Backend), test coverage (none)**.

#### Review and design

- When I reviewed the **new button's route through the `.ui`**, I noticed **it made the PR 10 files and over 500 lines with the regenerated `channels_view_ui.py`**. Therefore, I did **build the button in `ChannelsView.__init__` and leave the `.ui` alone**.
- The PR does not contain any temporary workaround because **the only gap, no bend yet, is the next PR's scope and every refusal is real**.
- The PR only contains small functions that are **at most 24 lines (`AddApplicatorDialog.__init__`)** long.
- I did **`anti_slop review --base main src tests utils` (three `shape` name warnings that AGENTS.md rule 6 says to ignore) and a line-by-line read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`helper.py`, `channels_model.py` and `channels_view.py`** because **a new module needs the architecture diagram redrawn, and these hold the geometry helpers, channel state and Channels tab**.
- This work belongs in **3 Channels** in the DFD because **it is another way to create a channel**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_an_added_applicator_is_visible_and_its_solid_opens_through_the_base`, `test_the_export_cut_removes_the_new_needle_from_the_cylinder` and `test_the_reference_sheet_lists_the_new_applicator_with_its_own_number` (20 new)** passed.
- I wrote tests to cover abnormal situations involving **a blank or imported name, no plan, a length change after adding, and Cancel** and they passed.
- I checked that these negative cases involving **four deliberate breaks (points reversed, height offset dropped, a repeated name allowed, the dialog closing on bad numbers)** failed as expected.
- Among these tests, **the 10 in `test_custom_needle_points.py`** are unit tests and **the 10 in `test_add_custom_needle.py`** are integration tests through the real window.
- These tests are included in the directory **`tests/mesh/` and `tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (321 passed, 17 failed, all in the structure surface tests with library failure, since `scipy` and `skimage` are not in the conda env), `build.py --check` and `session-start.sh` (exit 0), and brachify run on macOS with Ex1, driven by a script that pressed the real button, then an STL and a PDF exported (screenshot 1, whose panel 6 is the pytest result text drawn from the real output)**.

  ![1, Ex1 on macOS, the Add Applicator... button, the new row, a refused start, the 3D views and the pytest run](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/0f08474df7f5efe25818e39c924932b4c142199c/docs/logs/ahab/screenshots/week-8/pr-184-1-add-applicator.png)

- Not applicable: **generated-test review (no problem found)**.

### For PR #**194** (2 of 5, on #184)

- As part of requirement **FR-CN-01, create custom needles with a bend**, the user needs to do **import Ex1, press Add Applicator..., type a start, two lengths, a bend radius, Theta and Phi, press OK, then export the STL and the PDF**.
- Therefore, I implemented/generated code so that **medical physicists can add a custom applicator that runs straight up, turns by Theta towards Phi along an arc, and runs on into tissue**.

#### Data Modeling and Integrity

- This data **`CustomNeedleSpec`** is modeled as **#184's frozen dataclass with `radius`, `theta` and `phi` added, each defaulting to 0 so a straight needle is unchanged** because **one value still travels from the form to the builder**. We considered alternative models such as **a separate bend class, which would give the dialog and model a second value to carry**.
- This data **`CustomNeedleSpec`** uses the input validation to ensure it adheres to **finite numbers, Theta from 0 to 89 degrees, and a radius above 0 mm whenever Theta is above 0**.
- Not applicable: **see Shared**.

#### Backend

- The system architecture diagram consists of the following major components: **as in #184**. This structure has low coupling because **the form still reaches the rules only through `ChannelsModel.custom_needle_error`**. This structure has high cohesion because **`bent_needle_points` alone makes the arc**. This design is scalable because **a new bend field is one more spec field and one more step in that function**.

  **[System architecture (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74b0d97b3381c4d7ecc1b4e2d9eedef3d0c3734b/docs/architecture/diagrams/system-architecture.svg)**
- The Level 0 DFD consists of the following major components: **as in #184**. **A bent needle comes out in the STL and the PDF**.

  **[DFD level 0 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74b0d97b3381c4d7ecc1b4e2d9eedef3d0c3734b/docs/architecture/diagrams/existing-framework/dfd-0.svg)**
- The Level 1 DFD consists of the following major processes: **as in #184**. **A bend with no radius raises `CustomNeedleError` and the form stays open showing the text (screenshot 1, panel 2)**.

  **[DFD level 1 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74b0d97b3381c4d7ecc1b4e2d9eedef3d0c3734b/docs/architecture/diagrams/existing-framework/dfd-1.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-01 → `test_a_bend_turns_the_needle_by_theta_towards_phi_after_a_radius_arc`, `test_a_bend_is_sampled_along_the_arc_from_the_joint_to_the_arc_end`, `test_a_bent_applicator_solid_reaches_sideways_to_where_the_bend_sends_it`**
- Not applicable: **see Shared**.

#### Frontend

- The frontend adopts accessibility principle **WCAG 3.3.1, Error Identification**. The aspects that demonstrate this principle in the system include **a bend with no radius is explained in words under the fields, with no colour needed (screenshot 1, panel 2)**.
- Not applicable: **see Shared, and traceability matrix (in Backend)**.

#### Review and design

- When I reviewed **my first bend, sampled every 10 degrees and tested at 90 degrees**, I noticed **`rounded_channel` opens its modal error box when the last pipe is exactly flat, which stalled the offscreen test and would show a clinician an error box**. Therefore, I did **stop Theta at 89 degrees and record the trap in §7.6, rather than change inherited channel code in this PR**.
- The PR contains one limit that works around inherited code, because **Theta stops at 89 since `rounded_channel` cannot build a flat last pipe (§7.6)**.
- The PR only contains small functions that are **at most 28 lines (`AddApplicatorDialog.__init__`)** long. The two it adds or splits are **19 lines (`custom_needle_points`) and 11 lines (`bent_needle_points`)**.
- I did **`anti_slop review --base feat/custom-needle-straight src tests utils` (no findings) and a line-by-line read of the diff** to ensure that my feature contribution does not contain any of the following: **see Shared**.
- This work is written in **`helper.py` and `channels_view.py`** because **#184 put the builder and the form there, and a new module needs the architecture diagram redrawn**.
- This work belongs in **3 Channels** in the DFD because **it is another way to create a channel**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_a_bend_turns_the_needle_by_theta_towards_phi_after_a_radius_arc` and `test_a_bent_applicator_solid_reaches_sideways_to_where_the_bend_sends_it` (12 new; 21 in `test_custom_needle_points.py` and 11 in `test_add_custom_needle.py`)** passed.
- I wrote tests to cover abnormal situations involving **a Theta of 90 or below 0, NaN, a bend with no radius, an infinite Phi, and Theta 0 with a radius left in the form** and they passed.
- I checked that these negative cases involving **two deliberate breaks (Phi measured from +Y, the arc cut to one chord)** failed as expected.
- Among these tests, **the 11 new in `test_custom_needle_points.py`** are unit tests and **the 1 new in `test_add_custom_needle.py`** is an integration test through the real window.
- These tests are included in the directory **`tests/mesh/` and `tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (333 passed, 321 after #184, 17 failed, all in the structure surface tests with library failure, since `scipy` and `skimage` are not in the conda env), and brachify run on macOS with Ex1, driven by a script that pressed the real button, then an STL (2.1 MB) and a PDF (45 KB) exported (screenshot 1, whose panel 6 is the pytest result text drawn from the real output)**.

  ![1, Ex1 on macOS, the bend form, a refused bend, the new row, the bent needle in 3D and the pytest run](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/9cb94d086df77cd34bd7e2684386853b72b3821f/docs/logs/ahab/screenshots/week-8/pr-194-1-bend.png)

- Not applicable: **generated-test review (no problem found)**.

### For PR #**195** (3 of 5, on #194)

- As part of requirement **FR-CN-01, create custom needles, and edit or remove them**, the user needs to do **select a custom applicator on the Channels tab, press Remove Applicator, then export the STL and the PDF**.
- Therefore, I implemented/generated code so that **medical physicists can delete a custom applicator they added, and the export no longer cuts it**.

#### Data Modeling and Integrity

- This data **`ChannelsModel.custom_specs`** is modeled as **a dict from label to `CustomNeedleSpec`, filled when an applicator is added and cleared with a new plan** because **a plan channel has no spec, so the dict is also the record of which channels are custom, and the Edit PR needs the numbers back**. We considered alternative models such as **a flag on `NeedleChannel`, which would add a field to inherited geometry code for a UI rule**.
- This data **`custom_specs`** uses the input validation to ensure it adheres to **only a custom applicator being removable, and never the one that is the tandem**.
- Not applicable: **see Shared**.

#### Backend

- The system architecture diagram consists of the following major components: **as in #184**. This structure has low coupling because **the view only calls `remove_custom_needle` and reads `is_custom_needle`**. This structure has high cohesion because **removal clears a label from every list that holds it in one method**. This design is scalable because **a new list that keys on a label is one more line in that method**.

  **[System architecture (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74b0d97b3381c4d7ecc1b4e2d9eedef3d0c3734b/docs/architecture/diagrams/system-architecture.svg)**
- The Level 0 DFD consists of the following major components: **as in #184**. **A removed needle is no longer in the STL or the PDF**.

  **[DFD level 0 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74b0d97b3381c4d7ecc1b4e2d9eedef3d0c3734b/docs/architecture/diagrams/existing-framework/dfd-0.svg)**
- The Level 1 DFD consists of the following major processes: **as in #184**. **Channels deletes the channel, so Export cuts one hole fewer, and the export volume returns to 98960.757 mm cubed (screenshot 1, panel 6)**.

  **[DFD level 1 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74b0d97b3381c4d7ecc1b4e2d9eedef3d0c3734b/docs/architecture/diagrams/existing-framework/dfd-1.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-01 → `test_removing_a_custom_applicator_puts_the_export_cut_back_as_it_was`, `test_the_remove_button_takes_the_selected_applicator_out_of_the_model_and_the_list`, `test_a_plan_applicator_cannot_be_removed_and_nothing_changes`**
- Not applicable: **see Shared**.

#### Frontend

- The frontend adopts accessibility principle **WCAG 4.1.2, Name, Role, Value**. The aspects that demonstrate this principle in the system include **Remove Applicator is really disabled with `setEnabled`, and now greyed too, for a plan applicator and the tandem (screenshot 1, panels 2 and 3). I did not run a screen reader**.
- Not applicable: **see Shared, and traceability matrix (in Backend)**.

#### Review and design

- When I reviewed **my first screenshot of the button**, I noticed **Remove looked on while it was off, because the style copied from Disable has no disabled rule**. Therefore, I did **add a disabled rule in `make_applicator_button`, with a test, which also fixes Add Applicator... without a plan**.
- The PR contains one gap, because **Remove has no confirmation and no undo, so a deleted needle is re-added by hand**.
- The PR only contains small functions that are **at most 28 lines (`AddApplicatorDialog.__init__`, moved unchanged)** long. The ones it adds are **11 lines (`remove_custom_needle`) and 7 lines (`make_applicator_button`)**.
- I did **`anti_slop review --base feat/custom-needle-bend src tests utils` (no findings) and a line-by-line read of the diff** to ensure that my feature contribution does not contain any of the following: **see Shared**.
- This work is written in **`channels_model.py`, `channels_view.py` and a new `add_applicator_dialog.py`** because **`channels_view.py` was at 499 lines, and the new file is not a `*_view.py` and adds no layer, so the diagram check passes without a redraw**.
- This work belongs in **3 Channels** in the DFD because **it deletes a channel**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_removing_a_custom_applicator_puts_the_export_cut_back_as_it_was` and `test_the_remove_button_takes_the_selected_applicator_out_of_the_model_and_the_list` (7 new; 7 in `test_remove_custom_needle.py`)** passed.
- I wrote tests to cover abnormal situations involving **a plan applicator, the tandem, a disabled and selected applicator with its own diameter, and a new import** and they passed.
- I checked that these negative cases involving **two deliberate breaks (own diameter kept after removal, Remove left on for the tandem)** failed as expected, and **the disabled look assertion failed before its code**.
- Among these tests, **none are pure unit tests** and **all 7** are integration tests through the real window.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (340 passed, 333 after #194, 17 failed, all in the structure surface tests with library failure, since `scipy` and `skimage` are not in the conda env), and brachify run on macOS with Ex1, driven by a script that pressed the real Remove button and measured the export (screenshot 1, whose panel 6 is the pytest result and the volumes drawn from the real output)**.

  ![1, Ex1 on macOS, the Channels tab with Remove Applicator on, greyed, and after pressing it, the front view before and after, and the pytest run](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/658ed9196672839de90d7cdc95310d40a6b539c7/docs/logs/ahab/screenshots/week-8/pr-195-1-remove.png)

- Not applicable: **generated-test review (no problem found)**.
