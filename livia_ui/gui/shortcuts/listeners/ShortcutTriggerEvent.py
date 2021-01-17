from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction


class ShortcutTriggerEvent:
    def __init__(self, action: ShortcutAction, keys: str):
        self._action: ShortcutAction = action
        self._keys: str = keys

    @property
    def action(self) -> ShortcutAction:
        return self._action

    @property
    def keys(self) -> str:
        return self._keys
