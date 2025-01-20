from PySide6 import QtCore, QtWidgets, QtGui

from qfluentwidgets import (
    FluentStyleSheet, qconfig, Theme
)


class MaskWidget(QtWidgets.QWidget):
    mouse_left_button_clicked = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = None
        qconfig.themeChangedFinished.connect(self.handle_theme_changed)
        self.handle_theme_changed()

    @QtCore.Slot()
    def handle_theme_changed(self):
        if qconfig.theme == Theme.DARK:
            self._color = QtGui.QColor(255, 255, 255, 153)
        else:
            self._color = QtGui.QColor(0, 0, 0, 153)
        self.repaint()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.mouse_left_button_clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self._color)
        super().paintEvent(event)


class MaskDialogBase(QtWidgets.QDialog):
    """ Dialog box base class with a mask """

    def __init__(self, parent=None, widget_layout_type=QtWidgets.QHBoxLayout):
        super().__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        try:
            self.setGeometry(0, 0, parent.width(), parent.height())
        except AttributeError:
            # in case of parent=None
            pass

        self.window_mask = MaskWidget(self)
        self.window_mask.resize(self.size())
        self.window_mask.mouse_left_button_clicked.connect(self.accept)

        self.widget = QtWidgets.QFrame(self)
        self.widget.setObjectName('centerWidget')
        self.widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

        self.widget_layout = widget_layout_type(self.widget)
        self.widget_layout.setSpacing(0)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(100, 100, 100, 100)
        self.main_layout.addWidget(self.widget)

        self.window().installEventFilter(self)

        FluentStyleSheet.DIALOG.apply(self)

        self.set_shadow_effect(60, (0, 10), QtGui.QColor(0, 0, 0, 50))
        self.set_mask_color(QtGui.QColor(0, 0, 0, 76))

    def set_shadow_effect(self, blur_radius=60, offset=(0, 10), color=QtGui.QColor(0, 0, 0, 100)):
        """ add shadow to dialog """
        shadow_effect = QtWidgets.QGraphicsDropShadowEffect(self.widget)
        shadow_effect.setBlurRadius(blur_radius)
        shadow_effect.setOffset(*offset)
        shadow_effect.setColor(color)
        self.widget.setGraphicsEffect(None)
        self.widget.setGraphicsEffect(shadow_effect)

    def set_mask_color(self, color: QtGui.QColor):
        """ set the color of mask """
        self.window_mask.setStyleSheet(f"""
            background: rgba({color.red()}, {color.blue()}, {color.green()}, {color.alpha()})
        """)

    def showEvent(self, e):
        """ fade in """
        opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)
        opacity_ani = QtCore.QPropertyAnimation(opacity_effect, b'opacity', self)
        opacity_ani.setStartValue(0)
        opacity_ani.setEndValue(1)
        opacity_ani.setDuration(200)
        opacity_ani.setEasingCurve(QtCore.QEasingCurve.Type.InSine)
        opacity_ani.finished.connect(lambda: self.setGraphicsEffect(None))
        opacity_ani.start()
        super().showEvent(e)

    def done(self, code):
        """ fade out """
        self.widget.setGraphicsEffect(None)
        opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)
        opacity_ani = QtCore.QPropertyAnimation(opacity_effect, b'opacity', self)
        opacity_ani.setStartValue(1)
        opacity_ani.setEndValue(0)
        opacity_ani.setDuration(100)
        opacity_ani.finished.connect(lambda: self._on_done(code))
        opacity_ani.start()

    def _on_done(self, code):
        self.setGraphicsEffect(None)
        QtWidgets.QDialog.done(self, code)

    def resizeEvent(self, e):
        self.window_mask.resize(self.size())

    def eventFilter(self, obj, e: QtCore.QEvent):
        if obj is self.window():
            if e.type() == QtCore.QEvent.Type.Resize:
                re = QtGui.QResizeEvent(e)
                self.resize(re.size())
        return super().eventFilter(obj, e)
