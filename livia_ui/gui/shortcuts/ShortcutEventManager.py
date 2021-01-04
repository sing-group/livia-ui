from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Callable, Tuple
from typing import Union, Optional, Set

from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

from livia.process.listener.EventListeners import EventListeners
from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction
from livia_ui.gui.shortcuts.errors.ShortcutUnknownError import ShortcutUnknownError
from livia_ui.gui.shortcuts.listeners.ShortcutTirggerListener import ShortcutTriggerListener
from livia_ui.gui.shortcuts.listeners.ShortcutTriggerEvent import ShortcutTriggerEvent

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow


class _Shortcut:
    def __init__(self, action: ShortcutAction,
                 keys: Union[str, Set[str]],
                 window: Optional[LiviaWindow] = None,
                 listeners: EventListeners[ShortcutTriggerListener] = EventListeners[ShortcutTriggerListener]()):
        self._action: ShortcutAction = action
        self._keys: Set[str] = keys if isinstance(keys, set) else set([keys])
        self._window: Optional[LiviaWindow] = window
        self._listeners: EventListeners[ShortcutTriggerListener] = listeners

        self._key_callbacks: Dict[str, Tuple[QShortcut, Callable[[], None]]] = {}
        self._update_key_callbacks()

    def _update_key_callbacks(self):
        if self._window is None:
            return

        keys_with_callback = set(self._key_callbacks.keys())
        keys_without_callback = self._keys.difference(keys_with_callback)
        keys_removed = keys_with_callback.difference(self._keys)

        for keys in keys_without_callback:
            def shortcut_callback():
                self._notify_shortcut_trigger(keys)
            q_shortcut = QShortcut(QKeySequence(keys), self._window)
            q_shortcut.activated.connect(shortcut_callback)

            self._key_callbacks[keys] = (q_shortcut, shortcut_callback)

        for keys in keys_removed:
            shortcut = self._key_callbacks[keys]
            del self._key_callbacks[keys]
            shortcut[0].activated.disconnect(shortcut[1])
            shortcut[0].disconnect()

    def _detach_all(self):
        for keys in self._keys:
            shortcut = self._key_callbacks[keys]
            del self._key_callbacks[keys]
            shortcut[0].activated.disconnect(shortcut[1])
            shortcut[0].disconnect()

    def _notify_shortcut_trigger(self, keys: str):
        for listener in self._listeners:
            listener.shortcut_triggered(ShortcutTriggerEvent(self, self._action, keys))

    @property
    def keys(self) -> Set[str]:
        return self._keys

    @property
    def action(self) -> ShortcutAction:
        return self._action

    @property
    def listeners(self) -> EventListeners[ShortcutTriggerListener]:
        return self._listeners

    @property
    def window(self) -> Optional[LiviaWindow]:
        return self._window

    @window.setter
    def window(self, window: Optional[LiviaWindow]):
        if window != window:
            if self._window is not None:
                self._detach_all()

            self._window = window

            if self._window is not None:
                self._update_key_callbacks()

    def add_keys(self, keys: Union[str, Set[str]]):
        if not self._keys.issuperset(keys):
            if isinstance(keys, set):
                self._keys.update(keys)
            else:
                self._keys.add(keys)
            self._update_key_callbacks()

    def set_keys(self, keys: Union[str, Set[str]]):
        keys = {keys} if isinstance(keys, str) else keys

        if self._keys != keys:
            self._keys.clear()
            self.add_keys(keys)

    def remove_keys(self, keys: Union[str, Set[str]]):
        if not self._keys.isdisjoint(keys):
            if isinstance(keys, set):
                self._keys.difference_update(keys)
            else:
                self._keys.remove(keys)
            self._update_key_callbacks()


class ShortcutEventManager:
    def __init__(self, window: Optional[LiviaWindow] = None):
        self._shortcuts: Set[_Shortcut] = set()

        self._window: Optional[LiviaWindow] = window

    @property
    def window(self) -> Optional[LiviaWindow]:
        return self._window

    @window.setter
    def window(self, window: LiviaWindow):
        if window != self._window:
            self._window = window
            for shortcut in self._shortcuts:
                shortcut.window = window

    def add_shortcut(self, action: ShortcutAction, keys: Union[str, Set[str]]):
        shortcut = self._get_shortcut_by_action(action)

        if shortcut:
            shortcut.add_keys(keys)
        else:
            self._shortcuts.add(_Shortcut(action, keys, self._window))

    def set_shortcut(self, action: ShortcutAction, keys: Union[str, Set[str]]):
        shortcut = self._get_shortcut_by_action(action)

        if shortcut:
            shortcut.set_keys(keys)
        else:
            self._shortcuts.add(_Shortcut(action, keys, self._window))

    def remove_shortcut(self, action: ShortcutAction, keys: Optional[Union[str, Set[str]]]):
        if keys:
            shortcut = self._get_shortcut_by_action(action)

            if shortcut:
                shortcut.remove_keys(keys)
                if not any(shortcut.keys):
                    self._remove_shortcut_by_action(action)
            else:
                raise ShortcutUnknownError(action)
        else:
            self._remove_shortcut_by_action(action)

    def add_action_listener(self, action: ShortcutAction, listener: ShortcutTriggerListener):
        shortcut = self._get_shortcut_by_action(action)
        if shortcut:
            shortcut.listeners.append(listener)
        else:
            raise ShortcutUnknownError(action)

    def _is_key_bound(self, key: str) -> bool:
        return self._get_shortcut_by_key(key) is not None

    def _get_shortcut_by_action(self, action: ShortcutAction) -> Optional[_Shortcut]:
        shortcut = [shortcut for shortcut in self._shortcuts if shortcut.action == action]

        return shortcut[0] if any(shortcut) else None

    def _get_shortcut_by_key(self, key: str) -> Optional[_Shortcut]:
        shortcut = [shortcut for shortcut in self._shortcuts if key in shortcut.keys]

        return shortcut[0] if any(shortcut) else None

    def _remove_shortcut_by_action(self, action: ShortcutAction) -> bool:
        shortcut = self._get_shortcut_by_action(action)

        if shortcut:
            self._shortcuts.remove(shortcut)
            return True
        else:
            return False
