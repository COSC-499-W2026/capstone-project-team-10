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
  **`test_loading_a_plan_enables_every_channel_again` (68 passed)** passed.
- I checked that these negative cases involving **the test on `main` and with the fix removed
  (`assert not True`)** failed as expected.
- Among these tests, **none** are unit tests and **`test_loading_a_plan_enables_every_channel_again`**
  is an integration test.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (68
  passed, screenshot 1), `build.py --check` and `session-start.sh` (exit 0), and brachify run on
  macOS through its buttons, Ex2 imported after Ex1 (screenshot 2)**.

  ![1, python -m pytest on fix/disabled-channels-on-import at 3db7981, 68 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/c949d87ca07efff9cc1782c9d7f3956ef015de5c/docs/logs/ahab/screenshots/week-6/pr-43-1-pytest-68-passed.png)

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
- The PR only contains small functions that are **7, 7, 4 and 2 (the four model methods), and at
  most 29 in the tests** long.
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
- The review by **Ariq** identified **that clearing an own diameter fell back to the startup
  width, not the live config default, and that an unknown label could leave a phantom
  override**. Therefore, I did **clear to `NeedleChannel.default_diameter()`, look the channel
  up before storing, and add a test for each**.
- This work is written in **`channels_model.py`, with the minimum in `settings/defaults.py`**
  because **the model owns channel state, and the template library shares the minimum**.
- This work belongs in **3 Channels** in the DFD because **it sets each needle solid's width**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **Apply keeping an
  own diameter, and clearing it (80 passed)** passed.
- I wrote tests to cover abnormal situations involving **a new plan loaded over own diameters,
  a config import before clearing, and an unknown or unselected label** and they passed.
- I checked that these negative cases involving **0.2 mm and NaN** failed as expected.
- When I reviewed the **generated `test_channel_keeps_its_own_diameter_when_channels_diameter_is_applied`**,
  I noticed **it used `monkeypatch.setattr`, which anti-slop warns on**. Therefore, I did **restore
  the live settings in `finally` instead**.
- Among these tests, **none** are unit tests and **all six** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (80
  passed, screenshot 1), `build.py --check` and `session-start.sh` (exit 0)**.

  ![1, python -m pytest on feat/channel-own-diameter at 9fd84a9, 80 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/144974714611352ba317c6659ea0bf11161f0b2d/docs/logs/ahab/screenshots/week-6/pr-59-1-pytest-80-passed.png)

### For PR #**83**

- As part of requirement **FR-CN-05, save needle designs as templates, with FR-CN-06's corrupted
  file case**, the user needs to do **save a needle type's diameter under a name and get the same
  width back later**.
- Therefore, I implemented/generated code so that **physicists' templates are kept in
  `~/brachify/needle_templates.json`, validated and never overwritten when unreadable**.

#### Data Modeling and Integrity

- This data **`NeedleTemplate`** is modeled as **a frozen dataclass of `name` and `diameter_mm`**
  because **a template must not change once validated**. We considered alternative models such as
  **a raw `dict`, which anti-slop forbids**.
- This data **`needle_templates.json`** uses the input validation to ensure it adheres to **text names that are unique and
  non-blank, and number diameters (not booleans) that are finite of at least 0.3 mm**.
- This data **`needle_templates.json`** may be vulnerable to **a corrupt or hand-edited file**.
  Therefore, it uses a security-based sanitization by **refusing the whole file without
  overwriting it**. We considered alternative security solutions such as **skipping bad entries,
  which mislabels widths**.
- Not applicable: **privacy sanitization (no patient data), encryption (nothing sensitive),
  access controls (one local user)**.

#### Backend

- The system architecture diagram consists of the following major components: **External, Presentation, Application state, Domain services, Libraries and Local storage**. This
  structure has low coupling because **the module imports only `settings.defaults`**. This
  structure has high cohesion because **templates are handled in one module**. This design is scalable because **dead space for FR-CN-19 is one more field**.

  **[System architecture (SVG), redrawn to name `needle_templates`](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/b9109a1a59e8aeac3c5de1f207a598a2b7debe33/docs/architecture/diagrams/system-architecture.svg)**
