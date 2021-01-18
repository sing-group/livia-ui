from livia.input.FrameInput import FrameInput
from livia.input.NoFrameInput import NoFrameInput
from livia.output.FrameOutput import FrameOutput
from livia.output.NoFrameOutput import NoFrameOutput
from livia.process.analyzer.AnalyzerFrameProcessor import AnalyzerFrameProcessor
from livia.process.analyzer.AsyncAnalyzerFrameProcessor import AsyncAnalyzerFrameProcessor
from livia.process.analyzer.FrameAnalyzer import FrameAnalyzer
from livia.process.analyzer.NoChangeFrameAnalyzer import NoChangeFrameAnalyzer
from livia.process.analyzer.listener.FrameAnalyzerChangeEvent import FrameAnalyzerChangeEvent
from livia.process.analyzer.listener.FrameAnalyzerChangeListener import FrameAnalyzerChangeListener
from livia.process.listener import build_listener
from livia.process.listener.EventListeners import EventListeners
from livia.process.listener.IOChangeEvent import IOChangeEvent
from livia.process.listener.IOChangeListener import IOChangeListener
from livia_ui.gui.status.listener.FrameProcessingStatusChangeEvent import FrameProcessingStatusChangeEvent
from livia_ui.gui.status.listener.FrameProcessingStatusChangeListener import FrameProcessingStatusChangeListener


class FrameProcessingStatus:
    def __init__(self,
                 frame_input: FrameInput = NoFrameInput(),
                 frame_output: FrameOutput = NoFrameOutput(),
                 live_frame_analyzer: FrameAnalyzer = NoChangeFrameAnalyzer(),
                 static_frame_analyzer: FrameAnalyzer = NoChangeFrameAnalyzer()):
        self._static_frame_analyzer: FrameAnalyzer = static_frame_analyzer
        self._listeners: EventListeners[FrameProcessingStatusChangeListener] =\
            EventListeners[FrameProcessingStatusChangeListener]()

        self._frame_processor: AnalyzerFrameProcessor = self._build_frame_processor(
            frame_input, frame_output, live_frame_analyzer)

    def _build_frame_processor(self, frame_input: FrameInput, frame_output: FrameOutput,
                               live_frame_analyzer: FrameAnalyzer) -> AnalyzerFrameProcessor:
        analyzer = AsyncAnalyzerFrameProcessor(frame_input, frame_output, live_frame_analyzer)

        analyzer.add_io_change_listener(
            build_listener(IOChangeListener, input_changed=self._on_input_changed,
                           output_changed=self._on_output_changed)
        )
        analyzer.add_frame_analyzer_change_listener(
            build_listener(FrameAnalyzerChangeListener, analyzer_changed=self._on_analyzer_changed)
        )
        return analyzer

    @property
    def frame_input(self) -> FrameInput:
        return self._frame_processor.input

    @frame_input.setter
    def frame_input(self, frame_input: FrameInput):
        self._frame_processor.input = frame_input

    @property
    def frame_output(self) -> FrameOutput:
        return self._frame_processor.output

    @frame_output.setter
    def frame_output(self, frame_output: FrameOutput):
        self._frame_processor.output = frame_output

    @property
    def live_frame_analyzer(self) -> FrameAnalyzer:
        return self._frame_processor.frame_analyzer

    @live_frame_analyzer.setter
    def live_frame_analyzer(self, frame_analyzer: FrameAnalyzer):
        self._frame_processor.frame_analyzer = frame_analyzer

    @property
    def static_frame_analyzer(self) -> FrameAnalyzer:
        return self._static_frame_analyzer

    @static_frame_analyzer.setter
    def static_frame_analyzer(self, frame_analyzer: FrameAnalyzer):
        if self._static_frame_analyzer != frame_analyzer:
            old = self._static_frame_analyzer
            self._static_frame_analyzer = frame_analyzer

            event = FrameProcessingStatusChangeEvent(self, self._static_frame_analyzer, old)
            for listener in self._listeners:
                listener.static_frame_analyzer_changed(event)

    @property
    def frame_processor(self) -> AnalyzerFrameProcessor:
        return self._frame_processor

    def add_frame_processing_status_change_listener(self, listener: FrameProcessingStatusChangeListener):
        self._listeners.append(listener)

    def remove_frame_processing_status_change_listener(self, listener: FrameProcessingStatusChangeListener):
        self._listeners.remove(listener)

    def has_frame_processing_status_change_listener(self, listener: FrameProcessingStatusChangeListener) -> bool:
        return listener in self._listeners

    def _on_input_changed(self, event: IOChangeEvent[FrameInput]):
        event = FrameProcessingStatusChangeEvent(self, event.new, event.old)

        for listener in self._listeners:
            listener.frame_input_changed(event)

    def _on_output_changed(self, event: IOChangeEvent[FrameOutput]):
        event = FrameProcessingStatusChangeEvent(self, event.new, event.old)

        for listener in self._listeners:
            listener.frame_output_changed(event)

    def _on_analyzer_changed(self, event: FrameAnalyzerChangeEvent):
        event = FrameProcessingStatusChangeEvent(self, event.new, event.old)

        for listener in self._listeners:
            listener.live_frame_analyzer_changed(event)
