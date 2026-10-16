# Week 6, Ariq

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**31**

- As part of requirement **the course's weekly individual log, where week 5 lost marks for "excessive documentation checklists and repeated sections marked N/A"**, the user needs to do **run `/make-pr` and get a short Part A, a PR checked against the course size limits and a clear request for any missing screenshot, on a branch named by its type**.
- Therefore, I implemented/generated code so that **Team 10 students get one Not applicable line per subsection, a short Part A for documentation PRs, a size check discussed with the user, an Action needed notice for screenshots, and a `<type>/<what-it-is-about>` branch name rule, in `docs/workflows/make-pr.md` and `commit.md`**.

#### Review and design

- When I reviewed the **generated `make-pr.md` against my week 5 log**, I noticed **it still said "Keep every receipt", which gave that log 23 separate N/A lines**. Therefore, I did **replace it with one Not applicable line per subsection and a table naming each template receipt**.
- When I reviewed the **generated pointers**, I noticed **`pull_request_template.md` and `docs/logs/README.md` still said to mark each receipt N/A**. Therefore, I did **point both at the Not applicable line**.
- When I reviewed the **generated branch for PR #30**, I noticed **its name `make-pr-log-rules` had no type, unlike `fix/channels-list-selection`**. Therefore, I did **add the branch name rule and a `/make-pr` check, and reopen #30 from `docs/make-pr-log-rules`**.
- I did **a grep for "Keep every receipt" and "mark one that" (0 matches) and a check that the 8 section links in `make-pr.md` resolve** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/workflows/make-pr.md`** because **it is the canonical PR procedure that `/make-pr` points to**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **this Part A, written under the new rules (two Not applicable lines, no `— N/A` receipt)** passed.
- This new test PR did not break anything else in the system because **only markdown changed (`git diff --name-only main...HEAD`), `python -m pytest` (63 passed), `session-start.sh` and `build.py --check` (exit 0), and the `python -m pytest` run below**.

  ![1, python -m pytest on docs/make-pr-log-rules, 63 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/66c4f0c246e272a7d913ff53f3be0df55c5eeebf/docs/logs/ariq/screenshots/week-6/pr-31-1-pytest-run.png)

- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no code, the checks are shell commands)**.

### For PR #**32**

- As part of requirement **FR-CN-01 (Milestone 2), create cylinders and needles through
  forms**, the user needs to do **open the Channels tab on a Mac in dark mode and click the spin
  box arrows to change channel diameter or dead space**.
- Therefore, I implemented/generated code so that **physicists see black arrows on the four
  Channels spin boxes in any OS colour scheme, with the rest of the app unchanged**.

#### Frontend

- The frontend is designed using **PySide6, Qt Designer `.ui` files and stylesheets** with
  design components for **the five tab views**. Therefore, changing the design of **the
  `spin_box_arrows` stylesheet** will automatically change the look and feel of all instances
  of that component throughout the system. Changes to the content will not affect the design
  because **the values come from the models and the arrows from `arrows_rc.py`**.
- The frontend adopts accessibility principle **WCAG 2.1 SC 1.4.11 Non-text Contrast, at least
  3:1 for controls**. The aspects that demonstrate this principle in the system include **black
  arrows on the white field (21:1), where dark mode drew white on white**.
- The following traceability matrix shows the list of requirements completed in this
  milestone and their associated tests: **FR-CN-01 →
  `test_channels_spin_box_arrows_are_black`**
- Not applicable: **data caching (no data changes), restricted pages (no logins), usability
  evaluation (none run), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated arrow fixes**, I noticed **a light colour scheme turned the
  whole app light, file dialog included**. Therefore, I did **draw only the Channels spin box
  arrows from black images**.
- When I reviewed the **merged #21**, I noticed **it merged into `test/channels-list-selection`
  after #20 had left it, so `a0fe720` is not on `main`**. Therefore, I did **merge `main` into
  its branch and open this PR into `main`**.
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
- Not applicable: **DFD process (changes drawing, not data flow)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_channels_spin_box_arrows_are_black` (64 passed, screenshot 3 below)** passed.

  ![3, python -m pytest at 8e12632, 64 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/7ae1827c92662101ab620b5478303fe0cbdb570b/docs/logs/ariq/screenshots/week-6/pr-32-3-pytest-64-passed.png)

