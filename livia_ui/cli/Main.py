import logging

import livia.process.analyzer
import livia_ui.cli.command.converters
from livia.process.analyzer.FrameAnalyzerManager import FrameAnalyzerManager
from livia_ui.cli.LiviaArgumentParser import LiviaArgumentParser
from livia_ui.cli.command.converters.ValueConverterFactory import ValueConverterFactory

FrameAnalyzerManager.load_module(livia.process.analyzer)
ValueConverterFactory.load_module(livia_ui.cli.command.converters)

if __name__ == '__main__':
    parser = LiviaArgumentParser()
    parser.parse_and_execute()
