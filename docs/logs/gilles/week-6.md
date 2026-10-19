# Week 6, Gilles

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**78**

- As part of requirement **FR-SV-06 frontend, camera navigation**, the user needs to do **rotate, pan and zoom the scene while retaining click selection**.
- Therefore, I implemented/generated code so that **left-drag rotates, right/middle-drag pans, scrolling zooms proportionally and stationary left-click selects**.

#### Frontend

- The frontend uses **gesture state local to the viewport** received from the backend because **camera interaction does not change imported geometry**. Benefits for using this pattern include **independent camera movement**. Possible risks include **selection on drag release**.
  - To mitigate **accidental selection**, we implemented **a sticky drag flag and the platform drag threshold**.
- The frontend is designed using **PySide6 and OpenCASCADE** with design components for **the shared 3D viewport**. Therefore, changing the design of **mouse handling** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **gesture rules operate independently of displayed geometry**.
- The frontend adopts accessibility principle **tolerance for pointer jitter**. The aspects that demonstrate this principle in the system include **the platform drag threshold, covered by `test_small_left_motion_is_a_click`; no accessibility certification is claimed**.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-SV-06 camera-navigation subset maps to `test_camera_controls.py`; full structure framing remains outside this PR**.
- Not applicable: **restricted pages (no authentication), usability evaluation (no formal study), test coverage (no percentage measured)**.

#### Review and design

