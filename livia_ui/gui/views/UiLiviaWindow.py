from __future__ import annotations

from typing import TYPE_CHECKING

from PySide2.QtWidgets import QMenuBar, QWidget, QStatusBar

from livia_ui.gui.views.builders.BottomToolBarBuilder import BottomToolBarBuilder
from livia_ui.gui.views.builders.GuiBuilders import GuiBuilders
from livia_ui.gui.views.builders.MenuBarBuilder import MenuBarBuilder
from livia_ui.gui.views.builders.StatusBarBuilder import StatusBarBuilder
from livia_ui.gui.views.builders.TopToolBarBuilder import TopToolBarBuilder
from livia_ui.gui.views.builders.VideoPanelBuilder import VideoPanelBuilder
from livia_ui.gui.views.utils.BorderLayout import BorderLayout

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow


class UiLiviaWindow(object):
    def __init__(self):
        self._livia_window: LiviaWindow = None

        self._menu_bar_builder: MenuBarBuilder = None
        self._top_tool_bar_builder: TopToolBarBuilder = None
        self._video_panel_builder: VideoPanelBuilder = None
        self._bottom_tool_bar_builder: BottomToolBarBuilder = None
        self._status_bar_builder: StatusBarBuilder = None

        self._menu_bar: QMenuBar = None
        self._top_tool_bar: QWidget = None
        self._video_panel: QWidget = None
        self._bottom_tool_bar: QWidget = None
        self._central_panel: QWidget = None
        self._status_bar: QStatusBar = None

    def setup_ui(self, livia_window: LiviaWindow, builders: GuiBuilders):
        self._livia_window = livia_window

        self._menu_bar_builder = builders.menu_bar_builder.create_builder(self)
        self._top_tool_bar_builder = builders.top_tool_bar_builder.create_builder(self)
        self._video_panel_builder = builders.video_panel_builder.create_builder(self)
        self._bottom_tool_bar_builder = builders.bottom_tool_bar_builder.create_builder(self)
        self._status_bar_builder = builders.status_bar_builder.create_builder(self)

        self._menu_bar = self._menu_bar_builder.build(self._livia_window)
        self._status_bar = self._status_bar_builder.build(self._livia_window)

        self._central_panel = QWidget(self._livia_window)
        central_layout = BorderLayout(self._central_panel, 0)
        self._central_panel.setLayout(central_layout)

        self._top_tool_bar = self._top_tool_bar_builder.build(self._central_panel)
        self._video_panel = self._video_panel_builder.build(self._central_panel)
        self._bottom_tool_bar = self._bottom_tool_bar_builder.build(self._central_panel)

        central_layout.addWidget(self._top_tool_bar, BorderLayout.North)
        central_layout.addWidget(self._video_panel, BorderLayout.Center)
        central_layout.addWidget(self._bottom_tool_bar, BorderLayout.South)

        self._livia_window.setMenuBar(self._menu_bar)
        self._livia_window.setCentralWidget(self._central_panel)
        self._livia_window.setStatusBar(self._status_bar)

    @property
    def main_window(self):
        return self._livia_window

    @property
    def menu_bar(self) -> QMenuBar:
        return self._menu_bar

    @property
    def central_panel(self) -> QWidget:
        return self._central_panel

    @property
    def tool_bar(self) -> QWidget:
        return self._top_tool_bar

    @property
    def video_panel(self) -> QWidget:
        return self._video_panel

    @property
    def status_bar(self) -> QStatusBar:
        return self._status_bar
