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
  passed), `build.py --check` and `session-start.sh` (exit 0)**.

### For PR #**60**

- As part of requirement **FR-CN-08, with FR-CN-02 (interface), edit controls disabled with
  nothing selected**, the user needs to do **select a needle, type its diameter, press Apply to
  Channel, and later press Use Channels Diameter**.
- Therefore, I implemented/generated code so that **physicists give one needle its own diameter on
  the Channels tab, see each selected needle's width, and undo it**.

#### Frontend

- The frontend is designed using **PySide6 and Qt Designer** with design components for **the
  Selected Channel group, whose one stylesheet styles its buttons**. Therefore, changing the design
  of **that stylesheet** will automatically change the look and feel of all instances of that
  component throughout the system. Changes to the content will not affect the design because
  **values come from `ChannelsModel`**.
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **FR-CN-08 → `test_apply_to_channel_changes_only_the_selected_channel`;
  FR-CN-02 (interface) → `test_selected_channel_controls_are_disabled_with_no_channel_selected`**
- Not applicable: **data caching (no new data), restricted pages (no logins), usability
  evaluation (none run), accessibility (no new principle), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated Selected Channel group**, I noticed **it squeezed the spin boxes
  above it to 9 px in the default 770 × 472 window**. Therefore, I did **put the tab in a scroll
  area, with a test**.
- The PR does not contain any temporary workaround because **the scroll area is a standard Qt
  layout (§5.6)**.
- The PR only contains small functions that are **4 and 3 (the two actions), and at most 20 in the
  tests** long.
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
- This work is written in **`channels_view.py` and `channels_view.ui`** because **the view owns its
  widgets**.
- This work belongs in **3 Channels** in the DFD because **the per-needle bore enters there**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **apply, undo and the
  shown diameter (76 passed)** passed.
- I wrote tests to cover abnormal situations involving **the default window size and no
  selection** and they passed.
- I checked that these negative cases involving **0.1 mm typed into the box** failed as expected.
- When I reviewed the **generated `test_selecting_a_channel_shows_its_current_diameter`**, I
  noticed **it passed before the view was wired**. Therefore, I did **type an unapplied value
  first**.
- Among these tests, **none** are unit tests and **all six** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (76
  passed), `build.py --check` and `session-start.sh` (exit 0)**.

### For PR #**61**

- As part of requirement **FR-CN-05, save needle designs as templates in a library, with
  FR-CN-06's corrupted-file case**, the user needs to do **save a needle type's diameter under a
  name and get the same width back in a later session**.
- Therefore, I implemented/generated code so that **physicists' needle templates are kept in
  `~/brachify/needle_templates.json`, validated, unique by name, and never overwritten when the
  file is unreadable**.

#### Data Modeling and Integrity

- This data **`NeedleTemplate`** is modeled as **a frozen dataclass of `name` and `diameter_mm`**
  because **a template must not change once validated**. We considered alternative models such as
  **the decoded JSON `dict`, rejected because anti-slop forbids passing undecoded data inward**.
- This data **`needle_templates.json`** uses the input validation to ensure it adheres to **a JSON
  list of objects with a non-blank, unique `name` and a finite `diameter_mm` of at least 0.3**.
- This data **`needle_templates.json`** may be vulnerable to **a corrupt or hand-edited file**.
  Therefore, it uses a security-based sanitization by **decoding every entry through
  `make_template` and refusing the whole file, without overwriting it**. We considered alternative
  security solutions such as **skipping bad entries, rejected because a partly read library shows
  widths from the wrong entry**.
- Not applicable: **privacy sanitization (no patient data), encryption (nothing sensitive),
  access controls (one local user)**.

#### Backend

- The system architecture diagram consists of the following major components: **External,
  Presentation, Application state, Domain services (now naming `needle_templates`), Libraries and
  Local storage (now with `needle_templates.json`)**. This structure has low coupling because
  **the module imports only `settings.defaults`, and its caller passes the path**. This structure
  has high cohesion because **decoding, validating and saving templates live in one module**. This
  design is scalable because **dead space for FR-CN-19 is one more field in the same objects**.

  **[System architecture](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/a3db1e13f4fe77f045c6ee6d2e5b842a4b4a6e67/docs/architecture/diagrams/system-architecture.svg), redrawn in this PR**
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **FR-CN-05 → `test_a_saved_template_loads_back_with_identical_values`;
  FR-CN-06 → `test_a_corrupt_library_is_reported_and_left_unchanged`**
- Not applicable: **architectural pattern (unchanged), database (a JSON file, above), data
  processing (unchanged), state management (stateless module), Level 0 DFD, Level 1 DFD
  (unchanged, local state like `filepaths.json`), backend API (none), test coverage (no coverage
  tool)**.

#### Review and design

- When I reviewed the **generated `load_templates`**, I noticed **it let an `OSError` escape, which
  would stop brachify starting once the Channels tab reads the library**. Therefore, I did **turn
  read and write `OSError`s into `NeedleTemplateError`, with two tests**.
- The PR does not contain any temporary workaround because **the module is complete, and only
  its GUI caller is still to come**.
- The PR only contains small functions that are **8, 12 and 9 (`make_template`, `load_templates`,
  `save_template`), and at most 14 in the tests** long.
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
- This work is written in **`src/settings/needle_templates.py`** because **it is settings data from
  `~/brachify`, beside `values.py`, with no Qt**.
- This work belongs in **3 Channels** in the DFD because **a template sets a needle's bore there,
  through the next PR**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **a round trip and a
  replace by name (91 passed)** passed.
- I wrote tests to cover abnormal situations involving **no file yet, an unreadable path and an
  unwritable folder** and they passed.
- I checked that these negative cases involving **a blank name, 0.2 mm, NaN, a corrupt file and
  four malformed libraries** failed as expected.
- When I reviewed the **generated `test_a_library_with_a_malformed_entry_is_rejected`**, I noticed
  **its `entries: object` parameter, which anti-slop's `no-object-parameters` warns on**.
  Therefore, I did **type it as the `LibraryJson` alias**.
- Among these tests, **all 15 cases in `test_needle_templates.py`** are unit tests and integration
  tests are not required because **the module has no Qt or app dependency**.
- These tests are included in the directory **`tests/settings/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (91
  passed), `build.py --check` and `session-start.sh` (exit 0)**.
