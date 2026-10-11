# COSC 499 — Team 10 — Brachify Initial Codebase Guide

**What this is.** A plain-language guide to the brachify code **as it came from upstream, before
Team 10 changed any of it**. It explains what each part of the code does, where its values come
from, what reads them next, and what happens when a value changes, using real values from the
sample data in this repository. It assumes no background: every term is explained the first
time it appears, and every number shown is explained where it is used.

**What this is not.** It is not the source of truth.
[COSC499-TEAM10-PROJECT-DOCS.md](COSC499-TEAM10-PROJECT-DOCS.md) is. That file is the
reference: setup, architecture, the module reference, the configuration schema, and the
catalogue of known bugs in §7. This file is the walkthrough you read first, so that the
reference makes sense. Where the two disagree, the source of truth wins, and when either
disagrees with the code, **the code wins** and the document is corrected. The bugs this guide
found are recorded in §7 of the source of truth: §7.1 was corrected from the runs shown here,
and §7.7 to §7.9 were added (2026-10-02).

**The baseline: before any code changes.** This document describes brachify exactly as it came
from the upstream project, [brachify/brachify](https://github.com/brachify/brachify), before Team
10 implemented any new feature or made any significant change to the code. It was written at
that point, on purpose, so the team has a record of the starting point.

*Verified* on 2026-10-01: `src/` on Team 10's `main` (commit `5fedf69`) was byte-for-byte
identical to `src/` on upstream's `main` (commit `f89cafe`), and no Team 10 commit had touched
`src/`.

When the code changes later, this document is not rewritten to match. It stays a description of
the original code. A section that a change makes out of date gets a short note saying so, and
pointing to where the new behaviour is documented, in the same pull request as the change.

**How sure each statement is.** This file uses the same two markers as the source of truth:

- *Verified* means observed by running brachify's own code, with the result shown.
- *Reasoned from code* means worked out by reading the code, not run.

The *Verified* results came from running brachify's own code on copies of the sample folders,
with `HOME` pointed at a scratch folder so that no real `~/brachify/` files were read or written,
and with the PDF viewer switched off so nothing opened on screen. The scripts used were not
committed. The drawings of the 3D model in [chapter 11](#11-classesmesh) were made by slicing
brachify's real 3D shapes with a flat plane and testing one point per character, so every
character sits where the geometry really is.

---

## Table of contents

1. [3D Models and Templates/](#1-3d-models-and-templates)
    1. [Words you need](#11-words-you-need)
    2. [How a collet fits the printed cylinder](#12-how-a-collet-fits-the-printed-cylinder)
    3. [The two drawings](#13-the-two-drawings)
    4. [The two Word documents, and how they connect to the code](#14-the-two-word-documents-and-how-they-connect-to-the-code)
    5. [Things nothing checks](#15-things-nothing-checks)
2. [benchmarks/](#2-benchmarks)
    1. [What it was meant to do](#21-what-it-was-meant-to-do)
    2. [Why it does not run](#22-why-it-does-not-run)
    3. [Things nothing checks](#23-things-nothing-checks)
3. [Images/](#3-images)
    1. [How they differ from today's code](#31-how-they-differ-from-todays-code)
    2. [Things nothing checks](#32-things-nothing-checks)
4. [notes/](#4-notes)
    1. [The workflow in gui.txt](#41-the-workflow-in-guitxt)
    2. [Where the notes have gone stale](#42-where-the-notes-have-gone-stale)
    3. [Things nothing checks](#43-things-nothing-checks)
5. [resources/](#5-resources)
    1. [How the icon is reached](#51-how-the-icon-is-reached)
    2. [Things nothing checks](#52-things-nothing-checks)
6. [SI_C_D30 Brachify_Ex1/](#6-si_c_d30-brachify_ex1)
    1. [Words you need](#61-words-you-need)
    2. [How the three files fit together](#62-how-the-three-files-fit-together)
    3. [Inside the plan (RP)](#63-inside-the-plan-rp)
    4. [Inside the structures (RS)](#64-inside-the-structures-rs)
    5. [Inside the dose (RD)](#65-inside-the-dose-rd)
    6. [What brachify makes of Ex1](#66-what-brachify-makes-of-ex1)
    7. [Things nothing checks](#67-things-nothing-checks)
7. [SI_C_D30 Brachify_Ex2/](#7-si_c_d30-brachify_ex2)
    1. [How the three files fit together](#71-how-the-three-files-fit-together)
    2. [Inside the plan (RP)](#72-inside-the-plan-rp)
    3. [Inside the dose (RD)](#73-inside-the-dose-rd)
    4. [How Ex2 differs from Ex1](#74-how-ex2-differs-from-ex1)
    5. [What brachify makes of Ex2](#75-what-brachify-makes-of-ex2)
    6. [Things nothing checks](#76-things-nothing-checks)
8. [src/](#8-src)
    1. [Words you need](#81-words-you-need)
    2. [launch.py, starting the app](#82-launchpy-starting-the-app)
    3. [When starting fails](#83-when-starting-fails)
    4. [Starting with a folder](#84-starting-with-a-folder)
    5. [\_\_init\_\_.py, an empty file](#85-__init__py-an-empty-file)
    6. [windows - Shortcut.lnk, an accidental file](#86-windows---shortcutlnk-an-accidental-file)
    7. [What happens if something here changes](#87-what-happens-if-something-here-changes)
    8. [Things nothing checks](#88-things-nothing-checks)
9. [classes/](#9-classes)
    1. [Words you need](#91-words-you-need)
    2. [What happens when the app starts](#92-what-happens-when-the-app-starts)
    3. [\_\_init\_\_.py, an empty file](#93-__init__py-an-empty-file)
    4. [info.py, names and folders](#94-infopy-names-and-folders)
    5. [logger.py, the log](#95-loggerpy-the-log)
    6. [signals.py, app-wide announcements](#96-signalspy-app-wide-announcements)
    7. [app.py, the application object](#97-apppy-the-application-object)
    8. [What happens if something here changes](#98-what-happens-if-something-here-changes)
    9. [Things nothing checks](#99-things-nothing-checks)
10. [classes/dicom](#10-classesdicom)
    1. [The real-world story](#101-the-real-world-story)
    2. [Words you need](#102-words-you-need)
    3. [What is inside the sample files](#103-what-is-inside-the-sample-files)
    4. [data.py, the form brachify fills in](#104-datapy-the-form-brachify-fills-in)
    5. [fileio.py, how the form gets filled](#105-fileiopy-how-the-form-gets-filled)
    6. [Elekta Oncentra files](#106-elekta-oncentra-files)
    7. [What the rest of the app does with the form](#107-what-the-rest-of-the-app-does-with-the-form)
    8. [What happens if a value in the file changes](#108-what-happens-if-a-value-in-the-file-changes)
    9. [Things nothing checks](#109-things-nothing-checks)
11. [classes/mesh](#11-classesmesh)
    1. [Words you need](#111-words-you-need)
    2. [How to read the drawings](#112-how-to-read-the-drawings)
    3. [The whole model in one picture](#113-the-whole-model-in-one-picture)
    4. [The files](#114-the-files)
    5. [cylinder.py and notch.py, the solid cylinder](#115-cylinderpy-and-notchpy-the-solid-cylinder)
    6. [channel.py, one tube per needle](#116-channelpy-one-tube-per-needle)
    7. [tandem.py, the tandem](#117-tandempy-the-tandem)
    8. [helper.py, intersections.py and fileio.py](#118-helperpy-intersectionspy-and-fileiopy)
    9. [How it all comes together at export](#119-how-it-all-comes-together-at-export)
    10. [What happens if a setting changes](#1110-what-happens-if-a-setting-changes)
    11. [Things nothing checks](#1111-things-nothing-checks)
12. [classes/pdf](#12-classespdf)
    1. [What the reference sheet looks like](#121-what-the-reference-sheet-looks-like)
    2. [Words you need](#122-words-you-need)
    3. [How the sheet is made, step by step](#123-how-the-sheet-is-made-step-by-step)
    4. [How an interstitial length is measured](#124-how-an-interstitial-length-is-measured)
    5. [The base map](#125-the-base-map)
    6. [Every function](#126-every-function)
    7. [What happens if a setting changes](#127-what-happens-if-a-setting-changes)
    8. [Things nothing checks](#128-things-nothing-checks)
13. [src/settings](#13-srcsettings)
    1. [Words you need](#131-words-you-need)
    2. [The 19 settings](#132-the-19-settings)
    3. [defaults.py, the built-in values](#133-defaultspy-the-built-in-values)
    4. [values.py, the live settings](#134-valuespy-the-live-settings)
    5. [load.py, reading a settings file](#135-loadpy-reading-a-settings-file)
    6. [reset.py, into the boxes and back out](#136-resetpy-into-the-boxes-and-back-out)
    7. [The two files on disk](#137-the-two-files-on-disk)
    8. [What happens if something here changes](#138-what-happens-if-something-here-changes)
    9. [Things nothing checks](#139-things-nothing-checks)
14. [src/windows](#14-srcwindows)
    1. [Words you need](#141-words-you-need)
    2. [What the window is made of](#142-what-the-window-is-made-of)
    3. [main_window.py, building the window](#143-main_windowpy-building-the-window)
    4. [palettes.py, two themes nothing uses](#144-palettespy-two-themes-nothing-uses)
    5. [What happens if something here changes](#145-what-happens-if-something-here-changes)
    6. [Things nothing checks](#146-things-nothing-checks)
15. [src/windows/models](#15-srcwindowsmodels)
    1. [Words you need](#151-words-you-need)
    2. [How the models connect](#152-how-the-models-connect)
    3. [shape_model.py, one shape packaged for the 3D view](#153-shape_modelpy-one-shape-packaged-for-the-3d-view)
    4. [display_model.py, what the 3D view shows](#154-display_modelpy-what-the-3d-view-shows)
    5. [dicom_model.py, the imported plan](#155-dicom_modelpy-the-imported-plan)
    6. [cylinder_model.py, the cylinder](#156-cylinder_modelpy-the-cylinder)
    7. [channels_model.py, the needles](#157-channels_modelpy-the-needles)
    8. [tandem_model.py, the tandem](#158-tandem_modelpy-the-tandem)
    9. [navigation_model.py, the five tabs](#159-navigation_modelpy-the-five-tabs)
    10. [What happens if something here changes](#1510-what-happens-if-something-here-changes)
    11. [Things nothing checks](#1511-things-nothing-checks)
16. [src/windows/splashscreen](#16-srcwindowssplashscreen)
    1. [Words you need](#161-words-you-need)
    2. [How the splash screen is used](#162-how-the-splash-screen-is-used)
    3. [How the icons are used, and where they go missing](#163-how-the-icons-are-used-and-where-they-go-missing)
    4. [What happens if something here changes](#164-what-happens-if-something-here-changes)
    5. [Things nothing checks](#165-things-nothing-checks)
17. [src/windows/views](#17-srcwindowsviews)
    1. [Words you need](#171-words-you-need)
    2. [How every tab works](#172-how-every-tab-works)
    3. [import_view.py, the Import tab](#173-import_viewpy-the-import-tab)
    4. [cylinder_view.py, the Cylinder tab](#174-cylinder_viewpy-the-cylinder-tab)
    5. [channels_view.py, the Channels tab](#175-channels_viewpy-the-channels-tab)
    6. [tandem_view.py, the Tandem tab](#176-tandem_viewpy-the-tandem-tab)
    7. [export_view.py, the Export tab](#177-export_viewpy-the-export-tab)
    8. [viewport.py, the 3D view](#178-viewportpy-the-3d-view)
    9. [What happens if something here changes](#179-what-happens-if-something-here-changes)
    10. [Things nothing checks](#1710-things-nothing-checks)
18. [src/windows/ui](#18-srcwindowsui)
    1. [Words you need](#181-words-you-need)
    2. [From a drawing to a tab](#182-from-a-drawing-to-a-tab)
    3. [What each design file contains](#183-what-each-design-file-contains)
    4. [Are the generated files up to date?](#184-are-the-generated-files-up-to-date)
    5. [Changing a design file](#185-changing-a-design-file)
    6. [Colours and other text in the design files](#186-colours-and-other-text-in-the-design-files)
    7. [Things nothing checks](#187-things-nothing-checks)
19. [user_guide/](#19-user_guide)
    1. [What the manual covers](#191-what-the-manual-covers)
    2. [Where the manual and the code disagree](#192-where-the-manual-and-the-code-disagree)
    3. [Things nothing checks](#193-things-nothing-checks)

---

## 1. 3D Models and Templates/

**Summary.** `3D Models and Templates/` holds the physical side of brachify: 3D models and
drawings of the **collets**, the small threaded sleeves that screw into the base of a printed
cylinder and grip each needle, and two Word documents from the clinic. `Values for Cylinders` is
the physicist's list of dimensions, and six of its seven numbers are exactly the defaults in the
code's settings; the seventh, the needle thread depth, says 4.5 mm where the code says 5.0.
`3D Printed Cylinder QA` is the checklist run on every printed cylinder. No code reads anything
in this folder. Its `readme.txt` also lists wrench models and template cylinders that are not
there. The folder came from the upstream project and is never edited.

[`3D Models and Templates/`](../../3D%20Models%20and%20Templates/) holds 12 files. *Verified* by
opening each one:

| File | What it is |
|---|---|
| `Collets - Plastic - Gyn.SLDPRT` / `.STL` | the collet for plastic GYN needles. The `.STL` is 5 × 5 × 15 mm |
| `Collets - Plastic - Gyn - Small Outer Diameter.SLDPRT` / `.STL` | a thinner version, 4 × 4 × 15 mm |
| `Collets - Steel - Prostate.SLDPRT` / `.STL` | the collet for steel prostate needles, 5 × 5 × 15 mm |
| `Collet - Plastic - Gyn - Machined.SLDPRT` / `.pdf` | a collet cut on a lathe instead of printed, and its drawing |
| `Tandem collet - Sheet1.pdf` | the drawing of the tandem's collet |
| `Values for Cylinders (1).docx` | the physicist's reference dimensions |
| `3D Printed Cylinder QA.docx` | the checklist run on every printed cylinder |
| `readme.txt` | five lines describing the folder |

### 1.1 Words you need

| Word | What it means here | Real example |
|---|---|---|
| **collet** | a small threaded sleeve that screws into a hole in the cylinder's base and grips a needle | 5 mm across for plastic GYN needles |
| **`.SLDPRT`** | a SolidWorks part: the editable 3D source model. It needs SolidWorks to open | `Collets - Plastic - Gyn.SLDPRT` |
| **`.STL`** | the same part as triangles, the format 3D printers read ([11.8](#118-helperpy-intersectionspy-and-fileiopy)) | `Collets - Plastic - Gyn.STL` |
| **engineering drawing** | a 2D drawing with every dimension, for a machinist | `Tandem collet - Sheet1.pdf` |
| **M4 × 0.7** | a metric screw thread: 4 mm across, 0.7 mm between threads | the machined collet's thread |
| **QA** | quality assurance: the checks done before a device is used | the printed cylinder checklist |

### 1.2 How a collet fits the printed cylinder

```
            the printed cylinder, seen from the side, at its base
        │                                          │
        │        the needle's channel, 2.7 mm      │
        │                 │ │                      │
        │                 │ │                      │
        │               ┌─┘ └─┐  the threaded hole, 3.17 mm across, 5 mm deep
 ───────┴───────────────┤     ├────────────────────┴───────  the base, height 0
                        │█████│  ← the collet screws in here from below,
                        │█████│     5 mm across, and grips the needle
                        └─────┘
                           │
                           │  the needle comes in from below, through the collet
```

The holes are made by the code ([11.6](#116-channelpy-one-tube-per-needle)). The collets are
printed separately from the `.STL` files in this folder, screwed in by hand, and tightened on each
needle. The code never models a collet. Its only sign of one is the optional collet ring on the
PDF ([12.5](#125-the-base-map)).

### 1.3 The two drawings

| Drawing | Length | Body | Thread | Bore (the hole for the needle or tandem) |
|---|---|---|---|---|
| machined GYN collet | 14 mm | 5 mm across | M4 × 0.7 | 2.08 mm, a "#42 drill", for a plastic needle |
| tandem collet | 24 mm | 6 mm across, with an 8 mm head | M6 × 1.0 | 3.18 mm, for the tandem |

Both have a 0.5 mm slot cut across the threaded end, so screwing the collet in squeezes it onto
the needle. The drawings' title blocks say "DIMENSIONS ARE IN INCHES". That line comes from the
SolidWorks template: the main numbers are in millimetres, with inches in brackets.

### 1.4 The two Word documents, and how they connect to the code

**`Values for Cylinders`** against the code's defaults ([13.2](#132-the-19-settings)). *Verified*:

| The document says | The code's default | Match? |
|---|---|---|
| needle thread diameter 3.17 mm | `CONFIG_CHANNELS_THREADING_DIAMETER` 3.17 | yes |
| needle channel 2.7 mm | `CONFIG_CHANNELS_DIAMETER` 2.7 | yes |
| tandem channel 3.8 mm | `CONFIG_TANDEM_CHANNEL_DIAMETER` 3.8 | yes |
| tandem tap 5.0 mm | `CONFIG_TANDEM_THREADING_DIAMETER` 5.0 | yes |
| tandem thread depth 7 mm | `CONFIG_TANDEM_THREADING_DEPTH` 7.0 | yes |
| default cylinder length 160 mm | `CONFIG_CYLINDER_LENGTH` 160.0 | yes |
| **needle thread depth 4.5 mm** | **`CONFIG_CHANNELS_THREADING_DEPTH` 5.0** | **no** |

It also lists planning limits that nothing in the code checks: a minimum bend radius of 50 mm, at
most 45° from vertical, more than 4.5 mm from the cylinder's edge, and 6 mm between needle thread
centres. Ex2's closest needle holes are 3.10 mm apart ([11.10](#1110-what-happens-if-a-setting-changes)).

The collet sizes match the PDF's collet rings: the needle collet is 5 mm across
(`CONFIG_NEEDLE_COLLET_OUTER_DIAMETER` 5.0), and the tandem collet's head is 8 mm
(`CONFIG_TANDEM_COLLET_OUTER_DIAMETER_OUTER` 8.0). The tandem tap of 5.0 mm is the standard drill
size for the tandem collet's M6 × 1.0 thread, so the hole and the collet fit each other. That last
link is *Reasoned*: no file states it.

**`3D Printed Cylinder QA`** is the clinic's checklist, written by Michael Kudla on 15-Oct-25. It
shows where brachify sits in the clinical workflow:

```
 exam under anaesthesia → import and registration → contours → preplan
   → export and 3D model  ← brachify
   → print → QA → sterilize → treat
```

Its checks include "Needle threads lock with correct needle", "Needles are not too close to each
other", "Interstitial lengths are correct (… add 0.6 cm for plastic, 1.0 cm for metal needles)",
which is where the 6.0 mm `CONFIG_DEADSPACE` comes from, and "Tandem is channel 5".

### 1.5 Things nothing checks

- **That the readme is right.** `readme.txt` lists "3D Models of Wrenches" and "Template
  Cylinders", and the folder holds neither.
- **That the code and the document agree.** The needle thread depth is 4.5 mm in one and 5.0 in
  the other, and which is right has not been checked with the physicist.
- **The planning limits.** The minimum bend radius, the 45° limit and the 6 mm spacing are written
  down here, and nothing in the code enforces them.
- **This folder is inherited from upstream and is never edited** (AGENTS.md). Corrections go in
  the source of truth instead.

---

## 2. benchmarks/

**Summary.** `benchmarks/` is a small speed-testing tool the original developer wrote in October
2023, to time how long one needle's tube takes to build. `benchmarking.py` runs a function several
times and prints the fastest, average and slowest time, and `channels.py` uses it on the tube
builder. Both have been broken since December 2023, when the code was reorganised: `channels.py`
imports modules that no longer exist, and `benchmarking.py` crashes before it prints its summary.
Nothing in the app, the build or the tests uses this folder.

[`benchmarks/`](../../benchmarks/) holds two files:

| File | Size | What it is |
|---|---|---|
| [`benchmarking.py`](../../benchmarks/benchmarking.py) | 23 lines | `benchmark_test`: times a function, `count` times, and prints a table |
| [`channels.py`](../../benchmarks/channels.py) | 14 lines | times `rounded_channel` on a sample needle, 4 times |

### 2.1 What it was meant to do

```
 channels.py
   ├─ add the original developer's own Windows folder to Python's search path
   ├─ import the tube builder from Application.BRep.Channel     ← moved in December 2023
   ├─ import sample needles from testing.data.channels         ← deleted in December 2023
   └─ benchmark_test(build the 4th sample needle's tube).run(4)
          │
          ▼
 benchmarking.py
   for each of the 4 runs: start a timer, run the function, stop the timer, print the time
   then add the times up ← crashes here
   print  | min | avg | max |
```

The tube builder is the slowest part of brachify: on Ex2 it takes 0.5 to 1 second per needle
([11.6](#116-channelpy-one-tube-per-needle)). That is what this was written to measure.

### 2.2 Why it does not run

*Verified*, by running both:

| File | What happens |
|---|---|
| `channels.py` | stops at once: `ModuleNotFoundError: No module named 'Application'`. The tube builder moved from `Application/BRep/Channel.py` to `src/classes/mesh/channel.py` in commit `c1e0289` (2023-12-13), and the same commit deleted `testing/data/channels.py` |
| `benchmarking.py` | runs the function and prints each time, then stops with `UnboundLocalError: cannot access local variable 'total'`, because `total` is added to before it is ever set to 0 |

Line 3 of `channels.py` also adds `C://Users//nsmel//…` to Python's search path, a folder that only
existed on the original developer's computer.

### 2.3 Things nothing checks

- **That this folder still runs.** Nothing uses it, so nothing noticed it broke.
- **That it is not mistaken for tests.** It is not a test suite; the tests live in `tests/`.
  AGENTS.md and `tests/README.md` say the same.

---

## 3. Images/

**Summary.** `Images/` holds six screenshots used in the upstream project's README: one of each
tab, and one example reference sheet. They show an older version of brachify than the code in
this repository: the Export tab in the screenshot has no collet controls, and the example sheet
fits on one page. Nothing in the app uses them. The folder came from the upstream project and is
never edited.

[`Images/`](../../Images/) holds six pictures, all shown in
[`README-BRACHIFY.md`](../../README-BRACHIFY.md). *Verified* sizes:

| File | Size (pixels) | Shows |
|---|---|---|
| `import_tab.png` | 1,374 × 956 | the Import tab after importing a 22-needle plan, with the info panel filled in |
| `cylinder_tab.png` | 1,374 × 956 | the Cylinder tab |
| `channels_tab.png` | 1,374 × 956 | the Channels tab |
| `tandem_tab.png` | 1,374 × 956 | the Tandem tab |
| `export_tab.png` | 1,374 × 956 | the Export tab: the cut-out cylinder, *Show Tandem* and four export buttons |
| `Example Ref Sheet.png` | 615 × 852 | a one-page reference sheet for an example plan, dated June 13, 2025 |

### 3.1 How they differ from today's code

| Screenshot | Today's code | So the screenshot is |
|---|---|---|
| `export_tab.png` has *Show Tandem* and four buttons | the Export tab also has *Show Collet Spacings* and three collet boxes ([17.7](#177-export_viewpy-the-export-tab)) | older than the collet feature |
| `Example Ref Sheet.png` fits the table and the base map on one page | on Ex2, the table fills page 1 and the base map is on page 2 ([12.1](#121-what-the-reference-sheet-looks-like)) | from a plan with fewer needles, or an older layout |
| `Example Ref Sheet.png` has no collet rings | the rings are optional, so this is still possible today | — |
| `import_tab.png` shows a plan of another test patient | — | a different sample plan, not Ex1 or Ex2 |

The Windows title bar in every screenshot shows they were taken on Windows, where the app is
mainly used.

### 3.2 Things nothing checks

- **That the README's screenshots are current.** They predate the collet controls.
- **This folder is inherited from upstream and is never edited** (AGENTS.md).

---

## 4. notes/

**Summary.** `notes/` holds the upstream developers' own notes: six short text files and two tiny
markdown files. The most useful is `gui.txt`, which describes the workflow for adding a button or
a tab, from Qt Designer to a tab's `action_…` function, and is still accurate. The others are
links to examples, the command for building the `.exe`, how to change the 3D view's background,
and a summary of Python's naming rules. Some are out of date: the build command uses module names
that the real build script no longer uses, and the naming rules are not followed by much of the
code. Nothing reads these files. The folder came from upstream and is never edited.

[`notes/`](../../notes/) holds eight files:

| File | Size | What it says | Still true? |
|---|---|---|---|
| `gui.txt` | 2.3 KB | the workflow for changing the window: Qt Designer → `.ui` → `pyside6-uic` → a tab's `action_…` → connect a button → `@display_action` | **yes**, it matches [17.2](#172-how-every-tab-works) and [18.2](#182-from-a-drawing-to-a-tab) |
| `deployment.txt` | 0.6 KB | links to a tutorial, and the `pyinstaller` command for the `.exe` | **partly**: see below |
| `background_color.txt` | 0.8 KB | how to give the 3D view a background picture: save a `.png` in `resources/` and add one line to `initViews` | the line is **not** in the code, so the view has the default background |
| `display.txt` | 0.2 KB | two links to pythonocc examples for colours and materials | links only |
| `optimizations.txt` | 0.3 KB | a link and an example of `BOPAlgo_Builder`, for joining many shapes faster in parallel | **not used**: the code joins shapes one by one |
| `style guide.txt` | 0.7 KB | a summary of PEP 8, Python's naming rules: modules lowercase, classes `CapWords`, functions `lower_case` | **not followed** in many places |
| `code_notes/notch.md` | 94 B | one line about `CylinderNotch` | — |
| `code_notes/reset.md` | 115 B | one line about `resetAllValues` | — |

### 4.1 The workflow in `gui.txt`

```
 edit the screen in Qt Designer
   → save as src/windows/ui/<name>_view.ui
   → pyside6-uic <name>_view.ui -o <name>_view_ui.py
   → in <name>_view.py: write  def action_<something>(self, *args):
   → connect the button:        self.ui.btn_<something>.pressed.connect(self.action_<something>)
   → if it changes the 3D model, put @display_action above the function
   → reach the models with      get_app().window.<model>
```

This is still how the code works.

### 4.2 Where the notes have gone stale

| Note | Says | The code does |
|---|---|---|
| `deployment.txt` | `--hidden-import "pydicom.encoders.gdcm"` and `"pydicom.encoders.pylibjpeg"` | `build_executable.py` uses `pydicom.pixels.encoders.gdcm` and `pydicom.pixels.encoders.pylibjpeg`, where pydicom 3 moved them. `README-BRACHIFY.md` has the old names too |
| `background_color.txt` | add `self.display.SetBackgroundImage('resources\\background.png')` to `initViews` | not in the code, and no `background.png` exists |
| `style guide.txt` | functions in `lower_case`, classes in `CapWords` | many functions are `camelCase`, such as `resetAllValues`, `getCurrentValues`, `createConfigMessageText`, `toString`, and some classes are not `CapWords`, such as `Export_View` and `benchmark_test` |

`style guide.txt` is about **names**, not colours. AGENTS.md and the source of truth used to
mention it next to the colour palettes, which made it sound like a colour guide. Both were
corrected on 2026-10-02.

### 4.3 Things nothing checks

- **That the notes match the code.** The build command and the background instructions have
  drifted.
- **That the naming rules are followed.**
- **This folder is inherited from upstream and is never edited** (AGENTS.md).

---

## 5. resources/

**Summary.** `resources/` holds the app's icon and one picture. `brachify_splash-ico.ico` is the
Windows icon: the build script gives it to PyInstaller as the `.exe` file's own icon, and the app
asks for it as the window's icon, though only on Windows does that path work. `brachify_splash.png`
is the splash artwork without the word "brachify", and is byte-for-byte the same file as one in
`src/windows/splashscreen/`. The folder came from upstream.

[`resources/`](../../resources/) holds two files. *Verified* by opening each:

| File | Size | What it is | Used by |
|---|---|---|---|
| `brachify_splash-ico.ico` | 22 KB | the Windows icon, holding seven sizes from 16 × 9 to 256 × 144 pixels | `build_executable.py` (`--icon`); `app.py` and `main_window.py` ask for it as the window's icon |
| `brachify_splash.png` | 115 KB, 1,280 × 720 pixels | the blue bands without the word *brachify* | nothing in the code. **The same file** as `src/windows/splashscreen/brachify_splash-ico.png` |

### 5.1 How the icon is reached

```
 build_executable.py ── --icon ./resources/brachify_splash-ico.ico ──▶ the .exe file's icon   works

 app.py, main_window.py ── QIcon("resources\\brachify_splash-ico.ico") ──┬─▶ Windows, started from
                                                                         │   the top folder: works
                                                                         └─▶ macOS, Linux: no icon
```

The path is relative to the folder you start the app from, and uses the Windows `\\` separator
([16.3](#163-how-the-icons-are-used-and-where-they-go-missing)).

### 5.2 Things nothing checks

- **That the icon is found.** On macOS and Linux it never is, silently.
- **Duplicates.** The same picture is in `resources/` and in `src/windows/splashscreen/`.
- **That the icon is square.** It is 16:9.

---

## 6. SI_C_D30 Brachify_Ex1/

**Summary.** `SI_C_D30 Brachify_Ex1/` is a sample treatment plan, exported from Varian's planning
system for a test object, not a person. It holds the three standard DICOM files of a brachytherapy
plan: the **plan** (RP), with 13 channels, the Central Axis and 12 needles; the **structures** (RS),
with 42 drawn shapes; and the **dose** (RD), a 3D grid of the radiation the plan would deliver. The
three files point at each other by their ID numbers. Brachify reads the plan and the structures,
finds the Central Axis, and builds 12 needle holes. It has no tandem, which is the one way it
differs from Ex2. How brachify reads these files is explained in [chapter 10](#10-classesdicom);
this chapter draws what is in them.

[`SI_C_D30 Brachify_Ex1/`](../../SI_C_D30%20Brachify_Ex1/) holds three files. *Verified*, by
reading every field:

| File | Size | Type | What it holds |
|---|---|---|---|
| `RP.1.2.246.352.71.5.…091619.dcm` | 64 KB | RTPLAN, the plan | 13 channels, the radiation source, the treatment machine |
| `RS.1.2.246.352.71.4.…092027.dcm` | 231 KB | RTSTRUCT, the structures | 42 drawn shapes |
| `RD.1.2.246.352.71.7.…092203.dcm` | 266 KB | RTDOSE, the dose | a 13 × 13 × 111 grid of doses |

Each file is named after its **ID** (DICOM calls it the SOP Instance UID): a long, globally unique
number. The long numbers are shortened to their last digits here.

### 6.1 Words you need

| Word | What it means here | Real example |
|---|---|---|
| **SOP Instance UID** | a DICOM file's own unique ID | `…250927091619` for this RP |
| **reference** | a field in one file holding another file's ID, so the two can be matched | the RP's `ReferencedStructureSetSequence` |
| **frame of reference** | the coordinate system the coordinates are measured in. Files that share one can be laid on top of each other | shared by the RS and the RD |
| **dose grid** | a 3D grid of boxes (voxels), each holding the radiation dose there | 13 × 13 × 111 voxels |
| **DVH** | dose-volume histogram: how much of a structure gets how much dose | one, in the RD |
| **fraction** | one treatment session | 1 planned |

The other words are in [10.2](#102-words-you-need).

### 6.2 How the three files fit together

```
 SI_C_D30 Brachify_Ex1/
 │
 ├── RP …091619   the plan                                   brachify reads it
 │     ├─ ReferencedStructureSetSequence ──────────────┐
 │     │     "my structures are …092027"               │
 │     └─ ApplicationSetupSequence → ChannelSequence   │
 │           13 channels, each with a ROI number ──────┼──┐
 │                                                     │  │
 ├── RS …092027   the structures                       │  │  brachify reads it
 │     ◀───────────────────────────────────────────────┘  │
 │     ├─ ReferencedFrameOfReferenceSequence ───────┐     │
 │     └─ 42 shapes, each with a ROI number   ◀─────┼─────┘  "channel N follows shape M"
 │                                                  │
 └── RD …092203   the dose                          │        brachify NEVER reads it
       ├─ FrameOfReferenceUID ◀─────────────────────┘        the same frame as the RS
       ├─ ReferencedRTPlanSequence  → "my plan is …091619"
       └─ ReferencedStructureSetSequence → the RS
```

*Verified*: the RP's reference matches the RS's ID, the RD's plan reference matches the RP's ID,
and the RD and RS share one frame of reference. Brachify never checks any of these: it takes the
first plan and the first structures file it finds in the folder ([10.5](#105-fileiopy-how-the-form-gets-filled)).

### 6.3 Inside the plan (RP)

```
 RP …091619
 ├─ Modality          = "RTPLAN"
 ├─ Manufacturer      = "Varian Medical Systems"
 ├─ PatientName       = "CYLINDER^D30"            a test object
 ├─ PatientID         = "SI_C_D30"
 ├─ RTPlanLabel       = "Brachify_Ex1"
 ├─ RTPlanDate        = "20250927"
 ├─ ApprovalStatus    = "UNAPPROVED"
 ├─ BrachyTreatmentType      = "HDR"              high dose rate
 ├─ BrachyTreatmentTechnique = "INTRACAVITARY"
 ├─ SourceSequence (1)               the radiation source
 │    ├─ SourceIsotopeName       = "Ir-192HDRFlexi"     iridium-192
 │    ├─ SourceIsotopeHalfLife   = 73.81 days
 │    └─ ReferenceAirKermaRate   = 40370, measured 2024-04-12
 ├─ TreatmentMachineSequence (1)
 ├─ FractionGroupSequence (1)        1 fraction planned
 ├─ DoseReferenceSequence (1)
 ├─ ReferencedStructureSetSequence (1)  → RS …092027
 └─ ApplicationSetupSequence (1)
      └─ ChannelSequence (13)        the channels below
```

| Channel | Label | Shape (ROI) | Name of that shape in the RS | Radiation time | Control points |
|---|---|---|---|---|---|
| 1 | Central Axis | 20 | `Applicator 1` | **222.8 s** | 20 |
| 2 | Applicator2 | 21 | `Applicator16` | 0 s | 40 |
| 3 | Applicator3 | 22 | `Applicator17` | 0 s | 40 |
| 4 | Applicator4 | 23 | `Applicator18` | 0 s | 40 |
| 5 | Applicator5 | 24 | `Applicator19` | 0 s | 40 |
| 6 | Applicator6 | 25 | `Applicator20` | 0 s | 40 |
| 7 | Applicator7 | **30** | `Applicator25` | 0 s | 40 |
| 8 | Applicator8 | **31** | `Applicator8` | 0 s | 40 |
| 9 | Applicator9 | **32** | `Applicator9` | 0 s | 40 |
| 10 | Applicator10 | **26** | `Applicator21` | 0 s | 40 |
| 11 | Applicator11 | **27** | `Applicator22` | 0 s | 40 |
| 12 | Applicator12 | **28** | `Applicator23` | 0 s | 40 |
| 13 | Applicator13 | **29** | `Applicator24` | 0 s | 40 |

The ROI numbers in bold are out of the channels' order, which is why brachify has to re-sort them
([10.5](#105-fileiopy-how-the-form-gets-filled)). All the radiation is in the Central Axis, and the
needles have none: this is a plan for a plain cylinder, and the manual asks for the opposite
([10.3](#103-what-is-inside-the-sample-files)).

### 6.4 Inside the structures (RS)

The RS is the same file in Ex1 and Ex2 ([7.4](#74-how-ex2-differs-from-ex1)). Its 42 shapes:

```
 RS …092027
 ├─ StructureSetLabel = "CT_1"
 ├─ ReferencedFrameOfReferenceSequence (1)
 ├─ StructureSetROISequence    (42)   each shape's number and name
 ├─ ROIContourSequence         (42)   each shape's points
 └─ RTROIObservationsSequence  (42)   each shape's kind
        │
        ├─ ROI 1        BODY                  the body outline, 111 flat slices
        ├─ ROI 2        Surface3              a marker, 21 points
        ├─ ROI 4        SI Seg Cyl            a 2-point line
        ├─ ROI 5–19     Applicator2 … 15      older needle drafts              not used by Ex1
        ├─ ROI 20       Applicator 1          2 points    ← Ex1's Central Axis
        ├─ ROI 21–32    Applicator16 … 25,    13 points each ← Ex1's 12 needles
        │               Applicator8, 9
        ├─ ROI 33       Central Axis          2 points    ← Ex2's Central Axis
        ├─ ROI 34–45    Applicator26 … 37     13 points each ← Ex2's 12 needles
        └─ ROI 46       Central Axis1         5 points    ← Ex2's Tandem
```

Ex1 uses shapes 20 to 32. The other 29 shapes are ignored. The full layout of the RS file is drawn
in [10.3](#103-what-is-inside-the-sample-files).

### 6.5 Inside the dose (RD)

```
 RD …092203
 ├─ Modality           = "RTDOSE"
 ├─ DoseUnits          = "GY"                   grays
 ├─ DoseType           = "PHYSICAL"
 ├─ DoseSummationType  = "PLAN"                 the whole plan's dose
 ├─ Columns × Rows × NumberOfFrames = 13 × 13 × 111 voxels
 ├─ PixelSpacing       = 2.5 × 2.5 mm, frames 1.25 mm apart
 ├─ ImagePositionPatient = (−14.79, 69.91, −63.75)   the first voxel's corner
 ├─ GridFrameOffsetVector   heights −63.75 to 73.75 mm
 ├─ DoseGridScaling    = 0.00001             each stored number × this = grays
 ├─ PixelData          18,759 numbers, 4 bytes each
 ├─ DVHSequence (1)
 ├─ ReferencedRTPlanSequence (1)          → RP …091619
 └─ ReferencedStructureSetSequence (1)    → RS
```

The dose ranges from 0.13 Gy at the grid's edge to 394.8 Gy right beside the source. Brachify
never opens this file.

### 6.6 What brachify makes of Ex1

*Verified*, by running brachify's reader on the folder ([10.5](#105-fileiopy-how-the-form-gets-filled)):

| | Result |
|---|---|
| the vendor | Varian |
| the Central Axis | found, shape 20 |
| needles | 12, Applicator2 to Applicator13 |
| tandem | none: no label contains "tandem" |
| the needles' points | the same as Ex2's needles, to the hundredth of a millimetre |

### 6.7 Things nothing checks

- **That the files belong together.** The references between them are correct here, and
  brachify never looks at them.
- **The radiation times.** The Central Axis has 222.8 s of radiation, against the manual.
- **This is de-identified clinical data, inherited from upstream, and never edited** (AGENTS.md).

---

## 7. SI_C_D30 Brachify_Ex2/

**Summary.** `SI_C_D30 Brachify_Ex2/` is the same sample as Ex1 with one channel added: a
**Tandem**. Its plan has 14 channels instead of 13, its structures file is the very same shapes as
Ex1's, saved a few minutes later, and its dose file includes the tandem's radiation. Because a
channel is labelled `Tandem`, brachify sets it as the tandem, switches it off as a needle, and
aims the tandem at it. It is the only sample that exercises the tandem, which is why most examples
in this document use Ex2.

[`SI_C_D30 Brachify_Ex2/`](../../SI_C_D30%20Brachify_Ex2/) holds three files. *Verified*:

| File | Size | Type | What it holds |
|---|---|---|---|
| `RP.1.2.246.352.71.5.…092034.dcm` | 68 KB | RTPLAN | 14 channels |
| `RS.1.2.246.352.71.4.…092027.dcm` | 231 KB | RTSTRUCT | the same 42 shapes as Ex1 |
| `RD.1.2.246.352.71.7.…092042.dcm` | 266 KB | RTDOSE | a 13 × 13 × 111 grid of doses |

The words are the same as in [6.1](#61-words-you-need).

### 7.1 How the three files fit together

```
 SI_C_D30 Brachify_Ex2/
 │
 ├── RP …092034   the plan, 14 channels                      brachify reads it
 │     ├─ ReferencedStructureSetSequence ──▶ RS …092027
 │     └─ ChannelSequence (14) ──── ROI numbers 33 to 46 ──▶ shapes in the RS
 │
 ├── RS …092027   the structures, 42 shapes                  brachify reads it
 │     └─ ReferencedFrameOfReferenceSequence ──┐
 │                                             │ the same frame
 └── RD …092042   the dose                     │             brachify NEVER reads it
       ├─ FrameOfReferenceUID ◀─────────────────┘
       ├─ ReferencedRTPlanSequence ──▶ RP …092034
       └─ ReferencedStructureSetSequence ──▶ RS
```

*Verified*: every reference matches. The RS file has the same name and ID as Ex1's.

### 7.2 Inside the plan (RP)

The same fields as Ex1's plan ([6.3](#63-inside-the-plan-rp)), with `RTPlanLabel` = `Brachify_Ex2`
and 14 channels:

| Channel | Label | Shape (ROI) | Name of that shape in the RS | Radiation time | Control points |
|---|---|---|---|---|---|
| 1 | Central Axis | 33 | `Central Axis` | **222.8 s** | 20 |
| 2 | Applicator2 | 34 | `Applicator26` | 0 s | 40 |
| 3 | Applicator3 | 35 | `Applicator27` | 0 s | 40 |
| 4 | Applicator4 | 36 | `Applicator28` | 0 s | 40 |
| 5 | Applicator5 | 37 | `Applicator29` | 0 s | 40 |
| 6 | Applicator6 | 38 | `Applicator30` | 0 s | 40 |
| 7 | Applicator7 | **43** | `Applicator35` | 0 s | 40 |
| 8 | Applicator8 | **44** | `Applicator36` | 0 s | 40 |
| 9 | Applicator9 | **45** | `Applicator37` | 0 s | 40 |
| 10 | Applicator10 | **39** | `Applicator31` | 0 s | 40 |
| 11 | Applicator11 | **40** | `Applicator32` | 0 s | 40 |
| 12 | Applicator12 | **41** | `Applicator33` | 0 s | 40 |
| 13 | Applicator13 | **42** | `Applicator34` | 0 s | 40 |
| 14 | **Tandem** | 46 | `Central Axis1` | **43.1 s** | 20 |

The tandem's shape is named `Central Axis1` in the RS. Brachify uses the plan's labels for Varian
files, so that name never matters ([10.4](#104-datapy-the-form-brachify-fills-in)).

### 7.3 Inside the dose (RD)

The same layout as Ex1's ([6.5](#65-inside-the-dose-rd)): 13 × 13 × 111 voxels, 2.5 mm by 2.5 mm,
frames 1.25 mm apart, from height −63.75 to 73.75 mm. The dose ranges from 0.15 Gy to 395.0 Gy,
slightly more than Ex1's because the tandem adds 43.1 s of radiation. It refers to Ex2's own plan,
`…092034`.

### 7.4 How Ex2 differs from Ex1

| | Ex1 | Ex2 |
|---|---|---|
| channels in the plan | 13 | **14**: the same 13 plus `Tandem` |
| the plan's ID | `…091619` | `…092034` |
| the plan's label | `Brachify_Ex1` | `Brachify_Ex2` |
| shapes used | 20 to 32 | 33 to 46 |
| the needles' points | — | **the same as Ex1's**: two copies of one set of needles |
| the RS file | — | **the same file**: only its save time differs, 09:28:37 against 09:36:48 |
| the dose file | 266 KB, up to 394.8 Gy | 266 KB, up to 395.0 Gy |
| brachify's result | 12 needles, no tandem | 12 needles, and the `Tandem` channel set as the tandem, switched off and used to aim it ([15.2](#152-how-the-models-connect)) |

### 7.5 What brachify makes of Ex2

*Verified*, throughout this document: the reader in [chapter 10](#10-classesdicom), the 3D model
in [chapter 11](#11-classesmesh), the PDF in [chapter 12](#12-classespdf), and the tabs in
[chapter 17](#17-srcwindowsviews) were all run on Ex2.

| | Result |
|---|---|
| the Central Axis | shape 33 |
| needles | 12 shown, and the `Tandem` channel switched off |
| the tandem's aim | 359.996°, the same direction as 0° |
| the export solid | 98,960.8 mm³, with 10,638.5 mm³ of holes |
| the reference sheet | 12 needles, lengths 1.8 to 2.5 cm, and a Tandem row |

### 7.6 Things nothing checks

- **That a tandem is a tandem.** It is found only because its label contains "tandem".
- **The radiation times.** The Central Axis and the tandem both have radiation, and nothing reads
  it.
- **This is de-identified clinical data, inherited from upstream, and never edited** (AGENTS.md).

---

## 8. src/

**Summary.** `src/` is the application: everything brachify runs is inside it. Directly in the
folder are three files. `launch.py` is the one you run: it creates the application object, builds
the window, and hands control to Qt, which then waits for clicks until the window is closed. If
it is given a folder when started, it opens the import dialog at that folder, which is how a
separate tool, brachify-optimization, starts brachify on a plan. `__init__.py` is empty, and
`windows - Shortcut.lnk` is a Windows shortcut committed by accident. The real work lives in
the three folders beside them: `classes/` (the next chapters), `settings/` and `windows/`.
`launch.py`'s own error handling does not work: if the app cannot start, it ends with a second,
more confusing error.

[`src/`](../../src/) holds three files and three folders:

| Item | Size | What it is |
|---|---|---|
| [`launch.py`](../../src/launch.py) | 55 lines | **the file you run** to start brachify |
| [`__init__.py`](../../src/__init__.py) | 0 bytes | empty: marks the folder as a Python package |
| `windows - Shortcut.lnk` | 1,565 bytes | a Windows shortcut file, committed by accident. Nothing uses it |
| [`classes/`](../../src/classes/) | folder | the app object, the log, signals, DICOM reading, 3D shapes, the PDF: chapters [9](#9-classes) to [12](#12-classespdf) |
| [`settings/`](../../src/settings/) | folder | the 19 `CONFIG_*` settings: their defaults, loading and saving. Not covered in this document yet |
| [`windows/`](../../src/windows/) | folder | the window, the five tabs, the 3D view and the models behind them. Not covered in this document yet |

```
 src/
 ├── launch.py              ← python src/launch.py starts everything from here
 ├── __init__.py            (empty)
 ├── windows - Shortcut.lnk (an accidental Windows shortcut)
 │
 ├── classes/               the foundations and the domain code       chapters 9 to 12
 │   ├── app.py, info.py, logger.py, signals.py, __init__.py           chapter 9
 │   ├── dicom/             reading the plan files                     chapter 10
 │   ├── mesh/              building the 3D shapes                     chapter 11
 │   └── pdf/               writing the reference sheet                chapter 12
 ├── settings/              the CONFIG_* settings
 └── windows/               the window, the tabs, the 3D view, the models
```

### 8.1 Words you need

| Word | What it means here | Real example |
|---|---|---|
| **run a file** | ask Python to carry out a file's code from top to bottom | `python src/launch.py` |
| **command line** | the words you type to start a program | `python src/launch.py "SI_C_D30 Brachify_Ex2"` |
| **argument** | one extra word on the command line, after the file's name. Python lists them in `sys.argv` | `SI_C_D30 Brachify_Ex2` |
| **the window** | brachify's main window, with its five tabs and the 3D view | — |
| **event loop** | Qt's waiting loop: once the window is up, Qt waits for clicks and key presses and runs the matching code, until the window closes | `app.exec()` |
| **exit code** | the number a program hands back when it ends. 0 means it ended normally | `sys.exit(app.exec())` |
| **`.exe`** | the Windows program built from this code by a tool called PyInstaller, so clinicians can run brachify without Python | `dist/brachify/brachify.exe` |
| **splash screen** | a picture shown while a program loads. Only the `.exe` has one | `brachify_splash.png` |
| **log** | the running record of what the app did, in `~/brachify/app.log` ([9.5](#95-loggerpy-the-log)) | `INFO app: Starting brachify` |

### 8.2 `launch.py`, starting the app

#### What happens, in order

```
 python src/launch.py  [folder]
   │
   ├─ 1   import the log ─────────────────────── ~/brachify/app.log is ready      (chapter 9)
   ├─ 2   log "Loaded modules from: …/src/classes"
   ├─ 3   import RadiotherapyApp
   ├─ 4   keep only the file's own name for Qt;
   │      print "len of sys.argv = " and how many words were given
   ├─ 5   remember the folder, if one was given
   ├─ 6   create the application object ───────── RadiotherapyApp(argv)           (9.7)
   ├─ 7   tell Qt the app's name and version ──── "brachify", "alpha"
   ├─ 8   app.gui(): build the window ─────────── fails? → stop here, silently    (9.7)
   │         │ worked
   ├─ 9   close the splash screen ─────────────── only in the .exe
   ├─ 10  if a folder was given: open the import dialog at that folder
   └─ 11  app.exec(): Qt's event loop ──────────── until the window closes, then end
```

#### Each step, with the line it comes from

| Step | Line(s) | Code | What it does |
|---|---|---|---|
| 1 | 6 | `from classes.logger import log` | importing the log sets it up: it creates `~/brachify/` and opens `app.log` ([9.5](#95-loggerpy-the-log)) |
| 2 | 17 | `log.info(f"Loaded modules from: {info.DIR_PATH}")` | the first line of every log. It prints `src/classes`, not `src` ([9.4](#94-infopy-names-and-folders)) |
| 3 | 19 | `from classes.app import RadiotherapyApp` | loads the application class. This import sits inside the function, after the log line, probably so that the log is written before the slow imports start. *Reasoned from code*: no comment says why |
| 4 | 21–22 | `argv = [sys.argv[0]]`, then a `print` | gives Qt **only** the file's own name, so Qt does not try to read the folder as one of its own options. The `print` is a leftover debugging line |
| 5 | 24–26 | `filepath_to_open_to = str(sys.argv[1])` | if a second word was given, keeps it as a folder to open |
| 6 | 28–33 | `app = RadiotherapyApp(argv)` | creates the one application object ([9.7](#97-apppy-the-application-object)). The `except` around it is broken: see [8.3](#83-when-starting-fails) |
| 7 | 35–36 | `app.setApplicationName(...)`, `setApplicationVersion(...)` | tells Qt the name `brachify` and the version `alpha` |
| 8 | 39 | `if app.gui():` | builds the window, the models and the tabs. It answers `True` if that worked, `False` if not |
| 9 | 42–47 | `import pyi_splash`, `pyi_splash.close()` | `pyi_splash` exists only inside the `.exe`. Run from Python, the import fails, and `except: pass` ignores it |
| 10 | 49–50 | `views[0].action_import_dicom_folder(filepath_to_open_to)` | opens the import dialog at the given folder ([8.4](#84-starting-with-a-folder)). `views[0]` is the Import tab |
| 11 | 51 | `sys.exit(app.exec())` | starts Qt's event loop. The program waits here the whole time the window is open, and ends with Qt's exit code when it closes |
| — | 54–55 | `if __name__ == "__main__": main()` | runs `main()` only when this file is run directly, not when another file imports it |

Three lines do nothing useful: the `QApplication` import on line 1, which is never used; the
module-level `app = None` with `global app`, which nothing else reads, since every file uses
`get_app()` instead ([9.7](#97-apppy-the-application-object)); and the two `TODO` comments on
lines 14–15.

#### What a real start looks like

*Verified*, from `~/brachify/app.log` after a real start of the app on macOS on 2026-09-21, the
first start in a new conda environment:

```
11:31:25 INFO launch: Loaded modules from: …/src/classes        ← step 2
11:31:25 INFO app: Starting brachify                             ← step 6
11:32:20 INFO main_window: Starting main window initialization  ← step 8, 55 seconds later
11:32:23 INFO main_window: main window initialization complete
```

**The 55-second gap is normal on a first start.** Step 8 imports the 3D engine, OpenCASCADE, for
the first time, and Python prepares its large library files. Later starts are much faster. Do not
stop the app during that gap: it is working, not stuck.

*Verified* as well: started on its own, `launch.py` prints `len of sys.argv =  1` to the
terminal; started with a folder, it prints `len of sys.argv =  2`.

### 8.3 When starting fails

`launch.py` has two places where starting can fail, and neither tells you on screen.

```
 step 6: RadiotherapyApp(argv) fails
   └─ except: log "Radiotherapy App failed to load!"
            input("Press enter key to continue...")    ← waits for Enter in a terminal
   └─ carries on to step 7 with app still empty
            app.setApplicationName(...)                ← crashes: app is None

 step 8: app.gui() fails
   └─ app.py logs "Main window start failed: …" and returns False
   └─ the if-block is skipped, main() ends: no window, no message, only the log line
```

- **If step 6 fails**, the error handling makes things worse. `input(...)` waits for someone to
  press Enter in a terminal, but the `.exe` has no terminal, so `input` itself fails there. Even
  from a terminal, the code then carries on to step 7 with no application object and crashes
  with a second, confusing error: `'NoneType' object has no attribute 'setApplicationName'`.
  *Reasoned from code.*
- **If step 8 fails**, the app simply ends. The only trace is one line in `app.log`, with the
  error's message but not where it happened ([9.7](#97-apppy-the-application-object)).
  *Reasoned from code.*

**Running without a screen crashes at the 3D view.** *Verified*: started with Qt's offscreen
mode, the way an automated test would start it, `launch.py` gets as far as "Starting main window
initialization" and then the process is killed (exit code −11) while setting up the 3D view,
because OpenCASCADE needs a real display. So an automated test without a screen cannot start the full app: it has to test the code's
parts instead.

### 8.4 Starting with a folder

`launch.py` can be given a folder: `python src/launch.py "SI_C_D30 Brachify_Ex2"`. The comment
on line 25 says this is for **brachify-optimization**, a separate tool that starts brachify on a
plan.

```
 python src/launch.py "SI_C_D30 Brachify_Ex2"
        │
        ▼
 sys.argv = ["src/launch.py", "SI_C_D30 Brachify_Ex2"]
        │            └─ kept as filepath_to_open_to          (step 5)
        └─ only this is given to Qt                           (step 4)
        │
        ▼  after the window is built                          (step 10)
 the Import tab's action_import_dicom_folder("SI_C_D30 Brachify_Ex2")
        │
        ▼
 the folder-picker dialog opens, already showing that folder
        ├─ you choose the folder → the plan is imported, as if you had clicked Import Dicom
        └─ you cancel            → nothing is imported
```

**It does not import the plan by itself.** It opens the same folder picker that the *Import
Dicom* button opens, already showing the given folder, and you still have to choose it. The
commit that added this, `3013845` (2024-10-04), says so: "Open file dialog box immediately on
launch if run brachify from cmd with filepath given". *Reasoned from code and the commit message*;
not run with a screen. The source of truth (§1.4) and AGENTS.md described it as "auto-triggers a
DICOM import", which is not what the code does. Both were corrected on 2026-10-02.

### 8.5 `__init__.py`, an empty file

[`src/__init__.py`](../../src/__init__.py) is 0 bytes. A file with this name marks its folder as
a Python **package**. This one has no effect on running the app: the code's imports start at
`classes`, `settings` and `windows`, not at `src`, because Python puts the folder of the file you
run, `src/`, on the list of places it looks for modules. It does let tools that start from the
repository's top folder treat `src` as a package. It was added in commit `482678d` (2023-11-02).

### 8.6 `windows - Shortcut.lnk`, an accidental file

A `.lnk` file is a Windows shortcut: a small file that points at another folder or file, like an
alias on a Mac. This one points at `C:\Users\<someone>\Documents\Python\brachify\src\windows`, a
folder on a former developer's own computer, so it cannot work anywhere else. It was added in
commit `0711485` (2024-05-10), whose message is about adding keyboard shortcuts to the app, so it
was most likely committed by accident with that work. Nothing uses it. §7.4 of the source of
truth lists it as committed by accident.

### 8.7 What happens if something here changes

| Change | What happens | How sure |
|---|---|---|
| run from the repository's top folder | the normal way. The window's icon is looked up relative to this folder | *Reasoned from code* |
| run from inside `src/` | the app starts, but files looked up relative to the starting folder, like the window icon, are not found | *Reasoned from code* |
| the very first start in a new environment | about a minute of silence before the window appears | *Verified*: 55 seconds in the log above |
| start with a folder | the import dialog opens at that folder. You still choose it | *Reasoned from code* |
| start with no screen (offscreen) | the process is killed at the 3D view, exit code −11 | *Verified* |
| `app.gui()` fails | the app ends with no window and no message. Only `app.log` says why | *Reasoned from code* |
| `RadiotherapyApp(argv)` fails | a second error hides the first, and in the `.exe` the `input()` call fails too | *Reasoned from code* |
| the `print` on line 22 removed | nothing changes for the app. It only stops a debugging line in the terminal | *Reasoned from code* |

**A harmless warning you will see every start.** *Verified*: the terminal shows
`QCssParser::parseColorValue: Specified color with alpha value but no alpha given: 'rgba 240, 245, 250'`
several times. The window's design file, `windows/ui/main_window.ui`, sets six colours as
`rgba(240, 245, 250)`. `rgba` expects four numbers, red, green, blue and transparency, and these
give three, so Qt complains and carries on.

### 8.8 Things nothing checks

- **That the app actually started.** If building the window fails, `launch.py` ends quietly.
- **That the failure path works.** The `except` around step 6 leads straight into a second crash.
- **That the given folder exists.** It is handed to the folder picker as-is.
- **That nobody commits personal files.** The `.lnk` shortcut has been in the repository since
  2024.

---

## 9. classes/

**Summary.** The five files sitting directly in `src/classes/`, outside its subfolders, are the
app's foundations. `app.py` defines the one **application object**, which every other part of
the code reaches through a single function, `get_app()`. That object carries the app's
settings, its three app-wide **signals**, and, once the window is built, the window itself.
`signals.py` declares those signals: the announcements one part of the app makes so that other
parts can react, such as "switch to page 2" or "the cylinder got 20 mm shorter". `logger.py`
sets up the one **log** everything writes to, which goes both to the terminal and to the file
`~/brachify/app.log`, and creates that folder the moment it is first imported. `info.py` holds
the app's name, version and folder locations, and `__init__.py` is empty. None of these files
knows anything about DICOM, geometry or PDFs; the chapters after this one build on them.

[`src/classes/`](../../src/classes/) has five Python files of its own:

| File | Size | Job |
|---|---|---|
| [`__init__.py`](../../src/classes/__init__.py) | 0 bytes | empty: marks the folder as a Python package |
| [`info.py`](../../src/classes/info.py) | 16 lines | the app's name, version and folder locations |
| [`logger.py`](../../src/classes/logger.py) | 41 lines | sets up the one log the whole app writes to |
| [`signals.py`](../../src/classes/signals.py) | 12 lines | `AppSignals`: the three app-wide announcements |
| [`app.py`](../../src/classes/app.py) | 73 lines | `RadiotherapyApp`, the application object, and `get_app()` |

The folder also holds the three subfolders explained in the next chapters:
[classes/dicom](#10-classesdicom), [classes/mesh](#11-classesmesh) and [classes/pdf](#12-classespdf).

```
 src/launch.py                     the file you run: python src/launch.py
   │
   ├── imports logger.py ────────▶ creates ~/brachify/ and opens ~/brachify/app.log
   │      └── uses info.py         for the folder's location
   │
   └── creates RadiotherapyApp     (app.py)
          ├── AppSignals()         (signals.py)       the three signals
          ├── Values()             (settings/)        loads the settings
          └── gui()                builds the window, the models and the five tabs

 every other file:   get_app()  →  the same RadiotherapyApp
                     log        →  the same logger
```

### 9.1 Words you need

| Word | What it means here | Real example |
|---|---|---|
| **module** | one Python file, as seen by code that uses it | `classes.logger` is the file `src/classes/logger.py` |
| **package** | a folder of modules | `classes` |
| **import** | load a module and use something defined in it. A module's code runs **once**, the first time it is imported; later imports reuse it | `from classes.logger import log` |
| **class** | a description of a kind of object: what it holds and what it can do | `RadiotherapyApp` |
| **object** | one thing made from a class | the app object |
| **constructor** | the function a class runs when an object is made, written `__init__` in Python | `RadiotherapyApp.__init__` |
| **attribute** | a value stored on an object, reached with a dot | `app.values`, `app.window` |
| **method** | a function that belongs to an object | `app.gui()` |
| **inherit** | build a class on top of another one, so it gets everything the other has | `RadiotherapyApp` inherits from Qt's `QApplication` |
| **Qt** (and **PySide6**) | the library that draws the window, buttons and tabs. PySide6 is how Python talks to it | `QApplication` |
| **signal** | a named announcement an object can make. Other code **connects** a function to it, and every connected function runs each time it is **emitted** | `height_changed` |
| **log** | a running record of what the app did, one line per event | `~/brachify/app.log` |
| **log level** | how important a log line is: DEBUG, INFO, WARNING, ERROR or CRITICAL, from least to most | `INFO app: Starting brachify` |
| **`~`** | your home folder | `~/brachify` is `/Users/you/brachify` on a Mac |

### 9.2 What happens when the app starts

The five files do their work in this order when you run `python src/launch.py`. *Verified*:
steps 1 to 4 were run with `HOME` pointed at an empty scratch folder, and the results are shown.

```
 1  launch.py imports logger.py
      └─ logger.py runs, once:
           creates ~/brachify/                         (if it does not exist)
           opens  ~/brachify/app.log                   (adds to it, never wipes it)
           sets up two outputs: the file and the terminal

 2  launch.py creates RadiotherapyApp(argv)            (app.py, __init__)
      ├─ Qt's own setup runs first                     (super().__init__)
      ├─ self._signals = AppSignals()                  (signals.py)
      ├─ logs "INFO app: Starting brachify"
      └─ self.values = Values()                        (settings/)
           reads ~/brachify/filepaths.json to find the last settings file,
           or uses the built-in defaults

 3  launch.py calls app.gui()                          (app.py)
      ├─ self.window = MainWindow()                    the window
      ├─ self.window.initModels()                      the models
      ├─ self.window.initViews()                       the 3D view and the five tabs
      ├─ sets the window icon
      └─ shows which settings were loaded, on the Import tab
           │
           ├─ worked  → returns True
           └─ failed  → logs "Main window start failed: …" and returns False:
                        the app closes with no window and no message on screen

 4  launch.py calls app.exec()                         Qt waits for clicks until the window closes
```

On a first start, with no `filepaths.json` yet, these are the first lines written to the log,
exactly as they appeared:

```
10:08:26 INFO app: Starting brachify
10:08:26 DEBUG values: Couldn't read from filepaths.json.
10:08:26 DEBUG load: Config filename is None. Using defaults instead.
```

### 9.3 `__init__.py`, an empty file

[`__init__.py`](../../src/classes/__init__.py) is 0 bytes. A file with this name marks its folder
as a **package**, so Python treats `classes` as a group of modules that can be imported as
`classes.app`, `classes.logger` and so on. It holds no code. Since Python 3.3 a folder imports
fine without one, which is why `classes/dicom/`, `classes/mesh/` and `classes/pdf/` have none.

Imports throughout the code start at `classes`, not at `src`: `from classes.app import get_app`.
That works because Python adds the folder of the file you run, `src/`, to the places it looks for
modules. AGENTS.md warns not to "fix" these into `src.classes…`.

### 9.4 `info.py`, names and folders

[`info.py`](../../src/classes/info.py) holds **constants**: values set once and never changed.
Their names are written in capitals by Python custom. *Verified*, by importing the file:

| Constant | Value | Means | Used by |
|---|---|---|---|
| `APP_NAME` | `brachify` | the app's name | Qt's app name, the user folder's name |
| `VERSION_MAJOR` | `0` | version, first number | **nothing** |
| `VERION_MINOR` | `3` | version, second number. The name is missing an S | **nothing** |
| `APP_VERSION` | `alpha` | the version Qt is told | Qt's app version |
| `DIR_PATH` | `<repo>/src/classes` | this file's folder | one log line, and `app.path`, which nothing reads |
| `HOME_PATH` | `~` | your home folder | `USER_PATH` |
| `USER_PATH` | `~/brachify` | the app's own folder for its log and remembered settings | `logger.py`, `settings/`, the window |
| `RESOURCES_PATH` | `<repo>/src/classes/resources` | meant to be the resources folder | **nothing** |

`<repo>` stands for wherever the repository is on your computer.

Two of these are not what their comments say:

- **`DIR_PATH` is `src/classes`, not `src`.** The comment beside it says "src folder location".
  The code takes the folder of `info.py` itself, which is `src/classes`. *Verified*: the first log
  line of every start reads "Loaded modules from: …/src/classes".
- **`RESOURCES_PATH` points at a folder that does not exist.** The real resources folder is
  `resources/` at the top of the repository. *Verified*: `src/classes/resources` does not exist.
  Nothing uses `RESOURCES_PATH`, so nothing breaks.

```
 the repository
 ├── resources/                  ← the real resources folder (the icon, the splash image)
 └── src/
     ├── launch.py
     └── classes/                ← DIR_PATH points here
         ├── info.py
         └── resources/          ← RESOURCES_PATH points here, and it does not exist

 your home folder
 └── brachify/                   ← USER_PATH
     ├── app.log                 the log, written by logger.py
     └── filepaths.json          the last settings files you used, written when the window closes
```

### 9.5 `logger.py`, the log

[`logger.py`](../../src/classes/logger.py) has no functions. It is a set-up script that runs once,
the first time anything imports it, and leaves one ready-made object behind, `log`, which every
file then imports with `from classes.logger import log`.

#### Where a log line goes

```
  any file:  log.info("Starting brachify")
                │
                ▼
          the "Brachify" logger           level DEBUG: lets every line through
                │                          propagate = False: does not pass lines up to the root
        ┌───────┴────────────────┐
        ▼                        ▼
  file output                terminal output
  ~/brachify/app.log         where you ran the app (stderr)
  10:08:26 INFO app: …       INFO app: …
  (with the time)            (without the time)

  libraries (matplotlib, pydicom, …) log to the separate "root" logger,
  which shows only ERROR and CRITICAL, so their chatter stays out of the way
```

*Verified* settings, by importing the file:

| Setting | Value | Means |
|---|---|---|
| logger name | `Brachify` | its own logger, separate from the libraries' |
| logger level | DEBUG | every line, from DEBUG up, is kept |
| `propagate` | False | lines are not passed on to the root logger, so they are not printed twice |
| outputs | a rotating file, and the terminal | both at level DEBUG |
| file size limit | 26,214,400 bytes (25 MB) | then the file is renamed and a new one started |
| old files kept | 3 | `app.log.1`, `app.log.2`, `app.log.3`. At most about 100 MB in all |
| root logger level | ERROR | libraries only show errors |

#### What a log line looks like

```
10:08:26 INFO app: Starting brachify
└──┬───┘ └┬─┘ └┬┘  └──────┬───────┘
   │      │    │          └── the message
   │      │    └── the file it came from, without .py
   │      └── the level
   └── the time: hours, minutes, seconds. No date
```

**There is no date in the log.** The file keeps growing across days and restarts, so the time
alone cannot tell you which day a line came from.

#### Rotation

```
 app.log reaches 25 MB
        │
        ▼
 app.log.2 → app.log.3   (the old app.log.3 is deleted)
 app.log.1 → app.log.2
 app.log   → app.log.1
 a new, empty app.log is started
```

### 9.6 `signals.py`, app-wide announcements

[`signals.py`](../../src/classes/signals.py) declares one class, `AppSignals`, with three signals
and nothing else. The app makes one `AppSignals` object, and every file reaches it as
`get_app().signals`.

A signal works like a doorbell. Code that cares about it **connects** a function to it. Code
that has news **emits** it, with a value. Every connected function then runs, in the order they
were connected, before `emit` returns. The code that emits does not need to know who is
listening.

| Signal | Carries | Emitted by | Connected to |
|---|---|---|---|
| `viewChanged` | a whole number: the tab to show, 0 to 4 | the five tab buttons; the Import tab after a successful import (4, the Export tab) | `NavigationModel.set_page`, which switches tabs |
| `height_changed` | a decimal: how much the cylinder's length changed, in mm | the Cylinder tab's *Apply Settings* | `ChannelsModel.update_height_offset` and `TandemModel.update_height_offset` |
| `exportFile` | text | **nothing** | **nothing** |

**One real announcement**, `height_changed`, when the cylinder goes from 160 to 140 mm:

```
 Cylinder tab: you set the length to 140 and press Apply Settings
        │
        ▼
 height_changed.emit(140 − 160)  =  emit(−20.0)
        │
        ├──▶ ChannelsModel.update_height_offset(−20.0)   every needle moves down 20 mm
        └──▶ TandemModel.update_height_offset(−20.0)     the tandem moves down 20 mm
```

*Verified*, with two test functions connected to `height_changed`: one `emit(−20.0)` called both,
in the order they were connected, each receiving −20.0. Emitting `exportFile`, which nothing is
connected to, does nothing and raises no error.

Why the change is sent as a difference (−20) and not as the new length (140) is explained in
[10.7](#107-what-the-rest-of-the-app-does-with-the-form): the needles' points are never changed
after import, so each needle only needs to know how far to shift.

### 9.7 `app.py`, the application object

[`app.py`](../../src/classes/app.py) defines two things: a function, `get_app()`, and a class,
`RadiotherapyApp`.

#### `get_app()`

```python
def get_app():
    return QApplication.instance()
```

Qt allows only **one** application object per program, and keeps track of it. `get_app()` asks
Qt for it. So any file, anywhere, can write `get_app().values` or `get_app().window` without
anything being handed to it. It works like a shared global variable.

*Verified*:

| Situation | What `get_app()` gives |
|---|---|
| before the app object is made | `None`: nothing |
| after `RadiotherapyApp(...)` | that same object, of type `RadiotherapyApp` |
| trying to make a second `RadiotherapyApp` | **refused**, with a `RuntimeError` |

It is the most used function in the code: **96 calls** across `src/`. The cost is that every one
of those 96 places depends on the whole running app, so none of them can be tested without
building one. AGENTS.md asks for logic to be moved out into plain functions for that reason.

#### `RadiotherapyApp`, what it holds

`RadiotherapyApp` **inherits** from Qt's `QApplication`: it is a Qt application, with a few
attributes added. *Verified*, by making one:

| Attribute | Holds | Set in | Read by |
|---|---|---|---|
| `signals` | the one `AppSignals` | `__init__` | everything that emits or connects. It is **read-only**: `app.signals = …` raises an error |
| `values` | the settings: a `Values` object holding `config_values`, all 19 `CONFIG_*` settings | `__init__` | almost everything |
| `window` | the main window | `gui()` | almost everything. It does not exist until `gui()` runs |
| `args` | Qt's copy of the command-line words | `__init__` | **nothing** |
| `errors` | an empty list | `__init__` | **nothing** |
| `path` | `DIR_PATH`, which is `src/classes` | `__init__` | **nothing** |

#### `__init__`: what happens when the object is made

| Order | Line | What it does |
|---|---|---|
| 1 | `super().__init__(*args, **kwargs)` | runs Qt's own set-up first. Without it, no window could ever be made |
| 2 | `self.args = super().arguments()` | keeps Qt's copy of the command line |
| 3 | `self.errors = []` | an empty list, never used |
| 4 | `self._signals = AppSignals()` | makes the three signals |
| 5 | `from classes.logger import log` and `log.info(…)` | writes "Starting brachify" to the log |
| 6 | `self.path = DIR_PATH` | never used |
| 7 | `self.values = Values()` | loads the settings |

#### `gui()`: building the window

| Order | What it does |
|---|---|
| 1 | `from windows.main_window import MainWindow`. This import is inside the method on purpose: `main_window.py` itself imports `get_app` from `app.py`, so importing it at the top of `app.py` would make each file wait for the other |
| 2 | `self.window = MainWindow()`. Only after this line does `app.window` exist |
| 3 | `self.window.initModels()`, then `self.window.initViews()`. They are separate steps because the models and tabs reach the window through `get_app().window`, which only exists once step 2 has finished |
| 4 | sets the window's icon from `"resources\\brachify_splash-ico.ico"`. That path is written the Windows way and is relative to the folder you started from, so on macOS no icon is found and the window just has none |
| 5 | builds the "which settings were loaded" message and shows it on the Import tab |
| 6 | returns `True`. If anything in steps 1 to 5 failed, it logs `Main window start failed: …` and returns `False` instead |

```
 RadiotherapyApp(argv)          get_app() now works; app.signals and app.values exist
        │
        ▼
 app.gui()
        │   self.window = MainWindow()     ← app.window exists from here
        │   initModels()                   ← models can now use get_app().window
        │   initViews()                    ← tabs can now use the models
        ▼
   True  → launch.py starts Qt's event loop
   False → launch.py stops: no window, no message, only a line in app.log
```

### 9.8 What happens if something here changes

| Change | What happens | How sure |
|---|---|---|
| delete `~/brachify/` | made again, with a new empty `app.log`, the next time the app starts. The remembered settings files are forgotten | *Verified*: the folder appears the moment `logger.py` is imported |
| no `filepaths.json` | the built-in default settings are used, and the log says "Couldn't read from filepaths.json" and "Using defaults instead" | *Verified* |
| anything in `gui()` fails | the app closes with no window and no message on screen. Only `app.log` says why, and only the error's message, not where it happened | *Reasoned from code* |
| `APP_NAME` changed | `USER_PATH` changes with it, so the app looks in a different folder and finds no old log or settings | *Reasoned from code* |
| the `super().__init__` line removed | Qt is never set up, so the window can never be made | *Reasoned from code* |
| a second `RadiotherapyApp` made | refused with a `RuntimeError` | *Verified* |
| something assigns `app.signals = …` | refused with an `AttributeError`: it is read-only | *Verified* |
| a signal emitted that nothing is connected to | nothing happens, and no error | *Verified* |

### 9.9 Things nothing checks

- **That the comments match the code.** `DIR_PATH` is commented "src folder location" and is
  `src/classes`.
- **Values nobody uses.** `VERSION_MAJOR`, `VERION_MINOR`, `RESOURCES_PATH`, `app.args`,
  `app.errors`, `app.path` and the `exportFile` signal are all set and never read.
- **The date in the log.** Log lines carry only the time.
- **Where a start-up failure happened.** `gui()` logs the error's message but not the list of
  files and lines that led to it, so the log does not say where it failed. Changing that line to
  `log.exception(…)` while debugging records the full trace.
- **Whether the icon was found.** On macOS and Linux the icon path never matches, silently.
- **What goes into the log.** The patient's name is written to `app.log` in plain text on every
  import ([10.4](#104-datapy-the-form-brachify-fills-in)).

---

## 10. classes/dicom

**Summary.** `classes/dicom/` is brachify's front door. A treatment planning program exports a
plan as two DICOM files: a **plan** file that lists the channels (needles, the Central Axis, the
tandem) by name and number, and a **structures** file that holds each channel's path as a list of
3D points. `fileio.py` finds those two files in a folder, joins them using a shared ID number
called the ROI number, finds the channel named `Central Axis`, and uses it to turn and slide every
needle's points into the cylinder's own frame: base at (0, 0, 0), standing straight up, top at
z = 160 mm. The result goes into one container, `DicomData` from `data.py`, and the rest of the
app never reads a DICOM file again. Almost nothing here is checked: only a missing Central Axis
produces a warning, and every other mistake in the files quietly produces a different cylinder.

[`src/classes/dicom/`](../../src/classes/dicom/) has two files:

| File | Size | Job |
|---|---|---|
| [`data.py`](../../src/classes/dicom/data.py) | 101 lines, 1 class | `DicomData`, the empty form that holds what was read |
| [`fileio.py`](../../src/classes/dicom/fileio.py) | 584 lines, 13 functions | the readers that open the files and fill the form in |

```
 a folder of DICOM files
        │
        ▼
 fileio.read_dicom_folder()          finds the plan file and the structures file
        │
        ▼
 load_varian_dicom_data()            or load_nucletron_dicom_data() for Oncentra files
   ├─ reads names and numbers from the plan file
   ├─ finds the "Central Axis"
   ├─ reads every needle's points from the structures file
   └─ moves every point into the cylinder's frame
        │
        ▼
 one DicomData                       (data.py)
        │
        ▼
 the Import tab hands it to the rest of the app   (section 10.7)
```

### 10.1 The real-world story

1. A patient has a plastic **cylinder** placed where the treatment will happen. In the sample
   files the "patient" is a test object.
2. A medical physicist opens a **treatment planning program** on a computer. Varian's is called
   BrachyVision, Elekta's is called Oncentra. In it they draw:
   - a straight line down the middle of the cylinder, named **`Central Axis`**,
   - a line for each **needle**: where it runs through the cylinder, how it bends, and where its
     tip ends up in the body,
   - sometimes a line for the **tandem**, a rod that goes up the middle and bends to one side.
3. They **export** the plan. The program writes it to files in a medical file format called
   **DICOM**.
4. Brachify opens those files and builds a printable cylinder with a hole along each needle line.

`classes/dicom/` is the first half of step 4: reading the files.

### 10.2 Words you need

| Word | What it means here | Real example |
|---|---|---|
| **DICOM file** | a file made of many small labelled entries, one after another | `RP.1.2.246…dcm` |
| **field** | one labelled entry in a DICOM file: a name and a value | name `PatientID`, value `SI_C_D30` |
| **tag** | the number DICOM uses to identify a field. Every kind of field has a fixed tag | `PatientID` is always tag `(0010,0020)` |
| **list field** | a field whose value is a **list of items** instead of one value. DICOM calls it a *sequence* | the list of channels |
| **item** | one entry in a list field. Each item holds its own small set of fields | one channel |
| **RP file** | the **plan** file (DICOM type RTPLAN). It says which channels exist and what each is called | `RP…dcm` |
| **RS file** | the **structures** file (DICOM type RTSTRUCT). It holds the drawn shapes: their numbers, names and 3D points | `RS…dcm` |
| **channel** | one tube the radioactive source can travel through: a needle, the Central Axis, or the tandem. Each is one item in the RP file's channel list | `Applicator2` |
| **applicator** | the planning program's word for any device the source travels through. In the sample plans every needle is named `Applicator` plus a number | `Applicator2` to `Applicator13` |
| **Applicator2** | the needle used as the example throughout this document: the plan's channel number 2, which is the first needle in the list, because channel number 1 is the Central Axis | — |
| **shape** (DICOM calls it an **ROI**, "Region Of Interest") | one drawn object in the RS file, with a number, a name and points | shape number 34 |
| **ROI number** | a shape's ID number. The RP file uses it to say "this channel follows shape number N" | `34` |
| **point** | a position in 3D space: three numbers x, y and z, in millimetres | `(1.51, 59.14, 81.1)` |
| **contour** | the list of points that makes up a shape. For a needle, the points run along it starting **from its tip** | 13 points for Applicator2 |
| **label** | the channel's name as the planner typed it | `Applicator2`, `Central Axis`, `Tandem` |
| **Ex1, Ex2** | short names used in this file for the sample folders [`SI_C_D30 Brachify_Ex1/`](../../SI_C_D30%20Brachify_Ex1/) and [`SI_C_D30 Brachify_Ex2/`](../../SI_C_D30%20Brachify_Ex2/) | — |

### 10.3 What is inside the sample files

Each sample folder holds three files. Using Ex2:

| File | Type | What is in it | Does brachify read it? |
|---|---|---|---|
| `RP…dcm` | plan | the list of 14 channels, and patient information | **yes** |
| `RS…dcm` | structures | 42 drawn shapes with their points | **yes** |
| `RD…dcm` | dose | a 3D grid of radiation doses | **no**, never opened |

The two folders share the same RS file. The only field that differs between the two copies is
the time it was saved (`InstanceCreationTime`, 09:28:37 against 09:36:48). Ex1's plan has 13
channels and Ex2's has 14: the same 13 plus `Tandem`. *Verified*, by reading every field of
both files.

The "patient" in both is a test object, not a person, so its fields hold descriptive values:

| Field | Value | Note |
|---|---|---|
| `PatientName` | `CYLINDER^D30` | DICOM names are written `Family^Given`, so the family name is `CYLINDER` |
| `PatientID` | `SI_C_D30` | also the first half of each folder's name |
| `RTPlanLabel` | `Brachify_Ex1`, `Brachify_Ex2` | the second half of each folder's name |
| `OperatorsName` | `Michael Kudla` | |
| `ApprovalStatus` | `UNAPPROVED` | |

#### 10.3.1 The RP file, and what "the RP's channels" means

Inside the RP file is a list field called `ApplicationSetupSequence`. Its first item holds
another list field called `ChannelSequence`. **That inner list is "the RP's channels"**: one
item per channel.

```
RP file
 ├─ PatientName      = "CYLINDER^D30"
 ├─ PatientID        = "SI_C_D30"
 ├─ RTPlanLabel      = "Brachify_Ex2"
 ├─ Manufacturer     = "Varian Medical Systems"
 └─ ApplicationSetupSequence           (a list with 1 item)
      └─ item 0
           └─ ChannelSequence          (a list with 14 items: "the RP's channels")
                ├─ item 0  → channel "Central Axis"
                ├─ item 1  → channel "Applicator2"
                ├─ …
                └─ item 13 → channel "Tandem"
```

Each item holds about 14 fields. This is item 1, Applicator2, exactly as stored:

```
ReferencedROINumber         '34'            ← "my shape is number 34 in the RS file"
ChannelNumber               '2'             ← its number in the plan
SourceApplicatorID          'Applicator2'   ← its label
ChannelLength               '1300'          ← millimetres of tubing to the treatment machine
ChannelTotalTime            '0'             ← seconds of radiation in this needle
SourceApplicatorStepSize    '3'             ← millimetres between possible source stops
BrachyControlPointSequence  (40 items)      ← every planned stop of the source
… and a few more
```

**Brachify reads only three of these fields from each channel:**

| Field | Brachify calls it | Means |
|---|---|---|
| `ReferencedROINumber` | ROI number | which RS shape holds this channel's points |
| `ChannelNumber` | channel number | the number printed on the PDF reference sheet |
| `SourceApplicatorID` | label | the name shown in the app |

All 14 channels in Ex2's RP file, with those three fields:

| Item | Label | Channel number | ROI number |
|---|---|---|---|
| 0 | Central Axis | 1 | 33 |
| 1 | Applicator2 | 2 | 34 |
| 2 | Applicator3 | 3 | 35 |
| 3 | Applicator4 | 4 | 36 |
| 4 | Applicator5 | 5 | 37 |
| 5 | Applicator6 | 6 | 38 |
| 6 | Applicator7 | 7 | **43** |
| 7 | Applicator8 | 8 | **44** |
| 8 | Applicator9 | 9 | **45** |
| 9 | Applicator10 | 10 | **39** |
| 10 | Applicator11 | 11 | **40** |
| 11 | Applicator12 | 12 | **41** |
| 12 | Applicator13 | 13 | **42** |
| 13 | Tandem | 14 | 46 |

The ROI numbers in bold are **out of order**: Applicator7 uses shape 43, but Applicator10 uses
shape 39. This matters in [step 6b](#step-6b-each-needles-points).

Both samples also give the `Central Axis` channel **222.8 seconds** of radiation
(`ChannelTotalTime`) and every needle 0 seconds. The User Manual says the Central Axis should
have none. Brachify never reads this field, so nothing notices. *Verified*, from the files.

#### 10.3.2 The RS file

The RS file has a few single fields at the top, then **three list fields with one item per
shape**. Each list holds a different part of a shape's information. An item in one list is
matched to the items in the others by the shape's **ROI number**, not by its position.

```
RS file
 ├─ Modality           = "RTSTRUCT"
 ├─ PatientName        = "CYLINDER^D30"
 ├─ PatientID          = "SI_C_D30"
 ├─ Manufacturer       = "Varian Medical Systems"
 ├─ StructureSetLabel  = "CT_1"
 ├─ ReferencedFrameOfReferenceSequence   (1 item: which scan these coordinates belong to)
 │
 ├─ StructureSetROISequence              (42 items: each shape's NUMBER and NAME)
 │    ├─ item 0   → ROI 1   "BODY"
 │    ├─ item 1   → ROI 2   "Surface3"
 │    ├─ item 2   → ROI 4   "SI Seg Cyl"
 │    ├─ …
 │    ├─ item 29  → ROI 34  "Applicator26"      ← the shape Applicator2 uses
 │    ├─ …
 │    └─ item 41  → ROI 46  "Central Axis1"     ← the shape the plan's "Tandem" uses
 │
 ├─ ROIContourSequence                   (42 items: each shape's POINTS)
 │    ├─ …
 │    └─ item 29  → ROI 34  → 1 contour of 13 points
 │
 └─ RTROIObservationsSequence            (42 items: what KIND of thing each shape is)
      ├─ …
      └─ item 29  → ROI 34  → "BRACHY_CHANNEL"
```

These are the three items for shape 34, exactly as stored:

```
StructureSetROISequence, item 29
  ROINumber                       '34'
  ROIName                         'Applicator26'      ← the RS file's own name for it
  ReferencedFrameOfReferenceUID   '1.2.840.113619…'   ← which scan's coordinates

ROIContourSequence, item 29
  ReferencedROINumber             '34'                ← "these points belong to shape 34"
  ROIDisplayColor                 [0, 255, 0]         ← drawn in green in the planning program
  ContourSequence                 (1 item)
    ContourGeometricType          'OPEN_NONPLANAR'    ← a line through 3D space, not a closed outline
    NumberOfContourPoints         '13'
    ContourData                   39 numbers          ← the points themselves

RTROIObservationsSequence, item 29
  ReferencedROINumber             '34'
  RTROIInterpretedType            'BRACHY_CHANNEL'    ← "this shape is a source channel"
```

**What brachify reads from the RS file:**

| List | Field | Read when |
|---|---|---|
| `ROIContourSequence` | `ReferencedROINumber`, `ContourData` | **always**: these give every needle's points, and the Central Axis's |
| `RTROIObservationsSequence` | `ROIObservationLabel` | only in the backup plan when there is no Central Axis ([step 4](#step-4-find-the-central-axis-and-take-it-out-of-the-lists)) |
| `StructureSetROISequence` | — | **never**, for Varian files. Oncentra keeps a copy of this list inside its RP file and does read the names from it ([10.6](#106-elekta-oncentra-files)) |

Ex2's RS file holds **42 shapes**:

| Kind | How many | Examples |
|---|---|---|
| needle-type lines | 39 | shape 34 named `Applicator26`, shape 33 named `Central Axis` |
| body outline | 1 | `BODY` |
| marker | 1 | `Surface3` |
| other line | 1 | `SI Seg Cyl` |

The Ex2 plan uses 14 of the 39 needle-type lines, and Ex1's uses 13. The rest are leftover
drafts, and brachify ignores them.

**The names in the RS file do not match the plan's labels.** In the RS file, shape 34 is named
`Applicator26`, but the plan calls the channel that uses it `Applicator2`. In Ex1, the plan's
`Central Axis` uses shape 20, which the RS file names `Applicator 1`. **For Varian files,
brachify uses the plan's labels**, so the RS names never matter.

Shape 34's points, which Applicator2 uses, exactly as stored: a single piece of text with the
numbers separated by `\`.

```
1.51\59.14\81.1\1.52\72.76\60.09\1.52\73.42\58.92\ … (39 numbers in total)
```

Those 39 numbers are **13 points of 3 numbers each**, in the order x, y, z, x, y, z, and so on:

```
point 1  = (1.51, 59.14, 81.1)    ← the needle's tip
point 2  = (1.52, 72.76, 60.09)
…
point 13 = (1.59, 78.29, 17.82)   ← the end furthest from the tip
```

All 13 are listed in [11.6](#116-channelpy-one-tube-per-needle), before and after brachify moves
them.

These coordinates are in the **planning computer's frame**: millimetres, measured from wherever
the scanner put its zero. x runs left to right across the patient, y front to back, and z from
feet to head. In that frame the cylinder is tilted and not centred, so the numbers are not yet
useful for building anything.

#### 10.3.3 How the two files connect

The **ROI number** is the only link between the two files:

```
RP channel item 1                              RS shape list
  SourceApplicatorID  "Applicator2"
  ReferencedROINumber  34  ─────────────▶   shape number 34
                                             points: 1.51\59.14\81.1\ …  (13 points)
```

"Applicator2's shape" means: read its ROI number (34), then find shape 34 in the RS file.
**Brachify trusts that link completely.** If the plan said 39 instead of 34, Applicator2 would
silently take shape 39's points (see [10.8](#108-what-happens-if-a-value-in-the-file-changes)).

### 10.4 data.py, the form brachify fills in

[`data.py`](../../src/classes/dicom/data.py) defines one thing, **`DicomData`**: a container
with 21 named slots. Think of it as a paper form with blank boxes. Every box starts empty, which
Python writes as `None`. The form does no work itself. `fileio.py` fills the boxes in, and the
rest of the app reads them.

```
 DicomData
 ├─ about the patient and plan     patient_name, patient_id, plan_label, approval_status, operator
 ├─ the three channel lists        channels_labels, channel_numbers, channels_rois
 ├─ where the cylinder is          central_channel_roi, central_channel, cylinder_tip,
 │                                 cylinder_base, cylinder_direction
 ├─ the result                     channel_paths            ← every needle's points, moved
 ├─ filled in later by the app     tandem_channel
 └─ never used                     plan_ID, central_axis_flag, cylinder_diameter,
                                   channel_contours (used only inside fileio.py),
                                   cylinder_roi and cylinder_contour (backup plan only)
```

**About the patient and plan.** Each box is copied straight from one field of the RP file:

| Box | Copied from RP field | Ex2 value |
|---|---|---|
| `patient_name` | `PatientName`, the part before `^` | `CYLINDER` |
| `patient_id` | `PatientID` | `SI_C_D30` |
| `plan_label` | `RTPlanLabel` | `Brachify_Ex2` |
| `approval_status` | `ApprovalStatus` | `UNAPPROVED` |
| `operator` | `OperatorsName` | `Michael Kudla` |

**About the channels: three lists that must stay lined up.** Each list has one entry per
channel, in the same order as the RP's channel list:

| Box | Filled from | Ex2 value, after the Central Axis is removed in step 4 |
|---|---|---|
| `channels_labels` | each channel's `SourceApplicatorID` | `["Applicator2", "Applicator3", …, "Tandem"]` |
| `channel_numbers` | each channel's `ChannelNumber` | `[2, 3, …, 14]` |
| `channels_rois` | each channel's `ReferencedROINumber` | `[34, 35, 36, 37, 38, 43, 44, 45, 39, 40, 41, 42, 46]` |

```
 position:          0              1              2        …      12
 channels_labels    Applicator2    Applicator3    Applicator4  …  Tandem
 channel_numbers    2              3              4         …     14
 channels_rois      34             35             36        …     46
                    └────── one needle ──────┘
```

**Entry 0 of every list is the same needle, and so is entry 1, and so on.** Nothing else ties
them together. If one list lost an entry, every needle after that point would get the wrong
name and number. Lists that rely on matching positions like this are called *parallel lists*.

**About where the cylinder is:**

| Box | Means | Ex2 value |
|---|---|---|
| `central_channel_roi` | the shape number of the `Central Axis` | `33` |
| `central_channel` | that shape's points | `(1.32, 82.59, 75.21)` and `(1.32, 90.33, −121.44)` |
| `cylinder_tip` | the axis's **first** point: the top of the cylinder | `(1.32, 82.59, 75.21)` |
| `cylinder_base` | the axis's **last** point: its bottom end | `(1.32, 90.33, −121.44)` |
| `cylinder_direction` | an arrow from base to tip, worked out as tip minus base | `(0, −7.74, 196.65)` |

**The result:**

| Box | Means | Ex2 example |
|---|---|---|
| `channel_paths` | every needle's points, **moved into the cylinder's own frame** ([step 7](#step-7-move-everything-into-the-cylinders-frame)) | Applicator2's tip `(0.19, −23.20, 166.81)` |

**Filled in later, by another part of the app:** `tandem_channel`, the label of the channel
chosen as the tandem (`"Tandem"` in Ex2). `ChannelsModel` writes it during import, when a label
contains the word "tandem", and again when you press *Set as Tandem*. It is the only box changed
after the import.

**Boxes nothing uses:** `plan_ID` and `central_axis_flag`, which are never filled in, and
`cylinder_diameter`, which is filled in and never read. The cylinder's diameter comes from the
app's settings, not from the DICOM files.

`DicomData` also has two small methods:

- **`reset()`** empties every box. Every import builds a **new** `DicomData`, so `reset()` only
  matters when an import fails partway: then the old form stays in place, and `reset()` is what
  wipes the previous patient's values. A box missing from `reset()` survives only a failed
  import. *Reasoned from code.* `central_axis_flag` is the one box it misses.
- **`toString()`** builds a summary that is written to the log file. It includes the patient's
  name, so the name ends up in `~/brachify/app.log` in plain text.

### 10.5 fileio.py, how the form gets filled

A **function** is a named block of code that runs when something calls its name.
[`fileio.py`](../../src/classes/dicom/fileio.py) has 13. When you click **Import Dicom** and
choose a folder, they run in the order below. Each step says what goes in, what happens, and
what comes out on Ex2. Every Ex2 value in this section is *Verified*, from running brachify's
reader on the folder.

```
 Step 1  find the two files ─────────────── read_dicom_folder, is_rp_file, is_rs_file
 Step 2  pick the reader by vendor ──────── read_dicom_folder
 Step 3  copy the plan's three lists ────── load_varian_dicom_data
 Step 4  find the Central Axis, remove it ─ load_varian_dicom_data
 Step 5  open the RS file ───────────────── load_varian_dicom_data
 Step 6a work out where the cylinder is ─── load_central_axis_varian
 Step 6b find each needle's points ──────── load_channels_varian
 Step 7  move them into the cylinder's frame ── load_channels_varian
 Step 7b remove one-point "anchors" ──────── load_channels_varian
 Step 8  hand the form back ─────────────── back in the Import tab
```

#### Every function at a glance

| Function | Vendor | What it does |
|---|---|---|
| `read_dicom_folder` | both | finds the two files and picks the reader (steps 1 and 2) |
| `is_rp_file` | both | answers "is this a plan with at least one channel?" |
| `is_rs_file` | both | answers "is this a structures file?" |
| `load_varian_dicom_data` | Varian | the whole Varian reader (steps 3 to 8) |
| `load_central_axis_varian` | Varian | works out where the cylinder is (step 6a) |
| `load_channels_varian` | Varian | finds each needle's points and moves them into the cylinder's frame (steps 6b and 7) |
| `load_nucletron_dicom_data` | Oncentra | the whole Oncentra reader ([10.6](#106-elekta-oncentra-files)) |
| `load_central_axis_nucletron` | Oncentra | the Oncentra version of step 6a |
| `load_channels_nucletron` | Oncentra | the Oncentra version of steps 6b and 7 |
| `load_cylinder_contour` | both | the backup plan when there is no Central Axis (step 4) |
| `get_cylinder_from_dicom` | — | never called, and would crash if it were |
| `explore_rp_rs` | — | a debugging plot, never called |
| `get_dead_spaces` | — | commented out. Its comment says Varian files do not store the needle dead space |

`fileio.py` also keeps one shared yes/no value, **`method_found`**, meaning "we know where the
cylinder is". The readers set it, and the Import tab reads it afterwards to decide whether to
use the result.

#### Step 1: find the two files

Done by `read_dicom_folder`.

**In:** the folder you picked.

**What happens:**

1. It lists every file ending in `.dcm` in the folder, and in any folder inside it. Ex2 gives
   three files, listed in the order RS, RP, RD.
2. It opens each file in turn and asks `is_rp_file`: "is this a plan with at least one
   channel?" That means the file's `Modality` field, which records its type, must read
   `RTPLAN`, and its channel list must not be empty. **The first file that passes is used.**
3. It does the same with `is_rs_file`: "is this a structures file?" (`Modality` reads
   `RTSTRUCT`). **The first file that passes is used.**

**Out:** the RP file and the RS file. The RD file passes neither check, so it is never used.

**Watch out:**

- If a folder held two plans, brachify would take whichever one happened to be listed first.
- It never checks that the RS file is the one the plan was made with. The RP file has a field
  that names its RS file (`ReferencedStructureSetSequence`), and brachify does not read it.
- Every file is opened several times: once by each check, and again by the reader.

#### Step 2: pick the reader by vendor

**What happens:** `read_dicom_folder` reads the RP file's `Manufacturer` field.

- `"Varian Medical Systems"` → it runs `load_varian_dicom_data`.
- `"Nucletron"` → it runs `load_nucletron_dicom_data` ([10.6](#106-elekta-oncentra-files)).
- anything else → it crashes, and the app logs the misleading message "Empty folder selected."
  This is bug §7.2 in the source of truth.

Ex2 says `Varian Medical Systems`, so the Varian reader runs.

#### Step 3: copy the plan's lists

Done by `load_varian_dicom_data`.

**What happens:** it makes an empty `DicomData` form. Then it goes through the RP's channel list,
all 14 items, and copies three fields from each item into three lists. It also copies the five
patient and plan fields.

**Out on Ex2:**

```
channels_labels = [Central Axis, Applicator2, …, Applicator13, Tandem]   (14 entries)
channel_numbers = [1, 2, …, 14]
channels_rois   = [33, 34, 35, 36, 37, 38, 43, 44, 45, 39, 40, 41, 42, 46]
patient_name = "CYLINDER", patient_id = "SI_C_D30", plan_label = "Brachify_Ex2", …
```

If the RP file cannot be read, the error is written to the log and the reader carries on
anyway, so later steps fail with misleading messages such as "did not find Approval Status".

#### Step 4: find the Central Axis and take it out of the lists

Still `load_varian_dicom_data`.

**What happens:**

1. It goes through the labels one by one and asks: "does this label **contain** the words
   *central axis*?" Upper or lower case does not matter, and `centralaxis` written as one word
   also counts. **The first match wins.**
2. It remembers that channel's shape number in `central_channel_roi`.
3. It **removes that channel from all three lists**, at the same position, so they stay lined
   up. The Central Axis is a reference line, not a needle, so it must not become a hole.
4. It sets `method_found` to yes.

**Out on Ex2:** the match is at position 0, so `central_channel_roi` is `33`, and the lists go
from **14 entries to 13**.

**"Contains" is a trap.** A needle labelled `Central Axis Needle` also matches. If it comes
before the real axis in the list, it becomes the axis.
[10.8](#108-what-happens-if-a-value-in-the-file-changes) shows what that does.

**If no label matches**, a backup plan runs: `load_cylinder_contour` looks for an RS shape
whose observation label contains "surface" and works the cylinder out from that. It takes the
distance from the shape's first point to its last as the diameter, its middle point as the tip,
and the halfway point between first and last as the base. Neither sample can test this: both
have a Central Axis, and their `Surface3` marker has no observation label. If the backup also
fails, the app shows the "no central axis" error and the import stops. That is the only bad
input in this whole folder that produces a warning on screen.

#### Step 5: open the RS file

The structures file is read, so its shapes can be looked up.

#### Step 6a: work out where the cylinder is

Done by `load_central_axis_varian`.

**What happens:**

1. It searches the RS file's shapes for the one numbered **33**.
2. It takes that shape's points text, `1.32\82.59\75.21\1.32\90.33\-121.44`, and cuts it into
   points: `(1.32, 82.59, 75.21)` and `(1.32, 90.33, −121.44)`.
3. It treats the **first point as the cylinder's tip** and the **last point as its base end**.
   This relies on the planning program drawing the line from the tip, which is why the manual
   says to put the Central Axis's tip at the cylinder's tip.
4. It works out the arrow from base to tip: `(0, −7.74, 196.65)`. That arrow is the cylinder's
   direction. It points mostly along +z, tipped slightly in y. Its length is **196.8 mm**.

**Out:** `cylinder_tip`, `cylinder_base` and `cylinder_direction`.

#### Step 6b: each needle's points

Done by the first half of `load_channels_varian`.

**What happens:**

1. **It keeps only the shapes the plan uses.** From the RS file's 42 shapes, it keeps the 13
   whose numbers are in `channels_rois`.
2. **It puts them in the plan's order.** The RS file lists shapes by number (34, 35, … 42, 43,
   44 …). The plan's lists are in channel order (34, 35, 36, 37, 38, **43, 44, 45, 39** …). The
   code re-sorts the shapes to match the plan, so entry *i* of the shapes is the same needle as
   entry *i* of the labels. Without this step, Applicator7 (shape 43) would get shape 39's
   points, which belong to Applicator10.
3. **It cuts each shape's text into points:** 39 numbers become 13 points.

```
 RS file order (by shape number):   34  35  36  37  38  39  40  41  42  43  44  45  46
 plan order (by channel number):    34  35  36  37  38  43  44  45  39  40  41  42  46
                                                        └── re-sorted to match ──┘
```

**Out:** 13 lists of points, still in the planning computer's frame, in plan order. These are
also kept, unchanged, in the box `channel_contours`.

#### Step 7: move everything into the cylinder's frame

Done by the second half of `load_channels_varian`.

**Why:** brachify builds every cylinder the same way. Its **bottom sits at (0, 0, 0)**, it
**stands straight up along z**, and its **top is at z = the cylinder length**, which is 160 mm
by default (`CONFIG_CYLINDER_LENGTH`). The plan's points are tilted and somewhere else entirely.
So the code moves the whole plan, every needle at once, as if you picked up the cylinder with
its needles in it and stood it upright on a table.

```
  planning computer's frame                     cylinder's frame
  (tilted, somewhere in the scanner)            (upright, base on the origin)

        tip                                     z = 160 ── tip
          ╲                                         │
           ╲  Central Axis,        turn             │  Central Axis
            ╲ 196.8 mm long      ────────▶          │  now along +z
             ╲                   then slide         │
              ╲                                 z = 0 ── cylinder base
              base                                  │
                                                z = −36.8 ── where the axis's drawn base ends
```

**What happens to every point:**

| Stage | What it does | Central Axis tip | Applicator2 tip |
|---|---|---|---|
| start | the planning computer's frame | (1.32, 82.59, 75.21) | (1.51, 59.14, 81.10) |
| **turn** | rotate so the cylinder's arrow points straight up (`helper.rotate_points`) | (1.32, 85.48, 71.90) | — |
| **slide 1** | subtract the turned base point, so the axis's base end is at (0, 0, 0) | (0, 0, 196.8) | — |
| **slide 2** | move down by 196.8 − 160 = **36.8 mm**, so the axis tip is at z = 160 | **(0, 0, 160.0)** | **(0.19, −23.20, 166.81)** |

The turn and the two slides keep every distance between points exactly the same. *Verified*:
across all 13 needles, no piece of any needle changed length by more than 0.00000000000004 mm,
which is rounding noise. The shape of the plan is untouched; only its position and angle change.

The drawn axis is 196.8 mm long and the cylinder is 160 mm, so the axis's bottom 36.8 mm ends
up below the cylinder's base, where nothing uses it. **The cylinder is lined up by its tip**,
because the tip is where the needles leave it.

**Out:** `channel_paths`, 13 lists of points in the cylinder's frame. Applicator2's 13 points now
run from its tip at `(0.19, −23.20, 166.81)` to `(0.27, −6.55, 102.82)`. All 13 are listed in
[11.6](#116-channelpy-one-tube-per-needle).

Two things worth knowing about the result:

- **The needle tips are outside the cylinder.** Applicator2's tip is 23.2 mm from the centre, and
  the cylinder's radius is 15 mm. That is intended: the part of a needle beyond the cylinder is
  the part that goes into tissue.
- **The DICOM points stop about 103 mm above the base.** The straight run from there down to the
  base is added later, by the tube-building code in [chapter 11](#11-classesmesh). It is not in
  the plan.

**One edge case.** If the Central Axis pointed exactly the opposite way to +z in the planning
computer's frame, the turn would divide by zero and every coordinate would become `NaN`, "not
a number". *Verified* by calling `helper.rotate_points` directly. An axis that is only nearly
opposite works. A real plan is unlikely to hit this.

#### Step 7b: remove one-point "anchors"

Some plans include a "channel" that is a single point, used only to pin something in place. It
is not a needle, so the code removes it from all three lists and shows a warning on the first
one. Neither sample has any.

**Watch out:** the removal is correct for one anchor. A second one deletes the wrong entries,
which shifts every later needle's name and number by one position. The code's own comment says
it "will only work for if there is one single point". *Reasoned from code.*

#### Step 8: hand the result back

The filled form goes back to the Import tab
([`import_view.py`](../../src/windows/views/import_view.py)). The Import tab reads
`method_found`, and if it says yes, passes the form to the rest of the app
([10.7](#107-what-the-rest-of-the-app-does-with-the-form)).

The Import tab reads `method_found` with an import written *inside* its function, after the
reader has run. A yes/no value imported at the top of the file would be stuck at whatever it
was when the app started, which is no. The comment there says it must be imported late for this
reason.

### 10.6 Elekta Oncentra files

**Everything in this section is reasoned from code.** The repository has no Oncentra sample, so
none of this code has ever been run here.

Oncentra files go through the same steps. What differs is **where the shapes are kept**:

```
 Varian                                   Oncentra
 ──────                                   ────────
 RP file: names and numbers               RP file: names and numbers
 RS file: the shapes and their points       └─ private field (300F,1000)
                                                 └─ a copy of an RS file's lists:
                                                    shape numbers, names and points
                                          RS file: read only for the backup plan
```

- **Varian** puts the shapes in the **RS file**.
- **Oncentra** puts them in the **RP file**, inside a field Elekta invented: tag `(300F,1000)`.
  DICOM lets companies add fields of their own like this. They are called *private fields*, and
  standard tools do not know what is inside them.
- Inside that field is a list whose first item looks like a small RS file: shape numbers, names
  and points.
- Sometimes pydicom, the library brachify uses to read DICOM, cannot unpack that field and hands
  back a raw chunk of bytes. Brachify then unpacks it itself, assuming a particular byte layout.
  That code relies on a pydicom feature (`Dataset.read_encoding`) that has not been checked
  against the version the project pins, pydicom 3.0.2.

Five steps work differently:

| Step | Varian | Oncentra |
|---|---|---|
| 3: the shape-number list | from the plan's channels | from **every shape** in Elekta's private field, including any that are not channels |
| 4: finding the Central Axis | the plan's label **contains** "central axis" | the private shape's name **is exactly** "central axis" |
| 6b: re-sorting to plan order | yes | **no**: it assumes the order already matches |
| 6b: a shape with no points | dropped before matching | **skipped**, which shifts every later needle by one position. The code's comment says it adds an empty placeholder instead, but that line is switched off |
| 4: no Central Axis | the "surface" backup places the cylinder and the needles | the backup places the cylinder, but then **fails to load any needle**, because a value it needs (`center_index`) was never set. The failure is logged with the wrong cause, and no warning appears on screen |

The one-point anchor warning also differs: Varian warns on the first anchor, Oncentra on the
second.

### 10.7 What the rest of the app does with the form

Once the form is filled, the Import tab hands it to the app's **models**, the parts of the app
that hold its data, all at once:

```
 DicomData ──▶ Import tab's information panel       shows patient, plan and channel names
          ├──▶ Cylinder model                       builds the cylinder from the SETTINGS
          └──▶ Channels model ── one needle object per entry
                                  ├──▶ classes/mesh: the tube that becomes each hole   (chapter 11)
                                  ├──▶ the tandem: aimed at the channel named "Tandem"
                                  ├──▶ classes/pdf: the reference sheet                (chapter 12)
                                  └──▶ Export: tubes cut out of the cylinder, saved as STL
```

| Who | Reads | Does |
|---|---|---|
| Import tab's information panel | patient name, ID, plan label, approval, operator, channel labels and numbers | shows them as text |
| Cylinder model | nothing geometric | builds a cylinder from the **settings**: 30 mm across and 160 mm long by default |
| Channels model | the three lists and `channel_paths` | makes one needle object per entry: Applicator2, number 2, shape 34, with its 13 points |
| the tube builder in [chapter 11](#11-classesmesh) | each needle's points | builds the 3D tube that becomes the hole |
| the tandem | the channel whose label contains "tandem" | uses that channel's tip to aim the tandem |
| the PDF reference sheet in [chapter 12](#12-classespdf) | names, numbers and points | prints the channel table, the map of base holes, and each needle's length beyond the cylinder |
| Export | all the tubes | cuts them out of the cylinder and saves the printable STL file |

**After the import, nothing reads the DICOM files again.** If you change the cylinder's length
in the app, from 160 to 140 say, the needle points are not recalculated. Each needle stores the
difference, −20 mm, and adds it to its z values whenever its points are asked for. Importing at
160 and then changing to 140 gives the same result as importing at 140.

| You change in the app | Effect on what `classes/dicom` produced |
|---|---|
| cylinder length | `channel_paths` stay as imported. Each needle shifts itself by the difference |
| cylinder diameter | nothing: needles are placed relative to the axis, not the cylinder's wall |
| dead space, channel diameter, threading | nothing: the tubes are rebuilt from the same points |
| *Set as Tandem* | rewrites `tandem_channel`, the only box changed after import |

### 10.8 What happens if a value in the file changes

Each row is Ex2 with **one** value changed, passed through brachify's real reader. *Verified*:
these are the reader's outputs. They are not screenshots of the app's 3D view. "Base hole" means
where the needle's hole comes out of the bottom of the cylinder, written as its x and y.

| What was changed | What brachify produced | Did it warn you? |
|---|---|---|
| nothing | Applicator2's tip at `(0.2, −23.2, 166.8)`, its base hole at `(0.3, −6.6)` | — |
| the app's cylinder length set to 140 before importing | every tip 20 mm lower (166.8 → 146.8). The base holes did not move | no, and that is correct |
| the Central Axis's two points swapped, so its tip became its base | the whole model **upside down**: needle tips at z ≈ −43, below the cylinder | **no** |
| the Central Axis's tip moved 5 mm sideways, a tilt of 1.5° | **every needle moved**: Applicator2's tip x from 0.2 to −5.0, its base hole x from 0.3 to −3.3 | **no** |
| the Central Axis's label changed to `Reference Line` | no axis found, no channels, and the "no central axis" error | **yes** |
| a needle labelled `Central Axis Needle`, listed before the real axis | that needle became the axis and the real axis became a needle. Everything tilted: Applicator7's tip y went from 13.1 to 34.8, and the tandem's aim from 0° to 73.1° | **no** |
| Applicator7's shape number changed from 43 to 39 | Applicator7 silently took Applicator10's points, so two holes at one spot | **no** |
| the Tandem's tip moved 6 mm to one side | the tandem aimed at 32.7°. The tip's true direction from the axis is 30.0° | **no** |

What these show:

- **Only a missing Central Axis produces a warning.** Every other mistake quietly gives a
  different cylinder. This is why the project rules require a person to look at the model in the
  Export tab before it is printed.
- **The Central Axis carries most of the weight.** Swapping its points, moving its tip, or
  letting another needle take its place changes nothing about the needles themselves, yet every
  needle moves, because the axis defines the frame they are placed in.
- **The last row is a bug in `NeedleChannel.get_rotation()`**, in `classes/mesh/channel.py`. It
  measures the tandem's aim from the point (1, 0) instead of from the axis at (0, 0). The
  unchanged samples cannot show it: Ex2's tandem tip lies exactly on the x axis, where the error
  is zero. It is listed as §7.7 of the source of truth.

### 10.9 Things nothing checks

- **The radiation times.** Both samples give the Central Axis 222.8 seconds, although the
  manual says it should have none.
- **Whether the plan is approved.** An `UNAPPROVED` plan imports normally.
- **Whether the RS file belongs to this plan.**
- **Whether needles cross each other.** A function for it exists (`are_colliding` in
  `classes/mesh/intersections.py`) and is never called.
- **The dose file**, which is never opened.

---

## 11. classes/mesh

**Summary.** `classes/mesh/` turns the numbers from [chapter 10](#10-classesdicom) into solid 3D
objects, using a free 3D modelling engine called OpenCASCADE. It builds a solid plastic cylinder
with a rounded top and a small orientation bar, one solid tube along each needle's points, and,
if there is one, a solid bent rod for the tandem. Each tube is the needle's path from the plan,
with a pointed tip, rounded bends, a 6 mm "dead space" extension past the tip, and a straight
run down to the base that ends in a wider threaded hole for a collet. At export, every tube and
the tandem are subtracted from the cylinder, and what is left is saved as the printable STL file.
Nothing here checks whether holes overlap, and on Ex2 two pairs of base holes already do.

[`src/classes/mesh/`](../../src/classes/mesh/) holds seven files.

### 11.1 Words you need

| Word | What it means here | Real example |
|---|---|---|
| **solid** (in code: a **shape**, type `TopoDS_Shape`) | a closed 3D object with an inside and an outside, like a block of plastic | the cylinder |
| **OpenCASCADE** (in code: `OCC`) | the free 3D modelling engine brachify uses. It does all the geometry | `BRepPrimAPI_MakeCylinder` builds a cylinder |
| **primitive** | a ready-made basic solid: a cylinder, cone, sphere or box | a cylinder 1.35 mm in radius |
| **fuse** | join two solids into one | a cone fused onto a tube makes a pointed tube |
| **cut** | subtract one solid from another | a cylinder cut by a tube has a hole |
| **common** | keep only where two solids overlap | the tandem trimmed to a region around the cylinder |
| **fillet** | round off a sharp edge | the cylinder's flat top rounded into a dome |
| **sweep** | slide a 2D outline along a path to make a solid | a circle swept along an arc makes a bent tube |
| **edge, wire, face** | a line or curve; several edges joined end to end; a surface | used to draw the tandem's outline |
| **axis** (of the cylinder) | the cylinder's centre line, x = 0 and y = 0, running straight up | — |
| **distance from the axis** | how far a point is from that centre line: √(x² + y²) | Applicator2's tip is 23.2 mm from the axis |
| **height** | a point's z value: how far it is above the cylinder's base | the tip is at height 166.81 mm |
| **bounding box** | the smallest upright box around a solid, written (x-min, y-min, z-min, x-max, y-max, z-max) | Applicator2's tube: z from −1.0 to 171.97 |
| **volume** | how much space a solid takes up, in mm³ (cubic millimetres) | the cylinder: 109,599 mm³ |
| **cache** | a saved copy of a result, so it is not rebuilt every time | a needle tube is built once, then reused |
| **collet** | a small threaded sleeve that screws into the base of the cylinder and grips a needle | 5 mm across |
| **STL** | the file format 3D printers use: the surface chopped into tiny flat triangles | Ex2's export: 39,793 triangles |
| **STEP** | a 3D file format that keeps exact curves | used for tandem import and "Export Shape(s)" |

**The cylinder's frame.** Everything in this chapter uses the frame that [step 7](#step-7-move-everything-into-the-cylinders-frame) of chapter 10
set up: the cylinder's base is at (0, 0, 0), it stands straight up along z, and its top is at
z = 160. x and y say where a point is across the cylinder; z says how high it is.

```
                 z (height)
                 │
          top ── 160
                 │
                 │       one point (x, y, z):
                 │         x, y = where it is across the cylinder
                 │         z    = how high it is
                 │
         base ── 0 ────────── y
                ╱
               ╱
              x
```

### 11.2 How to read the drawings

The large drawings in this chapter are **slices**. Imagine cutting the finished model with a
very thin, flat knife and looking at the cut face. Each character is one point on that face,
tested against brachify's real 3D shapes:

| Character | Means |
|---|---|
| `.` | plastic: the point is inside the cylinder and not in any hole |
| `N` | a **needle hole**: the point is inside a needle's tube, where the tube cuts through plastic |
| `n` | the part of a needle's tube that is **outside** the cylinder. It cuts nothing, because there is no plastic there |
| `T` | the **tandem hole**, where it cuts through plastic |
| `t` | the part of the tandem's cut-out that is outside the cylinder |
| `o` | in the view from below: a needle's threaded hole |
| (blank) | air |
| `:` | many identical rows were folded into one to save space. The colons mark the holes carrying on |

The numbers down the left are the height or position of each row, in millimetres, and the `^`
marks along the bottom are the scale. A character is narrower than it is tall, so each drawing
says how many millimetres one character and one row stand for.

### 11.3 The whole model in one picture

```
 from chapter 10: every needle's points, already in the cylinder's frame
        │
        ├──▶ ChannelsModel ── one NeedleChannel per needle ── .shape() ──▶ rounded_channel()
        │                                                                 = a TUBE  (channel.py)
        │
 settings ──▶ CylinderModel ── BrachyCylinder ─────────────── .shape()
        │                                         = the CYLINDER, dome, notch, collar
        │                                                         (cylinder.py, notch.py)
        │
 settings ──▶ TandemModel ──── Tandem ── .generate_shape() = the TANDEM HOLE      (tandem.py)
                                     └── .tandem_shape()   = a preview of the tandem rod
        │
        ▼
 every tab's 3D view shows these shapes

 Export tab:   CYLINDER  −  TANDEM HOLE  −  every TUBE   =   the printable solid
                                                                  │
                                                     fileio.write_3d_file()
                                                                  ▼
                                                           .stl  or  .step
```

The idea: **a hole is made by building a solid the shape of the hole, then subtracting it.** Each
needle becomes a solid tube, the tandem becomes a solid bent rod, and both are cut out of a solid
cylinder.

**Ex2's finished model, sliced straight down the middle.** This slice is the plane x = 0.2,
which runs through the centre of the cylinder and happens to pass right along two needles,
Applicator2 and Applicator8, and up the tandem's straight part. The tandem is set up as the app
sets it up for Ex2: Tandem Height 160, bend angle 30°, aimed toward +x. *Verified*, sliced from
the real shapes. One character is 1 mm across; one row is 3 mm of height.

```
z= 180.0 |                                                 |
z= 177.0 |                                                 |
z= 174.0 |                                                 |
z= 171.0 |  nn                                             |
z= 168.0 |   nnn                     ttt             nnn   |
z= 165.0 |     nnn                   ttt            nnn    |
z= 162.0 |       nnn                 ttt            nn     |
z= 159.0 |        nnnn           ....TTT....       nnn     |
z= 156.0 |          nnn     .........TTT......... nnn      |
z= 153.0 |            nnn ...........TTT.........NNn       |
z= 150.0 |              NNN..........TTT........NNN..      |
z= 147.0 |              .NNNN........TTT.......NNN...      |
z= 144.0 |              ...NNN.......TTT.......NN....      |
z= 141.0 |              .....NN......TTT......NNN....      |
z= 138.0 |              ......NN.....TTT.....NNN.....      |
z= 135.0 |              ......NNN....TTT.....NNN.....      |
         |                    :::    :::     :::           |  (every row the same down to here)
z= 111.0 |              ......NNN....TTT.....NNN.....      |
z= 108.0 |              .......NN....TTT.....NNN.....      |
         |                     ::    :::     :::           |  (every row the same down to here)
z=  12.0 |              .......NN....TTT.....NNN.....      |
z=   9.0 |            .........NN....TTT.....NNN.....      |
z=   6.0 |            .........NN...TTTTT....NNN.....      |
z=   3.0 |            ........NNNN..TTTTT....NNN.....      |
z=   0.0 |            ........NNNN..TTTTT....NNN.....      |
z=  -3.0 |                                                 |
             ^    ^    ^    ^    ^    ^    ^    ^    ^    ^
             -25  -20  -15  -10  -5   0    5    10   15   20   y (mm)
```

What you are looking at, from left to right:

- **The left-hand `N` / `n` line is Applicator2.** Its tip (`n`, top left) is outside the
  cylinder, 23 mm from the axis. It enters the rounded top near height 150 and runs down inside
  the plastic about 7 mm from the axis, all the way to the base.
- **The middle `T` column is the tandem hole**, straight up the axis. It is wider at the bottom,
  heights 0 to 7, where the threaded part for its collet is. Above the cylinder (`t`) is the part
  of the cut-out that runs past the top so the hole opens cleanly.
- **The right-hand `N` / `n` line is Applicator8**, on the opposite side.
- **The dots** are the plastic. The dots narrow above height 145 because the top is a dome.
- **The extra dots at the bottom left**, heights 0 to 9, are the **notch**, the small bar on the
  outside of the cylinder that marks which side is which.
- **Applicator2 gets wider in the bottom rows**, heights 0 to 5: that is its threaded hole for
  its collet. Applicator8 has one too, but the threaded hole is only 0.47 mm wider than the
  channel, and at 1 mm per character that does not show on its side.

**The same model sliced the other way**, the plane y = 0.3, which runs along Applicator11 (left)
and Applicator5 (right). The tandem bends toward +x, so this slice shows its bend. Here it is
drawn at **Tandem Height 120**, lower than Ex2 uses, so the bend happens inside the cylinder and
is easy to see. *Verified*. One character is 1 mm across; one row is 3 mm of height.

```
z= 180.0 |                                                         |
z= 177.0 |                                                         |
z= 174.0 |                                                         |
z= 171.0 |   n                                                 n   |
z= 168.0 |   nnn                     ttttttttt              nnnn   |
z= 165.0 |     nnn                   ttttttttttttttt       nnn     |
z= 162.0 |       nnn                 ttttttttttttttttttt nnn       |
z= 159.0 |         nnn           ....TTTTTTTtttttttttttttt         |
z= 156.0 |          nnn     .........TTTTTTTTTTTTtttttttt          |
z= 153.0 |            nnn ...........TTTTTTTTTTTTTTtttt            |
z= 150.0 |              NNN..........TTTTTTTTTTTTTTTT              |
z= 147.0 |              ..NNN........TTTTTTTTTTTTTTT.              |
z= 144.0 |              ...NNN.......TTTTTTTTTTTTT...              |
z= 141.0 |              .....NNN.....TTTTTTTTTTT.....              |
z= 138.0 |              ......NNN....TTTTTTTTTN......              |
z= 135.0 |              ......NNN....TTTTTTTNNN......              |
z= 132.0 |              ......NNN....TTTTTT.NN.......              |
z= 129.0 |              ......NNN....TTTTT..NN.......              |
z= 126.0 |              .......NN....TTTT...NN.......              |
z= 123.0 |              .......NN....TTTT...NN.......              |
z= 120.0 |              .......NN....TTT....NN.......              |
z= 117.0 |              .......NN....TTT....NN.......              |
z= 114.0 |              .......NN....TTT...NNN.......              |
         |                     ::    :::   :::                     |  (every row the same down to here)
z= 105.0 |              .......NN....TTT...NNN.......              |
z= 102.0 |              .......NNN...TTT...NNN.......              |
         |                     :::   :::   :::                     |  (every row the same down to here)
z=   9.0 |              .......NNN...TTT...NNN.......              |
z=   6.0 |              .......NNN..TTTTT..NNN.......              |
z=   3.0 |              .......NNN..TTTTT..NNN.......              |
z=   0.0 |              .......NNN..TTTTT..NNN.......              |
z=  -3.0 |                                                         |
             ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^
             -25  -20  -15  -10  -5   0    5    10   15   20   25   x (mm)
```

Two things to notice:

- **The tandem hole (`T`) goes straight up the middle, starts to curve at height 120, and bends
  toward +x**, leaving through the rounded top. The wide region above it is the extra cut-out
  that makes the hole open cleanly through the surface.
- **At heights 135 to 138, the tandem hole runs into Applicator5's hole** (`TTTTTTTNNN`): the
  two holes merge. Nothing in brachify checks for this. At the Tandem Height Ex2 actually uses,
  160, they stay apart. The same slice at height 160 shows a straight tandem hole and two
  separate needle holes.

**The base, seen from below**, sliced at height 2 mm, through every threaded hole. It is drawn the
way the PDF draws it ([12.5](#125-the-base-map)): looking up from underneath, with −y at the top.
*Verified*. One character is 0.5 mm across; one row is 1 mm.

```
y= -18.0 |                                                                         |
y= -17.0 |                                                                         |
y= -16.0 |                                  .....                                  |
y= -15.0 |                                  .....                                  |
y= -14.0 |                          .....................                          |
y= -13.0 |                      .............................                      |
y= -12.0 |                  .....................................                  |
y= -11.0 |                .........................................                |
y= -10.0 |              .............................................              |
y=  -9.0 |            .................................................            |
y=  -8.0 |           .........................oo........................           |
y=  -7.0 |          ...................oo...oooooo..ooo..................          |
y=  -6.0 |         ..................oooooo.oooooooooooo..................         |
y=  -5.0 |        ...................oooooo...oo..oooooo.oo................        |
y=  -4.0 |        ..............oooooo.oo..............oooooo..............        |
y=  -3.0 |       ...............oooooo.................oooooo...............       |
y=  -2.0 |       ................ooo.......TTTTTTT.......oo.................       |
y=  -1.0 |       ...............ooo.......TTTTTTTTT......oooo...............       |
y=   0.0 |      ...............oooooo....TTTTTTTTTTT....oooooo...............      |
y=   1.0 |       ..............oooooo.....TTTTTTTTT.....oooooo..............       |
y=   2.0 |       .................ooo......TTTTTTT.......ooo................       |
y=   3.0 |       ...............ooooooo................oooooo...............       |
y=   4.0 |        ...............ooooo.................oooooo..............        |
y=   5.0 |        ...................oooo...........oo....o................        |
y=   6.0 |         .................oooooo........oooooo..................         |
y=   7.0 |          ................oooooo..oooooooooooo.................          |
y=   8.0 |           .......................oooooo......................           |
y=   9.0 |            .......................ooo.......................            |
y=  10.0 |              .............................................              |
y=  11.0 |                .........................................                |
y=  12.0 |                  .....................................                  |
y=  13.0 |                      .............................                      |
y=  14.0 |                          .....................                          |
y=  15.0 |                                    .                                    |
y=  16.0 |                                                                         |
y=  17.0 |                                                                         |
y=  18.0 |                                                                         |
                ^         ^         ^         ^         ^         ^         ^
                -15       -10       -5        0         5         10        15   x (mm)
```

- The circle of dots is the cylinder's base, 30 mm across.
- The block of dots sticking out at the top, y = −16 and −15, is the **notch**.
- The `T` in the middle is the tandem's threaded hole, 5 mm across.
- The 12 groups of `o` are the 12 needles' threaded holes, each 3.17 mm across, in a ring
  6.2 to 7.7 mm from the centre.
- Several groups look joined. The drawing is only 0.5 mm per character, so holes closer than
  that look merged, but **two pairs really do overlap**: see [11.10](#1110-what-happens-if-a-setting-changes).

### 11.4 The files

| File | Size | Builds | Used by |
|---|---|---|---|
| [`cylinder.py`](../../src/classes/mesh/cylinder.py) | 151 lines | the solid cylinder, dome, collar and notch | Cylinder model and view |
| [`notch.py`](../../src/classes/mesh/notch.py) | 36 | the small orientation bar | `cylinder.py` |
| [`channel.py`](../../src/classes/mesh/channel.py) | 584 | one tube per needle | Channels model, Export, PDF |
| [`tandem.py`](../../src/classes/mesh/tandem.py) | 566 | the tandem hole, and a preview of the tandem rod | Tandem model |
| [`helper.py`](../../src/classes/mesh/helper.py) | 188 | small shared maths: directions, distances, rotations | all of the above, and `classes/dicom` |
| [`intersections.py`](../../src/classes/mesh/intersections.py) | 16 | "do two solids touch?" | **nothing** |
| [`fileio.py`](../../src/classes/mesh/fileio.py) | 57 | reads STEP files, writes STL and STEP files | Tandem model (import), Export tab (export) |

```
 helper.py ◀──────────── cylinder.py ◀──── notch.py
     ▲                       ▲
     ├──────────────── channel.py
     │
     ├──────────────── classes/dicom/fileio.py      (uses rotate_points)
     │
     └──────────────── windows/models/tandem_model.py   (uses extend_bottom_face)

 tandem.py          used by the Tandem model; uses no other file in this folder
 fileio.py          used by the Tandem model (import) and the Export tab (export)
 intersections.py   used by nothing
```

An arrow points from a file to the file it uses.

### 11.5 cylinder.py and notch.py, the solid cylinder

#### What it looks like, with the real numbers

**From the side**, looking along the x axis, with the notch on the left. This is a sketch, not a
slice: the slices in [11.3](#113-the-whole-model-in-one-picture) show the real shape.

```
  height z (mm)
  160 ┤          .-'''''-.        ← top of the dome (its peak), on the axis
      │        .'         '.
  145 ┤       |             |     ← the straight wall ends and the dome begins
      │       |             |
      │       |             |       wall: 15 mm from the axis, so 30 mm across
      │       |             |
      │       |             |
   10 ┤     ██|             |     ← the notch: sticks out 1.8 mm, 10 mm tall
    0 ┴─────██|_____________|──   ← the base, at height 0
            ^ ^      ^      ^
        -16.8 -15    0      15        y (mm)
```

**From below**, as the PDF draws it, with −y at the top:

```
                   −y   (the PDF labels this side "Anterior", the patient's front)
                   ███                  ← the notch, at y = −16.8 to −14.8
              .-----┼-----.
            /       │       \
     −x ───┼────────┼────────┼─── +x    ← at rotation 0°, the tandem bends toward +x
            \       │       /
              '-----┼-----'
                    │
                   +y   (the PDF labels this side "Posterior", the patient's back)
```

#### How `shape()` builds it

| Step | What happens | Result with the default settings |
|---|---|---|
| 1 | make a plain cylinder 15 mm in radius and 160 mm tall, standing on (0, 0, 0) | a can with a flat top |
| 2 | search its faces for the highest flat one: the top | the circle at height 160 |
| 3 | **round that top edge** with a radius of 15 mm, the same as the cylinder's own radius | the flat top becomes a **half-sphere dome** |
| 4 | if *Add Collar* is ticked, fuse a ring around the base (`add_base`) | off by default |
| 5 | fuse on the notch (`add_notch`) | a 2 × 2 × 10 mm bar on the side |

Because the dome's radius equals the cylinder's, **the wall is straight up to height 145, and the
dome rises from there to its peak at height 160.** *Verified*, by testing points against the
solid:

| Point (x, y, z) | Inside the cylinder? | Why |
|---|---|---|
| (0, 0, 159.9), just under the peak | yes | under the top of the dome |
| (14.9, 0, 140), at the edge, below 145 | yes | still on the straight wall |
| (14.9, 0, 150), at the edge, above 145 | **no** | the dome has curved inward by then |

**The volume checks out.** *Verified*: brachify's cylinder is **109,599.3 mm³**. The textbook
volume of a 30 × 160 mm cylinder with a half-sphere top is **109,563.0 mm³**. The difference,
**36.3 mm³**, is the notch: its box is 2 × 2 × 10 mm, which is 40 mm³, and about 4 mm³ of that
sits inside the wall.

#### The notch (`notch.py`)

`CylinderNotch` is a box **2 mm wide, 2 mm deep and 10 mm tall**. It starts 0.2 mm inside the
wall, so it fuses on firmly, then turns 270° around the cylinder. That puts it on the **−y side**,
which the PDF's base map labels **Anterior**, the patient's front. *Verified* bounding box: x from
−1 to 1, y from −16.8 to −14.8, z from 0 to 10.

#### The collar (`add_base`)

The collar is an optional ring around the base:

```
           |             |          ← the cylinder wall
       ┌───|             |───┐      ← the collar, base_height tall
       │   |             |   │
       └───|_____________|───┘      its outer edge is 15 + base_thickness from the axis
```

It does nothing if either `CONFIG_BASE_HEIGHT` or `CONFIG_BASE_THICKNESS` is 0, and both are 0
by default. The notch was meant to move up onto the collar, but that line is commented out, so
the notch always sits at height 0 (§7.4 of the source of truth).

#### What `BrachyCylinder` holds, and its functions

| Field | Means | Comes from | Default |
|---|---|---|---|
| `diameter` | width | the Cylinder tab. Only the DICOM "surface" backup plan measures one from the file | 30 mm |
| `length` | height | setting `CONFIG_CYLINDER_LENGTH` | 160 mm |
| `expand_base` | collar on or off | the *Add Collar* tick box | off |
| `notch` | the orientation bar | built automatically | — |

| Function | What it does |
|---|---|
| `shape()` | builds the solid, steps 1 to 5 above |
| `setDiameter`, `setLength`, `enableBase` | change a value, rebuild, and **save** the result |
| `get_brachy_cylinder(data)` | makes the cylinder when a plan is imported |
| `add_base`, `add_notch` | the collar and the notch |

#### Two traps in the cylinder code

1. **`shape()` does not save its result.** It returns the saved copy when there is one, but it
   never saves one itself. On a cylinder no setter has touched, it rebuilds the dome and notch on
   every call. *Verified*: after calling it on a new cylinder, the saved copy is still empty.
   Only the three setters store a copy. The source of truth and AGENTS.md said "`shape()` caches
   into `self._shape`"; both were corrected on 2026-10-02.
2. **The default diameter is frozen when the program starts.** Python works out a default value
   once, when the file first loads, so a later change to the settings never reaches it. Every
   caller in the app passes a diameter, so nothing breaks today. *Reasoned from code.*

### 11.6 channel.py, one tube per needle

This section follows one needle, **Applicator2**, the plan's channel number 2 and the first
needle in its list ([10.2](#102-words-you-need)), from its 13 points to a finished tube.

#### Applicator2's 13 points, in full

These are the points from [chapter 10](#10-classesdicom), after brachify has moved them into the
cylinder's frame. Each point is three numbers (x, y, z). "Distance from the axis" is
√(x² + y²): how far the point is from the cylinder's centre line.

| Point | x | y | z (height) | Distance from the axis | Inside the cylinder? |
|---|---|---|---|---|---|
| 1, the tip | 0.19 | −23.20 | 166.81 | 23.20 | no |
| 2 | 0.20 | −10.42 | 145.28 | 10.42 | yes |
| 3 | 0.20 | −9.80 | 144.08 | 9.81 | yes |
| 4 | 0.20 | −9.29 | 142.99 | 9.29 | yes |
| 5 | 0.20 | −8.77 | 141.80 | 8.77 | yes |
| 6 | 0.20 | −8.25 | 140.51 | 8.26 | yes |
| 7 | 0.20 | −7.94 | 139.32 | 7.94 | yes |
| 8 | 0.20 | −7.52 | 138.02 | 7.52 | yes |
| 9 | 0.20 | −7.30 | 136.72 | 7.30 | yes |
| 10 | 0.20 | −7.08 | 135.42 | 7.09 | yes |
| 11 | 0.21 | −6.96 | 134.12 | 6.97 | yes |
| 12 | 0.21 | −6.95 | 132.82 | 6.96 | yes |
| 13, the last | 0.27 | −6.55 | 102.82 | 6.56 | yes |

How to read this table:

- **x hardly changes** (0.19 to 0.27), so the whole needle lies in one flat plane, the plane
  x ≈ 0.2. That is why the slice in [11.3](#113-the-whole-model-in-one-picture) at x = 0.2 shows it
  so clearly.
- **y goes from −23.20 to −6.55**, and **z goes from 166.81 down to 102.82.** Read top to
  bottom, the needle comes down from its tip and moves toward the centre line.
- **"Curving in" means exactly this:** from point 2 to point 12, the height drops 12.5 mm (from
  145.28 to 132.82) while the distance from the axis drops from 10.42 to 6.96 mm. Each step down,
  the needle moves a little closer to the centre, and the steps get smaller, so the path bends
  gently from slanting to nearly straight down.
- **Point 1 to point 2 is one long straight stretch**, 25.04 mm, slanting outward. The needle
  leaves the cylinder along this stretch, at (0.20, −13.78, 150.93), which is 18.46 mm before
  the tip. Everything above that point is in tissue.
- **Point 12 to point 13 is a long straight stretch of 30 mm**, almost vertical, ending 6.56 mm
  from the axis at height 102.82.
- **The plan stops at point 13.** Everything below height 102.82 is added by brachify.

#### What the finished tube looks like

The same needle, as a sketch from the side, with every number from the table above. The left
column is height; each label says the point's full (x, y, z).

```
 height (mm)
  171.97   ▲   the tip after dead space: (0.19, −26.26, 171.97)       ┐ 6 mm of dead space,
           │                                                          │ added past the tip
  166.81   ●   point 1, the DICOM tip: (0.19, −23.20, 166.81)         ┘
            ╲
             ╲   one straight stretch, 25 mm, slanting outward
  150.93      ╳  ← leaves the cylinder here: (0.20, −13.78, 150.93)
               ╲
  145.28        ●  point 2: (0.20, −10.42, 145.28), 10.42 mm from the axis
                ●  points 3 to 12: 1.3 mm apart, moving in toward the axis
  132.82        ●  point 12: (0.21, −6.95, 132.82), 6.96 mm from the axis
                │
                │  a straight stretch, 30 mm, almost vertical
  102.82        ●  point 13, the last DICOM point: (0.27, −6.55, 102.82)
                │
                │  added by brachify: straight down, 2.7 mm across
                │
    5.00       ┌┴┐
               │ │ the threaded hole: 3.17 mm across, where the collet screws in
    0.00  ─────┤ ├─────  the base of the cylinder
   −1.00       └─┘ 1 mm below the base, so the hole opens through the bottom face
```

This sketch is not to scale. Here is the real thing, sliced from the actual tube at x = 0.2:
first the top, where the needle leaves through the dome, then the base, where the threaded hole
is. *Verified*.

**The top**, one character 0.5 mm across, one row 1 mm of height:

```
z= 174.0 |                                                     |
z= 173.0 |                                                     |
z= 172.0 |                                                     |
z= 171.0 |    nnn                                              |
z= 170.0 |    nnnnn                                            |
z= 169.0 |    nnnnnnn                                          |
z= 168.0 |      nnnnnn                                         |
z= 167.0 |       nnnnnn                                        |
z= 166.0 |        nnnnnn                                       |
z= 165.0 |         nnnnnn                                      |
z= 164.0 |          nnnnnnn                                    |
z= 163.0 |           nnnnnnn                                   |
z= 162.0 |             nnnnnn                                  |
z= 161.0 |              nnnnnn                                 |
z= 160.0 |               nnnnnn                                |
z= 159.0 |                nnnnnnn                       .......|
z= 158.0 |                 nnnnnnn                  ...........|
z= 157.0 |                   nnnnnn              ..............|
z= 156.0 |                    nnnnnn          .................|
z= 155.0 |                     nnnnnn       ...................|
z= 154.0 |                      nnnnnn     ....................|
z= 153.0 |                       nnnnnnn ......................|
z= 152.0 |                         nnnnnN......................|
z= 151.0 |                          nnnNNN.....................|
z= 150.0 |                           nNNNNN....................|
z= 149.0 |                            NNNNNN...................|
z= 148.0 |                           ..NNNNNNN.................|
z= 147.0 |                           ...NNNNNNN................|
z= 146.0 |                           .....NNNNNN...............|
z= 145.0 |                           ......NNNNNN..............|
z= 144.0 |                           .......NNNNNN.............|
z= 143.0 |                           ........NNNNNN............|
z= 142.0 |                           .........NNNNNN...........|
z= 141.0 |                           ..........NNNNN...........|
z= 140.0 |                           ..........NNNNNN..........|
z= 139.0 |                           ...........NNNNNN.........|
z= 138.0 |                           ............NNNNN.........|
z= 137.0 |                           ............NNNNNN........|
z= 136.0 |                           ............NNNNNN........|
z= 135.0 |                           .............NNNNN........|
         |                                        :::::        |  (every row the same down to here)
z= 126.0 |                           .............NNNNN........|
                ^         ^         ^         ^         ^
                -25       -20       -15       -10       -5   y (mm)
```

Read it like this: the dots on the right are the plastic, with the rounded top curving down from
height 159 to the straight wall at y = −14.5. The tube (`n`) starts at the pointed tip near
(y −26, height 171), slants down and to the right, and turns into `N` where it enters the plastic
around height 151. Inside, it keeps moving right, toward the centre line, until about height 135,
and from there it goes straight down.

**The base**, one character 0.25 mm across, one row 0.5 mm of height:

```
z=  9.0 |.........NNNNNNNNNNN.........|
        |         :::::::::::         |  (every row the same down to here)
z=  5.5 |.........NNNNNNNNNNN.........|
z=  5.0 |........NNNNNNNNNNNNN........|
        |        :::::::::::::        |  (every row the same down to here)
z=  0.0 |........NNNNNNNNNNNNN........|
z= -0.5 |        nnnnnnnnnnnnn        |
z= -1.0 |        nnnnnnnnnnnnn        |
z= -1.5 |                             |
z= -2.0 |                             |
         ^   ^   ^   ^   ^   ^   ^   ^
         -10 -9  -8  -7  -6  -5  -4  -3   y (mm)
```

Above height 5 the hole is 11 characters wide, 2.75 mm, which is the 2.7 mm channel. From height
5 down to the base it is 13 characters, 3.25 mm, which is the 3.17 mm threaded hole. Below the
base (`n`) the tube carries on 1 mm into the air, so the cut opens cleanly through the bottom.

#### How the tube is built: `rounded_channel`, step by step

```
 Applicator2's 13 points
        │
  ① push the tip out by the dead space (6 mm) ─────────── tip height 166.81 → 171.97
        │
  ② add the height offset to every z ───────────────────── 0 here; changes with cylinder length
        │
  ③ cut every number to 5 decimal places ───────────────── avoids a joining bug in OpenCASCADE
        │
  ④ drop repeated points, then points on a straight line ─ 13 → 13 → 12 points
        │
  ⑤ a cone for the tip, then a tube to the second point
        │
  ⑥ for every next pair of points: a tube 2.7 mm across, fused on
        │      ├─ a stretch that crosses height 0 also gets a threaded hole there
        │      └─ if a join fails: the retry ladder (below)
        │
  ⑦ a ball 2.7 mm across at every point after the first ── smooth bends
        │
  ⑧ if the last point is above height 0: run straight down to the base
        │      2.7 mm tube down to height 5, then the 3.17 mm threaded hole down to −1
        ▼
   one solid tube
```

What each step does to Applicator2:

| Step | Done by | Before | After |
|---|---|---|---|
| ① dead space | `apply_deadspace_to_points` | tip (0.19, −23.20, 166.81) | tip (0.19, −26.26, 171.97): moved exactly 6.00 mm further out along the first stretch |
| ② height offset | `rounded_channel` | z + 0 | unchanged |
| ③ trim | `rounded_channel` | full precision | 5 decimal places, cut off, not rounded |
| ④ clean up | `remove_identical_points`, `remove_collinear_points` | 13 points | 13 after the first, **12** after the second |
| ⑤ tip | `create_point`, `_cone_pipe` | — | a cone 2.5 mm long at the tip. Crashes if the first stretch is shorter than 2.5 mm (§7.3 of the source of truth) |
| ⑥ pieces | `pipe_segment` | — | one straight tube per stretch |
| ⑦ joints | `rounded_channel` | sharp corners | rounded |
| ⑧ to the base | `down_to_end` | ends at height 102.82 | runs to height −1, with the threaded hole |

**Why the dead space.** A real needle's radioactive source can never reach the very end of the
needle. That unreachable length is the **dead space**, setting `CONFIG_DEADSPACE`, 6 mm by
default. Pushing the tip out by it makes the model's needle as long as the real one.

**Why 13 points become 12.** `remove_collinear_points` drops a point that lies on a straight line
between its neighbours, because a joint there adds nothing but an extra piece to join. For each
point it measures the angle between the stretch arriving at the point and the stretch leaving it.
If that angle is under **0.02°**, the point is dropped. *Verified* on Applicator2:

| At point | 2 | 3 | 4 | 5 | 6 | 7 | 8 | **9** | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Bend (degrees) | 3.53 | 1.80 | 2.05 | 1.41 | 7.21 | 3.20 | 8.34 | **0.0004** | 4.34 | 4.89 | 0.39 |

Point 9 bends by only 0.0004°, so it sits on the straight line from point 8 to point 10, and it
is dropped. Every other point bends by more than 0.02° and is kept. `remove_identical_points`
drops a point that is the same as the one before it, and Applicator2 has none.

**The retry ladder in step ⑥.** OpenCASCADE sometimes fails to join two pieces that only just
touch. When that happens, the code tries three fixes in turn:

```
 join fails ─▶ fix1: make the piece 0.001 mm wider, try again ──────────── works? done
                 │ no
                 ▼
               fix2: round both points to 4, then 3, then 2 decimals ────── works? done
                 │ no
                 ▼
               fix3: nudge each coordinate by ±0.01 mm in turn ───────────── works? done
                 │ no
                 ▼
               a warning or error dialog on screen
```

On Ex2, none of the 12 needles needed a dialog. *Verified*: a stand-in window recorded no dialog
calls.

**The result**, *Verified*: Applicator2's tube has a bounding box from height −1.0 to 171.97 and
a volume of 1,020.7 mm³. It took 0.57 seconds to build, and all 12 needle tubes took 8.9 seconds.

#### What a `NeedleChannel` holds

One `NeedleChannel` is made for each needle when a plan is imported (in `ChannelsModel`):

| Field | Means | Applicator2 |
|---|---|---|
| `label` | name | `Applicator2` |
| `channel_number` | number for the PDF | `2` |
| `roi_number` | shape number in the DICOM | `34` |
| `points` | the 13 points in the table above, **never changed after import** | 13 points |
| `_offset` | how far to shift it up or down after a cylinder length change | `0.0` |
| `_diameter` | tube width, setting `CONFIG_CHANNELS_DIAMETER` | `2.7` mm |

| Method | What it does |
|---|---|
| `shape()` | builds the tube the first time, then **reuses** the saved copy. Unlike the cylinder, this one does cache |
| `set_offset(h)` | stores a new shift and rebuilds. Called when the cylinder length changes |
| `set_diameter(d)` | stores a new width and rebuilds |
| `get_points()` | the points with the shift added to every z. The PDF reads these |
| `get_rotation()` | the tip's angle around the cylinder, used to aim the tandem. **Bug:** it measures from the point (1, 0) instead of from the axis at (0, 0) ([10.8](#108-what-happens-if-a-value-in-the-file-changes)) |

Three more functions in `channel.py`, `generate_cylinder_points`, `get_surface_intersection` and
`get_interstitial_length`, are never used from here. They are older copies of what the PDF code
does for itself ([chapter 12](#12-classespdf), and §7.4 of the source of truth).

### 11.7 tandem.py, the tandem

#### What the tandem hole looks like

The tandem goes **straight up the middle of the cylinder, then bends to one side**. The code
draws it **flat, in the x–z plane**, then gives it thickness. As a sketch, inside the cylinder:

```
z=  175 |                                          ***|
z=  170 |                                       ****  |
z=  165 |                                    ****     |
z=  160 |                 .               ****        |
z=  155 |      .                     . ****           |
z=  150 |   .                        ***.             | ← the hole leaves through the dome
z=  145 |  |                      ***    |            |
z=  140 |  |                   ****      |            |
z=  135 |  |                ****         |            | ← the bend ends near here: (4.69, 137.5)
z=  130 |  |               **            |            |
z=  125 |  |              **             |            |
z=  120 |  |              *              |            | ← the bend starts: (0, 120), the Tandem Height
z=  115 |  |              *              |            |
z=  110 |  |              *              |            |
z=  105 |  |              *              |            |
z=  100 |  |              *              |            |
z=   95 |  |              *              |            |
z=   90 |  |              *              |            |
z=   85 |  |              *              |            |
z=   80 |  |              *              |            |
z=   75 |  |              *              |            |
z=   70 |  |              *              |            |
z=   65 |  |              *              |            |
z=   60 |  |              *              |            |
z=   55 |  |              *              |            |
z=   50 |  |              *              |            |
z=   45 |  |              *              |            |
z=   40 |  |              *              |            |
z=   35 |  |              *              |            |
z=   30 |  |              *              |            |
z=   25 |  |              *              |            |
z=   20 |  |              *              |            |
z=   15 |  |              *              |            |
z=   10 |  |              *              |            |
z=    5 |  |              *              |            | ← threaded part, 5.0 mm across, up to height 7
z=    0 |  |______________*______________|            | ← the base
           ^    ^    ^    ^    ^    ^    ^    ^    ^
           -15  -10  -5   0    5    10   15   20   25   x (mm)
```

With the default bend (R = 35, θ = 30°), the bend always ends **4.69 mm to the side and
17.5 mm higher** than where it started. *Verified*: at H = 145 the bend ends at x = 4.69,
z = 162.5. The real shape, sliced, is the second drawing in
[11.3](#113-the-whole-model-in-one-picture).

#### How `generate_shape` builds the hole

1. **Draw the path in 2D:** a straight line up the middle to height H, then the arc.
2. **Build the solid pieces:**
   - the straight part, with its threaded base: 5.0 mm across up to height 7, then 3.8 mm,
   - the bend: a 3.8 mm circle swept along the arc,
   - an "interior" fill from the path up to the top of the dome, so the hole opens cleanly,
   - the stopper section (`stopper_shape`).
3. **Fuse them** into one solid.
4. **Trim it** to an imaginary cylinder 10 mm bigger than the real one, using *common*
   (`cylinder_offset_shape`). The hole then runs a little past the real surface, and opens
   cleanly through it, without sticking out forever.

```
     ┌──────────────────┐   the imaginary cylinder: 25 mm from the axis, about 10 mm taller
     │    .-'''''-.     │
     │   |         |    │   the real cylinder
     │   |         |    │
     │   |         |    │   the hole is trimmed to the outer box, so it runs
     │   |         |    │   a little past the real surface and opens through it
     └───|_________|────┘
```

#### How the settings change it

| Setting, on the Tandem tab's *Generate* sub-tab | Means | Default |
|---|---|---|
| Tandem Height, `CONFIG_TANDEM_TIP_HEIGHT` | H: where the bend **starts** | **170** (see trap 1) |
| Bend Angle, `CONFIG_TANDEM_TIP_ANGLE` | θ: how far it bends away from vertical | 30° |
| Bend Radius, `CONFIG_TANDEM_BEND_RADIUS` | R: how tight the bend is | 35 mm |
| Channel Diameter, `CONFIG_TANDEM_CHANNEL_DIAMETER` | hole width | 3.8 mm |
| Stopper Diameter, `CONFIG_TANDEM_STOPPER_DIAMETER` | width of the wider stopper section | 5.0 mm |
| Threading depth and diameter | the threaded base, as for the needles | 7 mm, 5.0 mm |
| Rotation, `CONFIG_TANDEM_ROTATION` | which way around the cylinder it bends, applied by `TandemModel` | 0°, toward +x |

*Verified*, building the hole at different heights with the other settings at their defaults:

| Tandem Height | Bend ends at height | Hole reaches x up to | So the hole… |
|---|---|---|---|
| 120 | 137.5 | 20.45 | bends well inside, and leaves through the side of the dome |
| 145 | 162.5 | 10.10 | bends near the top |
| 155 | 172.5 | 4.79 | barely bends before leaving |
| 160 | 177.5 | 3.09 | is almost straight inside the cylinder: the bend is mostly above it |
| **170, the default** | — | — | **crashes**, with an error from OpenCASCADE |

At height 150, changing only the angle:

| Bend Angle | Hole reaches x up to |
|---|---|
| 0° | 2.50: a straight hole, 5.0 mm at its widest (the threaded part) |
| 15° | 6.23 |
| 45° | 7.19 |

#### The other things in tandem.py

| Function | What it does |
|---|---|
| `tandem_shape()` | a **preview of the physical tandem rod**, not a hole. It is shown in the Export tab when *Show Tandem* is ticked, and never exported. At height 150 it reaches height 231.75 and x = 31.33, because the real rod goes well past the cylinder into the body |
| `stopper_shape()` | the wider stopper section of the hole |
| `cylinder_offset_shape()` | the bigger imaginary cylinder used for trimming |
| `make_edge`, `make_wire`, `make_symmetrical_shape`, `fuse_shapes`, `intersection2d` | building blocks |
| `make_arc`, `make_point`, `make_cylinder`, `make_curved_pipe`, `show_cylinder`, `make_thru_shape` | appear unused |
| the block at the bottom, `if __name__ == "__main__"` | lets you run `python src/classes/mesh/tandem.py` on its own to see a tandem, with built-in test values |

**What `TandemModel` does with the result:** it turns the shape around the axis by the rotation.
For an **imported** STEP tandem, it also moves it up or down by the height offset, and stretches
its lowest flat face down to height 0 with `helper.extend_bottom_face`, so the hole always
reaches the base.

#### Two traps in the tandem code

1. **The default Tandem Height (170) is taller than the default cylinder (160), so generating
   with the defaults crashes.** *Verified.* You do not see it in normal use: on import, the
   Tandem tab's height box is capped at the cylinder length
   ([import_view.py:140](../../src/windows/views/import_view.py#L140)), which turns 170 into 160.
   New code, or a test, that calls `Tandem()` gets defaults that do not work.
2. **The tandem hole and the needle holes are built separately.** Nothing checks whether they
   overlap, and at Tandem Height 120 on Ex2 they do ([11.3](#113-the-whole-model-in-one-picture)).

### 11.8 helper.py, intersections.py and fileio.py

#### helper.py, shared maths

| Function | What it does | Used by |
|---|---|---|
| `rotate_points(points, from, to)` | turns points so one direction lines up with another | `classes/dicom`, for chapter 10's [step 7](#step-7-move-everything-into-the-cylinders-frame) |
| `get_vector(p1, p2, length)` | the arrow from p1 to p2, stretched to `length` | the needle tip |
| `get_direction(p1, p2)` | the same arrow as a pure direction | every tube piece |
| `get_magnitude(p1, p2)` | the distance between two points | every tube piece |
| `face_is_plane`, `geom_plane_from_face` | "is this face flat?" and "which plane is it on?" | finding the cylinder's top |
| `get_faces`, `get_faces_axis`, `lowest_face_by_normal` | list a solid's flat faces, sorted by height | `extend_bottom_face` |
| `extend_bottom_face(shape)` | stretches a solid's lowest flat face down to height 0 | imported tandems |
| `translate_shape`, `get_vector_from_angle`, `add_point_and_vector` | — | appear unused |

#### intersections.py, built and never used

`are_colliding(a, b)` asks OpenCASCADE where two solids' surfaces cross, and answers yes if they
cross anywhere. **Nothing in the app calls it**, so the app never checks whether holes touch. On
Ex2's two closest needles, Applicator10 and Applicator11, it answers **yes**. *Verified*.

#### fileio.py, files in and out

```
  a .step or .stp file ──▶ read_3d_file() ──▶ a solid           importing a tandem model
                           any other file type → an error dialog

  a solid ──▶ write_3d_file() ──▶ .stl   triangles, binary      Export Mesh
                              └─▶ .step  exact curves (AP203)   Export Shape(s), or Export Mesh
```

**How smooth the STL is.** Curves become flat triangles, and two settings control how closely
they follow the true surface. `linear_deflection = 0.5` lets a triangle stray up to 0.5 mm from
it. `angular_deflection = 0.3` (radians, about 17°) limits the angle between neighbouring
triangles. Ex2's cylinder with its 12 needle holes became **39,793 triangles in a 1.99 MB file**.
*Verified.* Writing it also printed **"6 faces have been skipped due to null triangulation"** from
OpenCASCADE: six faces of the model got no triangles at all, which can leave small gaps in the
file. Which faces, and whether printing software minds, has not been checked.

**A bug in the error path.** If writing fails, [line 54](../../src/classes/mesh/fileio.py#L54)
runs `from src.classes.logger import log`, while every other file imports `classes.logger`. In
the Windows `.exe` there is no `src` package, so that line itself fails and hides the original
error. *Reasoned from code.*

### 11.9 How it all comes together at export

[export_view.py:202-210](../../src/windows/views/export_view.py#L202-L210):

```
  the cylinder        the tandem hole      tube 1           tube 12         the printable solid
  dome, notch,    −   (if there is    −   Applicator2  − … − Applicator13  =
  collar              one)                (a disabled channel is left out)
  109,599.3 mm³                                                             98,960.8 mm³

                         10,638.5 mm³ removed: about 10% of the plastic
```

*Verified* on Ex2's 12 needles, without the tandem. The cuts took 0.6 seconds, after 8.9 seconds
to build the tubes.

**The parts of a tube outside the cylinder remove nothing**, because there is no plastic there to
cut. That is why the pointed tips and the dead-space extension, which you see sticking out in the
3D view, do not change the print.

### 11.10 What happens if a setting changes

Applicator2's tube, rebuilt with one setting changed at a time. *Verified*:

| Change | Top of the tube (height) | Threaded base hole? | Volume (mm³) | Means |
|---|---|---|---|---|
| none | 171.97 | yes | 1,020.7 | — |
| Dead Space 6 → **0** | 166.81 | yes | 987.9 | only the part beyond the cylinder got shorter, so **the print does not change**. The PDF's lengths do ([12.7](#127-what-happens-if-a-setting-changes)) |
| Threading Depth 5 → **0** | 171.97 | **no** | 1,007.7 | **no wide hole at the base**, so no collet can be screwed in |
| cylinder 160 → **140** (`set_offset(−20)`) | 151.97 | yes | — | the whole tube moves down 20 mm, but **its bottom stays at height −1**, because the run to the base is rebuilt |
| Channels Diameter 2.7 → **4.0** | 171.97 | yes | 2,185.5 | more than double the volume, and neighbouring holes come closer to touching |

#### Two pairs of Ex2's base holes already overlap

Each threaded hole is 3.17 mm across. For two holes to stay separate, their centres must be more
than 3.17 mm apart. *Verified*, from every needle's base-hole centre:

| Pair | Centres apart | Plastic left between the holes |
|---|---|---|
| Applicator10 and Applicator11 | 3.10 mm | **−0.07 mm: they overlap** |
| Applicator5 and Applicator6 | 3.13 mm | **−0.04 mm: they overlap** |
| Applicator3 and Applicator4 | 3.21 mm | 0.04 mm |
| Applicator2 and Applicator3 | 3.24 mm | 0.07 mm |
| Applicator9 and Applicator10 | 3.36 mm | 0.19 mm |
| Applicator7 and Applicator8 | 3.41 mm | 0.24 mm |

```
                      Applicator10                   Applicator11
                       (−5.52, 3.41)                  (−6.34, 0.42)
                              ●──────────────────────────────●  centres 3.10 mm apart

threaded holes, 3.17 mm across
              ├───────────────────────────────┤
                                             ├───────────────────────────────┤
                                             ▓▓  ← 0.07 mm of overlap: the holes join

collets, 5.0 mm across
     ├─────────────────────────────────────────────────┤
                                    ├─────────────────────────────────────────────────┤
                                    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ← 1.90 mm of overlap

to scale: one character is 0.1 mm
```

So two threaded holes run into each other, several others have a wall thinner than a tenth of a
millimetre, and **no two collets could be screwed in side by side** anywhere in the ring: every
needle collet ring on Ex2's PDF base map is drawn red ([12.5](#125-the-base-map)). The QA checklist
asks for 6 mm between hole centres. **Nothing in the app warns about any of this.** Ex2 is a test
plan and was probably never meant to be printed, but it shows how easily it can happen.

### 11.11 Things nothing checks

- **Holes that are too close or overlap.** `are_colliding` exists and is never called.
- **Whether the tandem hole runs into a needle hole.**
- **Whether the default tandem settings work.** They do not: 170 on a 160 mm cylinder crashes.
- **Whether the STL is complete.** Six faces were skipped on Ex2, with no message in the app.
- **A needle whose first stretch is shorter than 2.5 mm**, which crashes the tip builder (§7.3 of
  the source of truth).

---

## 12. classes/pdf

**Summary.** `classes/pdf/` writes the **reference sheet**: a PDF that goes with each printed
cylinder, so the clinical team can match every hole to its needle. Page 1 has the patient's
details and a table listing each needle's name, channel number and **interstitial length**, the
length of needle that sticks out beyond the cylinder into tissue. Page 2 has the **base map**, a
drawing of the cylinder's base seen from below, with every hole numbered, the tandem marked, the
notch shown, and optional rings showing whether the collets would collide. To work out each
length, the code takes the needle's first stretch, extends it by the dead space, and finds where
it crosses a cloud of points laid over the cylinder's surface. Needles whose base hole falls
outside the cylinder are silently left off the sheet, and several calculations it makes are never
printed.

[`src/classes/pdf/`](../../src/classes/pdf/) has two files:

| File | Size | Job |
|---|---|---|
| [`template_reference.py`](../../src/classes/pdf/template_reference.py) | 806 lines, 12 functions | works out the numbers, draws the base map, and builds the PDF |
| [`canvas.py`](../../src/classes/pdf/canvas.py) | 66 lines, 1 class | `FooterCanvas`, which stamps "PDF produced on …" and "Page x of y" on every page |

```
 Export tab ── "Export Reference Sheet" ── you choose a file name
        │
        ▼
 generate_pdf()                                          template_reference.py
   ├─ keep the needles that come out of the base ─────── channels_inside_cylinder
   ├─ end every needle exactly at the base (height 0) ── extract_points_from_channels2
   ├─ push each tip out by the dead space ────────────── add_deadspace
   ├─ measure each interstitial length ───────────────── get_all_interstitial_lengths
   ├─ round to centimetres for the table ─────────────── process_lengths_and_create_data
   ├─ draw the base map, saved as basemap.png ────────── save_points_diagram
   └─ build the PDF, with the footer ─────────────────── reportlab + FooterCanvas (canvas.py)
        │
        ▼
 your_file.pdf  +  basemap.png beside it  →  opened in your PDF viewer
```

### 12.1 What the reference sheet looks like

This is the real sheet brachify made for Ex2, with the collet rings switched on. *Verified*, by
running `generate_pdf` on Ex2 and reading the PDF it wrote.

**Page 1:**

```
            Patient Specific Cylindrical Template Reference Sheet

 Date: October 02, 2026
 Patient Name: CYLINDER
 Patient ID: SI_C_D30
 Plan Label: Brachify_Ex2

            ┌──────────────┬────────────────┬───────────────────────┐
            │     Name     │ Channel Number │       Extension       │
            │              │                │ (Interstitial Length) │
            ├──────────────┼────────────────┼───────────────────────┤
            │ Applicator2  │       2        │        2.4 cm         │
            │ Applicator3  │       3        │        2.4 cm         │
            │ Applicator4  │       4        │        2.5 cm         │
            │ Applicator5  │       5        │        2.4 cm         │
            │ Applicator6  │       6        │        2.5 cm         │
            │ Applicator7  │       7        │        1.8 cm         │
            │ Applicator8  │       8        │        1.8 cm         │
            │ Applicator9  │       9        │        1.8 cm         │
            │ Applicator10 │       10       │        2.4 cm         │
            │ Applicator11 │       11       │        2.4 cm         │
            │ Applicator12 │       12       │        2.5 cm         │
            │ Applicator13 │       13       │        2.4 cm         │
            │ Tandem       │       14       │                       │
            └──────────────┴────────────────┴───────────────────────┘

 PDF produced on October 02, 2026 09:50:20                  Page 1 of 2
```

**Page 2** is the base map, described in [12.5](#125-the-base-map), with the same footer.

Where each part comes from:

| Part of the sheet | Comes from |
|---|---|
| Date | the computer's clock when you export |
| Patient Name, Patient ID, Plan Label | `DicomData` from [chapter 10](#10-classesdicom): `patient_name`, `patient_id`, `plan_label` |
| Name, Channel Number | each needle's `label` and `channel_number` |
| Extension (Interstitial Length) | worked out here ([12.4](#124-how-an-interstitial-length-is-measured)) |
| the Tandem row | the label and number of the channel set as the tandem. Its length is always blank |
| the footer | `FooterCanvas` in `canvas.py` |

### 12.2 Words you need

| Word | What it means here | Real example |
|---|---|---|
| **reference sheet** | the PDF that goes with a printed cylinder | `Ex2_reference.pdf` |
| **interstitial length** | how far a needle reaches beyond the cylinder's surface, into tissue, including the dead space | Applicator2: 24.45 mm, printed as 2.4 cm |
| **exit point** | where a needle's path crosses the cylinder's surface on its way out | Applicator2: (0.20, −13.78, 150.93) |
| **point cloud** | many points laid over a surface, here every 0.1 mm over the cylinder's wall and dome, used to find where a needle crosses it | — |
| **base map** | the drawing of the cylinder's base on page 2 | `basemap.png` |
| **collet ring** | a dashed circle on the base map, the size of a collet, drawn around a hole | 5 mm across for needles |
| **reportlab** | the library that builds the PDF | — |
| **matplotlib** | the library that draws the base map | — |

### 12.3 How the sheet is made, step by step

Every value in this section is *Verified*, from running the steps on Ex2.

**In:** the plan's form (`DicomData`), the cylinder, and the needles that are switched on. On
Ex2 that is 12 needles: the `Tandem` channel is switched off automatically when it is set as the
tandem, so it is not one of them.

#### Step 1: keep only the needles that come out of the base

`channels_inside_cylinder` follows each needle down to the base (step 2 below) and keeps it only
if the point where it reaches height 0 is inside the cylinder's radius, 15 mm. On Ex2, **all 12
of 12** are kept, because every base hole is 6.2 to 7.7 mm from the centre. A needle that is dropped
here is **missing from the sheet**, with no message.

#### Step 2: end every needle exactly at the base

`extract_points_from_channels2` makes every needle's list of points finish at height 0, in one
of three ways:

| The needle's last point is | What it does |
|---|---|
| above height 0 | adds a point straight below it, at height 0 |
| below height 0 | finds where the needle crosses height 0, cuts the list there, and ends it with that crossing point |
| exactly at height 0 | leaves it alone |

Applicator2's last point is at height 102.82, above the base, so a 14th point is added straight
below it: **(0.27, −6.55, 0)**. That point is where its hole comes out of the bottom, and it is
what the base map draws.

#### Step 3: push each tip out by the dead space

`add_deadspace` makes a copy of every needle with its tip pushed 6 mm further out
(`CONFIG_DEADSPACE`), the same way the tube builder does ([11.6](#116-channelpy-one-tube-per-needle)).
Applicator2's tip goes from (0.19, −23.20, 166.81) to **(0.19, −26.26, 171.97)**. The original
needles are not changed.

#### Step 4: measure each interstitial length

`get_all_interstitial_lengths`, explained in [12.4](#124-how-an-interstitial-length-is-measured).
Applicator2: **24.45 mm**.

#### Step 5: round for the table

`process_lengths_and_create_data` divides by 10 to get centimetres and rounds to one decimal
place: 24.45 mm → **2.4 cm**. The table has three columns: Name, Channel Number and Extension. A
Tandem row is added at the end if there is a tandem.

#### Step 6: draw the base map

`save_points_diagram`, explained in [12.5](#125-the-base-map). It saves the drawing as
**`basemap.png` in the same folder as the PDF**, replacing any `basemap.png` already there.

#### Step 7: build and open the PDF

reportlab lays out the header, the details, the table and the base map image, and `FooterCanvas`
stamps the footer on every page. On Ex2 the table fills page 1 and the base map goes on page 2.
The PDF is then **opened automatically** in the computer's PDF viewer.

### 12.4 How an interstitial length is measured

The question: how much of the needle is outside the cylinder? The code answers it like this.

```
                                ▲  tip with dead space (0.19, −26.26, 171.97)
                               ╱     ← 6.00 mm of dead space
                              ╱
                             ●  DICOM tip (0.19, −23.20, 166.81)
                            ╱
                           ╱         ← 18.45 mm from the exit point to the DICOM tip
                          ╱
        ─ ─ ─ ─ ─ ─ ─ ─ ─╳─ ─ ─ ─ ─ ─ the cylinder's surface (the dome)
                        ╱  exit point (0.20, −13.78, 150.93)
                       ●  point 2 (0.20, −10.42, 145.28)

        interstitial length = from the exit point to the tip with dead space
                            = 18.45 + 6.00 = 24.45 mm  →  printed as 2.4 cm
```

1. **It lays a point cloud over the cylinder's surface**: rings of points every 0.1 mm up the
   straight wall to height 145, and over the dome to the top.
2. **It takes only the needle's first stretch**, from point 2 to the tip (with the dead space
   added). It assumes the needle leaves the cylinder somewhere along that stretch.
3. **It finds the surface point closest to that stretch.** If one is within **0.25 mm** of the
   stretch, the place on the stretch next to it is the exit point.
4. **The length is the distance from the exit point to the tip.**
5. **If no surface point is within 0.25 mm**, it returns **0**, which the table prints as
   "0.0 cm".

All 12 of Ex2's needles, *Verified*:

| Needle | Channel | Interstitial length | Printed |
|---|---|---|---|
| Applicator2 | 2 | 24.45 mm | 2.4 cm |
| Applicator3 | 3 | 24.47 mm | 2.4 cm |
| Applicator4 | 4 | 24.77 mm | 2.5 cm |
| Applicator5 | 5 | 24.04 mm | 2.4 cm |
| Applicator6 | 6 | 24.75 mm | 2.5 cm |
| Applicator7 | 7 | 17.58 mm | 1.8 cm |
| Applicator8 | 8 | 18.07 mm | 1.8 cm |
| Applicator9 | 9 | 17.74 mm | 1.8 cm |
| Applicator10 | 10 | 24.37 mm | 2.4 cm |
| Applicator11 | 11 | 24.24 mm | 2.4 cm |
| Applicator12 | 12 | 24.75 mm | 2.5 cm |
| Applicator13 | 13 | 24.33 mm | 2.4 cm |

Applicator2's 24.45 mm agrees with the geometry worked out independently in
[11.6](#116-channelpy-one-tube-per-needle): the needle leaves the cylinder 18.46 mm before its DICOM
tip, plus 6 mm of dead space.

Two limits, *Reasoned from code*:

- **Only the first stretch is checked.** A needle that leaves the cylinder further down its path,
  not on the stretch nearest its tip, gets a length of 0.
- **A 0 looks like a real answer.** The sheet prints "0.0 cm" instead of saying the length could
  not be measured.

The code also works out a "protrusion length" for every needle, and **never prints it**. It is
calculated as the dead space minus the needle's whole length, which gives numbers like
−164.9 mm. *Verified*. It was probably meant for a column that was later removed.

### 12.5 The base map

The base map shows the cylinder's base **as seen from below**, looking up. That is how the team
holding the printed cylinder sees it, from its base, where the needles go in. In the code, every
point (x, y) is drawn at (x, −y). So −y, which the code calls **Anterior** (the patient's front),
is at the top of the page, and the notch is drawn there.

On Ex2, with the collet rings switched on, the page shows *Verified*:

```
┌──────────────────────────── Anterior (−y) ────────────────────────────┐
│                                                                       │
│                                 #####                                 │
│                            .....#####.....                            │
│                      ......               ......                      │
│                   ...                           ...                   │
│                ...                                 ...                │
│              ..                                       ..              │
│            ..                                           ..            │
│          ...                                             ...          │
│         ..                                                 ..         │
│        ..                          2                        ..        │
│       ..                   13            3                   ..       │
│      ..                                                       ..      │
│      ..                                       4               ..      │
│     ..               12                                        ..     │
│     ..                                                         ..     │
│     .                                                           .     │
│     .               11           14T  - - -   5                 .     │
│     .                                                           .     │
│     ..                                                         ..     │
│     ..                10                      6                ..     │
│      ..                                                       ..      │
│      ..                                                       ..      │
│       ..                  9              7                   ..       │
│        ..                                                   ..        │
│         ..                        8                        ..         │
│          ...                                             ...          │
│            ..                                           ..            │
│              ..                                       ..              │
│                ...                                 ...                │
│                   ...                           ...                   │
│                      ......               ......                      │
│                            ...............                            │
│                                                                       │
│                                                                       │
└──────────────────────────── Posterior (+y) ───────────────────────────┘
      ^         ^         ^         ^         ^         ^         ^
      -15       -10       -5        0         5         10        15   x (mm)
```

This is a sketch of the layout, not to scale; the exact positions are the `o` holes in the
base-view slice in [11.3](#113-the-whole-model-in-one-picture). On Ex2:

- **Every needle's collet ring is red**, and so is the tandem's 8 mm outer ring. Only the
  tandem's 5 mm inner ring is green. The needles sit about 3 to 4 mm apart and each collet is
  5 mm across, so every collet would hit its neighbours.
- **The notch's rectangle is drawn on top of the word "Anterior"**, so the two overlap on the
  page.

How each part is placed:

| Element | Drawn where | From |
|---|---|---|
| the big circle | radius = the cylinder's radius, 15 mm | the cylinder's diameter |
| each needle hole | at its base point (x, −y), 2.7 mm across, numbered | step 2's last point, `CONFIG_CHANNELS_DIAMETER`, the channel number |
| the tandem | the centre, 3.8 mm across, `14T` | `CONFIG_TANDEM_CHANNEL_DIAMETER`, the tandem channel's number |
| the dashed direction line | from the centre, half the radius long, at the tandem's rotation | only for a generated tandem, not an imported one |
| the notch | a 2 × 2 mm rectangle at the top | the cylinder's notch size |
| the collet rings | only if *Show Collet Spacings* is ticked | `CONFIG_NEEDLE_COLLET_OUTER_DIAMETER` (5), `CONFIG_TANDEM_COLLET_OUTER_DIAMETER_INNER` (5) and `…_OUTER` (8) |
| the numbers' position | inside the circle if the holes are big enough to fit them, otherwise beside it | the hole size compared with the cylinder |

The red-or-green test is simple geometry: two rings overlap when the distance between their
centres is less than the sum of their radii. Rings that share a centre, the tandem's two rings,
are not compared with each other.

### 12.6 Every function

| Function | What it does | Used? |
|---|---|---|
| `generate_pdf` | the whole sheet, steps 1 to 7 | yes, by the Export tab |
| `channels_inside_cylinder` | step 1 | yes |
| `extract_points_from_channels2` | step 2 | yes |
| `add_deadspace` | step 3 | yes |
| `get_all_interstitial_lengths` | step 4, with its own point cloud, crossing test and length inside it | yes |
| `process_lengths_and_create_data` | step 5 | yes |
| `save_points_diagram` | step 6, the base map | yes |
| `calculate_protrusion_lengths` | the protrusion lengths that are never printed | called, result unused |
| `extract_points_from_channels` | an older version of step 2 | **no** |
| `get_last_xy_points` | — | **no** |
| `get_point_at_z0` | an older version of step 2, which would crash if called: it unpacks each point as two values | **no** |
| `index_before_negative_point` | — | **no**: its only call is commented out |
| `FooterCanvas` (`canvas.py`) | the footer on every page: "PDF produced on …" on the left, "Page x of y" on the right | yes |

### 12.7 What happens if a setting changes

The table's numbers, recalculated with one setting changed at a time. *Verified*:

| Change | Needles on the sheet | Applicator2 | Applicator7 | Means |
|---|---|---|---|---|
| none: dead space 6, diameter 30 | 12 | 24.45 mm, 2.4 cm | 17.58 mm, 1.8 cm | — |
| Dead Space **0** | 12 | 18.45 mm, 1.8 cm | 11.58 mm, 1.2 cm | every length drops by exactly 6 mm |
| Dead Space **10** | 12 | 28.45 mm, 2.8 cm | 21.58 mm, 2.2 cm | every length grows by exactly 4 mm |
| Cylinder Diameter **25** | 12 | 27.06 mm, 2.7 cm | 19.29 mm, 1.9 cm | a thinner cylinder: the needles leave it sooner, so more of them is outside |
| Cylinder Diameter **13** | **4** | **not on the sheet** | **not on the sheet** | 8 needles' base holes are now outside the 6.5 mm radius, so they are **silently left off** |
| Cylinder Length 160 → **140** | 12 | 24.45 mm, 2.4 cm | 17.58 mm, 1.8 cm | unchanged: the needles and the dome move down together |

### 12.8 Things nothing checks

- **Needles left off the sheet.** A needle whose base hole falls outside the cylinder is dropped
  from the table and the map, with no message.
- **A length that could not be measured.** It prints as "0.0 cm", the same as a real zero.
- **Colliding collets.** The red rings are the only sign, they are optional, and nothing stops
  the export.
- **The file left beside the PDF.** `basemap.png` is written next to every PDF and replaces any
  file already called that.
- **Existing copy that breaks the project's writing rule.** The labels "Date:", "Patient Name:",
  "Patient ID:" and "Plan Label:" use colons, which AGENTS.md's UI copy rule forbids in new text.
  The rule records them as existing copy, to be fixed in their own pull request.

---

## 13. src/settings

**Summary.** `src/settings/` looks after brachify's **settings**: the 19 numbers, all named
`CONFIG_…`, that say how big to make the cylinder, the needle holes, the tandem and the collet
rings. `defaults.py` lists the built-in starting values. When the app starts, `values.py` looks
in `~/brachify/filepaths.json` for the settings file you used last, and `load.py` reads it,
keeping every value that is present and is a number, and filling the rest from the defaults. The
result is one shared collection of settings, `get_app().values.config_values`, that the whole app
reads, and that the *Apply* buttons write back into. `reset.py` moves settings in both
directions: into the tabs' number boxes when you import a settings file, and back out of the app
when you export one. The checks are thin: a file can set a diameter to −3, the collar settings
are lost on every export and import, and on a first start the live settings are the very same
object as the built-in defaults, so changing one changes the other.

[`src/settings/`](../../src/settings/) has four files:

| File | Size | Job |
|---|---|---|
| [`defaults.py`](../../src/settings/defaults.py) | 21 lines | `DEFAULT_CONFIG_VALUES`: the 19 settings and their built-in values |
| [`values.py`](../../src/settings/values.py) | 121 lines | `Values`: holds the live settings, finds the last settings file on start-up, writes the "what was loaded" message |
| [`load.py`](../../src/settings/load.py) | 84 lines | `load_config_file`: reads one settings file and fills in what is missing |
| [`reset.py`](../../src/settings/reset.py) | 163 lines | `resetAllValues`: settings → the tabs' boxes. `getCurrentValues`: the app → settings, for export |

```
 defaults.py: DEFAULT_CONFIG_VALUES, the 19 settings and their built-in values
                   │
                   ▼
 app starts ──▶ Values()                                          (values.py)
                 ├─ read ~/brachify/filepaths.json: "the last settings file was …"
                 └─ load_config_file(that file, the defaults)     (load.py)
                        ├─ found and readable  → keep its numbers, fill the rest from the defaults
                        └─ none, or unreadable → use the defaults
                                 │
                                 ▼
             get_app().values.config_values     the one shared collection of settings
                    │                ▲
                    │ read by        │ written by
                    │ every tab,     │ every tab's Apply button
                    │ the 3D code,   │
                    │ the PDF        │
                    ▼                │

 Import Config File  ─▶ load_config_file ─▶ resetAllValues ─▶ the tabs' number boxes    (reset.py)
 Export Current Settings as Config ◀── getCurrentValues ◀── the app's models            (reset.py)
 closing the window  ─▶ ~/brachify/filepaths.json: remembers which file to load next time
```

### 13.1 Words you need

| Word | What it means here | Real example |
|---|---|---|
| **setting** | one named number that controls part of the design | `CONFIG_CYLINDER_DIAMETER` = 30.0 |
| **default** | the value a setting has when nothing else is given | 30.0 for the cylinder's diameter |
| **dictionary** | Python's name for a collection of **key → value** pairs: look up a key, get its value | `{"CONFIG_CYLINDER_DIAMETER": 30.0, …}` |
| **key** | the name you look a value up by | `"CONFIG_CYLINDER_DIAMETER"` |
| **JSON** | a plain-text file format for exactly this kind of key → value list | `{"CONFIG_CYLINDER_DIAMETER": 30.0}` |
| **settings file** (the code says **config file**) | a JSON file of settings, made with *Export Current Settings as Config* and read with *Import Config File* | `my_settings.json` |
| **spin box** | a number box on a tab, with little up and down arrows | *Cylinder Diameter* on the Cylinder tab |
| **live settings** | the one collection of settings the running app uses: `get_app().values.config_values` | — |
| **the same object** | two names that point at one single thing in memory, so changing it through either name changes it for both | see [13.4](#134-valuespy-the-live-settings) |

### 13.2 The 19 settings

Every setting, its built-in value, and the box on screen that shows it. *Verified* against
`defaults.py` and the code that fills each box. All lengths are in millimetres.

| Setting | Default | What it controls | Box on screen | Used in |
|---|---|---|---|---|
| `CONFIG_CYLINDER_DIAMETER` | 30.0 | the cylinder's width | Cylinder tab, *Cylinder Diameter* | [11.5](#115-cylinderpy-and-notchpy-the-solid-cylinder) |
| `CONFIG_CYLINDER_LENGTH` | 160.0 | the cylinder's height | Cylinder tab, *Cylinder Length* | [10.5](#105-fileiopy-how-the-form-gets-filled), [11.5](#115-cylinderpy-and-notchpy-the-solid-cylinder) |
| `CONFIG_BASE_HEIGHT` | 0.0 | the collar's height. 0 means no collar | Cylinder tab, *Collar Height* | [11.5](#115-cylinderpy-and-notchpy-the-solid-cylinder) |
| `CONFIG_BASE_THICKNESS` | 0.0 | the collar's thickness. 0 means no collar | Cylinder tab, *Collar Thickness* | [11.5](#115-cylinderpy-and-notchpy-the-solid-cylinder) |
| `CONFIG_CHANNELS_DIAMETER` | 2.7 | every needle hole's width | Channels tab, *Channels Diameter* | [11.6](#116-channelpy-one-tube-per-needle) |
| `CONFIG_DEADSPACE` | 6.0 | how far each needle tip is pushed out | Channels tab, *Dead Space* | [11.6](#116-channelpy-one-tube-per-needle), [12.4](#124-how-an-interstitial-length-is-measured) |
| `CONFIG_CHANNELS_THREADING_DEPTH` | 5.0 | how deep the threaded hole for each needle's collet goes. 0 means none | Channels tab, *Threading Depth* | [11.6](#116-channelpy-one-tube-per-needle) |
| `CONFIG_CHANNELS_THREADING_DIAMETER` | 3.17 | the threaded hole's width. 0 means none | Channels tab, *Threading Diameter* | [11.6](#116-channelpy-one-tube-per-needle) |
| `CONFIG_TANDEM_TIP_HEIGHT` | 170.0 | where the tandem's bend starts | Tandem tab, *Tandem Height* | [11.7](#117-tandempy-the-tandem) |
| `CONFIG_TANDEM_CHANNEL_DIAMETER` | 3.8 | the tandem hole's width | Tandem tab, *Channel Diameter* | [11.7](#117-tandempy-the-tandem) |
| `CONFIG_TANDEM_STOPPER_DIAMETER` | 5.0 | the tandem's stopper section | Tandem tab, *Stopper Diameter* | [11.7](#117-tandempy-the-tandem) |
| `CONFIG_TANDEM_TIP_ANGLE` | 30 | how far the tandem bends, in degrees | Tandem tab, *Bend Angle* | [11.7](#117-tandempy-the-tandem) |
| `CONFIG_TANDEM_BEND_RADIUS` | 35.0 | how tight the bend is | Tandem tab, *Bend Radius* | [11.7](#117-tandempy-the-tandem) |
| `CONFIG_TANDEM_ROTATION` | 0.0 | which way around the cylinder the tandem bends, in degrees | Tandem tab, *Rotation* (on both sub-tabs) | [11.7](#117-tandempy-the-tandem) |
| `CONFIG_TANDEM_THREADING_DEPTH` | 7.0 | how deep the tandem's threaded hole goes | Tandem tab, *Threading Depth* | [11.7](#117-tandempy-the-tandem) |
| `CONFIG_TANDEM_THREADING_DIAMETER` | 5.0 | the tandem's threaded hole's width | Tandem tab, *Threading Diameter* | [11.7](#117-tandempy-the-tandem) |
| `CONFIG_NEEDLE_COLLET_OUTER_DIAMETER` | 5.0 | the needle collet ring on the PDF | Export tab, *Needle Collet Spacing Tol.* | [12.5](#125-the-base-map) |
| `CONFIG_TANDEM_COLLET_OUTER_DIAMETER_INNER` | 5.0 | the tandem's inner collet ring on the PDF | Export tab, *Tandem Inner Spacing Tol.* | [12.5](#125-the-base-map) |
| `CONFIG_TANDEM_COLLET_OUTER_DIAMETER_OUTER` | 8.0 | the tandem's outer collet ring on the PDF | Export tab, *Tandem Outer Spacing Tol.* | [12.5](#125-the-base-map) |

Two things are **not** settings, so they are never saved or loaded: whether the *Add Collar* box
is ticked, and the *Height Offset* of an imported tandem.

### 13.3 `defaults.py`, the built-in values

[`defaults.py`](../../src/settings/defaults.py) holds one dictionary, `DEFAULT_CONFIG_VALUES`, with
the 19 settings in the table above. It has no functions. It is the **list of which settings
exist**: `load.py` goes through its keys to decide what to look for in a settings file.

Adding a new setting means changing **four** places, which is easy to get wrong
(§6.2 of the source of truth):

```
 1  defaults.py          add the key and its built-in value
 2  reset.py, resetAllValues     put the value into its box on import
 3  reset.py, getCurrentValues   read it back out on export
 4  the tab's own code           fill the box when the app starts
```

The two collar settings show what happens when places 2 and 3 are missed ([13.6](#136-resetpy-into-the-boxes-and-back-out)).

### 13.4 `values.py`, the live settings

[`values.py`](../../src/settings/values.py) defines one class, `Values`. The app makes one
`Values` when it starts ([9.7](#97-apppy-the-application-object)), and every file reaches it as
`get_app().values`.

#### What it holds

| Attribute | Holds | Example on a first start |
|---|---|---|
| `config_values` | **the live settings**: a dictionary of all 19, and any extra keys a settings file brought with it | `{"CONFIG_CYLINDER_DIAMETER": 30.0, …}` |
| `config_keys_loaded` | two lists: the settings that came from the file, and the ones that did not | `[[], [all 19 names]]` |
| `most_recently_opened_config_file` | the path of the last settings file imported | `None` |
| `most_recently_saved_config_file` | the path of the last settings file exported. Saved, but never used | `None` |
| `num_configs_loaded_successfully` | how many settings files have given at least one value. Counted, but never used | `0` |
| `loaded_message` | the text shown on the Import tab about which settings were loaded | see below |
| `DEFAULT_CONFIG_VALUES` | the built-in values, from `defaults.py` | — |

#### What happens when it is made

| Order | What it does |
|---|---|
| 1 | sets every attribute to empty |
| 2 | `readConfigFilePaths()`: opens `~/brachify/filepaths.json` and reads which settings file was last imported. No file, or an unreadable one, means "none" |
| 3 | `load_config_file(that file, the defaults)` ([13.5](#135-loadpy-reading-a-settings-file)) |
| 4 | stores the result in `config_values` and `config_keys_loaded` |

#### The live settings are the defaults themselves, on a first start

When no settings file is found, `load_config_file` hands back the defaults dictionary **itself**,
not a copy. So `config_values` and `DEFAULT_CONFIG_VALUES` become two names for the same object.
*Verified*:

```
 first start, no filepaths.json
        │
        ▼
 config_values ─────────┐
                        ├──▶  one dictionary in memory:  {"CONFIG_CYLINDER_DIAMETER": 30.0, …}
 DEFAULT_CONFIG_VALUES ─┘

 you press Apply with diameter 25
        │
        ▼
 config_values["CONFIG_CYLINDER_DIAMETER"] = 25
        └─▶ DEFAULT_CONFIG_VALUES["CONFIG_CYLINDER_DIAMETER"] is now 25 as well
```

In the test, setting the live diameter to 25 changed `DEFAULT_CONFIG_VALUES` to 25 too. The
same happens when the settings file is broken or missing. Nothing in the app today reads the
defaults' values again after start-up, so nothing visibly goes wrong yet. But the built-in
defaults stop being the defaults the moment you change anything, and any future "reset to
defaults" feature would quietly reset to your current values instead. *Reasoned from code* for
the consequence.

#### The message on the Import tab

`createConfigMessageText` writes the text that the Import tab shows, listing which settings came
from the file and which did not. Each name is shortened for reading: `CONFIG_` is removed,
underscores become spaces, and each word gets a capital letter, so
`CONFIG_CYLINDER_DIAMETER` becomes *Cylinder Diameter*. On a first start, *Verified*:

```
Config file currently loaded:
None

The following values were successfully loaded from the config file:
None

The following values were not found in the config file:
(Default values used instead.)
Cylinder Diameter   =   30.0
Cylinder Length   =   160.0
…
```

After an import, the bracketed line says "(Previous values used instead.)".

### 13.5 `load.py`, reading a settings file

[`load.py`](../../src/settings/load.py) has two functions.

#### `load_config_file(file, fallback, count)`

```
 load_config_file(file, fallback)
        │
        ├─ no file given ─────────────▶ return the fallback itself; all 19 "not found"
        │
        ├─ the file cannot be opened,
        │  or is not valid JSON ──────▶ return the fallback itself; all 19 "not found"
        │
        └─ the file is read
               │
               ▼
          checkValuesExist: for each of the 19 settings
               ├─ in the file AND a number  → keep the file's value     → "loaded"
               └─ missing, or not a number  → use the fallback's value  → "not found"
               │
               ▼
          return the file's dictionary, with the gaps filled in.
          Keys the file has that are not settings are kept, and ignored
```

The **fallback** is the defaults when the app starts, and the **current live settings** when
you import a file part-way through a session. So a mid-session import only changes the settings
the file actually contains. *Verified*: with the live cylinder length at 140, importing a file
that only sets the diameter to 35 gave diameter 35 and length 140.

#### `checkValuesExist(file's values, lists, fallback)`

It decides, setting by setting, whether to trust the file. **Its only test is "is it a
number?"**. *Verified*, with a settings file holding a mix of values:

| In the file | Kept? | The app then uses | Why |
|---|---|---|---|
| `"CONFIG_CYLINDER_DIAMETER": 25` | yes | 25 | a number |
| `"CONFIG_CYLINDER_LENGTH": "150"` | **no** | 160.0, the default | text in quotes is not a number, even if it looks like one |
| `"CONFIG_DEADSPACE": true` | **yes** | `True` | in Python, true counts as the number 1 |
| `"CONFIG_CHANNELS_DIAMETER": -3.0` | **yes** | −3.0 | a number. There is no check that it makes sense |
| `"CONFIG_TANDEM_ROTATION": 0` | yes | 0 | a number |
| `"MY_NOTE": "hello"` | kept, ignored | `"hello"` | not a setting. It stays in the live settings, so they then hold 20 keys |
| (the other 14 settings) | not found | the defaults | missing from the file |

A file that is not valid JSON, or that does not exist, is treated as no file at all: every
setting comes from the fallback. *Verified*.

`load.py` also has a module-level `config_values = None` that nothing uses: the function keeps
its own `config_values` inside it.

### 13.6 `reset.py`, into the boxes and back out

[`reset.py`](../../src/settings/reset.py) has two functions that move settings in opposite
directions.

```
 settings  ──resetAllValues──▶  the tabs' number boxes        (when you import a settings file)
 the app   ──getCurrentValues──▶  settings                    (when you export, and in the Tandem tab)
```

#### `resetAllValues(settings)`: settings → the boxes

Called by *Import Config File*, after `load_config_file`. Tab by tab:

| Tab | Boxes it fills | Then |
|---|---|---|
| Cylinder | *Cylinder Diameter*, *Cylinder Length* | presses *Apply Settings* for you, if a cylinder already exists |
| Channels | *Channels Diameter*, *Dead Space*, *Threading Depth*, *Threading Diameter* | presses *Apply* for you |
| Tandem | *Tandem Height*, *Channel Diameter*, *Stopper Diameter*, *Bend Angle*, *Bend Radius*, both *Rotation* boxes, and the tandem model's values | regenerates the tandem, if a generated one exists. An imported tandem is left alone |
| Export | the three collet boxes | — |

It **does not fill the two collar boxes**, *Collar Height* and *Collar Thickness*. *Reasoned from
code*. Worse, the Cylinder tab's *Apply Settings*, which `resetAllValues` presses, reads the collar
values back **from the boxes** and writes them into the live settings, so a collar value just
imported from a file is replaced by whatever the boxes showed before.

#### `getCurrentValues()`: the app → settings

Called by *Export Current Settings as Config*, and by the Tandem tab's *Generate Tandem*. It
reads each value from the app's models and boxes, and returns a dictionary. *Verified*, with a
stand-in window supplying the values:

- **It returns 17 of the 19 settings.** `CONFIG_BASE_HEIGHT` and `CONFIG_BASE_THICKNESS`, the
  collar, are missing. This is bug §7.1 in the source of truth.
- **It crashes if there is no cylinder yet**, with `'NoneType' object has no attribute
  'diameter'`, because it reads the diameter from the cylinder object. So pressing *Export
  Current Settings as Config* before importing a plan or pressing *Apply Settings* fails.

#### Why the collar can never be saved or loaded

Putting those together, *Verified* for the export and import steps and *Reasoned from code* for
the rest:

```
 you set a collar: height 12, thickness 3, and press Apply
        │
        ▼
 Export Current Settings ──▶ getCurrentValues ──▶ my_settings.json has 17 settings: NO collar
        │
        ▼
 later, Import Config File my_settings.json
        ├─ load_config_file: the collar is "not found" → the current values are kept
        └─ resetAllValues: the collar boxes are not touched
        │
        ▼
 the collar comes from whatever the app had before, never from the file

 and on Generate Tandem:
 the Tandem tab replaces the whole live settings with getCurrentValues()
        └─▶ the collar settings disappear from the live settings
            → the cylinder already built keeps its collar, and the next Apply
              writes the settings back from the boxes (17.4, and §7.1 of the source of truth)
```

### 13.7 The two files on disk

**A settings file**, as *Export Current Settings as Config* writes it. *Verified*, the start of a
real export:

```
{
"CONFIG_CYLINDER_DIAMETER": 30.0,
"CONFIG_CYLINDER_LENGTH": 160.0,
"CONFIG_CHANNELS_DIAMETER": 2.7,
…
}
```

It holds 17 settings, one per line. You choose where it is saved.

**`~/brachify/filepaths.json`**, which the window writes every time it closes
(`MainWindow.save_file_paths`):

```
{
"most_recently_opened_config_file": "/path/to/my_settings.json",
"most_recently_saved_config_file": "/path/to/exported.json"
}
```

The next time the app starts, `Values` reads the first line to know which settings file to load.
The second line is saved and never used.

```
 import my_settings.json ──▶ most_recently_opened_config_file = it
 close the window        ──▶ filepaths.json written
 start the app again     ──▶ Values reads filepaths.json ──▶ loads my_settings.json again
```

The path is remembered even if the file turned out to be unreadable, so the app tries the same
file again on every start until another one is imported.

### 13.8 What happens if something here changes

| Change | What happens | How sure |
|---|---|---|
| no `filepaths.json` (a first start) | the defaults are used, and the live settings are the defaults dictionary itself | *Verified* |
| the remembered settings file was deleted | the defaults are used, with no message beyond the Import tab's "None" | *Verified* |
| the settings file is not valid JSON | the defaults are used | *Verified* |
| a setting written as text, like `"150"` | ignored: the default is used | *Verified* |
| a setting written as `true` | accepted, as 1 | *Verified* |
| a negative or zero setting, like a −3 mm hole | accepted, with no check | *Verified* |
| an unknown key in the file | kept in the live settings, never used | *Verified* |
| import a file with only some settings | only those change. The rest keep their current values | *Verified* |
| a value outside a box's limits, like a 400 mm cylinder (the box allows 60 to 300) | the box shows its limit, while the live settings may still hold 400 until *Apply* is pressed | *Reasoned from code*. Qt silently limits a box's value |
| export before any cylinder exists | crashes, and no file is written | *Verified* for the crash |
| export, then import, with a collar set | the collar is lost | *Verified* for the missing keys |

### 13.9 Things nothing checks

- **Whether a setting makes sense.** A −3 mm hole, a 0 mm cylinder, or `true` as a length all
  load. Only "is it a number" is checked.
- **That the defaults stay the defaults.** On a first start, changing a setting changes the
  built-in default too.
- **That the collar survives.** It is missing from the export, ignored by the import, and dropped
  by *Generate Tandem*.
- **That a cylinder exists before export.** Exporting settings first crashes.
- **That the remembered file still works.** A broken settings file is retried on every start.
- **Existing copy that breaks the project's writing rule.** The Import tab message uses colons,
  such as "Config file currently loaded:", which AGENTS.md's UI copy rule forbids in new text.

---

## 14. src/windows

**Summary.** `src/windows/` is everything you see on screen. Directly in the folder are two
files. `main_window.py` defines `MainWindow`, the app's one window: it builds the window from its
design file, wires the five tab buttons on the left so each one switches the page and colours
itself dark, creates the five **models** that hold the app's data and connects them together,
adds the 3D view, and holds every pop-up message the app can show, from "No central axis found"
to "Your PDF was not saved". When the window closes, it saves `~/brachify/filepaths.json` so the
next start knows which settings file to load. `palettes.py` defines a dark and a light colour
theme that nothing uses. The rest of the folder, the models, the tabs, the 3D view and the design
files, lives in four subfolders not covered in this document yet.

[`src/windows/`](../../src/windows/) holds two files and four folders:

| Item | Size | What it is |
|---|---|---|
| [`main_window.py`](../../src/windows/main_window.py) | 350 lines | `MainWindow`: the window, the tab buttons, the models, the 3D view, every pop-up message |
| [`palettes.py`](../../src/windows/palettes.py) | 96 lines | `Palettes`: a dark and a light colour theme. **Never used** |
| [`models/`](../../src/windows/models/) | folder | the six models: the app's data, with no buttons or boxes. Not covered yet |
| [`views/`](../../src/windows/views/) | folder | the five tabs and the 3D view. Not covered yet |
| [`ui/`](../../src/windows/ui/) | folder | the design files made in Qt Designer, and the Python made from them. Not covered yet |
| [`splashscreen/`](../../src/windows/splashscreen/) | folder | the picture shown while the `.exe` loads |

### 14.1 Words you need

| Word | What it means here | Real example |
|---|---|---|
| **window** | the app's main window: the frame with the tab buttons, the tab pages and the 3D view | `MainWindow` |
| **widget** | anything drawn in the window: a button, a number box, a panel, the 3D view | `btn_import_view` |
| **layout** | the invisible arrangement that places widgets inside a panel, in a row or a column | the column of tab buttons |
| **design file** (`.ui`) | the window's layout, drawn in a tool called Qt Designer and saved as a file. Python code is generated from it | `windows/ui/main_window.ui` |
| **model** | a part of the app that holds data and announces changes, with no widgets of its own | `CylinderModel` holds the cylinder |
| **view** (here, a **tab**) | a page of widgets that shows a model and lets you change it | the Cylinder tab |
| **pop-up message** (Qt calls it a **message box**) | a small window that tells you something and waits for you to press a button | "No central axis found." |
| **stylesheet** | CSS-like text that sets a widget's colours and borders | `background-color: rgb(28, 44, 81);` |
| **palette** | a set of colours Qt uses for a whole window when no stylesheet overrides them | `Palettes.dark` |
| **signal**, **connect** | an announcement, and attaching a function to it ([9.6](#96-signalspy-app-wide-announcements)) | `btn_import_view.pressed` |

### 14.2 What the window is made of

The window as you see it, with each part's name in the code. *Verified* sizes, from building the
real window: 770 × 472 pixels when it opens.

```
 ┌─────────────────────────────── brachify ──────────────────────────────┐
 │ ┌───────────────────────┐ ┌─────────────────────────────────────────┐ │
 │ │ [ Import   ]          │ │                                         │ │
 │ │ [ Cylinder ]          │ │                                         │ │
 │ │ [ Channels ]          │ │                                         │ │
 │ │ [ Tandem   ]          │ │           the 3D view                   │ │
 │ │ [ Export   ]          │ │           display_view_widget           │ │
 │ │   top_menu_bar        │ │           holds OrbitCameraViewer3d     │ │
 │ ├───────────────────────┤ │                                         │ │
 │ │                       │ │                                         │ │
 │ │  the current tab      │ │                                         │ │
 │ │  viewswidget:         │ │                                         │ │
 │ │  5 pages, one shown   │ │                                         │ │
 │ │  at a time            │ │                                         │ │
 │ │                       │ │                                         │ │
 │ └───────────────────────┘ └─────────────────────────────────────────┘ │
 └───────────────────────────────────────────────────────────────────────┘
```

| Part | Name in the code | What it holds |
|---|---|---|
| the five tab buttons | `btn_import_view`, `btn_cylinder_view`, `btn_channels_view`, `btn_tandem_view`, `btn_export_view` | labels *Import*, *Cylinder*, *Channels*, *Tandem*, *Export*. Each is 290 × 33 pixels |
| the panel around them | `top_menu_bar` | the column of five buttons |
| the tab pages | `viewswidget` | five pages, `page_import` to `page_export`, of which one is shown at a time |
| the 3D view | `display_view_widget` | the OpenCASCADE viewer, added when the window is built |

All of this comes from the design file
[`windows/ui/main_window.ui`](../../src/windows/ui/main_window.ui), turned into Python by a tool
called `pyside6-uic`. The window's code creates it with `self.ui = Ui_MainWindow()` and
`self.ui.setupUi(self)`, and then reaches every part as `self.ui.<name>`.

### 14.3 `main_window.py`, building the window

`MainWindow` is built in three steps, called one after another by `app.gui()`
([9.7](#97-apppy-the-application-object)). They are separate on purpose: the models and tabs reach
the window through `get_app().window`, which only exists once the first step has finished.

```
 app.gui()
   │
   ├─ 1  MainWindow()       __init__     the widgets from the design file; wire the 5 tab buttons
   │                                     ← only now does get_app().window exist
   ├─ 2  initModels()                    create the 5 models and connect them
   │
   └─ 3  initViews()                     the 3D view; the 5 tabs; show the window
```

*Verified*, building the real window: after step 1 there are no models and no 3D view yet, and
after step 2 the five models exist.

#### Step 1: `__init__`, the widgets and the tab buttons

| Order | What it does |
|---|---|
| 1 | `super().__init__(*args)`: Qt's own window set-up |
| 2 | `self.initialized = False`, set to `True` at the end of step 3 |
| 3 | logs "Starting main window initialization" |
| 4 | `self.ui = Ui_MainWindow()` and `self.ui.setupUi(self)`: builds every widget from the design file |
| 5 | connects each tab button to **two** functions: one that switches the page, one that recolours the buttons |

Each tab button, when **pressed** (the moment the mouse button goes down):

```
 btn_import_view pressed ──┬──▶ viewChanged.emit(0) ──▶ NavigationModel.set_page(0)   switch to page 0
                           └──▶ change_color_import()                                 recolour the buttons

 the same for Cylinder (1), Channels (2), Tandem (3) and Export (4)
```

The numbers 0 to 4 are the tabs' positions. They must match the order of the pages in the design
file and the order the tabs are created in `NavigationModel`, and nothing checks that they do.

#### The five colour functions

`change_color_import`, `change_color_cylinder`, `change_color_channels`, `change_color_tandem`
and `change_color_export` each give every tab button a **stylesheet**: the pressed one dark, the
other four light. *Verified*, by calling them on the real window:

| | Background | Text | When the mouse is over it |
|---|---|---|---|
| the selected button | `rgb(28, 44, 81)`, dark navy | white | — |
| the other four | `rgb(199, 219, 237)`, light blue | black | `rgb(48, 88, 162)`, mid blue, white text |

| Moment | Import | Cylinder | Channels | Tandem | Export |
|---|---|---|---|---|---|
| the window opens | **dark** | light | light | light | light |
| after pressing Channels | light | light | **dark** | light | light |
| after pressing Export, **before** any plan is imported | light | light | **dark** | light | light |
| after pressing Export, after a plan is imported | light | light | light | light | **dark** |

`change_color_export` only recolours once a plan has been imported. Before that, pressing Export
leaves the old button highlighted. After a successful import, the Import tab calls
`change_color_export()` itself, because it switches you to the Export tab.

The five functions are near-copies of each other, about 23 lines each, differing only in which
button turns dark. One function taking the button as a value would replace all five (§5.6 of the
source of truth calls this the most obvious tidy-up in the window code).

#### Step 2: `initModels`, the five models and their connections

```
 initModels()
   ├─ displaymodel  = DisplayModel()     what the 3D view shows, and in which colours
   ├─ dicommodel    = DicomModel()       the imported plan (chapter 10)
   ├─ cylindermodel = CylinderModel()    the cylinder (chapter 11)
   ├─ channelsmodel = ChannelsModel()    the needles (chapter 11)
   ├─ tandemmodel   = TandemModel()      the tandem (chapter 11)
   │
   ├─ dicommodel.values_changed ──┬──▶ cylindermodel.load_data      a new plan → a new cylinder
   │                              └──▶ channelsmodel.load_data      a new plan → new needles
   │
   └─ app.signals.height_changed ─┬──▶ channelsmodel.update_height_offset   cylinder length changed
                                  └──▶ tandemmodel.update_height_offset
```

A sixth model, `NavigationModel`, which owns the five tabs, is made in step 3.

#### Step 3: `initViews`, the 3D view, the tabs, and showing the window

| Order | What it does |
|---|---|
| 1 | creates the 3D view, `OrbitCameraViewer3d`, and puts it in `display_view_widget` |
| 2 | starts the 3D engine (`InitDriver`), draws the small x–y–z axes in the corner (`display_triedron`), and zooms to fit |
| 3 | connects `displaymodel.shapes_changed` to the 3D view, so every change of shapes redraws it |
| 4 | creates `NavigationModel`, which creates the five tabs in a fixed order and puts each in its page |
| 5 | `showWithCanvas()`: shows the window |
| 6 | `self.initialized = True`, and logs "main window initialization complete" |

`showWithCanvas` shrinks the window by 1 pixel, shows it, and sets it back to its size. The
comment says this makes the 3D view fit its panel properly: changing the size makes Qt lay the
window out again once the 3D view is in it.

This step is where the app stops when there is no screen. *Verified*: `__init__` and
`initModels` both work without a screen, and the process is killed after them, while the 3D view
starts, because the 3D engine needs a real display ([8.3](#83-when-starting-fails)).

#### Every pop-up message

Every message the app can show is a function on `MainWindow`, so any part of the code can show
one with `get_app().window.<name>()`. Each one builds a message box, sets its text, title and
icon, and waits for you to press OK. *Verified*: every text below was read from the real message
box. The titles come from the code: on macOS Qt does not show a message box's title, and in the
test it came back empty.

| Function | Icon | Title (from the code) | Message, shortened | Shown by |
|---|---|---|---|---|
| `no_central_axis_or_cylinder_outline` | warning | Central Axis Missing | "Error: No central axis found. Please ensure your model has a channel labeled "central axis". …" | DICOM import ([10.5](#105-fileiopy-how-the-form-gets-filled)) |
| `single_point_pop_up_Varian` | warning | Channel with Single Point Detected | "Warning, at least one channel with a single point was detected, this point WILL NOT be included in the 3D model." | Varian import |
| `single_point_pop_up_Nucleatron` | warning | Multiple Anchoring Points | "Warning: at least two of your channels contain only a single point. …" | Oncentra import |
| `channel_display_warning` | warning | Warning | "Warning thrown while constructing needle channels. Please inspect the export view …" | the tube builder ([11.6](#116-channelpy-one-tube-per-needle)), the PDF |
| `channel_display_error` | **critical** | Warning | "Error thrown while constructing channels. …" | the tube builder |
| `tandem_import_wrong_filetype_error` | warning | Tandem Import Error | "Please use a step file if importing a tandem." | importing a tandem that is not STEP |
| `tandem_error(code)` | warning | one of five, such as "Tandem Height Error - Tandem Height Set to Previous Value" | "Error: The input for tandem height is too large or too small. Tandem height reset to previous value." | generating a tandem with a value that fails |
| `tandem_rotation_warning` | warning, with **Yes** and **No** | Rotation Changed from DICOM value | "The inputted tandem rotation angle is different than the imported DICOM file tandem rotation angle. Do you wish to continue?" | changing the tandem's rotation away from the plan's |
| `pdf_save_error` | warning | PDF save error | "Your PDF was not saved, this may be because a pdf with the same name is open in another application. …" | exporting the reference sheet |

`tandem_error` takes a short code that says which value failed: `"diam"`, `"stopper"`,
`"angle"`, `"height"` or `"radius"`. Those are the only five codes the tandem model sends, but if
any other code were passed, the box would appear **empty**. *Verified*.

`tandem_rotation_warning` is the only one with a choice. Pressing **No** puts the rotation back to
the plan's value, in the model and in both *Rotation* boxes, and returns "No". Pressing **Yes**
returns nothing at all, not "Yes"; the code that calls it only checks for "No", so this works.
*Verified* for No.

#### When the window closes

```
 you close the window
        │
        ▼
 closeEvent()  →  save_file_paths()
        │
        ▼
 ~/brachify/filepaths.json  ←  { "most_recently_opened_config_file": …,
                                 "most_recently_saved_config_file": … }
```

*Verified*, on a fresh start with no settings file used, the file written was:

```
{
"most_recently_opened_config_file": null,
"most_recently_saved_config_file": null
}
```

`null` is JSON's word for "nothing". The next start reads this file to decide which settings
file to load ([13.4](#134-valuespy-the-live-settings)).

`closeEvent` replaces Qt's own close handler without calling it. Qt accepts a close by default,
so the window still closes. *Reasoned from code.*

### 14.4 `palettes.py`, two themes nothing uses

[`palettes.py`](../../src/windows/palettes.py) defines one class, `Palettes`, with two functions,
`dark(window)` and `light(window)`. Each builds a **palette**, a full set of colours for every
kind of widget, and applies it to a window. *Verified*: nothing in `src/` uses `Palettes`. The
window's colours come from the stylesheets in the design file and in the colour functions above.

| Part of a widget | Dark theme | Light theme |
|---|---|---|
| window background | `rgb(53, 53, 53)` | `rgb(240, 240, 240)` |
| text | `rgb(180, 180, 180)` | `rgb(0, 0, 0)` |
| button | `rgb(53, 53, 53)` | `rgb(240, 240, 240)` |
| selected item | `rgb(42, 130, 218)` | `rgb(76, 163, 224)` |
| disabled text | `rgb(127, 127, 127)` | `rgb(115, 115, 115)` |

`dark` is marked as a function of the class (`@staticmethod`); `light` is not. So
`Palettes.light(window)` works, but `Palettes().light(window)`, called on an object, would pass
the wrong value as `window`. *Reasoned from code.* Despite its place next to the palettes in
AGENTS.md, [`notes/style guide.txt`](../../notes/style%20guide.txt) is about Python's naming rules,
not colours ([4.2](#42-where-the-notes-have-gone-stale)).

### 14.5 What happens if something here changes

| Change | What happens | How sure |
|---|---|---|
| a tab button's number changed, say Import sends 1 | pressing Import shows the Cylinder page, and every part of the code that looks up a tab by number reaches the wrong one | *Reasoned from code* |
| `initModels` and `initViews` merged into `__init__` | the tabs try to reach `get_app().window` before it exists, and the window fails to build | *Reasoned from code* |
| Export pressed before a plan is imported | the page tries to switch, but the highlight stays on the previous button | *Verified* for the colours |
| the 3D view cannot start (no screen) | the window cannot be built | *Verified* ([8.3](#83-when-starting-fails)) |
| `tandem_error` given an unknown code | an empty message box | *Verified* |
| No pressed on the rotation warning | the rotation goes back to the plan's value | *Verified* for the returned answer |
| the window closed | `filepaths.json` is written | *Verified* |
| `Palettes.dark(window)` called at start-up | the window's palette changes, but the stylesheets still decide most colours | *Reasoned from code* |

### 14.6 Things nothing checks

- **That the tab numbers match.** The buttons' 0 to 4, the design file's page order and
  `NavigationModel`'s tab order must agree, and nothing checks.
- **That a message box has text.** An unknown `tandem_error` code shows an empty box.
- **That the icon and title agree.** `channel_display_error` has a critical icon and the title
  "Warning".
- **That the window icon is found.** `tandem_rotation_warning` loads
  `"resources\\brachify_splash-ico.ico"`, written the Windows way, so on macOS no icon is found.
- **That the theme is used.** `palettes.py` is never applied.
- **That the messages follow the project's writing rule.** Most messages start with "Error:",
  "Warning:" or "Warning,", which AGENTS.md's UI copy rule forbids in new text. The rule records
  these as existing copy, to be fixed in their own pull request with a clinical-wording review.

---

## 15. src/windows/models

**Summary.** `src/windows/models/` holds the app's **models**: the objects that keep the app's
data while it runs, with no buttons or boxes of their own. `DicomModel` holds the imported plan,
`CylinderModel` the cylinder, `ChannelsModel` the needles, which one is selected and which are
switched off, and `TandemModel` the tandem, generated or imported. They are connected by
**signals**: importing a plan makes `DicomModel` announce it, the cylinder and needle models load
it, and the tandem model follows the cylinder and the channel named "Tandem". Each of them hands
its 3D shapes to `DisplayModel`, which colours them for the current tab and tells the 3D view to
redraw. `ShapeModel` is the small package each shape travels in, and `NavigationModel` creates the
five tabs and switches between them. Several parts are broken but unused, and a few are used and
fragile: needles are kept by name, so two needles with the same name become one, and a Tandem
Height taller than the cylinder shows five error messages and then fails.

[`src/windows/models/`](../../src/windows/models/) has seven files:

| File | Size | Holds |
|---|---|---|
| [`dicom_model.py`](../../src/windows/models/dicom_model.py) | 15 lines | `DicomModel`: the imported plan, a `DicomData` ([10.4](#104-datapy-the-form-brachify-fills-in)) |
| [`cylinder_model.py`](../../src/windows/models/cylinder_model.py) | 53 | `CylinderModel`: the cylinder |
| [`channels_model.py`](../../src/windows/models/channels_model.py) | 191 | `ChannelsModel`: every needle, the selection, the switched-off ones |
| [`tandem_model.py`](../../src/windows/models/tandem_model.py) | 324 | `TandemModel`: the tandem, its settings, its offsets and its rotation |
| [`display_model.py`](../../src/windows/models/display_model.py) | 119 | `DisplayModel`: every shape the 3D view should show, and their colours |
| [`shape_model.py`](../../src/windows/models/shape_model.py) | 44 | `ShapeModel` and `ShapeTypes`: one shape, packaged for the 3D view |
| [`navigation_model.py`](../../src/windows/models/navigation_model.py) | 42 | `NavigationModel`: the five tabs and which one is showing |

### 15.1 Words you need

| Word | What it means here | Real example |
|---|---|---|
| **model** | an object that holds part of the app's data and announces when it changes. It has no widgets | `CylinderModel` |
| **view** (a **tab**) | a page of widgets that shows a model and changes it ([14.1](#141-words-you-need)) | the Cylinder tab |
| **signal**, **emit**, **connect** | an announcement; making it; attaching a function to it ([9.6](#96-signalspy-app-wide-announcements)) | `values_changed` |
| **label** | a shape's name, which the display uses as its key | `"Applicator2"`, `"cylinder"`, `"tandem_shape"` |
| **shape type** | which kind of thing a shape is: cylinder, channel, tandem, selected or export | `ShapeTypes.CHANNEL` |
| **material** | the colour and see-through setting a shape is drawn with | `{"rgb": [0.2, 0.55, 0.55], "transparent": True}` |
| **selected** | the needle you clicked, drawn in a different colour | — |
| **disabled** (switched off) | a needle left out of the 3D view, the export and the PDF | the `Tandem` channel, automatically |
| **generated** / **imported** tandem | a tandem built from the Tandem tab's numbers, or read from a STEP file | — |

### 15.2 How the models connect

All the connections, as `MainWindow.initModels` and `TandemModel.__init__` set them up
([14.3](#143-main_windowpy-building-the-window)):

```
 Import Dicom ─▶ DicomModel.update(plan) ─▶ values_changed ─┬─▶ CylinderModel.load_data
                                                            └─▶ ChannelsModel.load_data
                                                                     │
                                       a label contains "tandem" ─▶ set_tandem ─▶ tandem_changed
                                                                                        │
 CylinderModel ── values_changed ─┬─▶ TandemModel.update_cylinder                       │
                                  └─▶ Cylinder tab updates its boxes                    │
                                                                                        ▼
                                                                   TandemModel.set_tandem_channel
 app.signals.height_changed ─┬─▶ ChannelsModel.update_height_offset
                             └─▶ TandemModel.update_height_offset

 CylinderModel, ChannelsModel, TandemModel ── add_shape / add_shapes ─▶ DisplayModel
 the current tab's @display_action ─▶ DisplayModel.update() ─▶ shapes_changed ─▶ the 3D view redraws
```

The tandem model connects itself to the other two when it is created, which is why
`initModels` creates it last.

**Importing Ex2 through this chain**, with the real models, *Verified*:

| After `DicomModel.update(Ex2)` | Value |
|---|---|
| the cylinder | a `BrachyCylinder`, 30 mm across, 160 mm long |
| the needles | 13 channels, including `Tandem` |
| switched off | `["Tandem"]`, automatically, because its label contains "tandem" |
| the tandem's rotation | 359.996°, taken from the `Tandem` channel's tip, which is the same direction as 0° |
| `hasTandemInDICOM` | `True` |
| the tandem model's cylinder | 160 mm long, 30 mm across, copied from the cylinder model |
| a tandem built yet? | no: that waits for *Generate Tandem* |
| shapes in the display | 13: the cylinder and the 12 switched-on needles |
| needles that count as visible | 12 |

### 15.3 `shape_model.py`, one shape packaged for the 3D view

#### `ShapeTypes`

A short fixed list of the kinds of shape: `NONE`, `CYLINDER`, `CHANNEL`, `TANDEM`, `SELECTED` and
`EXPORT`. It is used only to **choose a colour**, not to say what a shape can do: each tab has its
own table of colours, one per type ([15.4](#154-display_modelpy-what-the-3d-view-shows)).

#### `ShapeModel`

The package a shape travels in, from a model to the display:

| Field | Holds | Example |
|---|---|---|
| `label` | the shape's name, and its key in the display | `"Applicator2"` |
| `shape` | the OpenCASCADE solid itself ([11.1](#111-words-you-need)) | Applicator2's tube |
| `type` | its `ShapeTypes`, `NONE` if none given | `ShapeTypes.CHANNEL` |
| `material` | the colour it will be drawn with, filled in by the display | `{"rgb": [0.2, 0.55, 0.55], "transparent": True}` |
| `rgb` | an older colour field the 3D view still reads | `None` |
| `selected` | whether it is the clicked needle | `False` |
| `transparent` | whether it is drawn see-through | `False` |
| `enabled` | whether it should be shown at all. `False` makes the display remove it | `True` |

`isMatch(shapes)` was meant to say whether one of a list of shapes is this shape. Its test is
written so that it skips every shape, so it always answers no. *Verified*: given a list holding
its own shape, it answered `False`. Nothing calls it.

### 15.4 `display_model.py`, what the 3D view shows

`DisplayModel` keeps a dictionary of shapes, `label → ShapeModel`, and the current tab's colour
table. Every model puts its shapes in; the 3D view draws whatever is there.

```
 CylinderModel.update_display()  ─┐
 ChannelsModel.update_display()  ─┼─▶  shapes = {"cylinder": …, "Applicator2": …, …, "tandem_shape": …}
 TandemModel.update_display()    ─┘          a shape with enabled = False is removed instead

 the tab opens ─▶ set_materials(that tab's colour table)

 update()  ─▶  for every shape: material = colours[its type]   (SELECTED if it is selected)
           ─▶  shapes_changed.emit(all the shapes)
           ─▶  the 3D view clears and draws them all
```

| Function | What it does | Used? |
|---|---|---|
| `add_shape(s)` | puts one shape in, or removes it if `enabled` is `False` | yes |
| `add_shapes(list)` | the same for many, used for the needles | yes |
| `remove_shape(label)` | takes one out, if it is there | yes, by the tandem |
| `set_materials(table)` | sets the colour table for the current tab | yes, by every tab when it opens |
| `set_transparent(yes/no)` | makes every shape see-through or not | yes, after import |
| `update()` | colours every shape and tells the 3D view to redraw | yes, after every change ([14.3](#143-main_windowpy-building-the-window)) |
| `show_shape`, `show_shapes` | tell the 3D view to draw only the given shapes | yes, by the Export tab |
| `set_selected_shapes` | marks a clicked shape as selected | yes |
| `reset()` | empties the display | yes, on import |
| `remove_shapes`, `set_shape_colour`, `set_shape_visibility` | — | **no** |

Two edge cases, *Verified*:

- `add_shape` with `enabled = False` for a shape that was never added **crashes** with a
  `KeyError`. `add_shapes` checks first and does not. In the app, the needles go through
  `add_shapes`, so this does not happen today.
- `update()` with an `EXPORT` shape while the **default** colour table is in use **crashes**,
  because the default table has no colour for `EXPORT`. Only the Export tab adds an `EXPORT`
  shape, and it installs its own colour table first.

### 15.5 `dicom_model.py`, the imported plan

The smallest model: it holds one `DicomData`, the form from [chapter 10](#10-classesdicom), and has
one function. `update(plan)` replaces the form with the new one and emits `values_changed`, which
starts the import chain in [15.2](#152-how-the-models-connect).

### 15.6 `cylinder_model.py`, the cylinder

| Field | Holds | Example |
|---|---|---|
| `cylinder` | the `BrachyCylinder` ([11.5](#115-cylinderpy-and-notchpy-the-solid-cylinder)), or nothing before the first import or *Apply Settings* | 30 mm across, 160 mm long |
| `starting_length` | the cylinder length at the moment the plan was imported, set by the Import tab | 160 |

| Function | What it does |
|---|---|
| `load_data(plan)` | makes a new cylinder for the plan, from the settings ([11.5](#115-cylinderpy-and-notchpy-the-solid-cylinder)) |
| `update_cylinder(cylinder)` | swaps in a new cylinder, from the Cylinder tab's *Apply Settings* |
| `update()` | emits `values_changed`, and puts the cylinder in the display as `"cylinder"` |
| `update_height_offset(h)` | **never connected, and wrong** |

`starting_length` is what makes cylinder-length changes work: the Cylinder tab sends
`height_changed(new length − starting_length)`, so the needles and the tandem shift by the
difference ([9.6](#96-signalspy-app-wide-announcements)).

`update_height_offset` has a comment saying it is connected to `height_changed`, but it is not:
only the needle and tandem versions are. If it were, it would set the cylinder's **length** to
the **difference**. *Verified*: calling it with −20 set the length to −20.0, and building the
cylinder then failed with an error from OpenCASCADE.

### 15.7 `channels_model.py`, the needles

| Field | Holds | Example on Ex2 |
|---|---|---|
| `channels` | every needle, `label → NeedleChannel` ([11.6](#116-channelpy-one-tube-per-needle)) | 13, from `"Applicator2"` to `"Tandem"` |
| `selected_channels` | the selected needle's label | `("Applicator5",)` after selecting it |
| `disabled_channels` | the labels of the switched-off needles | `["Tandem"]` |
| `diameter` | every needle's hole width | 2.7 |
| `threading_depth`, `threading_diamenter` | the threaded hole's depth and width. The second name is misspelled, and every use matches it | 5.0, 3.17 |

#### Loading the plan

`load_data` goes through the plan's three lists together ([10.4](#104-datapy-the-form-brachify-fills-in))
and makes one `NeedleChannel` per position, stored under its **label**. If a label contains
"tandem", that needle is set as the tandem.

**Needles are kept by name.** Two needles with the same label become one, and the second
replaces the first. *Verified*: with Ex2's second needle relabelled `Applicator2`, the model kept
12 needles of 13, and `Applicator2` held the second needle's shape, ROI 35, instead of its own,
ROI 34. Nothing warns.

#### Selecting, switching off, the tandem

| Function | What it does | Called from |
|---|---|---|
| `set_selected_channels(label)` | selects a needle by its label, and highlights it in the Channels tab's list | the list on the Channels tab |
| `set_selected_shapes(shapes)` | selects the needle whose shape was clicked in the 3D view | the 3D view, through the Channels tab |
| `clear_selected_channels()` | selects nothing | leaving the Channels tab |
| `toggle_channel_enabled(label)` | switches a needle off, or back on | *Disable* / *Enable* |
| `set_tandem(label)` | makes this needle the tandem, switches it off, and switches the previous tandem channel back on | *Set as Tandem*, and import |
| `get_tandem_channel()` | the tandem's needle, or nothing | the tandem, the PDF |
| `get_visible_channels()` | the needles that are switched on | the Export tab, the PDF |
| `update()` | emits `values_changed`, and puts every needle in the display, marking the selected one and leaving out the switched-off ones | after every change |
| `update_height_offset(h)` | shifts every needle by `h` ([11.6](#116-channelpy-one-tube-per-needle)) | `height_changed` |

`set_selected_channels` was written to accept either a label or a position number. The test for
"is this a position number?" compares the wrong things, so it is never true, and a number is
stored as if it were a label. *Verified*: selecting by label gave `("Applicator5",)`; selecting
by `0` stored `(0,)`, which matches no needle. The app only ever passes labels, so this does not
show up today.

### 15.8 `tandem_model.py`, the tandem

The busiest model. It keeps the tandem's settings, whether it was generated or imported, two
separate height offsets, and two rotations.

| Field | Holds | Example on Ex2 |
|---|---|---|
| `_base_shape` | the tandem hole's solid, before rotation and offsets. Nothing means "no tandem" | — |
| `_display_shape` | the preview of the tandem rod, for the Export tab | — |
| `is_shape_imported`, `filepath` | whether the tandem came from a STEP file, and which | `False`, `None` |
| `tandem_length` | the Tandem Height | 170 from the settings at first; 160 once the Tandem tab sends its box's value, capped at the cylinder's length |
| `tandem_diameter`, `stopper_diameter`, `tip_angle`, `bend_radius` | the other Tandem tab settings | 3.8, 5.0, 30, 35.0 |
| `threading_depth`, `threading_diameter` | the tandem's threaded hole | 7.0, 5.0 |
| `cylinder_length`, `cylinder_diameter` | copied from the cylinder model whenever it changes | 160.0, 30.0 |
| `rotation` | which way around the cylinder the tandem bends now | 359.996° |
| `protation` | the plan's rotation, to warn when you move away from it | 359.996° |
| `hasTandemInDICOM` | whether the plan had a channel named `Tandem` | `True` |
| `height_offset` | how far the cylinder's length has changed since import, set by `height_changed` | 0.0 |
| `mesh_offset` | the *Height Offset* box, for an **imported** tandem only | 0.0 |

The two offsets are easy to confuse. `height_offset` follows the cylinder automatically.
`mesh_offset` is a manual nudge you type in, and applies only to an imported STEP tandem.

#### Generating: `set_tandem` and `_generate_tandem`

*Generate Tandem* calls `set_tandem`, which calls `_generate_tandem`. That function tries each
setting one at a time, so a bad value can be found and put back:

```
 start from the built-in tandem values
   │
   ├─ try the new Channel Diameter  → build ─ fails? note "diam",    put the box back
   ├─ try the new Stopper Diameter  → build ─ fails? note "stopper", put the box back
   ├─ try the new Bend Angle        → build ─ fails? note "angle",   put the box back
   ├─ try the new Bend Radius       → build ─ fails? note "radius",  put the box back
   └─ try the new Tandem Height     → build ─ works? forget every earlier failure
                                             fails? note "height",  put the box back
   │
   ├─ for each noted failure: put that setting back to its built-in value,
   │                          and show its error message
   └─ keep the last tandem that was built
```

Each failure shows its message from `MainWindow` ([14.3](#143-main_windowpy-building-the-window)). Each try keeps the
settings already applied, so a value that fails early may be fixed by a later one. That is why
the last step forgets the earlier failures.

*Verified*, generating with the real model on Ex2's cylinder:

| Tandem Height | What happened |
|---|---|
| 160 | built, with no messages |
| 170, the built-in default | **five error messages**, then it **failed**: `cannot access local variable 'shape'` |
| 300 | the same: five messages, then it failed |

When every try fails, there is no tandem to keep, and the code trips over the missing value. The
default height fails because it is taller than the 160 mm cylinder ([11.7](#117-tandempy-the-tandem)),
and every try uses it until the last one. In normal use the Tandem Height box is capped at the
cylinder's length on import, so the 170 never reaches it.

#### The other functions

| Function | What it does |
|---|---|
| `import_tandem(file)` | reads a STEP file as the tandem ([11.8](#118-helperpy-intersectionspy-and-fileiopy)) |
| `clear_tandem()` | removes the tandem |
| `exists()` | whether there is a tandem at all |
| `shape()` | the tandem as the 3D view and the export see it: turned by `rotation`; for an imported one, also shifted up or down and stretched down to the base |
| `raw_shape()` | the preview of the tandem rod ([11.7](#117-tandempy-the-tandem)), turned by `rotation` |
| `set_tandem_channel(needle)` | takes the rotation from a needle's tip. If the needle is the plan's `Tandem`, also stores it as `protation` |
| `change_tandem_rotation(angle)` | turns the tandem to a new angle |
| `set_import_height_offset(h)` | the *Height Offset* box, for an imported tandem |
| `update_cylinder()` | copies the cylinder's new size, and rebuilds a generated tandem to fit |
| `update_height_offset(h)` | stores how far the cylinder's length has changed |
| `update()` | emits `values_changed`, and puts the tandem in the display as `"tandem_shape"`, or removes it |

`set_tandem_channel` checks whether it was given a needle before reading the needle's rotation,
but not before reading its label. *Verified*: given nothing, it fails with
`'NoneType' object has no attribute 'label'`. *Reasoned from code*: that can happen when the
Channels tab's rotation warning is answered No and no channel was the tandem before.

### 15.9 `navigation_model.py`, the five tabs

`NavigationModel` is not a Qt model and holds no data about the plan. It creates the five tabs,
in a fixed order, puts each in its page of the window, and switches between them.

| Position | Tab | Its model |
|---|---|---|
| 0 | Import | `DicomModel` |
| 1 | Cylinder | `CylinderModel` |
| 2 | Channels | `ChannelsModel` |
| 3 | Tandem | `TandemModel` |
| 4 | Export | all of them |

```
 viewChanged(page) ─▶ set_page(page)
                        ├─ already on it? stop
                        ├─ the old tab's on_close()
                        ├─ the new tab's on_open()     usually installs its colour table and redraws
                        └─ show that page of the window
```

Code all over the app reaches a tab by its position, such as `navigationmodel.views[3]` for the
Tandem tab. Changing the order breaks all of it (§4.3 of the source of truth).

### 15.10 What happens if something here changes

| Change | What happens | How sure |
|---|---|---|
| a plan is imported | the cylinder and needles load, the `Tandem` channel is switched off, the tandem's rotation is set | *Verified* |
| two needles share a label | one of them disappears, and the survivor has the other's shape | *Verified* |
| a needle is selected by position number | nothing is selected | *Verified* |
| Generate Tandem with a height taller than the cylinder | five error messages, then the tandem fails to build | *Verified* |
| `CylinderModel.update_height_offset` connected to `height_changed` | the cylinder's length becomes the difference, and building it fails | *Verified* for the call |
| the tandem model created before the needle or cylinder model | it connects to models that do not exist yet, and the window fails to build | *Reasoned from code* |
| the tabs' order changed in `NavigationModel` | every `views[n]` in the code reaches the wrong tab | *Reasoned from code* |

### 15.11 Things nothing checks

- **That needle names are unique.** Two needles with one name become one.
- **That a tandem was built.** When every try fails, the code fails too.
- **That the selection matches a needle.** A position number is stored as a name.
- **That a shape is in the display before removing it.** `add_shape` with a switched-off shape
  that was never added fails.
- **Code that cannot work.** `isMatch`, `CylinderModel.update_height_offset` and the index path of
  `set_selected_channels` are broken, and unused or unreachable today.

---

## 16. src/windows/splashscreen

**Summary.** `src/windows/splashscreen/` holds pictures, not code. `brachify_splash.png` is the
**splash screen**: the picture the Windows `.exe` shows while brachify loads, which `launch.py`
closes once the window is ready. `brachify_splash-ico.png` is the same artwork without the word
"brachify", and is byte-for-byte the same file as `resources/brachify_splash.png`.
`brachify_splash.pptx` is the PowerPoint file the pictures were made from. Running brachify from
Python shows no splash screen at all. The window's design file points at the `-ico.png` through a
Qt resource path that does not exist in the repository, so that icon never loads either.

[`src/windows/splashscreen/`](../../src/windows/splashscreen/) has three files. *Verified* sizes,
by opening each one:

| File | Size | What it is | Used by |
|---|---|---|---|
| `brachify_splash.png` | 1,220 × 687 pixels, 204 KB | the splash screen: curved blue bands, and the word *brachify* bottom right | `build_executable.py`, for the `.exe` |
| `brachify_splash-ico.png` | 1,280 × 720 pixels, 115 KB | the same bands **without** the word | the window's design file, through a path that never loads |
| `brachify_splash.pptx` | 47 KB | the PowerPoint slide the pictures were made from. It credits the two original developers | nothing: it is the source artwork |

The repository's top-level [`resources/`](../../resources/) folder holds two related files:

| File | What it is |
|---|---|
| `resources/brachify_splash.png` | **the same file** as `brachify_splash-ico.png`. *Verified*: identical checksums |
| `resources/brachify_splash-ico.ico` | the Windows icon, holding seven sizes from 16 × 9 to 256 × 144 pixels. It is wide, not square, which is unusual for an icon |

### 16.1 Words you need

| Word | What it means here | Real example |
|---|---|---|
| **splash screen** | a picture shown while a program loads, before its window appears | `brachify_splash.png` |
| **icon** | the small picture for the program, in the taskbar and the window's corner | `brachify_splash-ico.ico` |
| **`.ico` file** | Windows' icon format: one file holding the same picture at several sizes | `resources/brachify_splash-ico.ico` |
| **PyInstaller** | the tool that turns the Python code into the Windows `.exe` | `python build_executable.py` |
| **Qt resource path** | a path starting `:/`, for files packed into the program by a Qt resource file (`.qrc`) | `:/Icon/Icon/brachify_splash-ico.png` |

### 16.2 How the splash screen is used

Only the Windows `.exe` has a splash screen. `build_executable.py` passes the picture to
PyInstaller:

```
 python build_executable.py
   └─ pyinstaller … --icon ./resources/brachify_splash-ico.ico
                    --splash ./src/windows/splashscreen/brachify_splash.png …
        │
        ▼
 dist/brachify/brachify.exe
```

When a clinician starts the `.exe`:

```
 double-click brachify.exe
   │
   ├─ the splash picture appears straight away, while Python and the libraries load
   │
   ├─ launch.py runs, builds the window                              (8.2)
   │
   ├─ launch.py:  import pyi_splash ; pyi_splash.close()             closes the splash
   │              app.window.activateWindow()                         brings the window forward
   │
   └─ the window is showing
```

`pyi_splash` is a module PyInstaller puts inside the `.exe` only. Run from Python with
`python src/launch.py`, the import fails, `launch.py` ignores the failure, and there is no splash
screen ([8.2](#82-launchpy-starting-the-app)).

### 16.3 How the icons are used, and where they go missing

The code asks for the window's icon in three places, and on a Mac none of them finds a picture.
The fourth row is the `.exe` file's own icon, which works:

| Where | Asks for | Finds it? |
|---|---|---|
| the window's design file, `main_window.ui` | `:/Icon/Icon/brachify_splash-ico.png`, a Qt resource path | **never**: there is no `.qrc` resource file anywhere in the repository, so nothing provides `:/Icon/…`. *Verified*: no `.qrc` file exists |
| `app.py`, `gui()` | `"resources\\brachify_splash-ico.ico"`, relative to the folder you start from | only on Windows, started from the repository's top folder. On macOS and Linux the `\\` is not a folder separator, so no icon. *Reasoned from code* |
| `main_window.py`, the rotation warning | the same path as `app.py` | the same |
| the `.exe` itself | `resources/brachify_splash-ico.ico`, given to PyInstaller | yes: that becomes the `.exe` file's own icon |

```
 main_window.ui ── ":/Icon/Icon/brachify_splash-ico.png" ──▶ no .qrc in the repository ──▶ nothing

 app.py ── "resources\\brachify_splash-ico.ico" ──┬─▶ Windows, started from the top folder ──▶ the icon
                                                  └─▶ macOS or Linux ──▶ nothing, silently
```

None of this stops the app from working. The window simply has no icon, or the default one.

### 16.4 What happens if something here changes

| Change | What happens | How sure |
|---|---|---|
| `brachify_splash.png` replaced with another picture | the next `.exe` built shows the new picture while loading | *Reasoned from code* |
| `brachify_splash.png` deleted | `python build_executable.py` fails, because PyInstaller cannot find the splash picture | *Reasoned from code* |
| `brachify_splash-ico.png` or the `.pptx` deleted | nothing changes: neither is used by any code that runs | *Verified* that nothing loads them |
| a `.qrc` file added that provides `:/Icon/Icon/brachify_splash-ico.png` | the design file's icon would start to work, once the resource file is compiled and imported | *Reasoned from code* |
| `launch.py`'s `pyi_splash.close()` removed | in the `.exe`, the splash picture would stay on screen after the window opens | *Reasoned from code* |

### 16.5 Things nothing checks

- **That the icon exists.** Three places ask for an icon, and on a Mac none finds one, silently.
- **That there are no duplicates.** The same picture is stored twice, as
  `resources/brachify_splash.png` and `splashscreen/brachify_splash-ico.png`.
- **That the icon is square.** The `.ico` file is 16:9, so Windows has to fit a wide picture
  into a square space.

---

## 17. src/windows/views

**Summary.** `src/windows/views/` holds the five **tabs** you click through, Import, Cylinder,
Channels, Tandem and Export, and the **3D view** beside them. Each tab is a page of number boxes
and buttons, built from its design file ([chapter 18](#18-srcwindowsui)). Pressing a button runs
one of the tab's `action_…` functions, which reads the boxes, writes the values into the live
settings and the right model, and redraws the 3D view. Each tab also brings its own colours, so
the same model is drawn differently on each one. The Import tab reads a plan or a settings file,
the Cylinder, Channels and Tandem tabs change their part of the design, and the Export tab cuts
the holes out and saves the STL, the STEP, the PDF and the settings file. The 3D view draws
whatever the display holds, and turns mouse clicks into selections. Running the real tabs showed
two things the code gets wrong: pressing a key in the 3D view raises an error, and shortening the
cylinder below the tandem's height makes the tandem's rebuild fail.

[`src/windows/views/`](../../src/windows/views/) has seven files:

| File | Size | What it is | Position |
|---|---|---|---|
| [`custom_view.py`](../../src/windows/views/custom_view.py) | 31 lines | `CustomView`, the shared base of every tab, and `@display_action` | — |
| [`import_view.py`](../../src/windows/views/import_view.py) | 196 | the **Import** tab | 0 |
| [`cylinder_view.py`](../../src/windows/views/cylinder_view.py) | 103 | the **Cylinder** tab | 1 |
| [`channels_view.py`](../../src/windows/views/channels_view.py) | 197 | the **Channels** tab | 2 |
| [`tandem_view.py`](../../src/windows/views/tandem_view.py) | 170 | the **Tandem** tab | 3 |
| [`export_view.py`](../../src/windows/views/export_view.py) | 262 | the **Export** tab | 4 |
| [`viewport.py`](../../src/windows/views/viewport.py) | 202 | `OrbitCameraViewer3d`, the 3D view | — |

**How these were checked.** The real window, models and five tabs were built without a screen
and clicked through in code, on Ex2. Only three things were stand-ins: the 3D view (which needs a
screen) recorded what it was asked to draw, the file dialogs answered with the Ex2 folder, and the
message boxes recorded their text and answered Yes. Results from that run are marked *Verified*.

### 17.1 Words you need

| Word | What it means here | Real example |
|---|---|---|
| **tab** (the code says **view**) | one page of boxes and buttons | the Cylinder tab |
| **action** | a tab's function that runs when you press a button | `action_apply_settings` |
| **number box** (spin box) | a box holding a number, with up and down arrows. It has a lowest and highest allowed value | *Cylinder Length*, 60 to 300 |
| **list** | the box of names on the Channels tab, one row per needle | `listwidget_channels` |
| **tick box** | an on/off box | *Add Collar* |
| **sub-tab** | a tab inside a tab | the Tandem tab's *Import* and *Generate* |
| **colour table** (the code says **materials**) | each tab's colour and see-through setting for each kind of shape | the Channels tab draws needles teal |
| **decorator** | a line starting `@` above a function, that wraps the function in extra behaviour | `@display_action` |

### 17.2 How every tab works

Every tab follows the same pattern:

```
 the tab is created by NavigationModel (15.9)
   ├─ builds its boxes and buttons from its design file      self.ui = Ui_…_View(); setupUi(self)
   ├─ fills its boxes from the live settings
   └─ connects each button to an action                     btn_apply_settings → action_apply_settings

 you open the tab ──▶ on_open()     installs the tab's colour table, redraws the 3D view
 you press a button ─▶ action_…()   reads the boxes → updates the live settings and the model
                                    → @display_action redraws the 3D view
 you leave the tab ─▶ on_close()
```

`CustomView`, in `custom_view.py`, is the base every tab is built on. It only provides empty
`on_open` and `on_close`. The file's other part, `@display_action`, wraps a tab's function so that
**after it runs, even if it fails, the 3D view is redrawn**:

```python
@display_action
def action_apply_settings(self): …        # runs first
                                          # then, always: get_app().window.displaymodel.update()
```

A tab function that changes the 3D model without `@display_action` changes the model but not the
picture (§4.5 of the source of truth). The wrapped function's answer is thrown away: it always
returns nothing.

#### Each tab's colours

The same shapes are drawn with each tab's own colour table. All values are red, green, blue from
0 to 1, and "see-through" means drawn partly transparent. *Verified* for the Channels tab, from the
real run: the cylinder was drawn grey (0.8, 0.8, 0.8) and the needles teal (0.2, 0.55, 0.55).

| Shape | Import | Cylinder | Channels | Tandem | Export |
|---|---|---|---|---|---|
| cylinder | teal | **teal** | grey | grey | teal |
| needles | teal | grey | **teal** | grey | teal |
| tandem | teal | grey | grey | **teal, solid** | dark grey |
| selected needle | teal | teal | **blue** (0.2, 0.2, 0.7) | green | teal |
| the export solid | — | — | — | — | teal |

Teal is (0.2, 0.55, 0.55), grey (0.8, 0.8, 0.8). Everything is see-through except the tandem on
the Tandem tab. Each tab highlights its own part in teal and greys out the rest, which is why the
same model looked different in each tab's screenshot.

### 17.3 `import_view.py`, the Import tab

| Widget | Label | Does |
|---|---|---|
| `btn_import_folder` | *Import Dicom* | `action_import_dicom_folder`: import a plan |
| `btn_config_file` | *Import Config File* | `action_import_config_file`: import a settings file |
| `info_area` | — | the text panel: the plan's details, then which settings were loaded |

#### Import Dicom, step by step

*Verified*, on Ex2:

| Step | What happens | On Ex2 |
|---|---|---|
| 1 | a folder picker opens ([8.4](#84-starting-with-a-folder)). Cancel stops here | — |
| 2 | `starting_length` is set to the current cylinder length ([15.6](#156-cylinder_modelpy-the-cylinder)) | 160 |
| 3 | the old tandem's offsets are reset, the old plan and the old display are emptied | — |
| 4 | the plan is read ([chapter 10](#10-classesdicom)). If that fails, the log says "Empty folder selected." and it stops | read |
| 5 | if the reader found the cylinder, the plan is handed to the models ([15.2](#152-how-the-models-connect)) | 13 channels |
| 6 | every shape is made see-through, the info panel is rewritten, the Channels tab's list is refilled | 13 rows |
| 7 | the Tandem Height box's highest value is set to the cylinder's length | 160 |
| 8 | the app switches to the Export tab, and colours its button | page 4 |

The info panel after importing Ex2, exactly as written:

```
Folder: SI_C_D30 Brachify_Ex2

Patient and Plan Info
Patient ID:         	SI_C_D30
Patient Name:    	CYLINDER
Plan ID:                	Brachify_Ex2
Approval Status: 	UNAPPROVED
Operator:           	Michael Kudla

Channels Info
Applicator2,  Channel: 2
…
Tandem Label:  Tandem
```

followed by the settings message from [13.4](#134-valuespy-the-live-settings). The line called
"Plan ID" shows the plan's **label**, `RTPlanLabel`.

#### Import Config File

Opens a file picker for a `.json` file, reads it with `load_config_file` using the **current**
settings to fill any gaps ([13.5](#135-loadpy-reading-a-settings-file)), rewrites the info panel, caps
the Tandem Height box at the new cylinder length, and calls `resetAllValues` to put the new values
into every tab's boxes ([13.6](#136-resetpy-into-the-boxes-and-back-out)).

### 17.4 `cylinder_view.py`, the Cylinder tab

| Widget | Label | Allowed values |
|---|---|---|
| `spinbox_diameter` | *Cylinder Diameter* | 0 to 99.99 mm |
| `spinbox_length` | *Cylinder Length* | 60 to 300 mm, **whole numbers only** |
| `spinbox_base_thickness` | *Collar Thickness* | 0 to 99 mm, whole numbers only |
| `spinbox_base_height` | *Collar Height* | 0 to 99 mm, whole numbers only |
| `cb_add_base` | *Add Collar* | on or off. Not a setting, so never saved ([13.2](#132-the-19-settings)) |
| `btn_apply_settings` | *Apply Settings* | — |

#### Apply Settings, step by step

```
 Apply Settings
   ├─ 1  read the four boxes and the tick box
   ├─ 2  write diameter, length, collar thickness and collar height into the live settings
   ├─ 3  make a new BrachyCylinder with the new diameter
   ├─ 4  height_changed.emit(new length − starting_length)       the needles and tandem shift (9.6)
   ├─ 5  turn the collar on or off, which builds and saves the cylinder's shape
   ├─ 6  hand the new cylinder to the cylinder model             the tandem model follows (15.8)
   └─ 7  set the Tandem Height box's highest value to the new length
```

`action_update_settings` does the reverse: whenever the cylinder model changes, it puts the
cylinder's diameter, length and collar state back into the boxes.

#### What really happens to the collar

§7.1 of the source of truth said the collar silently disappears after *Generate Tandem*. The real
run shows that it does not, in this sequence, and §7.1 was corrected from it on 2026-10-02. *Verified*, with the real tabs:

| Step | Live settings' collar | Cylinder volume | The collar is |
|---|---|---|---|
| tick *Add Collar*, thickness 3, height 10, *Apply* | 10, 3 | 112,709.4 mm³ | there |
| *Generate Tandem* | **missing** | 112,709.4 mm³ | still there: the cylinder's saved shape is used |
| the Export tab's solid | missing | 100,198.9 mm³, with the collar and the tandem hole | still there |
| set the length to 150, *Apply* | 10, 3 again | 105,640.8 mm³ | there |

*Generate Tandem* does remove the collar keys from the live settings, as §7.1 says. But the
cylinder's shape was saved when it was built, so it keeps its collar, and the next *Apply* writes
the collar keys back from the boxes before building. Where the collar really is lost is in the
settings file: an export leaves it out and an import ignores it
([13.6](#136-resetpy-into-the-boxes-and-back-out)).
*Not checked*: whether some other path rebuilds the cylinder from the live settings between
*Generate Tandem* and the next *Apply*.

### 17.5 `channels_view.py`, the Channels tab

| Widget | Label | Allowed values / does |
|---|---|---|
| `spinbox_diameter` | *Channels Diameter* | 0.3 to 99.99 mm |
| `sb_needle_length` | *Dead Space* | 0 to 350 mm |
| `sb_threading_dept` | *Threading Depth* | 0 to 350 mm. The name is missing an h |
| `sb_threading_diameter` | *Threading Diameter* | 0 to 350 mm |
| `btn_apply_settings` | *Apply* | writes all four into the live settings and rebuilds every needle |
| `listwidget_channels` | *Channels* | one row per needle. Clicking a row selects it |
| `btn_enable` | *Disable* / *Enable* | switches the selected needle off or on |
| `btn_set_tandem` | *Set as Tandem* / *Clear Tandem* | makes the selected needle the tandem |

*Verified*, on Ex2:

| Action | Result |
|---|---|
| click the 4th row | `Applicator5` selected, drawn blue. The buttons read *Disable* and *Set as Tandem* |
| *Disable* | the button reads *Enable*, and 11 needles are left switched on |
| *Enable* | back to 12 |

You can also select a needle by clicking it in the 3D view: opening the Channels tab connects the
3D view's click signal to the tab, and leaving the tab disconnects it and clears the selection.
So clicking a needle in 3D only selects it while the Channels tab is open.

*Set as Tandem* makes the selected needle the tandem, switches it off, aims the tandem at it, and
may show the rotation warning ([14.3](#143-main_windowpy-building-the-window)). When the selected
needle already is the tandem, the button reads *Clear Tandem*, and pressing it does not clear
anything: the code only acts when the selected needle is **not** the tandem. *Reasoned from code.*

### 17.6 `tandem_view.py`, the Tandem tab

Two sub-tabs. *Generate* builds a tandem from numbers; *Import* reads one from a STEP file.

| Sub-tab | Widget | Label | Allowed values |
|---|---|---|---|
| Generate | `sb_tandem_height` | *Tandem Height* | 10 to 500 mm, capped at the cylinder's length after import |
| Generate | `sp_channel_diameter` | *Channel Diameter* | 0.5 to 99.99 mm |
| Generate | `sp_stopper_diameter` | *Stopper Diameter* | 0.5 to 99.99 mm |
| Generate | `sp_bend_angle` | *Bend Angle* | 0 to 99.99° |
| Generate | `sb_bend_radius` | *Bend Radius* | 10 to 1,000 mm |
| Generate | `sb_threading_depth`, `sb_threading_diameter` | *Threading Depth*, *Threading Diameter* | 0 to 350 mm |
| Generate | `tandem_rotation_2` | *Rotation* | −360 to 360° |
| Generate | `btn_apply`, `btn_clear_generate` | *Generate Tandem*, *Clear Tandem* | — |
| Import | `btn_import`, `btn_clear_import` | *Import*, *Clear Tandem* | — |
| Import | `sb_height_offset` | *Height Offset* | −100 to 100 mm |
| Import | `tandem_rotation` | *Rotation* | −360 to 360° |
| Import | `btn_apply_import` | *Apply Import Settings* | — |
| Import | `label_5` | shows "Model filepath:" and the imported file | — |

The two *Rotation* boxes hold the same value and must always be written together (§7.6 of the
source of truth).

#### Generate Tandem, step by step

```
 Generate Tandem
   ├─ 1  copy every box into the tandem model
   ├─ 2  build the tandem: try each setting in turn (15.8)
   ├─ 3  if the plan had a "Tandem" channel and the Rotation box differs from it,
   │     show the rotation warning, once per import
   ├─ 4  turn the tandem to the Rotation box's angle, and write it back into both Rotation boxes
   └─ 5  replace the whole live settings with getCurrentValues()   ← 17 keys: the collar is dropped
```

*Verified*, on Ex2: the tandem was built at Tandem Height 160, with no messages, and afterwards the
live settings held 17 keys, without the two collar keys.

**Importing a tandem** opens a file picker for `.stp` or `.step`, reads it, may show the rotation
warning, and turns it to the *Rotation* box's angle. *Apply Import Settings* applies the *Height
Offset* and *Rotation* boxes to an imported tandem.

### 17.7 `export_view.py`, the Export tab

| Widget | Label | Does |
|---|---|---|
| `cb_tandem_shown` | *Show Tandem* | also draws the tandem rod preview. Greyed out when there is no tandem |
| `cb_collet_preview_reference_sheet` | *Show Collet Spacings* | adds the collet rings to the PDF ([12.5](#125-the-base-map)) |
| `sb_needle_collet_od` | *Needle Collet Spacing Tol.* | the needle collet ring's size, 0 to 99.99 |
| `sb_tandem_collet_outer_od`, `sb_tandem_collet_inner_od` | *Tandem Outer / Inner Spacing Tol.* | the tandem's two rings |
| `btn_export_mesh` | *Export Mesh* | saves the solid as `.stl`, or `.step` |
| `btn_export_shapes` | *Export Shape(s)* | saves the cylinder, the tandem and the needles as separate pieces in one `.step` |
| `btn_export_template_reference` | *Export Reference Sheet* | saves the PDF ([chapter 12](#12-classespdf)). If that fails, shows "Your PDF was not saved" |
| `btn_export_current_config` | *Export Current Settings as Config* | saves a settings file ([13.7](#137-the-two-files-on-disk)) |

#### Opening the Export tab

The Export tab does not draw the display's shapes like the other tabs. Every time you open it:

```
 on_open()
   ├─ put the saved collet sizes into the three collet boxes
   ├─ grey out Show Tandem if there is no tandem
   ├─ build the export solid:  cylinder − tandem − every switched-on needle   (11.9)
   └─ draw only that solid, and the tandem preview if Show Tandem is ticked
```

*Verified*, right after importing Ex2: the 3D view was asked to draw one shape, the export solid,
of 98,960.8 mm³, and *Show Tandem* was greyed out because no tandem had been generated yet.

The solid is **rebuilt every time** the tab is opened, which on Ex2 means cutting 12 needles out
again. The collet boxes save themselves into the live settings every time their value changes.

### 17.8 `viewport.py`, the 3D view

`OrbitCameraViewer3d` is the 3D view on the right of the window: an OpenCASCADE viewer placed
inside a Qt widget.

#### The mouse

| You do | It does |
|---|---|
| left-click a shape | selects it, and announces the shape on `sig_topods_selected`. Only the Channels tab listens ([17.5](#175-channels_viewpy-the-channels-tab)) |
| drag with the **right** button | turns the model around |
| drag with the **middle** button | slides the model across the view |
| turn the wheel | zooms in or out, by 2× per notch |
| move the mouse | highlights the shape under the pointer |

#### Redrawing

Every time the display changes, `update_display` runs:

```
 update_display(shapes)
   ├─ remove everything from the view
   ├─ draw each shape in its colour, see-through or not
   ├─ repaint
   └─ zoom to fit every shape                      ← every time
```

Every caller asks for the zoom to fit, so after any change, such as pressing *Apply* or selecting
a needle, the camera jumps back to show the whole model, and any zooming you did is lost.
*Reasoned from code*: both of the display's redraw functions always ask for it.

#### Two broken parts

- **Pressing a key while the 3D view is selected raises an error.** The key handler looks up the
  key in `self._key_map`, which is never created. *Verified*: a key press gave
  `AttributeError: 'OrbitCameraViewer3d' object has no attribute '_key_map'`. Qt prints the error
  and carries on.
- **Unused parts.** `DrawBox`, for dragging a selection box, is never called, and the cursor
  shapes it would switch between were never set up, so the cursor never changes.

### 17.9 What happens if something here changes

| Change or action | What happens | How sure |
|---|---|---|
| import a plan | the info panel fills, the Tandem Height box is capped at the cylinder's length, the app switches to Export | *Verified* |
| Generate Tandem | the tandem is built, and the live settings drop the collar keys | *Verified* |
| tick *Add Collar*, Apply, then Generate Tandem | the collar stays on the cylinder and in the export | *Verified* |
| shorten the cylinder below the Tandem Height after a tandem exists | the tandem's rebuild fails: `cannot access local variable 'shape'` ([15.8](#158-tandem_modelpy-the-tandem)). The old tandem stays | *Verified* for the failure, *Reasoned from code* that the old tandem stays |
| press a key in the 3D view | an error is printed, and nothing else happens | *Verified* |
| zoom in the 3D view, then press Apply | the view zooms back out to fit | *Reasoned from code* |
| click a needle in 3D on any tab but Channels | nothing is selected | *Reasoned from code* |
| a tab function changing the model without `@display_action` | the model changes, the picture does not | *Reasoned from code* |

### 17.10 Things nothing checks

- **That the cylinder stays taller than the tandem.** Shortening it below the Tandem Height makes
  the tandem's rebuild fail. The box's cap is only updated afterwards.
- **That a key press is handled.** The key map was never set up.
- **That the view keeps your zoom.** Every redraw zooms to fit.
- **That *Clear Tandem* clears.** On the Channels tab it does nothing.
- **That whole-number boxes get whole numbers.** The cylinder length and the collar are whole
  millimetres only, while the settings and the files can hold any decimal.
- **That the copy follows the project's writing rule.** The info panel's labels, such as
  "Patient ID:", and the Tandem tab's "Model filepath:" use colons, which AGENTS.md's UI copy rule
  forbids in new text.

---

## 18. src/windows/ui

**Summary.** `src/windows/ui/` holds the **design files** for the window and its five tabs, and
the Python made from them. Each `.ui` file is a layout drawn by hand in a tool called Qt Designer,
saved as XML, saying which boxes and buttons exist, their names, labels, sizes, colours and allowed
values. A command, `pyside6-uic`, turns each `.ui` file into a `_ui.py` file of Python that builds
those widgets, and the window and each tab run that Python to build themselves. People edit the
`.ui` files; nobody edits the `_ui.py` files, because the next regeneration would overwrite them.
All six pairs were checked to match. The widget names in these files are the names the rest of
the code uses, so renaming one in Qt Designer breaks every line that uses the old name.

[`src/windows/ui/`](../../src/windows/ui/) holds six pairs of files, one pair per screen:

| Design file (edited by people) | Generated Python (never edited) | Builds | Generated by |
|---|---|---|---|
| [`main_window.ui`](../../src/windows/ui/main_window.ui) | `main_window_ui.py` | `Ui_MainWindow`: the window, the five tab buttons, the page stack, the 3D view's panel | uic 6.5.2 |
| [`import_view.ui`](../../src/windows/ui/import_view.ui) | `import_view_ui.py` | `Ui_Import_View` | uic 6.8.1 |
| [`cylinder_view.ui`](../../src/windows/ui/cylinder_view.ui) | `cylinder_view_ui.py` | `Ui_Cylinder_View` | uic 6.8.1 |
| [`channels_view.ui`](../../src/windows/ui/channels_view.ui) | `channels_view_ui.py` | `Ui_Channels_View` | uic 6.8.1 |
| [`tandem_view.ui`](../../src/windows/ui/tandem_view.ui) | `tandem_view_ui.py` | `Ui_Tandem_View` | uic 6.8.1 |
| [`export_view.ui`](../../src/windows/ui/export_view.ui) | `export_view_ui.py` | `Ui_Export_View` | uic 6.8.1 |

### 18.1 Words you need

| Word | What it means here | Real example |
|---|---|---|
| **Qt Designer** | a drag-and-drop tool for laying out Qt windows. It comes with PySide6 as `pyside6-designer` | — |
| **`.ui` file** | Qt Designer's saved layout, written as XML | `cylinder_view.ui` |
| **XML** | a text format of nested, named tags | `<widget class="QPushButton" name="btn_apply_settings">` |
| **generate** | make a file automatically from another one | `_ui.py` from `.ui` |
| **`pyside6-uic`** | the command that turns a `.ui` file into Python. "uic" stands for User Interface Compiler | — |
| **object name** | a widget's name in the code. Set in Qt Designer, never shown on screen | `btn_import_view` |
| **text** | what the widget shows on screen | *Import* |

### 18.2 From a drawing to a tab

```
 Qt Designer ──saves──▶ cylinder_view.ui            XML: widgets, names, labels, limits, colours
                              │
               pyside6-uic cylinder_view.ui -o cylinder_view_ui.py
                              ▼
                       cylinder_view_ui.py          Python: class Ui_Cylinder_View, setupUi()
                              │
                     imported by cylinder_view.py
                              ▼
          self.ui = Ui_Cylinder_View();  self.ui.setupUi(self)
                              │
                              ▼
          every widget exists as self.ui.<object name>:  self.ui.spinbox_length, …
```

One button, followed all the way through:

| Where | What it says about the Cylinder tab's *Apply Settings* button |
|---|---|
| `cylinder_view.ui` | `<widget class="QPushButton" name="btn_apply_settings">`, with text *Apply Settings* |
| `cylinder_view_ui.py` | `self.btn_apply_settings = QPushButton(…)`, and its text set to "Apply Settings" |
| `cylinder_view.py` | `self.ui.btn_apply_settings.pressed.connect(self.action_apply_settings)` |

The object name typed into Qt Designer becomes the Python name every other file uses.

### 18.3 What each design file contains

Every widget the code uses, with its label on screen and its allowed values. *Verified*, read
from the `.ui` files.

**`main_window.ui`**: the five tab buttons `btn_import_view`, `btn_cylinder_view`,
`btn_channels_view`, `btn_tandem_view`, `btn_export_view` (*Import* to *Export*); the page stack
`viewswidget`, with pages `page_import` to `page_export`; the panels `top_menu_bar` and
`display_view_widget` ([14.2](#142-what-the-window-is-made-of)).

**`import_view.ui`**: *Import Dicom* (`btn_import_folder`), *Import Config File*
(`btn_config_file`), and the text panel `info_area` ([17.3](#173-import_viewpy-the-import-tab)).

**`cylinder_view.ui`**, **`channels_view.ui`**, **`tandem_view.ui`** and **`export_view.ui`**:
their widgets, labels and limits are listed with each tab, in
[17.4](#174-cylinder_viewpy-the-cylinder-tab), [17.5](#175-channels_viewpy-the-channels-tab),
[17.6](#176-tandem_viewpy-the-tandem-tab) and [17.7](#177-export_viewpy-the-export-tab).

Two kinds of number box are used, and the difference matters:

| Kind | Holds | Used for |
|---|---|---|
| `QSpinBox` | **whole numbers only** | *Cylinder Length*, *Collar Thickness*, *Collar Height* |
| `QDoubleSpinBox` | decimals, with a set number of places | every other number box |

So the cylinder's length and the collar can only be whole millimetres on screen, though the
settings and the settings files can hold any decimal.

**Limits are set in the design file**, not in the code. Where a design file sets none, Qt uses its
own: 0 to 99 for a whole-number box, and 0 to 99.99 for a decimal box. That is why *Cylinder
Diameter*, *Bend Angle* and the collet boxes all stop at 99.99, and why *Cylinder Diameter* allows
0. One limit is changed by the code: the Tandem Height box's highest value is set to the cylinder's
length on import and on *Apply Settings*.

### 18.4 Are the generated files up to date?

The `_ui.py` files are only correct if someone regenerated them after the last change to their
`.ui` file. *Verified*, by regenerating all six from their `.ui` files with `pyside6-uic` 6.11.2
and comparing: **all six match**. The only differences are the version in the header comment, and
the newer tool spelling Qt's names in full, such as `QSizePolicy.Policy.Minimum` for
`QSizePolicy.Minimum`, which mean the same thing.

`main_window_ui.py` was last generated with uic 6.5.2 and the other five with 6.8.1. §5.6 of the
source of truth said all were made with 6.5.2, which is only true of the first. It was corrected
on 2026-10-02.

### 18.5 Changing a design file

```
 1  open it in Qt Designer:     pyside6-designer src/windows/ui/cylinder_view.ui
 2  make the change, save
 3  regenerate:                 pyside6-uic src/windows/ui/cylinder_view.ui -o src/windows/ui/cylinder_view_ui.py
 4  commit BOTH files together
```

Three rules:

- **Never edit a `_ui.py` file by hand.** The next regeneration overwrites it.
- **Renaming a widget breaks the code that uses its old name.** Search for the old name first:
  `btn_import_view`, for example, appears in `main_window.py` 8 times.
- **Regenerate with the Windows environment's version, 6.8.1, if you can.** A newer `pyside6-uic`
  rewrites every Qt name in full and the header, which makes the change hard to review.

### 18.6 Colours and other text in the design files

The design files also hold **stylesheets**, which set colours. Two things there show up when the
app runs:

- **A colour written wrong.** `main_window.ui` sets six colours as `rgba(240, 245, 250)`. `rgba`
  needs four numbers, so Qt prints `Specified color with alpha value but no alpha given` every
  start, and carries on ([8.7](#87-what-happens-if-something-here-changes)). *Verified*.
- **An icon that never loads.** `main_window.ui` asks for `:/Icon/Icon/brachify_splash-ico.png`,
  from a Qt resource file that does not exist in the repository
  ([16.3](#163-how-the-icons-are-used-and-where-they-go-missing)).

The labels in the design files are user-facing text, covered by AGENTS.md's UI copy rule. One
breaks it: `tandem_view.ui` sets `label_5` to "Model Filepath: None", with a colon. The code then
replaces that text with "Model filepath:" and the file's path whenever the Tandem tab updates.

### 18.7 Things nothing checks

- **That a `_ui.py` file was regenerated.** Nothing compares it with its `.ui` file. They match
  today because people regenerated them.
- **That the code's widget names exist.** A renamed widget is only found when the line using it
  runs and fails.
- **That the limits make sense.** *Cylinder Diameter* allows 0, and *Bend Angle* allows 99.99°,
  because no limits were set.
- **That the colours are written correctly.** The three-number `rgba` warns on every start.

---

## 19. user_guide/

**Summary.** `user_guide/` holds one file, the **Brachify User Manual**: a 22-page Word document
written at BC Cancer for the clinicians who use the app. It explains how to prepare a plan in
Varian BrachyVision or Elekta Oncentra, how to install the `.exe`, and what every tab, box and
button does. It is the authority on the clinical workflow. Checked against the code, most of it is
right, but a few things have drifted: it describes a selected needle's colour, the Export tab's
notch, and the export formats differently from what the code does, and it asks for an exact
`Central Axis` label that the code matches more loosely. The folder came from upstream and is
never edited.

[`user_guide/`](../../user_guide/) holds one file. *Verified*, from the file:

| File | Size | Pages | Words | Pictures | Last edited |
|---|---|---|---|---|---|
| `Brachify User Manual.docx` | 4.5 MB | 22 | 2,169 | 53 | 2026-06-12 |

### 19.1 What the manual covers

| Manual section | Covers | In this document |
|---|---|---|
| 1. Treatment Plan Requirements – Varian Brachyvision | drawing the Central Axis and the needles, labelling a tandem, exporting the RP and RS | [chapter 10](#10-classesdicom) |
| 2. Treatment Plan Requirements – Elekta Oncentra | the same for Oncentra, including the implant-model licence and *Tip End* | [10.6](#106-elekta-oncentra-files) |
| 3. Setting up Brachify for the First time | downloading the `.exe` from GitHub, unzipping it, a shortcut, the security warning | [8.2](#82-launchpy-starting-the-app) |
| 4.1 Import | Import Dicom, Import Config File, the info panel | [17.3](#173-import_viewpy-the-import-tab), [chapter 13](#13-srcsettings) |
| 4.2 Display Panel | the 3D view, and the mouse | [17.8](#178-viewportpy-the-3d-view) |
| 4.3 Cylinder | diameter, length, the collar, Apply Settings | [17.4](#174-cylinder_viewpy-the-cylinder-tab) |
| 4.4 Channels | diameter, threading, the list, Set as Tandem, Disable | [17.5](#175-channels_viewpy-the-channels-tab) |
| 4.5 Tandem | importing a STEP tandem, and generating one | [17.6](#176-tandem_viewpy-the-tandem-tab), [11.7](#117-tandempy-the-tandem) |
| 4.6 Export | the four export buttons, Show Tandem, the collet spacings | [17.7](#177-export_viewpy-the-export-tab), [chapter 12](#12-classespdf) |
| 5. Layout of Brachify | a list of every box and button | [18.3](#183-what-each-design-file-contains) |

The rules for preparing a plan, both vendors:

```
 1  line up the cylinder and draw a straight needle along its centre line
 2  label it exactly "Central Axis", with its tip at the cylinder's tip
 3  give it zero radiation time: it is not part of the model
 4  a central needle that DOES carry radiation needs a different label
 5  place the other needles; make sure no two cross
 6  optionally, label one channel "Tandem" to aim the tandem
 7  export the plan (RP) and the structures (RS) into one folder
```

### 19.2 Where the manual and the code disagree

Checked against the code on 2026-09-29. *Reasoned from code* unless marked.

| The manual says | The code does | In this document |
|---|---|---|
| label the axis exactly `Central Axis`, and give a dose-carrying central needle a different label | on Varian plans the code matches any label that **contains** "central axis", so a different label such as `Central Axis Needle` can still be taken as the axis | [10.5](#105-fileiopy-how-the-form-gets-filled), [10.8](#108-what-happens-if-a-value-in-the-file-changes) (*Verified*) |
| on Oncentra, give the Central Axis channel number 1 | nothing checks the channel number | [10.6](#106-elekta-oncentra-files) |
| make sure no needles cross | nothing checks this | [11.11](#1111-things-nothing-checks) |
| give the Central Axis zero radiation time | nothing reads the radiation times. Both samples give it 222.8 s | [6.3](#63-inside-the-plan-rp) (*Verified*) |
| a selected needle turns from blue to purple | on the Channels tab, needles are teal and the selected one is blue | [17.2](#172-how-every-tab-works) (*Verified*) |
| the Export tab shows the orientation notch removed from the cylinder | the notch is added on, as a raised bar | [11.5](#115-cylinderpy-and-notchpy-the-solid-cylinder) (*Verified*) |
| Export Mesh saves an STL | it offers STL or STEP | [17.7](#177-export_viewpy-the-export-tab) |
| Collar Thickness "changes the diameter of the collar" | it is the collar's wall thickness, added on each side | [11.5](#115-cylinderpy-and-notchpy-the-solid-cylinder) |
| (no description of *Clear Tandem* on the Channels tab) | it does nothing | [17.5](#175-channels_viewpy-the-channels-tab) |
| lists *Dead Space* in the layout, but never explains it | it pushes each needle tip out, for the model and the PDF's lengths | [11.6](#116-channelpy-one-tube-per-needle) |
| refers to "Section 4.5 Channels" | Channels is the manual's own section 4.4 | — |

What the manual gets right, and the code confirms: after an import the app switches to the Export
tab; the Export tab's labels match the code exactly; *Show Tandem* is only available when there is
a tandem; the mouse controls; and an imported tandem must be a STEP file.

### 19.3 Things nothing checks

- **That the manual keeps up with the code.** The differences above are written down here and in
  §6.5 of the source of truth, not in the manual.
- **This folder is inherited from upstream and is never edited** (AGENTS.md). Corrections go in
  the source of truth instead.
