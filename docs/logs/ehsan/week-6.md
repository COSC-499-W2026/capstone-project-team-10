# Week 6, Ehsan

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

### For PR #**28**

- As part of requirement **FR-CN-13: import a config, use defaults for missing keys and report
  them**, the user needs to do **load a saved config file and be told which settings came from
  it**.
- Therefore, I implemented/generated code so that **the medical physicist gets a config loader
  that rejects `true` and `false` as dimensions, with tests for a partial file, an unreadable
  file and a `true` value**.

#### Data Modeling and Integrity

- This data **a config file** is modeled as **a flat JSON object of `CONFIG_*` keys to numbers**
  because **`DEFAULT_CONFIG_VALUES` is that schema**. We considered alternative models such as
  **a dataclass per setting group, which would change every caller**.
- This data **each config value** uses the input validation to ensure it adheres to **an `int`
  or `float` that is not a `bool` (`is_config_number`)**.
- This data config file may be vulnerable to a security issue — **N/A**, it is a local file the
  user chose.
- This data config file may be vulnerable to a privacy issue — **N/A**, it holds no patient data.
- This data stores sensitive information and uses encryption — **N/A**, it holds no sensitive
  data.
- The data has access controls — **N/A**, brachify has no users.

#### Backend

- The system uses an architectural pattern — **N/A**, the PR changes no pattern.
- The system architecture diagram — **N/A**, no component changed.
- The system uses a database — **N/A**, brachify has no database.
- The system uses synchronous or asynchronous data processing — **N/A**, no processing changed.
- The system adopts a stateful or stateless approach — **N/A**, state handling is unchanged.
- The Level 0 DFD — **N/A**, no flow changed.
- The Level 1 DFD — **N/A**, no process changed.
- The backend API — **N/A**, brachify has no network API.
- The following traceability matrix — **N/A**, no requirement is complete yet.
- By using a coverage tool — **N/A**, none is configured.

#### Review and design

- When I reviewed the **`checkValuesExist` number check** for this functionality, I noticed
  **`true` passes `isinstance(value, int)` (the test failed with `assert True == 30.0`)**.
  Therefore, I did **reject `bool` before the number check**.
- When I reviewed the **first fix with the anti-slop review**, I noticed **a
  `no-adhoc-isinstance` warning on the inline check**. Therefore, I did **move it into
  `is_config_number() -> TypeGuard[int | float]`**.
- The PR does not contain any temporary workaround because **every value goes through one
  named check**.
- The PR only contains small functions that are **3 to 16 lines (counted with `ast`)** long.
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
- This work is written in **`src/settings/load.py`** because **it owns config loading**.
- This work belongs in **process 1, Import** in the DFD because **the config JSON is read
  there**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving
  **`test_partial_file_loads_its_keys_and_reports_the_rest_missing`** passed.
- I wrote tests to cover abnormal situations involving **`test_unreadable_file_falls_back_to_defaults`
  and `test_true_is_not_accepted_as_a_dimension`** and they passed.
- I checked that these negative cases involving **the `true` test before the fix and with the
  `bool` check removed (`assert True == 30.0`), and the partial-file test with two keys
  required to count (`assert 0 == 1`)** failed as expected.
- When I reviewed the **`test_unreadable_file_falls_back_to_defaults`**, I noticed **it passed
  the first time, so it proves nothing on its own**. Therefore, I did **keep it as the guard
  that a broken file is not counted as loaded**.
- Among these tests, **all three** are unit tests and integration tests are not required
  because **`load.py` only reads a file and returns values**.
- These tests are included in the directory **`tests/settings/`**.
- This new test PR did not break anything else in the system because **`python -m pytest`
  passed 22 of 22 on Windows after merging `main`, skipping `test_build_executable.py`,
  `tests/views/`, `tests/windows/` and `test_structures.py` (need conda). The app was not run
  and there is no screenshot**.

### For PR #**44**

- As part of requirement **FR-SV-01 (backend) and issue #40**, the user needs to do **import a DICOM folder and have decoded structures on DicomData**.
- Therefore, I implemented/generated code so that **import calls load_structures after reading the RTSTRUCT, and reset clears structures**.

#### Data Modeling and Integrity

