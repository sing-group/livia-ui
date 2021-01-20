from __future__ import annotations

import os
from abc import abstractmethod
from typing import TypeVar, Generic, TYPE_CHECKING, Optional, Tuple, List

from PySide2.QtCore import QObject, QCoreApplication
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QStatusBar, QToolBar

from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction
from livia_ui.gui.status.LiviaStatus import LiviaStatus

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow

T = TypeVar('T', QWidget, QStatusBar, QToolBar)


class GuiBuilder(QObject, Generic[T]):
    def __init__(self, livia_window: LiviaWindow, *args, **kwargs):
        if "parent" in kwargs:
            super(GuiBuilder, self).__init__(*args, **kwargs)
        else:
            super(GuiBuilder, self).__init__(parent=livia_window, *args, **kwargs)

        if livia_window is None:
            raise ValueError("livia_window can't be None")

        self._livia_window: LiviaWindow = livia_window
        self._parent_widget: Optional[T] = None

        self._path: str = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def _translate(self, text: str) -> str:
        return QCoreApplication.translate(self.__class__.__name__, text)

    @property
    def _livia_status(self) -> LiviaStatus:
        return self._livia_window.status

    def _get_shortcuts(self, action: ShortcutAction) -> Tuple[str, ...]:
        if not self._livia_status.shortcut_status.has_action(action):
            raise ValueError(f"Action not registered: {action}")

        return self._livia_status.shortcut_status.get_keys(action)

    def _get_icon(self, name: str, sub_path: List[str] = ["icons"]) -> QIcon:
        return QIcon(os.path.join(self._path, *sub_path, name))

    def build(self, parent: Optional[QWidget] = None) -> T:
        self._parent_widget = self._create_parent_widget(parent)

        self._init()

        self._parent_widget.destroyed.connect(self._on_destroy_parent_widget)

        return self._parent_widget

    @abstractmethod
    def _create_parent_widget(self, parent: QWidget) -> T:
        raise NotImplementedError()

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

    def _on_destroy_parent_widget(self):
        self._disconnect_signals()
