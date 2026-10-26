# Week 7, Gilles

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**133**

- As part of requirement **FR-SV-01/02, contour preview and registration**, the user needs to do **see supplied anatomy contours aligned with the probe**.
- Therefore, I implemented/generated code so that **a validated patient-to-probe transform produces separate closed wire loops for display**.

#### Backend

- The system uses **a mesh-domain service** because **geometry can be checked separately from widgets and printable shapes**. Benefits include **literal-coordinate tests**; risks include **misregistration**. To mitigate that risk, we implemented **frame and nonzero-axis validation**.
- The system uses **synchronous data processing** through **coordinate transformation and OpenCASCADE wire construction**. It adopts a **stateless** approach because **callers own the contour inputs and alignment**.
- Traceability: **FR-SV-02 → test_contour_transform_keeps_tip_alignment_and_closed_boundary; FR-SV-01 contour subset → test_closed_outline_has_all_edges_and_no_filled_faces**.
- Not applicable: **database, backend API (desktop geometry), test coverage (percentage not measured)**. Architecture and Level 0/1 DFD updates remain deferred.

#### Review and design

- When I reviewed **#121’s size**, I noticed **geometry and presentation could be reviewed separately**. Therefore, I did **extract the geometry implementation and its tests without changing their behavior**.
- This work is written in **src/classes/mesh/structure_contours.py** because **it owns patient-to-probe contour registration**, and belongs in **anatomy preview** in the DFD.
- Not applicable: **temporary workaround (none introduced), function length (no new length claim), code quality checklist (no blanket claim)**.

#### Testing receipts

- The happy path involving **all five contour cases** passed on this branch. They check **literal transformed coordinates, closed edges and absence of filled faces**.
- Abnormal cases cover **missing frame, zero-length/reversed-Z axes and open-contour rejection**. The original **deliberate Z-offset-sign mutation** failed its coordinate assertion and was restored.
- These are **unit tests in tests/mesh/test_structure_contours.py**. No widget or native-viewport change is made by this PR.
- Regression: **257 passed, 1 failed in 288.40 seconds**. Architecture coverage is the intentionally deferred failure.
- Not applicable: **generated-test review (no additional defect found), integration tests (service only)**.

Merge order: #116 → #117 → #133 → #121 → #122 → #123 → #124 → #134 → #125. Retarget each remaining PR after its parent merges; these are dependency PRs, not independent changes.

### For PR #**139**

- As part of requirement **FR-SV-01/02 documentation**, the user needs to do **find the registered contour service and its tests**.
- Therefore, I implemented/generated code so that **the documentation describes the implemented anatomy layer**.

#### Review and design

- When I reviewed the **documentation against the feature branch** for this functionality, I noticed **the architecture check rejected structure_contours**. Therefore, I did **name the module and document its transform, guards and tests**.
- This work is written in **system-architecture.mmd, project docs, tests/README.md and week-7.md** because **these files own the architecture and implementation reference**.
- I did **a base-relative file-list and diff check confirming documentation-only changes** to ensure that my feature contribution does not contain any of the following: **hardcoded values, duplicate or dead code, unnecessary calls, excessive conditionals, deep nesting, high cyclomatic complexity or unrelated implementation responsibilities (no executable code added)**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`python docs/architecture/build.py --check` (exit 0)** passed.
- This new test PR did not break anything else in the system because **the full isolated suite passed 258 tests on macOS; application code is unchanged**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no new tests)**.

### For PR #**140**

- As part of requirement **FR-SV-01/02 documentation**, the user needs to do **locate the background worker and its libraries**.
- Therefore, I implemented/generated code so that **the documentation describes the implemented anatomy layer**.

#### Review and design

- When I reviewed the **documentation against the feature branch** for this functionality, I noticed **the architecture omitted StructuresModel and both anatomy services**. Therefore, I did **map the worker, cache, pending state and unconnected opacity signal**.
- This work is written in **system-architecture.mmd and its generated SVG/viewer** because **these files own the architecture and implementation reference**.
- I did **a base-relative file-list and diff check confirming documentation-only changes** to ensure that my feature contribution does not contain any of the following: **hardcoded values, duplicate or dead code, unnecessary calls, excessive conditionals, deep nesting, high cyclomatic complexity or unrelated implementation responsibilities (no executable code added)**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`python docs/architecture/build.py --check` (exit 0)** passed.
- This new test PR did not break anything else in the system because **the full isolated suite passed 287 tests on macOS; application code is unchanged**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no new tests)**.

