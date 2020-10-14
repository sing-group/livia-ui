from argparse import Namespace

from livia.process.analyzer.FrameAnalyzerManager import FrameAnalyzerManager
from livia_ui.cli.command.ArgumentsCommand import ArgumentsCommand


class InfoArgumentsCommand(ArgumentsCommand):
    def __init__(self):
        super().__init__("info", "Information")

    def _build_subparser(self, subparser):
        subparser.add_argument("-a", "--analyzers", action="store_true", required=True)

    def execute_command(self, args: Namespace):
        if args.analyzers:
            print("Analyzers")
            for analyzer in FrameAnalyzerManager.list_analyzers():
                print(f"\t{analyzer}")
        else:
            print("Select an elements to get info")
