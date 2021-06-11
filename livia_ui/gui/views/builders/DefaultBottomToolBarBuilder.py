from __future__ import annotations

from typing import TYPE_CHECKING

from PySide2.QtCore import Signal, Slot
from PySide2.QtWidgets import QVBoxLayout

from livia.input.FrameInput import FrameInput
from livia.input.SeekableFrameInput import SeekableFrameInput
from livia.process.listener import build_listener
from livia_ui.gui.status.listener.DisplayStatusChangeEvent import DisplayStatusChangeEvent
from livia_ui.gui.status.listener.DisplayStatusChangeListener import DisplayStatusChangeListener
from livia_ui.gui.status.listener.FrameProcessingStatusChangeEvent import FrameProcessingStatusChangeEvent
from livia_ui.gui.status.listener.FrameProcessingStatusChangeListener import FrameProcessingStatusChangeListener
from livia_ui.gui.views.builders.BottomToolBarBuilder import BottomToolBarBuilder
from livia_ui.gui.views.builders.GuiBuilderFactory import GuiBuilderFactory
from livia_ui.gui.views.utils.VideoBar import VideoBar

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow


class DefaultBottomToolBarBuilder(BottomToolBarBuilder):
    _change_video_bar_visibility_signal: Signal = Signal(bool)

    @staticmethod
    def factory() -> GuiBuilderFactory[BottomToolBarBuilder]:
        class DefaultGuiBuilderFactory(GuiBuilderFactory[BottomToolBarBuilder]):
            def create_builder(self, *args, **kwargs) -> DefaultBottomToolBarBuilder:
                return DefaultBottomToolBarBuilder(*args, **kwargs)

        return DefaultGuiBuilderFactory()

    def __init__(self, livia_window: LiviaWindow, *args, **kwargs):
        super(DefaultBottomToolBarBuilder, self).__init__(livia_window, *args, **kwargs)

        self._video_bar: VideoBar = None

    def _build_widgets(self):
        self._parent_widget.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout(self._parent_widget)
        self._parent_widget.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._build_video_bar())

    def _connect_signals(self):
        self._change_video_bar_visibility_signal.connect(self._on_change_video_bar_visibility_signal)

    def _listen_livia(self):
        self._livia_status.video_stream_status.add_frame_processing_status_change_listener(
            build_listener(FrameProcessingStatusChangeListener,
                           frame_input_changed=self._on_frame_input_changed,
                           )
        )
        self._livia_status.display_status.add_display_status_change_listener(
            build_listener(DisplayStatusChangeListener,
                           fullscreen_changed=self._on_fullscreen_changed,
                           hide_controls_fullscreen_changed=self._on_hide_controls_fullscreen_changed
                           )
        )

    def _after_init(self):
        visible = isinstance(self._livia_status.video_stream_status.frame_input, SeekableFrameInput)
        self._change_video_bar_visibility_signal.emit(visible)

        display_status = self._livia_status.display_status
        if display_status.fullscreen and display_status.hide_controls_fullscreen:
            self._change_visibility(False)

    def _disconnect_signals(self):
        self._change_video_bar_visibility_signal.disconnect(self._on_change_video_bar_visibility_signal)

    def _build_video_bar(self):
        frame_processor = self._livia_status.video_stream_status.frame_processor
        self._video_bar = VideoBar(frame_processor, self._parent_widget)
        self._video_bar.setContentsMargins(0, 0, 0, 0)

        return self._video_bar

    @Slot(bool)
    def _on_change_video_bar_visibility_signal(self, visible: bool):
        self._video_bar.setVisible(visible)

    def _on_frame_input_changed(self, event: FrameProcessingStatusChangeEvent[FrameInput]):
        self._change_video_bar_visibility_signal.emit(isinstance(event.new, SeekableFrameInput))

    def _on_fullscreen_changed(self, event: DisplayStatusChangeEvent):
        self._change_visibility(not (event.value and self._livia_status.display_status.hide_controls_fullscreen))

    def _on_hide_controls_fullscreen_changed(self, event: DisplayStatusChangeEvent):
        self._change_visibility(not (event.value and self._livia_status.display_status.fullscreen))

    def _change_visibility(self, visible: bool):
        self._parent_widget.setVisible(visible)
        self._parent_widget.layout().update()

