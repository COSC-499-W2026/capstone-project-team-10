# Week 9, Ehsan

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**228**

- As part of requirement **FR-SV-01**, the user needs to do **select a listed organ, hide it with its checkbox or move to it with the keyboard, and still control that highlight**.
- Therefore, I implemented/generated code so that **the medical physicist keeps the highlight when showing or hiding an organ, and one click after a keyboard move clears it**.

#### Frontend

- The frontend is designed using **PySide6** with design components for **the Structures `QListWidget`**. Therefore, changing the design of **`structure_list` row updates** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **row text still comes from `structure_list_rows`**.
- Not applicable: **data caching (no backend fetch), restricted pages (no logins), usability evaluation (none run), accessibility (no new copy), traceability matrix (FR-SV not complete), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **Structures list click handling** for this functionality, I noticed **`changed` cleared every `QListWidgetItem`, so a checkbox click deleted its own row (`RuntimeError: Internal C++ object already deleted`)**. Therefore, I did **rewrite the rows in place when the ROI numbers are unchanged**.
- When I reviewed the **same-click guard** for this functionality, I noticed **keyboard movement set `_just_selected` and never cleared it, so the next click left `highlighted` at 2**. Therefore, I did **set the guard only when a mouse press changes the current row**.
- The PR does not contain any temporary workaround because **the same row objects stay for a visibility change, and a new plan still rebuilds the list**.
- The PR only contains small functions that are **33 lines** long (`action_update_structure_list`).
- I did **run `PYTHONPATH=agent-skills/anti-slop-py/src python -m anti_slop review --base origin/main src tests utils` (no findings)** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`structures_view.py`** because **the bug is which list signal the click handles**.
- This work belongs in **the Structures page** in the DFD because **highlight and visibility stay display-only and Export is unchanged**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_toggling_checkbox_does_not_drop_highlight` and `test_click_after_keyboard_navigation_can_rehighlight` (4 passed with the neighbouring highlight click tests)** passed.
- I checked that these negative cases involving **a forced list rebuild (deleted `QListWidgetItem`) and a guard left set after keyboard movement (`highlighted` stayed 2)** failed as expected.
- Among these tests, **`test_toggling_checkbox_does_not_drop_highlight` and `test_click_after_keyboard_navigation_can_rehighlight`** are integration tests and unit tests are not required because **the failure is in the list widget's click handling**.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` on this branch is 420 passed, 6 failed. The 6 are `test_the_default_dome_tandem_cut_out_is_unchanged` and five default-window layout tests. The two highlight tests passed. [author: attach a screenshot of the pytest summary]**
