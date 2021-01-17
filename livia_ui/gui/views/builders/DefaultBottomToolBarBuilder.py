from typing import Dict

from PyQt5.QtCore import pyqtSignal, pyqtSlot

from livia.input.FrameInput import FrameInput
from livia.input.SeekableFrameInput import SeekableFrameInput
from livia.process.listener import build_listener
from livia_ui.gui.status.listener.FrameProcessingStatusChangeEvent import FrameProcessingStatusChangeEvent
from livia_ui.gui.status.listener.FrameProcessingStatusChangeListener import FrameProcessingStatusChangeListener
from livia_ui.gui.views.builders.BottomToolBarBuilder import BottomToolBarBuilder
from livia_ui.gui.views.utils.VideoBar import VideoBar


class DefaultBottomToolBarBuilder(BottomToolBarBuilder):
    _change_video_bar_visibility_signal: pyqtSignal = pyqtSignal(bool)

    def __init__(self):
        super().__init__(True)

        self._video_bar: VideoBar = None

    def _build_widgets(self):
        self._parent.layout().addWidget(self._build_video_bar())

    def _register_signals(self) -> Dict[str, pyqtSignal]:
        return {
            "_change_video_bar_visibility_signal":
                (self._change_video_bar_visibility_signal, self._on_change_video_bar_visibility_signal)
        }

    def _listen_livia(self):
        self._livia_status.video_stream_status.add_frame_processing_status_change_listener(
            build_listener(FrameProcessingStatusChangeListener,
                           frame_input_changed=self._on_frame_input_changed,
                           )
        )

    def _after_init(self):
        visible = isinstance(self._livia_status.video_stream_status.frame_input, SeekableFrameInput)
        self._emit_change_video_bar_visibility_signal(visible)

    def _build_video_bar(self):
        frame_processor = self._livia_status.video_stream_status.frame_processor
        self._video_bar = VideoBar(frame_processor, self._parent)
        self._video_bar.setContentsMargins(0, 0, 0, 0)

        return self._video_bar

    @pyqtSlot(bool)
    def _on_change_video_bar_visibility_signal(self, visible: bool):
        if self._video_bar.isVisible() != visible:
            self._video_bar.setVisible(visible)

    def _on_frame_input_changed(self, event: FrameProcessingStatusChangeEvent[FrameInput]):
        self._emit_change_video_bar_visibility_signal(isinstance(event.new, SeekableFrameInput))
