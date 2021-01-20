from typing import Optional, Dict

from PySide2.QtGui import QImage
from cv2 import VideoCapture, cv2
from numpy import ndarray

from livia_ui.gui import LIVIA_GUI_LOGGER


def convert_image_opencv_to_qt(image: ndarray) -> Optional[QImage]:
    if image is not None:
        try:
            height, width, colors = image.shape
            bytes_per_line = colors * width

            image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)

            return image.rgbSwapped()
        except AttributeError:
            LIVIA_GUI_LOGGER.error("Unknown frame format")
            return None
    else:
        return None


def list_devices() -> Dict[int, str]:
    capture = VideoCapture()
    capture.setExceptionMode(True)

    index = 0
    devices = {}
    while True:
        try:
            capture.open(index)
            devices[index] = f"Device {index}"
            capture.release()
            index += 1
        except cv2.error:
            break

    return devices
