from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy
from numpy import ndarray

from livia.output.CallbackFrameOutput import CallbackFrameOutput
from livia.output.CompositeFrameOutput import CompositeFrameOutput
from livia.process.analyzer.FrameByFrameSquareFrameAnalyzer import FrameByFrameSquareFrameAnalyzer
from livia.process.analyzer.NoChangeFrameAnalyzer import NoChangeFrameAnalyzer
from livia.process.listener import build_listener
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.status.listener.DisplayStatusChangeEvent import DisplayStatusChangeEvent
from livia_ui.gui.status.listener.DisplayStatusChangeListener import DisplayStatusChangeListener
from livia_ui.gui.views.builders.VideoPanelBuilder import VideoPanelBuilder


class DefaultVideoPanelBuilder(VideoPanelBuilder):
    update_image_signal: pyqtSignal = pyqtSignal(QPixmap)
    clear_image_signal: pyqtSignal = pyqtSignal()

    def __init__(self):
        super().__init__(True, QThread.HighPriority)
        self._video_label: QLabel = None

    def _build(self):
        self._video_label = QLabel(self._parent)
        self._video_label.setMinimumSize(800, 600)
        self._video_label.setContentsMargins(0, 0, 0, 0)
        self._video_label.setAlignment(Qt.AlignCenter)
        self._video_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self._video_label.setAutoFillBackground(True)
        self._video_label.setText(self._translate("No image"))
        self._video_label.setObjectName("_video_panel__video_label")
        self._parent.layout().addWidget(self._video_label)

        self._update_detect_objects(self._livia_window.status.display_status.detect_objects)

        self.update_image_signal.connect(self._on_update_image_signal)
        self.clear_image_signal.connect(self._on_clear_image_signal)

        self._livia_window.status.video_stream_status.frame_output = CompositeFrameOutput(
            CallbackFrameOutput(
                show_frame_callback=self._on_show_frame,
                close_callback=self._on_close
            ),
            self._livia_window.status.video_stream_status.frame_output
        )

        self._livia_window.status.display_status.add_display_status_change_listener(
            build_listener(DisplayStatusChangeListener,
                           detect_objects_changed=self._on_detect_objects_changed)
        )

    @pyqtSlot(QPixmap)
    def _on_update_image_signal(self, image: QPixmap):
        self._video_label.setPixmap(image)

    @pyqtSlot()
    def _on_clear_image_signal(self):
        self._video_label.setPixmap(None)
        self._video_label.setText(self._translate("No image"))

    def _on_show_frame(self, frame: ndarray):
        if frame is not None:
            image = DefaultVideoPanelBuilder._map_to_qimage(frame)
            size = self._video_label.size()
            image = image.scaled(size.width(), size.height(), Qt.KeepAspectRatio)

            self.update_image_signal.emit(QPixmap.fromImage(image))
        else:
            self.clear_image_signal.emit()

    def _on_close(self):
        self.clear_image_signal.emit()

    def _on_detect_objects_changed(self, event: DisplayStatusChangeEvent):
        self._update_detect_objects(event.value)

    def _update_detect_objects(self, active: bool):
        if active:
            # TODO Change FrameByFrameSquareFrameAnalyzer for user configured analyzer when setup display is integrated
            self._livia_window.status.video_stream_status.live_frame_analyzer = FrameByFrameSquareFrameAnalyzer()
        else:
            self._livia_window.status.video_stream_status.live_frame_analyzer = NoChangeFrameAnalyzer()

    @staticmethod
    def _map_to_qimage(image: ndarray) -> Optional[QImage]:
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
