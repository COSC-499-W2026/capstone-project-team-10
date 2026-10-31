# Week 8, Ehsan

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**149**

- As part of requirement **FR-SV-01**, the user needs to do **import a plan, open Structures, and see organs and tumours without Applicator rows**.
- Therefore, I implemented/generated code so that **the medical physicist gets an anatomy-only Structures list, while Import keeps every ROI**.

#### Data Modeling and Integrity

- This data **decoded ROI list** is modeled as **a `tuple[Structure, ...]` filtered by `StructureType`** because **the tab shows organs and tumours, not needles**. We considered alternative models such as **deleting OTHER from `DicomData`, which would hide needles on Import too**.
- This data **Structures list** uses the input validation to ensure it adheres to **`ORGAN` and `TUMOUR` only**.
- Not applicable: **security sanitization, privacy sanitization, encryption, access controls (no network or logins)**.

#### Backend

- The system uses **a pure filter in `structure_list.py`** because **FR-SV-01 is anatomy beside the probe, not the full RTSTRUCT**. Benefits for using this pattern include **the same rule is testable without Qt**. Possible risks include **filtering in the view and drifting from Import**.
  - To mitigate **a second copy of the rule**, we implemented **`anatomy_structures` used by `StructuresView`**.
  - We considered alternative solutions such as **hiding rows in the widget, which would still build Applicator items**.
- The system architecture diagram consists of the following major components: **presentation, application state, domain services, libraries, local storage**. This structure has low coupling because **`DicomData.structures` is unchanged**. This structure has high cohesion because **list-row rules stay in `structure_list.py`**. This design is scalable because **a later type filter can reuse `anatomy_structures`**. [system architecture](docs/architecture/diagrams/system-architecture.svg)
- The system uses **synchronous data processing** because **the list is rebuilt on `StructuresModel.changed`**. This method is done by **`action_update_structure_list` calling `anatomy_structures`**. Benefits for using this approach include **Import and Structures stay independent**. Possible risks include **Ex1 looking empty**.
  - To mitigate **an empty list being a bug**, we implemented **keeping Import at 42 rows and documenting that Ex1 has no organs**.
  - We considered alternative solutions such as **showing BODY as anatomy, which is `OTHER`**.
- The system adopts a **stateful** approach to state management because **`StructuresModel.structures` still holds every ROI**. This method is done by **filtering only the view's rows**. Benefits for using this approach include **a failed import still clears the model**. Possible risks include **calling `set_visible` on a hidden OTHER ROI**.
  - To mitigate **turning on a needle from this tab**, we implemented **not listing OTHER**.
  - We considered alternative solutions such as **clearing OTHER from the model, which would drop Import rows**.
- The Level 0 DFD consists of the following major components: **TPS, physicist, printer, brachify**. **Unchanged; the filter is display-only**. [DFD level 0](docs/architecture/diagrams/existing-framework/dfd-0.svg)
- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem, Export**. **Happy path unchanged**. **Failure path unchanged**. [DFD level 1](docs/architecture/diagrams/existing-framework/dfd-1.svg)
- Not applicable: **database (none), backend API (none), traceability matrix (FR-SV not complete), test coverage (no coverage tool)**.

#### Frontend

