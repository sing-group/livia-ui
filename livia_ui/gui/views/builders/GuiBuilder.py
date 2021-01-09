from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar, Generic, TYPE_CHECKING, Optional, Tuple

from PyQt5.QtCore import QObject, QThread, QCoreApplication
from PyQt5.QtWidgets import QWidget, QStatusBar, QToolBar

from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow

T = TypeVar('T', QWidget, QStatusBar, QToolBar)


class GuiBuilder(QObject, Generic[T]):
    def __init__(self, independent_thread: bool = False, thread_priority: int = QThread.NormalPriority):
        super().__init__()
        self._thread: Optional[QThread] = None
        self._thread_priority: int = thread_priority

        self._livia_window: Optional[LiviaWindow] = None
        self._parent: Optional[T] = None

        if independent_thread:
            self._thread = QThread()
            self.moveToThread(self._thread)
            self._thread.finished.connect(self._thread.deleteLater)

    def build(self, livia_window: LiviaWindow, parent: T):
        self._livia_window = livia_window
        self._parent = parent

        self._build()

        if self._thread:
            self._thread.start()
            self._thread.setPriority(self._thread_priority)

    def _translate(self, text: str) -> str:
        return QCoreApplication.translate(self.__class__.__name__, text)

    def _get_shortcuts(self, action: ShortcutAction) -> Tuple[str]:
        return self._livia_window.status.shortcut_status.get_keys(action)

    @abstractmethod
    def _build(self):
        raise NotImplementedError()