from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QWidget

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow


class ToolBarBuilder(ABC):
    @abstractmethod
    def build(self, main_window: LiviaWindow, tool_bar: QWidget):
        pass
