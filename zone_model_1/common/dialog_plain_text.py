from PySide6 import QtWidgets, QtCore
from qfluentwidgets import BodyLabel, PlainTextEdit, TextEdit

from zone_model_1.common.mask_dialog_base import MaskDialogBase


class PlainTextDialog(MaskDialogBase):
    """ Custom message box """

    def __init__(self, title: str, parent=None):
        super().__init__(parent, widget_layout_type=QtWidgets.QVBoxLayout)
        self.title_label = BodyLabel(title, self)
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.title_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)

        self.content = PlainTextEdit(self)

        self.widget_layout.addSpacing(6)
        self.widget_layout.addWidget(self.title_label)
        self.widget_layout.addSpacing(6)
        self.widget_layout.addWidget(self.content)


class TextEditDialog(MaskDialogBase):
    """ Custom message box """

    def __init__(self, title: str, parent=None):
        super().__init__(parent, widget_layout_type=QtWidgets.QVBoxLayout)
        self.title_label = BodyLabel(title, self)
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.title_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)

        self.content = TextEdit(self)
        self.content.setReadOnly(True)

        self.widget_layout.addSpacing(6)
        self.widget_layout.addWidget(self.title_label)
        self.widget_layout.addSpacing(6)
        self.widget_layout.addWidget(self.content)
