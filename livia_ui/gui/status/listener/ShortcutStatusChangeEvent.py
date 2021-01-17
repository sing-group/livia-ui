from __future__ import annotations

from typing import Optional, Tuple, Set, Union, TYPE_CHECKING

from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction

if TYPE_CHECKING:
    from livia_ui.gui.status.ShortcutStatus import ShortcutStatus


class ShortcutStatusChangeEvent:
    def __init__(self,
                 configuration: ShortcutStatus,
                 action: ShortcutAction,
                 old_keys: Optional[Union[Tuple[str, ...], Set[str]]],
                 new_keys: Optional[Union[Tuple[str, ...], Set[str]]]):
        self._configuration: ShortcutStatus = configuration
        self._action: ShortcutAction = action

        self._old_keys: Optional[Tuple[str, ...]] = None
        self._new_keys: Optional[Tuple[str, ...]] = None

        if old_keys:
            self._old_keys = old_keys if isinstance(old_keys, tuple) else tuple(old_keys)
        if new_keys:
            self._new_keys = new_keys if isinstance(new_keys, tuple) else tuple(new_keys)

    @property
    def configuration(self) -> ShortcutStatus:
        return self._configuration

    @property
    def action(self) -> ShortcutAction:
        return self._action

    @property
    def old_keys(self) -> Optional[Tuple[str, ...]]:
        return self._old_keys

    @property
    def new_keys(self) -> Optional[Tuple[str, ...]]:
        return self._new_keys
