from queue import Queue
from threading import Lock
from typing import Optional

from PyQt5.QtCore import Qt, QCoreApplication, pyqtSignal, pyqtSlot, QThread, QSize
from PyQt5.QtGui import QResizeEvent, QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy
from numpy import ndarray

from livia_ui.gui.views.utils import convert_image_opencv_to_qt


class _ImageProcessingThread(QThread):
    update_image_signal: pyqtSignal = pyqtSignal(QPixmap)
    clear_image_signal: pyqtSignal = pyqtSignal()

    def __init__(self, resize_image: bool, size: QSize):
        super().__init__()

        self._queue: Queue = Queue()

        self._resize_image: bool = resize_image
        self._size: QSize = size

        self._last_image: Optional[QImage] = None

        self._lock: Lock = Lock()

    def run(self) -> None:
        while True:
            image = self._queue.get(True)

            with self._lock:
                if isinstance(image, ndarray):
                    image = convert_image_opencv_to_qt(image)

                if isinstance(image, QImage):
                    self._last_image = image
                    i_size = self._last_image.size()
                    if self._resize_image and self._size != i_size:
                        resized_image = self._last_image.scaled(self._size.width(), self._size.height(),
                                                                Qt.KeepAspectRatio)
                    else:
                        resized_image = self._last_image

                    self.update_image_signal.emit(QPixmap.fromImage(resized_image))
                else:
                    self._last_image = None
                    self.clear_image_signal.emit()

    def is_image_resizable(self) -> bool:
        return self._resize_image

    def set_image_size(self, size: QSize):
        if self._size != size:
            with self._lock:
                if self._size != size:
                    self._size = size
                    self._refresh_image()

    def set_image_resizable(self, resizable: bool):
        if self._resize_image != resizable:
            with self._lock:
                if self._resize_image != resizable:
                    self._resize_image = resizable
                    self._refresh_image()

    def clear_image(self):
        if self._last_image is not None:
            if self._lock:
                if self._last_image is not None:
                    self._last_image = None
                    self._refresh_image()

    def add_image(self, image: Optional[ndarray]):
        self._queue.put(image)

    def _refresh_image(self):
        self._queue.put(self._last_image)


class VideoPanel(QLabel):
    def __init__(self, resize_image: bool = True, *args, **kwargs):
        super(VideoPanel, self).__init__(*args, **kwargs)

        self.setMinimumSize(800, 600)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setAutoFillBackground(True)
        self.setText(QCoreApplication.translate(self.__class__.__name__, "No image"))

        self._thread: _ImageProcessingThread = _ImageProcessingThread(resize_image, self.size())
        self._thread.start()
        self._thread.setPriority(QThread.HighPriority)

        self._thread.update_image_signal.connect(self._on_update_image_signal)
        self._thread.clear_image_signal.connect(self._on_clear_image_signal)

    @pyqtSlot(QPixmap)
    def _on_update_image_signal(self, image: QPixmap):
        self.setPixmap(image)

    @pyqtSlot()
    def _on_clear_image_signal(self):
        self.setText(QCoreApplication.translate(self.__class__.__name__, "No image"))

    def resizeEvent(self, event: QResizeEvent):
        self._thread.set_image_size(event.size())

    def is_image_resizable(self) -> bool:
        return self._thread.is_image_resizable()

    def set_image_resizable(self, resizable: bool):
        self._thread.set_image_resizable(resizable)

    def show_frame(self, frame: Optional[ndarray]):
        self._thread.add_image(frame)

    def clear_frame(self):
        self._thread.clear_image()
