# Gilles — Week 9

## Part A

### Shared by every PR in this stack

- Scope: **issue #161, Gilles week 9; approximate organ intersections only. BODY, targets, needle–needle detection and distance measurement are excluded.**
- Checks: **isolated user files, focused tests for each layer, full-stack regression, architecture build/check and anti-slop. Native evidence uses Ex1 plus synthetic anatomy, not clinical validation.**
- Baseline: **the two Structures-highlight failures reproduce on main `6fa56b75`; #228 fixes them separately. The user authorized publishing with these failures. No tests are skipped or weakened.**
- Split: **dependency-ordered code and companion documentation PRs, with smaller-target exceptions authorized. Each own diff remains below 10 files and 500 changed lines. Screenshots are shared from the final documentation companion.**
- Not applicable: **database, network API, authentication, coverage percentage, formal usability evaluation (none introduced or measured).**

### For PR #**222** (1 of 6, on main)

- As part of requirement **FR-SV-07 / FR-SV-08 intersection warnings; issue #161**, the user needs to **identify possible needle contact with organs while editing a plan**.
- Therefore, I implemented/generated code so that **validate closed, consistently wound meshes and check complete needle paths**.

#### Backend and frontend

- The system uses **domain geometry, model-owned state and view-owned presentation** because **warnings must not modify printable geometry**. The worker receives immutable paths; revision checks refuse stale results. Approximate reconstruction and sampling remain limitations.
- Traceability: **the focused tests below exercise the intersection-warning requirement; native rendering evidence supplements offscreen widget tests. Distance measurement is not implemented.**
- Not applicable: **database, backend API, security roles, usability evaluation, coverage percentage (none added or measured)**.

#### Review and design

- When I reviewed **the geometry changes against the requested feedback**, I checked **geometry rejection and full-path coverage**.
- Code quality checklist: **see Shared; no new blocking anti-slop findings, no module mocking or export changes**.
- This work is written in **src/classes/mesh/needle_collisions.py and tests/mesh/test_needle_collisions.py** because **that layer owns this behaviour or documentation**.
- The PR does not contain a temporary workaround; **warnings use the existing anatomy cache and a separate collision state, and stay outside Export**.
- This work belongs in **Structures preview/checks** in the DFD.

#### Testing receipts