- The frontend is designed using **PySide6** with design components for **a `QListWidget` of organ and tumour rows**. Therefore, changing the design of **`structure_list` styling** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **row text still comes from `structure_list_rows`**.
- Not applicable: **data caching (no backend fetch), restricted pages (no logins), usability evaluation (none run), accessibility (no new copy), traceability matrix (FR-SV not complete), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **Structures list fill** for this functionality, I noticed **`tuple(model.structures.values())` included Applicator ROIs**. Therefore, I did **pass that tuple through `anatomy_structures`**.
- The PR does not contain any temporary workaround because **OTHER ROIs stay in `DicomData` and on Import**.
- The PR only contains small functions that are **16 lines** long (`anatomy_structures`).
- I did **run `PYTHONPATH=agent-skills/anti-slop-py/src python -m anti_slop review --base origin/main src tests utils` (no findings)** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`structure_list.py` and `structures_view.py`** because **the filter is pure and the tab only displays it**.
- This work belongs in **Import's follow-on Structures page** in the DFD because **the list is display-only and Export is unchanged**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_anatomy_structures_keep_organs_and_tumours_only`, `test_structures_tab_lists_only_organs_and_tumours`, `test_structures_tab_is_empty_for_ex1_while_import_keeps_needles` (10 passed with Import list tests)** passed.
- I wrote tests to cover abnormal situations involving **`anatomy_structures(None)` and `anatomy_structures(())`** and they passed.
- I checked that these negative cases involving **keeping Applicator26, BODY or Surface3** failed as expected.
- Among these tests, **`test_anatomy_structures_keep_organs_and_tumours_only`** is a unit test and **`test_structures_tab_lists_only_organs_and_tumours`, `test_structures_tab_is_empty_for_ex1_while_import_keeps_needles`** are integration tests.
- These tests are included in the directory **`tests/dicom/` and `tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` is 297 passed, 21 failed**. The 21 are scipy/skimage surface tests, `test_the_default_dome_tandem_cut_out_is_unchanged`, and three 20 px layout cases. New list tests passed.
  **[author: attach a screenshot of the pytest run showing the new tests and the 297 passed / 21 failed total]**

### For PR #**152**

- As part of requirement **FR-SV-01**, the user needs to do **import a plan, open Structures, and see BODY with organs and tumours, without Applicator rows**.
- Therefore, I implemented/generated code so that **the medical physicist still gets the external BODY outline on the Structures list after #149 hid OTHER ROIs**.

#### Data Modeling and Integrity

- This data **Structures list** is modeled as **a `tuple[Structure, ...]` of organs, tumours and EXTERNAL** because **BODY is the patient outline, not a needle**. We considered alternative models such as **keeping every OTHER ROI, which would bring Applicators back**.
- This data **Structures list** uses the input validation to ensure it adheres to **`ORGAN`, `TUMOUR`, or `interpreted_type == "EXTERNAL"`**.
- Not applicable: **security sanitization, privacy sanitization, encryption, access controls (no network or logins)**.

#### Backend

- The system uses **an EXTERNAL keep-clause in `anatomy_structures`** because **#149's ORGAN/TUMOUR filter mapped BODY to OTHER**. Benefits for using this pattern include **the view already calls that helper**. Possible risks include **dropping BODY again if its type is missing**.
  - To mitigate **an empty Ex1 list**, we implemented **`test_structures_tab_shows_body_on_ex1_and_hides_needles` asserting one BODY row**.
  - We considered alternative solutions such as **matching the name BODY, which would miss a renamed outline**.
- The system architecture diagram consists of the following major components: **presentation, application state, domain services, libraries, local storage**. This structure has low coupling because **`DicomData.structures` is unchanged**. This structure has high cohesion because **the keep rule stays in `structure_list.py`**. This design is scalable because **a later type filter can still reuse `anatomy_structures`**. [system architecture](docs/architecture/diagrams/system-architecture.svg)
- The system uses **synchronous data processing** because **the list is rebuilt on `StructuresModel.changed`**. This method is done by **`action_update_structure_list` calling `anatomy_structures`**. Benefits for using this approach include **Import still shows every ROI**. Possible risks include **auto-drawing BODY on open**.
  - To mitigate **a heavy EXTERNAL mesh on tab open**, we implemented **leaving BODY unchecked until the physicist selects it**.
  - We considered alternative solutions such as **default-visible BODY, which #151 left out of scope**.
- The system adopts a **stateful** approach to state management because **`StructuresModel.structures` still holds every ROI**. This method is done by **filtering only the view's rows**. Benefits for using this approach include **a failed import still clears the model**. Possible risks include **calling `set_visible` on a hidden needle**.
  - To mitigate **turning on a needle from this tab**, we implemented **still omitting BRACHY_CHANNEL and MARKER**.
  - We considered alternative solutions such as **clearing OTHER from the model, which would drop Import rows**.
- The Level 0 DFD consists of the following major components: **TPS, physicist, printer, brachify**. **Unchanged; the filter is display-only**. [DFD level 0](docs/architecture/diagrams/existing-framework/dfd-0.svg)
- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem, Export**. **Happy path unchanged**. **Failure path unchanged**. [DFD level 1](docs/architecture/diagrams/existing-framework/dfd-1.svg)
- Not applicable: **database (none), backend API (none), traceability matrix (FR-SV not complete), test coverage (no coverage tool)**.

