# Week 8, Ariq

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

## Stack #174 to #179, at a glance

Six stacked PRs that move the tandem channel choice to the Tandem tab and stop a tandem channel
being exported without its hole. Each PR is based on the one above it and closes its own issue.
A row's counts are **that PR's own diff only**, as GitHub shows it against its parent.

| PR | On | Closes | What this PR adds | Own diff (files, lines) | New tests | Suite after |
|---|---|---|---|---|---|---|
| [#174](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/174) | `main` | #168 | Clearing the tandem channel, the Ex2 fixture | 8, +193/−14 | 3 | 321 |
| [#175](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/175) | #174 | #169 | Tandem Channel box on the Tandem tab | 9, +454/−9 | 9 | 330 |
| [#176](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/176) | #175 | #170 | Channels list without the tandem channel | 9, +118/−25 | 3 (1 replaced) | 332 |
| [#177](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/177) | #176 | #171 | *Set as Tandem* removed from the Channels tab | 9, +68/−130 | 1 (replacing 1) | 332 |

The suite had 318 tests on `main` before #174 (`1f34b40`).

### Shared by every PR in this stack

Stated once here instead of in each section.

- **Code quality checklist.** For each PR, I did **`anti_slop review --base <parent branch>` (no findings) and a read of that PR's own diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- **Regression checks.** Every PR's regression receipt also includes **`build.py --check` and `session-start.sh`, both exit 0, and an end-to-end run of the real window on the top of the stack, #179, with Ex2, then Ex1, then a third Varian plan whose tandem is channel 1**. Each section gives only its own `python -m pytest` result.
- **Not applicable in every PR.** **Encryption and access controls (no stored secrets, no user roles), database (none), restricted pages (no logins), usability evaluation (none run), backend API (none), test coverage (no coverage tool)**.

### For PR #**174** (1 of 6, on `main`)

- As part of requirement **issue #168, a plan with no tandem channel**, the user needs to do **clear a plan's tandem channel so that no channel is the tandem**.
- Therefore, I implemented/generated code so that **clinicians can clear the tandem channel without an error, the old tandem channel is cut as a needle again, and the tandem keeps its rotation**.

#### Backend

- The system uses **the existing Qt model and signal pattern, `ChannelsModel.set_tandem` emitting `tandem_changed` to `TandemModel.set_tandem_channel`** because **the models own the tandem state and every tab calls them**. Benefits for using this pattern include **#175's Tandem tab clears the tandem with one call**. Possible risks include **Qt prints an exception raised in a slot instead of raising it, so a broken slot fails silently**.
  - To mitigate **a silent slot failure**, we implemented **tests that read the rotation the slot sets, not only that nothing raised**.
- The system architecture diagram consists of the following major components: **views, QObject models, domain services, libraries and local storage**. This structure has low coupling because **only an existing signal's handling changed**. This structure has high cohesion because **`ChannelsModel` owns which channel is the tandem and `TandemModel` owns its rotation**. This design is scalable because **a tandem built from the plan's path could reuse the same signal**.

  **[System architecture, unchanged](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/1f34b40bcfbab59fc662d20e25a682f7b33b47ab/docs/architecture/diagrams/system-architecture.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **#168: `tests/views/test_tandem_channel.py`, 3 tests**
- Not applicable: **data processing, state management, Level 0 DFD, Level 1 DFD (unchanged)**.

#### Review and design

- When I reviewed the **generated `set_tandem_channel`** for this functionality, I noticed **it dropped the `rotation` local that the branch for a channel named Tandem still used, so importing Ex2 raised `NameError` in the slot and left the tandem at 0°**. Therefore, I did **set the plan rotation from `self.rotation` and add the Ex2 import test, which failed at 0.0 first**.
- The PR does not contain any temporary workaround because **`set_tandem(None)` is the model's own clear, not a view-side patch**.
- The PR only contains small functions that are **8 and 14 lines (models) and 14 to 16 lines (tests)** long.
- Code quality checklist: **see Shared**.
- This work is written in **`channels_model.py` and `tandem_model.py`** because **each model owns its half of the tandem state**.
- This work belongs in **Channels and Tandem** in the DFD because **the tandem channel flows from Channels to Tandem**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_clearing_the_tandem_channel_makes_it_a_needle_again`, `test_importing_a_plan_with_a_tandem_channel_aims_the_tandem_along_it` (3 new; 3 in the file; screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **clearing after a needle, Applicator12, was the tandem, keeping its 208.37° rotation** and they passed.
- I checked that these negative cases involving **the code before the fix (`[None] == []`, rotation 0.0, and 0.0 instead of 359.996 at import)** failed as expected.
- Among these tests, **none** are unit tests and **all 3** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest`, 321 passed (318 on `main`, screenshot 1)**.

  ![1, python -m pytest on fix/tandem-channel-none, 3 passed in test_tandem_channel.py and 321 passed in the whole suite](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/40e32d755ba1d497b71cca7ccef0cc454e03386b/docs/logs/ariq/screenshots/week-8/pr-174-1-pytest-321-passed.png)

### For PR #**175** (2 of 6, on #174)

- As part of requirement **issue #169, choose the tandem channel where the tandem is set up**, the user needs to do **open the Tandem tab, pick which plan channel is the tandem, or None, and be told if it does not run along the axis**.
- Therefore, I implemented/generated code so that **clinicians choose, change or clear the tandem channel on the Tandem tab, and are warned about an off-axis or moved channel**.

#### Frontend

- The frontend uses **no cache: the box is refilled from `ChannelsModel` on every `values_changed`** because **an import or the Channels tab can also change the tandem channel**. Benefits for using this pattern include **the box never shows a stale channel**. Possible risks include **a refill re-applying a choice**.
  - To mitigate **a refill re-applying a choice**, we implemented **a `QSignalBlocker` around the refill and a connection to `activated`, which only a click emits**.
- The frontend is designed using **Qt Designer `.ui` files and PySide6** with design components for **a label and combo box row and a word-wrapped warning line, styled like the tab's other rows**. Therefore, changing the design of **the row in `tandem_view.ui`** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **the view fills the box and the warning at runtime**.
- The frontend adopts accessibility principle **WCAG 1.4.1, Use of Color: a problem is stated in words, never shown only by colour**. The aspects that demonstrate this principle in the system include **the warning sentence naming the channel and its 7.2 mm distance (screenshot 1)**.

  ![1, the real Tandem tab on Ex2 with Applicator7 chosen and the 7.2 mm warning, and python -m pytest on feat/tandem-channel-choice, 9 passed in test_tandem_channel_choice.py and 330 in the suite](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/340d2b46208c673b262a40684a39247ff8f5ff7b/docs/logs/ariq/screenshots/week-8/pr-175-1-tandem-channel-box.png)
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **#169: `tests/views/test_tandem_channel_choice.py`, 9 tests**

#### Review and design

- When I reviewed the **Tandem tab at the default 770 by 472 window** for this functionality, I noticed **the new row squeezed the Generate spin boxes from 16 to 14 px, and a scroll area alone did not help, because the `.ui` caps the sub-tabs at a 290 px minimum shorter than the Generate page**. Therefore, I did **add the scroll area and raise that minimum to the sub-tabs' size hint, guarded by a height test**.
- The PR does not contain any temporary workaround because **the scroll area is the Cylinder tab's tested fix (§7.12)**.
- The PR only contains small functions that are **2 to 15 lines (new) and 4 to 22 lines (tests)** long. The inherited `__init__` grew to 34 lines and was not split.
- Code quality checklist: **see Shared**.
- This work is written in **`tandem_view.py` and `tandem_view.ui`** because **the Tandem tab owns the tandem's settings**.
- This work belongs in **Tandem** in the DFD because **the tandem channel is now chosen there**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_choosing_a_channel_makes_it_the_tandem_and_aims_the_tandem_at_it`, `test_choosing_none_clears_the_tandem_channel` (9 new; 9 in the file; screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **No in the rotation warning, a moved channel, Applicator7 7.2 mm off the axis, and the default window's height** and they passed.
- I checked that these negative cases involving **four deliberate breaks (no refresh, the answer ignored, a 100 mm limit, the 290 px minimum kept)** failed as expected.
- When I reviewed the **`test_generate_spin_boxes_keep_their_height_in_the_default_window`**, I noticed **it read 15 px with the fix in place, because grabbing only the spin box never laid the tab out**. Therefore, I did **grab the whole tab first, and confirmed it still fails without the fix**.
- Among these tests, **none** are unit tests and **all 9** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest`, 330 passed (321 after #174, screenshot 1)**.

### For PR #**176** (3 of 6, on #175)

- As part of requirement **issue #170, keep the tandem channel off the needle list**, the user needs to do **see only needles on the Channels tab, and get the tandem channel back as a needle once it stops being the tandem**.
- Therefore, I implemented/generated code so that **clinicians never see or enable the tandem channel as a needle on the Channels tab**.

#### Backend

- The system uses **a model guard behind the view filter** because **hiding the row alone would leave `toggle_channel_enabled` able to cut the tandem as a needle**. Benefits for using this pattern include **no caller can enable it, not only the list**. Possible risks include **a caller that toggles without checking**.
  - To mitigate **an unchecked caller**, we implemented **a `ValueError`, tested directly on the model**.
- The system architecture diagram consists of the following major components: **as in #174**. This structure has low coupling because **the view listens to `tandem_changed`, which the model already emitted**. This structure has high cohesion because **the model decides what is the tandem and the view only shows the rest**. This design is scalable because **the same filter hides any channel the model marks**.

  **[System architecture, unchanged](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/1f34b40bcfbab59fc662d20e25a682f7b33b47ab/docs/architecture/diagrams/system-architecture.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **#170: three tests in `tests/views/test_channel_status_colours.py`**
- Not applicable: **data processing, state management, Level 0 DFD, Level 1 DFD (unchanged)**.

#### Frontend

- The frontend is designed using **Qt Designer `.ui` files and PySide6** with design components for **the Channels list and its legend**. Therefore, changing the design of **a status's row style in `STATUS_ROW_STYLES`** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **rows are styled by status, not by label**.
- The frontend adopts accessibility principle **WCAG 1.4.1, Use of Color: each remaining status keeps its own bold and italic pair**. The aspects that demonstrate this principle in the system include **the legend naming only the styles that can appear (screenshot 1)**.

  ![1, the real Channels tab on Ex2 after choosing None, Tandem back as a plain needle row, and python -m pytest on feat/channels-list-hides-tandem, 6 passed in test_channel_status_colours.py and 332 in the suite](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/c1590b218f36f4fb16eb0eebc94ecb4b673a77dd/docs/logs/ariq/screenshots/week-8/pr-176-1-channels-list.png)
- Not applicable: **data caching (the list reads the model)**.

#### Review and design

- When I reviewed the **generated list change** for this functionality, I noticed **the legend still described a bold italic tandem row that no longer appears**. Therefore, I did **remove the sentence, asserted by the Ex2 list test**.
- The PR does not contain any temporary workaround because **the row is left out by the model's own `is_channel_tandem`**.
- The PR only contains small functions that are **10 to 18 lines (changed) and 4 to 26 lines (tests)** long.
- Code quality checklist: **see Shared**.
- This work is written in **`channels_view.py` and `channels_model.py`** because **the Channels tab and its model own the needle list**.
- This work belongs in **Channels** in the DFD because **it changes which channels are offered as needles**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_ex2_lists_every_channel_except_its_tandem`, `test_the_tandem_channel_leaves_the_list_and_comes_back_as_a_needle` (3 new; 6 in the file; screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **a needle made the tandem and cleared again, and Enable pressed on the tandem** and they passed.
- I checked that these negative cases involving **three deliberate breaks (the row listed, Enable allowed, no rebuild) and the old legend** failed as expected.
- Among these tests, **none** are unit tests and **all 3** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest`, 332 passed (330 after #175, screenshot 1)**.

### For PR #**177** (4 of 6, on #176)

- As part of requirement **issue #171, one place to set the tandem channel**, the user needs to do **set the tandem channel only on the Tandem tab**.
- Therefore, I implemented/generated code so that **clinicians can no longer change the tandem from the Channels tab, where its effect was hidden**.

#### Frontend

- The frontend is designed using **Qt Designer `.ui` files and PySide6** with design components for **the Channels tab's buttons**. Therefore, changing the design of **the button style in `channels_view.ui`** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **removing a button leaves the others' style alone**.
- Not applicable: **data caching (nothing cached), accessibility (no new control)**.

#### Review and design

- When I reviewed the **generated removal** for this functionality, I noticed **`QMessageBox` was left imported and unused once `action_set_tandem` went**. Therefore, I did **remove the import**.
- The PR does not contain any temporary workaround because **the button is removed, not hidden**.
- The PR only contains small functions that are **20 lines (the new test)** long. `action_update_settings`, 35 lines and inherited, got shorter.
- Code quality checklist: **see Shared**.
- This work is written in **`channels_view.py` and `channels_view.ui`** because **that is where the button lived**.
- This work belongs in **Channels** in the DFD because **the Channels process no longer chooses the tandem channel**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_no_channels_tab_button_makes_a_channel_the_tandem` (1 new, replacing the button's test; 25 in the file; screenshot 1)** passed.
- I checked that these negative cases involving **the button still present** failed as expected.
- Among these tests, **none** are unit tests and **the 1 new test** is an integration test.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest`, 332 passed (332 after #176, one test replaced; screenshot 1)**.

  ![1, the real Channels tab on Ex2 with Applicator7 selected and no Set as Tandem button, and python -m pytest on feat/remove-set-as-tandem-button, 25 passed in test_move_channel.py and 332 in the suite](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/800d2b4655f8028644a0c7a11936253308a15870/docs/logs/ariq/screenshots/week-8/pr-177-1-channels-tab.png)
- Not applicable: **abnormal cases (a removal has no edge case)**.
