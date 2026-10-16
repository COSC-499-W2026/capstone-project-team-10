# Week 6, Ahab

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**43**

- As part of requirement **FR-CN-20, a disabled needle stays in the plan and is left out of the
  mesh**, the user needs to do **disable a needle in one plan, import the next patient's plan, and
  export a cylinder with a hole for every needle that plan has enabled**.
- Therefore, I implemented/generated code so that **physicists importing a plan get every channel
  enabled again, apart from the plan's tandem channel, so no needle hole goes missing unseen**.

#### Backend

- The system adopts a **stateful** approach to state management because **`ChannelsModel` must
  keep a clinician's disabled channels between edits on the Channels tab**. This method is done by
  **holding them in `disabled_channels`, now emptied by `load_data` on every import**. Benefits
  for using this approach include **one owner for which needles are cut, read by Export and the
  PDF**. Possible risks include **state a model forgets to reset carrying into the next patient's
  plan (§7.10)**.
  - To mitigate **disabled channels carrying across imports**, we implemented **`self.disabled_channels = []`
    in `load_data`, before the loop where `set_tandem` disables a plan's tandem channel**.
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **FR-CN-20 → `test_loading_a_plan_enables_every_channel_again`**
- Not applicable: **architectural pattern, architecture diagram, Level 0 DFD, Level 1 DFD
  (unchanged, `build.py --check` exit 0), database (none), data processing (unchanged), backend
  API (none), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **`ChannelsModel.load_data`** for this functionality, I noticed **it reset
  the selection and channels but not `disabled_channels`. Run offscreen, Applicator4 disabled in
  Ex1 stayed disabled in Ex2 and out of `get_visible_channels()`**. Therefore, I did **empty
  `disabled_channels` in `load_data` and record the bug as fixed in §7.10**.
- When I reviewed the **test inventories in `AGENTS.md` and `tests/README.md`**, I noticed **they
  listed what each test file checks, so every new test made them stale**. Therefore, I did **point
  both at `tests/README.md` and §8.2**.
- The PR does not contain any temporary workaround because **the reset sits beside the other
  per-plan resets in `load_data`**.
- The PR only contains small functions that are **28 (`load_data`, 1 line added) and 16 (the
  test)** long.
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
- This work is written in **`src/windows/models/channels_model.py`** because **the model owns
  which channels are disabled**.
- This work belongs in **3 Channels** in the DFD because **it decides which needle solids reach
  the Shapes store**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_loading_a_plan_enables_every_channel_again` (65 passed)** passed.
- I checked that these negative cases involving **the test on `main` and with the fix line removed
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

### For PR #**60**

- As part of requirement **FR-CN-08, with FR-CN-02 (interface), edit controls disabled with nothing
  selected**, the user needs to do **select a needle on the Channels tab, type its diameter, press
  Apply to Channel, and later press Use Channels Diameter to undo it**.
- Therefore, I implemented/generated code so that **physicists can give one needle its own
  diameter on the Channels tab, see each selected needle's width, and undo it**.

#### Frontend

- The frontend is designed using **PySide6 and Qt Designer `.ui` files** with design components
  for **the Selected Channel group, whose one stylesheet styles all its buttons**. Therefore,
  changing the design of **that stylesheet** will automatically change the look and feel of all
  instances of that component throughout the system. Changes to the content will not affect the
  design because **the values come from `ChannelsModel` through `action_update_settings`**.
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **FR-CN-08 → `test_apply_to_channel_changes_only_the_selected_channel`;
  FR-CN-02 (interface) → `test_selected_channel_controls_are_disabled_with_no_channel_selected`**
- Not applicable: **data caching (no new data), restricted pages (no logins), usability
  evaluation (none run), accessibility (no new principle), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated Selected Channel group**, I noticed **it squeezed the four spin
  boxes above it to 9 px in the default 770 × 472 window**. Therefore, I did **put the tab in a
  scroll area, with a test for it**.
- The PR does not contain any temporary workaround because **the scroll area is a standard Qt
  layout, recorded in §5.6**.
- The PR only contains small functions that are **4 and 3 (the two actions), 38 and 27
  (`action_update_settings` and `__init__`, 4 and 3 lines added), and at most 20 in the tests**
  long.
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
- This work is written in **`channels_view.py` and `channels_view.ui`** because **the view owns
  its widgets and calls `ChannelsModel` for every change**.
- This work belongs in **3 Channels** in the DFD because **the per-needle bore enters there**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **apply, use channels
  diameter and the shown diameter (3 tests, 76 passed)** passed.
- I wrote tests to cover abnormal situations involving **the default window
  (`test_channels_settings_keep_their_height_in_the_default_window`) and no selection** and they
  passed.
- I checked that these negative cases involving **0.1 mm typed into the box** failed as expected.
- When I reviewed the **generated `test_selecting_a_channel_shows_its_current_diameter`**, I
  noticed **it passed before the view was wired**. Therefore, I did **type an unapplied 1.0 first
  and assert the box shows the channel's 3.1**.
- Among these tests, **none** are unit tests and **all six** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (76
  passed), `build.py --check` and `session-start.sh` (exit 0)**.
