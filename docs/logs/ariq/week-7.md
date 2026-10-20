# Week 7, Ariq

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**93**

- As part of requirement **FR-CN-05, save cylinder designs as templates**, the user needs to do **set up a cylinder on the Cylinder tab and save it under a name to reuse for later patients**.
- Therefore, I implemented/generated code so that **a physicist's cylinder template holds the tab's 11 settings in mm with a name, note and dates, and can never hold a value the tab cannot show**.

#### Data Modeling and Integrity

- This data **a cylinder template** is modeled as **two frozen dataclasses, `CylinderTemplate` holding a `CylinderDesign`** because **AGENTS.md asks for named domain values instead of a bare dict**. We considered alternative models such as **reusing `TipShape` and `NotchSettings`, rejected because `classes.mesh.cylinder` cannot be imported before the app exists (§7.6)**.
- This data **the 11 settings** uses the input validation to ensure it adheres to **the Cylinder tab's spin box ranges in mm (`RANGES`), a non-blank trimmed name, a non-empty ID, and dates with a time zone where modified is not before created**.
- This data **a template** may be vulnerable to **storing patient data in a shared, unencrypted file**. Therefore, it uses a privacy-based sanitization by **having no patient name, ID or plan label field at all**. We considered alternative privacy solutions such as **storing them for provenance, rejected because a template is reused across patients**.
- Not applicable: **security sanitization (no external input yet, the file reader is #87), encryption, access controls (no stored secrets, no user roles)**.

#### Backend

- The system uses **a pure settings module with no Qt or OpenCASCADE imports** because **the caller passes the ID and times, so every rule is testable on its own**. Benefits for using this pattern include **18 tests run in 0.01 s with no window**. Possible risks include **`RANGES` drifting from `cylinder_view.ui`**.
  - To mitigate **range drift**, we implemented **the edge test, which fails if a limit the tab allows is refused, and #89 will compare them with the spin boxes**.
- The system architecture diagram consists of the following major components: **views, models, domain services, libraries and local storage**. This structure has low coupling because **`cylinder_templates.py` imports only the standard library**. This structure has high cohesion because **it only models and checks templates**. This design is scalable because **needles or tandem can join `CylinderDesign` behind a new file version**.

  **[System architecture, settings line now names `cylinder_templates`](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/61542ff991b5d374246c4eabed854531cc5367e6/docs/architecture/diagrams/system-architecture.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-05 (template values): `tests/settings/test_cylinder_templates.py`, 18 cases**
- Not applicable: **database (none), data processing, state management (no app state changed), Level 0 DFD, Level 1 DFD (nothing calls the module yet), backend API (none), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated `RANGES`** for this functionality, I noticed **the diameter box has no minimum in the `.ui`, so 0 mm would pass (§7.9)**. Therefore, I did **set the smallest diameter to 0.01 mm, the box's smallest non-zero value, tested by `("diameter_mm", 0.0)`**.
- The PR does not contain any temporary workaround because **the ranges are the tab's own limits, not guesses**.
- The PR only contains small functions that are **7 to 14 lines (module) and 6 to 10 lines (tests)** long.
- I did **`anti_slop review --base main` (no findings) and a read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **new `src/settings/cylinder_templates.py`** because **settings modules hold user-facing defaults and libraries, like `needle_templates.py`**.
- This work belongs in **Cylinder** in the DFD because **a template is the Cylinder tab's settings**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_a_value_on_the_edge_of_its_range_is_accepted`, `test_spaces_around_the_name_and_note_are_trimmed` (18 passed, screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **NaN and infinity (`test_a_value_outside_the_cylinder_tabs_range_is_rejected`), a naive or backwards date** and they passed.
- I checked that these negative cases involving **six deliberate breaks (no range check, 0 mm diameter, no trim, no ID, time zone or modified check) each failed a test** failed as expected.
- When I reviewed the **`test_a_template_without_an_id_is_rejected`**, I noticed **it was added after its check when this PR was split from #87, so it was never red**. Therefore, I did **remove the check and watch it fail**.
- Among these tests, **all 18** are unit tests and integration tests are not required because **the module imports nothing from the app**.
- These tests are included in the directory **`tests/settings/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (196 passed, screenshot 1), `build.py --check` and `session-start.sh` (exit 0)**.

  ![1, python -m pytest on feat/cylinder-template-values, 18 passed in test_cylinder_templates.py and 196 passed in the whole suite](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/973b7717407d6dd4ca383b1424509e774b91ba12/docs/logs/ariq/screenshots/week-7/pr-93-1-pytest-196-passed.png)

### For PR #**94**

- As part of requirement **FR-CN-05 and FR-CN-06, save templates in a library and keep it safe**, the user needs to do **save a cylinder template, close brachify, and find it again next time, even if the file was edited by hand**.
- Therefore, I implemented/generated code so that **physicists' cylinder templates are saved to and read from `~/brachify/cylinder_templates.json`, with a bad file refused rather than overwritten**.

#### Data Modeling and Integrity

- This data **the template library file** is modeled as **a versioned JSON object, `{"version": 1, "templates": [...]}`, decoded into `CylinderTemplate` values in `load_templates` and nowhere else** because **AGENTS.md asks to decode at the boundary**. We considered alternative models such as **a bare list like `needle_templates.json`, rejected because needles or tandem will join later and need a version to tell files apart**.
- This data **each saved template** uses the input validation to ensure it adheres to **JSON numbers that are not booleans, real `true`/`false` flags, ISO 8601 dates, unique IDs and names ignoring case, then #93's range checks**.
- This data **the library file** may be vulnerable to **a hand edit or a crash corrupting every saved template**. Therefore, it uses a security-based sanitization by **refusing the whole file on any bad entry, never writing over a file it could not read, and saving through a `.tmp` file swapped in with `os.replace`**. We considered alternative security solutions such as **skipping bad entries, rejected because the next save would then delete them**.
- Not applicable: **privacy sanitization (no patient data, #93), encryption, access controls (no stored secrets, no user roles)**.

#### Backend

- The system uses **a pure settings module that takes the file path from its caller** because **the Cylinder tab passes `~/brachify` and the tests pass `tmp_path`**. Benefits for using this pattern include **37 tests in 0.04 s that never touch the developer's home folder**. Possible risks include **two copies of brachify saving at once**.
  - To mitigate **a half-written file**, we implemented **the `.tmp` then `os.replace` save, so the file is always the old or the new library**.
- The system architecture diagram consists of the following major components: **views, models, domain services, libraries and local storage**. This structure has low coupling because **`cylinder_templates.py` imports only the standard library**. This structure has high cohesion because **it only checks, reads and writes templates**. This design is scalable because **a later version can be read beside version 1**.

  **[System architecture, local storage now names `cylinder_templates.json`](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/ef6f4ae21faa98dea9ed801a96f95187a950a171/docs/architecture/diagrams/system-architecture.svg)**
- The system uses **a local JSON file as its** database because **templates are a few small records for one clinic machine, like `needle_templates.json`**. This method is done by **`load_templates` and `add_template` in `cylinder_templates.py`**. Benefits for using this approach include **no server and a file a physicist can read**. Possible risks include **a hand edit breaking it**.
  - To mitigate **a broken hand edit**, we implemented **all-or-nothing decoding with the reason in the error, for example `Cylinder Length must be from 60 to 300 mm`**.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-05 and FR-CN-06 (library file): `tests/settings/test_cylinder_templates.py`, 19 file cases**
- Not applicable: **data processing, state management (no app state changed), Level 0 DFD, Level 1 DFD (nothing calls the module yet), backend API (none), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated malformed-file test** for this functionality, I noticed **its `true` sat in the length, where the 60 mm minimum refused it, so reading `true` as 1 went uncaught**. Therefore, I did **move it to the collar thickness, whose range includes 1**.
- The PR does not contain any temporary workaround because **the save is the needle library's tested pattern**.
- The PR only contains small functions that are **3 to 20 lines (module) and 3 to 25 lines (tests)** long.
- I did **`anti_slop review --base main` (no findings) and a read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/settings/cylinder_templates.py`** because **the file belongs with the template it stores**.
- This work belongs in **Cylinder** in the DFD because **the library stores the Cylinder tab's settings**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_a_saved_template_loads_back_with_identical_values`, `test_no_library_file_means_no_templates_yet` (37 passed, screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **a corrupt, malformed, unreadable or unwritable library, 10 to the 400, and a failed `os.replace`** and they passed.
- I checked that these negative cases involving **eight deliberate breaks (case-sensitive names, `true` as a number, 1 as a flag, writing in place, `OverflowError` escaping, a shared ID, any version, a missing file refused) each failed a test** failed as expected.
- When I reviewed the **`test_a_library_with_a_malformed_entry_is_rejected`**, I noticed **the `true` case passed for the wrong reason (see Review and design)**. Therefore, I did **move it to the collar thickness**.
- Among these tests, **all 37** are unit tests and integration tests are not required because **the module reads and writes only the path it is given**.
- These tests are included in the directory **`tests/settings/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (215 passed, screenshot 1), `build.py --check` and `session-start.sh` (exit 0)**.

  ![1, python -m pytest on feat/cylinder-template-library, 37 passed in test_cylinder_templates.py and 215 passed in the whole suite](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/3eb3e0aee41101555ded9b9ff287fdd8ac61fa9c/docs/logs/ariq/screenshots/week-7/pr-94-1-pytest-215-passed.png)

### For PR #**95**

- As part of requirement **FR-CN-06, manage templates**, the user needs to do **rename a saved cylinder template, change its settings or note, or delete it**.
- Therefore, I implemented/generated code so that **physicists can update or delete one saved cylinder template without touching the others**.

#### Data Modeling and Integrity

- This data **an updated template** uses the input validation to ensure it adheres to **#93's range checks, a name no other template uses in any case, and a known ID**.
- Not applicable: **data model (unchanged, #93), security sanitization (the file is read and written as in #94), privacy sanitization (no patient data), encryption, access controls (no stored secrets, no user roles)**.

#### Backend

- The system uses **the same read, change, then safe write as `add_template`** because **all three must refuse a file they could not read**. Benefits for using this pattern include **one save path (`write_templates`) for every change**. Possible risks include **an update moving the template in the list the physicist knows**.
  - To mitigate **a moved template**, we implemented **a replace at the same index, tested by `test_updating_a_template_keeps_its_id_created_date_and_place`**.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-06 (update and delete): `tests/settings/test_cylinder_templates.py`, seven cases**
- Not applicable: **architecture diagram (unchanged, the module is already named), database (the JSON file of #94), data processing, state management (no app state changed), Level 0 DFD, Level 1 DFD (nothing calls the module yet), backend API (none), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated `add_template` name check** for this functionality, I noticed **update needed the same check but must let a template keep its own name**. Therefore, I did **move it into `name_taken(templates, name, template_id)`, which skips the template's own ID, and use it in both**.
- The PR does not contain any temporary workaround because **update and delete reuse the tested load and save**.
- The PR only contains small functions that are **3 to 11 lines (module) and 5 to 17 lines (tests)** long.
- I did **`anti_slop review --base main` (no findings) and a read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/settings/cylinder_templates.py`** because **every change to the library file lives beside its reader**.
- This work belongs in **Cylinder** in the DFD because **the library stores the Cylinder tab's settings**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_updating_a_template_keeps_its_id_created_date_and_place`, `test_deleting_removes_only_that_template` (44 passed, screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **an unknown ID and a corrupt library, for both update and delete** and they passed.
- I checked that these negative cases involving **six deliberate breaks (created date replaced, template moved, own name taken, rename onto another name, delete dropping the rest, unknown ID read as the first) each failed a test** failed as expected.
- Among these tests, **all 44** are unit tests and integration tests are not required because **the module reads and writes only the path it is given**.
- These tests are included in the directory **`tests/settings/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (222 passed), `build.py --check` and `session-start.sh` (exit 0)**.

  ![1, python -m pytest on feat/cylinder-template-edits, 44 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/56d6fe2094f1381b130b42e9e440a18c022421e0/docs/logs/ariq/screenshots/week-7/pr-95-1-pytest-44-passed.png)
- Not applicable: **generated-test review (no problem found)**.

### For PR #**97**

- As part of requirement **FR-CN-14, set the cylinder's settings on the cylinder form**, the user needs to do **open the Cylinder tab in brachify's default window and read and change every value**.
- Therefore, I implemented/generated code so that **physicists see every Cylinder tab value at full height, scrolling down to reach the rest**.

#### Frontend

- The frontend is designed using **PySide6, Qt Designer `.ui` files and a `QScrollArea`** with design components for **the five tab views**. Therefore, changing the design of **`scroll_cylinder`** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **the rows still come from the generated `Ui_Cylinder_View`, only placed inside the scroll area**.
- The frontend adopts accessibility principle **WCAG 2.1 SC 1.4.10 Reflow, content readable without scrolling in two directions**. The aspects that demonstrate this principle in the system include **full-height values with vertical scrolling only (screenshot 1)**.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-14 (readable cylinder form): `test_cylinder_spin_boxes_keep_their_height_in_the_default_window`, `test_the_cylinder_tab_never_scrolls_sideways_in_the_default_window`**
- Not applicable: **data caching (no data changes), restricted pages (no logins), usability evaluation (none run), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated scroll area** for this functionality, I noticed **in the running app it scrolled sideways and cut off the tick boxes, which the height test could not see**. Therefore, I did **zero the spacer's 280 px width and add `test_the_cylinder_tab_never_scrolls_sideways_in_the_default_window`**.
- The PR does not contain any temporary workaround because **the scroll area replaces the squeeze rather than shrinking fonts or widgets**.
- The PR only contains small functions that are **19 and 16 lines (tests); `CylinderView.__init__` grows from 34 to 46 lines with the scroll area**.
- I did **`anti_slop review --base main` (no findings) and a read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/windows/views/cylinder_view.py`** because **wrapping the `.ui` in a scroll area would have rewritten the whole file**.
- This work belongs in **Cylinder** in the DFD because **it is the Cylinder tab's layout**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **both layout tests (224 passed) and the running app (screenshot 1)** passed.
- I checked that these negative cases involving **the code before the scroll area (16 px), the scroll area without its size constraint (16 px), and the 280 px spacer put back (18 px sideways)** failed as expected.
- Among these tests, **both** are integration tests and unit tests are not required because **the behaviour is the real window's layout**.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (224 passed, screenshot 1), `build.py --check` and `session-start.sh` (exit 0), and the running app on macOS (screenshot 1)**.

  ![1, the Cylinder tab at 770 by 472 on main and on this branch, then the tests on this branch, 19 and 224 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/5ccaea5d1fcb0aa452d105dde833e13cde16974d/docs/logs/ariq/screenshots/week-7/pr-97-1-cylinder-tab-before-after.png)
- Not applicable: **abnormal cases (layout only), generated-test review (no problem found)**.

### For PR #**98**

- As part of requirement **FR-CN-05, save cylinder designs as templates in a library**, the user needs to do **set up a cylinder on the Cylinder tab, type a name and an optional note, and press Save as Template**.
- Therefore, I implemented/generated code so that **physicists save the Cylinder tab's settings as a named template and see every saved template listed on the tab**.

#### Frontend

- The frontend uses **an in-memory tuple of `CylinderTemplate` values, reread from the library on start and replaced by the library each save returns** because **the file is the single source and the list must never show a template the file lacks**. Benefits for using this pattern include **the list cannot drift from the file**. Possible risks include **a file another copy of brachify changed since start**.
  - To mitigate **a stale list after a save**, we implemented **listing the tuple `add_template` returns after writing, not the old list plus one**.
- The frontend is designed using **PySide6, Qt Designer `.ui` files and one group stylesheet** with design components for **the five tab views**. Therefore, changing the design of **the `group_templates` stylesheet** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **the names and status text come from the view, the look from the `.ui`**.
- The frontend adopts accessibility principle **WCAG 2.1 SC 3.3.1 Error Identification, input errors described in text**. The aspects that demonstrate this principle in the system include **the status line naming why a save was refused, such as `A cylinder template needs a name`**.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-05 (save from the tab): `tests/views/test_cylinder_template_controls.py`, seven cases**
- Not applicable: **restricted pages (no logins), usability evaluation (none run), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated save test** for this functionality, I noticed **it saved the default cylinder, whose collar thickness and height are both 0, so saving one from the other's box went unnoticed**. Therefore, I did **add `test_every_setting_on_the_tab_is_saved_in_its_own_field`, with all 11 values different**.
- When I reviewed the **generated test run** for this functionality, I noticed **this file alone crashed at exit (138) after passing; one existing Cylinder test alone does the same on `main`**. Therefore, I did **record it as §7.13 and confirm the whole suite exits 0**.
- The PR does not contain any temporary workaround because **the controls call the tested library, and the §7.13 crash is recorded, not hidden**.
- The PR only contains small functions that are **7 to 15 lines (view) and 5 to 28 lines (tests); `CylinderView.__init__` grows from 46 to 49** long.
- I did **`anti_slop review --base main` (no findings) and a read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/windows/views/cylinder_view.py` and `cylinder_view.ui`** because **the group is part of the Cylinder tab**.
- This work belongs in **Cylinder** in the DFD because **it saves the Cylinder tab's settings to the Plan and settings store**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_save_as_template_lists_the_template_and_writes_it`, `test_every_setting_on_the_tab_is_saved_in_its_own_field`, `test_a_value_typed_in_centimetres_is_saved_in_millimetres` (7 and 231 passed, screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **an unreadable library (`test_an_unreadable_library_empties_the_list_and_names_the_file`)** and they passed.
- I checked that these negative cases involving **a blank name, a name taken in another case, and seven deliberate breaks (displayed number saved, collar fields swapped, saved but not listed, refusal not shown, read error escaping, wrong tooltip length, `RANGES` drifting from the `.ui`)** failed as expected.
- When I reviewed the **`test_save_as_template_lists_the_template_and_writes_it`**, I noticed **its default cylinder hid swapped collar fields (see Review and design)**. Therefore, I did **add the all-different test**.
- Among these tests, **all seven cases** are integration tests and unit tests are not required because **the library's rules are unit tested in `tests/settings/` (#93, #94)**.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (231 passed, exit 0, screenshot 1), `build.py --check` and `session-start.sh` (exit 0), and saving two templates in the running app on macOS (screenshot 1)**.

  ![1, the running app after saving 30 mm standard then 180 mm flat, then the tests on this branch, 7 and 231 passed](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/9c36e450f417428df193e4d33f668b9b6764a0ae/docs/logs/ariq/screenshots/week-7/pr-98-1-save-template-and-tests.png)

### For PR #**100**

- As part of requirement **FR-CN-05 and FR-CN-10, reuse a saved cylinder template without importing a plan**, the user needs to do **select a saved template on the Cylinder tab, press Load, check the values, then press Apply Settings**.
- Therefore, I implemented/generated code so that **physicists load any saved cylinder template onto the Cylinder tab and review it before building it**.

#### Frontend

- The frontend uses **the `CylinderTemplate` tuple the tab already holds, indexed by the list's selected row** because **the list is filled from that tuple in the same order**. Benefits for using this pattern include **no second read of the file on Load**. Possible risks include **Load pressed with no row selected**.
  - To mitigate **Load with no selection**, we implemented **`action_select_template`, which enables Load only while a row is selected**.
- The frontend is designed using **PySide6, Qt Designer `.ui` files and the Templates group's one stylesheet** with design components for **the five tab views**. Therefore, changing the design of **the `group_templates` stylesheet** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **the values come from the template, the look from the `.ui`**.
- The frontend adopts accessibility principle **WCAG 2.1 SC 3.2.2 On Input, no change of context without warning**. The aspects that demonstrate this principle in the system include **Load building nothing until Apply Settings, with the status line saying so (screenshot 1)**.
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-05 and FR-CN-10 (load a template): `test_load_fills_every_control_and_the_name_and_note_without_applying`, `test_load_then_apply_settings_builds_the_templates_cylinder`**
- Not applicable: **restricted pages (no logins), usability evaluation (none run), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **generated `set_cylinder_design`** for this functionality, I did not find any problems with it because **it writes lengths through `set_dimensions_mm` and the `LengthField`s, and `test_a_template_loaded_while_showing_cm_is_displayed_in_cm` passes**.
- The PR does not contain any temporary workaround because **Load reuses the tab's own setters, the same ones a config import uses**.
- The PR only contains small functions that are **3 to 10 lines (view) and 4 to 28 lines (tests); `CylinderView.__init__` grows from 49 to 51** long.
- I did **`anti_slop review --base main` (no findings) and a read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/windows/views/cylinder_view.py` and `cylinder_view.ui`** because **Load is part of the Cylinder tab's Templates group**.
- This work belongs in **Cylinder** in the DFD because **it reads the Cylinder tab's settings from the Plan and settings store**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_load_fills_every_control_and_the_name_and_note_without_applying`, `test_load_then_apply_settings_builds_the_templates_cylinder` (235 passed) and the running app (screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **a template loaded while the tab shows cm** and they passed.
- I checked that these negative cases involving **Load with nothing selected, and six deliberate breaks (collar tick, tip or note not loaded, mm shown as cm, Load applying, Load always enabled)** failed as expected.
- Among these tests, **all four** are integration tests and unit tests are not required because **the template is decoded and checked by the tested library (#93, #94)**.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (235 passed, exit 0), `build.py --check` and `session-start.sh` (exit 0)**.

  ![1, the running app after Load, the 30 mm standard template back on the Cylinder tab](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/d363c8080bc87597ebfc062561f7c47f3835ef5f/docs/logs/ariq/screenshots/week-7/pr-100-1-cylinder-tab-after-load.png)
- Not applicable: **generated-test review (no problem found)**.
