import logging

import livia.process.analyzer
from livia.process.analyzer.FrameAnalyzerManager import FrameAnalyzerManager
from livia_ui.cli import LIVIA_CLI_LOGGER
from livia_ui.cli.LiviaArgumentParser import LiviaArgumentParser

LIVIA_CLI_LOGGER.setLevel(logging.INFO)
LIVIA_CLI_LOGGER.addHandler(logging.StreamHandler())

FrameAnalyzerManager.load_module(livia.process.analyzer)

if __name__ == '__main__':
    parser = LiviaArgumentParser()
    parser.parse_and_execute()