### For PR #**141**

- As part of requirement **FR-SV-01/02 documentation**, the user needs to do **trace anatomy import, preview and background result delivery**.
- Therefore, I implemented/generated code so that **the documentation describes the implemented anatomy layer**.

#### Review and design

- When I reviewed the **documentation against the feature branch** for this functionality, I noticed **the UML and DFDs omitted the anatomy path**. Therefore, I did **draw frame-checked preview state and generation-tagged worker results**.
- This work is written in **existing-framework diagrams, architecture README and generated viewer** because **these files own the architecture and implementation reference**.
- I did **a base-relative file-list and diff check confirming documentation-only changes** to ensure that my feature contribution does not contain any of the following: **hardcoded values, duplicate or dead code, unnecessary calls, excessive conditionals, deep nesting, high cyclomatic complexity or unrelated implementation responsibilities (no executable code added)**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`python docs/architecture/build.py --check` (exit 0)** passed.
- This new test PR did not break anything else in the system because **the unchanged #134 code passed 287 tests on the parent documentation branch; diagram checks pass here; application code is unchanged**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no new tests)**.

### For PR #**134**

- As part of requirement **FR-SV-01/04, anatomy preview and reconstruction**, the user needs to do **retain responsive controls while an organ preview is reconstructed**.
- Therefore, I implemented/generated code so that **the model schedules reconstruction and tracks geometry, failure and opacity state independently**.

#### Backend

- The system uses **a Qt state model over mesh services** because **preview anatomy must stay separate from printable geometry**. Benefits include **independent model tests**; risks include **stale geometry after import or length changes**. To mitigate those risks, we implemented **generation-tagged results and alignment checks**.
- The system uses **asynchronous data processing** through **one QThreadPool worker producing private meshes and delivering results to the model’s GUI-thread slot**. Benefits include **bounded concurrent reconstruction**; late-result risks are covered by **reset and reused-ROI regressions**.
- The system adopts a **stateful** approach with **cached patient meshes, lazy outlines, per-ROI opacity and separate surface/outline errors**. An **unusable outline cannot disable a valid surface**, covered by its regression test.
- Traceability: **FR-SV-01/04 preview support → surface alignment, large EXTERNAL, opacity, mode switching and late-result tests**. Clinical volume accuracy remains unverified.
- Not applicable: **database, backend API (desktop app), test coverage (percentage not measured)**. Architecture and Level 0/1 DFD receipts remain deferred.

#### Frontend

- The frontend uses **model presentation and status values** to keep the **existing outline-only checkboxes and viewport** compatible with optional geometry. Benefits include **unchecked failed outlines and no AIS_Shape construction from None**.
- The frontend is designed using **existing PySide6 list rows and OpenCASCADE wire actors**. New mode/opacity controls and native surface actors belong to **#125**.
- Not applicable: **restricted pages (none), usability evaluation and accessibility (not audited), test coverage (percentage not measured), separate frontend traceability matrix (model integration tests above)**.

#### Review and design

