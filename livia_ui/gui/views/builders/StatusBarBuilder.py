from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QStatusBar

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow


class StatusBarBuilder(ABC):
    @abstractmethod
    def build(self, main_window: LiviaWindow, status_bar: QStatusBar):
        pass
