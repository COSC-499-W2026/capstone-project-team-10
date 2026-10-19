

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
  shown diameter (147 passed)** passed.
- I wrote tests to cover abnormal situations involving **the default window size and no
  selection** and they passed.
- I checked that these negative cases involving **0.1 mm typed into the box** failed as expected.
- When I reviewed the **generated `test_selecting_a_channel_shows_its_current_diameter`**, I
  noticed **it passed before the view was wired**. Therefore, I did **type an unapplied value
  first**.
- Among these tests, **none** are unit tests and **all six** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (147
  passed), `build.py --check` and `session-start.sh` (exit 0), and brachify run on
  macOS through its buttons, with Ex1 before this PR was split out (screenshot 1)**.

  ![1, Ex1 in brachify, Applicator4 given 3.5 mm by Apply to Channel and kept after Channels Diameter 2.0](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/e6f24e0b226af77974c9cfa765f539fe1245996c/docs/logs/ahab/screenshots/week-6/pr-60-2-selected-channel-group.png)
