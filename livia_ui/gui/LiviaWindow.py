from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QMainWindow

from livia.process.listener import build_listener
from livia_ui.gui.shortcuts.ShortcutEventManager import ShortcutEventManager
from livia_ui.gui.status.LiviaStatus import LiviaStatus
from livia_ui.gui.status.listener.ShortcutStatusChangeEvent import ShortcutStatusChangeEvent
from livia_ui.gui.status.listener.ShortcutStatusChangeListener import ShortcutStatusChangeListener
from livia_ui.gui.views.UiLiviaWindow import UiLiviaWindow
from livia_ui.gui.views.builders.GuiBuilders import GuiBuilders


class LiviaWindow(QMainWindow, UiLiviaWindow):
    exit_code_signal = pyqtSignal(int)

    def __init__(self, livia_status: LiviaStatus, gui_builders: GuiBuilders = GuiBuilders()):
        self.EXIT_CODE_REBOOT = -1

        super(LiviaWindow, self).__init__()

        self._livia_status = livia_status
        self._shortcuts_manager = ShortcutEventManager(self)

        for action, keys in self._livia_status.shortcut_status.shortcuts.items():
            self._shortcuts_manager.add_shortcut(action, set(keys))

        self._livia_status.shortcut_status.add_shortcut_configuration_change_listener(
            build_listener(ShortcutStatusChangeListener,
                           shortcut_added=self._on_shortcut_added,
                           shortcut_modified=self._on_shortcut_modified,
                           shortcut_removed=self._on_shortcut_removed)
        )

        self.setup_ui(self, gui_builders)

        size = livia_status.display_status.window_size
        self.resize(*size)
        self.setMinimumSize(*size)

        self._start_movie()

    def resizeEvent(self, event: QResizeEvent):
        new_size = event.size()
        if new_size != event.oldSize():
            self._livia_status.display_status.window_size = (new_size.width(), new_size.height())

    @property
    def status(self) -> LiviaStatus:
        return self._livia_status

    @property
    def fullscreen(self) -> bool:
        return self._livia_status.display_status.fullscreen

    @fullscreen.setter
    def fullscreen(self, fullscreen: bool) -> None:
        self._livia_status.display_status.fullscreen = fullscreen

    @property
    def resizable(self) -> bool:
        return self._livia_status.display_status.resizable

    @resizable.setter
    def resizable(self, resizable: bool) -> None:
        self._livia_status.display_status.resizable = resizable

    @property
    def status_message(self) -> str:
        return self._livia_status.display_status.status_message

    @status_message.setter
    def status_message(self, message: str) -> None:
        self._livia_status.display_status.status_message = message

    @property
    def shortcuts_manager(self) -> ShortcutEventManager:
        return self._shortcuts_manager

    def _on_shortcut_added(self, event: ShortcutStatusChangeEvent):
        self._shortcuts_manager.add_shortcut(event.action, set(event.new_keys))

    def _on_shortcut_modified(self, event: ShortcutStatusChangeEvent):
        self._shortcuts_manager.set_shortcut(event.action, set(event.new_keys))

    def _on_shortcut_removed(self, event: ShortcutStatusChangeEvent):
        self._shortcuts_manager.remove_shortcut(event.action)

    def _restart(self) -> None:
        self.exit_code_signal.emit(-1)
        self.close_app()

    def _start_movie(self) -> None:
        if not self.status.video_stream_status.frame_processor.is_running():
            self._livia_status.video_stream_status.frame_processor.start()

    def close_app(self) -> None:
        self.deleteLater()

    def closeEvent(self, event) -> None:
        self.close_app()
        event.accept()
