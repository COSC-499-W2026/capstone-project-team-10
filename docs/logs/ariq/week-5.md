# Week 5, Ariq

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**19**

- As part of requirement **FR-CN-02 (Milestone 2), edit the selected needle**, the user needs
  to do **select a channel in the Channels tab, switch tabs, come back, and see the list and the
  viewport agree that none is selected**.
- Therefore, I implemented/generated code so that **physicists get a Channels list that drops
  its highlight when no channel is selected and reselects on the next click, and every agent
  session reads the repo, code included, before its first reply**.

#### Frontend

- The frontend uses **`ChannelsModel.selected_channels` as the one selection state, mirrored
  into the list by `action_update_settings`** because **the list and the viewport must show the
  same channel**. Benefits for using this pattern include **one source of truth, so leaving the
  tab or clicking empty space clears both**. Possible risks include **clearing the list
  re-entering `action_select_channel` through `currentItemChanged`**.
  - To mitigate **that re-entry**, we implemented **`blockSignals` around `setCurrentRow(-1)`,
    as `create_channels_list` already does**.
- The frontend ensures only authorized users can access restricted pages — **N/A**, brachify
  has no logins or restricted pages.
- The frontend is designed using **PySide6 with Qt Designer `.ui` files** with design
  components for **the five tab views**. Therefore, changing the design of
  **`listwidget_channels` in `channels_view.ui`** will automatically change the look and feel
  of all instances of that component throughout the system. Changes to the content will not
  affect the design because **channel names are added at runtime by `create_channels_list`**.
- The usability evaluation identified the following major problems — **N/A**, no usability
  evaluation was run.
- The frontend adopts accessibility principle — **N/A**, this PR changes selection state only.
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **FR-CN-02 → test PR #20,
  `tests/views/test_channels_view.py`**
- By using a test coverage tool — **N/A**, the repo has no coverage tool.

#### Review and design

- When I reviewed the **generated `action_update_settings` change** for this functionality, I
  did not find any problems with it because **the two tests in test PR #20 fail without it,
  and with `clearSelection()` alone, and pass with it**.
- The PR does not contain any temporary workaround because **the list mirrors the model in the
  method that already syncs the Channels buttons to it**.
- The PR only contains small functions that are **35 (`action_update_settings`, 6 lines
  added)** long.
- I did **`anti_slop review --base main` (no findings) and a read of the 6-line `src/` diff**
  to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/windows/views/channels_view.py`** because **the list widget
  belongs to `ChannelsView`, and `action_update_settings` runs on every `values_changed`**.
- This work belongs in **Channels, DFD level 1** because **it changes how that tab shows the
  selected channel**.

#### Testing receipts

- The functionality works correctly because the happy path tests — **N/A**, the tests are in
  test PR #20.
- I wrote tests to cover abnormal situations — **N/A**, the tests are in test PR #20.
- I checked that these negative cases — **N/A**, the tests are in test PR #20.
- When I reviewed the generated tests — **N/A**, the tests are in test PR #20.
- Among these tests, unit and integration tests — **N/A**, the tests are in test PR #20.
- These tests are included in the directory — **N/A**, the tests are in test PR #20.
- This new test PR did not break anything else in the system because **`python -m pytest` (20
  passed), `build.py --check` and `session-start.sh` (exit 0), and [author: run the app on Ex1,
  repeat the tab switch, and attach a screenshot]**.

### For test PR #**20** written to assess functionality in **#19, clearing the Channels list highlight when no channel is selected**

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_returning_to_channels_tab_shows_no_channel_selected` (22 passed)** passed.
- I wrote tests to cover abnormal situations involving **clicking the channel that was
  current before leaving, which Qt ignores
  (`test_channel_can_be_selected_again_after_returning_to_channels_tab`)** and they passed.
- I checked that these negative cases involving **both tests without the #19 fix, and with
  `clearSelection()` in place of it (2 failed each)** failed as expected.
- When I reviewed the **generated `test_channels_view.py`**, I noticed **it imported
  `classes.app` at the top, fixing `~/brachify` to the real home before the fixture redirected
  `HOME`**. Therefore, I did **move the import into the helper**.
- When I reviewed the **generated `channels_window` fixture**, I noticed **it imported the
  mesh modules before the app existed (`AttributeError` from `BrachyCylinder`'s default
  argument)**. Therefore, I did **create the app first and record the trap in §7.6**.
- When I reviewed the **generated `channels_window` fixture**, I noticed **the full
  `app.gui()` exits 139 without a display**. Therefore, I did **create the canvas without
  `InitDriver()` and record the trap in §7.6**.
- Among these tests, **none** are unit tests and **both tests** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (22
  passed), `anti_slop review` (no findings), `build.py --check` and `session-start.sh` (exit
  0)**.

### For PR #**21**

- As part of requirement **FR-CN-01 (Milestone 2), create cylinders and needles through
  forms**, the user needs to do **open the Channels tab on a Mac in dark mode and click the spin
  box arrows to change channel diameter or dead space**.
- Therefore, I implemented/generated code so that **physicists see black arrows on the four
  Channels spin boxes in any OS colour scheme, with the rest of the app unchanged**.

#### Frontend

