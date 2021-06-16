import logging

import livia.process.analyzer
import livia_ui.cli.command.converters
from livia.process.analyzer.FrameAnalyzerManager import FrameAnalyzerManager
from livia_ui.cli import LIVIA_CLI_LOGGER
from livia_ui.cli.LiviaArgumentParser import LiviaArgumentParser
from livia_ui.cli.command.converters.ValueConverterFactory import ValueConverterFactory

LIVIA_CLI_LOGGER.setLevel(logging.INFO)
LIVIA_CLI_LOGGER.addHandler(logging.StreamHandler())

FrameAnalyzerManager.load_module(livia.process.analyzer)
ValueConverterFactory.load_module(livia_ui.cli.command.converters)

if __name__ == '__main__':
    parser = LiviaArgumentParser()
    parser.parse_and_execute()
