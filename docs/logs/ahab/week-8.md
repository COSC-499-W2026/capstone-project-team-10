# Week 8, Ahab

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**184**

- As part of requirement **FR-CN-01, create custom needles, and FR-CN-07, they reach the 3D export and the PDF**, the user needs to do **import Ex1, press Add Applicator..., type a name, a start on the base and two lengths, press OK, then export the STL and the PDF**.
- Therefore, I implemented/generated code so that **medical physicists can add a straight custom applicator that is listed, drawn, cut and put on the sheet like a plan needle**.

#### Data Modeling and Integrity

- This data **`CustomNeedleSpec`** is modeled as **a frozen dataclass of floats** because **the dialog, model and builder share one value that cannot change on the way**. We considered alternative models such as **a dict, which anti-slop bans for inward values**.
- This data **`CustomNeedleSpec`** uses the input validation to ensure it adheres to **finite numbers, lengths above 0 mm, Length 1 at most the cylinder length, a start within the radius less the needle radius, and a name not blank or repeated**.
- Not applicable: **security, privacy, encryption, access controls (typed numbers, nothing stored)**.

#### Backend

- The system architecture diagram consists of the following major components: **External, Presentation, Application state, Domain services, Libraries and Local storage**. This structure has low coupling because **the dialog reaches the rules only through `ChannelsModel.custom_needle_error`**. This structure has high cohesion because **`custom_needle_points` alone turns numbers into points**. This design is scalable because **the bend adds fields to the spec and one step to the builder**.

  **[System architecture (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74b0d97b3381c4d7ecc1b4e2d9eedef3d0c3734b/docs/architecture/diagrams/system-architecture.svg)**
- The Level 0 DFD consists of the following major components: **medical physicist, treatment planning system, brachify and printer or CAD**. **A typed needle comes out in the STL and the PDF**.

  **[DFD level 0 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74b0d97b3381c4d7ecc1b4e2d9eedef3d0c3734b/docs/architecture/diagrams/existing-framework/dfd-0.svg)**
- The Level 1 DFD consists of the following major processes: **Import, Cylinder, Channels, Tandem and Export**. **Channels takes the numbers, ChannelsModel builds the points and the channel, and Export cuts it**. **A start 50 mm out raises `CustomNeedleError` and the dialog stays open showing the text (screenshot 1, panel 3)**.

  **[DFD level 1 (SVG), unchanged by this PR](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/74b0d97b3381c4d7ecc1b4e2d9eedef3d0c3734b/docs/architecture/diagrams/existing-framework/dfd-1.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **FR-CN-01 → `test_the_points_run_from_the_tissue_end_down_to_the_base`, `test_add_applicator_offers_the_first_free_name_and_adds_a_row_and_cancel_adds_nothing`; FR-CN-07 → `test_the_export_cut_removes_the_new_needle_from_the_cylinder`, `test_the_reference_sheet_lists_the_new_applicator_with_its_own_number`**
- Not applicable: **architectural pattern, database, data processing, state management, backend API (unchanged or none), test coverage (no tool)**.

#### Frontend

- The frontend adopts accessibility principle **WCAG 3.3.1, Error Identification**. The aspects that demonstrate this principle in the system include **a refused start is explained in words under the fields, with no colour needed (screenshot 1, panel 3)**.
- Not applicable: **data caching, restricted pages, design components, usability evaluation, traceability matrix (in Backend), test coverage (none)**.

#### Review and design

- When I reviewed the **new button's route through the `.ui`**, I noticed **it made the PR 10 files and over 500 lines with the regenerated `channels_view_ui.py`**. Therefore, I did **build the button in `ChannelsView.__init__` and leave the `.ui` alone**.
- The PR does not contain any temporary workaround because **the only gap, no bend yet, is the next PR's scope and every refusal is real**.
- The PR only contains small functions that are **at most 24 lines (`AddApplicatorDialog.__init__`)** long.
- I did **`anti_slop review --base main src tests utils` (three `shape` name warnings that AGENTS.md rule 6 says to ignore) and a line-by-line read of the diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`helper.py`, `channels_model.py` and `channels_view.py`** because **a new module needs the architecture diagram redrawn, and these hold the geometry helpers, channel state and Channels tab**.
- This work belongs in **3 Channels** in the DFD because **it is another way to create a channel**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_an_added_applicator_is_visible_and_its_solid_opens_through_the_base`, `test_the_export_cut_removes_the_new_needle_from_the_cylinder` and `test_the_reference_sheet_lists_the_new_applicator_with_its_own_number` (20 new)** passed.
- I wrote tests to cover abnormal situations involving **a blank or imported name, no plan, a length change after adding, and Cancel** and they passed.
- I checked that these negative cases involving **four deliberate breaks (points reversed, height offset dropped, a repeated name allowed, the dialog closing on bad numbers)** failed as expected.
- Among these tests, **the 10 in `test_custom_needle_points.py`** are unit tests and **the 10 in `test_add_custom_needle.py`** are integration tests through the real window.
- These tests are included in the directory **`tests/mesh/` and `tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest` (321 passed, 17 failed, all in the structure surface tests with library failure, since `scipy` and `skimage` are not in the conda env), `build.py --check` and `session-start.sh` (exit 0), and brachify run on macOS with Ex1, driven by a script that pressed the real button, then an STL and a PDF exported (screenshot 1, whose panel 6 is the pytest result text drawn from the real output)**.

  ![1, Ex1 on macOS, the Add Applicator... button, the new row, a refused start, the 3D views and the pytest run](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/0f08474df7f5efe25818e39c924932b4c142199c/docs/logs/ahab/screenshots/week-8/pr-184-1-add-applicator.png)

- Not applicable: **generated-test review (no problem found)**.
