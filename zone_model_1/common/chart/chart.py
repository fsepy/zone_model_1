from PySide6 import QtCore, QtWidgets
from qfluentwidgets import (
    RoundMenu, FluentIcon, VerticalSeparator, ScrollArea, ToolButton
)

from .common import ChartSettingCommonBase, ChartWidget
from .setting import SettingWidget
from ..mask_dialog_base import MaskDialogBase


class ChartWithSettingWidget(QtWidgets.QWidget, ChartSettingCommonBase):
    def __init__(self, parent=None):
        self.fp_fds = None
        self.current_state_is_moving_average_applied: bool = False
        super().__init__(parent)
        self._chart = ChartWidget(self)
        self._setting = SettingWidget(self)
        self._setting.widget_layout.addStretch(1)
        self._setting.widget_layout.setContentsMargins(0, 0, 12, 0)
        scroll_area = ScrollArea()
        scroll_area.setWidget(self._setting)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('background-color: transparent;')

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._chart, stretch=1)
        layout.addWidget(VerticalSeparator(self))
        layout.addSpacing(12)
        layout.addWidget(scroll_area)

        self.connect_signals()

    @property
    def chart(self) -> ChartWidget:
        return self._chart

    @property
    def setting(self) -> SettingWidget:
        return self._setting


class ChartDialog(QtWidgets.QDialog, ChartSettingCommonBase):
    def __init__(self, parent=None):
        self.fp_fds = None
        self.current_state_is_moving_average_applied: bool = False
        super().__init__(parent)
        self._chart = ChartWidget(self)
        self._setting = SettingWidget(self)
        self._setting.widget_layout.addStretch(1)
        self._setting.widget_layout.setContentsMargins(0, 0, 12, 0)
        scroll_area = ScrollArea()
        scroll_area.setWidget(self._setting)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('ScrollArea{border:none;}')

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._chart, stretch=1)
        layout.addWidget(VerticalSeparator(self))
        layout.addSpacing(12)
        layout.addWidget(scroll_area)

        self.connect_signals()

    @property
    def chart(self) -> ChartWidget:
        return self._chart

    @property
    def setting(self) -> SettingWidget:
        return self._setting

    def sizeHint(self):
        return QtCore.QSize(1200, 800)


class CompactChartDialog(QtWidgets.QDialog, ChartSettingCommonBase):
    def __init__(self, parent=None):
        self.fp_fds = None
        self.current_state_is_moving_average_applied: bool = False
        super().__init__(parent)
        self._chart = ChartWidget(self)

        self._setting = SettingWidget(self)
        self._setting.widget_layout.addStretch(1)
        self._setting.widget_layout.setContentsMargins(0, 0, 0, 0)
        scroll_area = ScrollArea()
        scroll_area.setWidget(self._setting)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('ScrollArea{border:none;}')

        self.show_x_axis_setting_button = ToolButton()
        self.show_x_axis_setting_button.setIcon(FluentIcon.MORE)

        menu_widget = QtWidgets.QWidget(self)
        menu_widget.setContentsMargins(0, 0, 0, 0)
        menu_widget_layout = QtWidgets.QHBoxLayout(menu_widget)
        menu_widget_layout.addWidget(scroll_area)
        menu_widget.setFixedHeight(600)
        menu_widget.setFixedWidth(350)
        self.menu = RoundMenu(parent=self)
        self.menu.addWidget(menu_widget, selectable=False)

        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._chart, 0, 0)
        # layout.addWidget(VerticalSeparator(self))
        # layout.addSpacing(12)
        layout.addWidget(
            self.show_x_axis_setting_button, 0, 0,
            alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignRight
        )

        self.show_x_axis_setting_button.clicked.connect(lambda: self.menu.exec(
            self.show_x_axis_setting_button.mapToGlobal(QtCore.QPoint(self.show_x_axis_setting_button.width() + 3, -12))
        ))

        self.connect_signals()

    @property
    def chart(self) -> ChartWidget:
        return self._chart

    @property
    def setting(self) -> SettingWidget:
        return self._setting

    def show_setting_dialog(self, pos):
        self.menu.exec(pos)

    def sizeHint(self):
        return QtCore.QSize(800, 600)


class MaskChartDialog(MaskDialogBase, ChartSettingCommonBase):
    """ Custom message box """

    def __init__(self, parent=None):
        self.fp_fds = None
        self.current_state_is_moving_average_applied: bool = False
        super().__init__(parent)
        self._chart = ChartWidget(self)
        self._setting = SettingWidget(self)
        self._setting.widget_layout.addStretch(1)
        self._setting.widget_layout.setContentsMargins(0, 0, 12, 0)
        scroll_area = ScrollArea(self)
        scroll_area.setWidget(self._setting)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            'ScrollArea{border:1px solid transparent;border-radius:5px;}QWidget{background-color:transparent;}'
        )

        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.setSpacing(0)
        self.widget_layout.addWidget(self._chart, stretch=1)
        self.widget_layout.addWidget(VerticalSeparator(self))
        self.widget_layout.addSpacing(12)
        self.widget_layout.addWidget(scroll_area)

        self.connect_signals()

    @property
    def chart(self) -> ChartWidget:
        return self._chart

    @property
    def setting(self) -> SettingWidget:
        return self._setting