- I wrote tests to cover abnormal situations involving **PySide6 6.8.1, the Windows lockfile's
  Qt, loading the resource compiled by 6.11.2 (5 passed)** and they passed.
- I checked that these negative cases involving **no arrow stylesheet (darkest pixel 94) and no
  `arrows_rc` import (85)** failed as expected.
- When I reviewed the **generated `darkest_pixel_in_arrow`**, I noticed **it measured before
  `grab()` laid the hidden spin box out, so it read the wrong pixels (255)**. Therefore, I did
  **grab first, then locate the button**.
- Among these tests, **none** are unit tests and **`test_channels_spin_box_arrows_are_black`**
  is an integration test.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (64
  passed), `build.py --check` and `session-start.sh` (exit 0), and the app run on macOS in dark
  mode with Ex1 imported (darkest arrow pixel 39 up, 1 down, on all four Channels spin
  boxes; screenshots 1 and 2 below, from `main` and this branch)**.

  ![1, Channels spin boxes magnified, main above with arrows invisible, this PR below with black arrows](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/7ae1827c92662101ab620b5478303fe0cbdb570b/docs/logs/ariq/screenshots/week-6/pr-32-1-channels-arrows-before-after.png)

  ![2, brachify Channels tab on this branch in dark mode with Ex1 imported](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/7ae1827c92662101ab620b5478303fe0cbdb570b/docs/logs/ariq/screenshots/week-6/pr-32-2-channels-tab-dark-mode.png)

### For PR #**33**

- As part of requirement **the course's regression receipt, which asks for a "screenshot as proof" and was left as a placeholder in test PR #20**, the user needs to do **open this PR or my week 6 log and see the `python -m pytest` run behind #20's "24 passed"**.
- Therefore, I implemented/generated code so that **the grader gets a screenshot of `python -m pytest` at #20's head commit `24957d2`, in `docs/logs/ariq/screenshots/week-6/`**.

#### Review and design

- When I reviewed the **generated screenshot** for this functionality, I did not find any problems with it because **it shows commit `24957d2`, `collected 24 items` and `24 passed`, the figures in #20's receipt**.
- I did **a check that the image link returns HTTP 200 and that `git diff --name-only main...HEAD` lists only this log and the image** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/logs/ariq/week-6.md`** because **it is my log for the week the screenshot was added, with the image beside it in `screenshots/week-6/`**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`python -m pytest` at `24957d2` (24 passed), in the screenshot below** passed.

  ![1, python -m pytest at 24957d2, 24 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/e74d4ce4147b7443e419ca3a2bf13a93b2bcdb5d/docs/logs/ariq/screenshots/week-6/pr-33-1-pytest-24-passed.png)
- This new test PR did not break anything else in the system because **only this log and a PNG changed (`git diff --name-only main...HEAD`), and `python -m pytest` (64 passed), `session-start.sh` and `build.py --check` (exit 0)**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no code, the checks are shell commands)**.

### For PR #**42**

- As part of requirement **the course's regression receipt, which asks for a "screenshot as proof" and was missing from PR #32 ("screenshots missing" in its review)**, the user needs to do **open #32 or my week 6 log and see the Channels spin box arrows before and after the fix, and `python -m pytest` at #32's head**.
- Therefore, I implemented/generated code so that **the grader gets three screenshots in `docs/logs/ariq/screenshots/week-6/`, linked from #32, which stays under 10 files**.

#### Review and design

- When I reviewed the **generated full-window screenshot** for this functionality, I noticed **the arrows are 7 points wide, too small to judge at GitHub's page width**. Therefore, I did **add a 2× crop of the four spin boxes, `main` above and #32 below**.
- I did **a check that the three pinned image links return HTTP 200 and that `git diff --name-only main...HEAD` lists only this log and the three images** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/logs/ariq/screenshots/week-6/`** because **it holds this week's screenshots, beside the log that links them**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **brachify run on macOS in dark mode with Ex1 imported, from `main` (`b652641`, arrows invisible) and #32 (`8e12632`, arrows black), and `python -m pytest` at `8e12632` (64 passed), shown in #32's Part A** passed.
- This new test PR did not break anything else in the system because **only this log and three PNGs changed (`git diff --name-only main...HEAD`), and `python -m pytest` (64 passed), `session-start.sh` and `build.py --check` (exit 0)**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no code, the checks are shell commands)**.