#### Review and design

- When I reviewed the **`anatomy_structures` filter from #149** for this functionality, I noticed **BODY is EXTERNAL mapped to OTHER, so it was dropped**. Therefore, I did **keep `interpreted_type == "EXTERNAL"`**.
- The PR does not contain any temporary workaround because **the keep rule is the DICOM interpreted type, not a BODY name match**.
- The PR only contains small functions that are **16 lines** long (`anatomy_structures`).
- I did **run `PYTHONPATH=agent-skills/anti-slop-py/src python -m anti_slop review --base origin/main src tests utils` (no findings)** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`structure_list.py`** because **`StructuresView` already calls `anatomy_structures`**.
- This work belongs in **Import's follow-on Structures page** in the DFD because **the list is display-only and Export is unchanged**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_anatomy_structures_keep_organs_tumours_and_body`, `test_structures_tab_shows_body_on_ex1_and_hides_needles`, `test_structures_tab_lists_only_organs_and_tumours` (7 passed in those files)** passed.
- I wrote tests to cover abnormal situations involving **`anatomy_structures(None)` and `anatomy_structures(())`** and they passed.
- I checked that these negative cases involving **keeping Applicator26 or a marker, or dropping BODY** failed as expected.
- Among these tests, **`test_anatomy_structures_keep_organs_tumours_and_body`** is a unit test and **`test_structures_tab_shows_body_on_ex1_and_hides_needles`, `test_structures_tab_lists_only_organs_and_tumours`** are integration tests.
- These tests are included in the directory **`tests/dicom/` and `tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` is 297 passed, 21 failed**. The 21 are scipy/skimage surface tests, `test_the_default_dome_tandem_cut_out_is_unchanged`, and three 20 px layout cases. New list tests passed.
  **[author: attach a screenshot of the pytest run showing the new tests and the 297 passed / 21 failed total]**
  **[author: attach a screenshot of Ex1 Structures listing BODY and no Applicator rows]**

## Stack #154 then colour, at a glance

Seven stacked PRs for Structures selection, colour and black copy. Each PR is based on the one above it and closes its own issue. A row's counts are **that PR's own diff only**.

