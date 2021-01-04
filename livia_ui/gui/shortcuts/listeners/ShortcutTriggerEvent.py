from __future__ import annotations

from typing import TYPE_CHECKING

from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction

if TYPE_CHECKING:
    from livia_ui.gui.shortcuts.ShortcutEventManager import ShortcutEventManager


class ShortcutTriggerEvent:
    def __init__(self, manager: ShortcutEventManager, action: ShortcutAction, keys: str):
        self._manager: ShortcutEventManager = manager
        self._action: ShortcutAction = action
        self._keys: str = keys

    @property
    def manager(self) -> ShortcutEventManager:
        return self._manager

    @property
    def action(self) -> ShortcutAction:
        return self._action

    @property
    def keys(self) -> str:
        return self._keys
