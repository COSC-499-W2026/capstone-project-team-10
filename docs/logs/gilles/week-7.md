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
