from livia_ui.cli.command.converters.ValueConverterFactory import ValueConverterFactory


def value_converter(cls=None):
    ValueConverterFactory().register(cls())

    return cls
