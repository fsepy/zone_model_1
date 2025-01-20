from PySide6 import QtCore
from qfluentwidgets import (
    ListWidget, ToolTip
)


class CustomToolTip2(ToolTip):
    def __init__(self, text='', parent=None):
        super().__init__(text, parent, transparent_for_mouse_events=False)
        self.setDuration(6000)
        self.label.setWordWrap(True)
        self.container.setMaximumWidth(320)
        self.adjustSize()
        self.is_mouse_over: bool = False

    def setText(self, text):
        super().setText(text)
        self.adjustSize()

    def enterEvent(self, event):
        """Called when the mouse enters the tooltip."""
        # Stop the timer to prevent the tooltip from hiding
        self.is_mouse_over = True
        self.timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Called when the mouse leaves the tooltip."""
        # Restart the timer to hide the tooltip after the duration
        self.is_mouse_over = False
        if self.duration() > 0:
            self.timer.start(500)
        super().leaveEvent(event)

    def show_next_to_list_widget_item(self, list_widget: ListWidget, item):
        # Get the item's rectangle in the viewport's coordinate system
        item_rect = list_widget.visualItemRect(item)

        # Map the rectangle's top-left corner to global screen coordinates
        viewport_pos = list_widget.viewport().mapToGlobal(item_rect.topRight())
        x = viewport_pos.x()
        y = viewport_pos.y() + (item_rect.height() + 8) // 2 - self.height() // 2

        self.move(QtCore.QPoint(x, y))

        super().show()
