from typing import Type, Any, TextIO, Optional

from livia_ui.cli.command.converters.ValueConverter import ValueConverter
from livia_ui.cli.command.converters import value_converter


@value_converter
class TextIOValueConverter(ValueConverter[TextIO]):
    def can_convert(self, value_type: Type[Any]) -> bool:
        return value_type == TextIO or value_type == Optional[TextIO]

    def convert(self, value: str) -> TextIO:
        return open(value, "r", encoding="utf-8")
