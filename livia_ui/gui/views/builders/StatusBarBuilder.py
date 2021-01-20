from PyQt5.QtWidgets import QStatusBar, QWidget

from livia_ui.gui.views.builders.GuiBuilder import GuiBuilder


class StatusBarBuilder(GuiBuilder[QStatusBar]):
    def __init__(self):
        super().__init__()

    def _create_parent(self, parent: QWidget) -> QStatusBar:
        return QStatusBar(parent)
