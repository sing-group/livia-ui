from __future__ import annotations

from typing import TypeVar, Generic, TYPE_CHECKING

from livia.input.FrameInput import FrameInput
from livia.output.FrameOutput import FrameOutput
from livia.process.analyzer.FrameAnalyzer import FrameAnalyzer

if TYPE_CHECKING:
    from livia_ui.gui.status.FrameProcessingStatus import FrameProcessingStatus

T = TypeVar('T', FrameInput, FrameOutput, FrameAnalyzer)


class FrameProcessingStatusChangeEvent(Generic[T]):
    def __init__(self, status: FrameProcessingStatus, new: T, old: T):
        self.__status: FrameProcessingStatus = status
        self.__new: T = new
        self.__old: T = old

    def status(self):
        return self.__status

    @property
    def new(self) -> T:
        return self.__new

    @property
    def old(self) -> T:
        return self.__old
