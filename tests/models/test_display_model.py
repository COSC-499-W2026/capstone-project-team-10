"""Exercise DisplayModel.replace_shapes, which makes one type's shapes in the 3D view exactly the ones a model passes."""
from __future__ import annotations

from OCC.Core.TopoDS import TopoDS_Shape

from windows.models.display_model import DisplayModel
from windows.models.shape_model import ShapeModel, ShapeTypes


def shape(label: str, shape_type: ShapeTypes, enabled: bool = True) -> ShapeModel:
    """Make a ShapeModel around an empty solid, with the given label, type and enabled flag. A helper, not a test."""
    made = ShapeModel(label=label, shape=TopoDS_Shape(), shape_type=shape_type)
    made.enabled = enabled
    return made


def test_replacing_channel_shapes_drops_a_channel_that_is_gone_and_leaves_other_types_alone() -> None:
    """Check a channel label missing from the new list leaves the view, a listed one is replaced, and the cylinder stays.

    Fails if the missing channel's shape is kept, which is how a removed applicator stayed drawn
    in the 3D view (§7.25), if a listed channel keeps its old ShapeModel, or if the cylinder or
    any shape of another type is dropped with the channels. The clinician would check a viewport
    that no longer matches the device the export cuts.
    """
    display = DisplayModel()
    cylinder, removed, kept = shape("cylinder", ShapeTypes.CYLINDER), shape("Removed", ShapeTypes.CHANNEL), shape("Kept", ShapeTypes.CHANNEL)
    display.add_shapes([cylinder, removed, kept])
    rebuilt = shape("Kept", ShapeTypes.CHANNEL)

    display.replace_shapes(ShapeTypes.CHANNEL, [rebuilt])

    assert display.shapes == {"cylinder": cylinder, "Kept": rebuilt}


def test_a_disabled_shape_in_the_replacement_is_not_shown() -> None:
    """Check a listed shape marked not enabled is left out of the view, as add_shapes leaves it out.

    Fails if a disabled channel is drawn because it was in the list. A needle the clinician
    disabled, and the export does not cut, would still be drawn.
    """
    display = DisplayModel()
    display.add_shapes([shape("Disabled", ShapeTypes.CHANNEL)])

    display.replace_shapes(ShapeTypes.CHANNEL, [shape("Disabled", ShapeTypes.CHANNEL, enabled=False), shape("Shown", ShapeTypes.CHANNEL)])

    assert list(display.shapes) == ["Shown"]
