from PyQt5.QtWidgets import QWidget

from livia_ui.gui.views.builders.DefaultVideoPanelBuilder import DefaultVideoPanelBuilder
from livia_ui.gui.views.builders.DefaultMenuBarBuilder import DefaultMenuBarBuilder
from livia_ui.gui.views.builders.DefaultStatusBarBuilder import DefaultStatusBarBuilder
from livia_ui.gui.views.builders.DefaultToolBarBuilder import DefaultToolBarBuilder
from livia_ui.gui.views.builders.MenuBarBuilder import MenuBarBuilder
from livia_ui.gui.views.builders.StatusBarBuilder import StatusBarBuilder
from livia_ui.gui.views.builders.ToolBarBuilder import ToolBarBuilder
from livia_ui.gui.views.builders.VideoPanelBuilder import VideoPanelBuilder


class GuiBuilders:
    def __init__(self,
                 menu_bar_builder: MenuBarBuilder = DefaultMenuBarBuilder(),
                 tool_bar_builder: ToolBarBuilder = DefaultToolBarBuilder(),
                 video_panel_builder: VideoPanelBuilder = DefaultVideoPanelBuilder(),
                 status_bar_builder: StatusBarBuilder = DefaultStatusBarBuilder()
                 ):
        self._menu_bar_builder: MenuBarBuilder = menu_bar_builder
        self._tool_bar_builder: ToolBarBuilder = tool_bar_builder
        self._video_panel_builder: VideoPanelBuilder = video_panel_builder
        self._status_bar_builder: StatusBarBuilder = status_bar_builder

    @property
    def menu_bar_builder(self) -> MenuBarBuilder:
        return self._menu_bar_builder

    @property
    def tool_bar_builder(self) -> ToolBarBuilder:
        return self._tool_bar_builder

    @property
    def video_panel_builder(self) -> VideoPanelBuilder:
        return self._video_panel_builder

    @property
    def status_bar_builder(self) -> StatusBarBuilder:
        return self._status_bar_builder
