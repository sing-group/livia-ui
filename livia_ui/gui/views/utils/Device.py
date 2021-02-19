from typing import Union


class Device:
    def __init__(self, device_name: str, device_index: Union[str, int], api_preference: int):
        self._device_name: str = device_name
        self._device_index: Union[str, int] = device_index
        self._api_preference: int = api_preference

    @property
    def name(self) -> str:
        return self._device_name

    @property
    def index(self) -> Union[str, int]:
        return self._device_index

    @property
    def api(self) -> int:
        return self._api_preference
