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
