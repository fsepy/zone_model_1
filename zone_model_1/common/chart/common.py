from abc import abstractmethod
from typing import Dict, Tuple

import numpy as np
from PySide6 import QtCore, QtWidgets, QtGui, QtCharts
from qfluentwidgets import RoundMenu, qconfig, Theme

from .setting import LegendLocation, SettingWidget


def apply_moving_average(x: np.ndarray, y: np.ndarray, window: float = 5) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply a moving average filter to the y-values based on the x-values.

    Parameters:
        x (np.array): Array of x-values, assumed to be sorted.
        y (np.array): Array of y-values corresponding to x-values.
        window (int): Number of points to consider for the moving average.

    Returns:
        np.array: x-values for the moving average.
        np.array: y-values after applying the moving average.
    """
    if window <= 0:
        return x, y

    x_ma = np.copy(x)
    y_ma = np.zeros_like(y)

    for i in range(len(x)):
        start_index = np.searchsorted(x, x[i] - window, side='left')
        end_index = np.searchsorted(x, x[i] + window, side='right')

        # Calculate the average y-value within the window
        y_ma[i] = np.mean(y[start_index:end_index])

    return x_ma, y_ma


class LineSeries(QtCharts.QLineSeries):
    def __init__(self, x_array: np.ndarray, y_array: np.ndarray, parent=None):
        self.flag_legend_marker_conditional_visible: bool = False
        assert x_array.shape == y_array.shape

        super().__init__(parent)
        self._name_raw = None
        self._x_raw: np.ndarray = x_array
        self._y_raw: np.ndarray = y_array
        self._current_ma_window: int = 0
        self._current_abs: bool = False

        self.cache_points: Dict[Tuple[int, bool], Tuple[QtCore.QPointF, ...]] = dict()  # (ma window, abs): data
        self.cache_x_y_range: Dict[Tuple[int, bool], Tuple[Tuple[float, float], Tuple[float, float]]] = dict()

        self.apply_setting(self._current_ma_window, self._current_abs)

    @property
    def x_max(self) -> float:
        return self._x_max

    @property
    def x_min(self) -> float:
        return self._x_min

    @property
    def y_max(self) -> float:
        return self._y_max

    @property
    def y_min(self) -> float:
        return self._y_min

    def setName(self, name):
        self._name_raw = name
        super().setName(name)

    def apply_setting(self, ma_window: int = 0, abs_val: bool = False):
        assert ma_window >= 0

        self._current_ma_window = ma_window

        if ma_window not in self.cache_points:
            x_array, y_array = apply_moving_average(
                self._x_raw if abs_val is False else np.abs(self._x_raw),
                self._y_raw if abs_val is False else np.abs(self._y_raw),
                ma_window
            )

            self.cache_points[(ma_window, abs_val)] = tuple(
                QtCore.QPointF(x, y) for x, y in zip(x_array, y_array)
            )

            self.cache_x_y_range[(ma_window, abs_val)] = (
                (np.nanmin(x_array), np.nanmax(x_array)),
                (np.nanmin(y_array), np.nanmax(y_array)),
            )

        self.clear()
        self.append(self.cache_points[(ma_window, abs_val)])
        (self._x_min, self._x_max), (self._y_min, self._y_max) = self.cache_x_y_range[(ma_window, abs_val)]


class ChartWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        self.dict_chart_series: Dict[str, LineSeries] = dict()
        self.dict_chart_raw_data: Dict[str, Tuple[np.ndarray, np.ndarray]] = dict()
        self.__legend_custom_location = (75, 10, 25, 80)
        self.flag_marker_visible: bool = True
        super().__init__(parent)
        self.chart = QtCharts.QChart()
        self.x_axis = QtCharts.QValueAxis()
        self.y_axis = QtCharts.QValueAxis()
        self.chart.addAxis(self.x_axis, QtCore.Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.y_axis, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.w_chart_view = QtCharts.QChartView(self.chart)

        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.addWidget(self.w_chart_view)

        # styles
        self.chart.setBackgroundRoundness(8)
        self.chart.setContentsMargins(-24, -24, -24, -24)
        self.chart.setAnimationOptions(QtCharts.QChart.AnimationOption.NoAnimation)
        self.chart.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(QtCore.Qt.GlobalColor.transparent)))
        self.setStyleSheet('QWidget{background-color: transparent;}')
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.w_chart_view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.w_chart_view.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing)

        # default states/values
        self.chart.legend().show()

        # signals
        self.customContextMenuRequested.connect(self.open_context_menu)

        qconfig.themeChangedFinished.connect(self.handle_theme_changed)  # ensure colour matches global colour scheme
        self.handle_theme_changed()

    def legend(self):
        return self.chart.legend()

    def clear(self):
        self.dict_chart_series.clear()
        self.dict_chart_raw_data.clear()
        self.chart.removeAllSeries()

    def add_series(self, x: np.ndarray, y: np.ndarray, name: str):
        if name in self.dict_chart_series:
            self.dict_chart_raw_data[name] = (x, y)
            series = self.dict_chart_series[name]
            series.clear()
            series.cache_points.clear()
            series.cache_x_y_range.clear()
            series.apply_setting()
            return

        series = LineSeries(x, y)
        series.setName(name)
        self.chart.addSeries(series)
        series.attachAxis(self.x_axis)
        series.attachAxis(self.y_axis)

        self.dict_chart_series[name] = series
        self.dict_chart_raw_data[name] = (x, y)

        # Connect the marker clicked signal for the new series
        for marker in self.chart.legend().markers(series):
            marker.clicked.connect(self.handle_marker_clicked)
            marker.setLabelBrush(
                QtCore.Qt.GlobalColor.black if qconfig.theme == Theme.LIGHT else QtCore.Qt.GlobalColor.white
            )

        # ensure the legend marker text is right colour to the theme
        if qconfig.theme == Theme.DARK:
            for marker in self.chart.legend().markers(series):
                marker.setLabelBrush(QtCore.Qt.GlobalColor.white)
        else:
            for marker in self.chart.legend().markers(series):
                marker.setLabelBrush(QtCore.Qt.GlobalColor.black)

    @QtCore.Slot(bool)
    def handle_marker_visible_changed(self, state: bool):
        self.flag_marker_visible = state
        legend = self.chart.legend()
        for series in self.dict_chart_series.values():
            if state is False and not series.isVisible():
                for marker in legend.markers(series):
                    marker.setVisible(False)
            else:
                for marker in legend.markers(series):
                    marker.setVisible(True)
        legend.update()
        legend.layout().invalidate()

    @QtCore.Slot()
    def handle_marker_clicked(self):
        marker: QtCharts.QLegendMarker = self.sender()
        series = marker.series()
        current_state = series.isVisible()
        series.setVisible(not current_state)
        if self.flag_marker_visible is False:
            marker.setVisible(not current_state)
        else:
            marker.setVisible(True)
        # Adjust the marker label to reflect the visibility state
        if qconfig.theme == Theme.LIGHT:
            if series.isVisible():
                marker.setLabelBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.black))
            else:
                marker.setLabelBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.lightGray))
        else:
            if series.isVisible():
                marker.setLabelBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.white))
            else:
                marker.setLabelBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.darkGray))

    def hide_all_curves(self):
        for name, series in self.dict_chart_series.items():
            series.hide()
            if self.flag_marker_visible is False:
                for marker in self.legend().markers(series):
                    marker.setVisible(False)
            else:
                for marker in self.legend().markers(series):
                    marker.setVisible(True)
            # Find the corresponding marker and update its label and color
            if qconfig.theme == Theme.LIGHT:
                for marker in self.chart.legend().markers(series):
                    marker.setLabelBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.lightGray))
            else:
                for marker in self.chart.legend().markers(series):
                    marker.setLabelBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.darkGray))

    def show_all_curves(self):
        for name, series in self.dict_chart_series.items():
            series.show()
            for marker in self.legend().markers(series):
                marker.setVisible(True)
            # Find the corresponding marker and update its label and color
            for marker in self.chart.legend().markers(series):
                marker.setLabelBrush(QtGui.QBrush(QtGui.QColor("black")))
                marker.setVisible(True)

    @QtCore.Slot(bool)
    def set_legend_visible(self, state: bool):
        self.chart.legend().setVisible(state)

    @QtCore.Slot(LegendLocation)
    def set_legend_location(self, loc: LegendLocation):
        legend = self.chart.legend()

        if loc == LegendLocation.TOP:
            if not legend.isAttachedToChart():
                legend.attachToChart()
            self.chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
            self.chart.legend().setBackgroundVisible(False)
        elif loc == LegendLocation.BOTTOM:
            if not legend.isAttachedToChart():
                legend.attachToChart()
            self.chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)
            self.chart.legend().setBackgroundVisible(False)
        elif loc == LegendLocation.LEFT:
            if not legend.isAttachedToChart():
                legend.attachToChart()
            self.chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
            self.chart.legend().setBackgroundVisible(False)
        elif loc == LegendLocation.RIGHT:
            if not legend.isAttachedToChart():
                legend.attachToChart()
            self.chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            self.chart.legend().setBackgroundVisible(False)
        elif loc == LegendLocation.CUSTOM:
            if legend.isAttachedToChart():
                legend.detachFromChart()
                legend.setZValue(99)
            self.chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
            self.chart.legend().setBackgroundVisible(True)
            self.update_legend_geometry()

    @QtCore.Slot(int, int, int, int)
    def set_custom_legend_location(self, x: int, y: int, w: int, h: int):
        self.__legend_custom_location = (x, y, w, h)
        self.update_legend_geometry()

    def update_legend_geometry(self):
        legend = self.chart.legend()

        if legend.isAttachedToChart():
            return

        chart_rect = self.chart.plotArea()

        x, y, w, h = self.__legend_custom_location
        legend.setGeometry(QtCore.QRectF(
            chart_rect.x() + chart_rect.width() * x / 100,
            chart_rect.y() + chart_rect.height() * y / 100,
            chart_rect.width() * w / 100,
            chart_rect.height() * h / 100,
        ))

    @QtCore.Slot(float)
    def set_x_axis_upper_lim(self, value: float):
        if value > self.x_axis.min():
            self.x_axis.setMax(value)

    @QtCore.Slot(float)
    def set_x_axis_lower_lim(self, value: float):
        if value < self.x_axis.max():
            self.x_axis.setMin(value)

    @QtCore.Slot(int)
    def set_x_axis_tick_count(self, value: int):
        self.x_axis.setTickCount(value)
        self.w_chart_view.update()
        self.w_chart_view.repaint()

    @QtCore.Slot(str)
    def set_x_axis_label(self, label: str):
        self.x_axis.setTitleText(label)
        self.w_chart_view.update()
        self.w_chart_view.repaint()

    @QtCore.Slot(float)
    def set_y_axis_upper_lim(self, value: float):
        if value > self.y_axis.min():
            self.y_axis.setMax(value)

    @QtCore.Slot(float)
    def set_y_axis_lower_lim(self, value: float):
        if value < self.y_axis.max():
            self.y_axis.setMin(value)

    @QtCore.Slot(int)
    def set_y_axis_tick_count(self, value: int):
        self.y_axis.setTickCount(value)
        self.w_chart_view.update()
        self.w_chart_view.repaint()

    @QtCore.Slot(str)
    def set_y_axis_label(self, label: str):
        self.y_axis.setTitleText(label)
        self.w_chart_view.update()
        self.w_chart_view.repaint()

    @QtCore.Slot()
    def open_context_menu(self, position):
        menu = RoundMenu(self)

        copy_png = QtGui.QAction('Copy as Image')
        copy_png.triggered.connect(self.handle_copy_chart_to_clipboard)
        menu.addAction(copy_png)

        if len(self.chart.series()) > 1:
            menu.addSeparator()

            hide_all_action = QtGui.QAction('Hide All Data')
            hide_all_action.triggered.connect(self.hide_all_curves)
            menu.addAction(hide_all_action)

            show_all_action = QtGui.QAction('Show All Data')
            show_all_action.triggered.connect(self.show_all_curves)
            menu.addAction(show_all_action)

        menu.exec(self.mapToGlobal(position))

    def render_chart_as_image(self) -> QtGui.QImage:
        rect = self.w_chart_view.viewport().rect()

        # Set the scale factor for higher resolution (e.g., 2x)
        scale_factor = 2
        scaled_width = rect.width() * scale_factor
        scaled_height = rect.height() * scale_factor

        # Create a QImage with the new size
        image = QtGui.QImage(scaled_width, scaled_height, QtGui.QImage.Format.Format_ARGB32)

        # Fill the image with a transparent background
        if qconfig.theme == Theme.DARK:
            image.fill(QtCore.Qt.GlobalColor.black)
        else:
            image.fill(QtCore.Qt.GlobalColor.white)

        # Create a QPainter to render the chart onto the image
        painter = QtGui.QPainter(image)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.LosslessImageRendering)
        painter.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        # Scale the painter to render at higher resolution
        painter.scale(scale_factor, scale_factor)

        # Create a new rectangle with the same position but scaled size
        scaled_rect = QtCore.QRect(rect.topLeft(), rect.size() * scale_factor)

        # Render the chart view onto the QImage
        self.w_chart_view.render(painter, QtCore.QRect(), QtCore.QRect(scaled_rect))

        painter.end()

        # Set the DPI (dots per inch) to adjust the appearance size when pasted
        dpi = 96 * 2.1  # windows native is 96 dpi, the image has been scaled up by 2, so now need to scale down
        image.setDotsPerMeterX(int(dpi * 39.3701))  # 1 inch = 39.3701 meters
        image.setDotsPerMeterY(int(dpi * 39.3701))
        return image

    @QtCore.Slot()
    def handle_copy_chart_to_clipboard(self):
        # Convert QImage to QPixmap
        pixmap = QtGui.QPixmap.fromImage(self.render_chart_as_image())

        # Copy QPixmap to the clipboard
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.clear(QtGui.QClipboard.Mode.Clipboard)
        clipboard.setPixmap(pixmap, QtGui.QClipboard.Mode.Clipboard)

    @QtCore.Slot(str)
    def handle_save_chart_png(self, fp_png: str):
        self.render_chart_as_image().save(fp_png, 'PNG')

    @QtCore.Slot()
    def handle_theme_changed(self):
        if qconfig.theme == Theme.DARK:
            brush = QtGui.QBrush(QtCore.Qt.GlobalColor.white)
            background_brush = QtGui.QBrush(QtCore.Qt.GlobalColor.black)
        else:
            brush = QtGui.QBrush(QtCore.Qt.GlobalColor.black)
            background_brush = QtGui.QBrush(QtCore.Qt.GlobalColor.white)

        self.x_axis.setLabelsBrush(brush)
        self.x_axis.setTitleBrush(brush)
        self.y_axis.setLabelsBrush(brush)
        self.y_axis.setTitleBrush(brush)

        self.chart.legend().setBrush(background_brush)

        for name, series in self.dict_chart_series.items():
            if series.isVisible():
                for marker in self.chart.legend().markers(series):
                    marker.setLabelBrush(brush)
            else:
                for marker in self.chart.legend().markers(series):
                    marker.setLabelBrush(QtCore.Qt.GlobalColor.darkGray)


class MetaQWidget(type(QtWidgets.QWidget), type):
    pass


class ChartSettingCommonBase(metaclass=MetaQWidget):
    @property
    @abstractmethod
    def current_state_is_moving_average_applied(self) -> bool:
        pass

    @current_state_is_moving_average_applied.setter
    @abstractmethod
    def current_state_is_moving_average_applied(self, value: bool):
        pass

    @property
    @abstractmethod
    def setting(self) -> SettingWidget:
        pass

    @property
    @abstractmethod
    def chart(self) -> ChartWidget:
        pass

    def sync_setting_from_chart(self):
        # QtCore.QTimer.singleShot(0, self.update)
        self.setting.blockSignals(True)
        self.setting.axis_x.label.setText(self.chart.x_axis.titleText())
        self.setting.axis_x.upper_lim.set_default_value(self.chart.x_axis.max())
        self.setting.axis_x.lower_lim.set_default_value(self.chart.x_axis.min())
        self.setting.axis_x.tick_count.set_default_value(self.chart.x_axis.tickCount())
        self.setting.axis_y.label.setText(self.chart.y_axis.titleText())
        self.setting.axis_y.upper_lim.set_default_value(self.chart.y_axis.max())
        self.setting.axis_y.lower_lim.set_default_value(self.chart.y_axis.min())
        self.setting.axis_y.tick_count.set_default_value(self.chart.y_axis.tickCount())
        legend = self.chart.legend()
        self.setting.legend.in_visible.setChecked(legend.isVisible())
        self.setting.legend.in_marker_visible.setChecked(self.chart.flag_marker_visible)
        if (legend_alignment := legend.alignment()) == LegendLocation.LEFT.value:
            self.setting.legend.in_loc_left.setChecked(True)
        elif legend_alignment == LegendLocation.RIGHT.value:
            self.setting.legend.in_loc_right.setChecked(True)
        elif legend_alignment == LegendLocation.TOP.value:
            self.setting.legend.in_loc_top.setChecked(True)
        elif legend_alignment == LegendLocation.BOTTOM.value:
            self.setting.legend.in_loc_bottom.setChecked(True)
        elif legend_alignment == LegendLocation.CUSTOM.value:
            self.setting.legend.in_loc_custom.setChecked(True)
        self.setting.blockSignals(False)

    def connect_signals(self):
        self.setting.axis_x.label_changed.connect(self.chart.set_x_axis_label)
        self.setting.axis_x.upper_limit_changed.connect(self.chart.set_x_axis_upper_lim)
        self.setting.axis_x.lower_limit_changed.connect(self.chart.set_x_axis_lower_lim)
        self.setting.axis_x.tick_count_changed.connect(self.handle_x_axis_tick_count_changed_from_setting)

        self.setting.axis_y.label_changed.connect(self.chart.set_y_axis_label)
        self.setting.axis_y.upper_limit_changed.connect(self.chart.set_y_axis_upper_lim)
        self.setting.axis_y.lower_limit_changed.connect(self.chart.set_y_axis_lower_lim)
        self.setting.axis_y.tick_count_changed.connect(self.chart.set_y_axis_tick_count)

        self.setting.legend.visible_changed.connect(self.chart.set_legend_visible)
        self.setting.legend.marker_visible_changed.connect(self.chart.handle_marker_visible_changed)
        self.setting.legend.location_changed.connect(self.chart.set_legend_location)
        self.setting.legend.custom_location_changed.connect(self.chart.set_custom_legend_location)

        self.setting.data.setting_changed.connect(self.handle_data_setting_changed)

    @QtCore.Slot(str)
    def handle_x_axis_label_changed_from_setting(self, value: str):
        self.chart.set_x_axis_label(value)

    @QtCore.Slot(float)
    def handle_x_axis_upper_lim_changed_from_setting(self, float: int):
        self.chart.set_x_axis_upper_lim(float)

    @QtCore.Slot(int)
    def handle_x_axis_tick_count_changed_from_setting(self, value: int):
        self.chart.set_x_axis_tick_count(value)

    @QtCore.Slot()
    def handle_data_setting_changed(self):
        is_abs = self.setting.data.in_absolute_values.isChecked()
        is_ma = self.setting.data.in_ma_check.isChecked()
        ma_window = self.setting.data.in_ma_window.value() if self.setting.data.in_ma_check.isChecked() else 0

        max_, min_ = list(), list()
        for name, series in self.chart.dict_chart_series.items():
            series.apply_setting(ma_window, is_abs)
            if series.isVisible():
                max_.append(series.y_max)
                min_.append(series.y_min)

        max_ = max(max_ or (self.setting.axis_y.upper_lim.value()))
        if is_abs is True:
            self.setting.axis_y.upper_lim.set_default_value(max_)
            self.setting.axis_y.lower_lim.set_default_value(0)
            self.setting.axis_y.upper_lim.setSingleStep(max_ / 100)
            self.setting.axis_y.lower_lim.setSingleStep(max_ / 100)
        else:
            min_ = min(min_ or (self.setting.axis_y.lower_lim.value()))
            self.setting.axis_y.upper_lim.set_default_value(max_)
            self.setting.axis_y.lower_lim.set_default_value(min_)
            self.setting.axis_y.upper_lim.setSingleStep((max_ - min_) / 100)
            self.setting.axis_y.lower_lim.setSingleStep((max_ - min_) / 100)

        self.current_state_is_moving_average_applied = is_ma

        QtCore.QTimer.singleShot(0, self.chart.update)
