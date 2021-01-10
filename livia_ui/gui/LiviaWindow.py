from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QMainWindow

from livia.process.listener import build_listener
from livia_ui.gui.status.LiviaStatus import LiviaStatus
from livia_ui.gui.status.listener.DisplayStatusChangeEvent import DisplayStatusChangeEvent
from livia_ui.gui.status.listener.DisplayStatusChangeListener import DisplayStatusChangeListener
from livia_ui.gui.views.UiLiviaWindow import UiLiviaWindow
from livia_ui.gui.views.builders.GuiBuilders import GuiBuilders


class LiviaWindow(QMainWindow, UiLiviaWindow):
    change_fullscreen: pyqtSignal = pyqtSignal(bool)

    def __init__(self, livia_status: LiviaStatus, gui_builders: GuiBuilders = GuiBuilders()):
        super(LiviaWindow, self).__init__()

        self._livia_status = livia_status

        self.setup_ui(self, gui_builders)

        size = livia_status.display_status.window_size
        self.resize(*size)
        self.setMinimumSize(*size)

        self.change_fullscreen.connect(self._on_change_fullscreen)

        self._livia_status.display_status.add_display_status_change_listener(
            build_listener(DisplayStatusChangeListener,
                           fullscreen_changed=self._on_fullscreen_changed
                           )
        )

        self._start_movie()

    def resizeEvent(self, event: QResizeEvent):
        new_size = event.size()
        if new_size != event.oldSize():
            self._livia_status.display_status.window_size = (new_size.width(), new_size.height())

    @property
    def status(self) -> LiviaStatus:
        return self._livia_status

    @pyqtSlot(bool)
    def _on_change_fullscreen(self, fullscreen: bool):
        if fullscreen:
            self.showFullScreen()
        else:
            self.showNormal()

    def _on_fullscreen_changed(self, event: DisplayStatusChangeEvent[bool]):
        self.change_fullscreen.emit(event.value)

    def _start_movie(self) -> None:
        if not self.status.video_stream_status.frame_processor.is_running():
            self._livia_status.video_stream_status.frame_processor.start()

    def closeEvent(self, event) -> None:
        self.deleteLater()
        event.accept()
