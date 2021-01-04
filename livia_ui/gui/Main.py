import logging
import sys

from PyQt5.QtWidgets import QApplication

from livia.input.FileFrameInput import FileFrameInput
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.LiviaWindow import LiviaWindow
from livia_ui.gui.status.DisplayStatus import DisplayStatus
from livia_ui.gui.status.FrameProcessingStatus import FrameProcessingStatus
from livia_ui.gui.status.LiviaStatus import LiviaStatus
from livia_ui.gui.status.ShortcutStatus import ShortcutStatus

LIVIA_GUI_LOGGER.setLevel(logging.INFO)
LIVIA_GUI_LOGGER.addHandler(logging.StreamHandler())

if __name__ == '__main__':
    app = QApplication([LiviaWindow])

    input_frame = FileFrameInput(sys.argv[1])
    frame_size = input_frame.get_frame_size()

    window_size = (frame_size[0] + 50, frame_size[1] + 100)
    livia_status = LiviaStatus(FrameProcessingStatus(input_frame),
                               DisplayStatus(window_size, status_message="Welcome to LIVIA"),
                               ShortcutStatus())

    main_window = LiviaWindow(livia_status)
    main_window.setWindowTitle("LIVIA")

    main_window.adjustSize()
    main_window.move(app.desktop().screen().rect().center() - main_window.rect().center())  # Centers window

    main_window.show()

    app.exit(app.exec_())
