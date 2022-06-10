from livia_ui.gui.LiviaGuiArgumentParser import LiviaGuiArgumentParser

# os.environ["QT_QPA_PLATFORM"] = "xcb"  # Solves OpenCV-PySide2

if __name__ == '__main__':
    parser = LiviaGuiArgumentParser()

    parser.parse_and_execute()
