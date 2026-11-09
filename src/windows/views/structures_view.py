from PySide6.QtCore import QEvent, QObject, Qt, QSignalBlocker, QRect, QTimer, Signal
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QColorDialog, QComboBox, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QSlider, QVBoxLayout, QStyledItemDelegate, QStyleOptionViewItem,
)

from classes.app import get_app
from classes.dicom.structure_list import StructureListRow, anatomy_structures, structure_list_rows
from classes.dicom.structures import Structure, StructureType
from windows.views.custom_view import CustomView
from windows.models.structures_model import StructureDisplayMode


class CollisionWarningDelegate(QStyledItemDelegate):
    """Keep native checkbox/list behavior and a separate clickable warning region."""
    activated = Signal(int)

    @staticmethod
    def warning_rect(option: QStyleOptionViewItem) -> QRect:
        width = 2 * option.fontMetrics.height()
        return QRect(option.rect.right() - width, option.rect.top(), width, option.rect.height())

    def paint(self, painter, option, index):
        content = QStyleOptionViewItem(option)
        warned = bool(index.data(Qt.UserRole + 1))
        if warned:
            content.rect.adjust(0, 0, -self.warning_rect(option).width(), 0)
        super().paint(painter, content, index)
        if warned:
            painter.save()
            painter.setPen(QColor('#c62828'))
            font = painter.font()
            font.setBold(True)
            font.setPixelSize(option.fontMetrics.height())
            painter.setFont(font)
            painter.drawText(self.warning_rect(option), Qt.AlignCenter, '!')
            painter.restore()

    def editorEvent(self, event, model, option, index):
        if index.data(Qt.UserRole + 1):
            if (event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease)
                    and event.button() == Qt.LeftButton
                    and self.warning_rect(option).contains(event.position().toPoint())):
                if event.type() == QEvent.MouseButtonRelease:
                    self.activated.emit(index.data(Qt.UserRole))
                return True
            if event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.activated.emit(index.data(Qt.UserRole))
                return True
        return super().editorEvent(event, model, option, index)


