# Week 4, Ariq

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**7**

- As part of requirement **the course's Weekly Expectations, which grade each merged PR through
  the Part A receipts in every student's weekly log**, the user needs to do **run `/make-pr` on
  a branch, fill in Part A from the diff, open the PR, and have the same Part A committed to
  `docs/logs/<student>/week-<K>.md`**.
- Therefore, I implemented/generated code so that **the four Team 10 students get a PR template
  that opens with Part A, with all 142 placeholders pre-bolded (`pull_request_template.md`),
  a `/make-pr` procedure that fills Part A with evidence on every PR, ticks N/A boxes, and copies
  Part A into their weekly log (`docs/workflows/make-pr.md`), and week 4 log files for each
  student and the team (`docs/logs/`). The instructor and TAs get one Part A per PR, identical in
  the PR description and in the log**.

#### Review and design

- When I reviewed the **generated `pull_request_template.md`** for this functionality, I
  noticed **it was going to carry Part B, the team log, which covers the whole team's week
  rather than one PR**. Therefore, I did **keep Part B out of PRs and put its template in
  `docs/logs/README.md`, for `docs/logs/team/week-<K>.md`**.
- When I reviewed the **generated `docs/workflows/make-pr.md`** for this functionality, I
  noticed **it pointed diagram placeholders at a `docs/architecture.md` that did not exist on
  `main`**. Therefore, I did **point them at `docs/architecture/diagrams/uml.mmd`, `dfd-0.mmd`
  and `dfd-1.mmd` once PR #4 merged, and link to `docs/architecture/README.md` for when to
  redraw instead of restating that rule**.
- When I reviewed the **generated `docs/logs/` layout** for this functionality, I noticed **the
  weekly log files fell under "every markdown file in `docs/`", so the documentation-set rule
  would require rewriting past logs to match later code**. Therefore, I did **exclude
  `docs/logs/<student>/week-<K>.md` and `docs/logs/team/week-<K>.md` from the set in
  `AGENTS.md`, `README.md`, `docs/README.md` and §9.0 of the project docs, keeping
  `docs/logs/README.md` in it**.
- When I reviewed the **generated description of this PR** for this functionality, I noticed
  **its N/A checkboxes were left unticked, which tells a reviewer those items are missing when
  they were checked, and its Part A was a single N/A line, which would leave this graded weekly
  log empty**. Therefore, I did **change the rules in `make-pr.md`, `pull_request_template.md`
  and `docs/logs/README.md` so an N/A box is ticked, a box stays blank only when it was not
  checked or waits on the author, and Part A is filled in on every PR, then refilled this PR's
  description and `docs/logs/ariq/week-4.md`**.
- The PR does not contain any temporary workaround because **the Change checklist, Review
  section and upstream footer are deleted rather than commented out, and every file that
  described them was updated in this PR. A grep of the documentation set for their wording
  returns 0 matches**.
- The PR only contains small functions — **N/A**, the PR adds no functions.
  `git diff --name-only origin/main...HEAD` lists only markdown files.
- By doing **a grep of the documentation set for every phrase that described the removed
  sections, and a read of each rule I added against the files that already stated it**, I
  found that my feature contribution contained **duplicate code, a copy in `make-pr.md` of the
  diagram redraw rule that `docs/architecture/README.md` owns, and dead code, a `make-pr.md`
  line telling agents to leave the removed Reviewer block unticked**. Therefore, I did
  **replace the copy with a link to `docs/architecture/README.md` and delete the line**.

  Now, I can confirm that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`pull_request_template.md`, `docs/workflows/make-pr.md` and
  `docs/logs/`** because **GitHub pre-fills the template on its web form and `/make-pr` appends
  it by hand, `make-pr.md` is the one tool-agnostic procedure that
  `.claude/commands/make-pr.md` points to, and `docs/logs/` already held the team and
  individual logs beside the other course documents**.
- This work belongs in a process in the DFD — **N/A**, the PR changes the team's PR process, not
  brachify. No process in `docs/architecture/diagrams/dfd-1.mmd` moves.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`sh .claude/hooks/session-start.sh` (exit 0, no `UNDOCUMENTED` or `STALE ROW` line),
  `python docs/architecture/build.py --check` (exit 0), and a script confirming that all 142
  Part A placeholders in `pull_request_template.md` are bold** passed. These are repository
  checks run from the shell, not tests in `tests/`.
- I wrote tests to cover abnormal situations — **N/A**, the PR has no code for a test to
  exercise.
- I checked that these negative cases involving **a grep of the documentation set for the
  removed wording ("Reviewer block", "signs off", "template requires", "## Change checklist",
  "leave the box unticked", "not logged")** failed as expected, with 0 matches.
- When I reviewed the generated tests — **N/A**, no tests were generated.
- Among these tests, unit and integration tests — **N/A**, none of the checks is a unit or
  integration test. They are shell checks on the repository.
- These tests are included in the directory — **N/A**, nothing was added to `tests/`. The
  checks live in `.claude/hooks/session-start.sh` and `docs/architecture/build.py`.
- This new test PR did not break anything else in the system because **`git diff --name-only
  origin/main...HEAD` lists no file outside markdown, so nothing under `src/` changed and the app
  behaves as before. The app was not run and no screenshot was taken**.
