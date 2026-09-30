# Logs

> **This file is part of the documentation set**, the markdown files the team owns.
> The whole set is reviewed on every pull request and updated in the same PR when affected. Update this file when the log layout or format changes.
> See §9.0 of [the source of truth](../project/COSC499-TEAM10-PROJECT-DOCS.md).

The weekly logs the course grades. Only this README is part of the documentation set. The
`week-<K>.md` files are records of work already done, so they are never rewritten to match
later code.

The course's own requirements are on Canvas, in **Weekly Expectations** and the **weekly
submission rubric**. Check them for what is graded and how. If this README and Canvas
disagree, Canvas is right, and this README is updated to match.

## Layout

```
docs/logs/
├── README.md          this file
├── ahab/week-<K>.md   one individual log per student per week
├── ariq/week-<K>.md
├── ehsan/week-<K>.md
├── gilles/week-<K>.md
└── team/week-<K>.md   one team log per week
```

`<K>` is the week number in the semester. A new student gets a folder named the same way, in
lower case.

## Individual log: Part A

Each student's `week-<K>.md` holds **one section for each PR they merged that week**. Each
section is a copy of that PR's **Part A: What I Built and Why I Know It Works**, the receipts in
[pull_request_template.md](../../pull_request_template.md).

- **Written by `/make-pr`.** The [make-pr workflow](../workflows/make-pr.md#record-part-a-in-the-weekly-log)
  asks which student and which week, writes the section, and commits it on the PR's own branch.
- **Only merged work lands.** Because the section is committed on the PR branch, it reaches
  `main` when the PR merges, and never if the PR is closed without merging. If a PR merges in a
  later week than the one it was logged under, move its section to that week's file before
  merging.
- **The PR description and the log section stay identical.** An edit to one is copied to the
  other in the same step, whether it came from review, from GitHub's editor or from the file.
- **A PR with no receipts is not logged.** A documentation-only PR, whose Part A is a single
  **N/A** line, gets no section.

## Team log: Part B

`team/week-<K>.md` is written once per week by the team, covering everyone's merged work. It
is not written by `/make-pr`, and it does not go in any PR description. It uses the course's
Part B template below. Replace each `[...]` with the answer in **bold**, keep one side of each
_or_, and delete the italic guidance lines, the same way as Part A.

```markdown
## Part B: What Our Team Added and How the Changes Satisfy Software Engineering Principles

- This week, we decided to focus on **[brief description, include requirement reference if
  applicable]** with the goal of **[describe target outcome]**.
- The work was distributed so that **[student A]** focused on **[provide overview of their
  tasks]**, **[student B]** focused on **[provide overview of their tasks]**, **[repeat for
  each team member]**. We considered alternative workload distributions such as **[explain
  details and why you did not go with them]**.
- Based on **[observable criteria or metric measurements]**, we met this goal because
  **[connect criteria/metrics to the target outcome]**.

  _or_
- Based on **[observable criteria or metric measurement]**, we did not meet this goal due to
  the following challenges encountered: **[provide explanation of difficulties]**. Our plan for
  next week will be **[items needed to meet the goal]**.
- The team collectively did **[specific steps taken]** to ensure that the code base does not
  contain any of the following:
  - similar logic implemented multiple times
  - many dependencies between modules
  - changes in one component require changes elsewhere

  _or_
- By doing **[specific steps taken]**, **[name of team member]** found that the code base
  contained **[identify which problem from the list below]**. Therefore, **[name of team
  member(s)]** did **[specific solution taken]**.
  - _(Repeat for additional problems found.)_

  Now, the team can confirm that the code base does not contain any of the following:
  - similar logic implemented multiple times
  - many dependencies between modules
  - changes in one component require changes elsewhere
- With everyone's newly merged work for this week, the system DFD looks like **[same/updated
  diagram]**. The specific changes include **[list changes in the diagram and explain why]**.
  We considered alternative data flows such as **[list other considerations and why you did
  not go with them]**.
- With everyone's newly merged work for this week, the system architecture diagram looks like
  **[same/updated diagram]**. The specific changes include **[list changes in the diagram and
  explain why]**. We considered alternative architectural components **[explain details and
  why you did not go with them]**. We considered alternative dependencies **[explain details
  and why you did not go with them]**.
- _(If applicable)_ We changed our collaboration process so that **[provide details]**. The
  reason we did this is because **[explain what motivated the change]**. We considered
  alternatives **[list other considerations and why you did not go with them]**.
- _(If applicable)_ We amended our team contract so that **[provide details]**. The reason we
  did this is because **[explain what motivated the change]**. We considered alternatives
  **[list other considerations and why you did not go with them]**.
```

The diagrams come from `docs/architecture/`, the same as in Part A.
