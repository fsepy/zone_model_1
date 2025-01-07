import sys
from io import StringIO

import numpy as np
from PySide6 import QtCore, QtWidgets


def test_chart_setting_widget():
    from test_devc_csv import data

    data = StringIO(data)
    units = data.readline().strip().split(',')
    names = data.readline().strip().split(',')
    content = np.loadtxt(data, delimiter=',', dtype=float)

    app = QtWidgets.QApplication()

    from fdstoolsgui.i_output_proc.interface_fds_output_analysis import ChartSettingWidget
    graph_dialog = ChartSettingWidget()
    graph_dialog.chart.chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
    for i in range(1, content.shape[1]):
        graph_dialog.chart.add_series(content[:, 0], content[:, i], names[i].strip('"'))
    graph_dialog.chart.x_axis.setRange(np.amin(content[:, 0]), np.amax(content[:, 0]))
    graph_dialog.chart.y_axis.setRange(np.amin(content[:, 1:]), np.amax(content[:, 1:]))
    graph_dialog.sync_setting_from_chart()
    graph_dialog.show()

    sys.exit(app.exec())


def test_chart_dialog():
    from test_devc_csv import data
    from fdstoolsgui.common.chart.chart import ChartDialog

    data = StringIO(data)
    units = data.readline().strip().split(',')
    names = data.readline().strip().split(',')
    content = np.loadtxt(data, delimiter=',', dtype=float)

    app = QtWidgets.QApplication()

    graph_dialog = ChartDialog()
    graph_dialog.chart.chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
    for i in range(1, content.shape[1]):
        graph_dialog.chart.add_series(content[:, 0], content[:, i], names[i].strip('"'))
    graph_dialog.chart.x_axis.setRange(np.amin(content[:, 0]), np.amax(content[:, 0]))
    graph_dialog.chart.y_axis.setRange(np.amin(content[:, 1:]), np.amax(content[:, 1:]))
    graph_dialog.sync_setting_from_chart()
    graph_dialog.show()

    sys.exit(app.exec())


def test_compact_chart_dialog():
    from test_devc_csv import data
    from fdstoolsgui.common.chart.chart import CompactChartDialog

    data = StringIO(data)
    units = data.readline().strip().split(',')
    names = data.readline().strip().split(',')
    content = np.loadtxt(data, delimiter=',', dtype=float)

    app = QtWidgets.QApplication()

    graph_dialog = CompactChartDialog()
    graph_dialog.chart.chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
    for i in range(1, content.shape[1]):
        graph_dialog.chart.add_series(content[:, 0], content[:, i], names[i].strip('"'))
    graph_dialog.chart.x_axis.setRange(np.amin(content[:, 0]), np.amax(content[:, 0]))
    graph_dialog.chart.y_axis.setRange(np.amin(content[:, 1:]), np.amax(content[:, 1:]))
    graph_dialog.sync_setting_from_chart()
    graph_dialog.show()

    sys.exit(app.exec())


def test_mask_chart_dialog():
    from test_devc_csv import data
    from fdstoolsgui.common.chart.chart import MaskChartDialog

    data = StringIO(data)
    units = data.readline().strip().split(',')
    names = data.readline().strip().split(',')
    content = np.loadtxt(data, delimiter=',', dtype=float)

    app = QtWidgets.QApplication()

    w = QtWidgets.QWidget()
    w.setMinimumSize(1000, 600)

    graph_dialog = MaskChartDialog(w)
    graph_dialog.chart.chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
    for i in range(1, content.shape[1]):
        graph_dialog.chart.add_series(content[:, 0], content[:, i], names[i].strip('"'))
    graph_dialog.chart.x_axis.setRange(np.amin(content[:, 0]), np.amax(content[:, 0]))
    graph_dialog.chart.y_axis.setRange(np.amin(content[:, 1:]), np.amax(content[:, 1:]))
    graph_dialog.sync_setting_from_chart()
    graph_dialog.show()

    w.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    test_chart_dialog()