- The Level 0 DFD consists of the following major components: **medical physicist, treatment
  planning system, brachify and printer or CAD**. **Templates stay inside brachify, in local storage**

  **[DFD level 0 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587691980185009f292ce7454c352c9f1de4/docs/architecture/diagrams/existing-framework/dfd-0.svg)**
- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem and Export**. **Channels saves and
  applies templates in the next PR**. **An unreadable library raises `NeedleTemplateError`**.

  **[DFD level 1 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587691980185009f292ce7454c352c9f1de4/docs/architecture/diagrams/existing-framework/dfd-1.svg)**
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **FR-CN-05 → `test_a_saved_template_loads_back_with_identical_values`;
  FR-CN-06 → `test_a_corrupt_library_is_reported_and_left_unchanged`**
- Not applicable: **architectural pattern (unchanged), database (a JSON file, above), data
  processing (unchanged), state management (stateless module), backend API (none), test coverage
  (no coverage tool)**.

#### Review and design

- When I reviewed the **generated `load_templates`**, I noticed **an `OSError` could escape and stop
  brachify starting**. Therefore, I did **raise `NeedleTemplateError` instead**.
- When Writable04 reviewed this PR, they found **a failed save could leave truncated JSON, `{}` and a
  `null` name were accepted, and `10**400` raised `OverflowError`**. Therefore, I did **save through a
  temporary file and `os.replace`, check the JSON types, and raise `NeedleTemplateError`**. The eight
  new cases **failed before the fix**.
- The PR does not contain any temporary workaround because **only the GUI caller is still to
  come**.
- The PR only contains small functions that are **8, 12 and 9, and at most 14 in the tests** long.
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
- This work is written in **`src/settings/needle_templates.py`** because **it is settings data with
  no Qt**.
- This work belongs in **3 Channels** in the DFD because **a template sets a needle's bore there**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **a round trip and a
  replace by name (164 passed)** passed.
- I wrote tests to cover abnormal situations involving **no file, an unreadable path and an
  unwritable folder** and they passed.
- I checked that these negative cases involving **blank names, 0.2 mm, NaN and corrupt or
  malformed files** failed as expected.
- When I reviewed the **generated `test_a_library_with_a_malformed_entry_is_rejected`**, I noticed
  **an `object` parameter, which anti-slop warns on**. Therefore, I did **type it as `LibraryJson`**.
- Among these tests, **all 23 cases** are unit tests and integration tests are not required because
  **the module has no Qt or app dependency**.
