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
  ([1](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/129f218/docs/logs/ahab/screenshots/week-5/pr-22-1-export-grey-before-a-cylinder.png),
  [2](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/129f218/docs/logs/ahab/screenshots/week-5/pr-22-2-export-enabled-after-apply-settings.png),
  [3](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/129f218/docs/logs/ahab/screenshots/week-5/pr-22-3-export-open-and-highlighted.png))**.

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

---

### For PR #**24**

- As part of requirement **FR-CN-02, cylinder property editing, with this PR adding display units**, the user needs to do **select mm or cm, edit diameter, length and collar, then Apply**.
- Therefore, I implemented/generated code so that **clinicians can use either unit while geometry and config remain in mm**.

#### Data Modeling and Integrity

- This data **Cylinder dimensions** is modeled as **mm floats retained by `LengthField`** because **display rounding must not change device dimensions**. We considered alternative models such as **reading spin boxes on every switch, rejected because 175.25 mm becomes 175 mm**.
- This data **Cylinder length** uses the input validation to ensure it adheres to **60–300 mm or 6–30 cm through scaled widget limits**.
- This data may be vulnerable to security issues — **N/A**, this PR adds no external input format.
- This data may be vulnerable to privacy issues — **N/A**, dimensions contain no patient identifiers.
- This data stores sensitive information and uses encryption — **N/A**, this PR adds no sensitive storage.
- The data has access controls — **N/A**, brachify has no user roles.

#### Backend

- The system uses **the existing view/model architecture** because **config reset must update the current Cylinder view**. Benefits for using this pattern include **unchanged mm models**. Possible risks include **display values mistaken for mm**.
  - To mitigate **unit confusion**, we implemented **`set_dimensions_mm` in the config reset path**.
  - We considered alternative solutions such as **saving the unit, rejected because the agreed choice is display only**.
- The system architecture diagram consists of the following major components: **views, state, domain services, libraries and local storage**. This structure has low coupling because **conversion stays in `LengthField`**. This structure has high cohesion because **each field owns one length control**. This design is scalable because **additional controls can reuse the same conversion seam**.

[Unchanged system architecture](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/3278fc2/docs/architecture/diagrams/system-architecture.svg)

- The system uses a database — **N/A**, brachify has no database.
- The system uses **synchronous processing** because **Apply consumes the current controls**. This method is done by **Qt slots**. Benefits for using this approach include **immediate model updates**. Possible risks include **signal-driven rounding**.
  - To mitigate **rounding**, we implemented **`QSignalBlocker` for programmatic renders**.
  - We considered alternative solutions such as **reading the rounded widget, rejected by the precision test**.
- The system adopts a **stateful** approach to state management because **pending edits must survive switches**. This method is done by **retaining exact mm values per field**. Benefits for using this approach include **no rounding drift**. Possible risks include **stale cached edits**.
  - To mitigate **stale edits**, we implemented **`valueChanged` recording in mm**.
  - We considered alternative solutions such as **changing live settings on selection, rejected because selection must not Apply**.
- The Level 0 DFD consists of the following major components: **physicist, TPS, brachify and CAD/printer**. **Cylinder inputs may be mm or cm; config remains mm**.

[Unchanged DFD level 0](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/3278fc2/docs/architecture/diagrams/existing-framework/dfd-0.svg)

- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem and Export**. **Cylinder converts cm before model/config updates**. **Out-of-range length input is clamped by the scaled widget before Apply**.

[Unchanged DFD level 1](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/3278fc2/docs/architecture/diagrams/existing-framework/dfd-1.svg)

- The backend API must serve clients — **N/A**, brachify has no network API.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-02 display-unit support → `tests/views/test_cylinder_view.py`, test PR #25**.
- By using a tool to check test coverage — **N/A**, coverage was not measured.

#### Frontend

- The frontend uses **mm values cached in four `LengthField` instances** received from the backend because **display precision differs between units**. Benefits for using this pattern include **preserving exact configuration values**. Possible risks include **programmatic mm writes to cm controls**.
  - To mitigate **wrong writes**, we implemented **`set_dimensions_mm` for model/config updates**.
- The frontend ensures only authorized users can access restricted pages — **N/A**, brachify has no login or restricted pages.
- The frontend is designed using **PySide6 and generated `.ui` layouts** with design components for **Cylinder controls**. Therefore, changing the design of **`cylinder_view.ui`** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **conversion is in `length_field.py`**.
- The usability evaluation identified major problems — **N/A**, no formal usability evaluation was performed.
- The frontend adopts accessibility principles — **N/A**, no accessibility evaluation was performed.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-02 display-unit support → all-four-fields, bounds and Apply integration cases in the test PR #25**.
- By using a tool to check test coverage — **N/A**, coverage was not measured.

#### Review and design

