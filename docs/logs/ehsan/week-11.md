# Week 11, Ehsan

_Individual log. One section per PR merged this week, each a copy of that PR's Part A. See
[docs/logs/README.md](../README.md)._

## Stack #273 to #274, at a glance

Two stacked PRs for conda setup automation. Each is based on the one below it, closes its own issue or documents the stack, and should be retargeted to main once its parent merges. A row's counts are that PR's own diff only.

| PR | On | Closes | What this PR adds | Own diff (files, lines) | New tests | Suite after |
|---|---|---|---|---|---|---|
| [#273](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/273) | `main` | #167 | conda create helper | 8, +274/−3 | 5 | tooling test_conda_env 5 passed |
| [#274](https://github.com/COSC-499-W2026/capstone-project-team-10/pull/274) | #273 | — | AGENTS pointer and Part A log | 2 | 0 | inherited |

### Shared by every PR in this stack

- Code quality checklist: **`PYTHONPATH=agent-skills/anti-slop-py/src python -m anti_slop review --base origin/main src tests utils` reported no findings on the code PR. `python docs/architecture/build.py --check` exited 0.**
- Not applicable: **database (none), backend API (none), security sanitization, privacy sanitization, encryption, access controls (no network or logins), restricted pages (no logins), usability evaluation (none run), test coverage (no coverage tool)**.

### For PR #**273** (1 of 2, on main)

- As part of requirement **developer setup for brachify**, the user needs to do **install conda, then create the project environment for their OS in one step**.
- Therefore, I implemented/generated code so that **a teammate prints or runs the correct `conda create` without memorising Windows versus macOS package lists**.

#### Backend

- The system uses **an OS-branching command builder** because **Windows must use `spec-file.txt` and Unix must name every §1.1 package on conda-forge**. Benefits for using this pattern include **one entry point and tests that lock the argv**. Possible risks include **someone running it without conda installed**.
  - To mitigate **a missing conda**, we implemented **`--run` checking `PATH` and exiting 1 with a message**.
  - We considered alternative solutions such as **Docker, which §1.11 rejects for this desktop GUI**.
- The system architecture diagram consists of the following major components: **presentation, application state, domain services, libraries, local storage**. This structure has low coupling because **the helper lives in `utils/` and is not imported by the app**. This structure has high cohesion because **create argv stays in one module**. This design is scalable because **a new named package is one tuple entry plus the §1.1 table**. [system architecture](https://github.com/COSC-499-W2026/capstone-project-team-10/blob/main/docs/architecture/diagrams/system-architecture.svg)
- The system uses **synchronous data processing** because **conda create is a blocking local install**. This method is done by **`subprocess.run` on the built argv when `--run` is set**. Benefits for using this approach include **the exit code is conda's**. Possible risks include **a long download with no progress UI**.
  - To mitigate **surprise installs**, we implemented **dry-run as the default**.
  - We considered alternative solutions such as **always running create, which would recreate envs by accident**.
- Not applicable: **database, Level 0/1 DFD redraw (no app edge changed), traceability matrix, stateful clinical model**.

#### Review and design

- When I reviewed the **setup docs** for this functionality, I noticed **Windows and macOS already had different create commands and newcomers had to pick the right one**. Therefore, I did **add §1.2a and a tested helper that picks for them**.
- The PR does not contain any temporary workaround because **the helper only builds documented conda argv**.
- The PR only contains small functions that are about **20 lines** long (`conda_create_argv`).
- Code quality checklist: **see Shared**.
- This work is written in **`utils/common/`** because **setup is not runtime app code**.
- Not applicable: **frontend, temporary clinical workaround**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`tests/tooling/test_conda_env.py` (5 new)** passed.
- I wrote tests to cover abnormal situations involving **an unknown platform raising ValueError** and they passed.
- I checked that these negative cases involving **Windows create without `--file`** failed as expected.
- Among these tests, **the five cases** are unit tests and integration tests are not required because **no Qt or DICOM is involved**.
- These tests are included in the directory **`tests/tooling/`**.
- This new test PR did not break anything else in the system because **`python -m pytest tests/tooling/test_conda_env.py -q` is 5 passed, and anti-slop reported no findings**.
- Not applicable: **generated-test review**.

### For PR #**274** (2 of 2, on #273)

- As part of requirement **developer setup for brachify**, the user needs to do **find the one-command create from AGENTS.md and the weekly log**.
- Therefore, I implemented/generated code so that **agents and the grader see the §1.2a entry point and Part A for this stack**.

#### Review and design

- When I reviewed the **agent environment block** for this functionality, I noticed **AGENTS.md still only showed the raw Windows lockfile command**. Therefore, I did **add the `setup_conda_env` lines next to it**.
- Code quality checklist: **see Shared**.
- This work is written in **`AGENTS.md` and `docs/logs/ehsan/week-11.md`** because **agent guidance and Part A live there**.
- Not applicable: **backend, frontend, temporary workaround, function length**.

#### Testing receipts

- The functionality works correctly because the happy path tests involving **`python docs/architecture/build.py --check` (exit 0)** passed.
- This new test PR did not break anything else in the system because **the diff against #273 is documentation only**.
- Not applicable: **abnormal cases, negative cases, generated-test review, unit and integration tests, test directory (no code, the check is `build.py --check`)**.
