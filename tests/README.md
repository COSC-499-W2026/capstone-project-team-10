# Tests

> **This file is part of the documentation set**, the markdown files the team owns.
> The whole set is reviewed on every pull request and updated in the same PR when affected. Update this file whenever a test scope
> folder is added, the runner configuration changes, or the priority list below shifts. See
> §9.0 of [the source of truth](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md).

This project follows **test-driven development**, including the superpowers iron law: no
production code without a failing test first. Code written before its test is deleted and
rewritten from the test. Every session loads the superpowers `test-driven-development` skill
at start. See [Session start](../AGENTS.md#session-start) and
[Testing: write the test first](../AGENTS.md#testing-write-the-test-first) in
[AGENTS.md](../AGENTS.md) for the full rules: what to test, what cannot be tested here, and
[Anti-slop](../AGENTS.md#anti-slop), including the rule against mocking application modules.

## Layout rule, for humans and AI agents alike

**Every test file lives in a subfolder scoped to the part of `src/` it covers. Never put a
loose test file at the root of `tests/`.**

The subfolder name mirrors the `src/` path under test:

| Tests for | Goes in |
|---|---|
| `src/windows/views/` | `tests/views/` |
| `src/windows/models/` | `tests/models/` |
| `src/classes/mesh/` | `tests/mesh/` |
| `src/classes/dicom/` | `tests/dicom/` |
| `src/classes/pdf/` | `tests/pdf/` |
| `src/settings/` | `tests/settings/` |
| repository files outside `src/`: `build_executable.py`, `.gitattributes`, `docs/architecture/build.py` | `tests/tooling/` |

Create the subfolder if it does not exist yet. Add a row above when you create a new scope.

```
tests/
├── README.md
├── conftest.py            fixtures shared by everything
├── data/                  sample inputs, never beside a test file
├── dicom/
│   ├── conftest.py        fixtures used only by dicom tests
│   └── test_fileio.py
├── mesh/
│   └── test_helper.py
├── models/
├── pdf/
├── settings/
│   └── test_load.py
├── tooling/               exists: build, line-ending and architecture diagram checks
│   ├── test_build_executable.py
│   └── test_line_endings.py
└── views/
```

Only `tooling/` exists so far. The rest of the tree shows where tests will go.

Naming: `test_<module>.py`, mirroring the module under test. A test for
`src/classes/mesh/helper.py` is `tests/mesh/test_helper.py`.

## Every function explains itself

Every test, helper and fixture in `tests/` has a docstring saying what it checks, how it
fails, and why that failure matters. A `#` comment that only repeats the docstring is deleted.
The full rule is in
[AGENTS.md](../AGENTS.md#every-function-in-tests-explains-itself). For example, from
[tooling/test_build_executable.py](tooling/test_build_executable.py):

```python
@pytest.mark.parametrize("module_name", build_executable.HIDDEN_IMPORTS)
def test_hidden_import_exists_in_the_environment(module_name: str) -> None:
    """Import each module that build_executable.py tells PyInstaller to bundle.

    Runs once per entry in HIDDEN_IMPORTS and fails with ModuleNotFoundError if that module
    cannot be imported in the current conda environment. PyInstaller only logs
    "ERROR: Hidden import ... not found" for a missing module and still builds with exit 0,
    so a module renamed upstream (as pydicom 3 did with pydicom.encoders) would silently drop
    out of brachify.exe. This test makes that failure loud.
    """
    importlib.import_module(module_name)
```

Fixtures shared across the whole suite go in `tests/conftest.py`. Fixtures used by one area go
in that area's own `conftest.py`. Sample data goes in `tests/data/`, never next to a test file.

## Running the tests

From the repository root, in the conda environment (which includes `pytest`, see §1.1 of the
[project docs](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md)):

```bash
python -m pytest
```

[pytest.ini](../pytest.ini) sets `testpaths = tests` and `pythonpath = src .`. Every module in
this project imports as though `src/` were the root (`from classes.app import get_app`), and
the root is on the path for tests of root-level files such as `build_executable.py`.
[`.vscode/settings.json`](../.vscode/settings.json) points VS Code's test runner at `tests`.

Nothing in `src/` has a test yet. The first test of application code starts at the top of the
list below.

`benchmarks/` is **not** a test suite. It is stale, broken code kept only for reference.

## What to test first

§8 of [the project docs](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md) carries the ranked
list of highest-value targets. All are pure functions needing neither Qt nor OpenCASCADE:

1. `helper.rotate_points()` — the DICOM to cylinder transform. Wrong here means every needle
   in every model is wrong.
2. `settings/load.py` — pure dict logic, and the collar round-trip bug in §7.1 of the project
   docs would have been caught by a single assertion here.
3. The point cleanup functions in `mesh/channel.py`.
4. `template_reference.extract_points_from_channels2()` — all three `z=0` branches.

Keep §8 updated as tests land.
