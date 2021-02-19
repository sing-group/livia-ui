from abc import ABC, abstractmethod
from typing import List

from livia_ui.gui.views.utils.Device import Device


class DeviceProvider(ABC):
    @abstractmethod
    def list(self) -> List[Device]:
        raise NotImplementedError()