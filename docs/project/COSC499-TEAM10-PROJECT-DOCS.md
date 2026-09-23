# COSC 499 — Team 10 — Project Documentation

**This file is the source of truth for project documentation.**

Every other document in this repository is either upstream material we inherited, course
scaffolding, or a pointer back here. When any two documents disagree, this one wins — and
when this one disagrees with the code, **the code wins and this file must be corrected**.

| | |
|---|---|
| Project | *brachify* — 3D-printable brachytherapy cylinder generator |
| Course | COSC 499, UBC Okanagan (Capstone) |
| Repository | `COSC-499-W2026/capstone-project-team-10` |
| Upstream | `brachify/brachify` (configured as the `upstream` remote) |
| Last full code audit | 2026-09-21 |
| Audit scope | Every hand-written source file read end to end; see §2 |

---

## Table of contents

1. [Setup](#1-setup)
2. [Standing mandate for this document](#2-standing-mandate-for-this-document)
3. [What this project is](#3-what-this-project-is)
4. [Architecture](#4-architecture)
5. [Module reference](#5-module-reference)
6. [Data and configuration reference](#6-data-and-configuration-reference)
7. [Known bugs, traps, and dead code](#7-known-bugs-traps-and-dead-code)
8. [Testing](#8-testing)
9. [Maintaining this document](#9-maintaining-this-document)
10. [Glossary](#10-glossary)

---

## 1. Setup

### 1.1 Prerequisites

- **conda.** The project is conda-only. **Never run `pip install` into the environment** —
  mixing conda and pip is a known, documented breakage here
  ([virtual_environments_instructions.md](../../virtual_environments_instructions.md)).
- Python 3.12 (3.11 also works upstream).
- Git.

`pythonocc-core` is pinned to **7.7.2**. Upstream has never produced a working environment
above that version. Do not bump it casually.

### 1.2 macOS setup — verified working

> Verified on 2026-09-21: macOS (Darwin 25.6.0), Apple Silicon (arm64), Python 3.12.
> The app launches, the Qt window opens, and the OpenCASCADE 3D viewport initialises.

`spec-file.txt` **will not work on macOS.** Its line 3 reads `# platform: win-64` and 141 of
its 184 pinned package URLs are Windows binaries.

`environment.yml` alone is **also not sufficient on macOS.** It never names PySide6. On
Windows that is harmless because conda-forge's `matplotlib` meta-package depends on
`pyside6 >=6.7.2` for `win-64` — which is why PySide6 appears in the Windows lockfile without
being requested. The `osx-arm64` build of `matplotlib` has no Qt dependency at all, so a Mac
environment built from `environment.yml` has no PySide6 and `src/launch.py` dies on its first
import. Name it explicitly:

```bash
# 1. Install a conda. Miniforge defaults to conda-forge, which is the only channel
#    shipping pythonocc-core, and avoids the Anaconda commercial-repo terms that the
#    `defaults` channels in environment.yml would pull you into.
brew install --cask miniforge
conda init zsh
# open a new terminal here

# 2. Create the environment. pythonocc-core is the one hard pin.
conda create -n brachify -c conda-forge \
  python=3.12 \
  pythonocc-core=7.7.2 \
  pyside6 \
  matplotlib \
  reportlab \
  pydicom

# 3. Run, from the repository root
conda activate brachify
python src/launch.py
```

`numpy` arrives transitively via `matplotlib-base` and does not need naming. `pyinstaller` is
deliberately omitted — it exists only to build the Windows `.exe`.

### 1.3 Windows setup — the upstream-supported path

```bash
conda create --name brachify --file spec-file.txt
conda activate brachify
python src/launch.py
```

`spec-file.txt` is the canonical, fully pinned lockfile. Prefer it on Windows.

### 1.4 Running

```bash
cd <repo root>
python src/launch.py
```

**Run from the repository root, not from inside `src/`.** Python puts `src/` on `sys.path`
itself (it is the script's directory), but several resource paths resolve relative to the
current working directory.

`launch.py` accepts an optional `argv[1]` folder path which auto-triggers a DICOM import; this
exists so the separate *brachify-optimization* tool can launch straight into a plan.

### 1.5 First-run behaviour you must not mistake for a hang

The first launch in a fresh environment takes **roughly a minute** with no output. Measured on
the verification run:

```
11:31:25  Config filename is None. Using defaults instead.
11:32:20  Starting main window initialization      <-- 55 s gap
11:32:23  main window initialization complete
```

That gap is the cold `import OCC` — Python byte-compiling pythonocc's very large wrapper
package for the first time. The `__pycache__` persists, so later launches are far quicker.
**Do not Ctrl-C it.** It looks hung and is not.

Startup failures are silent by design, which compounds the confusion:
[`app.py`](../../src/classes/app.py) wraps the whole GUI construction in `try/except`, logs
`critical`, and returns `False`; `main()` then simply returns. No window, no dialog, no
traceback on screen. **The log is the only place failures surface:**

```bash
tail -f ~/brachify/app.log
```

Keep that open in a second pane while developing.

### 1.6 Sample data

Two complete DICOM triples (RP + RS + RD) ship in the repository:

| Folder | Manufacturer | Channels | Notable |
|---|---|---|---|
| `SI_C_D30 Brachify_Ex1/` | Varian Medical Systems | 13 | `Central Axis` + `Applicator2..13` |
| `SI_C_D30 Brachify_Ex2/` | Varian Medical Systems | 14 | Also has a channel labelled `Tandem` — use this one to exercise the tandem path |

Both exercise the **Varian** import branch only. We have **no sample data for the Nucletron /
Elekta Oncentra branch**, which is roughly half of [`dicom/fileio.py`](../../src/classes/dicom/fileio.py)
and is therefore completely unexercised by anything in this repository.

### 1.7 Building the Windows executable

```bash
python build_executable.py     # output: dist/brachify/brachify.exe
```

`--exclude-module PyQt5` in that script is load-bearing: PyQt5 and PySide6 clash at runtime.

### 1.8 IDE

Point VS Code at the environment interpreter (`Cmd+Shift+P` → *Python: Select Interpreter*)
so the existing [.vscode/launch.json](../../.vscode/launch.json) "Launch.py" configuration
works. On the verified macOS setup that path is:

```
/opt/homebrew/Caskroom/miniforge/base/envs/brachify/bin/python3.12
```

---

## 2. Standing mandate for this document

This document exists because of the following instruction. It is reproduced **verbatim** and
stands as the permanent rule for anyone — human or AI — who edits this file:

> Ok so I want you to please understand this repo and read everything in detail, not just the
> documentation and other files, but also the code, which is obviously the source of truth.
> Read absoutely everything so that you can understand everything about this codebase. Please
> be honest about this and actually do it (yes, do it again).

### What this means in practice

1. **The code is the source of truth, not the docs.** Upstream's README, the User Manual, and
   the `notes/` directory describe intent. They are frequently out of date. Where a document
   and the code disagree, believe the code and fix the document.
2. **Read, do not skim.** Do not describe a module you have not opened. Do not infer a
   module's behaviour from its name or its imports.
3. **Be honest about coverage.** If a file was skimmed rather than read, or a claim is
   reasoned from the source rather than observed at runtime, say so *in the text*. This
   document uses two explicit markers:
   - *Verified* — observed at runtime during an audit, with the evidence noted.
   - *Reasoned from code* — derived by reading, not executed or clicked through.
4. **No invented certainty.** "I don't know" and "not verified" are acceptable entries. A
   confident wrong statement in this file is worse than a gap, because the whole team and
   every AI agent treats this file as ground truth.

### Coverage of the 2026-09-21 audit

Read end to end: every hand-written `.py` file under `src/` and `benchmarks/` (~4,400 LOC
including all 806 lines of `template_reference.py`); all seven `.ui` XML files; `README.md`,
`README-BRACHIFY.md`, `virtual_environments_instructions.md`, every file in `notes/`;
`environment.yml`, `requirements.txt`, `spec-file.txt`, `build_executable.py`, `LICENSE`,
`.gitignore`, `.vscode/*`; the full text of `user_guide/Brachify User Manual.docx`; and the
headers of both sample DICOM sets.

Not read in full, and why:
- The seven generated `src/windows/ui/*_ui.py` files. Their complete widget inventory was
  extracted from the `.ui` XML they are generated from, which is equivalent and
  authoritative. They must never be hand-edited (§5.6).
- `3D Models and Templates/*.SLDPRT|.STL|.pdf|.docx` — binary CAD and Office assets with no
  bearing on program behaviour.
- `.vs/brachify/v17/.wsuo` — a Visual Studio binary user-state blob, committed by accident
  upstream.
- `src/windows - Shortcut.lnk` — a Windows shortcut, committed by accident upstream.

---

## 3. What this project is

### 3.1 Clinical purpose

*brachify* is a Windows desktop application written by **Michael Kudla, PhD** (BC Cancer) for
medical physicists doing **interstitial gynaecological (GYN) brachytherapy**.

The workflow it serves:

1. A clinician plans a treatment in their Treatment Planning System (TPS) — Varian
   BrachyVision or Elekta Oncentra — placing needles around and through a vaginal cylinder
   applicator.
2. They export the plan as DICOM: an **RTPLAN** (`RP*.dcm`) file and its associated
   **RTSTRUCT** (`RS*.dcm`) file.
3. brachify reads those, reconstructs the needle geometry in 3D, and generates a
   **patient-specific, 3D-printable cylinder** with each needle channel bored through it,
   optionally a curved tandem channel, an orientation notch, and an optional base collar.
4. It exports **STL** (for printing) or **STEP** (for CAD), plus a **PDF reference sheet**
   giving each channel's number, interstitial length, and position on a cross-section diagram.

The printed cylinder is a physical medical device used on a patient. Geometry bugs have
clinical consequences. This is the reason the upstream review process
(§[pull_request_template_brachify.md](../../pull_request_template_brachify.md)) requires a
reviewer to actually *run* the code, and requires Michael's sign-off before merge.

### 3.2 The hard clinical precondition

**The DICOM plan must contain a channel labelled exactly `Central Axis`.**

That channel defines the cylinder's central axis and tip direction; every other needle is
rotated and translated into cylinder-local coordinates relative to it. Its tip must sit at the
tip of the cylinder and its dwell times must be zero (it is not part of the printed model).

If it is absent, brachify falls back to a structure whose `ROIObservationLabel` contains
`"surface"`. If that is also absent, the import aborts with
`MainWindow.no_central_axis_or_cylinder_outline()`.

A channel labelled `Tandem` is optional; if present it supplies the tandem's rotation angle.

### 3.3 Repository provenance

This repository is a **fork of `brachify/brachify`**. The `upstream` remote still points there.
Essentially all code was written by the upstream authors.

Team 10's contribution as of the last audit consists of README edits, the course folder
scaffolding (`docs/`, `tests/`, `utils/`), and this documentation set. No `src/` code has been
modified by our team yet.

### 3.4 Licence — read this before publishing anything

brachify is licensed under **Business Source License 1.1**, *not* an open-source licence, and
**it never converts to one** (`Change Date: None`).

Permitted: internal use (including inside a for-profit organisation), forking for personal,
academic, research or non-commercial purposes, and distributing modified versions **for free
under these same terms**.

Not permitted without a separate commercial licence: selling or sublicensing brachify or any
fork as a standalone product or service, or bundling it into a commercial product or SaaS
offering.

Academic capstone use is squarely within the grant. Do not publish derivative work under a
permissive licence, and do not strip the `LICENSE` file.

---

## 4. Architecture

### 4.1 Technology stack

| Concern | Library |
|---|---|
| GUI toolkit | PySide6 (Qt 6) |
| Geometry kernel | OpenCASCADE via `pythonocc-core` 7.7.2 (`OCC.Core.*`, `OCC.Extend.*`) |
| DICOM parsing | `pydicom` |
| PDF generation | `reportlab` |
| Diagram rendering | `matplotlib` |
| Numerics | `numpy` |
| Packaging | PyInstaller (Windows only) |

### 4.2 Startup sequence

```
src/launch.py  main()
  └─ RadiotherapyApp(argv)                    # QApplication subclass
       ├─ AppSignals()                        # app.signals
       └─ Values()                            # app.values — reads ~/brachify/filepaths.json,
                                              #   then the last-used config JSON, else defaults
  └─ app.gui()
       ├─ MainWindow()                        # builds Ui_MainWindow, wires nav buttons
       ├─ MainWindow.initModels()             # models first...
       ├─ MainWindow.initViews()              # ...then views, which connect to them
       │    ├─ OrbitCameraViewer3d()          # the OCC canvas widget
       │    └─ NavigationModel()              # constructs the 5 views in fixed order
       └─ showWithCanvas()                    # resize -1px, show, resize back (canvas fit hack)
  └─ app.exec()                               # Qt event loop
```

The `__init__` → `initModels()` → `initViews()` split is deliberate: models must exist before
views try to connect signals to them. **Preserve that ordering when adding either.**

### 4.3 The five views are addressed by index

`NavigationModel.views` is a plain list, and the entire codebase reaches across views
positionally — e.g. `get_app().window.navigationmodel.views[3].ui.sb_tandem_height.setMaximum(...)`.

| Index | View class | File | Primary model |
|---|---|---|---|
| 0 | `ImportView` | [import_view.py](../../src/windows/views/import_view.py) | `DicomModel` |
| 1 | `CylinderView` | [cylinder_view.py](../../src/windows/views/cylinder_view.py) | `CylinderModel` |
| 2 | `ChannelsView` | [channels_view.py](../../src/windows/views/channels_view.py) | `ChannelsModel` |
| 3 | `TandemView` | [tandem_view.py](../../src/windows/views/tandem_view.py) | `TandemModel` |
| 4 | `Export_View` | [export_view.py](../../src/windows/views/export_view.py) | — (composes all) |

**Reordering this list breaks call sites scattered across `settings/reset.py`, every view, and
`main_window.py`.** There is no symbolic lookup. Treat the order as frozen.

### 4.4 Signal graph

Three application-wide signals live on `AppSignals` ([signals.py](../../src/classes/signals.py)):

| Signal | Emitted by | Received by |
|---|---|---|
| `viewChanged(int)` | the five nav buttons in `MainWindow.__init__` | `NavigationModel.set_page` |
| `height_changed(float)` | `CylinderView.action_apply_settings` | `ChannelsModel.update_height_offset`, `TandemModel.update_height_offset` |
| `exportFile(str)` | *nobody* | *nobody* — declared and unused |

Model-to-model wiring, all established in `MainWindow.initModels()` / `TandemModel.__init__`:

```
DicomModel.values_changed(DicomData)
    ├─→ CylinderModel.load_data
    └─→ ChannelsModel.load_data

ChannelsModel.tandem_changed(NeedleChannel) ─→ TandemModel.set_tandem_channel
CylinderModel.values_changed(BrachyCylinder) ─→ TandemModel.update_cylinder
                                             └─→ CylinderView.action_update_settings
DisplayModel.shapes_changed(list, bool)      ─→ OrbitCameraViewer3d.update_display
OrbitCameraViewer3d.sig_topods_selected(list) ─→ ChannelsView.action_set_selected_shapes
                                                 (connected on_open, disconnected on_close)
```

### 4.5 The display pipeline

Rendering is strictly one-way:

```
model computes an OCC TopoDS_Shape
  → wrapped in ShapeModel(label, shape, ShapeTypes.*)
  → DisplayModel.add_shape(s)           # dict keyed by label; enabled=False deletes the entry
  → DisplayModel.update()               # assigns materials by ShapeTypes, emits shapes_changed
  → OrbitCameraViewer3d.update_display  # RemoveAll, DisplayShape each, Repaint, FitAll
```

Any view method that mutates geometry **must** be decorated with `@display_action`
([custom_view.py](../../src/windows/views/custom_view.py)), which calls `displaymodel.update()`
in a `finally` block. Omit it and the model changes while the viewport silently does not
repaint.

`ShapeTypes` (`CYLINDER` / `CHANNEL` / `TANDEM` / `SELECTED` / `EXPORT`) is a **material key,
not a type hierarchy**. Each view installs its own `materials` dict in `on_open()`, which is
how the same cylinder renders opaque-grey on one tab and translucent-teal on another.

### 4.6 Coordinate conventions

- The generated model lives in **cylinder-local coordinates**: base at the origin `(0,0,0)`,
  axis along `+Z`, tip at `z = length`.
- DICOM points arrive in patient coordinates and are transformed at import by
  `helper.rotate_points` (Rodrigues' rotation), aligning the central-axis vector to `+Z`, then
  translated so the cylinder base sits at the origin.
- **Original DICOM needle points are never mutated.** Cylinder length changes propagate as a
  *delta*: `CylinderView` emits `height_changed(length - model.starting_length)`, where
  `starting_length` is captured at import time. Channels and tandem shift themselves by that
  offset. This is why `NeedleChannel` keeps both `points` and `_offset` and applies the offset
  only in `get_points()` / `shape()`.
- In the PDF cross-section diagram the view is **from the base looking up**, so the y-axis is
  drawn negated: `Anterior` is `-y`, `Posterior` is `+y`.

### 4.7 Directory map

```
.
├── AGENTS.md                  AI agent instructions (cross-tool standard)
├── CLAUDE.md                  pointer to AGENTS.md
├── pull_request_template.md   Team 10 PR template
├── pull_request_template_brachify.md   upstream's original PR process
├── README.md                  course scaffolding template
├── README-BRACHIFY.md         upstream project README
├── LICENSE                    BSL 1.1
├── environment.yml            loose conda spec (see §1.2 caveat)
├── spec-file.txt              pinned conda lockfile — WINDOWS ONLY
├── requirements.txt           STALE, unused — do not use (§7.4)
├── build_executable.py        PyInstaller wrapper
├── docs/                      course documentation
│   ├── project/               ← this document
│   └── workflows/             tool-agnostic procedures (commit, make-pr)
├── tests/                     empty placeholder
├── utils/                     empty placeholder
├── notes/                     upstream developer notes
├── benchmarks/                dead code (§7.3)
├── resources/                 splash image and icon
├── user_guide/                Brachify User Manual.docx
├── Images/                    README screenshots
├── 3D Models and Templates/   printable collets, wrenches, template cylinders
├── SI_C_D30 Brachify_Ex1/     sample Varian DICOM
├── SI_C_D30 Brachify_Ex2/     sample Varian DICOM (has a Tandem channel)
└── src/
    ├── launch.py
    ├── classes/
    │   ├── app.py             RadiotherapyApp, get_app()
    │   ├── info.py            APP_NAME, paths
    │   ├── logger.py          rotating file + stderr logging
    │   ├── signals.py         AppSignals
    │   ├── dicom/             data.py (DicomData), fileio.py (vendor readers)
    │   ├── mesh/              cylinder, channel, tandem, notch, helper, intersections, fileio
    │   └── pdf/               template_reference.py, canvas.py
    ├── settings/              defaults.py, load.py, values.py, reset.py
    └── windows/
        ├── main_window.py     MainWindow + every QMessageBox dialog
        ├── palettes.py        colour definitions (largely unused)
        ├── models/            six QObject models
        ├── views/             five views + custom_view.py + viewport.py
        └── ui/                .ui sources and generated *_ui.py
```

---

## 5. Module reference

### 5.1 Entry point and application singleton

**[`src/launch.py`](../../src/launch.py)** — builds `RadiotherapyApp`, calls `gui()`, closes the
PyInstaller splash screen if present (`pyi_splash` exists only in frozen Windows builds, so the
import is wrapped in a bare `except`), optionally auto-imports `argv[1]`, then enters the event
loop.

**[`src/classes/app.py`](../../src/classes/app.py)** — `RadiotherapyApp(QApplication)`.
Module-level `get_app()` returns `QApplication.instance()` and is how **every** module reaches
global state. Two attributes matter: `app.signals` (`AppSignals`) and `app.values` (`Values`).

**[`src/classes/info.py`](../../src/classes/info.py)** — `APP_NAME = "brachify"`, version
constants, and paths. Note `USER_PATH = ~/brachify`. There is a latent typo:
`VERION_MINOR` (missing `S`), and `APP_VERSION` is the string `"alpha"` rather than a number,
so `VERSION_MAJOR`/`VERION_MINOR` are effectively unused.

**[`src/classes/logger.py`](../../src/classes/logger.py)** — a `Brachify` child logger at DEBUG,
`propagate = False`, with a rotating file handler (`~/brachify/app.log`, 25 MB × 3 backups) and
a stderr stream handler. Creates `~/brachify/` at import time if missing.

### 5.2 Settings and configuration

**[`settings/defaults.py`](../../src/settings/defaults.py)** — `DEFAULT_CONFIG_VALUES`, the
schema: a flat `CONFIG_*` → number dict, 19 keys. Full table in §6.2.

**[`settings/load.py`](../../src/settings/load.py)** — `load_config_file()` is lenient by
design. It keeps any key present in the user's JSON whose value is `int` or `float`, falls back
to defaults (or the previous values, on a mid-session import) for the rest, and returns a
two-list `config_keys_loaded` of `[loaded, missing]` so the UI can tell the user exactly what
was and was not applied. Unknown keys in a user's JSON are preserved but never used.

**[`settings/values.py`](../../src/settings/values.py)** — `Values` holds `config_values` (the
single mutable dict every other module reads), the two most-recent config file paths read from
`~/brachify/filepaths.json`, and `createConfigMessageText()` which formats the human-readable
"what loaded" report shown in the Import tab.

**[`settings/reset.py`](../../src/settings/reset.py)** — the two halves of config round-tripping:
- `resetAllValues(dict)` pushes a config dict **into** every spin box and then applies it. It
  handles the three tandem states explicitly (absent / generated / imported), because a
  generated tandem must be regenerated while an imported one must not be touched.
- `getCurrentValues()` reads the current state **back out** into a dict. **It returns only 17
  of the 19 keys** — see §7.1, this is a live bug.

### 5.3 DICOM ingest

**[`dicom/data.py`](../../src/classes/dicom/data.py)** — `DicomData`, a flat mutable bag of ~20
fields. There is a comment in the file stating the rule explicitly: **any field added to
`__init__` must also be added to `reset()`**, or it leaks across successive imports.
(`central_axis_flag` currently violates this — it is set in `__init__`, absent from `reset()`,
and never read.)

**[`dicom/fileio.py`](../../src/classes/dicom/fileio.py)** — the vendor readers. `read_dicom_folder()`
globs `**/*.dcm`, takes the **first** file that parses as RTPLAN and the **first** that parses
as RTSTRUCT, then branches on `rp_dataset.Manufacturer`:

| Manufacturer string | Reader |
|---|---|
| `"Varian Medical Systems"` | `load_varian_dicom_data` |
| `"Nucletron"` | `load_nucletron_dicom_data` |
| anything else | falls through — raises `UnboundLocalError` (§7.2) |

The two branches are near-parallel and must usually be fixed in tandem:
`load_central_axis_varian` / `load_central_axis_nucletron`, `load_channels_varian` /
`load_channels_nucletron`.

Vendor differences that matter:
- **Varian** stores channel contour geometry in the RTSTRUCT's `ROIContourSequence`. The
  contours arrive ordered by ROI number while the label/number lists are ordered by channel
  number, so `load_channels_varian` explicitly re-sorts them into alignment. Getting this wrong
  silently mislabels every needle.
- **Nucletron / Oncentra** stores it in a **private tag `(300f,1000)`** inside the RTPLAN.
  Sometimes that tag's contents are raw binary, in which case the reader falls back to manual
  `read_sequence()` parsing with implicit VR, little-endian, and the dataset's own encoding.

Both branches strip the central-axis channel out of the channel lists after using it, and both
handle single-point "anchor" channels by deleting them and warning the user — with different
warning dialogs (`single_point_pop_up_Varian` vs `..._Nucleatron`) because the two systems
label anchors differently.

`module-level global method_found` is used as a success flag across functions. It is reset at
the top of each loader so that importing two folders in a row behaves correctly.

### 5.4 Geometry

All under [`src/classes/mesh/`](../../src/classes/mesh/), one concern per module.

**`cylinder.py`** — `BrachyCylinder`. `shape()` builds a `BRepPrimAPI_MakeCylinder`, finds the
highest planar face by walking a `TopExp_Explorer`, fillets that top edge into a dome, then
optionally fuses a base collar (`add_base`) and always fuses the orientation notch
(`add_notch`). **`shape()` caches into `self._shape`; every mutator must clear that cache** —
`setDiameter`, `setLength` and `enableBase` all do.

**`channel.py`** — `NeedleChannel` plus `rounded_channel()`, the single most intricate function
in the codebase. It:
1. applies the dead-space offset to the tip,
2. adds the cylinder height offset,
3. truncates coordinates to 5 decimals (*not* rounds — a documented workaround for an OCC
   fusion bug),
4. removes identical and near-collinear points,
5. builds a cone tip, then fuses one `BRepPrimAPI_MakeCylinder` per segment and one
   `BRepPrimAPI_MakeSphere` per interior vertex,
6. optionally widens the channel at the base for post-print threading,
7. extends the channel out of the cylinder base.

Steps 5–6 are wrapped in a **three-tier fallback ladder** (`fix1` / `fix2` / `fix3`) because
OCC's boolean fuse intermittently emits warnings on degenerate geometry: `fix1` nudges the
radius by 0.001 mm; `fix2` retries at 4, 3 and 2 decimal places; `fix3` jitters each coordinate
by ±0.01 mm in turn. If all three fail the user gets a warning or error dialog. This ladder is
the reason the User Manual tells clinicians to *visually re-inspect every channel* after
changing any value.

**`tandem.py`** — `Tandem`. Two distinct shape methods, easily confused:
- `generate_shape()` — the **cut-out** subtracted from the cylinder. Built by intersecting a
  swept tandem profile with a cylinder-shaped envelope (`BRepAlgoAPI_Common`), so the tandem
  channel stops at the cylinder surface.
- `tandem_shape()` — the **visual preview** of the physical tandem tool, shown in the Export
  tab when *Show Tandem* is ticked. Not exported.

Both work in 2D (`gp_Pnt2d`, `Geom2d_*`), find bend/exit points by curve intersection, lift to
3D, and sweep with `BRepFill_PipeShell`. `Tandem.__init__` has a `try/except` around
`get_app()` supplying hardcoded fallback values, so the module can be run standalone
(`python src/classes/mesh/tandem.py`) to visualise a tandem without launching brachify.

**`notch.py`** — `CylinderNotch`, a small box fused to the cylinder wall at `Z=0`, rotated
270°, marking orientation for the person inserting the applicator. The docstring still
describes an 'L' shape from two fused boxes; that code is commented out and it is now a single
box.

**`helper.py`** — shared utilities: `face_is_plane`, `geom_plane_from_face`, face sorting by Z,
`get_vector` / `get_direction` / `get_magnitude`, `extend_bottom_face` (prisms the lowest face
down through `z=0` so an imported tandem always reaches the cylinder base), and
`rotate_points()`, the Rodrigues rotation used for the DICOM→cylinder transform.

**`intersections.py`** — `are_colliding()` via `BRepAlgoAPI_Section`. Defined, but **not called
anywhere**. Collision detection between needles is not currently performed.

**`fileio.py`** (mesh) — `read_3d_file` (STEP only; anything else raises and shows a dialog) and
`write_3d_file` (STL binary with `linear_deflection=0.5`, `angular_deflection=0.3`; or STEP
AP203).

### 5.5 Models

All in [`src/windows/models/`](../../src/windows/models/). `QObject`s owning domain state and
emitting change signals. They hold no widgets.

| Model | Owns | Notes |
|---|---|---|
| `DicomModel` | a `DicomData` | thin; `update()` swaps the bag and emits |
| `CylinderModel` | a `BrachyCylinder`, `starting_length` | `cylinder` is `None` until a DICOM import or a manual *Apply Settings* |
| `ChannelsModel` | `{label: NeedleChannel}`, selection, disabled set | the tandem channel is auto-disabled when set |
| `TandemModel` | `_base_shape`, `_display_shape`, offsets, rotation | the most stateful; see below |
| `DisplayModel` | `{label: ShapeModel}`, materials | `add_shape` with `enabled=False` **deletes** the entry |
| `NavigationModel` | the five views | not a `QObject`; plain class |

`TandemModel` deserves attention. It distinguishes **imported** from **generated** tandems
(`is_shape_imported`) and tracks two independent vertical offsets:
- `height_offset` — automatic, follows cylinder length changes.
- `mesh_offset` — manual, the *Height Offset* spin box, applies to imported tandems only.

Its `_generate_tandem()` implements an unusual error-recovery algorithm, documented in a long
docstring in the file: it applies each spin-box value one at a time, rebuilding the shape after
each; any value that throws is recorded, reverted in the UI, but *left in place internally* in
case a later value fixes it. Survivors at the end trigger per-field error dialogs. The effect
is that an invalid tandem parameter reverts itself rather than blocking the user.

`ShapeModel` ([shape_model.py](../../src/windows/models/shape_model.py)) is the transport
object between models and the viewport: `label`, `shape`, `type`, plus `selected` /
`transparent` / `enabled` flags and a `material` dict.

### 5.6 Views and the Qt UI layer

[`src/windows/ui/`](../../src/windows/ui/) holds `.ui` files (Qt Designer XML) and their
generated `*_ui.py` counterparts.

> **The `*_ui.py` files are generated. Never hand-edit them.** They carry a
> `WARNING! All changes made in this file will be lost when recompiling UI file!` banner and
> were produced by Qt User Interface Compiler 6.5.2.

Regenerate after editing a `.ui`:

```bash
pyside6-uic src/windows/ui/<name>.ui -o src/windows/ui/<name>_ui.py
```

The full workflow — Designer → `.ui` → `uic` → hand-written `*_view.py` → register in
`NavigationModel` → connect signals to `action_*` methods → decorate with `@display_action` —
is documented upstream in [notes/gui.txt](../../notes/gui.txt).

Complete control inventory, extracted from the `.ui` sources:

**Import** (`import_view.ui`) — `btn_import_folder` "Import Dicom", `btn_config_file`
"Import Config File", `info_area` (QTextEdit, the information panel).

**Cylinder** (`cylinder_view.ui`)

| Widget | Label | Range |
|---|---|---|
| `spinbox_diameter` | Cylinder Diameter | — |
| `spinbox_length` | Cylinder Length | 60 – 300 |
| `spinbox_base_thickness` | Collar Thickness | — |
| `spinbox_base_height` | Collar Height | default 0, step 1 |
| `cb_add_base` | Add Collar | checkbox |
| `btn_apply_settings` | Apply Settings | |

**Channels** (`channels_view.ui`)

| Widget | Label | Range |
|---|---|---|
| `spinbox_diameter` | Channels Diameter | min 0.3, 3 dp |
| `sb_needle_length` | Dead Space | max 350, 3 dp |
| `sb_threading_dept` | Threading Depth | max 350, 3 dp — note the `dept` typo in the name |
| `sb_threading_diameter` | Threading Diameter | max 350, 3 dp |
| `listwidget_channels` | Channels | |
| `btn_set_tandem` | Set as Tandem / Clear Tandem | text toggles |
| `btn_enable` | Disable / Enable | text toggles |

**Tandem** (`tandem_view.ui`) — a `QTabWidget` (`ab`) with two sub-tabs.

*Import sub-tab:* `btn_import`, `btn_clear_import`, `sb_height_offset` (−100 – 100),
`tandem_rotation` (−360 – 360), `btn_apply_import`, `label_5` (shows the model file path).

*Generate sub-tab:* `sb_tandem_height` (10 – 500), `sp_channel_diameter` (min 0.5),
`sp_stopper_diameter` (min 0.5), `sp_bend_angle`, `sb_bend_radius` (10 – 1000),
`sb_threading_depth` (max 350), `sb_threading_diameter` (max 350), `tandem_rotation_2`
(−360 – 360), `btn_apply` "Generate Tandem", `btn_clear_generate`.

Note there are **two separate rotation spin boxes** (`tandem_rotation` on Import,
`tandem_rotation_2` on Generate) kept manually in sync — every write to one writes the other.

**Export** (`export_view.ui`) — `cb_tandem_shown`, `cb_collet_preview_reference_sheet`,
`sb_needle_collet_od`, `sb_tandem_collet_outer_od`, `sb_tandem_collet_inner_od`,
`btn_export_mesh`, `btn_export_template_reference`, `btn_export_shapes`,
`btn_export_current_config`.

**Main window** (`main_window.ui`) — `display_view_widget` (hosts the OCC canvas),
`top_menu_bar` with the five nav buttons, and `viewswidget` (`QStackedWidget`) with
`page_import` … `page_export`.

Styling for the nav buttons is applied as **inline `setStyleSheet` strings** in five
near-identical `change_color_*` methods in `main_window.py`.
[`palettes.py`](../../src/windows/palettes.py) and [notes/style guide.txt](../../notes/style%20guide.txt)
exist but the nav buttons do not use them. This is the most obvious refactor target in the UI
layer.

### 5.7 The 3D viewport

[`views/viewport.py`](../../src/windows/views/viewport.py) — `qtBaseViewer` sets
`WA_PaintOnScreen`, `WA_NativeWindow` and `WA_NoSystemBackground`, then `OrbitCameraViewer3d`
hands `int(self.winId())` to pythonocc's `OCCViewer.Viewer3d().Create()`.

Mouse bindings, which are non-standard and worth knowing:

| Input | Action |
|---|---|
| Left click | select shape (emits `sig_topods_selected`) |
| **Right** drag | rotate |
| Middle drag | pan |
| Wheel | zoom (fixed 2.0× / 0.5× per notch) |

> *Verified 2026-09-21:* this native-handle handoff works on macOS arm64. `lsof` on the running
> process confirmed `OpenGL`, `QtGui`, `QtWidgets` and the full OpenCASCADE `libTK*` set
> loaded, and the viewport rendered. This was the main porting risk and it is resolved.

### 5.8 PDF reference sheet

[`pdf/template_reference.py`](../../src/classes/pdf/template_reference.py) (806 lines) and
[`pdf/canvas.py`](../../src/classes/pdf/canvas.py).

`generate_pdf()` produces a one-page reportlab document: header, patient/plan identifiers, a
table of channels, and a matplotlib cross-section diagram.

The substantive computation is **interstitial length** — how far each needle protrudes beyond
the cylinder surface:

1. `channels_inside_cylinder()` keeps only channels whose `z=0` point lies within the cylinder
   radius.
2. `extract_points_from_channels2()` normalises every needle to terminate exactly at `z = 0`,
   interpolating the crossing point if the needle passes through, or dropping a perpendicular
   if it stops short.
3. `add_deadspace()` extends a **copy** of each needle tip outward by `CONFIG_DEADSPACE`.
4. `get_all_interstitial_lengths()` builds a dense point cloud of the cylinder surface
   (straight wall + hemispherical dome, 0.1 mm spacing) and finds where each needle's first
   segment crosses it, within a 0.25 mm tolerance.

`save_points_diagram()` draws the cross-section: one circle per channel with its channel
number, the tandem marked `<n>T`, a dashed line showing tandem rotation (generated tandems
only), the orientation notch as a rectangle, `Anterior`/`Posterior` labels, and — if *Show
Collet Spacings* is ticked — dashed collet rings coloured **green** when clear and **red** when
they overlap another collet. It writes `basemap.png` **next to the PDF**, as a side effect.

`FooterCanvas` in `canvas.py` subclasses `reportlab.pdfgen.canvas.Canvas` to stamp "Page x of
y" and an export timestamp on every page.

After building, the module opens the PDF in the OS viewer: `os.startfile` on Windows (falling
back to `subprocess.Popen(['start', ...], shell=True)`), `subprocess.Popen(['open', ...])` on
posix. macOS is handled correctly here.

There are two near-duplicate implementations of the cylinder point cloud and surface
intersection — one pair inside `get_all_interstitial_lengths` in this file, another at module
scope in [`mesh/channel.py`](../../src/classes/mesh/channel.py). The `template_reference.py`
copy is the better one (it pre-filters the cloud by z-range for speed). The `channel.py` copies
appear unused. See §7.3.

---

## 6. Data and configuration reference

### 6.1 DICOM input requirements

A single folder containing at least:

- one **RTPLAN** (`RP*.dcm`) whose `ApplicationSetupSequence[0].ChannelSequence` is non-empty,
- one **RTSTRUCT** (`RS*.dcm`).

An RTDOSE (`RD*.dcm`) may be present and is ignored. Files are discovered recursively
(`**/*.dcm`) and the **first** match of each modality wins — a folder containing two plans
gives undefined results.

Plan authoring requirements (from the User Manual, both vendors):

- A straight needle labelled **`Central Axis`**, placed as accurately as possible along the
  cylinder axis, tip at the cylinder tip, **dwell times set to zero**.
- No intersecting needles.
- Optionally a needle labelled **`Tandem`** to orient the tandem.
- Oncentra only: *Tip End* must be selected under Applicator Properties, and using implant
  models requires a licence that is not enabled by default.

### 6.2 Configuration keys

`DEFAULT_CONFIG_VALUES` — 19 keys, all numeric, all millimetres unless noted.

| Key | Default | Meaning | Round-trips? |
|---|---|---|---|
| `CONFIG_CYLINDER_DIAMETER` | 30.0 | cylinder outer diameter | yes |
| `CONFIG_CYLINDER_LENGTH` | 160.0 | cylinder length | yes |
| `CONFIG_CHANNELS_DIAMETER` | 2.7 | needle channel diameter (all channels) | yes |
| `CONFIG_DEADSPACE` | 6.0 | needle dead space at the tip | yes |
| `CONFIG_CHANNELS_THREADING_DEPTH` | 5.0 | channel threading depth; 0 disables | yes |
| `CONFIG_CHANNELS_THREADING_DIAMETER` | 3.17 | channel diameter at base; 0 disables | yes |
| `CONFIG_TANDEM_TIP_HEIGHT` | 170.0 | tandem height | yes |
| `CONFIG_TANDEM_CHANNEL_DIAMETER` | 3.8 | tandem channel diameter | yes |
| `CONFIG_TANDEM_STOPPER_DIAMETER` | 5.0 | tandem stopper diameter | yes |
| `CONFIG_TANDEM_TIP_ANGLE` | 30 | tandem bend angle (degrees) | yes |
| `CONFIG_TANDEM_BEND_RADIUS` | 35.0 | tandem bend radius | yes |
| `CONFIG_TANDEM_ROTATION` | 0.0 | tandem rotation about Z (degrees) | yes |
| `CONFIG_TANDEM_THREADING_DEPTH` | 7.0 | tandem threading depth; 0 disables | yes |
| `CONFIG_TANDEM_THREADING_DIAMETER` | 5.0 | tandem diameter at base; 0 disables | yes |
| `CONFIG_NEEDLE_COLLET_OUTER_DIAMETER` | 5.0 | needle collet tolerance ring (PDF only) | yes |
| `CONFIG_TANDEM_COLLET_OUTER_DIAMETER_INNER` | 5.0 | tandem collet inner ring (PDF only) | yes |
| `CONFIG_TANDEM_COLLET_OUTER_DIAMETER_OUTER` | 8.0 | tandem collet outer ring (PDF only) | yes |
| `CONFIG_BASE_HEIGHT` | 0.0 | collar height; 0 disables the collar | **NO — §7.1** |
| `CONFIG_BASE_THICKNESS` | 0.0 | collar wall thickness; 0 disables the collar | **NO — §7.1** |

Adding a setting touches **four** places: `settings/defaults.py`, `resetAllValues()` and
`getCurrentValues()` in `settings/reset.py`, and the owning view's `__init__`.

### 6.3 User state on disk

`~/brachify/` (`classes.info.USER_PATH`, created at logger import):

| File | Written by | Contents |
|---|---|---|
| `app.log` | `logger.py` | rotating, 25 MB × 3 backups |
| `filepaths.json` | `MainWindow.closeEvent` | `most_recently_opened_config_file`, `most_recently_saved_config_file` |

`most_recently_saved_config_file` is stored but never read — it is reserved for future use.

### 6.4 Export formats

| Button | Format | Produced by |
|---|---|---|
| Export Mesh | `.stl` (binary) or `.step`/`.stp` | `_final_mesh()` — booleans cut out of the cylinder |
| Export Shape(s) | `.step`/`.stp` | `_final_shape()` — a `TopoDS_Compound` keeping parts separate |
| Export Reference Sheet | `.pdf` (+ `basemap.png` alongside) | `template_reference.generate_pdf` |
| Export Current Settings as Config | `.json` | `getCurrentValues()` — **loses 2 keys, §7.1** |

---

## 7. Known bugs, traps, and dead code

Everything here was found by reading the code during the 2026-09-21 audit. Nothing here has
been fixed. Severity is our judgement, not upstream's.

### 7.1 HIGH — the base collar silently disappears after generating a tandem

*Verified by static analysis; not yet reproduced in the GUI.*

`getCurrentValues()` ([settings/reset.py](../../src/settings/reset.py)) returns **17 of the 19**
config keys. It omits `CONFIG_BASE_HEIGHT` and `CONFIG_BASE_THICKNESS`.

`TandemView.action_set_tandem()` ([tandem_view.py:59](../../src/windows/views/tandem_view.py))
ends with:

```python
get_app().values.config_values = getCurrentValues()
```

That **replaces the entire live config dict** with the 17-key version, permanently dropping the
two collar keys from the running session.

`BrachyCylinder.shape()` ([cylinder.py:65-66](../../src/classes/mesh/cylinder.py)) then reads
them with a default:

```python
base_height    = float(get_app().values.config_values.get("CONFIG_BASE_HEIGHT", 0.0))
base_thickness = float(get_app().values.config_values.get("CONFIG_BASE_THICKNESS", 0.0))
```

Both fall back to `0.0`, and `add_base()` returns the shape unmodified when either is zero.

**Reproduction path:** import a plan → Cylinder tab → tick *Add Collar*, set thickness and
height → Apply → Tandem tab → *Generate Tandem* → back to Cylinder → change anything → Apply.
The collar is gone, and the *Add Collar* checkbox may still read as ticked.

The same 17-key omission also means **Export Current Settings as Config never writes the collar
settings**, so collar geometry cannot be saved or shared via a config file at all.

Suggested fix: add both keys to the `current_values` dict in `getCurrentValues()`. Consider
also changing `tandem_view.py:59` to `config_values.update(getCurrentValues())` so a partial
snapshot can never drop keys again.

### 7.2 MEDIUM — unsupported TPS vendor raises an unhandled `UnboundLocalError`

`read_dicom_folder()` ([dicom/fileio.py](../../src/classes/dicom/fileio.py)):

```python
if manufacturer == "Varian Medical Systems":
    data = load_varian_dicom_data(rp_file, rs_file)
if manufacturer == "Nucletron":
    data = load_nucletron_dicom_data(rp_file, rs_file)
else:
    pass
return data
```

Any other manufacturer leaves `data` unbound. The caller in
[import_view.py](../../src/windows/views/import_view.py) catches it with a bare `except` and
logs `"Empty folder selected."` — a misleading message for what is actually an unsupported
vendor. Note also that the second `if` should be `elif`; as written, a Varian plan evaluates
the Nucletron test too (harmlessly, but it is clearly not what was meant).

### 7.3 MEDIUM — `create_point()` can return `None`, then gets indexed

[`mesh/channel.py`](../../src/classes/mesh/channel.py):

```python
check = [0, 1]
try:
    check = create_point(p1, p2, radius)
except:
    pass
if (check[1]):
```

`create_point()` returns a 2-tuple on its `else` branch but **falls off the end returning
`None`** when `length < TIP_LENGTH` (2.5 mm). In that case `check` becomes `None` and `check[1]`
raises `TypeError` outside any handler. A plan whose first two needle points are closer than
2.5 mm apart would hit this.

Separately, the `except` branch a few lines later calls `fix2(p1, p2, radius)` while `fix2()`
is defined to take **no** arguments — a `TypeError` inside an already-failing path.

### 7.4 LOW — dead code and stale files

| Item | Problem |
|---|---|
| `get_cylinder_from_dicom()` in `dicom/fileio.py` | never called; passes `tip=`/`base=` to a `BrachyCylinder.__init__` that accepts neither — would raise `TypeError` |
| `benchmarks/benchmarking.py` | `total` used before assignment → `NameError` |
| `benchmarks/channels.py` | imports `Application.BRep.Channel` and `testing.data.channels`, neither of which exists; contains a hardcoded `C://Users//nsmel//...` path |
| `requirements.txt` | unused and stale — typo `matlplotlib`, and every pin disagrees with `spec-file.txt` (PySide6 6.9.3 vs 6.8.1, pydicom 2.4.3 vs 3.0.2, pyinstaller 6.0.0 vs 6.20.0). **Do not use it.** |
| `intersections.are_colliding()` | defined, never called — needle collision detection is not performed |
| `AppSignals.exportFile` | declared, never emitted, never connected |
| `DicomData.central_axis_flag` | set in `__init__`, missing from `reset()`, never read |
| `add_notch(z_offset=...)` | the parameter is computed and passed but the translation is commented out, so the notch is always at `z=0` even with a collar |
| `generate_cylinder_points` / `get_surface_intersection` / `get_interstitial_length` in `mesh/channel.py` | duplicated (worse) copies of the `template_reference.py` versions; unused |
| `.vs/brachify/v17/.wsuo`, `src/windows - Shortcut.lnk` | Windows-only artifacts committed by accident |

### 7.5 LOW — cross-platform rough edges

- `QIcon("resources\\brachify_splash-ico.ico")` in
  [app.py](../../src/classes/app.py) and [main_window.py](../../src/windows/main_window.py) uses
  a Windows path separator. On macOS/Linux this silently yields a null icon. Cosmetic.
- `spec-file.txt` is `win-64` only (§1.2).

### 7.6 Traps that are not bugs — know these before editing

- **`BrachyCylinder.shape()` caches.** Clear `self._shape` in any new mutator.
- **`NavigationModel.views` order is frozen** (§4.3). It is indexed positionally everywhere.
- **`@display_action` is mandatory** on any view method that changes geometry (§4.5).
- **`DicomData.__init__` and `reset()` must stay in sync** (§5.3).
- **Adding a config key touches four places** (§6.2).
- **`*_ui.py` files are generated** — edit the `.ui` and re-run `pyside6-uic` (§5.6).
- **The two tandem rotation spin boxes** must be written together (§5.6).
- **Varian and Nucletron readers are parallel** — a fix in one usually needs a mirror fix
  (§5.3).
- **Bare `except:` is pervasive.** When debugging, expect failures to be swallowed; add a
  temporary `log.exception()` rather than trusting the absence of an error message.

---

## 8. Testing

### 8.1 Policy

**This project follows test-driven development**, including the superpowers iron law: no
production code without a failing test first. Code written before its test is deleted and
rewritten from the test. The full rules, including the anti-slop rules every agent applies at
session start, live in
[AGENTS.md](../../AGENTS.md#session-start) and
[AGENTS.md](../../AGENTS.md#testing-write-the-test-first). They are enforced by the
[pull request template](../../pull_request_template.md): write the test, watch it fail, make
it pass, then break the code on purpose to confirm the test catches it.

Test files are **scoped by subfolder** mirroring `src/` — `tests/mesh/`, `tests/dicom/`,
`tests/views/`, `tests/settings/`, and so on. Nothing sits loose at the root of `tests/`. See
[tests/README.md](../../tests/README.md). `utils/` follows the same scoping rule; see
[utils/README.md](../../utils/README.md).

### 8.2 Current state

**There are no tests yet.** No test files, no test framework configured correctly, no CI.

- [`.vscode/settings.json`](../../.vscode/settings.json) enables pytest against a `testing/`
  directory that does not exist. The repository now has `tests/`, so this setting is wrong and
  should be updated to `["tests"]`.
- `benchmarks/` is dead (§7.4) and is not a test suite.
- There is no `.github/` directory and no CI of any kind.

The first change that adds a test must also put `src/` on `sys.path` — either a `conftest.py`
at the repository root that inserts it, or `pythonpath = ["src"]` in a `pytest.ini` /
`pyproject.toml` — and fix the `.vscode` setting above to point at `tests`.

### 8.3 Highest-value targets

In rough order — all are pure functions with no Qt or OCC dependency
and can be tested without launching the app:

1. `helper.rotate_points()` — the DICOM→cylinder transform; wrong here means every needle is
   wrong.
2. `settings/load.load_config_file()` and `checkValuesExist()` — pure dict logic, and the
   round-trip bug in §7.1 would have been caught by a single test asserting
   `set(getCurrentValues()) == set(DEFAULT_CONFIG_VALUES)`.
3. `channel.remove_identical_points()` / `remove_collinear_points()` / `apply_deadspace_to_points()`.
4. `template_reference.extract_points_from_channels2()` — the `z=0` normalisation, with its
   three branches (crosses / stops short / lands exactly).
5. `template_reference.calculate_protrusion_lengths()`.

---

## 9. Maintaining this document

### 9.0 This file is part of a documentation set

**The whole documentation set is updated in the same pull request as the change it describes.**
It is never a follow-up task and never a separate "docs PR".

The set is **every markdown file** in `docs/`, `tests/` and `utils/`, plus three files at the
repository root:

| File | Covers |
|---|---|
| `docs/project/COSC499-TEAM10-PROJECT-DOCS.md` | this file, the source of truth |
| [docs/README.md](../README.md) | index of the `docs/` tree |
| [docs/contract/README.md](../contract/README.md) | team contract |
| [docs/proposal/README.md](../proposal/README.md) | project proposal |
| [docs/design/README.md](../design/README.md) | UI mocks and design artifacts |
| [docs/minutes/README.md](../minutes/README.md) | meeting minutes |
| [docs/logs/README.md](../logs/README.md) | team and individual logs |
| [docs/workflows/README.md](../workflows/README.md) | index of the tool-agnostic workflows |
| [docs/workflows/commit.md](../workflows/commit.md) | the canonical commit procedure |
| [docs/workflows/make-pr.md](../workflows/make-pr.md) | the canonical pull request procedure |
| [tests/README.md](../../tests/README.md) | TDD policy, `tests/` scoping rule, what to test first |
| [utils/README.md](../../utils/README.md) | `utils/` scoping rule and what belongs there |
| [README.md](../../README.md) | repository entry point |
| [AGENTS.md](../../AGENTS.md) | how to work in this repo |
| [CLAUDE.md](../../CLAUDE.md) | agent entry point, imports `AGENTS.md` |

Reviewing a file and concluding it needs no change is a valid outcome. **Silently not looking
is not.** If nothing in the set needed changing, say so explicitly in the pull request.

Not in the set, because they are inherited from upstream *brachify* and must not be edited
casually: [README-BRACHIFY.md](../../README-BRACHIFY.md),
[virtual_environments_instructions.md](../../virtual_environments_instructions.md),
[pull_request_template_brachify.md](../../pull_request_template_brachify.md), and everything in
[notes/](../../notes/). If one of those has become wrong, record the correction here instead of
rewriting upstream's file.

The set cross-references itself. **If you change a rule stated in more than one file, update
every copy.** A rule that appears in three places and is true in two is worse than one that
appears once.

[AGENTS.md](../../AGENTS.md) carries the same table for AI agents, and the
[pull request template](../../pull_request_template.md) turns it into a per-file checklist the
reviewer signs off.

### 9.1 When this file specifically must be updated

Beyond the set-wide rule above, update **this** document when you:

- add, remove, or rename a module, view, model, or config key;
- change the startup sequence, the signal graph, or the display pipeline;
- change the DICOM contract (new vendor, new required structure name, changed field);
- change setup, dependencies, or the environment in any way;
- fix anything listed in §7 — move it out of "known bugs", do not just delete the entry;
- discover a new bug or trap — add it to §7 rather than leaving it in a PR comment;
- add tests — update §8.

### 9.2 Which section to touch

| Change | Section |
|---|---|
| dependency, environment, run command | §1 Setup |
| new module or file | §4.7 directory map **and** §5 module reference |
| new/changed signal or model wiring | §4.4 |
| new/changed view or widget | §4.3, §5.6 |
| new/changed config key | §6.2 (and remember the four code sites) |
| new/changed export format | §6.4 |
| bug found or fixed | §7 |
| test added | §8 |

### 9.3 Rules for edits

1. Obey the standing mandate in §2 — read the code, do not guess.
2. Mark claims *Verified* or *Reasoned from code*. Do not silently promote the second to the
   first.
3. Update the **Last full code audit** date in the header only after an actual full re-read,
   not after a small edit.
4. Keep file references as relative markdown links so they stay clickable from GitHub and from
   an IDE.
5. If you remove a §7 entry because it was fixed, note the fix — a reader should be able to see
   that the trap once existed.

### 9.4 Related files

| File | Role |
|---|---|
| [AGENTS.md](../../AGENTS.md) | instructions for AI agents; points here for project context |
| [CLAUDE.md](../../CLAUDE.md) | Claude Code entry point; imports `AGENTS.md` |
| [pull_request_template.md](../../pull_request_template.md) | Team 10 PR checklist, includes the update-this-doc gate |
| [pull_request_template_brachify.md](../../pull_request_template_brachify.md) | upstream's original review process, preserved |
| [docs/README.md](../README.md) | index of the `docs/` tree |
| [README-BRACHIFY.md](../../README-BRACHIFY.md) | upstream project README (user-facing) |
| [virtual_environments_instructions.md](../../virtual_environments_instructions.md) | upstream conda guide (Windows-centric) |
| [notes/](../../notes/) | upstream developer notes |
| [user_guide/Brachify User Manual.docx](../../user_guide/Brachify%20User%20Manual.docx) | end-user manual; authoritative on clinical workflow |

---

## 10. Glossary

| Term | Meaning |
|---|---|
| **Brachytherapy** | Radiotherapy delivering a sealed radioactive source inside or next to the treatment volume. |
| **Interstitial** | Needles passing *through* tissue, as opposed to sitting in a body cavity. The "interstitial length" is how far a needle protrudes past the cylinder surface into tissue. |
| **Applicator / cylinder** | The physical device inserted into the patient. brachify generates a printable, patient-specific one. |
| **Tandem** | A curved central channel, typically for a uterine source. Either generated parametrically or imported as a STEP model. |
| **Channel** | One needle path. Each becomes a bored hole in the printed cylinder. |
| **Central Axis** | The mandatory reference channel defining the cylinder axis (§3.2). |
| **Dead space** | Distance from the needle tip to the first dwell position; extends the tip in interstitial length calculations. |
| **Collet** | A small printed insert holding a needle at the cylinder base. Models in `3D Models and Templates/`; the PDF draws tolerance rings for them. |
| **Notch** | Small raised marker fused to the cylinder wall at `z=0` indicating orientation. |
| **Collar / base** | Optional ring around the cylinder base (`CONFIG_BASE_*`). Called "base" in code, "Collar" in the UI. |
| **TPS** | Treatment Planning System — Varian BrachyVision or Elekta Oncentra. |
| **RTPLAN / RTSTRUCT / RTDOSE** | DICOM radiotherapy modalities. brachify reads the first two, ignores the third. |
| **ROI** | Region of Interest — a DICOM structure identifier. |
| **OCC / OpenCASCADE** | The B-rep CAD kernel, reached through `pythonocc-core`. |
| **B-rep** | Boundary representation — solids described by faces/edges/vertices rather than meshes. |
| **TopoDS_Shape** | The OCC base type for all geometry. |
| **Dwell time** | How long the source sits at a position. Must be zero for `Central Axis`. |
