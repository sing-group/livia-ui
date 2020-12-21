from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMenuBar, QMenu, QAction

from livia.process.analyzer.FrameByFrameSquareFrameAnalyzer import FrameByFrameSquareFrameAnalyzer
from livia.process.analyzer.NoChangeFrameAnalyzer import NoChangeFrameAnalyzer
from livia.process.listener import build_listener
from livia_ui.gui.status.listener.DisplayStatusChangeEvent import DisplayStatusChangeEvent
from livia_ui.gui.status.listener.DisplayStatusChangeListener import DisplayStatusChangeListener
from livia_ui.gui.views.builders.MenuBarBuilder import MenuBarBuilder

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow


class DefaultMenuBarBuilder(MenuBarBuilder):
    def __init__(self):
        self._translate = QtCore.QCoreApplication.translate
        self._main_window: LiviaWindow = None

        self._pause_action: QAction = None
        self._resume_action: QAction = None
        self._detect_objects_action: QAction = None
        self._classify_action: QAction = None
        self._fullscreen_action: QAction = None
        self._resizable_action: QAction = None
        self._shortcuts_action: QAction = None
        self._analyzer_action: QAction = None
        self._display_action: QAction = None

        self._video_menu: QMenu = None
        self._detection_menu: QMenu = None
        self._classification_menu: QMenu = None
        self._view_menu: QMenu = None
        self._configuration_menu: QMenu = None

    def build(self, main_window: LiviaWindow, menu_bar: QMenuBar):
        self._main_window = main_window

        self._add_video_menu(menu_bar, menu_bar)
        self._add_detection_menu(main_window, menu_bar)
        self._add_classification_menu(main_window, menu_bar)
        self._add_view_menu(main_window, menu_bar)
        self._add_configuration_menu(main_window, menu_bar)

        self._resizable_action.triggered.connect(self._on_toggle_resizable)
        self._fullscreen_action.triggered.connect(self._on_toggle_fullscreen)
        self._detect_objects_action.triggered.connect(self._on_toggle_detect_objects)
        self._pause_action.triggered.connect(self._on_pause)
        self._resume_action.triggered.connect(self._on_resume)

        main_window.status.display_status.add_display_status_change_listener(
            build_listener(DisplayStatusChangeListener,
                           fullscreen_changed=self._on_fullscreen_changed,
                           resizable_changed=self._on_resizable_changed,
                           detect_objects_changed=self._on_detect_objects_changed)
        )

    def _add_video_menu(self, parent, menu_bar):
        self._pause_action = QAction(parent)
        self._pause_action.setObjectName("_menu_bar__pause_action")
        self._pause_action.setText(self._translate("DefaultMenuBarBuilder", "Pause"))
        self._resume_action = QAction(parent)
        self._resume_action.setObjectName("_menu_bar__resume_action")
        self._resume_action.setText(self._translate("DefaultMenuBarBuilder", "Resume"))

        self._video_menu = QMenu(menu_bar)
        self._video_menu.setObjectName("_menu_bar__video_menu")
        self._video_menu.setTitle(self._translate("DefaultMenuBarBuilder", "Video"))
        self._video_menu.addAction(self._pause_action)
        self._video_menu.addAction(self._resume_action)

        menu_bar.addAction(self._video_menu.menuAction())

    def _add_detection_menu(self, parent, menu_bar):
        self._detect_objects_action = QAction(parent)
        self._detect_objects_action.setCheckable(True)
        self._detect_objects_action.setChecked(self._main_window.status.display_status.detect_objects)
        self._detect_objects_action.setObjectName("_menu_bar__start_detection_action")
        self._detect_objects_action.setText(self._translate("DefaultMenuBarBuilder", "Detect objects"))

        self._detection_menu = QMenu(menu_bar)
        self._detection_menu.setObjectName("_menu_bar__detection_menu")
        self._detection_menu.setTitle(self._translate("DefaultMenuBarBuilder", "Detection"))
        self._detection_menu.addAction(self._detect_objects_action)

        menu_bar.addAction(self._detection_menu.menuAction())

    def _add_classification_menu(self, parent, menu_bar):
        self._classify_action = QAction(parent)
        self._classify_action.setObjectName("_menu_bar__classify_action")
        self._classify_action.setText(self._translate("DefaultMenuBarBuilder", "Classify"))

        self._classification_menu = QMenu(menu_bar)
        self._classification_menu.setObjectName("_menu_bar__classification_menu")
        self._classification_menu.setTitle(self._translate("DefaultMenuBarBuilder", "Classification"))
        self._classification_menu.addAction(self._classify_action)

        menu_bar.addAction(self._classification_menu.menuAction())

    def _add_view_menu(self, parent, menu_bar):
        self._fullscreen_action = QAction(parent)
        self._fullscreen_action.setCheckable(True)
        self._fullscreen_action.setChecked(self._main_window.status.display_status.fullscreen)
        self._fullscreen_action.setObjectName("_menu_bar__fullscreen_action")
        self._fullscreen_action.setText(self._translate("DefaultMenuBarBuilder", "Fullscreen"))
        self._resizable_action = QAction(parent)
        self._resizable_action.setCheckable(True)
        print(self._main_window.status.display_status.resizable)
        self._resizable_action.setChecked(self._main_window.status.display_status.resizable)
        self._resizable_action.setObjectName("_menu_bar__resizable_action")
        self._resizable_action.setText(self._translate("DefaultMenuBarBuilder", "Resizable"))

        self._view_menu = QMenu(menu_bar)
        self._view_menu.setObjectName("_menu_bar__view_menu")
        self._view_menu.setTitle(self._translate("DefaultMenuBarBuilder", "View"))
        self._view_menu.addAction(self._fullscreen_action)
        self._view_menu.addAction(self._resizable_action)

        menu_bar.addAction(self._view_menu.menuAction())

    def _add_configuration_menu(self, parent, menu_bar):
        self._shortcuts_action = QAction(parent)
        self._shortcuts_action.setObjectName("_menu_bar__shortcuts_action")
        self._shortcuts_action.setText(self._translate("DefaultMenuBarBuilder", "Shortcuts"))
        self._analyzer_action = QAction(parent)
        self._analyzer_action.setObjectName("_menu_bar__analyzer_action")
        self._analyzer_action.setText(self._translate("DefaultMenuBarBuilder", "Analyzer"))
        self._display_action = QAction(parent)
        self._display_action.setObjectName("_menu_bar__display_action")
        self._display_action.setText(self._translate("DefaultMenuBarBuilder", "Display"))

        self._configuration_menu = QMenu(menu_bar)
        self._configuration_menu.setObjectName("_menu_bar__configuration_menu")
        self._configuration_menu.setTitle(self._translate("DefaultMenuBarBuilder", "Configuration"))
        self._configuration_menu.addAction(self._analyzer_action)
        self._configuration_menu.addAction(self._shortcuts_action)
        self._configuration_menu.addAction(self._display_action)

        menu_bar.addAction(self._configuration_menu.menuAction())

    def _on_toggle_resizable(self):
        self._main_window.status.display_status.toggle_resizable()

    def _on_toggle_fullscreen(self):
        self._main_window.status.display_status.toggle_fullscreen()

    def _on_toggle_detect_objects(self):
        self._main_window.status.display_status.toggle_detect_objects()

    def _on_pause(self):
        self._main_window.status.video_stream_status.frame_processor.pause()

    def _on_resume(self):
        self._main_window.status.video_stream_status.frame_processor.resume()

    def _on_fullscreen_changed(self, event: DisplayStatusChangeEvent):
        if self._fullscreen_action.isChecked() != event.value:
            self._fullscreen_action.setChecked(event.value)

    def _on_resizable_changed(self, event: DisplayStatusChangeEvent):
        if self._resizable_action.isChecked() != event.value:
            self._resizable_action.setChecked(event.value)

    def _on_detect_objects_changed(self, event: DisplayStatusChangeEvent):
        if self._detect_objects_action.isChecked() != event.value:
            self._detect_objects_action.setChecked(event.value)