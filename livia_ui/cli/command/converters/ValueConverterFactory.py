import os
import pkgutil
from importlib import import_module
from typing import Any, Set, Type

from livia_ui.cli import LIVIA_CLI_LOGGER
from livia_ui.cli.command.converters.ValueConverter import ValueConverter


class ValueConverterFactory:
    __instance = None

    def __init__(self):
        if not hasattr(self, "_ValueConverterFactory__converters"):
            self.__converters: Set[ValueConverter[Any]] = set()

    def __new__(cls, *args, **kwargs):
        if not ValueConverterFactory.__instance:
            ValueConverterFactory.__instance = super().__new__(cls, *args, **kwargs)

        return ValueConverterFactory.__instance

    @staticmethod
    def register(converter: ValueConverter):
        factory = ValueConverterFactory()
        factory.__converters.add(converter)
        LIVIA_CLI_LOGGER.debug(f"Value converter registered: {type(converter)}")

    def get_converter(self, value_type: Type[Any]) -> ValueConverter[Any]:
        for converter in self.__converters:
            if converter.can_convert(value_type):
                return converter

        raise ValueError(f"No converter found for type: {value_type}")

    @staticmethod
    def load_module(module):
        for module_loader, name, is_package in pkgutil.iter_modules([os.path.dirname(module.__file__)]):
            if not is_package:
                import_module(f"{module.__name__}.{name}")
