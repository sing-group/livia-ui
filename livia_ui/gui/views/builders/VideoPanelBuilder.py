from PyQt5.QtWidgets import QWidget

from livia_ui.gui.views.builders.GuiBuilder import GuiBuilder


class VideoPanelBuilder(GuiBuilder[QWidget]):
    def __init__(self):
        super().__init__()

    def _create_parent(self, parent: QWidget) -> QWidget:
        return QWidget(parent)