- When I reviewed the **left-release handler** for this functionality, I noticed **it selected after every left release**. Therefore, I did **suppress selection after a drag, including a drag returning to its starting point**.
- The PR does not contain any temporary workaround because **the same gesture rules drive the viewport and the regression tests**.
- The PR only contains small functions that are **4–19 lines for added or changed production functions and 7–11 lines for test functions, counted with AST** long.
- I did **review the diff, run the suite and lint, and check the native camera against Ex1 and Ex2** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/windows/views/viewport.py`** because **that widget owns camera input**.
- This work belongs in **scene review** in the DFD because **it changes camera interaction without changing data flows or geometry**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **incremental right/middle panning and reversible zoom, within 69 passing suite cases** passed.
- I wrote tests to cover abnormal situations involving **pointer jitter, a drag returning to its origin, distant releases without intermediate events, and zero wheel delta** and they passed.
- I checked that these negative cases involving **removing drag suppression, which caused two failures** failed as expected.
- When I reviewed the **controls fixture**, I noticed **importing the logger before isolating user files could touch real settings**. Therefore, I did **reuse the existing `units_app` fixture**.
- Among these tests, **the six new cases** are unit tests and **native Ex1/Ex2 camera checks through Qt events** are integration checks.
- These tests are included in the directory **tests/views/**.
- This new test PR did not break anything else in the system because **69 tests passed, lint and architecture checks passed, and native Ex1/Ex2 rotation, pan, zoom, selection and Export renders passed; render captures were inspected locally but are not attached**.

### For PR #**79**

- As part of requirement **the requested central-axis reference toggle, supporting viewport inspection alongside frontend FR-SV-06**, the user needs to do **load a model and show or hide its centre line**.
- Therefore, I implemented code so that **users can toggle a reference line without changing the camera or exported geometry**.

#### Backend

- The system uses **Qt signals and the existing model/view split** because **reset must notify the viewport**. Benefits for using this pattern include **reuse of `shapes_changed`**. Possible risks include **a previous model remaining visible after reset**.
  - To mitigate **stale geometry**, we implemented **an empty-scene emission in `DisplayModel.reset`**.
- The system architecture diagram consists of the following major components: **presentation, application state, domain services, libraries and local storage**. This structure has low coupling because **the overlay uses the existing display path**. This structure has high cohesion because **reference rendering stays in the viewport**. This design is scalable because **the overlay stays outside export geometry**.

  **[System architecture](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/central-axis-display/docs/architecture/diagrams/system-architecture.svg): diagram update deferred at author request.**
- The system uses **synchronous processing** because **Qt updates the scene on its UI thread**. This method is done by **emitting `shapes_changed([], False)` during reset**. Benefits for using this approach include **immediate scene clearing**. Possible risks include **native rendering requiring a display**.
  - To mitigate **missing native-render coverage**, we implemented **separate offscreen tests and native Ex1/Ex2 regression checks**.
- The system adopts a **stateful** approach to state management because **visibility should survive redraws**. This method is done by **a checkable button and the current axis length**. Benefits for using this approach include **preserving the user's visibility choice**. Possible risks include **showing a reference in an empty scene**.
  - To mitigate **an empty-scene reference**, we implemented **length validation and reset clearing**.
- The Level 0 DFD consists of the following major components: **physicist, treatment planning system, brachify and printer/CAD**. **This overlay changes only the on-screen reference**.

  **[DFD level 0](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/central-axis-display/docs/architecture/diagrams/existing-framework/dfd-0.svg), unchanged.**
- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem and Export**. **A loaded cylinder supplies the reference length**. **Missing or invalid lengths produce no line and disable the toggle**.

  **[DFD level 1](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/central-axis-display/docs/architecture/diagrams/existing-framework/dfd-1.svg), unchanged.**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **central-axis request → `test_central_axis.py`**.
- Not applicable: **alternative solutions (not evaluated), database (none added), backend API (none added), test coverage (no percentage measured)**.

#### Frontend

- The frontend uses **local widget state and cylinder length** received from the backend because **the reference follows the current model**. Benefits for using this pattern include **camera-preserving toggles**. Possible risks include **the overlay intercepting channel selection**.
  - To mitigate **selection interference**, we implemented **`Context.Deactivate(axis)` and checked that it has no active selection modes**.
- The frontend is designed using **PySide6 and OpenCASCADE** with design components for **the toggle and reference line**. Therefore, changing the design of **the viewport toggle** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **line geometry and button styling are separate**.
- The frontend adopts accessibility principle **visible control state**. The aspects that demonstrate this principle in the system include **a text-labelled, checkable button with distinct enabled, disabled and checked appearances; native capture inspected locally**.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **central-axis toggle → availability/preference test and native Ex1/Ex2 checks**.
- Not applicable: **restricted pages (no authentication), usability evaluation (no formal study), test coverage (no percentage measured)**.

#### Review and design

- When I reviewed the **scene reset path** for this functionality, I noticed **clearing the model dictionaries did not notify the viewport**. Therefore, I did **emit an empty scene and add a signal regression test**.
- The PR does not contain any temporary workaround because **the reference is an independent display presentation, not an export solid**.
- The PR only contains small functions that are **4–21 lines for new axis/reset helpers; the modified viewport constructor is 39 lines and update_display is 27 lines** long.
- I did **anti-slop review against origin/main, with no findings, and inspected the diff** to check for unnecessary complexity and duplicated logic.
- This work is written in **viewport.py and display_model.py** because **they own rendering and scene-reset notification**.
- This work belongs in **the existing display path used by Cylinder, Channels and Export** in the DFD because **the line is a visual reference only**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **axis endpoints, toggle preference and reset notification** passed.
- I wrote tests to cover abnormal situations involving **None, zero, negative, NaN and infinite lengths** and they passed.
- I checked that these negative cases involving **a deliberately doubled endpoint margin** failed as expected.
- When I reviewed the **endpoint regression test**, I noticed **its value depends on catching incorrect geometry**. Therefore, I did **double the margin temporarily, observe the assertion fail, restore the code and rerun all eight axis cases successfully**.
- Among these tests, **six axis-geometry cases** are unit tests and **two real widget/signal cases** are integration tests.
- These tests are included in the directory **tests/views/**.
- This new test PR did not break anything else in the system because **77 tests passed; native Ex1 and Ex2 checks verified visibility, non-selection, camera-preserving toggles, Export redraw and reset; local screenshots were inspected, but no screenshots are committed**.

### For PR #**81**

- As part of requirement **FR-SV-06 (frontend viewport navigation), extended by the requested coordinate grid**, the user needs to do **load a model, inspect its millimetre coordinates, and toggle the grid independently of the central axis**.
- Therefore, I implemented code so that **clinicians can display a labelled outer-wall grid without adding reference geometry to exports**.

#### Frontend

- The frontend uses **viewport-local grid definitions and native presentations rebuilt from scene bounds** received from the backend because **labels must follow the displayed geometry**. Benefits for using this pattern include **keeping rendering decorations out of export models**. Possible risks include **stale overlays after reset**.
  - To mitigate **stale overlays**, we implemented **presentation cleanup and empty-scene availability handling**.
- The frontend is designed using **PySide6 and OpenCASCADE** with design components for **QToolButton controls and AIS text/line presentations**. Therefore, changing the design of **grid_text_label** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **GridLabel stores text and position separately from native styling**.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **requested grid extension to FR-SV-06 → tests/views/test_bounding_grid.py in this PR; this does not claim completion of the entire requirement**.
- Not applicable: **restricted pages (no authentication), usability evaluation (no formal study), accessibility (no formal audit), test coverage (no percentage measured)**.

#### Review and design

- When I reviewed the **native grid-label construction** for this functionality, I noticed **passing a wrapped C++ string caused a native Standard_NullObject abort**. Therefore, I did **pass Python text and add a real AIS label regression**.
- The PR does not contain any temporary workaround because **the grid uses the existing viewport presentation lifecycle**.
- This work is written in **src/windows/views/viewport.py** because **reference decorations belong to the renderer**.
- This work belongs in **the existing 3D visualization process** in the DFD because **it presents scene coordinates without changing DICOM or export data**.
- Not applicable: **function length (existing viewport methods exceed a small-function claim), code quality checklist (intentional fixed styling constants prevent the blanket no-hardcoded-values assertion)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **rounded ticks, outer-wall lines, native text labels and overlay controls (9 cases)** passed.
- I wrote tests to cover abnormal situations involving **degenerate and large bounds, NaN, infinity and reversed bounds** and they passed.
- I checked that these negative cases involving **deliberately changing outward rounding and removing the empty-scene signal** failed as expected.
- Among these tests, **grid tick and reference-grid calculations** are unit tests and **real Qt controls, the reset signal and native AIS labels** are integration tests.
- These tests are included in the directory **tests/views/test_bounding_grid.py**.
- This new test PR did not break anything else in the system because **141 tests passed with isolated user directories; native macOS Ex1/Ex2 checks confirmed independent toggles, unchanged camera on toggle, nonselectable decorations, Export redraw and reset**.
- Not applicable: **generated-test review (no separate test-review defect found)**.

### For PR #**82**

- As part of requirement **the course's weekly Part A receipts**, the user needs to do **review Gilles's week 6 evidence for PRs #78, #79 and #81 together**.
- Therefore, I implemented code so that **the deferred receipts are recorded in one weekly log without changing application code**.

#### Review and design

- When I reviewed the **week 6 log** for this functionality, I did not find any problems with it because **each feature section was compared exactly with its source PR's Part A**.
- I did **check section uniqueness, source equality and git diff --check** to check for duplicated or stale receipt text.
- This work is written in **docs/logs/gilles/week-6.md** because **the repository stores each student's weekly receipts there**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **exact comparison of all three feature receipts with their source PR descriptions** passed.
- This new test PR did not break anything else in the system because **the diff changes only the week 6 log; the architecture check and 132 pytest cases passed on the branch with isolated HOME/USERPROFILE and offscreen Qt**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no code, the checks are shell commands)**.
