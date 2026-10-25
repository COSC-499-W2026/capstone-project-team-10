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
├── ahab/screenshots/week-<K>/  images that week's receipts link to, if any
├── ahab/evidence/     written regression records a receipt links to, if any
├── ariq/week-<K>.md
├── ariq/screenshots/week-<K>/   images a Part A cites as evidence
├── ehsan/week-<K>.md
├── gilles/week-<K>.md
└── team/week-<K>.md   one team log per week
```

`<K>` is the week number in the semester. A new student gets a folder named the same way, in
lower case.

A screenshot a Part A receipt cites goes in `<student>/screenshots/week-<K>/`, committed on
the PR's branch. Link it in both the PR description and the log by its
`raw.githubusercontent.com` URL pinned to the commit that added it, so the two texts stay
identical and the image renders in both. A relative path would render only in the log.

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
- **Minimal.** One short answer per receipt, with nothing written outside the template's
  sentences. Receipts that do not apply are named in one `Not applicable` line per
  subsection, not written out one by one as N/A. The grader marks a log down for length that
  slows the audit, and for repeated N/A sections. See
  [Keep Part A minimal](../workflows/make-pr.md#keep-part-a-minimal).
- **A stack shows what each PR added.** For stacked PRs, the log opens the stack with a table
  of each PR's own diff, new tests and suite total, and states the receipts every PR shares
  once, so each section holds only what its PR added. That block is log-only. See
  [Stacked PRs](../workflows/make-pr.md#stacked-prs), and `ariq/week-7.md` for an example.
  Week 6 lost a mark for repeating shared receipts and giving cumulative test counts.
- **Every PR is logged.** A documentation or process PR gets a short section, keeping only the
  receipts that apply to it, as
  [Tests in this PR or another](../workflows/make-pr.md#tests-in-this-pr-or-another) lists.
- **Screenshots live beside the log.** A receipt that cites a screenshot links to an image
  committed on the PR's branch in `docs/logs/<student>/screenshots/week-<K>/`, the same week as
  the log that links it, and named `pr-<n>-<step>-<what>.png`. The link is a
  `raw.githubusercontent.com` URL pinned to the commit that added the image, as `team/week-4.md`
  does for its diagrams, so the PR description and the log carry the same text and the link
  survives the merge. Rebasing that commit or moving the image changes the commit to pin, so
  update the link in both places if you do either. A screenshot the agent could not take is
  left as `[author: attach a screenshot of ...]`, and `/make-pr` tells the author and asks for
  the image, as
  [Screenshots the author must supply](../workflows/make-pr.md#screenshots-the-author-must-supply)
  describes.
- **Other regression records go in `evidence/`.** A written observation or terminal excerpt
  may be stored in `docs/logs/<student>/evidence/` and linked from the receipt. If a screenshot
  is supplied only in chat and its original file is unavailable, say so explicitly; a written
  observation or terminal excerpt is not an archived image.

## Team log: Part B

`team/week-<K>.md` is written once per week by the team, covering everyone's merged work. It
is written by [make-weekly-log](../workflows/make-weekly-log.md) (`/make-weekly-log <week> <PRs>`),
not by `/make-pr`, and it does not go in any PR description. It uses the course's
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

The diagrams come from [docs/architecture/diagrams/](../architecture/diagrams/), the same as in
Part A. [docs/architecture/README.md](../architecture/README.md) says when they are redrawn.
