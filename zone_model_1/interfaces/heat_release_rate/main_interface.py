# coding:utf-8

from PySide6 import QtWidgets, QtCore
from qfluentwidgets import (
    SingleDirectionScrollArea, BodyLabel, VBoxLayout, HorizontalSeparator
)

from zone_model_1.funcs.pd_7974_1_2019 import *
from ...common.chart.chart import ChartWithSettingWidget
from ...common.interface_gallery import SimpleCard, GalleryInterface
from ...common.spinbox import CompactDoubleSpinBox


class SettingWidget(QtWidgets.QWidget):
    value_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.in_fire_fuel_load_density = CompactDoubleSpinBox()
        self.in_fire_hrr_density = CompactDoubleSpinBox()
        self.in_fire_total_fuel_load_override = CompactDoubleSpinBox()
        self.in_fire_growth_factor = CompactDoubleSpinBox()
        self.in_fire_growth_power = CompactDoubleSpinBox()
        self.in_fire_decay_fuel_percentage = CompactDoubleSpinBox()
        self.in_room_width = CompactDoubleSpinBox()
        self.in_room_depth = CompactDoubleSpinBox()
        self.in_room_height = CompactDoubleSpinBox()
        self.in_vent_width = CompactDoubleSpinBox()
        self.in_vent_height = CompactDoubleSpinBox()

        geo_layout = QtWidgets.QGridLayout()
        geo_layout.setColumnStretch(0, 0)
        geo_layout.setColumnStretch(1, 1)
        geo_layout.setColumnStretch(2, 0)
        geo_layout.addWidget(BodyLabel('Room Width', self), 0, 0)
        geo_layout.addWidget(BodyLabel('Room Depth', self), 1, 0)
        geo_layout.addWidget(BodyLabel('Room Height', self), 2, 0)
        geo_layout.addWidget(BodyLabel('Vent Width', self), 3, 0)
        geo_layout.addWidget(BodyLabel('Vent Height', self), 4, 0)
        geo_layout.addWidget(BodyLabel('[m]', self), 0, 1)
        geo_layout.addWidget(BodyLabel('[m]', self), 1, 1)
        geo_layout.addWidget(BodyLabel('[m]', self), 2, 1)
        geo_layout.addWidget(BodyLabel('[m]', self), 3, 1)
        geo_layout.addWidget(BodyLabel('[m]', self), 4, 1)
        geo_layout.addWidget(self.in_room_width, 0, 2)
        geo_layout.addWidget(self.in_room_depth, 1, 2)
        geo_layout.addWidget(self.in_room_height, 2, 2)
        geo_layout.addWidget(self.in_vent_width, 3, 2)
        geo_layout.addWidget(self.in_vent_height, 4, 2)

        fire_layout = QtWidgets.QGridLayout()
        fire_layout.setColumnStretch(0, 0)
        fire_layout.setColumnStretch(1, 1)
        fire_layout.setColumnStretch(2, 0)
        fire_layout.addWidget(BodyLabel('Fuel Load Density', self), 0, 0)
        fire_layout.addWidget(BodyLabel('HRR Density', self), 1, 0)
        fire_layout.addWidget(BodyLabel('Fuel Load (Override)', self), 2, 0)
        fire_layout.addWidget(BodyLabel('Fire Growth Factor', self), 3, 0)
        fire_layout.addWidget(BodyLabel('Fire Growth Power', self), 4, 0)
        fire_layout.addWidget(BodyLabel('Decay Fuel Perc.', self), 5, 0)
        fire_layout.addWidget(BodyLabel('[MJ/m<sup>2</sup>]', self), 0, 1)
        fire_layout.addWidget(BodyLabel('[kW/m<sup>2</sup>]', self), 1, 1)
        fire_layout.addWidget(BodyLabel('[MJ]', self), 2, 1)
        fire_layout.addWidget(BodyLabel('[kW/m<sup>2</sup>]', self), 3, 1)
        fire_layout.addWidget(BodyLabel('[1]', self), 4, 1)
        fire_layout.addWidget(BodyLabel('[1]', self), 5, 1)
        fire_layout.addWidget(self.in_fire_fuel_load_density, 0, 2)
        fire_layout.addWidget(self.in_fire_hrr_density, 1, 2)
        fire_layout.addWidget(self.in_fire_total_fuel_load_override, 2, 2)
        fire_layout.addWidget(self.in_fire_growth_factor, 3, 2)
        fire_layout.addWidget(self.in_fire_growth_power, 4, 2)
        fire_layout.addWidget(self.in_fire_decay_fuel_percentage, 5, 2)

        # Content widget that will be placed inside the scroll area
        content_widget = QtWidgets.QWidget()
        content_layout = VBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)
        content_layout.addLayout(fire_layout)
        content_layout.addWidget(HorizontalSeparator())
        content_layout.addLayout(geo_layout)
        content_layout.addStretch()

        # Scroll area to make content scrollable
        scroll_area = SingleDirectionScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setStyleSheet('background-color: transparent;')

        # Main layout of the SettingPanelWidget
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)
        main_layout.addWidget(scroll_area)

        self.in_fire_growth_power.setDisabled(True)
        self.in_room_height.setDisabled(True)

        self.in_fire_fuel_load_density.setMaximum(999999999)
        self.in_fire_hrr_density.setMaximum(999999999)
        self.in_fire_total_fuel_load_override.setMaximum(999999999)
        self.in_fire_growth_factor.setMaximum(999999999)
        self.in_fire_growth_power.setMaximum(999999999)
        self.in_fire_decay_fuel_percentage.setMaximum(999999999)
        self.in_room_width.setMaximum(999999999)
        self.in_room_depth.setMaximum(999999999)
        self.in_room_height.setMaximum(999999999)
        self.in_vent_width.setMaximum(999999999)
        self.in_vent_height.setMaximum(999999999)
        self.in_fire_growth_factor.setDecimals(5)
        self.in_fire_growth_factor.setSingleStep(0.0001)
        self.in_fire_growth_power.setDecimals(0)
        self.in_fire_decay_fuel_percentage.setDecimals(3)
        self.in_fire_decay_fuel_percentage.setSingleStep(0.001)
        self.in_room_width.setSingleStep(0.1)
        self.in_room_depth.setSingleStep(0.1)
        self.in_room_height.setSingleStep(0.1)
        self.in_vent_width.setSingleStep(0.1)
        self.in_vent_height.setSingleStep(0.1)

        self.in_fire_fuel_load_density.valueChanged.connect(self.value_changed)
        self.in_fire_hrr_density.valueChanged.connect(self.value_changed)
        self.in_fire_total_fuel_load_override.valueChanged.connect(self.value_changed)
        self.in_fire_growth_factor.valueChanged.connect(self.value_changed)
        self.in_fire_growth_power.valueChanged.connect(self.value_changed)
        self.in_fire_decay_fuel_percentage.valueChanged.connect(self.value_changed)
        self.in_room_width.valueChanged.connect(self.value_changed)
        self.in_room_depth.valueChanged.connect(self.value_changed)
        self.in_room_height.valueChanged.connect(self.value_changed)
        self.in_vent_width.valueChanged.connect(self.value_changed)
        self.in_vent_height.valueChanged.connect(self.value_changed)
        self.in_fire_total_fuel_load_override.valueChanged.connect(self.handle_fuel_load_override_changed)

        self.in_fire_fuel_load_density.setFixedWidth(120)
        self.in_fire_hrr_density.setFixedWidth(120)
        self.in_fire_total_fuel_load_override.setFixedWidth(120)
        self.in_fire_growth_factor.setFixedWidth(120)
        self.in_fire_growth_power.setFixedWidth(120)
        self.in_fire_decay_fuel_percentage.setFixedWidth(120)
        self.in_room_width.setFixedWidth(120)
        self.in_room_depth.setFixedWidth(120)
        self.in_room_height.setFixedWidth(120)
        self.in_vent_width.setFixedWidth(120)
        self.in_vent_height.setFixedWidth(120)

    @QtCore.Slot(float)
    def handle_fuel_load_override_changed(self, value: float):
        if value:
            self.in_fire_fuel_load_density.setDisabled(True)
        else:
            self.in_fire_fuel_load_density.setEnabled(True)