- When I reviewed the **config reset path** for this functionality, I noticed **direct mm writes become cm input when cm is selected**. Therefore, I did **route updates through `set_dimensions_mm`**.
- The PR does not contain any temporary workaround because **one reusable field adapter owns unit conversion and exact mm storage**.
- The changed field/view functions are **2–37 lines long; the inherited `resetAllValues` is 103 lines with one call changed, counted with Python AST; generated layout functions excluded**.
- I did **review the full diff and run anti-slop with no findings** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`windows/length_field.py`, `cylinder_view.py`, its generated layout and `settings/reset.py`** because **conversion belongs at the widget boundary**.
- This work belongs in **Cylinder** in the DFD because **it converts clinician input into mm dimensions**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **cm display and Apply in `test_cylinder_view.py` (8 cases passed on the test PR #25)** passed.
- I wrote tests to cover abnormal situations involving **config reset before/after a cylinder and repeated unit switches** and they passed.
- I checked that these negative cases involving **wrong cm factor, wrong Apply conversion and rounded mm cache deliberately introduced during mutation checks** failed as expected.
- When I reviewed the **`cylinder_window` fixture**, I noticed **shared app signals could retain earlier windows**. Therefore, I did **disconnect navigation and height receivers during teardown**.
- Among these tests, **none** are unit tests and **all eight real widget/model cases** are integration tests.
- These tests are included in the directory **`tests/views/` on the test PR #25**.
- This new test PR did not break anything else in the system because **28 suite cases pass and Ahab supplied a cm GUI screenshot and Ex1 terminal output, recorded in [GUI evidence and terminal excerpt](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/6fc7159/docs/logs/ahab/evidence/cylinder-units-gui.md); the image is not archived, Ex2/tandem and Export after the edit remain visually unverified, and the existing `_key_map` bug appeared**.

---

### For test PR #**25** written to assess functionality in **#24, Cylinder display units**

#### Testing receipts

- The functionality works correctly because the happy path tests involving **cm display and Apply in `test_cylinder_view.py` (8 cases passed in this PR)** passed.
- I wrote tests to cover abnormal situations involving **config reset before/after a cylinder and repeated unit switches** and they passed.
- I checked that these negative cases involving **wrong cm factor, wrong Apply conversion and rounded mm cache deliberately introduced during mutation checks** failed as expected.
- When I reviewed the **`cylinder_window` fixture**, I noticed **shared app signals could retain earlier windows**. Therefore, I did **disconnect navigation and height receivers during teardown**.
- Among these tests, **none** are unit tests and **all eight real widget/model cases** are integration tests.
- These tests are included in the directory **`tests/views/` in this PR**.
- This new test PR did not break anything else in the system because **28 suite cases pass and Ahab supplied a cm GUI screenshot and Ex1 terminal output, recorded in [GUI evidence and terminal excerpt](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/6fc7159/docs/logs/ahab/evidence/cylinder-units-gui.md); the image is not archived, Ex2/tandem and Export after the edit remain visually unverified, and the existing `_key_map` bug appeared**.

---

### For PR #**29**

- As part of requirement **the course's weekly team log (Part B), with the week's DFD and system
  architecture diagram**, the user needs to do **open `docs/logs/team/week-5.md` and audit each
  member's merged week 5 work against its PR and the diagrams**.
- Therefore, I implemented/generated code so that **the instructor and Team 10 get a week 5 Part
  B covering the 11 merged PRs, with diagrams pinned at `e3cc2ae`**.

#### Review and design

- When I reviewed the **generated claim that every receipt records a test failing before the
  fix**, I noticed **#24 and #25 record failures under deliberate breaks instead
  (`docs/logs/ahab/week-5.md` line 182)**. Therefore, I did **reword it to "failing before the
  fix or with it deliberately broken"**.
- The PR does not contain any temporary workaround because **it adds only markdown, with no code
  logic**.
- The PR only contains small functions — **N/A**, no function changed.
- I did **a grep of the log for `TODO`, `[...]`, `_or_` and `(If applicable` (0 matches)** to
  ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- The review by **an independent reviewer agent** identified **#21 counted as on `main`, and
  the size overrun blamed on stacking**. Therefore, I did **mark #21 not on `main` (`git
  merge-base --is-ancestor a0fe720 e3cc2ae` exits 1) and give #19, #22 and #24's sizes before
  their tests (12, 14 and 17 files)**.
- This work is written in **`docs/logs/team/week-5.md`** because **`docs/logs/README.md` puts
  one team log per week in `team/`**.
- This work belongs in a process in the DFD — **N/A**, brachify's data flow is unchanged.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **each table row
  against `gh pr view` (files, lines and approvers, 11 of 11 match)** passed.
- I wrote tests to cover abnormal situations involving **stacked PRs, by checking that each
  merge commit is an ancestor of `main` (6 of 7)** and they passed.
- I checked that these negative cases involving **#21's merge commit `a0fe720` (not an ancestor
  of `main`) and #28 (still open)** failed as expected.
- When I reviewed the generated tests — **N/A**, no tests were generated.
- Among these tests, unit and integration tests — **N/A**, the checks are shell commands, not
  tests in `tests/`.
- These tests are included in the directory — **N/A**, no test file changed.
- This new test PR did not break anything else in the system because **only markdown changed,
  and `python -m pytest` (63 passed), `build.py --check` and `session-start.sh` (exit 0) pass**.

