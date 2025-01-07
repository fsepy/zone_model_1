from abc import abstractmethod
from enum import Enum
from typing import Union

from PySide6 import QtCore, QtWidgets
from qfluentwidgets import (
    LineEdit, BodyLabel, ScrollArea, StrongBodyLabel, SwitchButton, RadioButton, CheckBox, TransparentToolButton,
    FluentIcon, ToolTipFilter
)

from ..spinbox import CompactDoubleSpinBox, CompactSpinBox


class MetaQWidget(type(QtWidgets.QWidget), type):
    pass


class CompactCustomSpinBoxBase(metaclass=MetaQWidget):
    default_value_changed = QtCore.Signal(float)

    def init_signals(self):
        self.value = self.edit.value
        self.setSingleStep = self.edit.setSingleStep
        self.singleStep = self.edit.singleStep
        self.setRange = self.edit.setRange
        self.valueChanged = self.edit.valueChanged

        self.reset_button.setIcon(FluentIcon.SYNC)
        self.reset_button.setToolTip('Reset')

        self.edit.valueChanged.connect(self.__handle_value_changed_by_edit)
        self.reset_button.clicked.connect(self.__handle_reset_button_clicked)
        self.reset_button.hide()

        self.default_value = self.edit.value()

    @property
    @abstractmethod
    def edit(self) -> Union[CompactDoubleSpinBox, CompactSpinBox]:
        pass

    @property
    @abstractmethod
    def reset_button(self) -> TransparentToolButton:
        pass

    @QtCore.Slot()
    def __handle_reset_button_clicked(self):
        self.reset_to_default_value()

    @QtCore.Slot()
    def __handle_value_changed_by_edit(self):
        if self.reset_button.isHidden():
            self.reset_button.show()

    def set_value(self, value: float):
        self.edit.setValue(value)

    def set_default_value(self, value: float):
        if self.reset_button.isVisible() is False:
            self.edit.setValue(value)
            self.reset_button.hide()
        self.default_value = value
        self.default_value_changed.emit(value)

    def reset_to_default_value(self):
        if self.default_value is None:
            self.default_value = self.edit.value()
            return
        else:
            self.edit.setValue(self.default_value)
            self.reset_button.hide()


class CompactCustomSpinBox(QtWidgets.QWidget, CompactCustomSpinBoxBase):
    """A widget contains a spin box and a reset button. The spin box is a normal spin box. The reset button, upon
    click reset the spin box value to a cached value."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.default_value: float = 0.
        self._edit = CompactSpinBox()
        # self._edit = QtWidgets.QSpinBox()
        self._reset_button = TransparentToolButton()
        # self._edit.setFocusPolicy(QtCore.Qt.FocusPolicy.WheelFocus)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self.edit)
        layout.addWidget(self.reset_button)

        self.init_signals()

    @property
    def edit(self) -> Union[CompactDoubleSpinBox, CompactSpinBox]:
        return self._edit

    @property
    def reset_button(self) -> TransparentToolButton:
        return self._reset_button


class CompactCustomDoubleSpinBox(QtWidgets.QWidget, CompactCustomSpinBoxBase):
    """A widget contains a spin box and a reset button. The spin box is a normal spin box. The reset button, upon
    click reset the spin box value to a cached value."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.default_value: float = 0.
        self._edit = CompactDoubleSpinBox()
        self._reset_button = TransparentToolButton()

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self.edit)
        layout.addWidget(self.reset_button)

        self.init_signals()

    @property
    def edit(self) -> Union[CompactDoubleSpinBox, CompactSpinBox]:
        return self._edit

    @property
    def reset_button(self) -> TransparentToolButton:
        return self._reset_button


