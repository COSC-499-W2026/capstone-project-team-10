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
  passed), `build.py --check` and `session-start.sh` (exit 0)**.
- Not applicable: **abnormal cases (one path), generated-test review (no problem found)**.

### For PR #**59**

- As part of requirement **FR-CN-08, individual needles have their own properties that override
  the global channel settings**, the user needs to do **give one needle its own diameter, then
  press Apply on the Channels tab with a new Channels Diameter, and keep that needle's width**.
- Therefore, I implemented/generated code so that **physicists' per-needle diameters survive the
  Channels tab's Apply, are refused below 0.3 mm or as NaN, and are cleared by a new import**.

#### Backend

- The system adopts a **stateful** approach to state management because **a needle's own diameter
  must outlast every later Apply on the Channels tab**. This method is done by
  **`ChannelsModel.own_diameters`, a `dict[str, float]` by label, which `set_diameter` reads for
  each channel it rebuilds**. Benefits for using this approach include **one owner for every
  needle's width, which Export cuts through `channel.shape()`**. Possible risks include **one
  patient's width reaching the next patient's channel of the same label, and an invalid width
  reaching the geometry**.
  - To mitigate **own diameters carrying across imports**, we implemented **`load_data` emptying
    `own_diameters`**.
  - To mitigate **an invalid width**, we implemented **`ValueError` below
    `MINIMUM_CHANNEL_DIAMETER_MM` or for NaN, which otherwise crashes OpenCASCADE (exit 139)**.
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **FR-CN-08 → the four own-diameter tests in
  `test_channels_view.py`**
- Not applicable: **architectural pattern, architecture diagram, Level 0 DFD, Level 1 DFD
  (unchanged, `build.py --check` exit 0), database (none), data processing (unchanged), backend
  API (none), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated `set_channel_diameter`**, I noticed **its `< 0.3` check let NaN
  through, and a NaN diameter crashed the run with exit 139**. Therefore, I did **refuse any
  value that is not finite, with a NaN test case**.
- The PR does not contain any temporary workaround because **the PDF and config gaps are recorded
  in §7.6 for FR-CN-07, not patched around**.
- The PR only contains small functions that are **7, 6, 4 and 2 (`set_diameter`,
  `set_channel_diameter`, `clear_channel_diameter`, `has_own_diameter`), and at most 28 in the
  tests** long.
- I did **`anti_slop review --base main` (no findings) and a read of the diff** to ensure that my
  feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`channels_model.py`, with the minimum in `settings/defaults.py`**
  because **the model owns channel state, and `defaults.py` is pure, so the template library can
  share the minimum**.
- This work belongs in **3 Channels** in the DFD because **it sets the width of each needle solid
  sent to the Shapes store**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_channel_keeps_its_own_diameter_when_channels_diameter_is_applied` and
  `test_channel_follows_channels_diameter_again_once_its_own_is_cleared` (70 passed)** passed.
- I wrote tests to cover abnormal situations involving **a new plan loaded over own diameters
  (`test_loading_a_plan_clears_every_own_diameter`)** and they passed.
- I checked that these negative cases involving **0.2 mm and NaN
  (`test_own_diameter_below_the_minimum_or_not_a_number_is_rejected`)** failed as expected.
- When I reviewed the **generated `test_channel_keeps_its_own_diameter_when_channels_diameter_is_applied`**,
  I noticed **it used `monkeypatch.setattr`, which anti-slop's `no-module-mocking` warns on**.
  Therefore, I did **swap the live settings for a copy and restore them in `finally`**.
- Among these tests, **none** are unit tests and **all four** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (70
  passed), `build.py --check` and `session-start.sh` (exit 0)**.
