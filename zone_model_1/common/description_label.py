from PySide6 import QtWidgets

from zone_model_1.common.style_sheet import StyleSheet


class DescriptionLabel(QtWidgets.QLabel):
    def __init__(self, text=''):
        super().__init__(text=text)
        self.setWordWrap(True)
        StyleSheet.DESCRIPTION_LABEL.apply(self)
