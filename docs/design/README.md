# Design

> **This file is part of the documentation set**, the markdown files the team owns.
> The whole set is reviewed on every pull request and updated in the same PR when affected. Update this file when the UI changes, or a mock is added or superseded.
> See §9.0 of [the source of truth](../project/COSC499-TEAM10-PROJECT-DOCS.md).

The Cylinder tab has one Units selector for diameter, length, collar thickness and
collar height. It starts in mm; choosing cm changes values, suffixes, steps and limits.
Apply, DICOM import and config files retain mm internally. The choice is not saved.
*Verified* by offscreen widget tests and Ahab's supplied cm screenshot. The image was
provided in chat and was not saved as a repository artifact.
See [source of truth §5.6](../project/COSC499-TEAM10-PROJECT-DOCS.md#56-views-and-the-qt-ui-layer)
for the controls and precision.
