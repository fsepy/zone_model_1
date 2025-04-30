# coding: utf-8
from concurrent.futures import ThreadPoolExecutor

from PySide6 import QtCore, QtWidgets, QtGui
from qfluentwidgets import FluentIcon, NavigationItemPosition, FluentWindow, SplashScreen

from .common import resource
from .common.interface_gallery import GalleryInterface
from .interfaces import *
from .project_info import __display_name__

__kept_imports = (resource,)


class MainWindow(FluentWindow):
    def __init__(self, debug: bool = False):
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=2)  # used for update database
        self.future = None  # used for update database
        self.init_window()
        self.debug = debug

        self.setting_interface = SettingInterface(self)

        self.interface_heat_release_rate = FuelHRRInterface(self)
        self.addSubInterface(self.interface_heat_release_rate, FluentIcon.DOCUMENT, 'Fuel HRR')
        self.interface_heat_transfer = HeatTransferInterface(self)
        self.addSubInterface(self.interface_heat_transfer, FluentIcon.DOCUMENT, 'Heat Transfer')

        self.addSubInterface(self.setting_interface, FluentIcon.SETTING, 'Settings', NavigationItemPosition.BOTTOM)
        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(False)
        self.navigationInterface.setExpandWidth(200)
        self.setCustomBackgroundColor(QtGui.QColor(240, 244, 249), QtGui.QColor(32, 32, 32))

        # add items to navigation interface
        self.splash_screen.finish()

        # self.navigationInterface.panel.expandWidth = 180
        self.navigationInterface.panel.expand(False)

    def init_window(self):
        desktop = QtWidgets.QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()

        self.resize(1350 if 1350 < (w - 200) else w - 200, 900 if 900 < (h - 200) else h - 200)
        self.setMinimumWidth(600)
        self.setWindowIcon(QtGui.QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle(__display_name__)

        # create splash screen
        self.splash_screen = SplashScreen(QtGui.QIcon(':/gallery/images/logo.png'), self)
        self.splash_screen.setIconSize(QtCore.QSize(106, 106))
        self.splash_screen.raise_()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()
        QtWidgets.QApplication.processEvents()

    def switch_to_sample(self, route_key, index):
        """ switch to sample """
        interfaces = self.findChildren(GalleryInterface)
        for w in interfaces:
            if w.objectName() == route_key:
                self.stackedWidget.setCurrentWidget(w, False)
                w.scrollToCard(index)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splash_screen'):
            self.splash_screen.resize(self.size())
