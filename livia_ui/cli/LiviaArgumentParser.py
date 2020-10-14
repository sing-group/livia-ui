from typing import List

from livia_ui.cli.command.ArgumentsCommand import ArgumentsCommand
from livia_ui.cli.command.CommandArgumentParser import CommandArgumentParser
from livia_ui.cli.command.InfoArgumentsCommand import InfoArgumentsCommand
from livia_ui.cli.command.ProcessArgumentsCommand import ProcessArgumentsCommand


class LiviaArgumentParser(CommandArgumentParser):
    def __init__(self, prog: str = "LIVIA CLI", description: str = "LIVIA Command Line"):
        super().__init__(self._build_commands(), prog=prog, description=description)

    def _build_commands(self) -> List[ArgumentsCommand]:
        return [
            InfoArgumentsCommand(),
            ProcessArgumentsCommand()
        ]