- The frontend uses data received from the backend — **N/A**, the PR changes how arrows are
  drawn, not data.
- The frontend ensures only authorized users can access restricted pages — **N/A**, brachify
  has no logins or restricted pages.
- The frontend is designed using **PySide6, Qt Designer `.ui` files and stylesheets** with
  design components for **the five tab views**. Therefore, changing the design of **the
  `spin_box_arrows` stylesheet** will automatically change the look and feel of all instances
  of that component throughout the system. Changes to the content will not affect the design
  because **the values come from the models and the arrows from `arrows_rc.py`**.
- The usability evaluation identified the following major problems — **N/A**, no usability
  evaluation was run.
- The frontend adopts accessibility principle **WCAG 2.1 SC 1.4.11 Non-text Contrast, at least
  3:1 for controls**. The aspects that demonstrate this principle in the system include **black
  arrows on the white field (21:1), where dark mode drew white on white**.
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **FR-CN-01 →
  `test_channels_spin_box_arrows_are_black`**
- By using a test coverage tool — **N/A**, the repo has no coverage tool.

#### Review and design

- When I reviewed the **generated arrow fixes**, I noticed **a light colour scheme turned the
  whole app light, file dialog included**. Therefore, I did **draw only the Channels spin box
  arrows from black images**.
- The PR does not contain any temporary workaround because **the images are compiled into the
  app, and the tabs still open are recorded in §7.5**.
- The PR only contains small functions that are **23 (`ChannelsView.__init__`, 1 line added),
  and 20 and 19 in the test** long.
- I did **`anti_slop review --base main` (no findings) and a read of the diff** to ensure that
  my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/windows/views/channels_view.py` and `src/windows/ui/`**
  because **the view owns its spin boxes, and generated UI files live in `ui/`**.
- This work belongs in a process in the DFD — **N/A**, it changes drawing, not data flow.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_channels_spin_box_arrows_are_black` (23 passed)** passed.
- I wrote tests to cover abnormal situations involving **PySide6 6.8.1, the Windows lockfile's
  Qt, loading the resource compiled by 6.11.2 (3 passed)** and they passed.
- I checked that these negative cases involving **no arrow stylesheet (darkest pixel 94) and no
  `arrows_rc` import (85)** failed as expected.
- When I reviewed the **generated `darkest_pixel_in_arrow`**, I noticed **it measured before
  `grab()` laid the hidden spin box out, so it read the wrong pixels (255)**. Therefore, I did
  **grab first, then locate the button**.
- Among these tests, **none** are unit tests and **`test_channels_spin_box_arrows_are_black`**
  is an integration test.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (23
  passed), `build.py --check` and `session-start.sh` (exit 0), and a dark-mode render of the
  Channels spin box with black arrows**.

### For PR #**17**

- As part of requirement **the course's weekly individual log, where week 4 took a mark from
  two logs for being "excessively long"**, the user needs to do **run `/make-pr` and get a Part
  A that is quick to audit, identical in the PR and in `docs/logs/<student>/week-<K>.md`**.
- Therefore, I implemented/generated code so that **Team 10 students get a "Keep Part A
  minimal" rule in `docs/workflows/make-pr.md`, restated in one phrase in the PR template,
  `docs/logs/README.md`, `AGENTS.md` and `.claude/`**.

#### Review and design

- When I reviewed the **generated `make-pr.md` against my week 4 log (5,250 words, 6 PRs) and
  Gilles's full-marks log (652 words, 1 PR)**, I noticed **it asked for each receipt "as well
  as the diff allows" and for a shell-check caveat in every testing receipt, which added
  sentences after the bold fill-ins**. Therefore, I did **add the rule (template sentences
  only, one claim and one piece of evidence per fill-in, one-clause N/A reasons) and ask for
  the caveat once**.
- When I reviewed the **generated pointers in `AGENTS.md` and `.claude/`**, I noticed **they
  still said "bold answers backed by evidence" with no length rule**. Therefore, I did **add
  "minimal" to each**.
- The PR does not contain any temporary workaround because **the rule lives once, in
  `make-pr.md`, and every other file links to it or restates it in one phrase**.
- The PR only contains small functions — **N/A**, no function changed.
- I did **a grep of the documentation set for the replaced wording (0 matches)** to ensure
  that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/workflows/make-pr.md`** because **it is the canonical PR
  procedure that `/make-pr` points to**.
- This work belongs in a process in the DFD — **N/A**, brachify's data flow is unchanged.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **this Part A,
  written under the rule (492 words, against about 870 per PR in my week 4 log)** passed.
- I wrote tests to cover abnormal situations — **N/A**, the PR has no code to exercise.
- I checked that these negative cases involving **a grep for "with bold answers backed" and
  "as well as the diff allows" (0 matches)** failed as expected.
- When I reviewed the generated tests — **N/A**, no tests were generated.
- Among these tests, unit and integration tests — **N/A**, the checks are shell commands, not
  tests in `tests/`.
- These tests are included in the directory — **N/A**, nothing was added to `tests/`.
- This new test PR did not break anything else in the system because **only markdown changed
  (`git diff --name-only main...HEAD`), and `python -m pytest` (20 passed),
  `session-start.sh` and `build.py --check` (exit 0) still pass**.
