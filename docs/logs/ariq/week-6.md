# Week 6, Ariq

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**31**

- As part of requirement **the course's weekly individual log, where week 5 lost marks for "excessive documentation checklists and repeated sections marked N/A"**, the user needs to do **run `/make-pr` and get a short Part A, a PR checked against the course size limits and a clear request for any missing screenshot, on a branch named by its type**.
- Therefore, I implemented/generated code so that **Team 10 students get one Not applicable line per subsection, a short Part A for documentation PRs, a size check discussed with the user, an Action needed notice for screenshots, and a `<type>/<what-it-is-about>` branch name rule, in `docs/workflows/make-pr.md` and `commit.md`**.

#### Review and design

- When I reviewed the **generated `make-pr.md` against my week 5 log**, I noticed **it still said "Keep every receipt", which gave that log 23 separate N/A lines**. Therefore, I did **replace it with one Not applicable line per subsection and a table naming each template receipt**.
- When I reviewed the **generated pointers**, I noticed **`pull_request_template.md` and `docs/logs/README.md` still said to mark each receipt N/A**. Therefore, I did **point both at the Not applicable line**.
- When I reviewed the **generated branch for PR #30**, I noticed **its name `make-pr-log-rules` had no type, unlike `fix/channels-list-selection`**. Therefore, I did **add the branch name rule and a `/make-pr` check, and reopen #30 from `docs/make-pr-log-rules`**.
- I did **a grep for "Keep every receipt" and "mark one that" (0 matches) and a check that the 8 section links in `make-pr.md` resolve** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/workflows/make-pr.md`** because **it is the canonical PR procedure that `/make-pr` points to**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **this Part A, written under the new rules (two Not applicable lines, no `— N/A` receipt)** passed.
- This new test PR did not break anything else in the system because **only markdown changed (`git diff --name-only main...HEAD`), `python -m pytest` (63 passed), `session-start.sh` and `build.py --check` (exit 0), and the `python -m pytest` run below**.

  ![1, python -m pytest on docs/make-pr-log-rules, 63 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/66c4f0c246e272a7d913ff53f3be0df55c5eeebf/docs/logs/ariq/screenshots/week-6/pr-31-1-pytest-run.png)

- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no code, the checks are shell commands)**.

### For PR #**33**

- As part of requirement **the course's regression receipt, which asks for a "screenshot as proof" and was left as a placeholder in test PR #20**, the user needs to do **open this PR or my week 6 log and see the `python -m pytest` run behind #20's "24 passed"**.
- Therefore, I implemented/generated code so that **the grader gets a screenshot of `python -m pytest` at #20's head commit `24957d2`, in `docs/logs/ariq/screenshots/week-6/`**.

#### Review and design

- When I reviewed the **generated screenshot** for this functionality, I did not find any problems with it because **it shows commit `24957d2`, `collected 24 items` and `24 passed`, the figures in #20's receipt**.
- I did **a check that the image link returns HTTP 200 and that `git diff --name-only main...HEAD` lists only this log and the image** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/logs/ariq/week-6.md`** because **it is my log for the week the screenshot was added, with the image beside it in `screenshots/week-6/`**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`python -m pytest` at `24957d2` (24 passed), in the screenshot below** passed.

  ![1, python -m pytest at 24957d2, 24 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/e74d4ce4147b7443e419ca3a2bf13a93b2bcdb5d/docs/logs/ariq/screenshots/week-6/pr-33-1-pytest-24-passed.png)
- This new test PR did not break anything else in the system because **only this log and a PNG changed (`git diff --name-only main...HEAD`), and `python -m pytest` (63 passed), `session-start.sh` and `build.py --check` (exit 0)**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no code, the checks are shell commands)**.
