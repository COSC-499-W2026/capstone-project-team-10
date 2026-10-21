# Week 7, Ehsan

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**116**

- As part of requirement **FR-SV frontend, empty Structures page only**, the user needs to do **reach a Structures page without moving Cylinder or Export**.
- Therefore, I implemented/generated code so that **the medical physicist gets `StructuresView` at `views[5]`, with Cylinder still at 1**.

#### Backend

- The system uses **index-addressed views on `NavigationModel`** because **existing call sites use `views[n]`**. Benefits for using this pattern include **Cylinder stays 1**. Possible risks include **inserting after Import and shifting later tabs**.
  - To mitigate **shifted indexes**, we implemented **appending as `views[5]`**.
  - We considered alternative solutions such as **inserting at index 1, which would retarget every `views[n]`**.
- The system architecture diagram consists of the following major components: **presentation, application state, domain services, libraries, local storage**. This structure has low coupling because **the new view holds no model**. This structure has high cohesion because **`NavigationModel` still only holds views**. This design is scalable because **a later nav button can emit 5 without moving Cylinder**. [system architecture](docs/architecture/diagrams/system-architecture.svg)
- The system uses **synchronous data processing** because **tab switches run on the Qt thread**. This method is done by **`viewChanged(int)` calling `set_page`**. Benefits for using this approach include **one page on screen**. Possible risks include **emitting 5 with no sixth page**.
  - To mitigate **a missing stacked page**, we implemented **adding a page while `viewswidget.count()` is below `len(views)`**.
  - We considered alternative solutions such as **editing `main_window.ui`, which would add generated files**.
- The system adopts a **stateful** approach to state management because **`current_page` is the tab on screen**. This method is done by **`on_close` then `on_open`**. Benefits for using this approach include **one view open**. Possible risks include **opening Export at index 5 if Structures were inserted**.
  - To mitigate **Export at 5**, we implemented **appending Structures**.
  - We considered alternative solutions such as **symbolic view lookup, which this PR does not introduce**.
- The Level 0 DFD consists of the following major components: **TPS, physicist, printer, brachify**. **Unchanged; no new input or output**. [DFD level 0](docs/architecture/diagrams/existing-framework/dfd-0.svg)
- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem, Export**. **Happy path unchanged**. **Structures is empty, so it is not a sixth process**. [DFD level 1](docs/architecture/diagrams/existing-framework/dfd-1.svg)
- Not applicable: **database (none), backend API (none), traceability matrix (FR-SV not complete), test coverage (no coverage tool)**.

#### Frontend

- The frontend is designed using **PySide6** with design components for **`CustomView` pages on `QStackedWidget`**. Therefore, changing the design of **`CustomView.on_open`** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **this page has no widgets yet**.
- Not applicable: **data caching (no backend fetch), restricted pages (no logins), usability evaluation (none run), accessibility (no new copy), traceability matrix (FR-SV not complete), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **`NavigationModel.views` append** for this functionality, I noticed **inserting after Import would shift Cylinder**. Therefore, I did **append at index 5**.
- The PR does not contain any temporary workaround because **the sixth page is added in `NavigationModel` until the `.ui` file lists it**.
- The PR only contains small functions that are **33 lines** long (`NavigationModel.__init__`).
- I did **read `navigation_model.py` and run anti-slop `review --base main`** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`structures_view.py` and `navigation_model.py`** because **views live under `windows/views/` and `NavigationModel` owns the list**.
- This work belongs in **Import's follow-on page, not a sixth DFD process** in the DFD because **the page has no data flow yet**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_structures_view_is_appended_so_cylinder_and_export_keep_their_indexes` and `test_opening_structures_by_signal_shows_page_five` (7 passed in `tests/windows/test_main_window.py`)** passed.
- I wrote tests to cover abnormal situations involving **inserting Structures at index 1** and they passed.
- Not applicable: **negative cases (no invalid input), generated-test review (no generated tests)**.
- Among these tests, **none** are unit tests and **`test_structures_view_is_appended_so_cylinder_and_export_keep_their_indexes`, `test_opening_structures_by_signal_shows_page_five`** are integration tests.
- These tests are included in the directory **`tests/windows/`**.
- This new test PR did not break anything else in the system because **`tests/windows/test_main_window.py` is 7 passed**. Four tests already fail on `main` on this Windows machine (`test_the_default_dome_tandem_cut_out_is_unchanged` 3875.269 vs 3875.268, and three Cylinder/Channels 20 px layout cases at 19 px).

### For PR #**117**

- As part of requirement **FR-SV frontend, Structures tab**, the user needs to do **click Structures under Import and see its empty page**.
- Therefore, I implemented/generated code so that **the medical physicist gets a Structures button that opens `views[5]` without moving Cylinder**.

#### Frontend

- The frontend is designed using **PySide6** with design components for **left-bar `QPushButton`s and `QStackedWidget` pages**. Therefore, changing the design of **`NAV_BUTTON_STYLE`** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **the label is `setText("Structures")` on one button**.
- Not applicable: **data caching (no backend fetch), restricted pages (no logins), usability evaluation (none run), accessibility (no new colon or em dash copy), traceability matrix (FR-SV not complete), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **five `change_color_*` methods** for this functionality, I noticed **a sixth button would stay selected unless every method listed it**. Therefore, I did **`_nav_buttons` and `_highlight_nav`**.
- The PR does not contain any temporary workaround because **the button is created in `MainWindow` after `setupUi` instead of regenerating `main_window.ui`**.
- The PR only contains small functions that are **10 lines** long (`_add_structures_nav_button`).
- I did **read `main_window.py` and run anti-slop `review --base feat/structures-tab-page`** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`main_window.py`** because **nav buttons are wired there**.
- This work belongs in **Import's follow-on page, not a sixth DFD process** in the DFD because **the page still has no data flow**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_structures_button_sits_directly_under_import`, `test_clicking_structures_opens_the_structures_page_and_leaves_cylinder_at_one`, `test_clicking_cylinder_after_structures_still_opens_cylinder` (10 passed in `tests/windows/test_main_window.py`)** passed.
- I wrote tests to cover abnormal situations involving **Cylinder after Structures** and they passed.
- Not applicable: **negative cases (no invalid input), generated-test review (no generated tests)**.
- Among these tests, **none** are unit tests and **the three Structures click tests** are integration tests.
- These tests are included in the directory **`tests/windows/`**.
- This new test PR did not break anything else in the system because **`tests/windows/test_main_window.py` is 10 passed**. Four tests already fail on `main` on this Windows machine, named in #116.
