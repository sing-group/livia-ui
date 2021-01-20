from threading import Condition
from typing import Optional

from PySide2.QtCore import QThread, Signal, Qt, Slot, QCoreApplication
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from cv2 import VideoCapture, cv2

from livia_ui.gui.views.utils import convert_image_opencv_to_qt


class _VideoThread(QThread):
    image_signal: Signal = Signal(QImage)

    def __init__(self, device_index: Optional[int] = None, autoplay: bool = False):
        super().__init__()
        self._device: VideoCapture = VideoCapture()
        self._device.setExceptionMode(True)

        self._device_index: Optional[int] = device_index

        self._finished: bool = False
        self._play: bool = autoplay
        self._condition: Condition = Condition()

    def run(self):
        while not self._finished:
            with self._condition:
                if self._finished:
                    break

                if self._play and self._device_index is not None:
                    try:
                        if not self._device.isOpened():
                            self._device.open(self._device_index)

                        ret, image = self._device.read()
                        if ret:
                            qimage = convert_image_opencv_to_qt(image)
                            if qimage:
                                self.image_signal.emit(qimage)
                            else:
                                self._condition.wait()
                        else:
                            self._condition.wait()
                    except cv2.error:
                        self._condition.wait()
                else:
                    self._condition.wait()

    def stop(self):
        if self._play:
            with self._condition:
                if self._play:
                    self._play = False
                    if self._device.isOpened():
                        self._device.release()
                    self._condition.notify()

    def play(self):
        if not self._play:
            with self._condition:
                if not self._play:
                    self._play = True
                    self._condition.notify()

    def destroy(self):
        if not self._finished:
            with self._condition:
                if not self._finished:
                    self._finished = True
                    if self._device.isOpened():
                        self._device.release()
                    self._condition.notify()

    def change_device(self, device_index: Optional[int]):
        with self._condition:
            if device_index is not None:
                self._device.open(device_index)
            self._condition.notify()


class DevicePanel(QWidget):
    def __init__(self, device_index: Optional[int] = None, autoplay: bool = True):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self._image_label = QLabel(self)
        self._image_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self._image_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self._image_label)

        self.setLayout(layout)

        self._thread: _VideoThread = _VideoThread(device_index, autoplay)
        self._thread.image_signal.connect(self._on_change_image_signal)
        self._thread.start()
        self._thread.setPriority(QThread.LowPriority)

        self.destroyed.connect(self._thread.stop)

    @Slot(QImage)
    def _on_change_image_signal(self, image: QImage):
        if image:
            image = image.scaled(self._image_label.width(), self._image_label.height(), Qt.KeepAspectRatio)
            self._image_label.setPixmap(QPixmap.fromImage(image))
        else:
            self._image_label.setPixmap(None)
            self._image_label.setText(QCoreApplication.translate(self.__class__.__name__, "No image"))

    def change_device(self, device_index: int):
        self._thread.change_device(device_index)

    def stop(self):
        self._thread.stop()

    def play(self):
        self._thread.play()
