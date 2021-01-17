from livia_ui.gui.views.builders.BottomToolBarBuilder import BottomToolBarBuilder
from livia_ui.gui.views.builders.DefaultBottomToolBarBuilder import DefaultBottomToolBarBuilder
from livia_ui.gui.views.builders.DefaultMenuBarBuilder import DefaultMenuBarBuilder
from livia_ui.gui.views.builders.DefaultStatusBarBuilder import DefaultStatusBarBuilder
from livia_ui.gui.views.builders.DefaultTopToolBarBuilder import DefaultTopToolBarBuilder
from livia_ui.gui.views.builders.DefaultVideoPanelBuilder import DefaultVideoPanelBuilder
from livia_ui.gui.views.builders.MenuBarBuilder import MenuBarBuilder
from livia_ui.gui.views.builders.StatusBarBuilder import StatusBarBuilder
from livia_ui.gui.views.builders.TopToolBarBuilder import TopToolBarBuilder
from livia_ui.gui.views.builders.VideoPanelBuilder import VideoPanelBuilder


class GuiBuilders:
    def __init__(self,
                 menu_bar_builder: MenuBarBuilder = DefaultMenuBarBuilder(),
                 top_tool_bar_builder: TopToolBarBuilder = DefaultTopToolBarBuilder(),
                 video_panel_builder: VideoPanelBuilder = DefaultVideoPanelBuilder(),
                 bottom_tool_bar_builder: BottomToolBarBuilder = DefaultBottomToolBarBuilder(),
                 status_bar_builder: StatusBarBuilder = DefaultStatusBarBuilder()):
        self._menu_bar_builder: MenuBarBuilder = menu_bar_builder
        self._top_tool_bar_builder: TopToolBarBuilder = top_tool_bar_builder
        self._video_panel_builder: VideoPanelBuilder = video_panel_builder
        self._bottom_tool_bar_builder: BottomToolBarBuilder = bottom_tool_bar_builder
        self._status_bar_builder: StatusBarBuilder = status_bar_builder

    @property
    def menu_bar_builder(self) -> MenuBarBuilder:
        return self._menu_bar_builder

    @property
    def top_tool_bar_builder(self) -> TopToolBarBuilder:
        return self._top_tool_bar_builder

    @property
    def bottom_tool_bar_builder(self) -> TopToolBarBuilder:
        return self._bottom_tool_bar_builder

    @property
    def video_panel_builder(self) -> VideoPanelBuilder:
        return self._video_panel_builder

    @property
    def status_bar_builder(self) -> StatusBarBuilder:
        return self._status_bar_builder
