from livia_ui.gui.views.builders.BottomToolBarBuilder import BottomToolBarBuilder
from livia_ui.gui.views.builders.DefaultBottomToolBarBuilder import DefaultBottomToolBarBuilder
from livia_ui.gui.views.builders.DefaultMenuBarBuilder import DefaultMenuBarBuilder
from livia_ui.gui.views.builders.DefaultStatusBarBuilder import DefaultStatusBarBuilder
from livia_ui.gui.views.builders.DefaultTopToolBarBuilder import DefaultTopToolBarBuilder
from livia_ui.gui.views.builders.DefaultVideoPanelBuilder import DefaultVideoPanelBuilder
from livia_ui.gui.views.builders.GuiBuilderFactory import GuiBuilderFactory
from livia_ui.gui.views.builders.MenuBarBuilder import MenuBarBuilder
from livia_ui.gui.views.builders.StatusBarBuilder import StatusBarBuilder
from livia_ui.gui.views.builders.TopToolBarBuilder import TopToolBarBuilder
from livia_ui.gui.views.builders.VideoPanelBuilder import VideoPanelBuilder


class GuiBuilders:
    def __init__(self,
                 menu_bar_builder: GuiBuilderFactory[MenuBarBuilder] = DefaultMenuBarBuilder.factory(),
                 top_tool_bar_builder: GuiBuilderFactory[TopToolBarBuilder] = DefaultTopToolBarBuilder.factory(),
                 video_panel_builder: GuiBuilderFactory[VideoPanelBuilder] = DefaultVideoPanelBuilder.factory(),
                 bottom_tool_bar_builder: GuiBuilderFactory[
                     BottomToolBarBuilder] = DefaultBottomToolBarBuilder.factory(),
                 status_bar_builder: GuiBuilderFactory[StatusBarBuilder] = DefaultStatusBarBuilder.factory()):
        self._menu_bar_builder: GuiBuilderFactory[MenuBarBuilder] = menu_bar_builder
        self._top_tool_bar_builder: GuiBuilderFactory[TopToolBarBuilder] = top_tool_bar_builder
        self._video_panel_builder: GuiBuilderFactory[VideoPanelBuilder] = video_panel_builder
        self._bottom_tool_bar_builder: GuiBuilderFactory[BottomToolBarBuilder] = bottom_tool_bar_builder
        self._status_bar_builder: GuiBuilderFactory[StatusBarBuilder] = status_bar_builder

    @property
    def menu_bar_builder(self) -> GuiBuilderFactory[MenuBarBuilder]:
        return self._menu_bar_builder

    @property
    def top_tool_bar_builder(self) -> GuiBuilderFactory[TopToolBarBuilder]:
        return self._top_tool_bar_builder

    @property
    def bottom_tool_bar_builder(self) -> GuiBuilderFactory[TopToolBarBuilder]:
        return self._bottom_tool_bar_builder

    @property
    def video_panel_builder(self) -> GuiBuilderFactory[VideoPanelBuilder]:
        return self._video_panel_builder

    @property
    def status_bar_builder(self) -> GuiBuilderFactory[StatusBarBuilder]:
        return self._status_bar_builder
