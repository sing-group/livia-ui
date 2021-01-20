from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, TYPE_CHECKING

from livia_ui.gui.views.builders.BottomToolBarBuilder import BottomToolBarBuilder
from livia_ui.gui.views.builders.MenuBarBuilder import MenuBarBuilder
from livia_ui.gui.views.builders.StatusBarBuilder import StatusBarBuilder
from livia_ui.gui.views.builders.TopToolBarBuilder import TopToolBarBuilder
from livia_ui.gui.views.builders.VideoPanelBuilder import VideoPanelBuilder

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow

T = TypeVar("T", MenuBarBuilder, TopToolBarBuilder, VideoPanelBuilder, BottomToolBarBuilder, StatusBarBuilder)


class GuiBuilderFactory(ABC, Generic[T]):
    @abstractmethod
    def create_builder(self, livia_window: LiviaWindow, *args, **kwargs) -> T:
        raise NotImplementedError()
