from __future__ import annotations

from typing import TYPE_CHECKING

from PySide2.QtWidgets import QWidget

from livia_ui.gui.views.builders.GuiBuilder import GuiBuilder

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow


class BottomToolBarBuilder(GuiBuilder[QWidget]):
    def __init__(self, livia_window: LiviaWindow, *args, **kwargs):
        super(BottomToolBarBuilder, self).__init__(livia_window, *args, **kwargs)

    def _create_parent_widget(self, parent: QWidget) -> QWidget:
        return QWidget(parent)
