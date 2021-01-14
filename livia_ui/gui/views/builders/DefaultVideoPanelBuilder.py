from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy
from numpy import ndarray

from livia.output.CallbackFrameOutput import CallbackFrameOutput
from livia.output.CompositeFrameOutput import CompositeFrameOutput
from livia.output.FrameOutput import FrameOutput
from livia.process.analyzer.FrameByFrameSquareFrameAnalyzer import FrameByFrameSquareFrameAnalyzer
from livia.process.analyzer.NoChangeFrameAnalyzer import NoChangeFrameAnalyzer
from livia.process.listener import build_listener
from livia.process.listener.ProcessChangeEvent import ProcessChangeEvent
from livia.process.listener.ProcessChangeListener import ProcessChangeListener
from livia_ui.gui.status.listener.DisplayStatusChangeEvent import DisplayStatusChangeEvent
from livia_ui.gui.status.listener.DisplayStatusChangeListener import DisplayStatusChangeListener
from livia_ui.gui.status.listener.FrameProcessingStatusChangeEvent import FrameProcessingStatusChangeEvent
from livia_ui.gui.status.listener.FrameProcessingStatusChangeListener import FrameProcessingStatusChangeListener
from livia_ui.gui.views.builders.VideoPanelBuilder import VideoPanelBuilder
from livia_ui.gui.views.utils import convert_image_opencv_to_qt


class DefaultVideoPanelBuilder(VideoPanelBuilder):
    _update_image_signal: pyqtSignal = pyqtSignal(QPixmap)
    _clear_image_signal: pyqtSignal = pyqtSignal()

    def __init__(self):
        super().__init__(True, QThread.HighPriority)
        self._video_label: QLabel = None

        self._frame_output_callback: CallbackFrameOutput = CallbackFrameOutput(
            output_frame_callback=self._on_show_frame
        )

    def _build_widgets(self):
        self._parent.layout().addWidget(self._build_video_label())

    def _connect_signals(self):
        self._update_image_signal.connect(self._on_update_image_signal)
        self._clear_image_signal.connect(self._on_clear_image_signal)

    def _listen_livia(self):
        self._update_detect_objects(self._livia_window.status.display_status.detect_objects)

        self._add_frame_output_callback()

        self._livia_window.status.video_stream_status.add_frame_processing_status_change_listener(
            build_listener(FrameProcessingStatusChangeListener,
                           frame_output_changed=self._on_frame_output_changed
                           )
        )

        self._livia_window.status.display_status.add_display_status_change_listener(
            build_listener(DisplayStatusChangeListener,
                           detect_objects_changed=self._on_detect_objects_changed)
        )

        self._livia_window.status.video_stream_status.frame_processor.add_process_change_listener(
            build_listener(ProcessChangeListener,
                           finished=self._on_stream_finished)
        )

    def _disconnect_signals(self):
        self._update_image_signal.disconnect(self._on_update_image_signal)
        self._clear_image_signal.disconnect(self._on_clear_image_signal)

    def _build_video_label(self):
        self._video_label = QLabel(self._parent)
        self._video_label.setMinimumSize(800, 600)
        self._video_label.setContentsMargins(0, 0, 0, 0)
        self._video_label.setAlignment(Qt.AlignCenter)
        self._video_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self._video_label.setAutoFillBackground(True)
        self._video_label.setText(self._translate("No image"))
        self._video_label.setObjectName("_video_panel__video_label")

        return self._video_label

    def _add_frame_output_callback(self):
        frame_output = self._livia_window.status.video_stream_status.frame_output

        if isinstance(frame_output, CompositeFrameOutput) and frame_output.has_descendant(self._frame_output_callback):
            return

        self._livia_window.status.video_stream_status.frame_output = CompositeFrameOutput(
            self._frame_output_callback,
            self._livia_window.status.video_stream_status.frame_output
        )

    @pyqtSlot(QPixmap)
    def _on_update_image_signal(self, image: QPixmap):
        self._video_label.setPixmap(image)

    @pyqtSlot()
    def _on_clear_image_signal(self):
        self._video_label.setText(self._translate("No image"))

    def _on_frame_output_changed(self, event: FrameProcessingStatusChangeEvent[FrameOutput]):
        if isinstance(event.old, CompositeFrameOutput):
            event.old.remove_output(self._frame_output_callback)

        self._add_frame_output_callback()

    def _on_show_frame(self, num_frame: int, frame: ndarray):
        if frame is not None:
            image = convert_image_opencv_to_qt(frame)
            size = self._video_label.size()
            image = image.scaled(size.width(), size.height(), Qt.KeepAspectRatio)

            self._update_image_signal.emit(QPixmap.fromImage(image))
        else:
            self._clear_image_signal.emit()

    def _on_stream_finished(self, event: ProcessChangeEvent):
        self._clear_image_signal.emit()

    def _on_detect_objects_changed(self, event: DisplayStatusChangeEvent):
        self._update_detect_objects(event.value)

    def _update_detect_objects(self, active: bool):
        if active:
            # TODO Change FrameByFrameSquareFrameAnalyzer for user configured analyzer when setup display is integrated
            self._livia_window.status.video_stream_status.live_frame_analyzer = FrameByFrameSquareFrameAnalyzer()
        else:
            self._livia_window.status.video_stream_status.live_frame_analyzer = NoChangeFrameAnalyzer()
