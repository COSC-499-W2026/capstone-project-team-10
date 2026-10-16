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

### For PR #**50**

- As part of requirement **FR-CN-15, set the notch's size and angle in addition to diameter, length and collar**, the user needs to do **choose where the orientation notch sits, clockwise from Anterior as the reference sheet shows it, and how wide, deep and tall it is**.
- Therefore, I implemented/generated code so that **the geometry can build a notch of any size and angle from `NotchSettings`, with the defaults building today's notch exactly**.

#### Data Modeling and Integrity

- This data **the notch settings** is modeled as **`NotchSettings`, a frozen dataclass in mm and degrees** because **AGENTS.md asks to decode config into a named value at the boundary**. We considered alternative models such as **reading the config dict inside `CylinderNotch`, rejected as a bare dict passed inward**.
- This data **the notch config keys** uses the input validation to ensure it adheres to **all five keys present, `KeyError` otherwise, never a guessed value**.
- Not applicable: **security sanitization, privacy sanitization (settings hold no patient data), encryption, access controls (no stored secrets, no user roles)**.

#### Backend

- The system uses **a geometry module per concern under `classes/mesh/`** because **the notch is built independently of the cylinder**. Benefits for using this pattern include **testing the notch without a cylinder or window**. Possible risks include **the sheet and the geometry disagreeing on the angle**.
  - To mitigate **an angle mismatch**, we implemented **one convention, clockwise from Anterior as the sheet draws it, converted once in `CylinderNotch`**.
