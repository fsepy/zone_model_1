# coding:utf-8

from PySide6 import QtWidgets, QtCore

from ...common.chart.chart import ChartWithSettingWidget
from ...common.interface_gallery import SimpleCard, GalleryInterface


class SettingWidget(QtWidgets.QWidget):
    value_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)


class HeatTransferInterface(GalleryInterface):
    """ Basic input interface """

    def __init__(self, parent=None):
        super().__init__(
            title='Heat Transfer',
            subtitle='Heat transfer in walls, soffits and floors',
            parent=parent
        )
        self.setObjectName('HeatTransferInterface')

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

        self.handle_parameters_changed()

    @QtCore.Slot()
    def handle_parameters_changed(self):
        pass
