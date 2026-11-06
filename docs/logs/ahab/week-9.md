# Week 9, Ahab

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

## Stack #238 to #238, at a glance

Four stacked PRs for issue #156, edit and remove any applicator, imported or custom. Each PR is
based on the one above it and is retargeted to `main` once its parent merges. A row's counts are
**that PR's own diff only**. Everything in earlier rows is inherited, not repeated.

| PR | On | Closes | Adds | Own diff | New tests | Suite after |
|---|---|---|---|---|---|---|
| [#238](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/238) | main | #156 | Remove Applicator for any applicator, a question for an imported one, and a removed one leaves the 3D view | 8 files, 243 lines | 5 (11 in the file) | 428 passed, 2 failed |

The 2 failures are `test_structure_display.py::test_toggling_checkbox_does_not_drop_highlight` and
`::test_click_after_keyboard_navigation_can_rehighlight`. They also fail on `main`.

### Shared by every PR in this stack

- The code quality checklist, for every PR in the stack: **no hardcoded values, duplicate code, dead code, unnecessary function calls, excessive conditional logic, deep nesting, high cyclomatic complexity, or classes, modules and functions with many unrelated responsibilities, checked with `anti_slop review --base <parent branch> src tests utils` and a line-by-line read of each diff**.
- Checks run on every PR: **`python docs/architecture/build.py --check` and `sh .claude/hooks/session-start.sh`, both exit 0**.
- Not applicable to any PR in the stack: **security, privacy, encryption, access controls (typed numbers, nothing stored); architectural pattern, database, data processing, state management, backend API (unchanged or none); data caching, restricted pages, design components, usability evaluation; test coverage (no tool)**.

### For PR #**238** (1 of 4, on main)

- As part of requirement **FR-CN-03, remove needles, and FR-CN-07, a removed needle is left out of the 3D export and the PDF**, the user needs to do **import Ex1, select Applicator6 on the Channels tab, press Remove Applicator, answer Yes, then export the STL and the PDF**.
- Therefore, I implemented/generated code so that **medical physicists can delete any applicator, imported or custom, with a question first for an imported one, and see it gone from the list, the 3D view, the export cut and the PDF**.

#### Backend

- The system architecture diagram consists of the following major components: **unchanged (`ChannelsModel` removes, `ChannelsView` asks and calls it, `DisplayModel` drops the shape)**. This structure has low coupling because **the view only calls `remove_channel` and the `confirm_remove` seam**. This structure has high cohesion because **`remove_channel` clears a label from every record that holds it in one method**. This design is scalable because **a new label-keyed record is one more line in that method (the viewport was missed, see Review and design)**.

  **[System architecture (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/6fa56b753644a6013574760d5a07f3f1c42581d3/docs/architecture/diagrams/system-architecture.svg)**
- The Level 0 DFD consists of the following major components: **unchanged**. **A removed needle is no longer in the STL or the PDF, which both read `get_visible_channels`**.

  **[DFD level 0 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/6fa56b753644a6013574760d5a07f3f1c42581d3/docs/architecture/existing-framework/dfd-0.svg)**
- The Level 1 DFD consists of the following major processes: **unchanged**. **Channels deletes the channel and its shape, so Export cuts one hole fewer and the 3D view draws one needle fewer (screenshot 1)**.

  **[DFD level 1 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/6fa56b753644a6013574760d5a07f3f1c42581d3/docs/architecture/existing-framework/dfd-1.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-03 → `test_a_plan_applicator_can_be_removed_and_leaves_the_export_and_the_sheet`, `test_removing_a_plan_applicator_asks_first_and_cancel_keeps_it`; FR-CN-07 → `test_a_removed_applicator_leaves_the_viewport`, `test_removing_a_custom_applicator_puts_the_export_cut_back_as_it_was`**
- Not applicable: **see Shared**.

#### Frontend

- The frontend adopts accessibility principle **WCAG 3.3.4, Error Prevention**. The aspects that demonstrate this principle in the system include **a plan applicator, which only importing again brings back, asks before it is removed, and Remove Applicator is greyed with nothing selected and for the tandem (screenshot 1). I did not run a screen reader**.
- Not applicable: **see Shared, and traceability matrix (in Backend)**.

#### Review and design

- When I reviewed **my screenshot of Ex1 after pressing Remove**, I noticed **the removed needle was still drawn, in the selected colour, because `DisplayModel.add_shapes` never drops a shape, so every removal, custom ones too, left a ghost in the 3D view that the export and the list did not have**. Therefore, I did **call `DisplayModel.remove_shape` in `remove_channel`, with `test_a_removed_applicator_leaves_the_viewport`, which failed first, and record it as §7.21**.
- The PR does not contain any temporary workaround because **it replaces `remove_custom_needle` outright and keeps no alias**.
- The PR only contains small functions that are **14 lines (`remove_channel`), 5 lines (`action_remove_applicator`) and 3 lines (`ask_remove_plan_needle`)** long.
- I did **`anti_slop review --base main src tests utils` (0 blocking) and a line-by-line read of the diff** to ensure that my feature contribution does not contain any of the following: **see Shared**.
- This work is written in **`channels_model.py` and `channels_view.py`** because **the rule is the model's and the question is the view's, through a `confirm_remove` seam like `ask_needle`, so a test answers it without a dialog**.
- This work belongs in **3 Channels** in the DFD because **it deletes a channel**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_a_plan_applicator_can_be_removed_and_leaves_the_export_and_the_sheet`, `test_a_removed_applicator_leaves_the_viewport`, `test_confirming_removes_a_plan_applicator_and_a_custom_one_is_never_asked_about` and `test_the_remove_button_is_on_for_any_selected_applicator_that_is_not_the_tandem` (5 new; 11 in `test_remove_custom_needle.py`)** passed.
- I wrote tests to cover abnormal situations involving **an unknown label (`KeyError`), the tandem, a disabled, selected applicator with its own diameter, and answering No** and they passed.
- I checked that these negative cases involving **skipping the confirm (`test_removing_a_plan_applicator_asks_first_and_cancel_keeps_it` failed) and leaving the shape in the display model (`test_a_removed_applicator_leaves_the_viewport` failed with the label still in `displaymodel.shapes`)** failed as expected.
- Among these tests, **none are pure unit tests** and **all 11** are integration tests through the real window.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (428 passed, 424 on main by test count, 2 failed, the same two on `main`), and brachify run on macOS with Ex1, driven by a script that pressed the real Remove button (screenshot 1)**.

  ![1, Ex1 on macOS, Applicator6 selected with Remove Applicator on, after Remove and Yes with the list and the 3D view one needle fewer, and the pytest output](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/e6d141a8e91eaeaeff52fcabdf016a807179c31e/docs/logs/ahab/screenshots/week-9/pr-238-1-remove.png)

- Not applicable: **generated-test review (no generated test)**.
