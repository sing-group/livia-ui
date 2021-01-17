from __future__ import annotations

from typing import TypeVar, Generic, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from livia_ui.gui.status.DisplayStatus import DisplayStatus

T = TypeVar('T', bool, str, Tuple[int, int])


class DisplayStatusChangeEvent(Generic[T]):
    def __init__(self, status: DisplayStatus, value: T):
        self._status: DisplayStatus = status
        self._value: T = value

    @property
    def status(self) -> DisplayStatus:
        return self._status

    @property
    def value(self) -> T:
        return self._value