- When I reviewed **the #125 feedback**, I noticed **synchronous reconstruction, stale-worker risks and ROI-wide failure state**. Therefore, I did **move reconstruction to a worker and isolate result generations and representation errors**.
- This work is written in **StructuresModel with minimal outline-view adapters** because **state and rendering have separate owners**. It belongs in **anatomy preview** in the DFD and does not change export inputs.
- Not applicable: **temporary workaround (Outlines remains the supported default until #125), function length (no blanket claim), code quality checklist (no blanket claim)**.

#### Testing receipts

- **21 targeted model/widget cases passed** on this intermediate branch, including **large BODY, mode cache reuse, alignment and independent ROI opacity**.
- Abnormal cases cover **failed outlines, late results after reset/new import and length changes during reconstruction**.
- I wrote tests to cover abnormal situations involving **IndexError, TypeError and MemoryError at the reconstruction boundary, asserting error delivery and cleared pending state**, and they passed.
- Deliberate mutations that **restored geometry redraws for opacity, poisoned the entire ROI on outline failure, omitted generation checks or accepted stale alignment** were caught before extraction and restored.
- These are **model/widget integration tests in tests/views/test_structure_display.py**, using real Qt event delivery and reconstruction. They do not initialise the native viewport.
- Regression: **286 passed, 1 failed in 299.95 seconds**. Native Ex1/Ex2 surface checks were performed on the final #125 stack before splitting, not claimed for this intermediate outline-only UI.
- Not applicable: **generated-test review (no additional defect found)**.

Merge order: #116 → #117 → #133 → #121 → #122 → #123 → #124 → #134 → #125. Retarget each remaining PR after its parent merges; these are dependency PRs, not independent changes.

### For PR #**142**

- As part of requirement **FR-SV-01/02 documentation**, the user needs to do **understand anatomy setup, reconstruction limits and asynchronous state**.
- Therefore, I implemented/generated code so that **the documentation describes the implemented anatomy layer**.

#### Review and design

- When I reviewed the **documentation against the feature branch** for this functionality, I noticed **the reference still described an empty Structures page and omitted the surface dependencies**. Therefore, I did **document the implemented outline UI separately from the later surface controls**.
- This work is written in **project reference, init-guide notes, design/test indexes and Gilles week 7 log** because **these files own the architecture and implementation reference**.
- I did **a base-relative file-list and diff check confirming documentation-only changes** to ensure that my feature contribution does not contain any of the following: **hardcoded values, duplicate or dead code, unnecessary calls, excessive conditionals, deep nesting, high cyclomatic complexity or unrelated implementation responsibilities (no executable code added)**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`python docs/architecture/build.py --check` (exit 0)** passed.
- This new test PR did not break anything else in the system because **the identical application/test tree passed 287 tests on the worker documentation branch; the flow update passed 15 architecture checks; application code is unchanged**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no new tests)**.

### For PR #**121**

- As part of requirement **FR-SV-01/02, contour preview and coordinate alignment**, the user needs to do **import a plan and show or hide its structure outlines alongside the probe**.
- Therefore, I implemented/generated code so that **the Structures list controls aligned, display-only DICOM contour outlines**.

#### Backend

- The system uses **domain geometry plus a QObject state model** because **alignment can be tested without a native viewport**. Benefits for using this pattern include **separating anatomy from printable ShapeModel geometry**. Possible risks include **misregistered anatomy**.
  - To mitigate **misregistration**, we implemented **probe-frame validation and synthetic Nucletron regressions; the literal-coordinate tests belong to #133**.
  - We considered alternative solutions such as **surface reconstruction, deferred because this change displays supplied contours only**.
- The system uses **synchronous data processing** because **the existing desktop application updates models through Qt signals**. This method is done by **building outlines on import or first visibility selection**. Benefits for using this approach include **deterministic updates**. Possible risks include **UI pauses for large contour sets**.
- The system adopts a **stateful** approach to state management because **visibility must survive viewport redraws**. This method is done by **StructuresModel retaining visible ROI identifiers and cached wire presentations**. Benefits for using this approach include **reusing hidden outlines**. Possible risks include **stale patient anatomy**.
  - To mitigate **stale anatomy**, we implemented **clearing on import/reset, exercised by the failed-import test**.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-SV-02 registration: test_nucletron_uses_embedded_probe_frame_not_colliding_rs_roi; FR-SV-01 contour-preview subset: test_structures_checkboxes_control_anatomy_and_failed_import_clears_it**.
- Not applicable: **database, backend API (local desktop app), test coverage (no coverage percentage measured)**.
- Architecture and Level 0/1 DFD receipts are **deferred to the week 7 documentation PR at the author's request**.

#### Frontend

- The frontend uses **StructuresModel visibility and outline cache** received from the backend because **the Structures list and viewport share the same ROI state**. Benefits for using this pattern include **consistent checkboxes and rendering**. Possible risks include **recursive widget updates**.
  - To mitigate **recursive updates**, we implemented **QSignalBlocker while refreshing the list**.
- The frontend is designed using **PySide6 and OpenCASCADE** with design components for **Structures checkboxes and viewport wire presentations**. Therefore, changing the design of **the structure-row renderer** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **ROI metadata remains in the model**.
- Not applicable: **restricted pages (no logins), usability evaluation and accessibility audit (none conducted), test coverage (no coverage percentage measured), separate frontend traceability matrix (tests mapped above)**.

