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
  passed), `build.py --check` and `session-start.sh` (exit 0), and [author: run the app, disable
  Applicator4 in Ex1, import Ex2, and confirm Applicator4 is drawn and cut in Export]**.
- Not applicable: **abnormal cases (one path), generated-test review (no problem found)**.
