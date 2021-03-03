import os
from argparse import ArgumentParser, FileType, Namespace

from PySide2.QtWidgets import QApplication

from livia.input.FileFrameInput import FileFrameInput
from livia.input.NoFrameInput import NoFrameInput
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.LiviaWindow import LiviaWindow
from livia_ui.gui.configuration.ConfigurationStorage import ConfigurationStorage
from livia_ui.gui.status.DisplayStatus import DisplayStatus
from livia_ui.gui.status.FrameProcessingStatus import FrameProcessingStatus
from livia_ui.gui.status.LiviaStatus import LiviaStatus
from livia_ui.gui.status.ShortcutStatus import ShortcutStatus

FILE_NAME = "configuration.xml"
FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, FILE_NAME))


class LiviaGuiArgumentParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(LiviaGuiArgumentParser, self).__init__(*args, **kwargs)

        self._app: QApplication = None
        self._livia_window: LiviaWindow = None
        self._configuration_storage: ConfigurationStorage = None

        self.add_argument("--open", dest="open", type=FileType('r'), help="Opens a file when application is started")

    def _build_status(self, args: Namespace) -> LiviaStatus:
        if args.open:
            input_frame = FileFrameInput(args.open.name)
            frame_size = input_frame.get_frame_size()
        else:
            input_frame = NoFrameInput()
            frame_size = (800, 600)

        window_size = (frame_size[0] + 50, frame_size[1] + 100)
        return LiviaStatus(FrameProcessingStatus(input_frame),
                           DisplayStatus(window_size, status_message="Welcome to LIVIA"),
                           ShortcutStatus())

    def _build_window(self, livia_status: LiviaStatus) -> LiviaWindow:
        livia_window = LiviaWindow(livia_status)
        livia_window.setWindowTitle("LIVIA")

        return livia_window

    def parse_and_execute(self):
        args = self.parse_args()

        self._app = QApplication(["LiviaWindow"])

        livia_status = self._build_status(args)

        self._livia_window = self._build_window(livia_status)
        self._livia_window.adjustSize()

        self._configuration_storage = ConfigurationStorage(livia_status, FILE_PATH)

        try:
            window_center = self._livia_window.rect().center()
            screen_center = self._app.desktop().screen().rect().center()
            self._livia_window.move(screen_center - window_center)  # Centers window
        except RuntimeError:
            LIVIA_GUI_LOGGER.exception("Window could not be centered in the screen")

        self._livia_window.show()

        self._livia_window.status.video_stream_status.frame_processor.start()

        self._app.exit(self._app.exec_())
