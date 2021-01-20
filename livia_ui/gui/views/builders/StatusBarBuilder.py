from __future__ import annotations

from typing import TYPE_CHECKING

from PySide2.QtWidgets import QStatusBar, QWidget

from livia_ui.gui.views.builders.GuiBuilder import GuiBuilder

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow


class StatusBarBuilder(GuiBuilder[QStatusBar]):
    def __init__(self, livia_window: LiviaWindow, *args, **kwargs):
        super(StatusBarBuilder, self).__init__(livia_window, *args, **kwargs)

    def _create_parent_widget(self, parent: QWidget) -> QStatusBar:
        return QStatusBar(parent)