- The system architecture diagram consists of the following major components: **views, models, domain services, libraries and local storage**. This structure has low coupling because **`notch.py` imports only OpenCASCADE**. This structure has high cohesion because **`notch.py` only builds the notch**. This design is scalable because **a new notch setting is one dataclass field**.

  **[Unchanged system architecture](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587/docs/architecture/diagrams/system-architecture.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-15 (notch): `tests/mesh/test_notch.py`, six tests**
- Not applicable: **database (none), data processing, state management (unchanged by this PR), Level 0 DFD, Level 1 DFD (no new process or data flow), backend API (none), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated notch rotation** for this functionality, I did not find any problems with it because **sheet angle 90 lands on +x in `test_a_quarter_turn_clockwise_on_the_sheet_moves_the_notch_to_plus_x`, and turning it the other way fails five tests**.
- The PR does not contain any temporary workaround because **the defaults are measured to reproduce today's notch**.
- The PR only contains small functions that are **7 to 9 lines (`notch.py`) and 9 to 19 lines (tests); `BrachyCylinder.shape` (53) was long already and changes 1 line**.
- I did **`anti_slop review` against #49's branch (no findings) and a read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/classes/mesh/notch.py`** because **it is the notch's module**.
- This work belongs in **Cylinder** in the DFD because **the notch is part of the cylinder solid**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_default_settings_build_the_notch_brachify_always_made`, `test_a_quarter_turn_clockwise_on_the_sheet_moves_the_notch_to_plus_x` (74 passed, screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **a config missing a notch key (`test_a_config_without_a_notch_key_is_rejected`)** and they passed.
- I checked that these negative cases involving **the angle turned the wrong way (5 failed)** failed as expected.
- Among these tests, **all six in `test_notch.py`** are unit tests and integration tests are not required because **the notch builds without the cylinder or a window**.
- These tests are included in the directory **`tests/mesh/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (74 passed), `build.py --check` and `session-start.sh` (exit 0), screenshot 1**.

  ![1, python -m pytest on this branch, test_notch.py and 74 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/ae3aff970db3dc3abea9eab23ec0e2351c37058e/docs/logs/ariq/screenshots/week-6/pr-50-1-pytest-74-passed.png)
- Not applicable: **generated-test review (no problem found)**.

### For PR #**51**

- As part of requirement **FR-CN-15, set the notch's size and angle in addition to diameter, length and collar**, the user needs to do **set the notch through a config file and get a cylinder whose notch matches it, or no notch**.
- Therefore, I implemented/generated code so that **the cylinder is built from the five `CONFIG_NOTCH_*` keys, and they are saved in exported configs**.

#### Data Modeling and Integrity

- This data **the five notch keys** is modeled as **numbers in the flat config, `CONFIG_NOTCH_ENABLED` as 1 or 0** because **`load_config_file` accepts only numbers**. We considered alternative models such as **a JSON boolean, rejected because the loader accepts only numbers and, since #28, rejects `true` and `false`**.
- This data **the notch keys** uses the input validation to ensure it adheres to **numeric values, as `checkValuesExist` enforces**.
- Not applicable: **security sanitization, privacy sanitization (settings hold no patient data), encryption, access controls (no stored secrets, no user roles)**.

#### Backend

- The system uses **settings read once when a `BrachyCylinder` is built**, as its length already is, because **the solid must match the settings it was applied with**. Benefits for using this pattern include **a stable notch until the next Apply**. Possible risks include **a setting changed without Apply**.
  - To mitigate **a stale notch**, we implemented **Apply writing the keys before it builds the cylinder**.
- The system architecture diagram consists of the following major components: **views, models, domain services, libraries and local storage**. This structure has low coupling because **the geometry reads settings through `notch_settings_from_config`**. This structure has high cohesion because **the cylinder module owns how the notch joins the wall**. This design is scalable because **a new setting is a key and a dataclass field**.

  **[Unchanged system architecture](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587/docs/architecture/diagrams/system-architecture.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-15 (notch): `tests/mesh/test_cylinder.py`, five tests**
- Not applicable: **database (none), data processing, state management (unchanged by this PR), Level 0 DFD, Level 1 DFD (no new process or data flow), backend API (none), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated collar cap test** for this functionality, I noticed **it passed on `main`, whose fixed 10 mm notch was already capped**. Therefore, I did **add `test_a_notch_shorter_than_the_collar_keeps_its_own_height`, which failed first**.
- When I reviewed the **generated snapshot**, I noticed **#49's guard test failed on the five new keys**. Therefore, I did **export them in `getCurrentValues()`**.
- The PR does not contain any temporary workaround because **the defaults keep the measured volume, 109,599.266 mm³**.
- The PR only contains small functions that are **7 lines (`__init__`) and 8 to 14 lines (tests); `shape` (54) and `getCurrentValues` (66) were long already and change 3 and 6 lines**.
- I did **`anti_slop review` against #50's branch (no findings) and a read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/classes/mesh/cylinder.py`** because **`BrachyCylinder` decides how the notch joins the wall and collar**.
- This work belongs in **Cylinder** in the DFD because **it changes the cylinder solid**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_default_settings_build_the_cylinder_brachify_always_made`, `test_the_notch_angle_setting_moves_the_notch` (79 passed, screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **a 20 mm notch on a 5 mm collar, and an 8 mm notch on a 20 mm collar** and they passed.
- I checked that these negative cases involving **always fusing the notch (`test_a_disabled_notch_leaves_a_plain_cylinder` failed)** failed as expected.
- Among these tests, **all five** are unit tests and integration tests are not required because **the cylinder builds without a window**.
- These tests are included in the directory **`tests/mesh/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (79 passed), `build.py --check` and `session-start.sh` (exit 0), screenshot 1**.

  ![1, python -m pytest on this branch, test_cylinder.py and 79 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/7fcc64f4ec5c1fc8d4b992feef187c11f1acb254/docs/logs/ariq/screenshots/week-6/pr-51-1-pytest-79-passed.png)

### For PR #**52**

- As part of requirement **FR-CN-14 (Milestone 2), set notch size and angle on the cylinder form**, the user needs to do **open the Cylinder tab, tick or untick Add Notch, type its angle, width, depth and height in mm or cm, and press Apply Settings**.
- Therefore, I implemented/generated code so that **physicists set the notch on the Cylinder tab and see it in the viewport, with no DICOM needed**.

#### Backend

- The system uses **Qt models and views, the view reading its controls into a `NotchSettings`** because **the notch must be set where the cylinder is**. Benefits for using this pattern include **the geometry never reads a widget**. Possible risks include **a control the config import misses**.
  - To mitigate **a missed control**, we implemented **`set_notch_settings`, used by both the model update and `resetAllValues`**.
- The system architecture diagram consists of the following major components: **views, models, domain services, libraries and local storage**. This structure has low coupling because **the view hands the geometry a `NotchSettings`, never a widget**. This structure has high cohesion because **`CylinderView` owns every Cylinder control**. This design is scalable because **another notch field is one row and one `LengthField`**.

  **[Unchanged system architecture](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587/docs/architecture/diagrams/system-architecture.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-14 (notch): four tests in test PR #53**
- Not applicable: **database (none), data processing, state management (unchanged by this PR), Level 0 DFD, Level 1 DFD (no new process or data flow), backend API (none), test coverage (no coverage tool)**.

#### Frontend

- The frontend is designed using **PySide6 and Qt Designer `.ui` files** with design components for **the Cylinder tab's label and spin box rows**. Therefore, changing the design of **a row's stylesheet** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **values come from the model through `set_notch_settings`**.
- The frontend adopts accessibility principle **labels named by the control they describe, without abbreviation, per the repository's UI copy rule**. The aspects that demonstrate this principle in the system include **Notch Angle, Width, Depth and Height, each a label buddy of its field (screenshot 1)**.
- Not applicable: **data caching (no new data store), traceability matrix (in Backend), restricted pages (no logins), usability evaluation (none run), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated notch rows and `CylinderView` methods** for this functionality, I did not find any problems with it because **the app run showed a 4 mm notch at 90 degrees on the +x side (screenshot 1), and #53's four tests pass**.
- The PR does not contain any temporary workaround because **lengths go through `LengthField`, like the existing four**.
- The PR only contains small functions that are **5 to 8 lines (`notch_settings`, `set_notch_settings`, `action_enable_notch_fields`); `action_apply_settings` (43), `__init__` (33) and `resetAllValues` (107) were long already and gain 6, 9 and 1 lines**.
- I did **`anti_slop review` against #51's branch (no findings) and a read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/windows/views/cylinder_view.py` and `src/windows/ui/cylinder_view.ui`** because **the Cylinder view owns its controls, and the `.ui` is regenerated, not hand-edited**.
- This work belongs in **Cylinder** in the DFD because **it is the Cylinder tab's input**.

#### Testing receipts

- This new test PR did not break anything else in the system because **`python -m pytest` (79 passed on this branch, 83 with #53's tests), `build.py --check` and `session-start.sh` (exit 0), and the app run on macOS with Ex1 imported and a 4 mm notch at 90 degrees applied (screenshot 1)**.

  ![1, brachify on this branch with Ex1 imported, Cylinder tab, a 4 mm notch at 90 degrees applied and drawn on the +x side](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/29b2bf4c630209683686f54d393c48db08cccf87/docs/logs/ariq/screenshots/week-6/pr-52-1-cylinder-tab-notch-90.png)
- Not applicable: **happy path, abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (all in test PR #53)**.

### For test PR #**53** written to assess functionality in **#52, the Cylinder tab's notch controls**

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_apply_builds_the_notch_typed_on_the_cylinder_tab`, `test_config_import_fills_the_notch_controls` (83 passed, screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **Add Notch unticked, and notch lengths typed in cm** and they passed.
- I checked that these negative cases involving **the code before #52 (4 failed with `AttributeError`) and the notch line removed from `resetAllValues` (1 failed)** failed as expected.
- Among these tests, **none** are unit tests and **all four** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (83 passed), `build.py --check` and `session-start.sh` (exit 0), screenshot 1**.

  ![1, python -m pytest on this branch, the four notch control tests and 83 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/1a394e886d1db6c9a58fc33e8efd9f4e43c05eb1/docs/logs/ariq/screenshots/week-6/pr-53-1-pytest-83-passed.png)
- Not applicable: **generated-test review (no problem found)**.

### For PR #**54**

- As part of requirement **FR-CN-15, set a cylinder's tip shape, dome or flat**, the user needs to do **choose a flat tip instead of the dome and get a flat-topped cylinder**.
- Therefore, I implemented/generated code so that **the cylinder is built with a dome or a flat top from `CONFIG_CYLINDER_FLAT_TIP`**.

#### Data Modeling and Integrity

- This data **the tip** is modeled as **`TipShape`, an enum of DOME and FLAT, from a 0 or 1 config key** because **the config holds numbers and the code needs a name**. We considered alternative models such as **a tip radius, rejected when the dome-or-flat choice was agreed**.
- This data **the tip key** uses the input validation to ensure it adheres to **a number, as `checkValuesExist` enforces, read as flat when non-zero**.
- Not applicable: **security sanitization, privacy sanitization (settings hold no patient data), encryption, access controls (no stored secrets, no user roles)**.

#### Backend

- The system uses **settings read once when a `BrachyCylinder` is built** because **the solid must match the applied settings**. Benefits for using this pattern include **the PDF can ask the cylinder for its tip**. Possible risks include **other code still assuming a dome**.
  - To mitigate **dome assumptions**, we implemented **§7.10, naming the two places and the PRs that fix them**.
- The system architecture diagram consists of the following major components: **views, models, domain services, libraries and local storage**. This structure has low coupling because **`add_dome` is a separate function `shape()` calls only for a dome**. This structure has high cohesion because **`cylinder.py` owns the solid's shape**. This design is scalable because **a third tip is one enum value and one branch**.

  **[Unchanged system architecture](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587/docs/architecture/diagrams/system-architecture.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-15 (tip): `test_a_flat_tip_builds_a_plain_cylinder_with_a_flat_top`**
- Not applicable: **database (none), data processing, state management (unchanged by this PR), Level 0 DFD, Level 1 DFD (no new process or data flow), backend API (none), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated tip change**, I noticed **the reference sheet's interstitial maths and the tandem cut-out also assume a dome**. Therefore, I did **record it as §7.10 and fix it in #55 and #56**.
- The PR does not contain any temporary workaround because **the flat tip is a real branch in the build; only a config file can set it until #57**.
- The PR only contains small functions that are **3 lines (`tip_shape_from_config`), 26 (`add_dome`, moved out of `shape`), 31 (`shape`, down from 54) and 12 (the test)**.
- I did **`anti_slop review` against #53's branch (no findings) and a read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/classes/mesh/cylinder.py`** because **it builds the solid**.
- This work belongs in **Cylinder** in the DFD because **it changes the cylinder solid**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_a_flat_tip_builds_a_plain_cylinder_with_a_flat_top`, pi x 15² x 160 = 113,097.336 mm³ (84 passed, screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **the default dome kept at 109,599.266 mm³ (`test_default_settings_build_the_cylinder_brachify_always_made`)** and they passed.
- I checked that these negative cases involving **the dome always built (109,563.044, failed)** failed as expected.
- Among these tests, **the flat-tip test** are unit tests and integration tests are not required because **the cylinder builds without a window**.
- These tests are included in the directory **`tests/mesh/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (84 passed), `build.py --check` and `session-start.sh` (exit 0), screenshot 1**.

  ![1, python -m pytest on this branch, the flat-tip test and 84 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/86976b0a4874fa3c27f8a7c9b79eed616420791d/docs/logs/ariq/screenshots/week-6/pr-54-1-pytest-84-passed.png)
- Not applicable: **generated-test review (no problem found)**.

### For PR #**55**

- As part of requirement **FR-CN-07, include custom cylinders in the 3D export and the PDF reference sheet**, the user needs to do **export the reference sheet for a flat-tipped cylinder and read each needle's interstitial length**.
- Therefore, I implemented/generated code so that **the sheet's interstitial lengths match the flat top a clinician prints**.

#### Data Modeling and Integrity

- This data **the cylinder surface for the length maths** is modeled as **a point cloud, 0.1 mm apart, now a flat disc and rim ring for a flat tip** because **the existing method measures needles against points**. We considered alternative models such as **an exact ray and plane intersection, rejected to keep one method for both tips**.
- This data **the interstitial lengths** uses the input validation to ensure it adheres to **the existing 0.25 mm match tolerance**.
- Not applicable: **security sanitization, privacy sanitization (settings hold no patient data), encryption, access controls (no stored secrets, no user roles)**.

#### Backend

- The system uses **the existing point-cloud measurement, with a surface per tip** because **the sheet's numbers must follow the cylinder**. Benefits for using this pattern include **dome lengths untouched**. Possible risks include **a gap where the wall meets the top**.
  - To mitigate **a gap**, we implemented **the rim ring and `test_a_flat_tip_keeps_its_wall_up_to_the_top`**.
- The system architecture diagram consists of the following major components: **views, models, domain services, libraries and local storage**. This structure has low coupling because **the maths reads only `cylinder.tip`, `length` and `diameter`**. This structure has high cohesion because **`template_reference.py` owns the sheet's numbers**. This design is scalable because **another tip adds one surface function**.

  **[Unchanged system architecture](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/7b31587/docs/architecture/diagrams/system-architecture.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-07 (lengths): three tests in `tests/pdf/test_template_reference.py`**
- Not applicable: **database (none), data processing, state management (unchanged by this PR), Level 0 DFD, Level 1 DFD (no new process or data flow), backend API (none), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated wall test** for this functionality, I noticed **a needle leaving at z 100 passed even if the flat-tip wall stopped where a dome begins**. Therefore, I did **move it to z 155, where the two differ (5 vs 8.82 mm)**.
- When I reviewed the **geometry fixtures**, I noticed **`tests/pdf/` needed `tests/mesh/conftest.py`'s app**. Therefore, I did **move it to `tests/conftest.py` rather than copy it**.
- The PR does not contain any temporary workaround because **the flat surface is built from the same spacing as the dome**.
- The PR only contains small functions that are **11 lines (`flat_top_points`) and 9 to 11 (tests); `get_all_interstitial_lengths` (170) was long already and gains 4 lines**.
- I did **`anti_slop review` against #54's branch (no findings) and a read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/classes/pdf/template_reference.py`** because **it computes the sheet's lengths**.
- This work belongs in **Export** in the DFD because **it is part of writing the PDF**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_a_needle_leaving_a_flat_tip_is_measured_from_the_flat_top`, 20 mm (87 passed, screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **a dome needle 10 mm off axis (23.82 mm) and a sideways needle high on a flat tip's wall (5 mm)** and they passed.
- I checked that these negative cases involving **the dome measured for a flat tip (23.81, failed) and the wall stopped at 145 mm (failed)** failed as expected.
- Among these tests, **all three** are unit tests and integration tests are not required because **the lengths need a cylinder object, not a window**.
- These tests are included in the directory **`tests/pdf/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (87 passed), `build.py --check` and `session-start.sh` (exit 0), screenshot 1**.

  ![1, python -m pytest on this branch, the three length tests and 87 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/b8cb81bfb64c0cfd1351dd1ebd6f8fea95ccc438/docs/logs/ariq/screenshots/week-6/pr-55-1-pytest-87-passed.png)
