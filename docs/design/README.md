# Design

> **This file is part of the documentation set**, the markdown files the team owns.
> The whole set is reviewed on every pull request and updated in the same PR when affected. Update this file when the UI changes, or a mock is added or superseded.
> See §9.0 of [the source of truth](../project/COSC499-TEAM10-PROJECT-DOCS.md).

The Cylinder tab has one Units selector for diameter, length, collar thickness, collar
height, and notch width, depth and height. It starts in mm; choosing cm changes values,
suffixes, steps and limits.

Since 2026-10-15 the tab also has *Add Notch*, which greys out the notch fields when unticked,
and *Notch Angle* in degrees clockwise from Anterior as the reference sheet draws it. The
labels follow the UI copy rule, with no colon or dash. The notch controls sit below Units, and
*Tip Shape*, a Dome or Flat dropdown that Units does not affect, sits below them.
*Verified* by offscreen widget tests; no mock was drawn for them.
Apply, DICOM import and config files retain mm internally. The choice is not saved.
*Verified* by offscreen widget tests and Ahab's supplied cm screenshot. The image was
provided in chat and was not saved as a repository artifact.
See [source of truth §5.6](../project/COSC499-TEAM10-PROJECT-DOCS.md#56-views-and-the-qt-ui-layer)
for the controls and precision.
Since 2026-10-19 the Cylinder tab scrolls up and down, as the Channels tab does: at the default
770 × 472 window its spin boxes had been squeezed to 16 px, with the bottoms of the values cut off.
Nothing scrolls sideways. *Verified* by offscreen tests and in the running app (§7.12).

Below *Apply Settings*, a Templates group saves the tab's settings under a name: a name field, a
note field, the list of saved templates and *Save as Template*. Hovering a template shows its
note, dates and a one-line summary. As with the needle templates, a refused save or an unreadable
file is explained in a status line beside the controls, not a dialog. *Load* fills the tab from
the selected template but builds nothing: the status line says to press *Apply Settings*, so the
physicist checks the values first, and loading never moves an imported plan's needles by itself.
*Update* and *Delete* each ask first, naming the template, with Cancel the default. The question
is a system dialog, so it follows the system's light or dark colours; parented to the tab it had
inherited the tab's light background under dark-mode white text and could not be read. The group's colours match
the tab's, and its buttons look like *Apply Settings*. *Verified* by offscreen tests and in the
running app.

*Reasoned from viewport code, PRs #78/#79/#81:* left-drag rotates, right/middle-drag pans,
and scrolling zooms proportionally. Click jitter is tolerated; a drag never selects on
release. These are project bindings, not a universal medical-software standard.

The dark viewport has white millimetre labels and faint grid lines on three outer walls,
with no intersecting planes. The top-right **XYZ grid (mm)** control is blue when checked;
the independent **Central axis** control below it is amber when checked and shows a dashed
local-Z reference above solids. Both are disabled when their reference is unavailable.
Toggling preserves the camera; preferences survive redraws but are not saved to config.
Neither overlay is selectable or exported. Details and native-run limitations are in
[§5.7](../project/COSC499-TEAM10-PROJECT-DOCS.md#57-the-3d-viewport).

The Channels tab has a Selected Channel group below the list. It is enabled only while a
channel is selected, shows that channel's diameter, and gives it its own diameter with
*Apply to Channel*. *Use Channels Diameter* returns it to the tab's Channels Diameter, and
Apply on the tab keeps any own diameter. The whole tab now scrolls: at the default 770 × 472
window the group is below the fold and the list shows about four rows, where without the
scroll area the spin boxes above were squeezed unreadable. *Verified* by offscreen widget tests
and a render of the shown window. A screenshot of it is linked from Ahab's week 6 log.

Each row of the Channels list shows its channel's status. Own diameter is bold on amber,
disabled is italic on grey, and the tandem is bold italic on blue, with a legend under the
list. Every colour has its own bold and italic pair, so colour is never the only cue (WCAG
1.4.1, Use of Color), and hovering a row names its status and diameter. A selected row shows
the system highlight instead of its colour, and keeps its font. *Verified* by offscreen tests
and a render. A screenshot of it is linked from Ahab's week 6 log.

The Selected Channel group also holds the needle templates: a name field with *Save as
Template*, a list of saved templates with *Apply Template*, and a status line. A refused save
or an unreadable template file is explained in the status line beside the controls rather
than in a dialog, so the clinician sees why without leaving the tab, and a file brachify cannot
read never stops it starting. *Verified* by offscreen widget tests. A screenshot of it is linked from Ahab's week 6 log.

The Structures page (index 5, navigation button under Import) lists checkable anatomy
ROIs with their category and DICOM colour; Import's inventory remains read-only. The mode
dropdown applies Surface/Outlines/Both to the whole list and defaults to Surface without
automatic contour fallback. ORGAN/TUMOUR ROIs start requested visible; OTHER, including
BODY, requires selection. A mode tooltip explains the approximate 1 mm / 2 mm EXTERNAL grid.

Loading and failure reasons appear as wrapped row text and tooltips. Pending rows stay
checkable for hiding. In Surface mode a failed surface is unchecked; permanent unavailability
disables the row. The 0–100% opacity slider applies only to the selected ROI (default 45%) and commits
a drag on release. Without selection it is disabled. Opacity updates retain actors and list
items; model changes rebuild rows while restoring selection by ROI number.
*Reasoned from #125 code and covered by offscreen widgets/native-actor tests; no fresh native
screenshot or usability evaluation is claimed.* See [§5.6](../project/COSC499-TEAM10-PROJECT-DOCS.md#56-views-and-the-qt-ui-layer)
and [§5.7](../project/COSC499-TEAM10-PROJECT-DOCS.md#57-the-3d-viewport).
