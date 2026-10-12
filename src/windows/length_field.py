"""Keep a length in millimetres while a Qt spin box displays mm or cm."""

from enum import Enum

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QDoubleSpinBox


class LengthUnit(Enum):
    MILLIMETRES = "mm"
    CENTIMETRES = "cm"

    @property
    def millimetres_per_unit(self) -> float:
        return 10.0 if self is LengthUnit.CENTIMETRES else 1.0


class LengthField:
    """Retain the exact mm value when Qt rounds a programmatic display update.

    User edits replace that value. Changing units only renders it, with signals blocked,
    so repeated switches never read a rounded display back into the design.
    """

    def __init__(self, spinbox: QDoubleSpinBox):
        self.spinbox = spinbox
        self.unit = LengthUnit.MILLIMETRES
        self.millimetres = spinbox.value()
        self.minimum_mm = spinbox.minimum()
        self.maximum_mm = spinbox.maximum()
        self.step_mm = spinbox.singleStep()
        self.decimals_mm = spinbox.decimals()
        spinbox.valueChanged.connect(self._record_edit)

    def _record_edit(self, value: float) -> None:
        self.millimetres = value * self.unit.millimetres_per_unit

    def set_millimetres(self, value: float) -> None:
        self.millimetres = min(self.maximum_mm, max(self.minimum_mm, value))
        with QSignalBlocker(self.spinbox):
            self.spinbox.setValue(self.millimetres / self.unit.millimetres_per_unit)

    def set_unit(self, unit: LengthUnit) -> None:
        self.unit = unit
        factor = unit.millimetres_per_unit
        with QSignalBlocker(self.spinbox):
            self.spinbox.setDecimals(self.decimals_mm + (unit is LengthUnit.CENTIMETRES))
            self.spinbox.setRange(self.minimum_mm / factor, self.maximum_mm / factor)
            self.spinbox.setSingleStep(self.step_mm / factor)
            self.spinbox.setSuffix(f" {unit.value}")
            self.spinbox.setValue(self.millimetres / factor)