### For PR #**49**

- As part of requirement **FR-CN-13, save and restore all cylinder settings, collar included, through config files**, the user needs to do **set a collar and Apply, Export Current Settings as Config, later Import Config File, and see the collar boxes and the cylinder keep it, also after Generate Tandem**.
- Therefore, I implemented/generated code so that **physicists get the collar exported and imported, and Generate Tandem keeps every live setting, in `reset.py` and `tandem_view.py`**.

#### Data Modeling and Integrity

- This data **the config snapshot** is modeled as **a flat `CONFIG_*` to number dict with all 19 default keys** because **`load_config_file` already accepts any numeric key**. We considered alternative models such as **a nested collar object, rejected because saved config files are flat**.
- This data **the collar keys** uses the input validation to ensure it adheres to **the existing `checkValuesExist` rule: present and numeric, else the current value is kept**.
- Not applicable: **security sanitization, privacy sanitization (settings hold no patient data), encryption, access controls (no stored secrets, no user roles)**.

#### Backend

- The system uses **Qt models and views, with `settings/reset.py` copying between the live settings and the tabs** because **config files and widgets must agree**. Benefits for using this pattern include **one place to add a setting**. Possible risks include **a key missed in one direction**.
  - To mitigate **a missed key**, we implemented **`test_exported_config_names_every_setting`, which fails for any default key missing from the snapshot**.
- The system architecture diagram consists of the following major components: **views, models, domain services, libraries and local storage**. This structure has low coupling because **the tabs reach settings only through `reset.py`**. This structure has high cohesion because **`reset.py` owns both directions of the round trip**. This design is scalable because **a new key needs one line per direction, and the guard test names a forgotten one**.

  **[Unchanged system architecture](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587/docs/architecture/diagrams/system-architecture.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-13: three tests in `test_cylinder_view.py`, one in `test_tandem_view.py`**
- Not applicable: **database (none), data processing, state management (unchanged by this PR), Level 0 DFD, Level 1 DFD (no new process or data flow), backend API (none), test coverage (no coverage tool)**.

#### Frontend

- The frontend uses **the shared live settings dict, merged rather than replaced on Generate Tandem** received from the backend because **a partial snapshot dropped the collar**. Benefits for using this pattern include **no tab can erase another tab's setting**. Possible risks include **a stale key surviving**.
  - To mitigate **a stale key**, we implemented **a snapshot that names every default key, so merging overwrites each one**.
- Not applicable: **restricted pages (no logins), design components, accessibility (no visible change), usability evaluation (none run), traceability matrix (in Backend), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated `getCurrentValues()` and `resetAllValues()` collar lines** for this functionality, I did not find any problems with it because **they read the live settings Apply writes, not unapplied box edits, and the three collar tests failed before them**.
- The PR does not contain any temporary workaround because **it is §7.1's suggested fix: both keys in both directions, and a merge in place of the replace**.
- The PR only contains small functions that are **13 to 19 lines (the four tests); `getCurrentValues` (60) and `resetAllValues` (106) were long already and gain 6 and 3 lines**.
- I did **`anti_slop review --base main` (no findings) and a read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/settings/reset.py`** because **it owns the config round trip**.
- This work belongs in **Import and Export** in the DFD because **config files are read on Import and written on Export**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_exported_config_keeps_the_applied_collar`, `test_config_import_fills_the_collar_boxes` (68 passed, screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **a setting the snapshot does not list surviving Generate Tandem (`test_generating_a_tandem_keeps_settings_the_snapshot_omits`)** and they passed.
- I checked that these negative cases involving **the code before the fix: `KeyError: 'CONFIG_BASE_THICKNESS'`, collar boxes left at 0, the extra setting dropped (4 failed)** failed as expected.
- Among these tests, **none** are unit tests and **all four** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (68 passed), `build.py --check` and `session-start.sh` (exit 0), screenshot 1**.

  ![1, python -m pytest on this branch, the four new tests and 68 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/5c92a09d7318905f61b4b62f27dc8bc2617bf711/docs/logs/ariq/screenshots/week-6/pr-49-1-pytest-68-passed.png)
- Not applicable: **generated-test review (no problem found)**.
