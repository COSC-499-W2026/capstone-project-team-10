# Week 5, Ahab

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**22**

- As part of requirement **FR-CN-10 (Milestone 2), start a design without importing a DICOM
  file**, the user needs to do **open brachify, see Export greyed out, press Apply Settings on
  the Cylinder tab or import a plan, then open the Export tab**.
- Therefore, I implemented/generated code so that **physicists can open the Export tab only once
  a cylinder exists, from an import or from Apply Settings, instead of breaking the tabs**.

#### Frontend

- The frontend uses **`CylinderModel.values_changed` to enable the Export button** received from
  the backend because **that signal fires on both ways to get a cylinder**. Benefits for using
  this pattern include **the button follows the model, with no separate "plan imported" flag**.
  Possible risks include **code that sets `cylindermodel.cylinder` directly leaves Export
  disabled**.
  - To mitigate **that risk**, we implemented **a §7.6 trap saying a new cylinder must go
    through `CylinderModel`**.
- The frontend ensures only authorized users — **N/A**, brachify has no logins or restricted
  pages.
- The frontend is designed using **PySide6 with Qt Designer `.ui` files and stylesheets** with
  design components for **the nav bar and the five tab views**. Therefore, changing the design
  of **`NAV_BUTTON_STYLE`** will automatically change the look and feel of all instances of that
  component throughout the system. Changes to the content will not affect the design because
  **the button labels come from `main_window.ui` and the colours from the two style strings**.
- The usability evaluation identified the following major problems — **N/A**, no usability
  evaluation was run.
- The frontend adopts accessibility principle — **N/A**, the PR adds a disabled state, which
  WCAG 2.1 SC 1.4.11 exempts from contrast.
- The following traceability matrix shows the list of requirements completed in this milestone
  and their associated tests: **FR-CN-10 → test PR #23,
  `tests/windows/test_main_window.py`**
- By using a test coverage tool — **N/A**, the repo has no coverage tool.

#### Review and design

- When I reviewed the **generated `main_window.py` changes** for this functionality, I did not
  find any problems with it because **the five tests in test PR #23 fail on `main` and
  under four deliberate breaks of the fix, and pass with it**.
- The PR does not contain any temporary workaround because **the button follows
  `CylinderModel`, the one owner of the cylinder**.
- The PR only contains small functions that are **2 (`enable_export_view`) and 7 (each
  `change_color_*`) lines, plus 4 and 2 lines added to `__init__` (36) and `initModels` (17)**
  long.
- I did **`anti_slop review --base main` (no findings) and a read of the diff** to ensure that my
  feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/windows/main_window.py`** because **`MainWindow` owns the nav
  buttons and wires the models in `initModels`**.
- This work belongs in **Export, DFD level 1** because **it decides when that process can
  start**.

#### Testing receipts

- The functionality works correctly because the happy path tests — **N/A**, the tests are in
  test PR #23.
- I wrote tests to cover abnormal situations — **N/A**, the tests are in test PR #23.
- I checked that these negative cases — **N/A**, the tests are in test PR #23.
- When I reviewed the generated tests — **N/A**, the tests are in test PR #23.
- Among these tests, unit and integration tests — **N/A**, the tests are in test PR #23.
- These tests are included in the directory — **N/A**, the tests are in test PR #23.
- This new test PR did not break anything else in the system because **`python -m pytest` (20
  passed), `build.py --check` and `session-start.sh` (exit 0), and a macOS run with no plan,
  where Export was grey and did nothing, then enabled and highlighted after Apply Settings
  ([1](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/32f86a6/docs/logs/ahab/screenshots/pr-22-1-export-grey-before-a-cylinder.png),
  [2](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/32f86a6/docs/logs/ahab/screenshots/pr-22-2-export-enabled-after-apply-settings.png),
  [3](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/32f86a6/docs/logs/ahab/screenshots/pr-22-3-export-open-and-highlighted.png))**.

### For test PR #**23** written to assess functionality in **#22, disabling the Export tab until a cylinder exists**

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_export_tab_opens_once_cylinder_settings_are_applied`,
  `test_export_button_is_enabled_after_a_plan_is_imported` and
  `test_export_button_is_highlighted_after_opening_export_with_applied_settings` (25 passed)**
  passed.
- I wrote tests to cover abnormal situations involving **clicking Export before a cylinder
  exists (`test_clicking_export_before_a_cylinder_exists_stays_on_the_import_tab`) and the
  disabled look surviving a tab click
  (`test_export_button_looks_disabled_after_visiting_another_tab`)** and they passed.
- I checked that these negative cases involving **the tests on `main` without #22 (3 failed)
  and four deliberate breaks of #22, such as dropping the `:disabled` rule (each caught)** failed
  as expected.
- When I reviewed the **generated `fresh_window` fixture**, I noticed **the app's signals
  outlive each window, so a later Apply Settings also rebuilt an earlier window's 13 Ex1
  channels (26.5 s run became 40.6 s)**. Therefore, I did **disconnect each window's three
  app-signal slots after its test**.
- Among these tests, **none** are unit tests and **all five** are integration tests.
- These tests are included in the directory **`tests/windows/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (25
  passed), `anti_slop review` (no findings), `build.py --check` and `session-start.sh` (exit
  0)**.
