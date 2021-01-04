from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction


class ShortcutActionAlreadyRegisteredError(Exception):
    def __init__(self, action: ShortcutAction):
        self._action: ShortcutAction = action

    @property
    def action(self) -> ShortcutAction:
        return self._action
