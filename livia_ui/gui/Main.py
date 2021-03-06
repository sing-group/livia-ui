import logging

from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.LiviaGuiArgumentParser import LiviaGuiArgumentParser

LIVIA_GUI_LOGGER.setLevel(logging.INFO)
LIVIA_GUI_LOGGER.addHandler(logging.StreamHandler())

# os.environ["QT_QPA_PLATFORM"] = "xcb"  # Solves OpenCV-PySide2

if __name__ == '__main__':
    parser = LiviaGuiArgumentParser()

    parser.parse_and_execute()
