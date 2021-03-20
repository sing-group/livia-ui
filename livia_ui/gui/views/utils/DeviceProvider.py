from abc import ABC, abstractmethod
from typing import List

from livia.input.DeviceFrameInput import Device


class DeviceProvider(ABC):
    @abstractmethod
    def list(self) -> List[Device]:
        raise NotImplementedError()
