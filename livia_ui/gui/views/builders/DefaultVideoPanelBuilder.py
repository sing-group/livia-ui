from typing import Optional

from PyQt5.QtCore import QThread
from PyQt5.QtGui import QImage
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
from livia_ui.gui.views.utils.VideoPanel import VideoPanel


class DefaultVideoPanelBuilder(VideoPanelBuilder):
    def __init__(self):
        super().__init__(True, QThread.HighPriority)
        self._video_panel: VideoPanel = None
        self._last_image: Optional[QImage] = None

        self._frame_output_callback: CallbackFrameOutput = CallbackFrameOutput(
            output_frame_callback=self._on_show_frame
        )

    def _build_widgets(self):
        self._parent.layout().addWidget(self._build_video_label())

    def _listen_livia(self):
        self._update_detect_objects(self._livia_status.display_status.detect_objects)

        self._add_frame_output_callback()

        self._livia_status.video_stream_status.add_frame_processing_status_change_listener(
            build_listener(FrameProcessingStatusChangeListener,
                           frame_output_changed=self._on_frame_output_changed
                           )
        )

        self._livia_status.display_status.add_display_status_change_listener(
            build_listener(DisplayStatusChangeListener,
                           detect_objects_changed=self._on_detect_objects_changed,
                           resizable_changed=self._on_resizable_changed)
        )

        self._livia_status.video_stream_status.frame_processor.add_process_change_listener(
            build_listener(ProcessChangeListener,
                           finished=self._on_stream_finished)
        )

    def _build_video_label(self) -> VideoPanel:
        self._video_panel = VideoPanel(self._livia_status.display_status.resizable, self._parent)
        self._video_panel.setObjectName("_video_panel__video_label")

        return self._video_panel

    def _add_frame_output_callback(self):
        frame_output = self._livia_status.video_stream_status.frame_output

        if isinstance(frame_output, CompositeFrameOutput) and frame_output.has_descendant(self._frame_output_callback):
            return

        self._livia_status.video_stream_status.frame_output = CompositeFrameOutput(
            self._frame_output_callback,
            self._livia_status.video_stream_status.frame_output
        )

    def _on_frame_output_changed(self, event: FrameProcessingStatusChangeEvent[FrameOutput]):
        if isinstance(event.old, CompositeFrameOutput):
            event.old.remove_output(self._frame_output_callback)

        self._add_frame_output_callback()

    def _on_show_frame(self, num_frame: int, frame: ndarray):
        if frame is not None:
            self._video_panel.show_frame(frame)
        else:
            self._video_panel.clear_frame()

    def _on_stream_finished(self, event: ProcessChangeEvent):
        self._video_panel.clear_frame()

    def _on_detect_objects_changed(self, event: DisplayStatusChangeEvent):
        self._update_detect_objects(event.value)

    def _on_resizable_changed(self, event: DisplayStatusChangeEvent):
        self._video_panel.set_image_resizable(event.value)

    def _update_detect_objects(self, active: bool):
        if active:
            # TODO Change FrameByFrameSquareFrameAnalyzer for user configured analyzer when setup display is integrated
            self._livia_status.video_stream_status.live_frame_analyzer = FrameByFrameSquareFrameAnalyzer()
        else:
            self._livia_status.video_stream_status.live_frame_analyzer = NoChangeFrameAnalyzer()
