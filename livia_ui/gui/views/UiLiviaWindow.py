from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QMenuBar, QWidget, QStatusBar

from livia_ui.gui.views.builders.GuiBuilders import GuiBuilders
from livia_ui.gui.views.utils.BorderLayout import BorderLayout

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow


class UiLiviaWindow(object):
    def __init__(self):
        self._livia_window: LiviaWindow = None
        self._menu_bar: QMenuBar = None
        self._top_tool_bar: QStatusBar = None
        self._video_panel: QWidget = None
        self._bottom_tool_bar: QStatusBar = None
        self._central_panel: QWidget = None
        self._status_bar: QStatusBar = None

    def setup_ui(self, livia_window: LiviaWindow, builders: GuiBuilders):
        self._livia_window = livia_window

        self._menu_bar = builders.menu_bar_builder.build(self._livia_window, self._livia_window)
        self._status_bar = builders.status_bar_builder.build(self._livia_window, self._livia_window)

        self._central_panel = QWidget(self._livia_window)
        central_layout = BorderLayout(self._central_panel, 0)
        self._central_panel.setLayout(central_layout)

        self._top_tool_bar = builders.top_tool_bar_builder.build(self._livia_window, self._central_panel)
        self._video_panel = builders.video_panel_builder.build(self._livia_window, self._central_panel)
        self._bottom_tool_bar = builders.bottom_tool_bar_builder.build(self._livia_window, self._central_panel)

        central_layout.addWidget(self._top_tool_bar, BorderLayout.North)
        central_layout.addWidget(self._video_panel, BorderLayout.Center)
        central_layout.addWidget(self._bottom_tool_bar, BorderLayout.South)

        livia_window.setMenuBar(self._menu_bar)
        livia_window.setCentralWidget(self._central_panel)
        livia_window.setStatusBar(self._status_bar)

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
