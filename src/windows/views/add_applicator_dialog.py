from collections.abc import Callable

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QLabel, QLineEdit

from classes.mesh.helper import MAX_THETA_DEGREES, CustomNeedleSpec

RANGE_MM = 300.0  # the longest cylinder the Cylinder tab allows


class AddApplicatorDialog(QDialog):
    """Asks for a custom applicator's name, start, lengths and bend (mm and degrees), with no parent like MoveChannelDialog.

    OK checks the numbers with the model's own rules and stays open, showing the reason, until they pass.
    """

    def __init__(self, label: str, check: Callable[[CustomNeedleSpec], str]):
        super().__init__()
        self.check = check
        self.setWindowTitle("Add Applicator")
        form = QFormLayout(self)
        form.setSizeConstraint(QFormLayout.SizeConstraint.SetFixedSize)
        self.edit_label = QLineEdit(label)
        self.spin_x = self.make_spin_box(0.0, -RANGE_MM)
        self.spin_y = self.make_spin_box(0.0, -RANGE_MM)
        self.spin_length1 = self.make_spin_box(10.0, 0.0)
        self.spin_length2 = self.make_spin_box(10.0, 0.0)
        self.spin_radius = self.make_spin_box(10.0, 0.0)
        self.spin_theta = self.make_spin_box(0.0, 0.0, MAX_THETA_DEGREES, " °")
        self.spin_phi = self.make_spin_box(0.0, 0.0, 360.0, " °")
        for name, widget in (("Name", self.edit_label), ("Start X", self.spin_x), ("Start Y", self.spin_y),
                             ("Length 1 inside the cylinder", self.spin_length1), ("Length 2 out into tissue", self.spin_length2),
                             ("Bend radius", self.spin_radius), ("Theta tilt from the axis", self.spin_theta),
                             ("Phi direction from X towards Y", self.spin_phi)):
            form.addRow(name, widget)
        self.label_error = QLabel()
        self.label_error.setWordWrap(True)
        self.label_error.setMinimumWidth(360)
        self.label_error.setHidden(True)
        form.addRow(self.label_error)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.try_accept)
        self.buttons.rejected.connect(self.reject)
        form.addRow(self.buttons)

    def make_spin_box(self, value: float, minimum: float, maximum: float = RANGE_MM, suffix: str = " mm") -> QDoubleSpinBox:
        spin_box = QDoubleSpinBox()
        spin_box.setRange(minimum, maximum)
        spin_box.setDecimals(3)
        spin_box.setSuffix(suffix)
        spin_box.setValue(value)
        return spin_box

    def spec(self) -> CustomNeedleSpec:
        return CustomNeedleSpec(label=self.edit_label.text(), x=self.spin_x.value(), y=self.spin_y.value(),
                                length1=self.spin_length1.value(), length2=self.spin_length2.value(),
                                radius=self.spin_radius.value(), theta=self.spin_theta.value(), phi=self.spin_phi.value())

    def try_accept(self) -> None:
        error = self.check(self.spec())
        self.label_error.setText(error)
        self.label_error.setHidden(not error)
        if not error: self.accept()
