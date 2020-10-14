from abc import ABC, abstractmethod
from argparse import Namespace


class ArgumentsCommand(ABC):
    def __init__(self, id: str, help: str):
        self.__id: str = id
        self.__help: str = help

    @property
    def id(self) -> str:
        return self.__id

    @property
    def help(self) -> str:
        return self.__help

    def is_command(self, id: str) -> bool:
        return self.id == id

    def add_parser(self, subparsers):
        subparser = subparsers.add_parser(self.id, help=self.help)
        self._build_subparser(subparser)

    @abstractmethod
    def _build_subparser(self, subparser):
        pass

    @abstractmethod
    def execute_command(self, args: Namespace):
        pass
