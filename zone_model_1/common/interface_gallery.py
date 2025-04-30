from PySide6 import QtWidgets, QtCore, QtGui
from qfluentwidgets import (
    ScrollArea, ToolButton, FluentIcon, isDarkTheme, IconWidget, ToolTipFilter, TitleLabel, CaptionLabel,
    StrongBodyLabel, BodyLabel, toggleTheme
)

from zone_model_1.common.style_sheet import StyleSheet


class SeparatorWidget(QtWidgets.QWidget):
    """ Seperator widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(6, 16)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(1)
        pen.setCosmetic(True)
        c = QtGui.QColor(255, 255, 255, 21) if isDarkTheme() else QtGui.QColor(0, 0, 0, 15)
        pen.setColor(c)
        painter.setPen(pen)

        x = self.width() // 2
        painter.drawLine(x, 0, x, self.height())


class ToolBar(QtWidgets.QWidget):
    """ Tool bar """

    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent=parent)
        self.title_label = TitleLabel(title, self)
        self.subtitle_label = CaptionLabel(subtitle, self)

        self.theme_button = ToolButton(FluentIcon.CONSTRACT, self)
        self.feedback_button = ToolButton(FluentIcon.FEEDBACK, self)

        # self.vBoxLayout = QVBoxLayout(self)

        self.setFixedHeight(88)

        header_layout = QtWidgets.QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        header_layout.addWidget(self.title_label)
        header_layout.addSpacing(4)
        header_layout.addWidget(self.subtitle_label)

        button_layout_ = QtWidgets.QHBoxLayout()
        button_layout_.setContentsMargins(0, 0, 0, 0)
        button_layout_.addStretch()
        button_layout_.addWidget(self.theme_button)
        button_layout_.addWidget(self.feedback_button)
        button_layout = QtWidgets.QVBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addLayout(button_layout_)
        button_layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(36, 22, 36, 12)
        layout.addLayout(header_layout)
        # layout.addStretch(1)
        layout.addLayout(button_layout)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.theme_button.installEventFilter(ToolTipFilter(self.theme_button))
        self.feedback_button.installEventFilter(
            ToolTipFilter(self.feedback_button))
        self.theme_button.setToolTip(self.tr('Toggle theme'))
        self.feedback_button.setToolTip(self.tr('Send feedback'))

        self.theme_button.clicked.connect(lambda: toggleTheme(True))

        self.subtitle_label.setTextColor(QtGui.QColor(96, 96, 96), QtGui.QColor(216, 216, 216))

        self.feedback_button.hide()


class ExampleCard(QtWidgets.QWidget):
    """ Example card """

    def __init__(self, title, widget: QtWidgets.QWidget, sourcePath, stretch=0, parent=None):
        super().__init__(parent=parent)
        self.widget = widget
        self.stretch = stretch

        self.titleLabel = StrongBodyLabel(title, self)
        self.card = QtWidgets.QFrame(self)

        self.sourceWidget = QtWidgets.QFrame(self.card)
        self.sourcePath = sourcePath
        self.sourcePathLabel = BodyLabel(self.tr('Source code'), self.sourceWidget)
        self.linkIcon = IconWidget(FluentIcon.LINK, self.sourceWidget)

        self.vBoxLayout = QtWidgets.QVBoxLayout(self)
        self.cardLayout = QtWidgets.QVBoxLayout(self.card)
        self.topLayout = QtWidgets.QHBoxLayout()
        self.bottomLayout = QtWidgets.QHBoxLayout(self.sourceWidget)

        self.__init_widget()

    def __init_widget(self):
        self.linkIcon.setFixedSize(16, 16)
        self.__init_layout()

        self.sourceWidget.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.sourceWidget.installEventFilter(self)

        self.card.setObjectName('card')
        self.sourceWidget.setObjectName('sourceWidget')

    def __init_layout(self):
        self.vBoxLayout.setSizeConstraint(QtWidgets.QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.cardLayout.setSizeConstraint(QtWidgets.QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.topLayout.setSizeConstraint(QtWidgets.QHBoxLayout.SizeConstraint.SetMinimumSize)

        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.setContentsMargins(12, 12, 12, 12)
        self.bottomLayout.setContentsMargins(18, 18, 18, 18)
        self.cardLayout.setContentsMargins(0, 0, 0, 0)

        self.vBoxLayout.addWidget(self.titleLabel, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.card, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.cardLayout.setSpacing(0)
        self.cardLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.cardLayout.addLayout(self.topLayout, 0)
        self.cardLayout.addWidget(self.sourceWidget, 0, QtCore.Qt.AlignmentFlag.AlignBottom)

        self.widget.setParent(self.card)
        self.topLayout.addWidget(self.widget)
        if self.stretch == 0:
            self.topLayout.addStretch(1)

        self.widget.show()

        self.bottomLayout.addWidget(self.sourcePathLabel, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.bottomLayout.addStretch(1)
        self.bottomLayout.addWidget(self.linkIcon, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        self.bottomLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)

    def eventFilter(self, obj, e):
        if obj is self.sourceWidget:
            if e.type() == QtCore.QEvent.Type.MouseButtonRelease:
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(self.sourcePath))

        return super().eventFilter(obj, e)


class SimpleCard(QtWidgets.QWidget):
    """ Example card """

    def __init__(self, title: str, widget: QtWidgets.QWidget, stretch=0, parent=None):
        super().__init__(parent=parent)
        self.widget = widget
        self.stretch = stretch

        self.title_label = StrongBodyLabel(title, self)
        if not title:
            self.title_label.hide()
        self.title_widget = QtWidgets.QWidget()
        self.title_layout = QtWidgets.QHBoxLayout(self.title_widget)
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_layout.addWidget(self.title_label)
        self.card = QtWidgets.QFrame(self)
        self.card.setObjectName('card')

        self.top_layout = QtWidgets.QVBoxLayout()
        self.top_layout.setContentsMargins(12, 12, 12, 12)
        self.top_layout.setSizeConstraint(QtWidgets.QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.top_layout.addWidget(self.widget)

        self.card_layout = QtWidgets.QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(0)
        self.card_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.card_layout.addLayout(self.top_layout, 0)
        self.card_layout.setSizeConstraint(QtWidgets.QVBoxLayout.SizeConstraint.SetMinimumSize)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QtWidgets.QVBoxLayout.SizeConstraint.SetMinimumSize)
        layout.addWidget(self.title_widget, 0)
        layout.addWidget(self.card, 1)
        # layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.widget.setParent(self.card)
        if self.stretch == 0:
            self.top_layout.addStretch(1)

        self.widget.show()


# SimpleCard = ExampleCard

class GalleryInterfaceViewWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class GalleryInterface(ScrollArea):
    """ Gallery interface """

    def __init__(self, title: str, subtitle: str, parent=None):
        """
        Parameters
        ----------
        title: str
            The title of gallery

        subtitle: str
            The subtitle of gallery

        parent: QWidget
            parent widget
        """
        super().__init__(parent=parent)
        self.view = QtWidgets.QWidget(self)
        self.tool_bar = ToolBar(title, subtitle, self)
        self.v_layout = QtWidgets.QVBoxLayout(self.view)

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, self.tool_bar.height(), 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.v_layout.setSpacing(30)
        self.v_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.v_layout.setContentsMargins(36, 20, 36, 36)

        self.view.setObjectName('view')
        StyleSheet.GALLERY_INTERFACE.apply(self)

    def addExampleCard(self, title: str, widget: QtWidgets.QWidget, sourcePath: str, stretch=0):
        card = ExampleCard(title, widget, sourcePath, stretch, self.view)
        self.v_layout.addWidget(card, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        return card

    def add_simple_card(self, title, widget, stretch=0):
        card = SimpleCard(title, widget, stretch, self.view)
        self.v_layout.addWidget(card, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        return card

    def add_card(self, title, card, stretch=0):
        self.v_layout.addWidget(card, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        return card

    def scrollToCard(self, index: int):
        """ scroll to example card """
        w = self.v_layout.itemAt(index).widget()
        self.verticalScrollBar().setValue(w.y())

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.tool_bar.resize(self.width(), self.tool_bar.height())
