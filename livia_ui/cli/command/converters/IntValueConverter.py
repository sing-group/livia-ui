from typing import Type, Any, Optional

from livia_ui.cli.command.converters.ValueConverter import ValueConverter
from livia_ui.cli.command.converters import value_converter


@value_converter
class IntValueConverter(ValueConverter[int]):
    def can_convert(self, value_type: Type[Any]) -> bool:
        return value_type == int or value_type == Optional[int]

    def convert(self, value: str) -> int:
        return int(value)
