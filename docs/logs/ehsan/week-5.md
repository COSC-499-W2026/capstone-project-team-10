# Week 5, Ehsan

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**26**

- As part of requirement **FR-SV-01 (backend): no partially imported dataset becomes active**,
  the user needs to do **import one patient's DICOM folder, then another, and see only the
  second patient's values**.
- Therefore, I implemented/generated code so that **the medical physicist gets a `DicomData`
  whose `reset()` clears every field, `central_axis_flag` included, and a test that names any
  field it misses**.

#### Data Modeling and Integrity

- This data **`DicomData`** is modeled as **a class of 21 fields, each `None` until a reader
  fills it** because **the Varian and Nucletron readers fill different fields**. We considered
  alternative models such as **a frozen dataclass per import, which changes every reader**.
- This data `DicomData` uses the input validation — **N/A**, `reset()` takes no input.
- This data `DicomData` may be vulnerable to a security issue — **N/A**, the PR adds no input
  path.
- This data **`DicomData`** may be vulnerable to **one patient's values surviving a failed
  import into the next**. Therefore, it uses a privacy-based sanitization by **`reset()`
  setting every field to `None`**. We considered alternative privacy solutions such as
  **relying on the new `DicomData` each import builds, which a failed import never reaches**.
- This data stores sensitive information and uses encryption — **N/A**, the PR stores nothing.
- The data has access controls — **N/A**, brachify has no users.

#### Backend

- The system uses an architectural pattern — **N/A**, the PR changes no pattern.
- The system architecture diagram — **N/A**, no component changed.
- The system uses a database — **N/A**, brachify has no database.
- The system uses synchronous or asynchronous data processing — **N/A**, no processing changed.
- The system adopts a **stateful** approach to state management because **`DicomModel` keeps
  one `DicomData` per session (`dicom_model.py` line 11)**. This method is done by
  **`ImportView` calling `reset()` before each import (`import_view.py` line 112)**. Benefits
  for using this approach include **every tab reads the same plan**. Possible risks include
  **a field `reset()` misses keeps the previous patient's value**.
  - To mitigate **a field missing from `reset()`**, we implemented **a test that reads the
    fields from `__init__` with `vars()`**.
  - We considered alternative solutions such as **listing the 21 names in the test, which a
    new field would skip**.
- The Level 0 DFD — **N/A**, no flow changed.
- The Level 1 DFD — **N/A**, no process changed.
- The backend API — **N/A**, brachify has no network API.
- The following traceability matrix — **N/A**, no requirement is complete yet.
- By using a coverage tool — **N/A**, none is configured.

#### Review and design

- When I reviewed the **`DicomData.reset()` against `__init__`** for this functionality, I
  noticed **`reset()` skipped `central_axis_flag` (the test failed naming it)**. Therefore, I
  did **add `self.central_axis_flag = None` to `reset()`**.
- When I reviewed the **generated documentation of the fix**, I noticed **nothing in `src/`
  reads `central_axis_flag`, so the leak could not reach a patient**. Therefore, I did **keep
  "never read" in §7.4 and describe the fix as guarding the rule**.
- The PR does not contain any temporary workaround because **the test covers fields added
  later**.
- The PR only contains small functions that are **8 and 13 lines (counted with `ast`)** long.
- I did **read the full diff and run the anti-slop review (no findings)** to ensure that my
  feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`src/classes/dicom/data.py`** because **it owns `DicomData`**.
- This work belongs in **process 1, Import** in the DFD because **`ImportView` calls `reset()`
  there**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_new_dicom_data_starts_with_every_field_empty`** passed.
- I wrote tests to cover abnormal situations involving **`reset()` after every field holds a
  leftover value (`test_reset_empties_every_field_that_init_declares`)** and they passed.
- I checked that these negative cases involving **the reset test before the fix (failed naming
  `central_axis_flag`) and with `self.operator = None` removed (failed naming `operator`)**
  failed as expected.
- When I reviewed the **`test_new_dicom_data_starts_with_every_field_empty`**, I noticed **it
  passed the first time, so it proves nothing on its own**. Therefore, I did **keep it as the
  guard that `None` means missing**.
- Among these tests, **both** are unit tests and integration tests are not required because
  **`data.py` imports nothing**.
- These tests are included in the directory **`tests/dicom/`**.
- This new test PR did not break anything else in the system because **`python -m pytest`
  passed 19 of 19 on Windows after merging `main`, skipping `test_build_executable.py` and
  `tests/views/` (need conda). The app was not run and there is no screenshot**.
