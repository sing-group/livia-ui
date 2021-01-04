from typing import List, Union, Tuple

from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction


class ShortcutUnknownError(Exception):
    def __init__(self, actions: Union[ShortcutAction, List[ShortcutAction]]):
        self._shortcuts: Tuple[ShortcutAction] = tuple(actions if isinstance(actions, ShortcutAction) else actions)

    @property
    def actions(self) -> Tuple[ShortcutAction]:
        return self._actions
