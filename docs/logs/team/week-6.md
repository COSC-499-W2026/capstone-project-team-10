# Week 6, Team

_Team log. Part B, written once for the whole team, covering everyone's merged work this week.
The template is in [docs/logs/README.md](../README.md#team-log-part-b)._

**Authors:** Ehsan Babar (`ebabar5`).

**PRs covered:** the 34 PRs that reached `main` from 2026-10-15 through 2026-10-19 (after
week 5's cutoff). Week 5 already logged #17–#27 and #29. Numbers are from GitHub and from
`main` at `e559396`. Individual receipts are in each author's `docs/logs/<student>/week-6.md`.

**Still open at log time:** none. #63, #74 and #82, which the earlier draft still listed as
open, and Ahab's follow-up Channels slices #83–#85, all reached `main` on 2026-10-19.


| PR | Author | What it did | Files | Lines changed | Approved by |
|---|---|---|---|---|---|
| [#28](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/28) | Ehsan | `load_config_file` tests; reject `true`/`false` as dimensions | 7 | 194 | Ariq |
| [#31](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/31) | Ariq | Collapse N/A receipts; PR size checks; branch naming | 9 | 305 | Ahab |
| [#32](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/32) | Ariq | Land #21 on main: black Channels spin-box arrows in dark mode | 9 | 259 | Ahab |
| [#33](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/33) | Ariq | Pytest screenshot left out of #20 | 2 | 28 | Ahab |
| [#42](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/42) | Ariq | Screenshots #32's review asked for | 4 | 26 | Ahab |
| [#43](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/43) | Ahab | Every imported plan starts with all channels enabled | 9 | 145 | Ariq, Ehsan |
| [#44](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/44) | Ehsan | Attach `read_structures` onto `DicomData` at import | 9 | 145 | Gilles, Ariq |
| [#49](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/49) | Ariq | Save and load the collar in config files | 9 | 207 | Ahab, Ehsan |
| [#50](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/50) | Ariq | Size and place the notch from `NotchSettings` | 8 | 295 | Ahab, Ehsan |
| [#51](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/51) | Ariq | Build the cylinder notch from notch config keys | 8 | 241 | Ahab, Ehsan |
| [#52](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/52) | Ariq | Notch controls on the Cylinder tab | 9 | 342 | Ahab, Ehsan |
| [#53](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/53) | Ariq | Tests for Cylinder notch controls | 5 | 98 | Ahab, Ehsan |
| [#54](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/54) | Ariq | Flat or domed tip from the tip setting | 7 | 176 | Ahab, Ehsan |
| [#55](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/55) | Ariq | Interstitial lengths against a flat tip | 7 | 189 | Ahab, Ehsan |
| [#56](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/56) | Ariq | Keep tandem cut-out whole in a flat-tipped cylinder | 6 | 159 | Ahab, Ehsan |
| [#57](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/57) | Ariq | Tip Shape choice on the Cylinder tab | 9 | 149 | Ahab, Ehsan |
| [#58](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/58) | Ariq | Notch as set + cylinder on the reference sheet | 6 | 249 | Ahab, Ehsan |
| [#59](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/59) | Ahab | Keep a channel's own diameter through Channels Apply | 9 | 316 | Gilles, Ariq |
| [#60](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/60) | Ahab | Edit one channel's diameter on the Channels tab | 9 | 507 | Ariq |
| [#61](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/61) | Ahab | Needle template library (`needle_templates.py`) | 9 | 337 | Ariq |
| [#62](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/62) | Ahab | Channel status colours on the Channels list | 15 | 655 | Ariq |
| [#63](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/63) | Ahab | Save and apply needle templates on the Channels tab | 9 | 323 | Ariq, Ehsan |
| [#74](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/74) | Ahab | Week-6 screenshots for #59, #63, #84 and #85 | 5 | 36 | Ariq, Gilles |
| [#75](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/75) | Ehsan | Show decoded structures on the Import tab list | 7 | 246 | Gilles, Ariq |
| [#76](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/76) | Ariq | Land #50–#54 on main | 21 | 1,104 | Gilles, Ehsan |
| [#77](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/77) | Ehsan | Docs for `load_structures` wiring and week-6 Part A | 3 | 119 | Gilles, Ariq |
| [#78](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/78) | Gilles | Viewport rotate / pan / proportional zoom | 2 | 190 | Ariq, Ehsan |
| [#79](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/79) | Gilles | Toggleable central-axis reference in the viewport | 4 | 340 | Ariq, Ehsan |
| [#80](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/80) | Ehsan | Docs for Import structure list and week-6 Part A | 4 | 98 | Gilles, Ariq |
| [#81](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/81) | Gilles | Cartesian bounding-box grid with mm labels | 2 | 279 | Ariq, Ehsan |
| [#82](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/82) | Gilles | Viewport docs + Gilles week-6 log (trimmed to 5 files) | 5 | 265 | Ehsan, Ariq |
| [#83](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/83) | Ahab | Needle template library saved as JSON (hardened re-land) | 9 | 420 | Ariq, Gilles, Ehsan |
| [#84](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/84) | Ahab | Edit one channel's diameter (sized re-land of #60) | 9 | 491 | Gilles, Ariq, Ehsan |
| [#85](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/85) | Ahab | Channel status colours (sized re-land of #62) | 9 | 314 | Ehsan, Ariq |

## Part B: What Our Team Added and How the Changes Satisfy Software Engineering Principles

- This week, we decided to focus on **FR-CN cylinder and needle editing (notch, tip, per-channel
  diameter, templates), FR-SV structure import and Import-list display, and FR-SV-06 viewport
  navigation (camera, central axis, mm grid), plus finishing week 5 leftovers (#28, #21 on
  main)** with the goal of **every member landing at least two sized `src/`+`tests/` merges, and
  keeping most PRs under 10 files and 500 lines**.
- The work was distributed so that **Ariq** focused on **FR-CN-14 notch/tip/reference-sheet
  (#49–#58, landed via #76), process rules (#31), and week-5 leftovers (#32, #33, #42)**,
  **Ahab** focused on **Channels: enabled-on-import (#43), own diameter (#59–#60 / #84), status
  colours (#62 / #85), the template library (#61 / #83), template save/apply UI (#63), and
  week-6 screenshots (#74)**, **Ehsan** focused on **config bool rejection (#28) and FR-SV
  structure attach + Import list (#44, #75) with docs (#77, #80)**, and **Gilles** focused on
  **viewport camera (#78), central-axis overlay (#79), mm grid (#81), and viewport docs/log
  (#82)**. We considered alternative workload distributions such as **splitting notch and tip
  across two authors. We kept them with Ariq because both touch `CylinderView`, mesh and the
  PDF, and stacking kept each feature PR under 10 files**.
- Based on **GitHub and `main` at `e559396`**:
  - **all four members merged tested `src/` (or stacked docs) work into `main` this week:
    Ariq's notch/tip stack, Ahab's Channels edits and template apply, Ehsan's structure
    import/list, Gilles's viewport overlays and docs**
  - **Ehsan: five merges (#28, #44, #75, #77, #80); Ariq: many; Ahab: ten (#43, #59–#63, #74,
    #83–#85); Gilles: four (#78, #79, #81, #82)**
  - **most feature PRs are within 10 files; #33, #42, #74, #77, #78, #80, #81 are under 200
    lines. Oversized on `main`: #76 (21 files / 1,104 lines, land PR), #62 (15 files / 655
    lines), #60 (507 lines). Follow-ups #84 and #85 re-landed those Channels slices under 10
    files and 500 lines**

  we met the code goal because **FR-CN-14 notch/tip, per-channel diameter, template save/apply,
  structure attach and Import list, and viewport camera/axis/grid all reached `main` with
  tests, and every member has at least two merges**. We did not fully meet the size goal due
  to the following challenges encountered: **#76's land PR and the first Channels diameter /
  status PRs (#60, #62) went over the preferred limits; #82 had to be trimmed from 15 files to
  5 after review**. Our plan for next week will be **keep follow-up PRs under 10 files, land
  deferred architecture-diagram updates for the viewport overlays, and continue FR-SV 3D
  structure display**.
- By doing **the first `load_config_file` tests (#28)**, **Ehsan** found that the code base
  contained **similar logic treating `True` as 1 via `isinstance(value, int)`**. Therefore,
  **Ehsan** did **reject `bool` in `is_config_number()`**.
  - By doing **a review of `ChannelsModel.load_data` (#43)**, **Ahab** found that the code base
    contained **changes in one component requiring changes elsewhere: `disabled_channels`
    survived into the next plan**. Therefore, **Ahab** did **empty it in `load_data` (§7.10)**.
  - By doing **collar save/load (#49)**, **Ariq** found that the code base contained **changes in
    one component requiring changes elsewhere: collar keys omitted from
    `getCurrentValues` / `resetAllValues`, and *Generate Tandem* replaced live settings**.
    Therefore, **Ariq** did **round-trip the collar and merge the tandem snapshot (§7.1)**.
  - By doing **the flat-tip change (#54)**, **Ariq** found that the code base contained
    **similar dome assumptions in interstitial maths and the tandem cut-out**. Therefore,
    **Ariq** did **record §7.11 and fix the sheet (#55) and tandem cut (#56)**.
  - By doing **structure import wiring (#44) then the Import list (#75)**, **Ehsan** found that
    the code base contained **a reader with no GUI caller, then list text that inherited
    near-white colour from `page_import`**. Therefore, **Ehsan** did **call `load_structures` from
    both vendor readers, and set a black-on-white stylesheet on the structure list**.
  - By doing **viewport camera work (#78)**, **Gilles** found that the code base contained
    **selection firing after every left release, including after a drag**. Therefore, **Gilles**
    did **a sticky drag flag and platform drag threshold**.
  - By doing **the template library re-land (#83)**, **Ahab** found that the code base
    contained **a save path that could truncate the library on a failed write**. Therefore,
    **Ahab** did **atomic write via a temporary file, stricter JSON type checks, and catch
    `OverflowError`**.

  Now, the team can confirm that **the code merged this week, checked by the reviews above,**
  does not contain any of the following, **except the oversized land/status PRs already on
  `main` (#76, #60, #62) that later Channels slices (#84, #85) sized down**:
  - similar logic implemented multiple times
  - many dependencies between modules
  - changes in one component require changes elsewhere
- With everyone's newly merged work for this week, the system DFD looks like **the same
  diagrams as week 5 for external flows. Structure decode and the Import list stay inside
  Import; viewport overlays do not add a process**.

  ![DFD level 0 at e559396](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/e559396/docs/architecture/diagrams/existing-framework/dfd-0.svg)

  ![DFD level 1 at e559396](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/e559396/docs/architecture/diagrams/existing-framework/dfd-1.svg)

  The specific changes include **none to the drawn DFD edges. Import now fills
  `DicomData.structures` and the Import list; that is still process 1**. We considered
  alternative data flows such as **a new process for viewport overlays. Rejected because the
  grid and central axis are display-only and never reach Export**.
- With everyone's newly merged work for this week, the system architecture diagram looks like
  **the updated diagram below**.

  ![System architecture at e559396](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/e559396/docs/architecture/diagrams/system-architecture.svg)

  The specific changes include **`load_structures` and `structure_list` on the domain `dicom:`
  line (#44 / #75), because `build.py --check` fails on modules the diagram does not name.
  Notch, tip, Channels diameter/status/templates, and viewport overlays did not add new
  packages**. We considered alternative architectural components **such as a separate
  NotchModel or a StructureListModel. Rejected because `CylinderModel` and `ImportView`
  already own those surfaces**. We considered alternative dependencies **none; no conda
  package was added this week**.
- We changed our collaboration process so that **#31 collapsed Part A N/A lines, added PR size
  checks and `<type>/<what>` branch names; large features stayed in stacked PRs (#50–#54 via
  #76, #44→#77→#75→#80); #82 was trimmed from 15 files to 5 after review; and Ahab re-landed
  oversized Channels slices as #83–#85 under the size limits**. The reason we did this is
  because **week 5 overran size and N/A length, deleting a stack base branch auto-closed
  dependent PRs until they were reopened onto `main`, and review kept rejecting PRs over 10
  files**. We considered alternatives **such as one mega PR for notch+tip or for structure
  import+list. Rejected in favour of stacks, though land PRs (#76) and the first Channels
  diameter/status PRs (#60, #62) still went over before the sized re-lands**.
- We did not amend the team contract this week. **No commit has touched `docs/contract/` since
  `a7879b5` on 2026-09-25.**
