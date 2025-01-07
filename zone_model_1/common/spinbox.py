from PySide6 import QtCore, QtWidgets

from qfluentwidgets import Flyout, FlyoutAnimationType
from qfluentwidgets.components.widgets.spin_box import SpinBoxBase, CompactSpinButton, SpinFlyoutView


class __CompactSpinBoxBase(SpinBoxBase):
    """ Compact spin box base """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.compactSpinButton = CompactSpinButton(self)
        self.spinFlyoutView = SpinFlyoutView(self)
        self.spinFlyout = Flyout(self.spinFlyoutView, self, False)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.compactSpinButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.compactSpinButton.clicked.connect(self._showFlyout)
        self.spinFlyoutView.upButton.clicked.connect(self.stepUp)
        self.spinFlyoutView.downButton.clicked.connect(self.stepDown)

        self.spinFlyout.hide()
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()

    def setAccelerated(self, on: bool):
        super().setAccelerated(on)
        self.spinFlyoutView.upButton.setAutoRepeat(on)
        self.spinFlyoutView.downButton.setAutoRepeat(on)

    def focusInEvent(self, e):
        super().focusInEvent(e)

    def setSymbolVisible(self, isVisible: bool):
        super().setSymbolVisible(isVisible)
        self.compactSpinButton.setVisible(isVisible)

    def _showFlyout(self):
        if self.spinFlyout.isVisible() or self.isReadOnly():
            return

        y = int(self.compactSpinButton.height() / 2 - 46)
        pos = self.compactSpinButton.mapToGlobal(QtCore.QPoint(-12, y))

        self.spinFlyout.exec(pos, FlyoutAnimationType.FADE_IN)


class CompactDoubleSpinBox(__CompactSpinBoxBase, QtWidgets.QDoubleSpinBox):
    pass


class CompactSpinBox(__CompactSpinBoxBase, QtWidgets.QSpinBox):
    pass
