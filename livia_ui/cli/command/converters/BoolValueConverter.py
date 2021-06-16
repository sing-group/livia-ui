from typing import Type, Any, Optional

from livia_ui.cli.command.converters.ValueConverter import ValueConverter
from livia_ui.cli.command.converters import value_converter


@value_converter
class BoolValueConverter(ValueConverter[bool]):
    def can_convert(self, value_type: Type[Any]) -> bool:
        return value_type == bool or value_type == Optional[bool]

    def convert(self, value: str) -> bool:
        return bool(value)
