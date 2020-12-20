from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QMenuBar, QWidget, QStatusBar

from livia_ui.gui.views.builders.GuiBuilders import GuiBuilders
from livia_ui.gui.views.utils.BorderLayout import BorderLayout

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow


class UiLiviaWindow(object):
    def __init__(self):
        self._main_window: LiviaWindow = None
        self._menu_bar: QMenuBar = None
        self._tool_bar: QStatusBar = None
        self._video_panel: QWidget = None
        self._central_panel: QWidget = None
        self._status_bar: QStatusBar = None

    def setup_ui(self, main_window: LiviaWindow, builders: GuiBuilders):
        main_window.setObjectName("MainWindow")
        main_window.setEnabled(True)

        self._main_window = main_window

        self._menu_bar = QMenuBar(main_window)
        self._menu_bar.setObjectName("_menu_bar")

        self._status_bar = QStatusBar(main_window)
        self._status_bar.setObjectName("_status_bar")

        self._central_panel = QWidget(main_window)
        self._central_panel.setObjectName("_central_panel")
        central_layout = BorderLayout(self._central_panel)
        central_layout.setContentsMargins(0, 0, 0, 0)

        self._tool_bar = QWidget(self._central_panel)
        self._tool_bar.setObjectName("_tool_bar")
        BorderLayout(self._tool_bar)

        self._video_panel = QWidget(self._central_panel)
        self._video_panel.setObjectName("_video_panel")
        self._video_panel.setContentsMargins(0, 0, 0, 0)

        central_layout.addWidget(self._tool_bar, BorderLayout.North)
        central_layout.addWidget(self._video_panel, BorderLayout.Center)

        main_window.setMenuBar(self._menu_bar)
        main_window.setCentralWidget(self._central_panel)
        main_window.setStatusBar(self._status_bar)

        builders.menu_bar_builder.build(main_window, self._menu_bar)
        builders.tool_bar_builder.build(main_window, self._tool_bar)
        builders.video_panel_builder.build(main_window, self._video_panel)
        builders.status_bar_builder.build(main_window, self._status_bar)

    @property
    def main_window(self):
        return self._main_window

    @property
    def menu_bar(self) -> QMenuBar:
        return self._menu_bar

    @property
    def central_panel(self) -> QWidget:
        return self._central_panel

    @property
    def tool_bar(self) -> QWidget:
        return self._tool_bar

    @property
    def video_panel(self) -> QWidget:
        return self._video_panel

    @property
    def status_bar(self) -> QStatusBar:
        return self._status_bar
