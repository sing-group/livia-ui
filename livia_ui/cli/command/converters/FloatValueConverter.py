from typing import Type, Any, Optional

from livia_ui.cli.command.converters.ValueConverter import ValueConverter
from livia_ui.cli.command.converters import value_converter


@value_converter
class FloatValueConverter(ValueConverter[float]):
    def can_convert(self, value_type: Type[Any]) -> bool:
        return value_type == float or value_type == Optional[float]

    def convert(self, value: str) -> float:
        return float(value)
