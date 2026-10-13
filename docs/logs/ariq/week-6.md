# Week 6, Ariq

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

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
  **`test_channels_spin_box_arrows_are_black` (64 passed)** passed.
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
  boxes)**.