class StructuresView(CustomView):
    """Control display-only anatomy independently of the read-only Import inventory."""

    def __init__(self):
        super().__init__()
        # viewswidget paints color rgba(240, 245, 250). Cylinder labels override it
        # with this same rule so copy stays readable on the pale sidebar.
        self.setStyleSheet("color: rgb(0, 0, 0);")
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
        self.change_colour_button = QPushButton("Change colour", self)
        self.change_colour_button.setToolTip("Change the selected structure colour")
        controls.addWidget(self.change_colour_button)
        self.hide_all_button = QPushButton("Hide all", self)
        self.hide_all_button.setToolTip("Hide every listed structure")
        self.hide_all_button.setEnabled(False)
        controls.addWidget(self.hide_all_button)
        layout.addLayout(controls)
        self.surface_mode.currentTextChanged.connect(lambda text: model.set_mode(StructureDisplayMode(text)))
        self.surface_opacity.valueChanged.connect(self.action_change_opacity)
        self.change_colour_button.clicked.connect(self.action_change_colour)
        self.hide_all_button.clicked.connect(self.action_hide_all)
        model.opacity_changed.connect(self.update_opacity_controls)
        model.color_changed.connect(self.update_structure_swatch)
        self.structure_list = QListWidget(self)
        self.structure_list.setObjectName("structure_list")
        self.structure_list.setWordWrap(True)
        self.structure_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.structure_list.setStyleSheet("background-color: white; color: black;")
        layout.addWidget(self.structure_list)
        self._collision_roi: int | None = None
        self.collision_delegate = CollisionWarningDelegate(self.structure_list)
        self.structure_list.setItemDelegate(self.collision_delegate)
        self.collision_delegate.activated.connect(self.show_collision)
        self.collision_status = QLabel(self)
        self.collision_status.setWordWrap(True)
        layout.addWidget(self.collision_status)
        self.collision_toast = QLabel(self)
        self.collision_toast.setWordWrap(True)
        self.collision_toast.setStyleSheet('background: #fff0ee; color: #a31515; padding: 8px; border: 1px solid #c62828;')
        self.collision_toast.hide()
        layout.addWidget(self.collision_toast)
        self.toast_timer = QTimer(self)
        self.toast_timer.setSingleShot(True)
        self.toast_timer.setInterval(6000)
        self.toast_timer.timeout.connect(self.collision_toast.hide)
        get_app().window.collisionmodel.changed.connect(self.update_collision_warnings)
        get_app().window.collisionmodel.highlight_changed.connect(self.clear_collision_toast)
        self._just_selected = False
        self._checkbox_toggled = False
        self._mouse_selecting = False
        self.structure_list.viewport().installEventFilter(self)
        self.structure_list.itemChanged.connect(self.action_toggle_structure)
        self.structure_list.itemClicked.connect(self.action_click_structure)
        self.structure_list.currentItemChanged.connect(self.action_current_structure)
        model.changed.connect(self.action_update_structure_list)
        self.update_opacity_controls()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """Tell a mouse press apart from a keyboard move before the list handles it.

        The press clears the same-click guard, then the list may set it again if
        this press changes the current row. Arrow keys never come through here,
        so they leave the guard clear and the next click can drop the highlight.
        """
        if watched is self.structure_list.viewport():
            if event.type() == QEvent.Type.MouseButtonPress:
                self._mouse_selecting = True
                self._just_selected = False
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self._mouse_selecting = False
        return super().eventFilter(watched, event)

    def action_update_structure_list(self):
        """Show ROI visibility controls and explain unavailable contours.

        The same ROI numbers keep the same list items. A checkbox click emits
        changed while that item is still in use, and clearing the list would
        delete it before the click finishes.
        """
        model = get_app().window.structuresmodel
        with QSignalBlocker(self.surface_mode):
            self.surface_mode.setCurrentText(model.mode.value)
        structures = anatomy_structures(tuple(model.structures.values()))
        rows = structure_list_rows(structures)
        current = self.structure_list.currentItem()
        selected = current.data(Qt.UserRole) if current is not None else None
        shown = tuple(
            self.structure_list.item(index).data(Qt.UserRole)
            for index in range(self.structure_list.count())
        )
        incoming = tuple(structure.roi_number for structure in structures)
        with QSignalBlocker(self.structure_list):
            if shown == incoming:
                for index, (structure, row) in enumerate(zip(structures, rows)):
                    self._write_structure_item(
                        self.structure_list.item(index), structure, row)
            else:
                self.structure_list.clear()
                for structure, row in zip(structures, rows):
                    item = QListWidgetItem()
                    self._write_structure_item(item, structure, row)
                    self.structure_list.addItem(item)
                    # After hide_all the model clears the highlight; do not put
                    # the previous row back or the viewport keeps selection colour.
                    if structure.roi_number == selected and (
                            selected in model.visible or model.highlighted == selected):
                        self.structure_list.setCurrentItem(item)
        self.hide_all_button.setEnabled(bool(model.visible))
        self.update_opacity_controls()
        self.update_collision_warnings()

    def _write_structure_item(
        self, item: QListWidgetItem, structure: Structure, row: StructureListRow,
    ) -> None:
        """Fill one row from the model. Caller blocks list signals."""
        model = get_app().window.structuresmodel
        roi = structure.roi_number
        item.setData(Qt.UserRole, roi)
        item.setFlags(
            item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        pending_visible = model.mode != StructureDisplayMode.OUTLINES and roi in model.pending
        requested = model.is_displayed(roi) or (roi in model.visible and pending_visible)
        item.setCheckState(Qt.Checked if requested else Qt.Unchecked)
        reason = model.status_message(roi)
        text = f"{row.label}  {row.category}"
        if reason:
            text = f"{text}\n{reason}"
        item.setText(text)
        item.setToolTip(reason or "Show or hide this structure")
        if roi in model.unavailable:
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
        elif reason and not model.is_displayed(roi) and not pending_visible:
            item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
        swatch = QPixmap(12, 12)
        swatch.fill(QColor(*model.color_for(roi)))
        item.setIcon(QIcon(swatch))

    def action_hide_all(self):
        """Hide every listed structure. The list refresh unchecks the rows.

        Clear the current row first so the rebuild cannot re-select it and put
        the highlight back on an organ that just left the preview.
        """
        with QSignalBlocker(self.structure_list):
            self.structure_list.setCurrentItem(None)
        get_app().window.structuresmodel.hide_all()

    def action_toggle_structure(self, item: QListWidgetItem):
        """Keep anatomy visibility separate from printable shapes."""
        self._checkbox_toggled = True
        get_app().window.structuresmodel.set_visible(
            item.data(Qt.UserRole), item.checkState() == Qt.Checked)

    def action_click_structure(self, item: QListWidgetItem):
        """Toggle the highlight when the click is on a row that was already current.

        A checkbox click emits itemChanged first and must leave the highlight
        alone. The mouse press that first moves the current row also emits
        itemClicked. That click is ignored, because the row change already
        applied the highlight. Keyboard movement does not set the guard, so
        the next click on that row can clear the highlight.
        """
        just_selected = self._just_selected
        self._just_selected = False
        if self._checkbox_toggled:
            self._checkbox_toggled = False
            return
        if just_selected:
            return
        model = get_app().window.structuresmodel
        roi = item.data(Qt.UserRole)
        model.set_highlight(None if model.highlighted == roi else roi)

    def action_current_structure(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None):
        """Follow the current row into the preview highlight and the opacity slider.

        The guard is set only while a mouse press is changing the row. Arrow
        keys change the row too, and they must not arm the guard.
        """
        self.update_opacity_controls()
        roi = None if current is None else current.data(Qt.UserRole)
        model = get_app().window.structuresmodel
        if model.highlighted != roi:
            model.set_highlight(roi)
            if self._mouse_selecting:
                self._just_selected = True

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

    def action_change_colour(self):
        """Open a colour dialog for the current row. Cancel leaves the colour."""
        item = self.structure_list.currentItem()
        if item is None:
            return
        roi = item.data(Qt.UserRole)
        current = get_app().window.structuresmodel.color_for(roi)
        picked = QColorDialog.getColor(QColor(*current), self, "Choose structure colour")
        self.action_apply_colour(picked)

    def action_apply_colour(self, colour: QColor | None):
        """Store a picked colour, or ignore a cancelled dialog."""
        item = self.structure_list.currentItem()
        if item is None or colour is None or not colour.isValid():
            return
        model = get_app().window.structuresmodel
        model.set_color(item.data(Qt.UserRole), (colour.red(), colour.green(), colour.blue()))
        model.set_highlight(None)
        self._just_selected = False

    def update_structure_swatch(self, roi: int, rgb: tuple[int, int, int]):
        """Repaint one list swatch without rebuilding the rows."""
        with QSignalBlocker(self.structure_list):
            for index in range(self.structure_list.count()):
                item = self.structure_list.item(index)
                if item.data(Qt.UserRole) == roi:
                    swatch = QPixmap(12, 12)
                    swatch.fill(QColor(*rgb))
                    item.setIcon(QIcon(swatch))
                    return

    def action_change_opacity(self, value: int):
        item = self.structure_list.currentItem()
        if item is not None:
            get_app().window.structuresmodel.set_opacity(item.data(Qt.UserRole), value / 100)

    def update_collision_warnings(self):
        model = get_app().window.collisionmodel
        with QSignalBlocker(self.structure_list):
            for index in range(self.structure_list.count()):
                item = self.structure_list.item(index)
                roi = item.data(Qt.UserRole)
                hits = model.collisions.get(roi, ())
                item.setData(Qt.UserRole + 1, hits)
                reason = get_app().window.structuresmodel.status_message(roi)
                if hits:
                    reason += '\nPossible collision detected. ' + ', '.join(hits) + '. Click ! or press Enter.'
                elif roi in model.unchecked:
                    reason += '\nCollision not checked. ' + model.unchecked[roi]
                item.setToolTip(reason.strip() or 'Show or hide this structure')
        status = 'Checking needle–organ intersections…' if model.busy else 'Approximate organ check; targets and BODY excluded.'
        if not any(s.category == StructureType.ORGAN for s in get_app().window.structuresmodel.structures.values()):
            status = 'No organs to check. Targets and BODY are excluded.'
        if model.highlighted:
            status += ' Red needles indicate possible contact. Click the same warning to clear.'
        if model.unchecked:
            status += f' {len(model.unchecked)} organ(s) not checked; see row tooltips.'
        self.collision_status.setText(status)

    def show_collision(self, roi: int):
        model = get_app().window.collisionmodel
        selected = None if self._collision_roi == roi and model.highlighted else roi
        self._collision_roi = selected
        model.highlight(selected)
        self.update_collision_warnings()
        if model.highlighted:
            self.collision_toast.setText('Possible collision detected. ' + ', '.join(model.highlighted))
            self.collision_toast.show()
            self.toast_timer.start()

    def clear_collision_toast(self):
        if not get_app().window.collisionmodel.highlighted:
            self._collision_roi = None
            self.toast_timer.stop()
            self.collision_toast.hide()

    def on_close(self):
        """Clear the highlight when leaving the Structures tab."""
        get_app().window.structuresmodel.set_highlight(None)
        get_app().window.collisionmodel.highlight(None)
        super().on_close()
