# Week 6, Ahab

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**43**

- As part of requirement **FR-CN-20, a disabled needle is left out of the mesh**, the user needs
  to do **disable a needle, import the next plan, and export with every enabled needle cut**.
- Therefore, I implemented/generated code so that **physicists get every channel but the tandem
  enabled on each import**.

#### Backend

- The system adopts a **stateful** approach to state management because **`ChannelsModel` keeps
  disabled channels between edits**. This method is done by **`disabled_channels`**. Benefits for
  using this approach include **one owner of which needles are cut**. Possible risks include
  **state carried into the next plan (§7.10)**.
  - To mitigate **that**, we implemented **emptying it in `load_data`**.
- The system architecture diagram consists of the following major components: **External, Presentation, Application state, Domain services, Libraries and Local storage**. This
  structure has low coupling because **views change channels only through `ChannelsModel`**. This
  structure has high cohesion because **`ChannelsModel` alone owns channel state**. This design is
  scalable because **this fix stays inside that one model**.

  **[System architecture (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587691980185009f292ce7454c352c9f1de4/docs/architecture/diagrams/system-architecture.svg)**
- The Level 0 DFD consists of the following major components: **medical physicist, treatment
  planning system, brachify and printer or CAD**. **The physicist imports a plan, and brachify returns the STL and PDF**

  **[DFD level 0 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587691980185009f292ce7454c352c9f1de4/docs/architecture/diagrams/existing-framework/dfd-0.svg)**
- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem and Export**. **Import loads Ex2,
  Channels enables every needle, Export cuts them**. **A plan with no Central Axis or surface
  stops at Import with an error dialog**.

  **[DFD level 1 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587691980185009f292ce7454c352c9f1de4/docs/architecture/diagrams/existing-framework/dfd-1.svg)**
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **FR-CN-20 → `test_loading_a_plan_enables_every_channel_again`**
- Not applicable: **architectural pattern (unchanged), database (none), data processing
  (unchanged), backend API (none), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **`ChannelsModel.load_data`** for this functionality, I noticed **it kept
  `disabled_channels`, so Ex1's disabled Applicator4 stayed disabled in Ex2**. Therefore, I did
  **empty it there (§7.10)**.
- When I reviewed the **test inventories in `AGENTS.md` and `tests/README.md`**, I noticed **every
  new test made them stale**. Therefore, I did **point both at §8.2**.
- The PR does not contain any temporary workaround because **the reset sits beside the other
  per-plan resets**.
- The PR only contains small functions that are **28 (`load_data`, 1 line added) and 16 (the
  test)** long.
- I did **`anti_slop review --base main` (no findings)** to ensure that my feature contribution does
  not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`channels_model.py`** because **the model owns disabled channels**.
- This work belongs in **3 Channels** in the DFD because **it decides which needle solids reach
  Shapes**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_loading_a_plan_enables_every_channel_again` (65 passed)** passed.
- I checked that these negative cases involving **the test on `main` and with the fix removed
  (`assert not True`)** failed as expected.
- Among these tests, **none** are unit tests and **`test_loading_a_plan_enables_every_channel_again`**
  is an integration test.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (65
  passed, screenshot 1), `build.py --check` and `session-start.sh` (exit 0), and brachify run on
  macOS through its buttons, Ex2 imported after Ex1 (screenshot 2)**.

  ![1, python -m pytest on fix/disabled-channels-on-import at 5949174, 65 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/dd20968af6ad7fb912bf42d8157cd1ac164c980b/docs/logs/ahab/screenshots/week-6/pr-43-1-pytest-65-passed.png)

  ![2, Ex2 in brachify after Applicator4 was disabled in Ex1, Applicator4 enabled and drawn](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/dd20968af6ad7fb912bf42d8157cd1ac164c980b/docs/logs/ahab/screenshots/week-6/pr-43-2-ex2-applicator4-enabled.png)

- Not applicable: **abnormal cases (one path), generated-test review (no problem found)**.

### For PR #**59**

- As part of requirement **FR-CN-08, a needle's own properties override the global channel
  settings**, the user needs to do **give one needle its own diameter, then press Apply on the
  Channels tab with a new Channels Diameter**.
- Therefore, I implemented/generated code so that **physicists' per-needle diameters survive
  Apply, are refused below 0.3 mm or as NaN, and clear on a new import**.

#### Backend

- The system adopts a **stateful** approach to state management because **a needle's own
  diameter must outlast later Applies**. This method is done by **`ChannelsModel.own_diameters`**.
  Benefits for using this approach include **one owner of each needle's width**. Possible risks
  include **a width reaching the next patient, or NaN reaching the geometry**.
  - To mitigate **both**, we implemented **clearing on import, and `ValueError` below 0.3 mm or
    for NaN**.
- The system architecture diagram consists of the following major components: **External, Presentation, Application state, Domain services, Libraries and Local storage**. This
  structure has low coupling because **views set widths only through `ChannelsModel`**. This
  structure has high cohesion because **channel state stays in `ChannelsModel`**. This design is
  scalable because **dead space can join `own_diameters` (FR-CN-19)**.

  **[System architecture (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587691980185009f292ce7454c352c9f1de4/docs/architecture/diagrams/system-architecture.svg)**
- The Level 0 DFD consists of the following major components: **medical physicist, treatment
  planning system, brachify and printer or CAD**. **Channel settings go in, and the STL and PDF come out**

  **[DFD level 0 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587691980185009f292ce7454c352c9f1de4/docs/architecture/diagrams/existing-framework/dfd-0.svg)**
- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem and Export**. **Apply in
  Channels keeps Applicator4's own 3.2 mm, and Export cuts it**. **Below 0.3 mm or NaN is refused
  with `ValueError`, and nothing changes**.

  **[DFD level 1 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587691980185009f292ce7454c352c9f1de4/docs/architecture/diagrams/existing-framework/dfd-1.svg)**
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **FR-CN-08 → the four own-diameter tests in
  `test_channels_view.py`**
- Not applicable: **architectural pattern (unchanged), database (none), data processing
  (unchanged), backend API (none), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated `set_channel_diameter`**, I noticed **its `< 0.3` check let NaN
  through, and NaN crashed the run (exit 139)**. Therefore, I did **refuse non-finite values, with
  a NaN case**.
- The PR does not contain any temporary workaround because **the PDF and config gaps are recorded
  in §7.6 for FR-CN-07**.
- The PR only contains small functions that are **7, 6, 4 and 2 (the four model methods), and at
  most 28 in the tests** long.
- I did **`anti_slop review --base main` (no findings)** to ensure that my feature contribution does
  not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`channels_model.py`, with the minimum in `settings/defaults.py`**
  because **the model owns channel state, and the template library shares the minimum**.
- This work belongs in **3 Channels** in the DFD because **it sets each needle solid's width**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **Apply keeping an
  own diameter, and clearing it (70 passed)** passed.
- I wrote tests to cover abnormal situations involving **a new plan loaded over own diameters**
  and they passed.
- I checked that these negative cases involving **0.2 mm and NaN** failed as expected.
- When I reviewed the **generated `test_channel_keeps_its_own_diameter_when_channels_diameter_is_applied`**,
  I noticed **it used `monkeypatch.setattr`, which anti-slop warns on**. Therefore, I did **restore
  the live settings in `finally` instead**.
- Among these tests, **none** are unit tests and **all four** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (70
  passed, screenshot 1), `build.py --check` and `session-start.sh` (exit 0)**.

  ![1, python -m pytest on feat/channel-own-diameter at 632b389, 70 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/5f297c8dafd3c13319dc0683b835927fd7eaefc2/docs/logs/ahab/screenshots/week-6/pr-59-1-pytest-70-passed.png)

- Review follow-up for **Ariq's #59 comments**: **clearing uses the live config default,
  unknown or unselected labels cannot leave phantom overrides, and shared test state is
  restored**. The new config-import and invalid-label cases **failed before the fix and
  under deliberate reversions**. **73 tests pass on macOS offscreen; anti-slop reports no
  findings; architecture and session-start checks exit 0**. The documentation set was reviewed;
  the project reference, init-guide note and test-fixture documentation changed. The four
  diagrams still describe the same ownership, signals and files. **Native viewport and Windows
  were not rerun**; screenshot 1 remains the original 70-test receipt.
