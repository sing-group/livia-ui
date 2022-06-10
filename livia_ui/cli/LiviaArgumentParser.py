import logging
from argparse import FileType, Namespace
from typing import List

from livia import LIVIA_LOGGER
from livia.benchmarking import LIVIA_BENCHMARK_LOGGER
from livia_ui.cli import LIVIA_CLI_LOGGER
from livia_ui.cli.command.ArgumentsCommand import ArgumentsCommand
from livia_ui.cli.command.CommandArgumentParser import CommandArgumentParser
from livia_ui.cli.command.InfoArgumentsCommand import InfoArgumentsCommand
from livia_ui.cli.command.ProcessArgumentsCommand import ProcessArgumentsCommand


class LiviaArgumentParser(CommandArgumentParser):
    def __init__(self, prog: str = "LIVIA CLI", description: str = "LIVIA Command Line"):
        super().__init__(self._build_commands(), prog=prog, description=description)

        logging_group = self.add_argument_group("Logging")
        logging_group.add_argument("--log-all-stdout", dest="log_all_stdout", action="store_true",
                                   help="shows core and CLI logs on the standard output.")
        logging_group.add_argument("--log-core-stdout", dest="log_core_stdout", action="store_true",
                                   help="shows core log on the standard output")
        logging_group.add_argument("--log-cli-stdout", dest="log_cli_stdout", action="store_true",
                                   help="shows CLI log on the standard output")
        logging_group.add_argument("--log-benchmark-stdout", dest="log_benchmark_stdout", action="store_true",
                                   help="shows benchmark log on the standard output")
        logging_group.add_argument("--log-stdout-format", dest="log_stdout_format", type=str,
                                   default="%(asctime)s,%(message)s", help="sets the standard output logging format.")

        logging_group.add_argument("--log-all-file", dest="log_all_file", type=FileType("a"), required=False,
                                   help="stores core and CLI logs on the specified file. If this parameter is "
                                        "provided, then --log-core-file and --log-cli-file are ignored.")
        logging_group.add_argument("--log-core-file", dest="log_core_file", type=FileType("a"), required=False,
                                   help="stores core log on the specified file.")
        logging_group.add_argument("--log-cli-file", dest="log_cli_file", type=FileType("a"), required=False,
                                   help="stores CLI log on the specified file.")
        logging_group.add_argument("--log-benchmark-file", dest="log_benchmark_file", type=FileType("a"),
                                   required=False, help="stores benchmark log on the specified file.")

        logging_group.add_argument("--log-all-file-format", dest="log_all_file_format", type=str, required=False,
                                   help="sets the core and CLI logging file format. If this parameter is "
                                        "provided, then --log-core-file-format and --log-cli-file-format are ignored.")
        logging_group.add_argument("--log-core-file-format", dest="log_core_file_format", type=str,
                                   default="%(asctime)s,%(message)s", help="sets the core logging file format.")
        logging_group.add_argument("--log-cli-file-format", dest="log_cli_file_format", type=str,
                                   default="%(asctime)s,%(message)s", help="sets the CLI logging file format.")
        logging_group.add_argument("--log-benchmark-file-format", dest="log_benchmark_file_format", type=str,
                                   required=False, help="sets the benchmark logging file format.")

        logging_group.add_argument("--log-all-level", dest="log_all_level", type=str, required=False,
                                   help="sets the core and CLI logging level. If this parameter is provided, then "
                                        "--log-core-level and --log-cli-level are ignored.")
        logging_group.add_argument("--log-core-level", dest="log_core_level", type=str, default="INFO",
                                   help="sets the core logging level.")
        logging_group.add_argument("--log-cli-level", dest="log_cli_level", type=str, default="INFO",
                                   help="sets the CLI logging level.")
        logging_group.add_argument("--log-benchmark-level", dest="log_benchmark_level", type=str, default="INFO",
                                   help="sets the benchmark logging level.")

    def parse_and_execute(self):
        self._configure_logs(self.parse_args())

        super().parse_and_execute()

    def _build_commands(self) -> List[ArgumentsCommand]:
        return [
            InfoArgumentsCommand(),
            ProcessArgumentsCommand()
        ]

    def _configure_logs(self, args: Namespace) -> None:
        if args.log_all_level is not None:
            level = logging.getLevelName(args.log_all_level)
            LIVIA_LOGGER.setLevel(level)
            LIVIA_CLI_LOGGER.setLevel(level)
        else:
            LIVIA_LOGGER.setLevel(logging.getLevelName(args.log_core_level))
            LIVIA_CLI_LOGGER.setLevel(logging.getLevelName(args.log_cli_level))

        LIVIA_BENCHMARK_LOGGER.setLevel(args.log_benchmark_level)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(logging.Formatter(args.log_stdout_format))

        if args.log_all_stdout:
            LIVIA_LOGGER.addHandler(stdout_handler)
            LIVIA_CLI_LOGGER.addHandler(stdout_handler)
        else:
            if args.log_core_stdout:
                LIVIA_LOGGER.addHandler(stdout_handler)
            if args.log_cli_stdout:
                LIVIA_CLI_LOGGER.addHandler(stdout_handler)

        if args.log_benchmark_stdout:
            LIVIA_BENCHMARK_LOGGER.addHandler(stdout_handler)

        fh = {}
        if args.log_all_file is not None:
            file_handler_all = logging.FileHandler(
                filename=args.log_all_file.name, mode="a", encoding=args.log_all_file.encoding
            )

            if args.log_all_file_format is not None:
                log_all_file_format = args.log_all_file_format
            else:
                log_core_format = args.log_core_file_format
                log_cli_format = args.log_cli_file_format

                if log_core_format != log_cli_format:
                    raise ValueError(f"Two different formats provided for the same logging file")

                log_all_file_format = log_core_format

            file_handler_all.setFormatter(logging.Formatter(log_all_file_format))

            fh[log_all_file_format] = (file_handler_all, log_all_file_format)

            LIVIA_LOGGER.addHandler(file_handler_all)
            LIVIA_CLI_LOGGER.addHandler(file_handler_all)
        else:
            if args.log_core_file is not None:
                file_core_handler = logging.FileHandler(
                    filename=args.log_core_file.name, mode="a", encoding=args.log_core_file.encoding
                )
                if args.log_core_file_format is not None:
                    file_core_handler.setFormatter(logging.Formatter(args.log_core_file_format))

                fh[args.log_core_file.name] = (file_core_handler, args.log_core_file_format)
                LIVIA_LOGGER.addHandler(file_core_handler)

            if args.log_cli_file is not None:
                if args.log_cli_file.name in fh:
                    logger, logging_format = fh[args.log_cli_file.name]
                    if args.log_cli_file_format is not None and args.log_cli_file_format != logging_format:
                        raise ValueError(f"Two different formats provided for the same logging file")

                    LIVIA_CLI_LOGGER.addHandler(logger)
                else:
                    file_cli_handler = logging.FileHandler(
                        filename=args.log_cli_file.name, mode="a", encoding=args.log_cli_file.encoding
                    )
                    if args.log_cli_file_format is not None:
                        file_cli_handler.setFormatter(logging.Formatter(args.log_cli_file_format))

                    fh[args.log_cli_file.name] = (file_cli_handler, args.log_cli_file_format)
                    LIVIA_CLI_LOGGER.addHandler(file_cli_handler)

        if args.log_benchmark_file is not None:
            if args.log_benchmark_file.name in fh:
                logger, logging_format = fh[args.log_benchmark_file.name]
                if args.log_benchmark_file_format is not None and args.log_benchmark_file_format != logging_format:
                    raise ValueError(f"Two different formats provided for the same logging file")

                LIVIA_BENCHMARK_LOGGER.addHandler(logger)
            else:
                file_benchmark_handler = logging.FileHandler(
                    filename=args.log_benchmark_file.name, mode="a", encoding=args.log_benchmark_file.encoding
                )
                if args.log_benchmark_file_format is not None:
                    file_benchmark_handler.setFormatter(logging.Formatter(args.log_benchmark_file_format))

                fh[args.log_benchmark_file.name] = (file_benchmark_handler, args.log_benchmark_file_format)
                LIVIA_BENCHMARK_LOGGER.addHandler(file_benchmark_handler)
