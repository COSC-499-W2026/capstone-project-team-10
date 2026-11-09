"""The question the Cylinder and Tandem tabs ask before Update or Delete changes a saved template."""

from PySide6.QtWidgets import QMessageBox


def template_change_dialog(title: str, question: str) -> QMessageBox:
    """The dialog Update and Delete ask with. Cancel is the default, so pressing Return changes nothing.

    It has no parent, like the app's other dialogs: parented to the tab it inherited the main
    window's light stylesheet, and its dark-mode white text could not be read.
    """
    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Icon.Question)
    dialog.setWindowTitle(title)
    dialog.setText(question)
    dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
    dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)
    return dialog


def ask_to_change(title: str, question: str) -> bool:
    """Ask the clinician to confirm a change to a saved template, with Cancel the default."""
    return template_change_dialog(title, question).exec() == QMessageBox.StandardButton.Yes
