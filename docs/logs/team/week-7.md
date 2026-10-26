# Week 7, Team

_Team log. Part B, written once for the whole team, covering everyone's merged work this week.
The template is in [docs/logs/README.md](../README.md#team-log-part-b)._

**Authors:** Gilles Fricker (`Writable04`).

**PRs covered:** #93 through #145, merged October 20–25, 2026 in America/Vancouver
(through October 26, 03:46 UTC). Evidence is pinned to `main` at
[`eab39fc`](https://github.com/COSC-499-W2026/capstone-project-team-10/commit/eab39fca37665c60dee4cca85892ddfc6a62ff7c).
There are 32 PR records in this range, representing 31 contributions landed on `main`.
#120 was merged into a feature branch and replaced by #138; its original merge commit is not
an ancestor of this cutoff. #138 lands that work, counted once. The other 31 merge commits
were confirmed as ancestors of the cutoff. No unmerged PR was found in the requested range.

Individual receipts: [Ariq](../ariq/week-7.md), [Ahab](../ahab/week-7.md),
[Ehsan](../ehsan/week-7.md), [Gilles](../gilles/week-7.md).

## Contributions and review evidence

Files and lines are GitHub's final per-PR diff counts; lines means additions plus deletions.
Approvers are distinct teammates with an approving latest substantive review, excluding the author.
**New tests** below means newly added `test_*` functions, compared with each main merge's first
parent; parametrized cases are not separate functions. This avoids treating inherited tests
as new. Case counts and historical runs remain in the linked individual receipts.

### Cylinder-template stack: #93 → #94 → #95 → #97 → #98 → #100 → #101 → #102

| PR | Author | Own contribution | Files | Lines | New tests | Approved by |
|---|---|---|---:|---:|---:|---|
| [#93](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/93) | Ariq | Validated cylinder template values | 9 | 315 | 6 | Ahab, Ehsan |
| [#94](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/94) | Ariq | Versioned JSON library and safe writes | 9 | 405 | 9 | Ahab, Ehsan |
| [#95](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/95) | Ariq | Library update/delete and shared name check | 6 | 228 | 7 | Ahab, Ehsan |
| [#97](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/97) | Ariq | Scrollable Cylinder form | 9 | 131 | 2 | Ahab, Ehsan |
| [#98](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/98) | Ariq | Save-as-template controls | 9 | 446 | 6 | Ahab, Ehsan |
| [#100](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/100) | Ariq | Load settings without applying them | 9 | 229 | 4 | Ahab, Ehsan |
| [#101](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/101) | Ariq | Update/delete controls and confirmation | 9 | 311 | 6 | Ahab, Ehsan |
| [#102](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/102) | Ariq | Template-to-mesh/PDF regression tests | 5 | 164 | 3 | Ahab, Ehsan |

### Channel-move stack: #118 → #119 → #138 (replacement for #120)

| PR | Author | Own contribution | Files | Lines | New tests | Approved by |
|---|---|---|---:|---:|---:|---|
| [#118](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/118) | Ahab | XYZ channel moves preserving DICOM points | 10 | 548 | 14 | Ariq, Gilles, Ehsan |
| [#119](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/119) | Ahab | Move button and underline legend | 8 | 162 | 3 | Ariq, Gilles, Ehsan |
| [#120](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/120) | Ahab | Warning/PDF work, superseded by #138 | 7 | 283 | counted at #138 | Ariq, Gilles, Ehsan |
| [#138](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/138) | Ahab | Land #120: out-of-cylinder warning and PDF note | 7 | 283 | 7 | Ehsan, Gilles |

### Structures navigation: #116 → #117, then #126

| PR | Author | Own contribution | Files | Lines | New tests | Approved by |
|---|---|---|---:|---:|---:|---|
| [#116](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/116) | Ehsan | Structures page at index 5 | 9 | 158 | 2 | Ariq, Gilles |
| [#117](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/117) | Ehsan | Navigation button and shared highlighting | 8 | 292 | 6 | Ariq, Gilles |
| [#126](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/126) | Ehsan | UML view indexes corrected to 0–5 | 6 | 32 | 0 | Ariq, Gilles, Ahab |

### Anatomy stack, in the order landed

| PR | Author | Own contribution | Files | Lines | New tests | Approved by |
|---|---|---|---:|---:|---:|---|
| [#133](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/133) | Gilles | Frame-checked contour geometry | 2 | 133 | 4 | Ehsan, Ariq, Ahab |
| [#139](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/139) | Gilles | Contour registration docs and test reference | 7 | 89 | 0 | Ahab, Ehsan |
| [#121](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/121) | Gilles | Outline visibility, probe frame and reset wiring | 9 | 345 | 5 | Ehsan, Ariq, Ahab |
| [#122](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/122) | Gilles | Surface dependencies and setup documentation | 3 | 40 | 0 | Ehsan, Ariq, Ahab |
| [#123](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/123) | Gilles | Shared array-based registration transform | 2 | 24 | 1 | Ehsan, Ariq, Ahab |
| [#124](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/124) | Gilles | Axial contour-to-surface reconstruction | 2 | 202 | 5 | Ehsan, Ariq, Ahab |
| [#134](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/134) | Gilles | Worker, caches, generations and per-ROI state | 4 | 492 | 12 | Ehsan, Ariq, Ahab |
| [#140](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/140) | Gilles | Worker system-architecture map | 4 | 34 | 0 | Ahab, Ehsan |
| [#141](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/141) | Gilles | Anatomy state UML and data flows | 9 | 130 | 0 | Ahab, Ehsan, Ariq |
| [#142](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/142) | Gilles | Worker/reconstruction reference and test index | 5 | 237 | 0 | Ahab, Ehsan |
| [#125](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/125) | Gilles | Surface/Outlines/Both and opacity controls | 5 | 206 | 3 | Ehsan, Ariq, Ahab |
| [#143](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/143) | Gilles | Surface actor map and feature receipts | 4 | 198 | 0 | Ehsan, Ariq |
| [#144](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/144) | Gilles | Mode/opacity UML and data flows | 9 | 82 | 0 | Ehsan, Ariq |
| [#145](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/145) | Gilles | Surface controls reference and test index | 5 | 138 | 0 | Ehsan, Ariq |

### Traceability workflow stack: #130 → #131 → #132

| PR | Author | Own contribution | Files | Lines | New tests | Approved by |
|---|---|---|---:|---:|---:|---|
| [#130](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/130) | Ariq | Per-PR stack receipts, issue and screenshot rules | 6 | 434 | 0 | Ahab, Ehsan |
| [#131](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/131) | Ariq | Team weekly-log workflow | 5 | 231 | 0 | Ahab, Ehsan |
| [#132](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/132) | Ariq | Workflow links across documentation set | 6 | 48 | 0 | Ahab, Ehsan |

#138 adds no separate feature beyond the replacement described in its PR body. Its seven new
main-branch test functions and 283 changed lines are counted there, not again at #120.
Documentation and dependency rows with zero new test functions do not claim inherited tests.

## Part B: What Our Team Added and How the Changes Satisfy Software Engineering Principles

- This week, we decided to focus on **more templating and channel customization, and making
  imported structures visible in brachify, as Gilles confirmed for this log: FR-CN-05/06,
  FR-CN-02/07 and the FR-SV-01/02/04 preview work above** with the goal of **landing usable
  template controls, channel moves and structure visualization in `main`, assessed through
  the merged features and their regression tests rather than a pre-agreed numerical target**.
- The work was distributed so that **Ariq** focused on **cylinder templates (#93–#102) and
  traceable PR/log procedures (#130–#132)**, **Ahab** focused on **channel movement, its controls
  and warnings (#118, #119, #138)**, **Ehsan** focused on **the Structures page, navigation and
  view-index documentation (#116, #117, #126)**, and **Gilles** focused on **registered contour
  and surface previews, asynchronous state and their documentation (#133, #121–#125, #134,
  #139–#145)**. We considered alternative workload distributions such as **none recorded in
  the reviewed receipts; no additional workload alternative was supplied for this log**.
- Based on **the 31 main-branch contributions above, each with at least two teammate approvals;
  315 tests passing in 314.21 seconds on macOS at `eab39fc`; and
  `python docs/architecture/build.py --check` exiting 0 across seven diagrams**, we met this
  goal because **template save/load/update/delete, channel XYZ editing with reference-sheet
  warnings, and visible structure surfaces/outlines all reached `main` with regression checks**.

  Evidence limits and the separate process target:

  - **Observed:** the full pytest suite ran with `Path.home()` redirected at the filesystem
    boundary before collection, keeping configuration isolated. No tests were excluded.
    This was not a new native-viewport or Windows/Linux regression run.
  - **Reported baseline:** Ariq's stack receipt records 178 cases before #93 (`aaeb8b9`).
    Its `src/` and `tests/` trees match week 6's cutoff `e559396`; the observed final total is
    137 cases higher. Week 6's team log itself does not give a suite total.
  - **PR-size target not met:** excluding superseded #120, 30/31 PRs (96.8%) satisfy both
    <10 files and <500 changed lines, below the 99% target. **#118 has 10 files/548 lines**.
    Only 3/31 (9.7%) satisfy <3 files and 15/31 (48.4%) satisfy <200 lines, below the 50–75%
    targets. These are separate thresholds; #124 meets the small-file threshold but not the
    small-line threshold. The workflow does not audit the per-file 500-lines-of-code rule.
    A follow-up process goal is to plan smaller review slices before implementation; this is
    a recommendation from this audit, not a claim that the team already agreed a next-week plan.
  - **Reported limitations:** Ehsan's #116/#117 receipts record four existing Windows failures
    (one geometry tolerance and three layout cases). Gilles's receipts do not establish clinical
    volume accuracy, native Nucletron rendering or Windows executable packaging. The current
    dependency reference (§1.3) still records an unresolved conda-forge lockfile migration.
    Earlier failed architecture checks in individual receipts are historical; the final check
    above passes. Those historical receipts have not been rewritten.
- By doing **the library-edit work recorded in #95**, **Ariq** found that the code base
  contained **a name check that update needed to share while excluding the current template**.
  Therefore, **Ariq** did **extract `name_taken` and reuse the existing safe-write path**.
  By doing **the navigation work recorded in #117**, **Ehsan** found that the code base
  contained **five highlight methods that would each need editing for a sixth button**.
  Therefore, **Ehsan** did **centralize `_nav_buttons` and `_highlight_nav`**.
  By doing **the warning work recorded in #138**, **Ahab** found that the code base
  contained **a PDF rule that listed channels wholly below the base with a made-up zero length**.
  Therefore, **Ahab** did **correct `channels_inside_cylinder` and reuse that rule in the popup**.
  By doing **surface alignment and review fixes recorded in #123/#134**, **Gilles** found that
  the code base contained **unnecessary contour conversions and reconstruction tied to GUI updates**.
  Therefore, **Gilles** did **share `transform_points` and isolate reconstruction in a single worker
  with generation checks and separate opacity updates**.

  These receipts support specific reductions in duplicated logic and change propagation.
  They do **not** establish that the whole repository has no duplication or coupling;
  the architecture reference still documents index-addressed views and direct model access.
- With everyone's newly merged work for this week, the system DFD looks like **the updated
  level 0 and level 1 snapshots below, changed by #141 and #144**. The specific changes include
  **structure visibility/mode/opacity input and preview/status output at level 0; a separate
  Structures preview, anatomy cache and reconstruction worker at level 1; and reset invalidation
  of old results. No anatomy edge enters printable Export geometry**. We considered alternative
  data flows such as **synchronous reconstruction, replaced after #134's review because it
  blocked GUI work; #123 also replaced surface vertices routed through temporary Contour values
  with a shared array transform, as their receipts record**.

  ![Level 0 adds structure controls and preview/status feedback](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/ac784210680620fd7806abd557bd4ada5481c083/docs/logs/team/screenshots/week-7/dfd-0.png)

  [Version-controlled SVG](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/ac784210680620fd7806abd557bd4ada5481c083/docs/architecture/diagrams/existing-framework/dfd-0.svg).

  ![Level 1 adds display-only anatomy state, reset invalidation and the surface worker](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/ac784210680620fd7806abd557bd4ada5481c083/docs/logs/team/screenshots/week-7/dfd-1.png)

  [Version-controlled SVG](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/ac784210680620fd7806abd557bd4ada5481c083/docs/architecture/diagrams/existing-framework/dfd-1.svg).

- With everyone's newly merged work for this week, the system architecture diagram looks like
  **the updated snapshot below**. The specific changes include **cylinder template values and
  local JSON storage (#93/#94), the sixth view (#116), contour geometry (#139), worker/cache
  and scientific libraries (#140), and native surface actors with separate opacity delivery
  (#143)**. We considered alternative architectural components **inserting Structures at view
  index 1, rejected in #116 to preserve existing indexes; and mesh-layer template values,
  rejected in #93 because importing cylinder geometry requires the app to exist**.
  We considered alternative dependencies **switching the Windows tifffile build to conda-forge;
  the documented #122 solver checks rejected a one-URL replacement because its dependencies
  were incompatible with the pinned environment (§1.3). SciPy and scikit-image support the
  implemented distance-field and marching-cubes service; no comparison with other surface
  libraries is recorded**.

  ![System architecture adds templates, six views, anatomy services, worker state and surface actors](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/ac784210680620fd7806abd557bd4ada5481c083/docs/logs/team/screenshots/week-7/system-architecture.png)

  [Version-controlled SVG](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/ac784210680620fd7806abd557bd4ada5481c083/docs/architecture/diagrams/system-architecture.svg).

  The PNGs were rendered from the cutoff's unchanged Mermaid sources using mermaid-cli 11
  at scale 2. Level 1 uses the ELK layout with node spacing 100 and rank spacing 160 to keep
  labels apart; its nodes and edges match the version-controlled source.
- We changed our collaboration process so that **#130 requires distinct stacked-PR contributions,
  issue links and screenshots; #131 adds the team-log workflow; and #132 makes it discoverable
  across the documentation set**. The reason we did this is because **the week 6 grader asked
  for unique contributions and incremental test evidence, recorded in #130 and the workflow's
  feedback table**. We considered alternatives **repeating full shared receipts in every log
  section, replaced by shared blocks in #130; and putting the workflow plus every index update
  in one PR, split into #131/#132 when it reached ten files, as Ariq's receipts explain**.

No contract amendment is evidenced: `git diff e559396 eab39fc -- docs/contract` is empty.
No additional process or contract change was supplied for this log.