#### Review and design

- When I reviewed **the PR feedback**, I noticed **an external ROI collision could authorize the wrong probe frame and empty scene updates cleared anatomy**. Therefore, I did **read the frame from the actual probe source and wire an explicit reset signal**.
- The PR does not contain any temporary workaround because **anatomy has a dedicated display-only state model**.
- This work is written in **classes/dicom, windows/models and windows/views** because **geometry, state and rendering have separate responsibilities**.
- This work belongs in **Structures and viewport preview** in the DFD because **it consumes decoded ROIs without changing export inputs**.
- Not applicable: **blanket code-quality claim (not asserted); anti-slop review passed with only the repository-exempt shape-name warning**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **probe-frame validation, visibility and cylinder-length alignment** passed.
- I wrote tests to cover abnormal situations such as **missing and mismatched embedded probe frame identifiers**.
- I checked that these negative cases **a mismatched ROI frame and failed subsequent import** are handled by **refusing preview and clearing previous anatomy**.
- Among these tests, **the real Structures-checkbox and model tests exercise widget/model integration**.
- These tests are included in the directory **tests/views**.
- Regression result: **12 targeted tests passed on this branch. Combined stack after the review fixes has 283 passed, 1 failed (architecture coverage intentionally deferred); final widget checks 4 passed**. Native Ex1/Ex2 runs on #125 verified non-selection, Export redraw and explicit reset; screenshots remain local for the separate documentation PR.
- Deliberately using the wrong probe frame or omitting the explicit reset signal failed the regression tests. Bundled samples contain no ORGAN/TUMOUR-classified ROIs; named-organ and Nucletron native rendering remain unverified.

Merge order: #116 → #117 → #133 → #121 → #122 → #123 → #124 → #134 → #125. Retarget each remaining PR after its parent merges; these are dependency PRs, not independent changes.

### For PR #**122**

- As part of requirement **backend FR-SV-04, structure reconstruction**, the user needs to do **install the numerical libraries used by the upcoming surface service**.
- Therefore, I implemented/generated code so that **the environment declares SciPy and scikit-image**.

#### Review and design

- When I reviewed the **dependency manifests**, I noticed **the added tifffile pin comes from defaults**. Therefore, I did **check conda-forge metadata before attempting a replacement; the channel migration remains unresolved**.
- This work is written in **environment.yml and spec-file.txt** because **they define the supported conda installations**.
- Not applicable: **temporary workaround, function length, code quality checklist, DFD process (dependency manifests only)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **macOS imports and reconstruction with SciPy 1.17.1 and scikit-image 0.26.0** passed.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (dependency-only change)**.
- Regression evidence: **the final stack has 283 passed, 1 failed (architecture coverage intentionally deferred); final widget checks 4 passed; Windows and Linux runtime were not tested**.

Merge order: #116 → #117 → #133 → #121 → #122 → #123 → #124 → #134 → #125. Retarget each remaining PR after its parent merges; these are dependency PRs, not independent changes.

### For PR #**123**

- As part of requirement **frontend FR-SV-01, registered anatomy display**, the user needs to do **see contours and reconstructed surfaces aligned with the same probe**.
- Therefore, I implemented/generated code so that **both preview paths can share patient-to-probe transformation without mesh-to-contour conversions**.

#### Backend

- The system uses **a shared mesh-domain transform** because **surfaces and contours must agree on registration**. Benefits for using this pattern include **one rotation and translation implementation**. Possible risks include **mutating cached patient vertices**.
  - To mitigate **source mutation**, we implemented **test_point_array_alignment_preserves_input_and_patient_registration**.
  - We considered alternative solutions such as **copying the transform into the surface builder, rejected to avoid divergent geometry**.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-SV-01 alignment support → test_point_array_alignment_preserves_input_and_patient_registration**.
- Not applicable: **database, backend API, state management (pure helper), test coverage (not measured), data processing (existing synchronous transform unchanged)**. Architecture and DFD updates remain deferred.

#### Review and design

