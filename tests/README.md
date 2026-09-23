# Tests

> **This file is part of the documentation set.** Every markdown file in `docs/`, `tests/` and
> `utils/`, plus the root-level `README.md`, `AGENTS.md` and `CLAUDE.md`, is reviewed on every
> pull request and updated in the same PR when affected. Update this file whenever a test scope
> folder is added, the runner configuration changes, or the priority list below shifts. See
> §9.0 of [the source of truth](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md).

This project follows **test-driven development**, including the superpowers iron law: no
production code without a failing test first. Code written before its test is deleted and
rewritten from the test. See [Session start](../AGENTS.md#session-start) and
[Testing: write the test first](../AGENTS.md#testing-write-the-test-first) in
[AGENTS.md](../AGENTS.md) for the full rules, including anti-slop.

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
└── views/
```

Naming: `test_<module>.py`, mirroring the module under test. A test for
`src/classes/mesh/helper.py` is `tests/mesh/test_helper.py`.

Fixtures shared across the whole suite go in `tests/conftest.py`. Fixtures used by one area go
in that area's own `conftest.py`. Sample data goes in `tests/data/`, never next to a test file.

## Before the first test runs

The suite is not yet configured. The first change that adds a test must also:

1. Put `src/` on `sys.path`, either with a root `conftest.py` or `pythonpath = ["src"]` in a
   `pytest.ini` / `pyproject.toml`. Every module in this project imports as though `src/` were
   the root (`from classes.app import get_app`), so nothing imports without this.
2. Fix [`.vscode/settings.json`](../.vscode/settings.json), which currently points pytest at a
   `testing/` directory that does not exist. It should read `["tests"]`.

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
