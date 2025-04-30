# coding:utf-8
from PySide6.QtCore import Qt, QSize, QModelIndex, QEvent, QRect, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPalette
from PySide6.QtWidgets import QTreeWidget, QStyledItemDelegate, QStyle, QTreeView, QApplication, QStyleOptionViewItem
from qfluentwidgets import themeColor, isDarkTheme, getFont, SmoothScrollDelegate, setCustomStyleSheet
from qfluentwidgets.components.widgets.check_box import CheckBoxIcon

from zone_model_1.common.style_sheet import StyleSheet


class TreeItemDelegate(QStyledItemDelegate):
    """ Tree item delegate """
    buttonClickedSignal = Signal(QModelIndex)

    def __init__(self, parent: QTreeView):
        super().__init__(parent)
        self.hovered_index = QModelIndex()
        self.button_hovered = False

    def paint(self, painter, option, index):
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)

        # Draw background if selected or hovered
        if option.state & (QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver):
            # Draw background
            h = option.rect.height() - 4
            c = 255 if isDarkTheme() else 0
            painter.setBrush(QColor(c, c, c, 9))
            # painter.setBrush(QColor('red'))
            painter.drawRoundedRect(5, option.rect.y() + 2, self.parent().width() - 11, h, 5, 5)

            # Draw indicator
            if option.state & QStyle.StateFlag.State_Selected and self.parent().horizontalScrollBar().value() == 0:
                painter.setBrush(themeColor())
                painter.drawRoundedRect(4, 9 + option.rect.y(), 3, h - 13, 1.5, 1.5)

        painter.restore()

        super().paint(painter, option, index)

    def _drawButton(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        button_rect = self._getButtonRect(option)
        # Adjust the button appearance based on hover state
        print(self.button_hovered)
        if self.button_hovered and self.hovered_index == index:
            painter.setBrush(Qt.GlobalColor.red)  # Hover color
        else:
            painter.setBrush(Qt.GlobalColor.gray)  # Normal color
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(button_rect, 4, 4)

        # Draw button text
        painter.setPen(Qt.white)
        painter.drawText(button_rect, Qt.AlignCenter, "Button")

    def _getButtonRect(self, option):
        button_width = 60  # Adjust as needed
        button_height = option.rect.height() - 8
        button_x = option.rect.right() - button_width - 10
        button_y = option.rect.y() + 4

        return QRect(button_x, button_y, button_width, button_height)

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseMove:
            button_rect = self._getButtonRect(option)
            pos_in_item = event.pos() - option.rect.topLeft()
            if button_rect.contains(pos_in_item):
                if not self.button_hovered or self.hovered_index != index:
                    self.button_hovered = True
                    self.hovered_index = index
                    self.parent().viewport().update(option.rect)
            else:
                if self.button_hovered and self.hovered_index == index:
                    self.button_hovered = False
                    self.hovered_index = QModelIndex()
                    self.parent().viewport().update(option.rect)
        elif event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton:
                button_rect = self._getButtonRect(option)
                pos_in_item = event.pos() - option.rect.topLeft()
                if button_rect.contains(pos_in_item):
                    self.buttonClicked(index)
                    return True
        return super().editorEvent(event, model, option, index)

    def buttonClicked(self, index):
        # Emit a signal or perform the desired action
        self.buttonClickedSignal.emit(index)

    def _drawCheckBox(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()
        checkState = Qt.CheckState(index.data(Qt.ItemDataRole.CheckStateRole))

        isDark = isDarkTheme()

        r = 4.5
        x = option.rect.x() + 23
        y = option.rect.center().y() - 9
        rect = QRectF(x, y, 19, 19)

        if checkState == Qt.CheckState.Unchecked:
            painter.setBrush(QColor(0, 0, 0, 26)
                             if isDark else QColor(0, 0, 0, 6))
            painter.setPen(QColor(255, 255, 255, 142)
                           if isDark else QColor(0, 0, 0, 122))
            painter.drawRoundedRect(rect, r, r)
        else:
            painter.setPen(themeColor())
            painter.setBrush(themeColor())
            painter.drawRoundedRect(rect, r, r)

            if checkState == Qt.CheckState.Checked:
                CheckBoxIcon.ACCEPT.render(painter, rect)
            else:
                CheckBoxIcon.PARTIAL_ACCEPT.render(painter, rect)

        painter.restore()

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)

        # Use your original getFont function or set font explicitly
        option.font = index.data(Qt.FontRole) or getFont(14)  # Replace getFont with your function

        # Text color
        textColor = Qt.white if isDarkTheme() else Qt.black
        textBrush = index.data(Qt.ForegroundRole)
        if textBrush is not None:
            textColor = textBrush.color()

        option.palette.setColor(QPalette.Text, textColor)
        option.palette.setColor(QPalette.HighlightedText, textColor)

    # def themeColor(self):
    #     # Return your theme color
    #     return QColor(0, 122, 204)

    def renderCheckIcon(self, painter, rect, checked):
        # Implement your check icon rendering
        painter.setPen(Qt.white)
        if checked:
            painter.drawLine(rect.left() + 4, rect.center().y(),
                             rect.center().x(), rect.bottom() - 4)
            painter.drawLine(rect.center().x(), rect.bottom() - 4,
                             rect.right() - 4, rect.top() + 4)
        else:
            # Partial accept icon
            painter.drawLine(rect.left() + 4, rect.center().y(),
                             rect.right() - 4, rect.center().y())


class TreeWidget(QTreeWidget):
    """ Tree widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._initView()
        self.setMouseTracking(True)

    def _initView(self):
        self.scrollDelagate = SmoothScrollDelegate(self)

        self.header().setHighlightSections(False)
        self.header().setDefaultAlignment(Qt.AlignCenter)

        delegate = TreeItemDelegate(self)
        delegate.buttonClickedSignal.connect(print)
        self.setItemDelegate(delegate)
        self.setIconSize(QSize(16, 16))

        StyleSheet.TREE_VIEW.apply(self)

    def drawBranches(self, painter, rect, index):
        rect.moveLeft(15)
        return QTreeView.drawBranches(self, painter, rect, index)

    def setBorderVisible(self, isVisible: bool):
        """ set the visibility of border """
        self.setProperty("isBorderVisible", isVisible)
        self.setStyle(QApplication.style())

    def setBorderRadius(self, radius: int):
        """ set the radius of border """
        qss = f"QTreeView{{border-radius: {radius}px}}"
        setCustomStyleSheet(self, qss, qss)


class TreeView(QTreeView):
    """ Tree view """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._initView()
        self.setMouseTracking(True)

    def _initView(self):
        self.scrollDelagate = SmoothScrollDelegate(self)

        self.header().setHighlightSections(False)
        self.header().setDefaultAlignment(Qt.AlignCenter)

        delegate = TreeItemDelegate(self)
        delegate.buttonClickedSignal.connect(print)
        self.setItemDelegate(delegate)
        self.setIconSize(QSize(16, 16))

        StyleSheet.TREE_VIEW.apply(self)

    def drawBranches(self, painter, rect, index):
        rect.moveLeft(15)
        return QTreeView.drawBranches(self, painter, rect, index)

    def setBorderVisible(self, isVisible: bool):
        """ set the visibility of border """
        self.setProperty("isBorderVisible", isVisible)
        self.setStyle(QApplication.style())

    def setBorderRadius(self, radius: int):
        """ set the radius of border """
        qss = f"QTreeView{{border-radius: {radius}px}}"
        setCustomStyleSheet(self, qss, qss)
