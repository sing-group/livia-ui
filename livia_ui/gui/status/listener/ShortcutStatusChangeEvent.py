from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from livia_ui.gui.status.ShortcutStatus import ShortcutStatus


class ShortcutStatusChangeEvent:
    def __init__(self, status: ShortcutStatus, new: str, old: str):
        self._status: ShortcutStatus = status
        self._new: str = new
        self._old: str = old

    @property
    def status(self) -> ShortcutStatus:
        return self._status

    @property
    def new(self) -> str:
        return self._new

    @property
    def old(self) -> str:
        return self._old
