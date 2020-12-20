from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import cv2
from PyQt5.QtCore import QRect, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy
from numpy import ndarray
import numpy as np

from livia.output.CallbackFrameOutput import CallbackFrameOutput
from livia.output.CompositeFrameOutput import CompositeFrameOutput
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.views.builders.VideoPanelBuilder import VideoPanelBuilder

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow


class DefaultVideoPanelBuilder(VideoPanelBuilder):
    def __init__(self):
        self._main_window: LiviaWindow = None
        self._video_label: QLabel = None

    def build(self, main_window: LiviaWindow, panel: QWidget):
        self._main_window = main_window
        self._video_label = QLabel(panel)
        self._video_label.setMinimumSize(800, 600)
        self._video_label.setContentsMargins(0, 0, 0, 0)
        self._video_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._video_label.setAutoFillBackground(False)
        self._video_label.setText("")
        self._video_label.setObjectName("_video_panel__video_label")

        main_window.status.video_stream_status.frame_output = CompositeFrameOutput(
            CallbackFrameOutput(
                show_frame_callback=self._on_show_frame,
                close_callback=self._on_close
            ),
            main_window.status.video_stream_status.frame_output
        )

    def _on_show_frame(self, frame: ndarray):
        if frame is not None:
            if isinstance(self._video_label.parent(), QWidget):
                parent: QWidget = self._video_label.parent()
                if parent.size() != self._video_label.size():
                    self._video_label.resize(parent.size())

            frame = DefaultVideoPanelBuilder._resize_image(frame, self._video_label.size())
            image = DefaultVideoPanelBuilder._map_to_qimage(frame)

            self._video_label.setPixmap(QPixmap.fromImage(image))

    def _on_close(self):
        pass

    @staticmethod
    def _resize_image(image: ndarray, bounds: QSize) -> ndarray:
        border_vertical = 0
        border_horizontal = 0
        image_width = image.shape[0]
        image_height = image.shape[1]

        bounds_height = bounds.height()
        bounds_width = bounds.width()

        if (bounds_height / bounds_width) >= (image_width / image_height):
            border_vertical = int((((bounds_height / bounds_width) * image_height) - image_width) / 2)
        else:
            border_horizontal = int((((bounds_width / bounds_height) * image_width) - image_height) / 2)

        image = cv2.copyMakeBorder(image, border_vertical, border_vertical, border_horizontal, border_horizontal, cv2.BORDER_CONSTANT, 0)

        return cv2.resize(image, (bounds_width, bounds_height))

    @staticmethod
    def _map_to_qimage(image: ndarray) -> Optional[QImage]:
        if image is not None:
            try:
                assert (np.max(image) <= 255)
                image8 = image.astype(np.uint8, order='C', casting='unsafe')
                height, width, colors = image8.shape
                bytes_per_line = 3 * width

                image = QImage(image8.data, width, height, bytes_per_line, QImage.Format_RGB888)

                image = image.rgbSwapped()
                return image
            except AttributeError:
                LIVIA_GUI_LOGGER.error("Unknown frame format")
                return None
        else:
            return None