- This data **DicomData.structures** is modeled as **None or a tuple of Structure** because **that is what read_structures returns**. We considered alternative models such as **a separate GUI model, out of scope for #40**.
- This data **structures** uses the input validation to ensure it adheres to **StructureReadError; failures set structures to None**.
- This data may be vulnerable to a security issue — **N/A**, local DICOM only.
- This data may be vulnerable to **another plan's anatomy surviving a failed decode**. Therefore, it uses a privacy-based sanitization by **setting structures to None on StructureReadError**. We considered alternative privacy solutions such as **aborting the whole import, which would also drop the needles**.
- This data stores sensitive information and uses encryption — **N/A**, no new persistence.
- The data has access controls — **N/A**, brachify has no users.

#### Backend

- The system uses an architectural pattern — **N/A**, no pattern change.
- The system architecture diagram — **updated**: domain dicom line now names load_structures. Low coupling because **that module only depends on data, structures and the logger**. `build.py --check` exits 0.
- The system uses a database — **N/A**, brachify has no database.
- The system uses synchronous or asynchronous data processing — **N/A**, unchanged.
- The system adopts a stateful or stateless approach — **N/A**, unchanged.
- The Level 0 DFD — **N/A**, no external flow changed.
- The Level 1 DFD — **N/A**, no process flow changed.
- The backend API — **N/A**, no network API.
- The following traceability matrix — **N/A**, FR-SV-01 is not complete yet.
- By using a coverage tool — **N/A**, none is configured.

#### Review and design

- When I reviewed the **first wiring inside fileio.py** for this functionality, I noticed **the tests could not import fileio without numpy and the mesh stack**. Therefore, I did **move load_structures into its own module**.
- The PR does not contain any temporary workaround because **both vendor readers call the same function**.
- The PR only contains small functions that are **11 to 18 lines (fixture 27, counted with ast)** long.
- I did **read the full diff, run anti-slop (no findings), and break load_structures on purpose** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **src/classes/dicom/load_structures.py** because **tests can import it without the vendor readers**.
- This work belongs in **process 1, Import** in the DFD because **fileio calls it while loading the RTSTRUCT**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **test_load_structures_fills_dicom_data_from_rtstruct (4 passed with pydicom)** passed.
- I wrote tests to cover abnormal situations involving **test_load_structures_clears_structures_when_decode_fails** and they passed.
- I checked that these negative cases involving **reset without clearing structures, empty-tuple attach, and leaving a previous value on StructureReadError** failed as expected.
- When I reviewed the **test importing fileio**, I noticed **it needed the full conda stack**. Therefore, I did **import the thin module and verify Ex1 yields 42 structures**.
- Among these tests, **all four** are unit tests and integration tests are not required because **load_structures only writes one field**.
- These tests are included in the directory **tests/dicom/**.
- This new test PR did not break anything else in the system because **build.py --check and anti-slop passed. The GUI was not run, so there is no screenshot**.

### For PR #**77**

- As part of requirement **the course documentation receipts for FR-SV-01 / issue #40**, the user needs to do **open the source of truth and see that folder import attaches decoded structures**.
- Therefore, I implemented/generated code so that **teammates reading the docs get the `load_structures` wiring, test inventory and this Part A recorded**.

#### Review and design

- When I reviewed the **§3.3 contribution paragraph** for this functionality, I noticed **it still said the RTSTRUCT reader was not connected to the GUI import path**. Therefore, I did **rewrite that sentence to match §5.3 and the #44 call sites**.
- When I reviewed the **`tests/README.md` "exist" sentence**, I noticed **`test_load_structures.py` was only in the tree**. Therefore, I did **add it to that sentence**.
- I did **diff the docs against #44's `load_structures` calls, count 22 `DicomData` fields, and drop the init-guide out-of-date note** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- This work is written in **`docs/project/COSC499-TEAM10-PROJECT-DOCS.md`, `tests/README.md` and `docs/logs/ehsan/week-6.md`** because **those are the documentation-set files left stale by #44**.
- Not applicable: **temporary workaround, function length, DFD process (no code changed)**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`rg` for the old "not yet connected" sentence (no hits) and a 22-field count of `DicomData.__init__`** passed.
- This new test PR did not break anything else in the system because **`python docs/architecture/build.py --check` exits 0 on this branch. No `src/` change; no GUI run**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no code, the checks are shell commands)**.
