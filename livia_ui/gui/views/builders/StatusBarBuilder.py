from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QStatusBar

from livia_ui.gui.views.builders.GuiBuilder import GuiBuilder


class StatusBarBuilder(GuiBuilder[QStatusBar]):
    def __init__(self, independent_thread: bool = False, thread_priority: int = QThread.NormalPriority):
        super().__init__(independent_thread, thread_priority)
