from argparse import ArgumentParser, FileType

from PyQt5.QtWidgets import QApplication

from livia.input.FileFrameInput import FileFrameInput
from livia.input.NoFrameInput import NoFrameInput
from livia_ui.gui.LiviaWindow import LiviaWindow
from livia_ui.gui.status.DisplayStatus import DisplayStatus
from livia_ui.gui.status.FrameProcessingStatus import FrameProcessingStatus
from livia_ui.gui.status.LiviaStatus import LiviaStatus
from livia_ui.gui.status.ShortcutStatus import ShortcutStatus


class LiviaGuiArgumentParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_argument("--open", dest="open", type=FileType('r'), help="Opens a file when application is started")

    def parse_and_execute(self):
        args = self.parse_args()

        if args.open:
            input_frame = FileFrameInput(args.open.name)
            frame_size = input_frame.get_frame_size()
        else:
            input_frame = NoFrameInput()
            frame_size = (800, 600)

        window_size = (frame_size[0] + 50, frame_size[1] + 100)
        livia_status = LiviaStatus(FrameProcessingStatus(input_frame),
                                   DisplayStatus(window_size, status_message="Welcome to LIVIA"),
                                   ShortcutStatus())

        app = QApplication([LiviaWindow])

        main_window = LiviaWindow(livia_status)
        main_window.setWindowTitle("LIVIA")

        main_window.adjustSize()
        main_window.move(app.desktop().screen().rect().center() - main_window.rect().center())  # Centers window

        main_window.show()

        app.exit(app.exec_())
