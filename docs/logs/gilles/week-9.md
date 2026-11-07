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