class AxisSettingWidget(QtWidgets.QWidget):
    upper_limit_changed = QtCore.Signal(float)
    lower_limit_changed = QtCore.Signal(float)
    label_changed = QtCore.Signal(str)
    tick_count_changed = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title_label = StrongBodyLabel('Title', self)
        self.upper_lim = CompactCustomDoubleSpinBox()
        self.upper_lim.setRange(-100000, 100000)
        self.upper_lim.setSingleStep(1)
        self.upper_lim.valueChanged.connect(self.upper_limit_changed.emit)
        self.lower_lim = CompactCustomDoubleSpinBox()
        self.lower_lim.setRange(-100000, 100000)
        self.lower_lim.setSingleStep(1)
        self.lower_lim.valueChanged.connect(self.lower_limit_changed.emit)
        self.tick_count = CompactCustomSpinBox()
        self.tick_count.setRange(3, 21)
        self.tick_count.valueChanged.connect(self.tick_count_changed.emit)
        self.label = LineEdit(self)
        self.label.textChanged.connect(self.label_changed.emit)

        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(12)
        layout.addWidget(self.title_label, 0, 0, 1, 2)
        layout.addWidget(BodyLabel('Title', self), 1, 0)
        layout.addWidget(self.label, 1, 1)
        layout.addWidget(BodyLabel('Upper Limit', self), 2, 0)
        layout.addWidget(self.upper_lim, 2, 1)
        layout.addWidget(BodyLabel('Lower Limit', self), 3, 0)
        layout.addWidget(self.lower_lim, 3, 1)
        layout.addWidget(BodyLabel('Tick Count', self), 4, 0)
        layout.addWidget(self.tick_count, 4, 1)

        self.upper_lim.default_value_changed.connect(self.__handle_upper_lim_default_changed)
        self.lower_lim.default_value_changed.connect(self.__handle_lower_lim_default_changed)

    @QtCore.Slot(float)
    def __handle_upper_lim_default_changed(self, value: float):
        step = (self.upper_lim.default_value - self.lower_lim.default_value) / 100
        self.lower_lim.setSingleStep(step)
        self.upper_lim.setSingleStep(step)

    @QtCore.Slot(float)
    def __handle_lower_lim_default_changed(self, value: float):
        step = (self.upper_lim.default_value - self.lower_lim.default_value) / 100
        self.lower_lim.setSingleStep(step)
        self.upper_lim.setSingleStep(step)

    @QtCore.Slot(str)
    def handle_label_changed(self, value: str):
        self.label_changed.emit(value)


class LegendLocation(Enum):
    TOP = QtCore.Qt.AlignmentFlag.AlignTop
    RIGHT = QtCore.Qt.AlignmentFlag.AlignRight
    BOTTOM = QtCore.Qt.AlignmentFlag.AlignBottom
    LEFT = QtCore.Qt.AlignmentFlag.AlignLeft
    CUSTOM = QtCore.Qt.AlignmentFlag.AlignAbsolute


