# Week 5, Ariq

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**17**

- As part of requirement **the course's weekly individual log, where week 4 took a mark from
  two logs for being "excessively long"**, the user needs to do **run `/make-pr` and get a Part
  A that is quick to audit, identical in the PR and in `docs/logs/<student>/week-<K>.md`**.
- Therefore, I implemented/generated code so that **Team 10 students get a "Keep Part A
  minimal" rule in `docs/workflows/make-pr.md`, restated in one phrase in the PR template,
  `docs/logs/README.md`, `AGENTS.md` and `.claude/`**.

#### Review and design

- When I reviewed the **generated `make-pr.md` against my week 4 log (5,250 words, 6 PRs) and
  Gilles's full-marks log (652 words, 1 PR)**, I noticed **it asked for each receipt "as well
  as the diff allows" and for a shell-check caveat in every testing receipt, which added
  sentences after the bold fill-ins**. Therefore, I did **add the rule (template sentences
  only, one claim and one piece of evidence per fill-in, one-clause N/A reasons) and ask for
  the caveat once**.
- When I reviewed the **generated pointers in `AGENTS.md` and `.claude/`**, I noticed **they
  still said "bold answers backed by evidence" with no length rule**. Therefore, I did **add
  "minimal" to each**.
- The PR does not contain any temporary workaround because **the rule lives once, in
  `make-pr.md`, and every other file links to it or restates it in one phrase**.
- The PR only contains small functions — **N/A**, no function changed.
- I did **a grep of the documentation set for the replaced wording (0 matches)** to ensure
  that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/workflows/make-pr.md`** because **it is the canonical PR
  procedure that `/make-pr` points to**.
- This work belongs in a process in the DFD — **N/A**, brachify's data flow is unchanged.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **this Part A,
  written under the rule (492 words, against about 870 per PR in my week 4 log)** passed.
- I wrote tests to cover abnormal situations — **N/A**, the PR has no code to exercise.
- I checked that these negative cases involving **a grep for "with bold answers backed" and
  "as well as the diff allows" (0 matches)** failed as expected.
- When I reviewed the generated tests — **N/A**, no tests were generated.
- Among these tests, unit and integration tests — **N/A**, the checks are shell commands, not
  tests in `tests/`.
- These tests are included in the directory — **N/A**, nothing was added to `tests/`.
- This new test PR did not break anything else in the system because **only markdown changed
  (`git diff --name-only main...HEAD`), and `python -m pytest` (20 passed),
  `session-start.sh` and `build.py --check` (exit 0) still pass**.
