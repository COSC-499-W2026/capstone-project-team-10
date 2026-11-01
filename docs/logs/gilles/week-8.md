# Week 8, Gilles

_Individual log. One section per PR merged this week, each a copy of that PR’s Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**197**

- As part of requirement **#159, restore the grey viewport background**, the user needs to do **open Brachify and view the probe against the original grey background**.
- Therefore, I implemented/generated code so that **the viewport retains OpenCASCADE's default grey background**.

#### Frontend

- The frontend is designed using **PySide6 and OpenCASCADE** with design components for **the shared 3D viewport**. Therefore, changing the design of **the viewport background** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **background setup is independent of the displayed shapes**.
- Not applicable: **data caching, usability evaluation, accessibility evaluation, coverage measurement (none introduced or performed)**.

#### Review and design

- When I reviewed the **viewport initialization** for this functionality, I did not find any problems with it because **the two-line removal restores the initialization used before the grid change, and the native framebuffer shows grey**.
- The PR does not contain any temporary workaround because **it removes the dark override instead of adding another colour override**.
- The PR only contains small functions that are **5 lines long (`InitDriver`)**.
- I did **a diff review and anti-slop review with no findings** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/windows/views/viewport.py`** because **`InitDriver` initializes the native viewport**.
- This work belongs in **the existing display process** in the DFD because **only its background appearance changes**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **the native macOS viewport capture with Ex1, compared with the previous dark override (image 1)** passed.
- This new test PR did not break anything else in the system because **318 passed in 328.08s (0:05:28) (0 new tests; all inherited); architecture and session-start checks passed; image 1 includes the captured test output**.

  ![1, native viewport background comparison and captured pytest output](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/76ac6f54a0e30ffafbee4acb465322f5346e84c9/docs/logs/gilles/screenshots/week-8/pr-197-1-grey-background.png)
- Not applicable: **new unit/integration tests, abnormal and negative cases, generated-test review (a visual default restoration; existing tests were rerun)**.
