from PySide2.QtCore import Signal, Slot, Qt
from PySide2.QtGui import QResizeEvent
from PySide2.QtWidgets import QMainWindow

from livia.process.listener import build_listener
from livia_ui.gui.status.LiviaStatus import LiviaStatus
from livia_ui.gui.status.listener.DisplayStatusChangeEvent import DisplayStatusChangeEvent
from livia_ui.gui.status.listener.DisplayStatusChangeListener import DisplayStatusChangeListener
from livia_ui.gui.views.UiLiviaWindow import UiLiviaWindow
from livia_ui.gui.views.builders.GuiBuilders import GuiBuilders


class LiviaWindow(QMainWindow, UiLiviaWindow):
    _change_to_fullscreen_signal: Signal = Signal(bool)

    def __init__(self, livia_status: LiviaStatus, gui_builders: GuiBuilders = GuiBuilders()):
        super(LiviaWindow, self).__init__()
        self._livia_status = livia_status

        self.setup_ui(self, gui_builders)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        size = livia_status.display_status.window_size
        self.resize(*size)
        self.setMinimumSize(*size)

        self._change_to_fullscreen_signal.connect(self._on_change_to_fullscreen_signal)

        self._livia_status.display_status.add_display_status_change_listener(
            build_listener(DisplayStatusChangeListener,
                           fullscreen_changed=self._on_fullscreen_changed
                           )
        )

    def resizeEvent(self, event: QResizeEvent):
        new_size = event.size()
        if new_size != event.oldSize():
            self._livia_status.display_status.window_size = (new_size.width(), new_size.height())

    @property
    def status(self) -> LiviaStatus:
        return self._livia_status

    @Slot(bool)
    def _on_change_to_fullscreen_signal(self, fullscreen: bool):
        if fullscreen:
            self.showFullScreen()
        else:
            self.showNormal()

    def _on_fullscreen_changed(self, event: DisplayStatusChangeEvent[bool]):
        self._change_to_fullscreen_signal.emit(event.value)

    def closeEvent(self, event) -> None:
        self.deleteLater()
        event.accept()