- These tests are included in the directory **`tests/settings/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (164
  passed), `build.py --check` and `session-start.sh` (exit 0)**.

### For PR #**84**

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
  shown diameter (170 passed)** passed.
- I wrote tests to cover abnormal situations involving **the default window size and no
  selection** and they passed.
- I checked that these negative cases involving **0.1 mm typed into the box** failed as expected.
- When I reviewed the **generated `test_selecting_a_channel_shows_its_current_diameter`**, I
  noticed **it passed before the view was wired**. Therefore, I did **type an unapplied value
  first**.
- Among these tests, **none** are unit tests and **all six** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (170
  passed), `build.py --check` and `session-start.sh` (exit 0), and brachify run on
  macOS through its buttons, with Ex1 before this PR was split out (screenshot 1)**.

  ![1, Ex1 in brachify, Applicator4 given 3.5 mm by Apply to Channel and kept after Channels Diameter 2.0](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/e6f24e0b226af77974c9cfa765f539fe1245996c/docs/logs/ahab/screenshots/week-6/pr-60-2-selected-channel-group.png)

### For PR #**85**

- As part of requirement **FR-CN-03 and FR-CN-16 (interface), show each needle's status,
  disabled included**, the user needs to do **see on the Channels tab which needles have their own
  diameter, are disabled or are the tandem**.
- Therefore, I implemented/generated code so that **physicists see each needle's status as a colour,
  a font cue and a tooltip**.

#### Backend

- The system architecture diagram consists of the following major components: **External, Presentation, Application state, Domain services, Libraries and Local storage**. This
  structure has low coupling because **the view only draws `channel_status`**. This structure has
  high cohesion because **the status order lives in the model**. This design is scalable because
  **a new status is one enum member and one style**.

  **[System architecture (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587691980185009f292ce7454c352c9f1de4/docs/architecture/diagrams/system-architecture.svg)**
- The Level 0 DFD consists of the following major components: **medical physicist, treatment
  planning system, brachify and printer or CAD**. **Statuses stay inside brachify**

  **[DFD level 0 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587691980185009f292ce7454c352c9f1de4/docs/architecture/diagrams/existing-framework/dfd-0.svg)**
- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem and Export**. **A disabled
  needle's row reads disabled, and Export leaves it out**. **A status is never stored, so it
  cannot go stale**.

  **[DFD level 1 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587691980185009f292ce7454c352c9f1de4/docs/architecture/diagrams/existing-framework/dfd-1.svg)**
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **FR-CN-03 (interface) → `test_channel_with_its_own_diameter_is_bold_on_amber_in_the_list`;
  FR-CN-16 (interface) → `test_a_disabled_channel_reads_disabled_and_stays_in_the_list`**
- Not applicable: **architectural pattern (unchanged), database (none), data processing
  (unchanged), state management (computed, not stored), backend API (none), test coverage (no
  coverage tool)**.

#### Frontend

- The frontend is designed using **PySide6 and Qt Designer** with design components for **one
  `ChannelRowStyle` per status**. Therefore, changing the design of **one status's style** will
  automatically change the look and feel of all instances of that component throughout the system.
  Changes to the content will not affect the design because **row text stays the channel label**.
- The frontend adopts accessibility principle **WCAG 2.1 SC 1.4.1 Use of Color**. The aspects that
  demonstrate this principle in the system include **a bold or italic cue for each colour, a
  legend and a tooltip (screenshot 1)**.

  ![1, Ex2 in brachify, Applicator4 bold on amber, Applicator7 italic on grey, Tandem bold italic on blue, with the legend](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/e6f24e0b226af77974c9cfa765f539fe1245996c/docs/logs/ahab/screenshots/week-6/pr-62-2-status-colours.png)

- Not applicable: **data caching (no new data), restricted pages (no logins), usability
  evaluation (none run), traceability matrix (under Backend), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **first plan for this issue**, I noticed **disabled needles, which are not
  cut, still looked enabled**. Therefore, I did **add disabled and tandem statuses**.
- The PR does not contain any temporary workaround because **3D colour is left for FR-CN-04, as
  #46 records**.
- The PR only contains small functions that are **5, 5 and 12, and at most 20 in the tests** long.
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
- This work is written in **`channels_model.py` and `channels_view.py`** because **the model
  decides the status and the view draws it**.
- This work belongs in **3 Channels** in the DFD because **the statuses come from that tab's
  state**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **an own diameter
  marked and a cleared one unmarked (174 passed)** passed.
- I wrote tests to cover abnormal situations involving **a disabled channel with its own diameter,
  and the tandem** and they passed.
- I checked that these negative cases involving **four deliberate breaks** failed as expected.
- When I reviewed the **generated `test_clearing_a_channels_own_diameter_removes_its_mark`**, I
  noticed **it passed with no restyling at all**. Therefore, I did **assert the mark before the
  clear**.
- Among these tests, **none** are unit tests and **all four** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (174
  passed), `build.py --check` and `session-start.sh` (exit 0)**.

### For PR #**74**

- As part of requirement **the course's Part A receipts, which ask for a screenshot as proof of
  each regression run**, the user needs to do **open #84, #85 and #63 and see the running app
  behind each receipt, and #59's test run**.
- Therefore, I implemented/generated code so that **graders see brachify on macOS for #84, #85 (the WCAG 1.4.1
  receipt) and #63, and `python -m pytest` for #59**.

#### Review and design

- When I reviewed the **first captures** for this functionality, I noticed **3D-engine messages
  pushed the pytest result off screen, and one capture took the wrong window**. Therefore, I did
  **filter those messages in the shown command, and capture brachify by its window number**.
- I did **open each image, and `git diff --name-only main...HEAD` (four PNGs and this log)** to
  ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/logs/ahab/screenshots/week-6/`** because **the log README keeps
  screenshots by student and week**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **each image showing
  its feature, or for #59 its branch, commit and pass count (80 passed)** passed.
- This new test PR did not break anything else in the system because **no file outside
  `docs/logs/` changed (`git diff --name-only`), and `session-start.sh` exits 0**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration
  tests, test directory (no code, the checks are shell commands)**.
