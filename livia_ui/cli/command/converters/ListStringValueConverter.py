from typing import Type, Any, Optional, List

from livia_ui.cli.command.converters.ValueConverter import ValueConverter
from livia_ui.cli.command.converters import value_converter


@value_converter
class ColorValueConverter(ValueConverter[List[str]]):
    def can_convert(self, value_type: Type[Any]) -> bool:
        return value_type == List[str] or value_type == Optional[List[str]]

    def convert(self, value: str) -> List[str]:
        return value.split(",")
