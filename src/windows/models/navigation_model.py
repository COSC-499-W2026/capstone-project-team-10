from PySide6.QtWidgets import QVBoxLayout, QWidget

from classes.app import get_app
from classes.logger import log
from windows.views.channels_view import ChannelsView
from windows.views.cylinder_view import CylinderView
from windows.views.export_view import Export_View
from windows.views.import_view import ImportView
from windows.views.structures_view import StructuresView
from windows.views.tandem_view import TandemView


class NavigationModel():

    def __init__(self):
        log.debug(f"Navigation model initializing!")
        self.current_page = 0
        self.views = []
        self.views.append(ImportView())
        self.views.append(CylinderView())
        self.views.append(ChannelsView())
        self.views.append(TandemView())
        self.views.append(Export_View())
        # Appended, not inserted after Import: Cylinder stays views[1], Export stays views[4].
        self.views.append(StructuresView())

        # adding views to the main window from the self.views list
        app = get_app()
        window = app.window
        stacked = window.ui.viewswidget
        while stacked.count() < len(self.views):
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(0, 0, 0, 0)
            page_layout.setSpacing(0)
            stacked.addWidget(page)
        for i, view in enumerate(self.views):
            stacked.widget(i).layout().addWidget(view)

        # signals
        app.signals.viewChanged.connect(self.set_page)

        # initializing the first page
        self.views[0].on_open()
        get_app().window.ui.viewswidget.setCurrentIndex(0)

        log.debug(f"Navigation model initialized")

    def set_page(self, page:int):
        if page == self.current_page: return
        log.debug(f"setting page to {page}")
        self.views[self.current_page].on_close()
        self.current_page = page
        self.views[self.current_page].on_open()
        get_app().window.ui.viewswidget.setCurrentIndex(page)