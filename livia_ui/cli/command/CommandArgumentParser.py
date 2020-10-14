from argparse import ArgumentParser
from typing import List

from livia_ui.cli.command.ArgumentsCommand import ArgumentsCommand


class CommandArgumentParser(ArgumentParser):
    def __init__(self, commands: List[ArgumentsCommand], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__commands: List[ArgumentsCommand] = commands.copy()

        subparsers = self.add_subparsers(dest="command", parser_class=ArgumentParser, required=True)
        for command in self.__commands:
            command.add_parser(subparsers)

    def parse_and_execute(self):
        args = self.parse_args()

        for command in self.__commands:
            if command.is_command(args.command):
                command.execute_command(args)
                return

        self.error("Unrecognized command: " + args.command)
