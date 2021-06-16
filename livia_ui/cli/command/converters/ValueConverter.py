from abc import ABC
from typing import TypeVar, Generic, Type, Any

T = TypeVar('T')


class ValueConverter(ABC, Generic[T]):
    def convert(self, value: str) -> T:
        raise NotImplementedError()

    def can_convert(self, value_type: Type[Any]) -> bool:
        raise NotImplementedError()
