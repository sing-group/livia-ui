from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Tuple

from PySide2.QtCore import Signal, Slot, QCoreApplication
from PySide2.QtWidgets import QMenu, QAction, QFileDialog, QMessageBox

from livia.input.DeviceFrameInput import DeviceFrameInput
from livia.input.FileFrameInput import FileFrameInput
from livia.input.FrameInput import FrameInput
from livia.input.NoFrameInput import NoFrameInput
from livia.process.listener import build_listener
from livia.process.listener.ProcessChangeEvent import ProcessChangeEvent
from livia.process.listener.ProcessChangeListener import ProcessChangeListener
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.shortcuts.DefaultShortcutAction import DefaultShortcutAction
from livia_ui.gui.status.listener.DisplayStatusChangeEvent import DisplayStatusChangeEvent
from livia_ui.gui.status.listener.DisplayStatusChangeListener import DisplayStatusChangeListener
from livia_ui.gui.status.listener.ShortcutStatusChangeEvent import ShortcutStatusChangeEvent
from livia_ui.gui.status.listener.ShortcutStatusChangeListener import ShortcutStatusChangeListener
from livia_ui.gui.views.builders.GuiBuilderFactory import GuiBuilderFactory
from livia_ui.gui.views.builders.MenuBarBuilder import MenuBarBuilder
from livia_ui.gui.views.utils.AnalyzeImageDialog import AnalyzeImageDialog
from livia_ui.gui.views.utils.ConfigureShortcutsDialog import ConfigureShortcutsDialog
from livia_ui.gui.views.utils.DefaultDeviceProvider import DefaultDeviceProvider
from livia_ui.gui.views.utils.DeviceProvider import DeviceProvider
from livia_ui.gui.views.utils.SelectDeviceDialog import SelectDeviceDialog

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow


class DefaultMenuBarBuilder(MenuBarBuilder):
    _check_play_action_signal: Signal = Signal(bool)
    _check_fullscreen_action_signal: Signal = Signal(bool)
    _check_resizable_action_signal: Signal = Signal(bool)
    _check_detect_objects_action_signal: Signal = Signal(bool)
    _enable_analyze_image_action_signal: Signal = Signal(bool)

    @staticmethod
    def factory() -> GuiBuilderFactory[MenuBarBuilder]:
        class DefaultGuiBuilderFactory(GuiBuilderFactory[MenuBarBuilder]):
            def create_builder(self, *args, **kwargs) -> DefaultMenuBarBuilder:
                return DefaultMenuBarBuilder(*args, **kwargs)

        return DefaultGuiBuilderFactory()

    def __init__(self, livia_window: LiviaWindow, *args, **kwargs):
        super(DefaultMenuBarBuilder, self).__init__(livia_window, *args, **kwargs)
        self._current_path: str = str(Path.home())
        self._shortcuts_widgets: Dict[QAction, Tuple[str, ...]] = {}

        self._device_dialog: SelectDeviceDialog = None
        self._analyze_image_dialog: AnalyzeImageDialog = None
        self._configure_shortcuts_dialog: ConfigureShortcutsDialog = None

        self._open_file_action: QAction = None
        self._open_device_action: QAction = None
        self._quit_action: QAction = None
        self._pause_action: QAction = None
        self._resume_action: QAction = None
        self._toggle_video_analyzer_action: QAction = None
        self._analyze_image_action: QAction = None
        self._fullscreen_action: QAction = None
        self._resizable_action: QAction = None
        self._configure_shortcuts_action: QAction = None
        self._configure_video_analyzer_action: QAction = None
        self._configure_image_analyzer_action: QAction = None

        self._video_menu: QMenu = None
        self._analysis_menu: QMenu = None
        self._classification_menu: QMenu = None
        self._view_menu: QMenu = None
        self._configuration_menu: QMenu = None

    def _build_widgets(self):
        self._device_dialog = SelectDeviceDialog(self._device_provider(), self._livia_window)
        self._analyze_image_dialog = AnalyzeImageDialog(self._livia_status.video_stream_status, self._livia_window)
        self._configure_shortcuts_dialog = ConfigureShortcutsDialog(self._livia_status.shortcut_status)

        self._add_file_menu()
        self._add_video_menu()
        self._add_analysis_menu()
        self._add_view_menu()
        self._add_configuration_menu()

    def _connect_widgets(self):
        self._device_dialog.accepted.connect(self._on_accept_device)

        self._open_file_action.triggered.connect(self._on_open_file)
        self._open_device_action.triggered.connect(self._on_open_device)
        self._release_device_action.triggered.connect(self._on_release_device)
        self._quit_action.triggered.connect(self._on_quit)
        self._resizable_action.triggered.connect(self._on_toggle_resizable)
        self._fullscreen_action.triggered.connect(self._on_toggle_fullscreen)
        self._toggle_video_analyzer_action.triggered.connect(self._on_toggle_detect_objects)
        self._play_action.triggered.connect(self._on_toggle_play)
        self._analyze_image_action.triggered.connect(self._on_analyze_image)
        self._configure_shortcuts_action.triggered.connect(self._on_configure_shortcuts)

    def _connect_signals(self):
        self._check_play_action_signal.connect(self._on_check_play_action_signal)
        self._check_fullscreen_action_signal.connect(self._on_check_play_action_signal)
        self._check_resizable_action_signal.connect(self._on_check_fullscreen_action_signal)
        self._check_detect_objects_action_signal.connect(self._on_check_detect_objects_action_signal)
        self._enable_analyze_image_action_signal.connect(self._on_enable_analyze_image_action_signal)

    def _listen_livia(self):
        self._livia_status.display_status.add_display_status_change_listener(
            build_listener(DisplayStatusChangeListener,
                           fullscreen_changed=self._on_fullscreen_changed,
                           resizable_changed=self._on_resizable_changed,
                           detect_objects_changed=self._on_detect_objects_changed
                           )
        )
        self._livia_status.video_stream_status.frame_processor.add_process_change_listener(
            build_listener(ProcessChangeListener,
                           started=self._on_video_started,
                           stopped=self._on_video_stopped,
                           finished=self._on_video_finished,
                           paused=self._on_video_paused,
                           resumed=self._on_video_resumed
                           )
        )
        self._livia_status.shortcut_status.add_shortcut_configuration_change_listener(
            build_listener(ShortcutStatusChangeListener,
                           shortcut_modified=self._on_modified_shortcut,
                           shortcut_removed=self._on_removed_shortcut
                           )
        )

    def _disconnect_signals(self):
        self._check_play_action_signal.disconnect(self._on_check_play_action_signal)
        self._check_fullscreen_action_signal.disconnect(self._on_check_play_action_signal)
        self._check_resizable_action_signal.disconnect(self._on_check_fullscreen_action_signal)
        self._check_detect_objects_action_signal.disconnect(self._on_check_detect_objects_action_signal)
        self._enable_analyze_image_action_signal.disconnect(self._on_enable_analyze_image_action_signal)

    def _on_modified_shortcut(self, event: ShortcutStatusChangeEvent):
        for widget in self._shortcuts_widgets:
            if widget.shortcut().toString() == event.old_keys[0]:
                widget.setShortcuts(event.new_keys)
                self._shortcuts_widgets[widget] = event.new_keys
                break

    def _on_removed_shortcut(self, event: ShortcutStatusChangeEvent):
        for widget in self._shortcuts_widgets:
            if widget.shortcut().toString() == event.old_keys[0]:
                widget.setShortcuts(event.new_keys)
                widget.setEnabled(False)
                self._shortcuts_widgets[widget] = event.new_keys
                LIVIA_GUI_LOGGER.warning("Menu Action '" + widget.objectName() +
                                         "' disabled caused by 'removed_shortcut' event.")
                break

    def _add_file_menu(self):
        self._open_file_action = QAction(self._livia_window)
        self._open_file_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.OPEN_FILE))
        self._shortcuts_widgets[self._open_file_action] = self._get_shortcuts(DefaultShortcutAction.OPEN_FILE)
        self._open_file_action.setObjectName("_menu_bar__open_file_action")
        self._open_file_action.setText(self._translate("Open file"))

        self._open_device_action = QAction(self._livia_window)
        self._open_device_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.OPEN_DEVICE))
        self._shortcuts_widgets[self._open_device_action] = self._get_shortcuts(DefaultShortcutAction.OPEN_DEVICE)
        self._open_device_action.setObjectName("_menu_bar__open_device_action")
        self._open_device_action.setText(self._translate("Open device"))

        self._release_device_action = QAction(self._livia_window)
        self._release_device_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.RELEASE_DEVICE))
        self._shortcuts_widgets[self._release_device_action] = self._get_shortcuts(DefaultShortcutAction.RELEASE_DEVICE)
        self._release_device_action.setObjectName("_menu_bar__release_device_action")
        self._release_device_action.setText(self._translate("Release device"))

        self._quit_action = QAction(self._livia_window)
        self._quit_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.QUIT))
        self._shortcuts_widgets[self._quit_action] = self._get_shortcuts(DefaultShortcutAction.QUIT)
        self._quit_action.setObjectName("_menu_bar__quit_action")
        self._quit_action.setText(self._translate("Quit"))

        self._file_menu = QMenu(self._parent_widget)
        self._file_menu.setObjectName("_menu_bar__file_menu")
        self._file_menu.setTitle(self._translate("File"))
        self._file_menu.addAction(self._open_file_action)
        self._file_menu.addAction(self._open_device_action)
        self._file_menu.addAction(self._release_device_action)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._quit_action)

        self._parent_widget.addAction(self._file_menu.menuAction())

    def _add_video_menu(self):
        self._play_action = QAction(self._livia_window)
        self._play_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.TOGGLE_PLAY))
        self._shortcuts_widgets[self._play_action] = self._get_shortcuts(DefaultShortcutAction.TOGGLE_PLAY)
        self._play_action.setCheckable(True)
        self._play_action.setChecked(self._livia_status.video_stream_status.frame_processor.is_running())
        self._play_action.setObjectName("_menu_bar__play")
        self._play_action.setText(self._translate("Play"))

        self._video_menu = QMenu(self._parent_widget)
        self._video_menu.setObjectName("_menu_bar__video_menu")
        self._video_menu.setTitle(self._translate("Video"))
        self._video_menu.addAction(self._play_action)

        self._parent_widget.addAction(self._video_menu.menuAction())

    def _add_analysis_menu(self):
        self._toggle_video_analyzer_action = QAction(self._livia_window)
        self._toggle_video_analyzer_action.setShortcuts(
            self._get_shortcuts(DefaultShortcutAction.TOGGLE_VIDEO_ANALYSIS))
        self._shortcuts_widgets[self._toggle_video_analyzer_action] = self._get_shortcuts(
            DefaultShortcutAction.TOGGLE_VIDEO_ANALYSIS)
        self._toggle_video_analyzer_action.setCheckable(True)
        self._toggle_video_analyzer_action.setChecked(self._livia_status.display_status.detect_objects)
        self._toggle_video_analyzer_action.setObjectName("_menu_bar__toggle_video_analyzer_action")
        self._toggle_video_analyzer_action.setText(self._translate("Analyze video"))

        self._analyze_image_action = QAction(self._livia_window)
        self._analyze_image_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.ANALYZE_IMAGE))
        self._shortcuts_widgets[self._analyze_image_action] = self._get_shortcuts(DefaultShortcutAction.ANALYZE_IMAGE)
        self._analyze_image_action.setObjectName("_menu_bar__analyze_image_action")
        self._analyze_image_action.setText(self._translate("Analyze image"))

        self._analysis_menu = QMenu(self._parent_widget)
        self._analysis_menu.setObjectName("_menu_bar__analysis_menu")
        self._analysis_menu.setTitle(self._translate("Analysis"))
        self._analysis_menu.addAction(self._toggle_video_analyzer_action)
        self._analysis_menu.addAction(self._analyze_image_action)

        self._parent_widget.addAction(self._analysis_menu.menuAction())

    def _add_view_menu(self):
        self._fullscreen_action = QAction(self._livia_window)
        self._fullscreen_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.TOGGLE_FULLSCREEN))
        self._shortcuts_widgets[self._fullscreen_action] = self._get_shortcuts(DefaultShortcutAction.TOGGLE_FULLSCREEN)
        self._fullscreen_action.setCheckable(True)
        self._fullscreen_action.setChecked(self._livia_status.display_status.fullscreen)
        self._fullscreen_action.setObjectName("_menu_bar__fullscreen_action")
        self._fullscreen_action.setText(self._translate("Fullscreen"))
        self._resizable_action = QAction(self._livia_window)
        self._resizable_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.TOGGLE_RESIZABLE))
        self._shortcuts_widgets[self._resizable_action] = self._get_shortcuts(DefaultShortcutAction.TOGGLE_RESIZABLE)
        self._resizable_action.setCheckable(True)
        self._resizable_action.setChecked(self._livia_status.display_status.resizable)
        self._resizable_action.setObjectName("_menu_bar__resizable_action")
        self._resizable_action.setText(self._translate("Resizable"))

        self._view_menu = QMenu(self._parent_widget)
        self._view_menu.setObjectName("_menu_bar__view_menu")
        self._view_menu.setTitle(self._translate("View"))
        self._view_menu.addAction(self._fullscreen_action)
        self._view_menu.addAction(self._resizable_action)

        self._parent_widget.addAction(self._view_menu.menuAction())

    def _add_configuration_menu(self):
        self._configure_shortcuts_action = QAction(self._livia_window)
        self._configure_shortcuts_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.CONFIGURE_SHORTCUTS))
        self._shortcuts_widgets[self._configure_shortcuts_action] = self._get_shortcuts(
            DefaultShortcutAction.CONFIGURE_SHORTCUTS)
        self._configure_shortcuts_action.setObjectName("_menu_bar__configure_shortcuts_action")
        self._configure_shortcuts_action.setText(self._translate("Shortcuts"))
        self._configure_video_analyzer_action = QAction(self._livia_window)
        self._configure_video_analyzer_action.setShortcuts(
            self._get_shortcuts(DefaultShortcutAction.CONFIGURE_VIDEO_ANALYZER))
        self._shortcuts_widgets[self._configure_video_analyzer_action] = self._get_shortcuts(
            DefaultShortcutAction.CONFIGURE_VIDEO_ANALYZER)
        self._configure_video_analyzer_action.setObjectName("_menu_bar__configure_video_analyzer_action")
        self._configure_video_analyzer_action.setText(self._translate("Video analyzer"))
        self._configure_image_analyzer_action = QAction(self._livia_window)
        self._configure_image_analyzer_action.setShortcuts(
            self._get_shortcuts(DefaultShortcutAction.CONFIGURE_IMAGE_ANALYZER))
        self._shortcuts_widgets[self._configure_image_analyzer_action] = self._get_shortcuts(
            DefaultShortcutAction.CONFIGURE_IMAGE_ANALYZER)
        self._configure_image_analyzer_action.setObjectName("_menu_bar__configure_image_analyzer_action")
        self._configure_image_analyzer_action.setText(self._translate("Image analyzer"))

        self._configuration_menu = QMenu(self._parent_widget)
        self._configuration_menu.setObjectName("_menu_bar__configuration_menu")
        self._configuration_menu.setTitle(self._translate("Configuration"))
        self._configuration_menu.addAction(self._configure_video_analyzer_action)
        self._configuration_menu.addAction(self._configure_image_analyzer_action)
        self._configuration_menu.addAction(self._configure_shortcuts_action)

        self._parent_widget.addAction(self._configuration_menu.menuAction())

    def _device_provider(self) -> DeviceProvider:
        return DefaultDeviceProvider()

    @Slot(bool)
    def _on_check_play_action_signal(self, checked: bool):
        self._play_action.setChecked(checked)

    @Slot(bool)
    def _on_check_fullscreen_action_signal(self, checked: bool):
        self._fullscreen_action.setChecked(checked)
        if checked:
            self._livia_window.showFullScreen()
        else:
            self._livia_window.showNormal()

    @Slot(bool)
    def _on_check_resizable_action_signal(self, checked: bool):
        self._resizable_action.setChecked(checked)

    @Slot(bool)
    def _on_check_detect_objects_action_signal(self, checked: bool):
        self._toggle_video_analyzer_action.setChecked(checked)

    @Slot(bool)
    def _on_enable_analyze_image_action_signal(self, enabled: bool):
        self._analyze_image_action.setEnabled(enabled)

    def _on_analyze_image(self):
        self._analyze_image_dialog.open()

    def _on_open_file(self):
        file_filter = self._translate("Video Files (*.mp4 *.avi)")
        file = QFileDialog.getOpenFileName(self._livia_window,
                                           self._translate("Open file"),
                                           self._current_path,
                                           file_filter,
                                           file_filter)

        if file[0]:
            self._current_path = os.path.dirname(os.path.realpath(file[0]))
            self.__change_frame_input(FileFrameInput(file[0]))

    def _on_open_device(self):
        self._device_dialog.open()

    def _on_release_device(self):
        self._livia_status.video_stream_status.frame_processor.stop()
        self._livia_status.video_stream_status.frame_input = NoFrameInput()

    def _on_quit(self):
        message = QMessageBox(self._livia_window)
        message.setIcon(QMessageBox.Warning)

        message.setWindowTitle("Exit Livia")
        message.setText("Livia is about to exit. Do you want to continue?")
        message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        if message.exec_() == QMessageBox.Ok:
            QCoreApplication.quit()

    def _on_accept_device(self):
        self.__change_frame_input(DeviceFrameInput(self._device_dialog.get_device()))

    def _on_toggle_resizable(self):
        self._livia_status.display_status.toggle_resizable()

    def _on_toggle_fullscreen(self):
        self._livia_status.display_status.toggle_fullscreen()

    def _on_toggle_detect_objects(self):
        self._livia_status.display_status.toggle_detect_objects()

    def _on_toggle_play(self):
        if self._livia_status.video_stream_status.frame_processor.is_alive():
            if self._livia_status.video_stream_status.frame_processor.is_paused():
                self._livia_status.video_stream_status.frame_processor.resume()
            else:
                self._livia_status.video_stream_status.frame_processor.pause()

    def _on_fullscreen_changed(self, event: DisplayStatusChangeEvent):
        if self._fullscreen_action.isChecked() != event.value:
            self._check_fullscreen_action_signal.emit(event.value)

    def _on_resizable_changed(self, event: DisplayStatusChangeEvent):
        if self._resizable_action.isChecked() != event.value:
            self._check_resizable_action_signal.emit(event.value)

    def _on_detect_objects_changed(self, event: DisplayStatusChangeEvent):
        if self._toggle_video_analyzer_action.isChecked() != event.value:
            self._check_detect_objects_action_signal.emit(event.value)

    def _on_video_started(self, event: ProcessChangeEvent):
        if not self._play_action.isChecked():
            self._check_play_action_signal.emit(True)
        if not self._analyze_image_action.isEnabled():
            self._enable_analyze_image_action_signal.emit(True)

    def _on_video_stopped(self, event: ProcessChangeEvent):
        if self._play_action.isChecked():
            self._check_play_action_signal.emit(False)
        if self._analyze_image_action.isEnabled():
            self._enable_analyze_image_action_signal.emit(False)

    def _on_video_finished(self, event: ProcessChangeEvent):
        if self._play_action.isChecked():
            self._check_play_action_signal.emit(False)
        if self._analyze_image_action.isEnabled():
            self._enable_analyze_image_action_signal.emit(False)

    def _on_video_paused(self, event: ProcessChangeEvent):
        if self._play_action.isChecked():
            self._check_play_action_signal.emit(False)

    def _on_video_resumed(self, event: ProcessChangeEvent):
        if not self._play_action.isChecked():
            self._check_play_action_signal.emit(True)

    def _on_configure_shortcuts(self):
        self._configure_shortcuts_dialog.open()

    def __change_frame_input(self, frame_input: FrameInput):
        status = self._livia_status.video_stream_status

        if status.frame_processor.is_alive():
            status.frame_processor.stop_and_wait()

        old_frame_input = status.frame_input
        status.frame_input = frame_input
        old_frame_input.close()

        status.frame_processor.start()