- When I reviewed the **surface alignment flow**, I noticed **mesh vertices were converted through temporary Contour tuples**. Therefore, I did **extract a NumPy-array transform for the subsequent surface service**.
- The PR does not contain any temporary workaround because **transform_contour delegates to the shared implementation**.
- The PR only contains small functions that are **4 and 15 lines for the changed transform functions** long.
- This work is written in **src/classes/mesh/structure_contours.py** because **it already owns patient-to-probe registration**.
- This work belongs in **anatomy preview** in the DFD because **it transforms decoded patient coordinates for display**.
- Not applicable: **code quality checklist (no claim beyond the reviewed transform)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **all four contour tests on this intermediate branch** passed.
- I wrote tests to cover abnormal situations involving **input-coordinate mutation** and they passed.
- I checked that these negative cases involving **a deliberately reversed Z offset** failed as expected.
- Among these tests, **tests/mesh/test_structure_contours.py** are unit tests and integration tests are not required because **this change is a pure coordinate transform**.
- These tests are included in the directory **tests/mesh/**.
- Not applicable: **generated-test review (no additional defect found)**.
- Regression evidence: **final-stack native Ex1/Ex2 previews passed; full suite 283 passed, 1 failed (architecture coverage intentionally deferred); final widget checks 4 passed**.

Merge order: #116 → #117 → #133 → #121 → #122 → #123 → #124 → #134 → #125. Retarget each remaining PR after its parent merges; these are dependency PRs, not independent changes.

### For PR #**124**

- As part of requirement **backend FR-SV-04, structure reconstruction**, the user needs to do **inspect a surface reconstructed from closed axial contours**.
- Therefore, I implemented/generated code so that **the display layer can request a sampled mesh or receive a reason reconstruction is unavailable**.

#### Backend

- The system uses **a mesh-domain service** because **display meshes must remain separate from printable device geometry**. Benefits for using this pattern include **independent geometry tests**. Possible risks include **inventing anatomy across unsupported contours**.
  - To mitigate **unsupported reconstruction**, we implemented **validation for closed axial stacks, sufficient slices and excessive gaps**.
  - We considered alternative solutions such as **connecting arbitrary contour vertices, rejected because separate loops and holes must be retained**.
- The system uses **synchronous data processing** because **the caller requests one mesh at a time**. This method is done by **signed-distance sampling and marching cubes**. Benefits for using this approach include **deterministic results**. Possible risks include **memory growth**.
  - To mitigate **memory growth**, we implemented **a 32-million combined grid and intermediate-field sample limit**.
  - We considered alternative solutions such as **unbounded sampling, rejected for large BODY datasets**.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-SV-04 preview support → closed-mesh and unsupported-stack tests; clinical volume-accuracy acceptance remains unverified**.
- Not applicable: **database, backend API, state management (stateless service), test coverage (not measured)**. Architecture and DFD updates remain deferred.

#### Review and design

- When I reviewed the **sampling budget**, I noticed **intermediate slice fields also consume memory**. Therefore, I did **include both fields and volume samples in the cap**.
- The PR does not contain any temporary workaround because **unsupported stacks raise explicit errors rather than fabricating a mesh**.
- The PR only contains small functions that are **at most 27 lines in the new service** long.
- This work is written in **src/classes/mesh/structure_surfaces.py** because **reconstruction is independent of widgets**.
- This work belongs in **anatomy reconstruction** in the DFD because **decoded contours become display-only mesh vertices and triangles**.
- Not applicable: **code quality checklist (sampling thresholds are explicit policy constants)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **11 contour/surface tests on this intermediate branch** passed.
- I wrote tests to cover abnormal situations involving **single slices, large gaps, open contours and excessive intermediate-field memory** and they passed.
- I checked that these negative cases involving **a deliberate XOR-to-union mutation** failed as expected.
- Among these tests, **mesh geometry tests** are unit tests and integration tests are not required because **Qt/OCC display integration is in the next PR**.
- These tests are included in the directory **tests/mesh/**.
- Not applicable: **generated-test review (no additional defect found)**.
- Regression evidence: **final-stack suite 283 passed, 1 failed (architecture coverage intentionally deferred); final widget checks 4 passed; 02a organs and BODY reconstructed locally, using 2 mm sampling for BODY**.

Merge order: #116 → #117 → #133 → #121 → #122 → #123 → #124 → #134 → #125. Retarget each remaining PR after its parent merges; these are dependency PRs, not independent changes.

### For PR #**125**

- As part of requirement **FR-SV-01/04, anatomy display and reconstruction**, the user needs to do **inspect a surface beside the probe and control each organ’s visibility and opacity**.
- Therefore, I implemented/generated code so that **Structures controls native display-only surfaces and reports reconstruction failures visibly**.

#### Backend

- The system uses **the state model supplied by #134**, with **Surface selected as the default only once its UI and rendering are available**. Background reconstruction, generations and caches belong to that dependency.
- Traceability: **FR-SV-01 surface default → test_failed_surface_is_explained_in_visible_structure_row**.
- Not applicable: **database, backend API (desktop app), data processing and state management (implemented by dependency), test coverage (percentage not measured)**. Architecture and Level 0/1 DFD updates remain deferred.

#### Frontend

- The frontend uses **separate geometry and opacity signals** because **transparency should update existing actors**. Benefits include **actor and list-item reuse**. Failed-surface risks are mitigated by **visible row status and unchecked unavailable previews**.
- The frontend is designed using **PySide6 and OpenCASCADE**, with shared **structure-row rendering and triangulation presentation helpers**. ROI content stays in the model.
- Traceability: **FR-SV-01/04 preview support → real mode/opacity widget, failed-surface row and mesh-actor display tests**. Clinical volume accuracy remains unverified.
- Not applicable: **restricted pages (none), usability evaluation and accessibility (not audited), test coverage (percentage not measured)**.

#### Review and design

- When I reviewed **the PR feedback**, I noticed **shared-opacity redraws and failed surfaces hidden behind checked rows**. Therefore, I did **update per-ROI actors in place and show failure reasons directly in the list**.
- This work is written in **StructuresView, viewport and MainWindow**, with the **model’s default-mode change**, because **controls, rendering and signal wiring have separate owners**. It belongs in **anatomy preview** in the DFD and does not alter exports.
- Not applicable: **temporary workaround (no automatic fallback), function length (existing constructors exceed the target), code quality checklist (no blanket claim)**.

#### Testing receipts

- The happy path tests involving **real mode/opacity controls and explicit triangulation display mode/colour** passed. The abnormal **single-slice failure row** test verifies a visible reason, unchecked state and no contour fallback.
- These are **widget/native-actor integration tests in tests/views/test_structure_display.py**. The worker/model tests are owned by **#134**.
- Regression: **289 passed, 1 failed in 298.22 seconds**. The only failure is `tests/tooling/test_architecture_drift.py::test_the_real_system_architecture_names_every_module_in_src`, because diagrams remain deferred.
- Native Ex1/Ex2 runs before splitting verified **visible BODY surfaces, actor/list-item reuse during opacity changes, Surface/Outlines/Both, Export redraw, non-selection and reset**. The final production tree is byte-identical after splitting. Screenshots remain local for the separate documentation update. Windows packaging and native Nucletron rendering were not tested.
- Not applicable: **generated-test review (no additional defect found), separate new mutation receipt (worker and opacity mutation evidence recorded in #134)**.

Merge order: #116 → #117 → #133 → #121 → #122 → #123 → #124 → #134 → #125. Retarget each remaining PR after its parent merges; these are dependency PRs, not independent changes.

### For PR #**143**

- As part of requirement **FR-SV-01/04 documentation**, the user needs to do **find the surface controls and audit the five deferred feature receipts**.
- Therefore, I implemented/generated code so that **the documentation describes the implemented anatomy layer**.

#### Review and design

- When I reviewed the **documentation against the feature branch** for this functionality, I noticed **the architecture stopped at the worker API and week 7 lacked receipts for PRs 121–125**. Therefore, I did **map native surface actors and opacity delivery, and copy each original Part A verbatim**.
- This work is written in **system architecture source/SVG/viewer and Gilles week 7 log** because **these files own the architecture and implementation reference**.
- I did **a base-relative file-list and diff check confirming documentation-only changes** to ensure that my feature contribution does not contain any of the following: **hardcoded values, duplicate or dead code, unnecessary calls, excessive conditionals, deep nesting, high cyclomatic complexity or unrelated implementation responsibilities (no executable code added)**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`python docs/architecture/build.py --check` (exit 0)** passed.
- This new test PR did not break anything else in the system because **290 passed in 286.76s on the surface architecture branch (identical application/test tree); application code is unchanged**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no new tests)**.
