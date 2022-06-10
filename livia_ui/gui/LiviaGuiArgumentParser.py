import logging
import os
from PySide2.QtWidgets import QApplication
from argparse import ArgumentParser, FileType, Namespace, ArgumentTypeError, ArgumentDefaultsHelpFormatter

from livia import LIVIA_LOGGER
from livia.benchmarking import LIVIA_BENCHMARK_LOGGER
from livia.input.FileFrameInput import FileFrameInput
from livia.input.NoFrameInput import NoFrameInput
from livia.process.analyzer.AsyncAnalyzerFrameProcessor import DEFAULT_MODIFICATION_PERSISTENCE, DEFAULT_NUM_THREADS
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.LiviaWindow import LiviaWindow
from livia_ui.gui.configuration.ConfigurationStorage import ConfigurationStorage
from livia_ui.gui.status.DisplayStatus import DisplayStatus
from livia_ui.gui.status.FrameProcessingStatus import FrameProcessingStatus
from livia_ui.gui.status.LiviaStatus import LiviaStatus
from livia_ui.gui.status.ShortcutStatus import ShortcutStatus


def at_least_one(value: str) -> int:
    value_as_int = int(value)
    if value_as_int < 1:
        raise ArgumentTypeError("the minimum accepted value is 1")

    return value_as_int