- Happy path: **geometry rejection and full-path coverage; 22 new cases in this layer**.
- Regression: **see the recorded layer/full-stack checks below; baseline failures are retained explicitly**.
- Negative cases: **red-before-green review tests and deliberate mutation checks are recorded with the update evidence**. Tests use real geometry/models/widgets with isolated files.
- Tests live in **tests/mesh/** or **tests/views/**; unit geometry and integrated model/widget coverage are counted separately.

### For PR #**pending** (2 of 6, on #222)

- As part of requirement **FR-SV-07 / FR-SV-08 intersection warnings; issue #161**, the user needs to **identify possible needle contact with organs while editing a plan**.
- Therefore, I implemented/generated code so that **request registered organ meshes independently of display visibility**.

#### Backend and frontend

- The system uses **domain geometry, model-owned state and view-owned presentation** because **warnings must not modify printable geometry**. The worker receives immutable paths; revision checks refuse stale results. Approximate reconstruction and sampling remain limitations.
- Traceability: **the focused tests below exercise the intersection-warning requirement; native rendering evidence supplements offscreen widget tests. Distance measurement is not implemented.**
- Not applicable: **database, backend API, security roles, usability evaluation, coverage percentage (none added or measured)**.

#### Review and design

- When I reviewed **the organ inputs changes against the requested feedback**, I checked **hidden Outlines organ requests and mismatched-frame refusal**.
- Code quality checklist: **see Shared; no new blocking anti-slop findings, no module mocking or export changes**.
- This work is written in **structures_model.py and tests/views/test_organ_collision_inputs.py** because **that layer owns this behaviour or documentation**.
- The PR does not contain a temporary workaround; **warnings use the existing anatomy cache and a separate collision state, and stay outside Export**.
- This work belongs in **Structures preview/checks** in the DFD.

#### Testing receipts

- Happy path: **hidden Outlines organ requests and mismatched-frame refusal; 3 new cases in this layer**.
- Regression: **see the recorded layer/full-stack checks below; baseline failures are retained explicitly**.
- Negative cases: **red-before-green review tests and deliberate mutation checks are recorded with the update evidence**. Tests use real geometry/models/widgets with isolated files.
- Tests live in **tests/mesh/** or **tests/views/**; unit geometry and integrated model/widget coverage are counted separately.

### For PR #**223** (3 of 6, on #pending)

- As part of requirement **FR-SV-07 / FR-SV-08 intersection warnings; issue #161**, the user needs to **identify possible needle contact with organs while editing a plan**.
- Therefore, I implemented/generated code so that **preserve warnings through display changes and reject stale or failed geometry checks**.

#### Backend and frontend

- The system uses **domain geometry, model-owned state and view-owned presentation** because **warnings must not modify printable geometry**. The worker receives immutable paths; revision checks refuse stale results. Approximate reconstruction and sampling remain limitations.
- Traceability: **the focused tests below exercise the intersection-warning requirement; native rendering evidence supplements offscreen widget tests. Distance measurement is not implemented.**
- Not applicable: **database, backend API, security roles, usability evaluation, coverage percentage (none added or measured)**.

#### Review and design

- When I reviewed **the background state changes against the requested feedback**, I checked **display-only stability, failure status, stale revisions, cache reuse and generated shafts**.
- Code quality checklist: **see Shared; no new blocking anti-slop findings, no module mocking or export changes**.
- This work is written in **collision_model.py, MainWindow and tests/views/test_collision_model.py** because **that layer owns this behaviour or documentation**.
- The PR does not contain a temporary workaround; **warnings use the existing anatomy cache and a separate collision state, and stay outside Export**.
- This work belongs in **Structures preview/checks** in the DFD.

#### Testing receipts

- Happy path: **display-only stability, failure status, stale revisions, cache reuse and generated shafts; 9 new cases in this layer**.
- Regression: **see the recorded layer/full-stack checks below; baseline failures are retained explicitly**.
- Negative cases: **red-before-green review tests and deliberate mutation checks are recorded with the update evidence**. Tests use real geometry/models/widgets with isolated files.
- Tests live in **tests/mesh/** or **tests/views/**; unit geometry and integrated model/widget coverage are counted separately.

### For PR #**224** (4 of 6, on #223)

- As part of requirement **FR-SV-07 / FR-SV-08 intersection warnings; issue #161**, the user needs to **identify possible needle contact with organs while editing a plan**.
- Therefore, I implemented/generated code so that **identify affected needles through accessible warnings, named toasts and red overlays**.

#### Backend and frontend

- The system uses **domain geometry, model-owned state and view-owned presentation** because **warnings must not modify printable geometry**. The worker receives immutable paths; revision checks refuse stale results. Approximate reconstruction and sampling remain limitations.
- Traceability: **the focused tests below exercise the intersection-warning requirement; native rendering evidence supplements offscreen widget tests. Distance measurement is not implemented.**
- Not applicable: **database, backend API, security roles, usability evaluation, coverage percentage (none added or measured)**.

#### Review and design

- When I reviewed **the warning UI changes against the requested feedback**, I checked **warning click/toggle, no eligible organs, font scaling and red actor properties**.
- Code quality checklist: **see Shared; no new blocking anti-slop findings, no module mocking or export changes**.
- This work is written in **structures_view.py, viewport.py and tests/views/test_organ_collisions.py** because **that layer owns this behaviour or documentation**.
- The PR does not contain a temporary workaround; **warnings use the existing anatomy cache and a separate collision state, and stay outside Export**.
- This work belongs in **Structures preview/checks** in the DFD.

#### Testing receipts

- Happy path: **warning click/toggle, no eligible organs, font scaling and red actor properties; 6 new cases in this layer**.
- Regression: **see the recorded layer/full-stack checks below; baseline failures are retained explicitly**.
- Negative cases: **red-before-green review tests and deliberate mutation checks are recorded with the update evidence**. Tests use real geometry/models/widgets with isolated files.
- Tests live in **tests/mesh/** or **tests/views/**; unit geometry and integrated model/widget coverage are counted separately.

### For PR #**225** (5 of 6, on #224)

- As part of requirement **FR-SV-07 / FR-SV-08 intersection warnings; issue #161**, the user needs to **identify possible needle contact with organs while editing a plan**.
- Therefore, I updated the documentation so that **document the worker, signal and display-only data flow**.

#### Review and design

- When I reviewed **the architecture changes against the requested feedback**, I checked **diagram source hashes, module coverage and viewer links**.
- Code quality checklist: **see Shared; no new blocking anti-slop findings, no module mocking or export changes**.
- This work is written in **docs/architecture/ source diagrams and generated artifacts** because **that layer owns this behaviour or documentation**.
- Not applicable: **temporary workaround, function length, DFD process (no application code changed)**.

#### Testing receipts

- Happy path: **diagram source hashes, module coverage and viewer links; 0 new cases in this layer**.
- Regression: **see the recorded layer/full-stack checks below; baseline failures are retained explicitly**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit/integration tests, test directory (documentation checks only)**.
