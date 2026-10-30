# Week 8, Gilles

_Individual log. One section per PR merged this week, each a copy of that PR’s Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**180**

- As part of requirement **FR-SV-06 (frontend camera controls), issue #160**, the user needs to do **scroll sideways to roll the view clockwise/counterclockwise and vertically to zoom**.
- Therefore, I implemented/generated code so that **the viewport routes the dominant scroll axis to camera twist or proportional zoom**.

#### Frontend

- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-SV-06, side-scroll roll only → `test_scroll_routes_dominant_axis_without_combining_actions` (5 new cases); existing pan, drag and zoom checks remain**.
- Not applicable: **data caching, restricted pages, design components (unchanged), usability evaluation, accessibility, test coverage (not measured)**.

#### Review and design

- When I reviewed the **side-scroll camera handler** for this functionality, I noticed **orbit changed the viewing direction instead of turning the view like a clock face**. Therefore, I did **replace it with `V3d_View.SetTwist`, removing the side-scroll orbit path**.
- The PR does not contain any temporary workaround because **roll uses the existing native camera API**.
- The PR only contains small functions that are **7 lines for the added `wheel_camera_motion` helper and 10 lines for the updated `wheelEvent` handler** long.
- This work is written in **`src/windows/views/viewport.py`** because **that module owns camera input and native viewer calls**.
- This work belongs in **the existing viewport presentation in the DFD** because **only camera orientation changes; geometry, models and export flows are unchanged**.
- Not applicable: **code quality checklist (the explicit 10-degree sensitivity is a documented fixed control setting, so no blanket claim of no hardcoded values), teammate review (none requested)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_scroll_routes_dominant_axis_without_combining_actions`, including opposite roll directions and angle-only input (5 new cases; 11 camera cases total)** passed.
- I wrote tests to cover abnormal situations involving **zero movement and diagonal input selecting only one action** and they passed.
- I checked that these negative cases involving **reversing the roll sign, which produced 3 failures before restoring the implementation** failed as expected.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **the isolated-home pytest run passed all 323 tests in 308.44 seconds; lint and architecture checks passed; [author: attach a screenshot showing the 11 camera cases and 323-test suite result, plus a native before/after view demonstrating clockwise/counterclockwise roll]. Native verification remains pending after desktop automation timed out**.
- Not applicable: **generated-test review (no additional defect found), unit and integration tests (new cases test pure routing; native camera integration remains unverified)**.

