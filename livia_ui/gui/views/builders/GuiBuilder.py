from __future__ import annotations

import os
from queue import Queue
from typing import TypeVar, Generic, TYPE_CHECKING, Optional, Tuple, List, Dict, Callable

from PyQt5.QtCore import QObject, QThread, QCoreApplication, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QStatusBar, QToolBar

from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction
from livia_ui.gui.status.LiviaStatus import LiviaStatus

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow

T = TypeVar('T', QWidget, QStatusBar, QToolBar)


class _ActionQueueThread(QThread):
    def __init__(self):
        super().__init__()
        self._queue: Queue = Queue()
        self._alive: bool = True

    def run(self) -> None:
        while self._alive:
            action = self._queue.get(True)
            action()

    def add_action(self, action: Callable[[], None]):
        self._queue.put(action)

    def stop(self):
        self._alive = False
        self._queue.put(lambda: None)


class GuiBuilder(QObject, Generic[T]):
    def __init__(self, independent_thread: bool = False, thread_priority: int = QThread.NormalPriority):
        super().__init__()
        self._thread: Optional[_ActionQueueThread] = None
        self._thread_priority: int = thread_priority

        self.__livia_window: Optional[LiviaWindow] = None
        self._parent: Optional[T] = None

        self._signals: Dict[str, Tuple[pyqtSignal, Callable[..., None]]] = {}

        self._path: str = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        if independent_thread:
            self._thread = _ActionQueueThread()
            self.moveToThread(self._thread)
            self._thread.finished.connect(self._thread.deleteLater)

    def __getattr__(self, name):
        if name.startswith("_emit"):
            signal_name = name[5:]

            if signal_name not in self._signals:
                raise AttributeError(f"Missing signal {signal_name}")

            signal = self._signals[signal_name][0]

            def wrapper(*args, **kwargs):
                if self._thread:
                    self._thread.add_action(lambda: signal.emit(*args, **kwargs))
                else:
                    signal.emit(*args, **kwargs)

            return wrapper

        return super(QObject, self).__getattr__(name)

    def _translate(self, text: str) -> str:
        return QCoreApplication.translate(self.__class__.__name__, text)

    @property
    def _livia_window(self) -> LiviaWindow:
        if not self.__livia_window:
            raise AssertionError("Livia window was not assigned")

        return self.__livia_window

    @property
    def _livia_status(self) -> LiviaStatus:
        return self._livia_window.status

    def _get_shortcuts(self, action: ShortcutAction) -> Tuple[str, ...]:
        if not self._livia_status.shortcut_status.has_action(action):
            raise ValueError(f"Action not registered: {action}")

        return self._livia_status.shortcut_status.get_keys(action)

    def _get_icon(self, name: str, sub_path: List[str] = ["icons"]) -> QIcon:
        return QIcon(os.path.join(self._path, *sub_path, name))

    def build(self, livia_window: LiviaWindow, parent: T):
        self.__livia_window = livia_window
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
        self._signals.update(self._register_signals())
        self._connect_signals()
        self._listen_livia()
        self._after_init()

    def _before_init(self):
        pass

    def _build_widgets(self):
        pass

    def _connect_widgets(self):
        pass

    def _register_signals(self) -> Dict[str, Tuple[pyqtSignal, Callable[..., None]]]:
        return {}

    def _connect_signals(self):
        for signal in self._signals.values():
            signal[0].connect(signal[1])

    def _listen_livia(self):
        pass

    def _after_init(self):
        pass

    def _disconnect_signals(self):
        for signal in self._signals.values():
            signal[0].disconnect(signal[1])

    def _on_destroy_parent(self):
        if self._thread:
            self._thread.stop()

        self._disconnect_signals()