class FuelHRRInterface(GalleryInterface):
    """ Basic input interface """

    def __init__(self, parent=None):
        super().__init__(
            title='Heat Release Rate PD 7974-1:2019',
            subtitle='Heat release rate from fuel (excluding timber)',
            parent=parent
        )
        self.setObjectName('FuelHRRInterface')

        self.widget_parameters = SettingWidget()
        self.widget_parameters.value_changed.connect(self.handle_parameters_changed)
        self.widget_chart = ChartWithSettingWidget()

        self.card_inputs = SimpleCard('Parameters', self.widget_parameters, self)
        self.card_plot = SimpleCard('Graph', self.widget_chart, self)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self.card_inputs, stretch=0)
        layout.addWidget(self.card_plot, stretch=1)

        self.v_layout.addLayout(layout)

        self.card_inputs.title_label.setMinimumWidth(360)
        self.card_plot.title_label.setMinimumWidth(390)

        self.widget_chart.setting.axis_x.label.setText('Time [min]')
        self.widget_chart.setting.axis_y.label.setText('Heat Release Rate [kW]')
        self.widget_chart.setting.legend.in_visible.setChecked(True)

        self.widget_parameters.blockSignals(True)
        self.widget_parameters.in_fire_fuel_load_density.setValue(200)
        self.widget_parameters.in_fire_hrr_density.setValue(250)
        self.widget_parameters.in_fire_total_fuel_load_override.setValue(2500)
        self.widget_parameters.in_fire_growth_factor.setValue(0.01172)
        self.widget_parameters.in_fire_growth_power.setValue(2)
        self.widget_parameters.in_fire_decay_fuel_percentage.setValue(0.8)
        self.widget_parameters.in_room_width.setValue(5)
        self.widget_parameters.in_room_depth.setValue(5)
        self.widget_parameters.in_room_height.setValue(2.1)
        self.widget_parameters.in_vent_width.setValue(1)
        self.widget_parameters.in_vent_height.setValue(1)
        self.widget_parameters.blockSignals(False)
        self.handle_parameters_changed()

    @QtCore.Slot()
    def handle_parameters_changed(self):
        self.widget_chart.chart.clear()

        q_fd = self.widget_parameters.in_fire_fuel_load_density.value() * 1000.
        q_dot = self.widget_parameters.in_fire_hrr_density.value()
        Q_fd = self.widget_parameters.in_fire_total_fuel_load_override.value() * 1000.
        alpha = self.widget_parameters.in_fire_growth_factor.value()
        n = self.widget_parameters.in_fire_growth_power.value()
        Q_fd_decay = self.widget_parameters.in_fire_decay_fuel_percentage.value()
        W = self.widget_parameters.in_room_width.value()
        D = self.widget_parameters.in_room_depth.value()
        H = self.widget_parameters.in_room_height.value()
        W_v = self.widget_parameters.in_vent_width.value()
        H_v = self.widget_parameters.in_vent_height.value()

        if not Q_fd:
            Q_fd = q_fd * W * D

        A_v = W_v * H_v
        A_t = W * D

        t1, hrr = calc_hrr(Q_fd=Q_fd, q_dot=q_dot, A_t=A_t, A_v=A_v, H_v=H_v, alpha=alpha)
        t2, hrr_capped = calc_hrr_fo_capped(Q_fd=Q_fd, q_dot=q_dot, A_t=A_t, A_v=A_v, H_v=H_v, alpha=alpha)

        t1 = t1 / 60.
        t2 = t2 / 60.

        self.widget_chart.chart.add_series(t1, hrr, 'HRR')
        self.widget_chart.chart.add_series(t2, hrr_capped, 'HRR (FO)')

        if not self.widget_chart.setting.axis_x.upper_lim.value():
            self.widget_chart.setting.axis_x.upper_lim.set_value(max(t1[-1], t2[-1]))
        if not self.widget_chart.setting.axis_x.lower_lim.value():
            self.widget_chart.setting.axis_x.lower_lim.set_value(min(t1[0], t2[0]))
        if not self.widget_chart.setting.axis_y.upper_lim.value():
            self.widget_chart.setting.axis_y.upper_lim.set_value(max(np.max(hrr), np.max(hrr_capped)))
        if not self.widget_chart.setting.axis_y.lower_lim.value():
            self.widget_chart.setting.axis_y.lower_lim.set_value(min(np.min(hrr), np.min(hrr_capped)))
