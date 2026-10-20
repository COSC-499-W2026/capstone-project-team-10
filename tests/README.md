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
| `src/windows/main_window.py` | `tests/windows/` |
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
├── conftest.py            geometry_app, the one QApplication, and default_settings, for mesh/ and pdf/
├── data/                  sample inputs, never beside a test file
├── dicom/                 exists: DicomData reset, RTSTRUCT reader, import attach and list-row tests
│   ├── conftest.py        fixtures used only by dicom tests
│   ├── test_data.py
│   ├── test_load_structures.py  exists: attach read_structures onto DicomData
│   ├── test_structure_list.py   exists: Import-tab list rows from Structures
│   ├── test_structures.py   exists: RTSTRUCT decoding and validation
│   └── test_fileio.py
├── mesh/                  exists: the notch, the solid cylinder and the tandem cut-out, through OpenCASCADE
│   ├── test_cylinder.py
│   ├── test_notch.py
│   └── test_tandem.py
├── models/
├── pdf/                   exists: the reference sheet's lengths, notch drawing and cylinder table
│   └── test_template_reference.py
├── settings/              exists: config file loading, the needle template library and cylinder templates
│   ├── test_cylinder_templates.py
│   ├── test_needle_templates.py
│   └── test_load.py
├── tooling/               exists: build, line-ending and architecture diagram checks
│   ├── test_architecture_build.py
│   ├── test_architecture_drift.py
│   ├── test_build_executable.py
│   └── test_line_endings.py
├── views/                 exists: the Channels, Cylinder, Tandem and Import views, against the real window
│   ├── conftest.py        units_app, channels_window (Ex1 imported) and cylinder_window
│   ├── test_camera_controls.py  camera gesture and zoom rules
│   ├── test_central_axis.py     reference geometry and toggle/reset state
│   ├── test_bounding_grid.py    bounds, labels and independent controls (PR #81)
│   ├── test_channels_view.py
│   ├── test_cylinder_template_controls.py
│   ├── test_cylinder_view.py
│   ├── test_import_view.py  exists: Import structure list after DICOM import
│   └── test_tandem_view.py
└── windows/               exists: the main window, driven offscreen
    ├── conftest.py        fresh_window, a new window per test with no plan
    └── test_main_window.py
```

`tooling/`, `views/`, `windows/`, `mesh/`, `pdf/`, `settings/`, `settings/test_needle_templates.py`,
`settings/test_cylinder_templates.py`, `dicom/test_data.py`,
`dicom/test_structures.py`, `dicom/test_load_structures.py`, `dicom/test_structure_list.py`
and `views/test_import_view.py` exist. The rest of the tree shows where tests will go.

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

`dicom/test_structures.py` tests the standalone RTSTRUCT reader using real in-memory
pydicom datasets. It covers ROI joins, all contour slices, metadata defaults, contour
semantics, input preservation, and malformed input.

`windows/` and `views/` hold the widget tests. Both fixtures build the real `MainWindow`,
models and five views offscreen, with the 3D canvas never initialised and `HOME` and
`USERPROFILE` pointed at a temporary folder. Each reuses the one QApplication if the other
started it first, and disconnects application signals in its teardown. No application module is
mocked. The pure functions below still have no tests.

`settings/test_needle_templates.py` tests the needle template library against files in `tmp_path`.
It imports no Qt and no `classes` module. `settings/test_cylinder_templates.py` checks cylinder
templates against every Cylinder tab range edge, and their library, including update and delete,
against files in `tmp_path`, with no Qt either.

`windows/test_main_window.py` uses `fresh_window` to click buttons with `QTest` and assert what
the window shows.

`mesh/test_notch.py` and `mesh/test_cylinder.py` build real solids and compare their bounding
boxes and volumes with hand-worked literals. No window is built. `default_settings` gives each
test a fresh copy of the defaults as the live settings. The literals for the default cylinder
were measured on `main` before the notch settings existed, so the defaults are proven unchanged.
`geometry_app` and `default_settings` live in the root `tests/conftest.py`, because `pdf/` needs
them too.

`pdf/test_template_reference.py` checks the reference sheet's interstitial lengths against
hand-worked distances, for a dome tip, a flat tip, and a flat-tipped cylinder's wall, and the
notch drawing, the label placement and the cylinder table against literals.

`dicom/test_data.py` checks that a new `DicomData` starts empty and that `reset()` clears every
field `__init__` declares. It imports no Qt or conda-only package.

`settings/test_load.py` writes real config files to pytest's `tmp_path` and loads them. It
imports no Qt or conda-only package.

`views/conftest.py` holds three fixtures. `units_app` is the one QApplication for the whole
run, created offscreen with HOME and USERPROFILE pointed at a temporary folder. Qt allows one
QApplication per process, so the two window fixtures share it rather than each making their
own. `channels_window` builds the real `MainWindow`, models and five views once per module
and imports `SI_C_D30 Brachify_Ex1/`. It reads that folder where it is rather than from a copy
in `tests/data/`, because the folder is inherited upstream and never edited. `cylinder_window`
builds a fresh window with default settings for each test and restores the previous app
window afterwards, so later tests still reach their own models. Neither calls
`canvas.InitDriver()`, since OpenCASCADE's viewer segfaults without a display, and both
disconnect their window from the application signals on teardown. No application module is
mocked.

`views/test_channels_view.py` drives the Channels tab through the real window and models. §8.2
of the [project docs](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md) says what makes it fail.

`views/test_cylinder_view.py` checks the Cylinder tab's controls with the real window, models
and widgets. It covers the mm/cm selector across all four dimensions, precision, limits, Apply,
configuration reset and Ex1 import with needle offsets, and the settings round trip: every
default key is in the exported snapshot, and the collar is exported and loaded back. The notch
controls are applied, grey out when *Add Notch* is unticked, follow the units, and are filled
by a config import. The tab's spin boxes keep 20 px and nothing scrolls sideways in the default
window.

`views/test_cylinder_template_controls.py` checks the Cylinder tab's Templates group: *Save as
Template* writes every setting from its own control, in mm, a blank or taken name or an unreadable
library is explained in the status line, and the library's ranges match the tab's spin boxes.
*Load* fills every control, the name and the note, in the displayed unit, without applying.
Run alone, a small `tests/views` file can crash at exit after passing (§7.13 of the project docs).

`views/test_tandem_view.py` checks that *Generate Tandem* keeps a live setting the settings
snapshot does not list.

Verified 2026-10-10: eight new cases watched red before implementation, 28 suite cases
green afterwards; wrong scale, wrong Apply conversion and rounded-cache mutations all caught.

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

`tooling/test_architecture_build.py` runs the real diagram CLI against temporary trees.
It checks nested viewer URLs and rejects missing, stale or unembedded nested diagrams. It
also checks that a diagram checked out with CRLF line endings, as Git for Windows does, still
matches a stamp written on macOS or Linux, and that the `npx` it renders with can be started,
which on Windows means `npx.cmd`. That test is skipped where Node is not installed.

## Viewport controls and references

`views/test_camera_controls.py` has six cases for left-drag versus click, jitter, distant
release, incremental right/middle panning and proportional reversible wheel/trackpad zoom.
`views/test_central_axis.py` has eight cases for local-Z endpoints, invalid lengths, the
real toggle's availability/preference and `DisplayModel.reset` emitting an empty scene.
`views/test_bounding_grid.py` (PR #81) has nine cases for rounded bounds, invalid input,
outer-wall lines, model-mm axis titles, real AIS label text/position, reset and independent
nonoverlapping controls. The fixtures isolate user files before importing the viewport.

These tests never initialise the native canvas. They cannot prove the grid is visually
legible or the camera moves correctly; native Ex1/Ex2 checks supplement them, as recorded
in [§5.7](../docs/project/COSC499-TEAM10-PROJECT-DOCS.md#57-the-3d-viewport).
