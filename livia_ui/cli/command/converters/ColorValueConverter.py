from typing import Type, Any, Optional, Tuple

from livia_ui.cli.command.converters.ValueConverter import ValueConverter
from livia_ui.cli.command.converters import value_converter


@value_converter
class ColorValueConverter(ValueConverter[Tuple[int, int, int]]):
    def can_convert(self, value_type: Type[Any]) -> bool:
        return value_type == Tuple[int, int, int] or value_type == Optional[Tuple[int, int, int]]

    def convert(self, value: str) -> Tuple[int, int, int]:
        colors = value.split(",")

        if len(colors) != 3:
            raise ValueError("Invalid color format")

        colors = tuple([int(color) for color in colors])

        for i in range(0, 3):
            if colors[i] < 0 or colors[i] > 255:
                raise ValueError("Color out of range")

        return colors
