# Workflow: make-weekly-log

> **This file is part of the documentation set.** See §9.0 of
> [the source of truth](../project/COSC499-TEAM10-PROJECT-DOCS.md). Update it when the team
> log process changes, or when the grader comments on a team log.

**Tool-agnostic.** This is the canonical procedure. Any AI agent, or any person, can follow it
directly. Claude Code users can invoke it as `/make-weekly-log <week> <PRs>`, which is a thin
pointer to this file. Other agents should be pointed at this path, or will find it via
[AGENTS.md](../../AGENTS.md#workflows).

---

Write the team's weekly log, `docs/logs/team/week-<N>.md`: the course's **Part B**, covering
everyone's merged work that week. Part A, each student's own log, is written by
[make-pr.md](make-pr.md), not here. Follow these rules exactly.

## Inputs

| Input | Form | Used for |
|---|---|---|
| **Week** | the week number `N`, such as `7` | the file, `docs/logs/team/week-<N>.md` |
| **PRs** | PR numbers, or URLs of the form `https://github.com/COSC-499-W2026/capstone-project-team-10/pull/<id>`, separated by spaces or commas | the PRs the log covers |

If either is missing, ask for it. Do not work the week out from the date, and do not choose the
PRs yourself. You may suggest the PRs merged into `main` since the previous team log's cutoff,
which that log's **PRs covered** line states, but the user decides.

## Ask clarifying questions before writing

Gather the evidence first, as [Gather the evidence](#gather-the-evidence) describes, so that
your questions are specific. Then ask, in one batch, and wait for the answers. Ask at least:

- **Authors.** Who is writing this team log? The course gives no mark for it to a member who
  did not contribute to it.
- **The PR list.** Name any PR you found that is not merged, merged only into a branch that never
  reached `main`, or merged in another week, and ask whether to leave it out or record it as open.
  Name any PR merged in the week that the user did not list. Only merged work is graded.
- **The goal.** What did the team set out to do this week, and how did it plan to measure it?
  Offer what the previous team log's "plan for next week" said.
- **Choices you cannot see in the record.** Alternative workload distributions, data flows,
  architectural components or dependencies the team considered, and why it rejected them. Offer
  any you found in PR bodies or reviews, and ask for the rest.
- **Process and contract.** Did the team change how it works together, or amend the team
  contract? Offer what the diff and the PR bodies suggest.
- Anything else the evidence leaves unclear, such as a number that disagrees between a PR body
  and GitHub.

Never fill a receipt with an alternative, a problem or a decision nobody recorded or told you.
If none was recorded and the user has none to add, write that none was recorded.

## What the grader has said

The team log is graded on **Evidence-Claim Alignment** and **Minimal Viable Traceability**, 3
points each. Read every comment below before writing, and add each new one to this table when
the user shares it.

| Week | Mark | Grader's comment |
|---|---|---|
| 4 | 6/6 | "Excellent team log. It follows the Part B template closely and supports its claims with concrete evidence, including 20 passing tests, architecture checks across seven diagrams, and two teammate approvals on all nine PRs. The team also identified and resolved duplicated pytest setup and dependency issues, and gave clear rationale for DFD and architecture changes with alternatives considered. Limitations are stated clearly, making the reasoning easy to verify." |
| 5 | 5/6 | "Reduce lengthy explanations, provide accessible diagram references, and keep feature PRs within the size limits." |
| 6 | 5/6 | "Good implementation work on cylinder customization, supported by detailed testing, geometric validation, and clear explanations of engineering decisions. Improve traceability by consolidating repetitive explanations and clearly identifying the unique changes and test evidence associated with each PR. The stacked PR structure should make it straightforward to distinguish incremental contributions from inherited changes." |

What that means for this log:

- **Follow the Part B template closely** and back every claim with a number a grader can check:
  tests passing, `build.py --check` over the diagrams, approvals per PR (week 4).
- **State limitations plainly,** and say which claims you observed, which a PR or log
  reports, and which you reasoned from the code (week 4).
- **Keep explanations short.** One claim and its evidence per fill-in. Bullets for lists. Do
  not retell what an individual log already says: link it (week 5).
- **Make diagrams accessible,** as [Diagrams](#diagrams) describes (week 5).
- **Report PR sizes honestly** against the limits, and name every PR that breaks one (week 5).
- **Write each explanation once.** A fact that holds for several PRs or a whole stack is stated
  once, not in every bullet (week 6).
- **Show each PR's own contribution.** For a stack, give each PR's own diff and new tests, and
  never count the same lines or tests twice. A PR that lands a stack on `main` adds no new work
  of its own (week 6).

## Gather the evidence

Do this before asking questions, and cite only what you gathered.

1. **Each PR, from GitHub:**
   ```bash
   gh pr view <n> --repo COSC-499-W2026/capstone-project-team-10 --json \
     number,title,author,state,mergedAt,mergeCommit,baseRefName,headRefName,changedFiles,additions,deletions,reviews,closingIssuesReferences,body
   ```
   Keep only merged PRs. For each, confirm it reached `main`:
   `git merge-base --is-ancestor <merge commit> origin/main`. A PR merged into another
   branch that never reached `main` is not on `main`, as #21 was in week 5.
2. **Approvals.** Count the approving reviews from teammates other than the author.
3. **Size.** Files changed and lines changed (additions plus deletions), against the limits in
   [Check the PR size limits](make-pr.md#check-the-pr-size-limits).
4. **Stacks.** Group PRs whose base was another PR's branch. GitHub's counts for a stacked PR
   are its own diff against its parent. A PR that merges a whole stack into `main` repeats its
   members' lines, so mark it as a land PR and do not count its lines as new work.
5. **Each author's log,** `docs/logs/<student>/week-<N>.md`. Part B summarises the team; the
   receipts stay in the individual logs, so link them rather than copying.
6. **`main` now.** Fetch, note the commit, and run, in the conda environment:
   - `python -m pytest` and note the total. Compare it with the previous team log's figure.
   - `python docs/architecture/build.py --check`, which must exit 0, and the number of diagrams.
7. **What changed in the diagrams and the contract** since the previous team log's commit:
   `git diff <previous commit> <this commit> --stat -- docs/architecture/diagrams docs/contract`.

## Write the log

Open `docs/logs/team/week-<N>.md`, creating it if needed, and lay it out as the earlier weeks
do:

1. `# Week <N>, Team` and the same italic note as `team/week-4.md`.
2. `**Authors:**` with each author's name and GitHub login.
3. `**PRs covered:**` with the date range, the `main` commit the numbers come from, and a
   pointer to the individual logs.
4. **A table of the PRs:** PR (linked), author, what it did, files, lines changed, approved by.
   Group a stack's rows together under its own name, such as "Stack #93 to #102", so that each
   row is that PR's own diff. Mark a land PR as such.
5. **Part B,** from the template in
   [docs/logs/README.md](../logs/README.md#team-log-part-b). Do not copy the template from
   anywhere else. Replace each `[...]` with the answer in **bold**, keep the true side of each
   _or_ and delete the other, delete _(If applicable)_ receipts that do not apply, and delete
   the italic guidance lines.

Rules for the fill-ins:

- **Every claim carries its evidence** inside the bold: a PR number, a test count with the
  commit it was observed at, a file, or a command and its result.
- **Calibrate.** Mark what you observed yourself (and where), what a PR or log reports, and
  what is reasoned from code. Where the evidence is partial, say so in a short limits list after
  the goal receipt, as `team/week-4.md` does.
- **Did we meet the goal.** Use the metric the user gave. If any part was not met, use the
  _did not meet_ receipt, with the challenges and the plan for next week.
- **Problems found.** Use the _By doing ... found_ form only for problems a member actually
  found this week, from PR bodies, reviews, logs or the user. Each one names who found it, what
  was found, and the fix with its PR.
- **One mention per fact.** If a sentence would repeat another receipt, point to it instead.
- **No length for its own sake.** Week 4 got full marks at about 2,000 words of Part B because
  each sentence carried evidence. Cut any sentence a grader would not check.

### Diagrams

For the DFD receipt and the architecture receipt, show the diagram as an image that renders
anywhere, with a link to its source:

1. Render each diagram the receipt names as a PNG from its `.mmd` source at the commit the log
   describes:
   `npx --yes @mermaid-js/mermaid-cli@11 -i docs/architecture/diagrams/<path>.mmd -o docs/logs/team/screenshots/week-<N>/<name>.png -s 2`.
   The diagrams are `existing-framework/dfd-0`, `existing-framework/dfd-1` and
   `system-architecture`.
2. Commit the PNGs, then embed each one by its `raw.githubusercontent.com` URL pinned to that
   commit, with alt text that says what the diagram shows and what changed this week. Under
   each image, link the version-controlled `.svg` at the same commit as its source.
3. Say in the receipt whether the diagram is the same as last week or updated, and if updated,
   which PR changed it. Never hand-edit an `.svg`. [docs/architecture/README.md](../architecture/README.md)
   owns when diagrams are redrawn.

## Commit and open the PR

1. Create a branch `docs/team-week-<N>-log` from `main`, as [commit.md](commit.md) describes,
   and commit the log and its images following that file.
2. Open the PR following [make-pr.md](make-pr.md). It is a documentation PR, so its Part A is
   short. Each PNG is a changed file toward the size limits.
3. Never add AI attribution, in a commit or in the PR. The rule and its reasons are in
   [commit.md](commit.md#never-add-ai-attribution) and
   [make-pr.md](make-pr.md#never-add-ai-attribution).

## Finishing

Return:

- the file written, and the PR URL if one was opened
- each receipt still waiting on the user, such as an alternative nobody recorded
- the counts from the PR size check
- a reminder to add the grader's comment on this log to
  [What the grader has said](#what-the-grader-has-said) once it is marked
