from __future__ import annotations

import os
from abc import abstractmethod
from typing import TypeVar, Generic, TYPE_CHECKING, Optional, Tuple, List

from PyQt5.QtCore import QObject, QThread, QCoreApplication
from PyQt5.QtGui import QIcon
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

        self._path: str = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        if independent_thread:
            self._thread = QThread()
            self.moveToThread(self._thread)
            self._thread.finished.connect(self._thread.deleteLater)

    def _translate(self, text: str) -> str:
        return QCoreApplication.translate(self.__class__.__name__, text)

    def _get_shortcuts(self, action: ShortcutAction) -> Tuple[str]:
        return self._livia_window.status.shortcut_status.get_keys(action)

    def _get_icon(self, name: str, sub_path: List[str] = ["icons"]) -> QIcon:
        return QIcon(os.path.join(self._path, *sub_path, name))

    def build(self, livia_window: LiviaWindow, parent: T):
        self._livia_window = livia_window
        self._parent = parent

        self._init()

        self._parent.destroyed.connect(self._on_destroy_parent)

        if self._thread:
            self._thread.start()
            self._thread.setPriority(self._thread_priority)

    def _init(self):
        self._before_init()
        self._build_widgets()
        self._connect_widgets()
        self._connect_signals()
        self._listen_livia()
        self._after_init()

    def _before_init(self):
        pass

    def _build_widgets(self):
        pass

    def _connect_widgets(self):
        pass

    def _connect_signals(self):
        pass

    def _listen_livia(self):
        pass

    def _after_init(self):
        pass

    def _disconnect_signals(self):
        pass

    def _on_destroy_parent(self):
        self._disconnect_signals()