| PR | On | Closes | What this PR adds | Own diff (files, lines) | New tests | Suite after |
|---|---|---|---|---|---|---|
| [#154](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/154) | `main` | #111 | Highlight the selected organ in channel-selection blue | 6, code and tests | 4 | 322 collected, 318 passed / 4 failed |

The suite had 318 tests on `main` before #154. The four failures are pre-existing (`test_the_default_dome_tandem_cut_out_is_unchanged` and three 20 px layout cases). Counts were collected with `pytest --collect-only` and a full `python -m pytest` on this branch.

### Shared by every PR in this stack

Stated once here instead of in each section.

- **Code quality checklist.** For each PR, I did **`anti_slop review --base <parent>` (no findings) and a read of that PR's own diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- **Regression checks.** Every PR's regression receipt also includes **`python docs/architecture/build.py --check` and `session-start.sh`, both exit 0**. Each section gives only its own `python -m pytest` result.
- **Not applicable in every PR.** **Encryption and access controls (no stored secrets, no user roles), restricted pages (no logins), usability evaluation (none run), backend API (none), database (none), test coverage (no coverage tool), security sanitization (no network input), privacy sanitization (no new patient fields)**.

### For PR #**154** (1 of 7, on `main`)

- As part of requirement **FR-SV-01**, the user needs to do **import a plan with organs, open Structures, click a row, and see that organ emphasised in the preview**.
- Therefore, I implemented/generated code so that **the medical physicist can highlight one listed organ in the channel-selection blue, and click it again to clear**.

#### Backend

- The system uses **one optional ROI on `StructuresModel`** because **FR-SV-01 is display-only and the highlight must not rebuild meshes**. Benefits for using this pattern include **`set_highlight` is testable without a native canvas**. Possible risks include **highlighting a row that has no contours**.
  - To mitigate **adding a shape for an empty organ**, we implemented **`set_highlight` stores the ROI and does not call `_enable`**.
  - We considered alternative solutions such as **hiding the colour in the list font, which would not change the preview**.
- The system architecture diagram consists of the following major components: **as in #149, plus `highlight_changed`**. This structure has low coupling because **the viewport reads `color_for` and `highlighted` and does not own the ROI**. This structure has high cohesion because **selection state stays on the model**. This design is scalable because **a colour override can reuse `structure_display_rgb`**.
  **[system architecture](docs/architecture/diagrams/system-architecture.svg)**
- The system uses **synchronous data processing** because **a list click must recolour existing actors immediately**. This method is done by **`highlight_changed` calling `update_structure_highlight`**. Benefits for using this approach include **no worker and no mesh rebuild**. Possible risks include **stale actors after a plan clear**.
  - To mitigate **a leftover highlight**, we implemented **`clear` setting `highlighted` to `None`**.
  - We considered alternative solutions such as **rebuilding anatomy on every click**.
- The system adopts a **stateful** approach to state management because **one ROI is highlighted at a time**. This method is done by **`set_highlight(roi | None)`**. Benefits for using this approach include **a second click can pass `None` while the row stays current**. Possible risks include **leaving the highlight after leaving Structures**.
  - To mitigate **the highlight surviving a new plan**, we implemented **clearing it in `clear`**.
  - We considered alternative solutions such as **tying it to checkbox visibility**.
- The Level 0 DFD consists of the following major components: **as in #149**. **Unchanged; highlight is display-only**. [DFD level 0](docs/architecture/diagrams/existing-framework/dfd-0.svg)
- The Level 1 DFD consists of the following major processes: **as in #149**. **Happy path unchanged**. **Failure path unchanged**. [DFD level 1](docs/architecture/diagrams/existing-framework/dfd-1.svg)
- Not applicable: **database (none), backend API (none)**.

#### Frontend

- The frontend is designed using **PySide6** with design components for **the existing Structures `QListWidget`**. Therefore, changing the design of **that list** will automatically change the look and feel of all instances of that component throughout the system. Changes to the content will not affect the design because **row text still comes from `structure_list_rows`**.
- Not applicable: **data caching (no backend fetch), new copy (no `setText` added)**.

#### Review and design

- When I reviewed the **surface presentation colour** for this functionality, I noticed **DICOM RGB would hide which row was selected**. Therefore, I did **return `(0.2, 0.2, 0.7)` from `structure_display_rgb` when highlighted**.
- The PR does not contain any temporary workaround because **the blue is the Channels selection colour, not a one-off**.
- The PR only contains small functions that are **16 lines** long (`update_structure_highlight`).
- Code quality checklist: **see Shared**.
- This work is written in **`structures_model.py` and `viewport.py`** because **the ROI lives on the model and the actors live on the canvas**.
- This work belongs in **Import's follow-on Structures page** in the DFD because **the highlight is display-only and Export is unchanged**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_selecting_a_structure_highlights_only_that_organ`, `test_highlighted_surface_uses_the_channel_selection_colour` (4 new)** passed.
- I wrote tests to cover abnormal situations involving **`test_highlighting_an_organ_without_contours_adds_no_presentation`** and they passed.
- I checked that these negative cases involving **`test_clicking_the_highlighted_row_again_drops_the_highlight`** failed as expected.
- Among these tests, **`test_highlighted_surface_uses_the_channel_selection_colour`** is a unit test and **`test_selecting_a_structure_highlights_only_that_organ`, `test_clicking_the_highlighted_row_again_drops_the_highlight`, `test_highlighting_an_organ_without_contours_adds_no_presentation`** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` is 318 passed, 4 failed (4 new, 318 collected on `main`)**. The four failures are pre-existing and not from this diff: `test_the_default_dome_tandem_cut_out_is_unchanged`, `test_channels_settings_keep_their_height_in_the_default_window`, `test_cylinder_spin_boxes_keep_their_height_in_the_default_window`, `test_the_cylinder_tab_never_scrolls_sideways_in_the_default_window`.
  **[author: attach a screenshot of the pytest run showing the 4 new tests and 318 passed / 4 failed]**
  **[author: attach a screenshot of Structures with one organ highlighted blue]**
