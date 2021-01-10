import os
from pathlib import Path

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog

from livia.input.DeviceFrameInput import DeviceFrameInput
from livia.input.FileFrameInput import FileFrameInput
from livia.input.FrameInput import FrameInput
from livia.process.listener import build_listener
from livia.process.listener.ProcessChangeEvent import ProcessChangeEvent
from livia.process.listener.ProcessChangeListener import ProcessChangeListener
from livia_ui.gui.shortcuts.DefaultShortcutAction import DefaultShortcutAction
from livia_ui.gui.status.listener.DisplayStatusChangeEvent import DisplayStatusChangeEvent
from livia_ui.gui.status.listener.DisplayStatusChangeListener import DisplayStatusChangeListener
from livia_ui.gui.views.builders.MenuBarBuilder import MenuBarBuilder
from livia_ui.gui.views.utils.SelectDeviceDialog import SelectDeviceDialog


class DefaultMenuBarBuilder(MenuBarBuilder):
    _check_play_action_signal: pyqtSignal = pyqtSignal(bool)
    _check_fullscreen_action_signal: pyqtSignal = pyqtSignal(bool)
    _check_resizable_action_signal: pyqtSignal = pyqtSignal(bool)
    _check_detect_objects_action_signal: pyqtSignal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._current_path: str = str(Path.home())

        self._camera_dialog: SelectDeviceDialog = None

        self._open_file_action: QAction = None
        self._open_device_action: QAction = None
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
        self._camera_dialog = SelectDeviceDialog(self._livia_window)

        self._add_file_menu()
        self._add_video_menu()
        self._add_analysis_menu()
        self._add_view_menu()
        self._add_configuration_menu()

    def _connect_widgets(self):
        self._camera_dialog.accepted.connect(self._on_accept_camera)

        self._open_file_action.triggered.connect(self._on_open_file)
        self._open_device_action.triggered.connect(self._on_open_camera)
        self._resizable_action.triggered.connect(self._on_toggle_resizable)
        self._fullscreen_action.triggered.connect(self._on_toggle_fullscreen)
        self._toggle_video_analyzer_action.triggered.connect(self._on_toggle_detect_objects)
        self._play_action.triggered.connect(self._on_toggle_play)

    def _connect_signals(self):
        self._check_play_action_signal.connect(self._on_check_play_action_signal)
        self._check_fullscreen_action_signal.connect(self._on_check_fullscreen_action_signal)
        self._check_resizable_action_signal.connect(self._on_check_resizable_action_signal)
        self._check_detect_objects_action_signal.connect(self._on_check_detect_objects_action_signal)

    def _listen_livia(self):
        self._livia_window.status.display_status.add_display_status_change_listener(
            build_listener(DisplayStatusChangeListener,
                           fullscreen_changed=self._on_fullscreen_changed,
                           resizable_changed=self._on_resizable_changed,
                           detect_objects_changed=self._on_detect_objects_changed
                           )
        )
        self._livia_window.status.video_stream_status.frame_processor.add_process_change_listener(
            build_listener(ProcessChangeListener,
                           started=self._on_video_started,
                           stopped=self._on_video_stopped,
                           finished=self._on_video_finished,
                           paused=self._on_video_paused,
                           resumed=self._on_video_resumed
                           )
        )

    def _disconnect_signals(self):
        self._check_play_action_signal.disconnect(self._on_check_play_action_signal)
        self._check_fullscreen_action_signal.disconnect(self._on_check_fullscreen_action_signal)
        self._check_resizable_action_signal.disconnect(self._on_check_resizable_action_signal)
        self._check_detect_objects_action_signal.disconnect(self._on_check_detect_objects_action_signal)

    def _add_file_menu(self):
        self._open_file_action = QAction(self._livia_window)
        self._open_file_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.OPEN_FILE))
        self._open_file_action.setObjectName("_menu_bar__open_action")
        self._open_file_action.setText(self._translate("Open file"))

        self._open_device_action = QAction(self._livia_window)
        self._open_device_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.OPEN_DEVICE))
        self._open_device_action.setObjectName("_menu_bar__open_device")
        self._open_device_action.setText(self._translate("Open device"))

        self._file_menu = QMenu(self._parent)
        self._file_menu.setObjectName("_menu_bar__file_menu")
        self._file_menu.setTitle(self._translate("File"))
        self._file_menu.addAction(self._open_file_action)
        self._file_menu.addAction(self._open_device_action)

        self._parent.addAction(self._file_menu.menuAction())

    def _add_video_menu(self):
        self._play_action = QAction(self._livia_window)
        self._play_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.TOGGLE_PLAY))
        self._play_action.setCheckable(True)
        self._play_action.setChecked(self._livia_window.status.video_stream_status.frame_processor.is_running())
        self._play_action.setObjectName("_menu_bar__play")
        self._play_action.setText(self._translate("Play"))

        self._video_menu = QMenu(self._parent)
        self._video_menu.setObjectName("_menu_bar__video_menu")
        self._video_menu.setTitle(self._translate("Video"))
        self._video_menu.addAction(self._play_action)

        self._parent.addAction(self._video_menu.menuAction())

    def _add_analysis_menu(self):
        self._toggle_video_analyzer_action = QAction(self._livia_window)
        self._toggle_video_analyzer_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.TOGGLE_VIDEO_ANALYSIS))
        self._toggle_video_analyzer_action.setCheckable(True)
        self._toggle_video_analyzer_action.setChecked(self._livia_window.status.display_status.detect_objects)
        self._toggle_video_analyzer_action.setObjectName("_menu_bar__toggle_video_analyzer_action")
        self._toggle_video_analyzer_action.setText(self._translate("Analyze video"))

        self._analyze_image_action = QAction(self._livia_window)
        self._analyze_image_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.ANALYZE_IMAGE))
        self._analyze_image_action.setObjectName("_menu_bar__analyze_image_action")
        self._analyze_image_action.setText(self._translate("Analyze image"))

        self._analysis_menu = QMenu(self._parent)
        self._analysis_menu.setObjectName("_menu_bar__analysis_menu")
        self._analysis_menu.setTitle(self._translate("Analysis"))
        self._analysis_menu.addAction(self._toggle_video_analyzer_action)
        self._analysis_menu.addAction(self._analyze_image_action)

        self._parent.addAction(self._analysis_menu.menuAction())

    def _add_view_menu(self):
        self._fullscreen_action = QAction(self._livia_window)
        self._fullscreen_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.TOGGLE_FULLSCREEN))
        self._fullscreen_action.setCheckable(True)
        self._fullscreen_action.setChecked(self._livia_window.status.display_status.fullscreen)
        self._fullscreen_action.setObjectName("_menu_bar__fullscreen_action")
        self._fullscreen_action.setText(self._translate("Fullscreen"))
        self._resizable_action = QAction(self._livia_window)
        self._resizable_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.TOGGLE_RESIZABLE))
        self._resizable_action.setCheckable(True)
        self._resizable_action.setChecked(self._livia_window.status.display_status.resizable)
        self._resizable_action.setObjectName("_menu_bar__resizable_action")
        self._resizable_action.setText(self._translate("Resizable"))

        self._view_menu = QMenu(self._parent)
        self._view_menu.setObjectName("_menu_bar__view_menu")
        self._view_menu.setTitle(self._translate("View"))
        self._view_menu.addAction(self._fullscreen_action)
        self._view_menu.addAction(self._resizable_action)

        self._parent.addAction(self._view_menu.menuAction())

    def _add_configuration_menu(self):
        self._configure_shortcuts_action = QAction(self._livia_window)
        self._configure_shortcuts_action.setShortcuts(self._get_shortcuts(DefaultShortcutAction.CONFIGURE_SHORTCUTS))
        self._configure_shortcuts_action.setObjectName("_menu_bar__configure_shortcuts_action")
        self._configure_shortcuts_action.setText(self._translate("Shortcuts"))
        self._configure_video_analyzer_action = QAction(self._livia_window)
        self._configure_video_analyzer_action.setShortcuts(
            self._get_shortcuts(DefaultShortcutAction.CONFIGURE_VIDEO_ANALYZER))
        self._configure_video_analyzer_action.setObjectName("_menu_bar__configure_video_analyzer_action")
        self._configure_video_analyzer_action.setText(self._translate("Video analyzer"))
        self._configure_image_analyzer_action = QAction(self._livia_window)
        self._configure_image_analyzer_action.setShortcuts(
            self._get_shortcuts(DefaultShortcutAction.CONFIGURE_IMAGE_ANALYZER))
        self._configure_image_analyzer_action.setObjectName("_menu_bar__configure_image_analyzer_action")
        self._configure_image_analyzer_action.setText(self._translate("Image analyzer"))

        self._configuration_menu = QMenu(self._parent)
        self._configuration_menu.setObjectName("_menu_bar__configuration_menu")
        self._configuration_menu.setTitle(self._translate("Configuration"))
        self._configuration_menu.addAction(self._configure_video_analyzer_action)
        self._configuration_menu.addAction(self._configure_image_analyzer_action)
        self._configuration_menu.addAction(self._configure_shortcuts_action)

        self._parent.addAction(self._configuration_menu.menuAction())

    @pyqtSlot(bool)
    def _on_check_play_action_signal(self, checked: bool):
        self._play_action.setChecked(checked)

    @pyqtSlot(bool)
    def _on_check_fullscreen_action_signal(self, checked: bool):
        self._fullscreen_action.setChecked(checked)
        if checked:
            print("Fullscreen")
            self._livia_window.showFullScreen()
        else:
            print("Normal")
            self._livia_window.showNormal()

    @pyqtSlot(bool)
    def _on_check_resizable_action_signal(self, checked: bool):
        self._resizable_action.setChecked(checked)

    @pyqtSlot(bool)
    def _on_check_detect_objects_action_signal(self, checked: bool):
        self._toggle_video_analyzer_action.setChecked(checked)

    def _on_open_file(self):
        file = QFileDialog.getOpenFileName(self._livia_window,
                                           self._translate("Open file"),
                                           self._current_path,
                                           self._translate("Video Files (*.mp4)"))

        if file[0]:
            self._current_path = os.path.dirname(os.path.realpath(file[0]))
            self.__change_frame_input(FileFrameInput(file[0]))

    def _on_open_camera(self):
        self._camera_dialog.open()

    def _on_accept_camera(self):
        self.__change_frame_input(DeviceFrameInput(self._camera_dialog.get_device()))

    def _on_toggle_resizable(self):
        self._livia_window.status.display_status.toggle_resizable()

    def _on_toggle_fullscreen(self):
        self._livia_window.status.display_status.toggle_fullscreen()

    def _on_toggle_detect_objects(self):
        self._livia_window.status.display_status.toggle_detect_objects()

    def _on_toggle_play(self):
        if self._livia_window.status.video_stream_status.frame_processor.is_alive():
            if self._livia_window.status.video_stream_status.frame_processor.is_paused():
                self._livia_window.status.video_stream_status.frame_processor.resume()
            else:
                self._livia_window.status.video_stream_status.frame_processor.pause()

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

    def _on_video_stopped(self, event: ProcessChangeEvent):
        if self._play_action.isChecked():
            self._check_play_action_signal.emit(False)

    def _on_video_finished(self, event: ProcessChangeEvent):
        if self._play_action.isChecked():
            self._check_play_action_signal.emit(False)

    def _on_video_paused(self, event: ProcessChangeEvent):
        if self._play_action.isChecked():
            self._check_play_action_signal.emit(False)

    def _on_video_resumed(self, event: ProcessChangeEvent):
        if not self._play_action.isChecked():
            self._check_play_action_signal.emit(True)

    def __change_frame_input(self, frame_input: FrameInput):
        status = self._livia_window.status.video_stream_status

        if status.frame_processor.is_alive():
            status.frame_processor.stop_and_wait()

        status.frame_input = frame_input

        status.frame_processor.start()
