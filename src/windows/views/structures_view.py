from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout

from classes.app import get_app
from classes.dicom.structure_list import structure_list_rows
from windows.views.custom_view import CustomView


class StructuresView(CustomView):
    """Control display-only anatomy independently of the read-only Import inventory."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.instructions = QLabel("Select structures to display beside the probe.", self)
        self.instructions.setWordWrap(True)
        layout.addWidget(self.instructions)
        self.structure_list = QListWidget(self)
        self.structure_list.setObjectName("structure_list")
        self.structure_list.setStyleSheet("background-color: white; color: black;")
        layout.addWidget(self.structure_list)
        self.structure_list.itemChanged.connect(self.action_toggle_structure)
        get_app().window.structuresmodel.changed.connect(self.action_update_structure_list)

    def action_update_structure_list(self):
        """Show ROI visibility controls and explain unavailable contours."""
        model = get_app().window.structuresmodel
        structures = tuple(model.structures.values())
        with QSignalBlocker(self.structure_list):
            self.structure_list.clear()
            for structure, row in zip(structures, structure_list_rows(structures)):
                item = QListWidgetItem(f"{row.label}  {row.category}")
                roi = structure.roi_number
                item.setData(Qt.UserRole, roi)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked if model.is_displayed(roi) else Qt.Unchecked)
                reason = model.status_message(roi)
                if reason:
                    item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                    item.setToolTip(reason)
                else:
                    item.setToolTip("Show or hide this DICOM contour outline")
                swatch = QPixmap(12, 12)
                swatch.fill(QColor(*row.color))
                item.setIcon(QIcon(swatch))
                self.structure_list.addItem(item)

    def action_toggle_structure(self, item: QListWidgetItem):
        """Keep anatomy visibility separate from printable shapes."""
        get_app().window.structuresmodel.set_visible(
            item.data(Qt.UserRole), item.checkState() == Qt.Checked)