class LiviaGuiArgumentParser(ArgumentParser):
    def __init__(self, app_name: str = "LIVIA", *args, **kwargs):
        super(LiviaGuiArgumentParser, self).__init__(
            formatter_class=ArgumentDefaultsHelpFormatter,  # Shows defaults in help
            *args, **kwargs
        )

        self._app_name: str = app_name

        self._app: QApplication = None
        self._livia_window: LiviaWindow = None
        self._configuration_storage: ConfigurationStorage = None

        default_modification_persistence = DEFAULT_MODIFICATION_PERSISTENCE
        default_frame_processor_threads = DEFAULT_NUM_THREADS

        self.add_argument("--open", dest="open", type=FileType("r"), help="Opens a file when application is started")
        self.add_argument("--modification-persistence", dest="modification_persistence", type=int,
                          default=default_modification_persistence,
                          help="Sets the number of frames that a frame modification will persist "
                               f"if no new modification is created (default: {default_modification_persistence})")
        self.add_argument("--frame-processor-threads", dest="frame_processor_threads", type=at_least_one,
                          default=default_frame_processor_threads,
                          help="Number of thread used by the asynchronous frame processor "
                               f"(default: {default_frame_processor_threads})")

        config_group = self.add_argument_group("Configuration")
        config_group.add_argument("--config-file", dest="config_file", type=FileType("r"),
                                  default=os.path.abspath(os.path.join(os.getcwd(), "configuration.xml")),
                                  help="Configuration file. By default, the application will load a "
                                       "'configuration.xml' file in the working directory")
        config_group.add_argument("--no-config", dest="no_config", action="store_true",
                                  help="Application starts with default configuration.")
        config_group.add_argument("--no-auto-update-config", dest="auto_update_config", action="store_false",
                                  help="Automatically updates the configuration file with the changes done in the "
                                       "application. Default value: True")

        logging_group = self.add_argument_group("Logging")
        logging_group.add_argument("--log-all-stdout", dest="log_all_stdout", action="store_true",
                                   help="shows core and GUI logs on the standard output.")
        logging_group.add_argument("--log-core-stdout", dest="log_core_stdout", action="store_true",
                                   help="shows core log on the standard output")
        logging_group.add_argument("--log-gui-stdout", dest="log_gui_stdout", action="store_true",
                                   help="shows GUI log on the standard output")
        logging_group.add_argument("--log-benchmark-stdout", dest="log_benchmark_stdout", action="store_true",
                                   help="shows benchmark log on the standard output")
        logging_group.add_argument("--log-stdout-format", dest="log_stdout_format", type=str,
                                   default="%(asctime)s,%(message)s", help="sets the standard output logging format.")

        logging_group.add_argument("--log-all-file", dest="log_all_file", type=FileType("a"), required=False,
                                   help="stores core and GUI logs on the specified file. If this parameter is "
                                        "provided, then --log-core-file and --log-gui-file are ignored.")
        logging_group.add_argument("--log-core-file", dest="log_core_file", type=FileType("a"), required=False,
                                   help="stores core log on the specified file.")
        logging_group.add_argument("--log-gui-file", dest="log_gui_file", type=FileType("a"), required=False,
                                   help="stores GUI log on the specified file.")
        logging_group.add_argument("--log-benchmark-file", dest="log_benchmark_file", type=FileType("a"),
                                   required=False, help="stores benchmark log on the specified file.")

        logging_group.add_argument("--log-all-file-format", dest="log_all_file_format", type=str, required=False,
                                   help="sets the core and GUI logging file format. If this parameter is "
                                        "provided, then --log-core-file-format and --log-gui-file-format are ignored.")
        logging_group.add_argument("--log-core-file-format", dest="log_core_file_format", type=str,
                                   default="%(asctime)s,%(message)s", help="sets the core logging file format.")
        logging_group.add_argument("--log-gui-file-format", dest="log_gui_file_format", type=str,
                                   default="%(asctime)s,%(message)s", help="sets the GUI logging file format.")
        logging_group.add_argument("--log-benchmark-file-format", dest="log_benchmark_file_format", type=str,
                                   required=False, help="sets the benchmark logging file format.")

        logging_group.add_argument("--log-all-level", dest="log_all_level", type=str, required=False,
                                   help="sets the core and GUI logging level. If this parameter is provided, then "
                                        "--log-core-level and --log-gui-level are ignored.")
        logging_group.add_argument("--log-core-level", dest="log_core_level", type=str, default="INFO",
                                   help="sets the core logging level.")
        logging_group.add_argument("--log-gui-level", dest="log_gui_level", type=str, default="INFO",
                                   help="sets the GUI logging level.")
        logging_group.add_argument("--log-benchmark-level", dest="log_benchmark_level", type=str, default="INFO",
                                   help="sets the benchmark logging level.")

    def _build_status(self, args: Namespace) -> LiviaStatus:
        if args.open:
            input_frame = FileFrameInput(args.open.name)
            frame_size = input_frame.get_frame_size()
        else:
            input_frame = NoFrameInput()
            frame_size = (800, 600)

        window_size = (frame_size[0] + 50, frame_size[1] + 100)
        return LiviaStatus(FrameProcessingStatus(input_frame, modification_persistence=args.modification_persistence,
                                                 analyzer_threads=args.frame_processor_threads),
                           DisplayStatus(window_size, status_message=f"Welcome to {self._app_name}"),
                           ShortcutStatus())

    def _build_window(self, livia_status: LiviaStatus) -> LiviaWindow:
        livia_window = LiviaWindow(livia_status)
        livia_window.setWindowTitle(self._app_name)

        return livia_window

    def _build_configuration(self, args: Namespace) -> ConfigurationStorage:
        return ConfigurationStorage(self._livia_window.status, args.config_file, not args.no_config,
                                    args.auto_update_config)

    def _configure_logs(self, args: Namespace) -> None:
        if args.log_all_level is not None:
            level = logging.getLevelName(args.log_all_level)
            LIVIA_LOGGER.setLevel(level)
            LIVIA_GUI_LOGGER.setLevel(level)
        else:
            LIVIA_LOGGER.setLevel(logging.getLevelName(args.log_core_level))
            LIVIA_GUI_LOGGER.setLevel(logging.getLevelName(args.log_gui_level))

        LIVIA_BENCHMARK_LOGGER.setLevel(args.log_benchmark_level)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(logging.Formatter(args.log_stdout_format))

        if args.log_all_stdout:
            LIVIA_LOGGER.addHandler(stdout_handler)
            LIVIA_GUI_LOGGER.addHandler(stdout_handler)
        else:
            if args.log_core_stdout:
                LIVIA_LOGGER.addHandler(stdout_handler)
            if args.log_gui_stdout:
                LIVIA_GUI_LOGGER.addHandler(stdout_handler)

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
                log_gui_format = args.log_gui_file_format

                if log_core_format != log_gui_format:
                    raise ValueError(f"Two different formats provided for the same logging file")

                log_all_file_format = log_core_format

            file_handler_all.setFormatter(logging.Formatter(log_all_file_format))

            fh[log_all_file_format] = (file_handler_all, log_all_file_format)

            LIVIA_LOGGER.addHandler(file_handler_all)
            LIVIA_GUI_LOGGER.addHandler(file_handler_all)
        else:
            if args.log_core_file is not None:
                file_core_handler = logging.FileHandler(
                    filename=args.log_core_file.name, mode="a", encoding=args.log_core_file.encoding
                )
                if args.log_core_file_format is not None:
                    file_core_handler.setFormatter(logging.Formatter(args.log_core_file_format))

                fh[args.log_core_file.name] = (file_core_handler, args.log_core_file_format)
                LIVIA_LOGGER.addHandler(file_core_handler)

            if args.log_gui_file is not None:
                if args.log_gui_file.name in fh:
                    logger, logging_format = fh[args.log_gui_file.name]
                    if args.log_gui_file_format is not None and args.log_gui_file_format != logging_format:
                        raise ValueError(f"Two different formats provided for the same logging file")

                    LIVIA_GUI_LOGGER.addHandler(logger)
                else:
                    file_gui_handler = logging.FileHandler(
                        filename=args.log_gui_file.name, mode="a", encoding=args.log_gui_file.encoding
                    )
                    if args.log_gui_file_format is not None:
                        file_gui_handler.setFormatter(logging.Formatter(args.log_gui_file_format))

                    fh[args.log_gui_file.name] = (file_gui_handler, args.log_gui_file_format)
                    LIVIA_GUI_LOGGER.addHandler(file_gui_handler)

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

    def parse_and_execute(self):
        args = self.parse_args()
        self._configure_logs(args)

        self._app = QApplication(["LiviaWindow"])

        livia_status = self._build_status(args)

        self._livia_window = self._build_window(livia_status)
        self._livia_window.adjustSize()

        self._configuration_storage = self._build_configuration(args)

        try:
            window_center = self._livia_window.rect().center()
            desktop = QApplication.desktop()
            screen_center = desktop.screen().rect().center()
            self._livia_window.move(screen_center - window_center)  # Centers window
        except RuntimeError:
            LIVIA_GUI_LOGGER.exception("Window could not be centered in the screen")

        self._livia_window.show()

        self._livia_window.status.video_stream_status.frame_processor.start()

        self._app.exit(self._app.exec_())
