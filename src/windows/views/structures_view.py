from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QSlider, QVBoxLayout

from classes.app import get_app
from classes.dicom.structure_list import structure_list_rows
from windows.views.custom_view import CustomView
from windows.models.structures_model import StructureDisplayMode


class StructuresView(CustomView):
    """Control display-only anatomy independently of the read-only Import inventory."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.instructions = QLabel("Select structures to display beside the probe. Surface previews are approximate.", self)
        self.instructions.setWordWrap(True)
        layout.addWidget(self.instructions)
        model = get_app().window.structuresmodel
        controls = QVBoxLayout()
        opacity_controls = QHBoxLayout()
        self.surface_mode = QComboBox(self)
        self.surface_mode.addItems([mode.value for mode in StructureDisplayMode])
        self.surface_mode.setCurrentText(model.mode.value)
        self.surface_mode.setToolTip(
            "Approximate preview on a 1 mm grid, or 2 mm for external body contours. "
            "Sampling can move boundaries; grid-aligned contours can expand by half a grid step.")
        self.opacity_label = QLabel(self)
        self.surface_opacity = QSlider(Qt.Horizontal, self)
        self.surface_opacity.setRange(0, 100)
        self.surface_opacity.setTracking(False)
        self.surface_opacity.setStyleSheet(
            "QSlider::groove:horizontal { background: #8393a2; height: 4px; }"
            "QSlider::handle:horizontal { background: #245b80; width: 12px;"
            " margin: -4px 0; border-radius: 6px; }")
        self.surface_opacity.setToolTip("Opacity of the selected structure")
        controls.addWidget(self.surface_mode)
        opacity_controls.addWidget(self.opacity_label)
        opacity_controls.addWidget(self.surface_opacity, 1)
        controls.addLayout(opacity_controls)
        layout.addLayout(controls)
        self.surface_mode.currentTextChanged.connect(lambda text: model.set_mode(StructureDisplayMode(text)))
        self.surface_opacity.valueChanged.connect(self.action_change_opacity)
        model.opacity_changed.connect(self.update_opacity_controls)
        self.structure_list = QListWidget(self)
        self.structure_list.setObjectName("structure_list")
        self.structure_list.setWordWrap(True)
        self.structure_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.structure_list.setStyleSheet("background-color: white; color: black;")
        layout.addWidget(self.structure_list)
        self.structure_list.itemChanged.connect(self.action_toggle_structure)
        self.structure_list.currentItemChanged.connect(self.update_opacity_controls)
        model.changed.connect(self.action_update_structure_list)
        self.update_opacity_controls()

    def action_update_structure_list(self):
        """Show ROI visibility controls and explain unavailable contours."""
        model = get_app().window.structuresmodel
        with QSignalBlocker(self.surface_mode):
            self.surface_mode.setCurrentText(model.mode.value)
        current = self.structure_list.currentItem()
        selected = current.data(Qt.UserRole) if current is not None else None
        structures = tuple(model.structures.values())
        with QSignalBlocker(self.structure_list):
            self.structure_list.clear()
            for structure, row in zip(structures, structure_list_rows(structures)):
                item = QListWidgetItem(f"{row.label}  {row.category}")
                roi = structure.roi_number
                item.setData(Qt.UserRole, roi)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                requested = model.is_displayed(roi) or (roi in model.visible and roi in model.pending)
                item.setCheckState(Qt.Checked if requested else Qt.Unchecked)
                reason = model.status_message(roi)
                if reason:
                    item.setText(f"{row.label}  {row.category}\n{reason}")
                item.setToolTip(reason or "Show or hide this structure")
                if roi in model.unavailable:
                    item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                elif reason and not model.is_displayed(roi) and roi not in model.pending:
                    item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
                swatch = QPixmap(12, 12)
                swatch.fill(QColor(*row.color))
                item.setIcon(QIcon(swatch))
                self.structure_list.addItem(item)
                if roi == selected:
                    self.structure_list.setCurrentItem(item)
        self.update_opacity_controls()

    def action_toggle_structure(self, item: QListWidgetItem):
        """Keep anatomy visibility separate from printable shapes."""
        get_app().window.structuresmodel.set_visible(
            item.data(Qt.UserRole), item.checkState() == Qt.Checked)

    def update_opacity_controls(self):
        item = self.structure_list.currentItem()
        self.surface_opacity.setEnabled(item is not None)
        if item is None:
            self.opacity_label.setText("Select a structure to change opacity")
            return
        opacity = get_app().window.structuresmodel.opacity_for(item.data(Qt.UserRole))
        with QSignalBlocker(self.surface_opacity):
            self.surface_opacity.setValue(round(opacity * 100))
        self.opacity_label.setText(f"Opacity {round(opacity * 100)}%")

    def action_change_opacity(self, value: int):
        item = self.structure_list.currentItem()
        if item is not None:
            get_app().window.structuresmodel.set_opacity(item.data(Qt.UserRole), value / 100)
