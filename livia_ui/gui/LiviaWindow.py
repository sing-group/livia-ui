from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QMainWindow

from livia_ui.gui.status.LiviaStatus import LiviaStatus
from livia_ui.gui.views.UiLiviaWindow import UiLiviaWindow
from livia_ui.gui.views.builders.GuiBuilders import GuiBuilders


class LiviaWindow(QMainWindow, UiLiviaWindow):
    exit_code_signal = pyqtSignal(int)

    def __init__(self, livia_status: LiviaStatus, gui_builders: GuiBuilders = GuiBuilders()):
        self.EXIT_CODE_REBOOT = -1

        super(LiviaWindow, self).__init__()

        self._livia_status = livia_status

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
