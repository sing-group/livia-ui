from PyQt5.QtWidgets import QMenuBar, QWidget

from livia_ui.gui.views.builders.GuiBuilder import GuiBuilder


class MenuBarBuilder(GuiBuilder[QMenuBar]):
    def __init__(self):
        super().__init__()

    def _create_parent(self, parent: QWidget) -> QMenuBar:
        return QMenuBar(parent)
