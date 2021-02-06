from queue import Queue
from threading import Lock
from typing import Optional

from PySide2.QtCore import Qt, Signal, Slot, QThread, QSize, QCoreApplication
from PySide2.QtGui import QResizeEvent, QImage, QPainter, QPaintEvent, QPixmap
from PySide2.QtWidgets import QSizePolicy, QWidget, QStyleOption
from numpy import ndarray

from livia_ui.gui.views.utils import convert_image_opencv_to_qt


class _ImageProcessingThread(QThread):
    update_image_signal: Signal = Signal(QPixmap)
    clear_image_signal: Signal = Signal()

    def __init__(self, resize_image: bool, size: QSize):
        super().__init__()

        self._queue: Queue = Queue()

        self._resize_image: bool = resize_image
        self._size: QSize = size

        self._last_image: Optional[QImage] = None

        self._running: bool = False
        self._lock: Lock = Lock()

    def run(self) -> None:
        self._running = True
        while self._running:
            image = self._queue.get(True)

            with self._lock:
                if isinstance(image, ndarray):
                    image = convert_image_opencv_to_qt(image)

                if isinstance(image, QImage):
                    self._last_image = image
                    i_size = self._last_image.size()
                    if self._resize_image and self._size != i_size:
                        resized_image = self._last_image.scaled(self._size.width(), self._size.height(),
                                                                Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    else:
                        resized_image = self._last_image

                    self.update_image_signal.emit(QPixmap.fromImage(resized_image))
                else:
                    self._last_image = None
                    self.clear_image_signal.emit()

    def stop(self):
        self._running = False
        self._queue.put(None)

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


class VideoPanel(QWidget):
    def __init__(self, resize_image: bool = True, *args, **kwargs):
        super(VideoPanel, self).__init__(*args, **kwargs)

        self._painter: QPainter = QPainter()
        self._image: Optional[QPixmap] = None
        self._resize_image: bool = resize_image

        self._no_image_text: str = QCoreApplication.translate(self.__class__.__name__, "No image")

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self._thread: _ImageProcessingThread = _ImageProcessingThread(resize_image, self.size())
        self._thread.start()
        self._thread.setPriority(QThread.HighPriority)
        self.moveToThread(self._thread)

        self._thread.update_image_signal.connect(self._on_update_image_signal)
        self._thread.clear_image_signal.connect(self._on_clear_image_signal)

    def paintEvent(self, event: QPaintEvent):
        rect = event.rect()
        event.accept()

        options: QStyleOption = QStyleOption()
        options.initFrom(self)

        self._painter.begin(self)
        self._painter.fillRect(rect, Qt.black)
        if self._image:
            image_rect = self._image.rect()
            image_rect.moveCenter(rect.center())
            self._painter.drawPixmap(image_rect, self._image)
        else:
            self._painter.setPen(Qt.white)
            self._painter.drawText(rect.center(), self._no_image_text)
        self._painter.end()

    @Slot(QPixmap)
    def _on_update_image_signal(self, image: QImage):
        self._image = image
        self.repaint()

    @Slot()
    def _on_clear_image_signal(self):
        self._image = None
        self.repaint()

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
