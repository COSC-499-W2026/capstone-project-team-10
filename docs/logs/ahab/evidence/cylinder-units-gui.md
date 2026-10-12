# Cylinder units GUI evidence, 2026-10-10

Ahab supplied a screenshot in chat showing the Cylinder tab with diameter 3.125 cm,
length 17.3 cm, collar thickness 0.3 cm, collar height 1.2 cm, Add Collar selected and
Units set to cm. The viewport shows the cylinder, collar and needle channels. Ahab
confirmed that the original screenshot was not saved, so this record describes the
supplied image and does not replace it with a fabricated screenshot.

The following excerpt is from Ahab's supplied terminal output, preserving the relevant
lines and their order. Unrelated lines are omitted.

```text
INFO import_view: file /Users/ahabmasudsiddiqui/Desktop/capstone-project-team-10/SI_C_D30 Brachify_Ex1/ has been selected
DEBUG fileio: Found central axis at ROI 20
DEBUG navigation_model: setting page to 4
DEBUG export_view: on open
DEBUG viewport: updating viewport: ['export']
DEBUG navigation_model: setting page to 1
DEBUG cylinder_view: applying cylinder settings
DEBUG tandem_model: updating tandem height offset to 13.0
DEBUG viewport: updating viewport: ['cylinder', 'Applicator2', 'Applicator3', 'Applicator4', 'Applicator5', 'Applicator6', 'Applicator7', 'Applicator8', 'Applicator9', 'Applicator10', 'Applicator11', 'Applicator12', 'Applicator13']
Error calling Python override of QWidget::keyPressEvent(): Traceback (most recent call last):
  File "/Users/ahabmasudsiddiqui/Desktop/capstone-project-team-10/src/windows/views/viewport.py", line 106, in keyPressEvent
    if code in self._key_map:
AttributeError: 'OrbitCameraViewer3d' object has no attribute '_key_map'
```

The 13 mm offset agrees with increasing the imported 160 mm cylinder to 17.3 cm.
The key-press failure is the existing viewport bug in source of truth §7.9, outside this
units issue. The supplied log shows Export opening before the cm edit; it does not verify
Export after that edit. Ex2 and its tandem were not visually verified.

Direct desktop capture from this session was attempted with `screencapture` and failed
with `could not create image from display`. Offscreen tests verify widget/model state,
not the native viewport. No independent GUI run is claimed.
