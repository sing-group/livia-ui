from typing import Optional

from PySide2.QtCore import Qt, QCoreApplication, Signal, Slot
from PySide2.QtGui import QResizeEvent, QImage, QPixmap
from PySide2.QtWidgets import QLabel, QSizePolicy
from numpy import ndarray

from livia_ui.gui.views.utils import convert_image_opencv_to_qt


class ImagePanel(QLabel):
    _update_image_signal: Signal = Signal(QPixmap)
    _clear_image_signal: Signal = Signal()

    def __init__(self, resize_image: bool = True, *args, **kwargs):
        super(ImagePanel, self).__init__(*args, **kwargs)

        self._resize_image: bool = resize_image
        self._last_image: Optional[QImage] = None
        self._processing_text = QCoreApplication.translate(self.__class__.__name__, "Processing image...")

        self.setMinimumSize(800, 600)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setAutoFillBackground(True)
        self.setText(self._processing_text)

        self._update_image_signal.connect(self._on_update_image_signal)
        self._clear_image_signal.connect(self._on_clear_image_signal)

    @Slot(QPixmap)
    def _on_update_image_signal(self, image: QPixmap):
        self.setPixmap(image)

    @Slot()
    def _on_clear_image_signal(self):
        self.setText(self._processing_text)

    def resizeEvent(self, event: QResizeEvent):
        if self._resize_image:
            self.refresh_image()

    def is_image_resizable(self) -> bool:
        return self._resize_image

    def set_image_resizable(self, resizable: bool):
        if self._resize_image != resizable:
            self._resize_image = resizable
            self.refresh_image()

    def show_frame(self, frame: Optional[ndarray]):
        if frame is not None:
            self._last_image = convert_image_opencv_to_qt(frame)
            self._display_image(self._last_image)
        else:
            self._clear_image_signal.emit()

    def refresh_image(self):
        if self._last_image is not None:
            self._display_image(self._last_image)

    def clear_frame(self):
        self._clear_image_signal.emit()

    def _display_image(self, image: QImage):
        size = self.size()
        if self._resize_image and image.size() != size:
            image = image.scaled(size.width(), size.height(), Qt.KeepAspectRatio)

        self._update_image_signal.emit(QPixmap.fromImage(image))
