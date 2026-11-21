# Week 11, Ahab

_Individual log, one section per merged PR. See [docs/logs/README.md](../README.md)._

## Stack #280, at a glance

| PR | On | Closes | Adds | Own diff | New tests | Suite after |
|---|---|---|---|---|---|---|
| [#280](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/280) | main | #229 | Alt+arrow and Alt+Page keys nudge the selected applicator from the channel list | 7 files, 345 lines | 28 (28 in the file) | 654 passed, 1 env failure |

### Shared by every PR in this stack

- The code quality checklist, for every PR in the stack: **no hardcoded values, duplicate code, dead code, unnecessary function calls, excessive conditional logic, deep nesting, high cyclomatic complexity, or classes, modules and functions with many unrelated responsibilities, checked with `anti_slop review --base <parent branch> src tests utils` (no findings) and a line-by-line read of each diff**.
- Checks run on every PR: **`python docs/architecture/build.py --check` and `sh .claude/hooks/session-start.sh`, both exit 0**.
- Not applicable to any PR in the stack: **Data Modeling and Integrity and Backend (no model, data or file format changed); data caching (no backend), restricted pages (no logins), usability evaluation (none run), test coverage (no tool)**.

### For PR #**280** (1 of 3, on main)

- As part of requirement **FR-CN-02, move a needle**, the user needs to do **select an applicator in the Channels list, press Alt (Option) with an arrow or Page key to nudge it by 1 mm, or 0.1 mm with Shift, and watch the 3D view follow**.
- Therefore, I implemented/generated code so that **medical physicists can line a needle up by eye from the keyboard, with each nudge added to the popup's move and kept to its ±300 mm**.

#### Frontend

- The frontend is designed using **PySide6, with a `NudgeKeys` event filter on the channel list** with design components for **the list, the 3D view and the Move popup**. Therefore, changing the design of **the key table in `nudge_keys.py`** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **the filter only turns keys into steps and `ChannelsView.nudge_selected` applies them**.
- The frontend adopts accessibility principle **WCAG 2.1.1 Keyboard, every function works from a keyboard**. The aspects that demonstrate this principle in the system include **a move needs no mouse: Alt+arrows nudge, the popup shows the total (screenshots 1 to 3)**.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-02 → `test_alt_arrow_in_the_list_moves_the_selected_channel_and_marks_its_row`, `test_a_nudge_adds_to_the_popups_move_and_the_popup_shows_the_total`**
- Not applicable: **see Shared**.

#### Review and design

- When I reviewed the **`nudge_step` keypad mask** for this functionality, I noticed **a mutation that removed it failed no test, because the modifiers are tested with `&`, so the mask was dead code**. Therefore, I did **delete it and keep the macOS keypad case in the test table**.
- The PR does not contain any temporary workaround because **the keys go through the same `move_channel` as the popup**.
- The PR only contains small functions that are **at most 8 lines (`nudge_step`, `nudge_selected`)**.
- Code quality checklist: **see Shared**.
- This work is written in **new `src/windows/views/nudge_keys.py` and `channels_view.py`** because **`channels_view.py` is near 500 lines, and the key table is pure and testable without Qt widgets**.
- This work belongs in **Channels** in the DFD because **it moves a needle the way the popup does**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_each_nudge_key_gives_its_axis_and_step` and `test_alt_arrow_in_the_list_moves_the_selected_channel_and_marks_its_row` (28 new; 28 in the file)** passed.
- I wrote tests to cover abnormal situations involving **a nudge past ±300 mm, a press at 300 mm (no rebuild), and a nudge out of the cylinder (tooltip warning)** and they passed.
- I checked that these negative cases involving **four deliberate breaks (no limit check, no tandem check, no rounding, no filter installed)** failed as expected.
- Among these tests, **the 22 `nudge_step` and `nudged` cases** are unit tests and **the 6 window tests** are integration tests.
- These tests are included in the directory **`tests/views/test_nudge_channel.py`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (654 passed, 1 failed `test_pytest_xdist_is_installed_in_this_environment`, as pytest-xdist is not in my conda env; 627 tests on main) and a driven run of the real window on macOS: Ex1, Applicator3, ten Alt+Left, Alt+Shift+Up and Alt+Page Up sent in-process with `QTest` gave a move of -10, 0.1, 1 mm (screenshots 1 to 4)**.

  ![1 to 4, the nudged needle, the popup at the total, the underlined row, and pytest](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/0f6006e283bb734150a7c71994763dd42b94b0c7/docs/logs/ahab/screenshots/week-11/pr-229a-nudge.png)
