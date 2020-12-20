from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QMenuBar

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow


class MenuBarBuilder(ABC):
    @abstractmethod
    def build(self, main_window: LiviaWindow, menu_bar: QMenuBar):
        pass
