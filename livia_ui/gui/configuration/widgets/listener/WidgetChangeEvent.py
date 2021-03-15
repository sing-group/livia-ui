from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from livia.process.FrameProcessor import FrameProcessor


class WidgetChangeEvent:
    def __init__(self, new_value: Any):
        self.__new_value: int = new_value

    def value(self) -> Any:
        return self.__new_value

