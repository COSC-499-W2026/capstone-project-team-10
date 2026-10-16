# Week 6, Ahab

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**74**

- As part of requirement **the course's Part A receipts, which ask for a screenshot as proof of
  each regression run**, the user needs to do **open #60, #61, #62 and #63 and see the test run
  and the running app behind each receipt**.
- Therefore, I implemented/generated code so that **graders see a `python -m pytest` run on each
  PR's own branch, and brachify on macOS for #60, #62 and #63**.

#### Review and design

- When I reviewed the **first captures** for this functionality, I noticed **3D-engine messages
  pushed the pytest result off screen, and one capture took the wrong window**. Therefore, I did
  **filter those messages in the shown command, and capture brachify by its window number**.
- I did **open each image, and `git diff --name-only main...HEAD` (seven PNGs and this log)** to
  ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/logs/ahab/screenshots/week-6/`** because **the log README keeps
  screenshots by student and week**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **each image showing
  its PR, branch, commit and pass count (65 to 99 passed)** passed.
- This new test PR did not break anything else in the system because **no file outside
  `docs/logs/` changed (`git diff --name-only`), and `session-start.sh` exits 0**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration
  tests, test directory (no code, the checks are shell commands)**.