class LegendSettingWidget(QtWidgets.QWidget):
    widget_size_changed = QtCore.Signal()
    visible_changed = QtCore.Signal(bool)
    marker_visible_changed = QtCore.Signal(bool)
    location_changed = QtCore.Signal(LegendLocation)
    custom_location_changed = QtCore.Signal(int, int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.in_visible_label = BodyLabel('Visible', self)
        self.in_marker_visible_label = BodyLabel('Marker Visible', self)

        self.in_visible = SwitchButton()
        self.in_visible.setToolTip('Show/hide legend')
        self.in_visible.installEventFilter(ToolTipFilter(self.in_visible))
        self.in_marker_visible = SwitchButton()
        self.in_marker_visible.setToolTip('Show/hide legend marker when the corresponding line plot is visible/hidden')
        self.in_marker_visible.installEventFilter(ToolTipFilter(self.in_marker_visible))
        self.in_loc_right = RadioButton(self)
        self.in_loc_right.setText('Right')
        self.in_loc_right.setToolTip('Legend position at the right')
        self.in_loc_right.installEventFilter(ToolTipFilter(self.in_loc_right))
        self.in_loc_left = RadioButton(self)
        self.in_loc_left.setText('Left')
        self.in_loc_left.setToolTip('Legend position at the left')
        self.in_loc_left.installEventFilter(ToolTipFilter(self.in_loc_left))
        self.in_loc_top = RadioButton(self)
        self.in_loc_top.setText('Top')
        self.in_loc_top.setToolTip('Legend position at the top')
        self.in_loc_top.installEventFilter(ToolTipFilter(self.in_loc_top))
        self.in_loc_bottom = RadioButton(self)
        self.in_loc_bottom.setText('Bottom')
        self.in_loc_bottom.setToolTip('Legend position at the bottom')
        self.in_loc_bottom.installEventFilter(ToolTipFilter(self.in_loc_bottom))
        self.in_loc_custom = RadioButton(self)
        self.in_loc_custom.setText('Custom')
        self.in_loc_custom.setToolTip('Legend overlap the chart')
        self.in_loc_custom.installEventFilter(ToolTipFilter(self.in_loc_custom))
        self.in_height = CompactSpinBox()
        self.in_height.setRange(1, 100)
        self.in_height.setToolTip('Height of the legend as a percentage to the chart height')
        self.in_height.installEventFilter(ToolTipFilter(self.in_height))
        self.in_height_label = BodyLabel('H', self)
        self.in_width = CompactSpinBox()
        self.in_width.setRange(1, 100)
        self.in_width.setToolTip('Width of the legend as a percentage to the chart width')
        self.in_width.installEventFilter(ToolTipFilter(self.in_width))
        self.in_width_label = BodyLabel('W', self)
        self.in_location_x = CompactSpinBox()
        self.in_location_x.setRange(0, 100)
        self.in_location_x.setToolTip('Legend horizontal location as a percentage to the chart width')
        self.in_location_x.installEventFilter(ToolTipFilter(self.in_location_x))
        self.in_location_y = CompactSpinBox()
        self.in_location_y.setRange(0, 100)
        self.in_location_y.setToolTip('Legend vertical location as a percentage to the chart height')
        self.in_location_y.installEventFilter(ToolTipFilter(self.in_location_y))
        self.in_location_x_label = BodyLabel('X', self)
        self.in_location_y_label = BodyLabel('Y', self)

        visible_layout = QtWidgets.QGridLayout()
        visible_layout.setSpacing(12)
        visible_layout.setContentsMargins(0, 0, 0, 0)
        visible_layout.setColumnStretch(0, 1)
        visible_layout.setColumnStretch(1, 0)
        visible_layout.addWidget(self.in_visible_label, 0, 0)
        visible_layout.addWidget(self.in_marker_visible_label, 1, 0)
        visible_layout.addWidget(self.in_visible, 0, 1)
        visible_layout.addWidget(self.in_marker_visible, 1, 1)

        location_layout_custom = QtWidgets.QGridLayout()
        location_layout_custom.setSpacing(12)
        location_layout_custom.setContentsMargins(0, 0, 0, 0)
        location_layout_custom.setColumnStretch(1, 1)
        location_layout_custom.addWidget(self.in_width_label, 0, 0)
        location_layout_custom.addWidget(self.in_height_label, 1, 0)
        location_layout_custom.addWidget(self.in_location_x_label, 2, 0)
        location_layout_custom.addWidget(self.in_location_y_label, 3, 0)
        location_layout_custom.addWidget(self.in_width, 0, 1)
        location_layout_custom.addWidget(self.in_height, 1, 1)
        location_layout_custom.addWidget(self.in_location_x, 2, 1)
        location_layout_custom.addWidget(self.in_location_y, 3, 1)

        location_layout = QtWidgets.QGridLayout()
        location_layout.setSpacing(12)
        location_layout.setContentsMargins(0, 0, 0, 0)
        location_layout.addWidget(self.in_loc_top, 0, 0)
        location_layout.addWidget(self.in_loc_bottom, 0, 1)
        location_layout.addWidget(self.in_loc_left, 1, 0)
        location_layout.addWidget(self.in_loc_right, 1, 1)
        location_layout.addWidget(self.in_loc_custom, 2, 0)
        location_layout.addLayout(location_layout_custom, 3, 0, 1, 2)

        layout = QtWidgets.QGridLayout(self)
        layout.setVerticalSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setColumnStretch(1, 1)
        layout.addWidget(StrongBodyLabel('Legend Settings', self), 0, 0, 1, 2)
        layout.addLayout(visible_layout, 1, 0, 1, 2)
        layout.addWidget(BodyLabel('Location', self), 2, 0, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        layout.addLayout(location_layout, 2, 1)

        self.in_location_x.setValue(75)
        self.in_location_y.setValue(10)
        self.in_width.setValue(25)
        self.in_height.setValue(80)

        self.in_loc_right.setChecked(True)
        self.in_location_x.hide()
        self.in_location_y.hide()
        self.in_location_x_label.hide()
        self.in_location_y_label.hide()
        self.in_width_label.hide()
        self.in_width.hide()
        self.in_height_label.hide()
        self.in_height.hide()

        self.in_loc_right.toggled.connect(
            lambda state: self.location_changed.emit(LegendLocation.RIGHT) if state else None
        )
        self.in_loc_left.toggled.connect(
            lambda state: self.location_changed.emit(LegendLocation.LEFT) if state else None
        )
        self.in_loc_top.toggled.connect(
            lambda state: self.location_changed.emit(LegendLocation.TOP) if state else None
        )
        self.in_loc_bottom.toggled.connect(
            lambda state: self.location_changed.emit(LegendLocation.BOTTOM) if state else None
        )
        self.in_loc_custom.toggled.connect(
            lambda state: self.location_changed.emit(LegendLocation.CUSTOM) if state else None
        )
        self.in_visible.checkedChanged.connect(self.visible_changed.emit)
        self.in_visible.checkedChanged.connect(self.in_loc_right.setEnabled)
        self.in_visible.checkedChanged.connect(self.in_loc_left.setEnabled)
        self.in_visible.checkedChanged.connect(self.in_loc_top.setEnabled)
        self.in_visible.checkedChanged.connect(self.in_loc_bottom.setEnabled)
        self.in_visible.checkedChanged.connect(self.in_loc_custom.setEnabled)
        self.in_visible.checkedChanged.connect(self.in_width.setEnabled)
        self.in_visible.checkedChanged.connect(self.in_height.setEnabled)
        self.in_visible.checkedChanged.connect(self.in_location_x.setEnabled)
        self.in_visible.checkedChanged.connect(self.in_location_y.setEnabled)
        self.in_marker_visible.checkedChanged.connect(self.marker_visible_changed.emit)
        self.in_loc_custom.toggled.connect(self.handle_custom_location_toggled)
        self.in_location_x.valueChanged.connect(self.handle_custom_location_changed)
        self.in_location_y.valueChanged.connect(self.handle_custom_location_changed)
        self.in_width.valueChanged.connect(self.handle_custom_location_changed)
        self.in_height.valueChanged.connect(self.handle_custom_location_changed)

    @QtCore.Slot(bool)
    def handle_custom_location_toggled(self, state: bool):
        self.in_location_x.setVisible(state)
        self.in_location_y.setVisible(state)
        self.in_location_x_label.setVisible(state)
        self.in_location_y_label.setVisible(state)
        self.in_width_label.setVisible(state)
        self.in_width.setVisible(state)
        self.in_height_label.setVisible(state)
        self.in_height.setVisible(state)
        self.widget_size_changed.emit()
        if state is True:
            QtCore.QTimer.singleShot(0, self.update)
            self.custom_location_changed.emit(
                self.in_location_x.value(),
                self.in_location_y.value(),
                self.in_width.value(),
                self.in_height.value(),
            )

    @QtCore.Slot()
    def handle_custom_location_changed(self):
        self.custom_location_changed.emit(
            self.in_location_x.value(),
            self.in_location_y.value(),
            self.in_width.value(),
            self.in_height.value(),
        )


class DataSettingWidget(QtWidgets.QWidget):
    setting_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.in_ma_check = CheckBox('Moving Average', self)
        self.in_ma_check.setToolTip('Apply moving average for all series')
        self.in_ma_check.installEventFilter(ToolTipFilter(self.in_ma_check))
        self.in_ma_window = CompactSpinBox()
        self.in_ma_window.setRange(0, 100)
        self.in_ma_window.setSingleStep(1)
        self.in_ma_window.setValue(1)
        self.in_ma_window.setToolTip('The time window used for the moving average')
        self.in_ma_window.installEventFilter(ToolTipFilter(self.in_ma_window))
        self.in_absolute_values = CheckBox('Transform to Absolute', self)
        self.in_absolute_values.setToolTip('Convert all negative values to positive values')
        self.in_absolute_values.installEventFilter(ToolTipFilter(self.in_absolute_values))
        self.ctrl_apply = TransparentToolButton()
        self.ctrl_apply.setText('Apply')
        self.ctrl_apply.setToolTip('Apply data settings')
        self.ctrl_apply.installEventFilter(ToolTipFilter(self.ctrl_apply))

        layout_header = QtWidgets.QHBoxLayout()
        layout_header.setContentsMargins(0, 0, 0, 0)
        layout_header.addWidget(StrongBodyLabel('Data Processing', self))
        layout_header.addStretch(1)
        layout_header.addWidget(self.ctrl_apply)

        layout_content = QtWidgets.QGridLayout()
        layout_content.setContentsMargins(0, 0, 0, 0)
        layout_content.addWidget(self.in_ma_check, 0, 0)
        layout_content.addWidget(self.in_ma_window, 0, 1)
        layout_content.addWidget(self.in_absolute_values, 1, 0, 1, 2)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(layout_header)
        layout.addLayout(layout_content)

        self.in_ma_check.toggled.connect(self.in_ma_window.setEnabled)
        self.ctrl_apply.clicked.connect(self.setting_changed.emit)

        self.in_ma_check.setChecked(False)
        self.in_ma_window.setEnabled(False)
        self.in_absolute_values.setChecked(False)


class SettingWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.axis_x = AxisSettingWidget()
        self.axis_x.title_label.setText('X-Axis Settings')
        self.axis_y = AxisSettingWidget()
        self.axis_y.title_label.setText('Y-Axis Settings')
        self.legend = LegendSettingWidget()
        self.data = DataSettingWidget()

        self.widget_layout = QtWidgets.QVBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.addWidget(self.data)
        self.widget_layout.addSpacing(25)
        self.widget_layout.addWidget(self.axis_x)
        self.widget_layout.addSpacing(25)
        self.widget_layout.addWidget(self.axis_y)
        self.widget_layout.addSpacing(25)
        self.widget_layout.addWidget(self.legend)


class SettingScrollWidget(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.axis_x = AxisSettingWidget()
        self.axis_x.title_label.setText('X-Axis Settings')
        self.axis_y = AxisSettingWidget()
        self.axis_y.title_label.setText('Y-Axis Settings')
        self.legend = LegendSettingWidget()
        self.data = DataSettingWidget()

        widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(widget)
        # layout.setContentsMargins(0, 10, 20, 0)  # keep 10 right margin for the scroll bar
        layout.setContentsMargins(0, 0, 12, 0)  # keep 10 right margin for the scroll bar
        layout.addWidget(self.data)
        layout.addSpacing(25)
        layout.addWidget(self.axis_x)
        layout.addSpacing(25)
        layout.addWidget(self.axis_y)
        layout.addSpacing(25)
        layout.addWidget(self.legend)
        layout.addStretch()

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.setWidgetResizable(True)
        self.setWidget(widget)
        # StyleSheet.SAMPLE_CARD.apply(self)
        self.setStyleSheet(
            'QWidget{'
            '   background-color:transparent;'
            '   border-bottom-left-radius: 12px;'
            '   border-top-right-radius: 12px;'
            '}'
        )

        self.legend.widget_size_changed.connect(self.handle_widget_size_changed)

    @QtCore.Slot()
    def handle_widget_size_changed(self):
        QtCore.QTimer.singleShot(0, lambda: self.ensureWidgetVisible(self.legend.in_location_y, ymargin=50))
