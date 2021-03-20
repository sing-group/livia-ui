from livia.input.FrameInput import FrameInput
from livia.output.FrameOutput import FrameOutput
from livia.process.analyzer.FrameAnalyzer import FrameAnalyzer
from livia.process.listener.EventListener import EventListener
from livia_ui.gui.status.listener.FrameProcessingStatusChangeEvent import FrameProcessingStatusChangeEvent


class FrameProcessingStatusChangeListener(EventListener):
    def frame_input_changed(self, event: FrameProcessingStatusChangeEvent[FrameInput]) -> None:
        pass

    def frame_output_changed(self, event: FrameProcessingStatusChangeEvent[FrameOutput]) -> None:
        pass

    def live_frame_analyzer_changed(self, event: FrameProcessingStatusChangeEvent[FrameAnalyzer]) -> None:
        pass

    def static_frame_analyzer_changed(self, event: FrameProcessingStatusChangeEvent[FrameAnalyzer]) -> None:
        pass

    def live_frame_analyzer_activation_changed(self, event: FrameProcessingStatusChangeEvent[bool]):
        pass
