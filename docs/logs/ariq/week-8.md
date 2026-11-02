# Week 8, Ariq

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

## Stack #174 to #179, at a glance

Six stacked PRs that move the tandem channel choice to the Tandem tab and stop a tandem channel
being exported without its hole. Each PR is based on the one above it and closes its own issue.
A row's counts are **that PR's own diff only**, as GitHub shows it against its parent.

| PR | On | Closes | What this PR adds | Own diff (files, lines) | New tests | Suite after |
|---|---|---|---|---|---|---|
| [#174](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/174) | `main` | #168 | Clearing the tandem channel, the Ex2 fixture | 8, +193/−14 | 3 | 321 |

The suite had 318 tests on `main` before #174 (`1f34b40`).

### Shared by every PR in this stack

Stated once here instead of in each section.

- **Code quality checklist.** For each PR, I did **`anti_slop review --base <parent branch>` (no findings) and a read of that PR's own diff** to ensure that my feature contribution does not contain any of the following:
  - hardcoded values
  - duplicate code
  - dead code
  - unnecessary function calls
  - excessive conditional logic
  - deep nesting
  - high cyclomatic complexity
  - classes/modules/functions with many unrelated responsibilities
- **Regression checks.** Every PR's regression receipt also includes **`build.py --check` and `session-start.sh`, both exit 0, and an end-to-end run of the real window on the top of the stack, #179, with Ex2, then Ex1, then a third Varian plan whose tandem is channel 1**. Each section gives only its own `python -m pytest` result.
- **Not applicable in every PR.** **Encryption and access controls (no stored secrets, no user roles), database (none), restricted pages (no logins), usability evaluation (none run), backend API (none), test coverage (no coverage tool)**.

### For PR #**174** (1 of 6, on `main`)

- As part of requirement **issue #168, a plan with no tandem channel**, the user needs to do **clear a plan's tandem channel so that no channel is the tandem**.
- Therefore, I implemented/generated code so that **clinicians can clear the tandem channel without an error, the old tandem channel is cut as a needle again, and the tandem keeps its rotation**.

#### Backend

- The system uses **the existing Qt model and signal pattern, `ChannelsModel.set_tandem` emitting `tandem_changed` to `TandemModel.set_tandem_channel`** because **the models own the tandem state and every tab calls them**. Benefits for using this pattern include **#175's Tandem tab clears the tandem with one call**. Possible risks include **Qt prints an exception raised in a slot instead of raising it, so a broken slot fails silently**.
  - To mitigate **a silent slot failure**, we implemented **tests that read the rotation the slot sets, not only that nothing raised**.
- The system architecture diagram consists of the following major components: **views, QObject models, domain services, libraries and local storage**. This structure has low coupling because **only an existing signal's handling changed**. This structure has high cohesion because **`ChannelsModel` owns which channel is the tandem and `TandemModel` owns its rotation**. This design is scalable because **a tandem built from the plan's path could reuse the same signal**.

  **[System architecture, unchanged](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/1f34b40bcfbab59fc662d20e25a682f7b33b47ab/docs/architecture/diagrams/system-architecture.svg)**
- The following traceability matrix shows the list of requirements completed in this milestone and their associated tests: **#168: `tests/views/test_tandem_channel.py`, 3 tests**
- Not applicable: **data processing, state management, Level 0 DFD, Level 1 DFD (unchanged)**.

#### Review and design

- When I reviewed the **generated `set_tandem_channel`** for this functionality, I noticed **it dropped the `rotation` local that the branch for a channel named Tandem still used, so importing Ex2 raised `NameError` in the slot and left the tandem at 0°**. Therefore, I did **set the plan rotation from `self.rotation` and add the Ex2 import test, which failed at 0.0 first**.
- The PR does not contain any temporary workaround because **`set_tandem(None)` is the model's own clear, not a view-side patch**.
- The PR only contains small functions that are **8 and 14 lines (models) and 14 to 16 lines (tests)** long.
- Code quality checklist: **see Shared**.
- This work is written in **`channels_model.py` and `tandem_model.py`** because **each model owns its half of the tandem state**.
- This work belongs in **Channels and Tandem** in the DFD because **the tandem channel flows from Channels to Tandem**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`test_clearing_the_tandem_channel_makes_it_a_needle_again`, `test_importing_a_plan_with_a_tandem_channel_aims_the_tandem_along_it` (3 new; 3 in the file; screenshot 1)** passed.
- I wrote tests to cover abnormal situations involving **clearing after a needle, Applicator12, was the tandem, keeping its 208.37° rotation** and they passed.
- I checked that these negative cases involving **the code before the fix (`[None] == []`, rotation 0.0, and 0.0 instead of 359.996 at import)** failed as expected.
- Among these tests, **none** are unit tests and **all 3** are integration tests.
- These tests are included in the directory **`tests/views/`**.
- This new test PR did not break anything else in the system because **`python -m pytest`, 321 passed (318 on `main`, screenshot 1)**.

  ![1, python -m pytest on fix/tandem-channel-none, 3 passed in test_tandem_channel.py and 321 passed in the whole suite](https://raw.githubusercontent.com/COSC-499-W2026/capstone-project-team-10/40e32d755ba1d497b71cca7ccef0cc454e03386b/docs/logs/ariq/screenshots/week-8/pr-174-1-pytest-321-passed.png)
