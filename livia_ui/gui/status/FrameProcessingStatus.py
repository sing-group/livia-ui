from typing import List, Optional

from livia.input.FrameInput import FrameInput
from livia.input.NoFrameInput import NoFrameInput
from livia.output.FrameOutput import FrameOutput
from livia.output.NoFrameOutput import NoFrameOutput
from livia.process.analyzer.AnalyzerFrameProcessor import AnalyzerFrameProcessor
from livia.process.analyzer.AsyncAnalyzerFrameProcessor import AsyncAnalyzerFrameProcessor, \
    DEFAULT_MODIFICATION_PERSISTENCE, DEFAULT_NUM_THREADS
from livia.process.analyzer.FrameAnalyzer import FrameAnalyzer
from livia.process.analyzer.FrameAnalyzerManager import FrameAnalyzerManager
from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerMetadata
from livia.process.analyzer.NoChangeFrameAnalyzer import NoChangeFrameAnalyzer
from livia.process.analyzer.listener.FrameAnalyzerChangeEvent import FrameAnalyzerChangeEvent
from livia.process.analyzer.listener.FrameAnalyzerChangeListener import FrameAnalyzerChangeListener
from livia.process.listener import build_listener
from livia.process.listener.EventListeners import EventListeners
from livia.process.listener.IOChangeEvent import IOChangeEvent
from livia.process.listener.IOChangeListener import IOChangeListener
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.configuration.FrameAnalyzerConfiguration import FrameAnalyzerConfiguration
from livia_ui.gui.status.listener.FrameProcessingStatusChangeEvent import FrameProcessingStatusChangeEvent
from livia_ui.gui.status.listener.FrameProcessingStatusChangeListener import FrameProcessingStatusChangeListener


class FrameProcessingStatus:
    NO_CHANGE_LIVE_ANALYZER = NoChangeFrameAnalyzer()

    def __init__(self,
                 frame_input: FrameInput = NoFrameInput(),
                 frame_output: FrameOutput = NoFrameOutput(),
                 live_frame_analyzer: FrameAnalyzer = NoChangeFrameAnalyzer(),
                 static_frame_analyzer: FrameAnalyzer = NoChangeFrameAnalyzer(),
                 activate_live_analysis: bool = False,
                 modification_persistence: int = DEFAULT_MODIFICATION_PERSISTENCE,
                 analyzer_threads: int = DEFAULT_NUM_THREADS):
        self._static_frame_analyzer: FrameAnalyzer = static_frame_analyzer
        self._live_frame_analyzer: FrameAnalyzer = live_frame_analyzer

        self._listeners: EventListeners[FrameProcessingStatusChangeListener] = \
            EventListeners[FrameProcessingStatusChangeListener]()

        self._frame_processor: AnalyzerFrameProcessor = self._build_frame_processor(
            frame_input, frame_output,
            live_frame_analyzer if activate_live_analysis else FrameProcessingStatus.NO_CHANGE_LIVE_ANALYZER,
            modification_persistence, analyzer_threads
        )

        self._active_live_analyzer_configuration_index = None
        self._active_static_analyzer_configuration_index = None
        self._live_analyzer_configurations: List[FrameAnalyzerConfiguration] = []
        self._static_analyzer_configurations: List[FrameAnalyzerConfiguration] = []

    def _build_frame_processor(self, frame_input: FrameInput, frame_output: FrameOutput,
                               live_frame_analyzer: FrameAnalyzer,
                               modification_persistence: int,
                               analyzer_threads: int) -> AnalyzerFrameProcessor:
        analyzer = AsyncAnalyzerFrameProcessor(frame_input, frame_output, live_frame_analyzer,
                                               modification_persistence=modification_persistence,
                                               num_threads=analyzer_threads)

        analyzer.add_io_change_listener(
            build_listener(IOChangeListener,
                           input_changed=self._on_input_changed,
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
        return self._live_frame_analyzer

    @property
    def static_frame_analyzer(self) -> FrameAnalyzer:
        return self._static_frame_analyzer

    @property
    def frame_processor(self) -> AnalyzerFrameProcessor:
        return self._frame_processor

    @property
    def live_analyzer_configurations(self) -> List[FrameAnalyzerConfiguration]:
        return self._live_analyzer_configurations

    def set_live_analyzer_configurations(self, live_analyzer_configurations: List[FrameAnalyzerConfiguration],
                                         index_selected: Optional[int] = None):
        if live_analyzer_configurations is None or live_analyzer_configurations == []:
            self.deactivate_live_analysis()
        else:
            old = self._live_analyzer_configurations
            self._live_analyzer_configurations = live_analyzer_configurations
            event = FrameProcessingStatusChangeEvent(self, self._live_analyzer_configurations, old)
            self._listeners.notify(FrameProcessingStatusChangeListener.live_frame_analyzer_configurations_changed,
                                   event)
        if index_selected is not None:
            self.active_live_analyzer_configuration_index = index_selected

    @property
    def active_live_analyzer_configuration_index(self) -> Optional[int]:
        return self._active_live_analyzer_configuration_index

    @active_live_analyzer_configuration_index.setter
    def active_live_analyzer_configuration_index(self, index: Optional[int] = None):
        if index is None:
            self.deactivate_live_analysis()
        else:
            old = self._active_live_analyzer_configuration_index
            self._active_live_analyzer_configuration_index = index
            event = FrameProcessingStatusChangeEvent(self, self._active_live_analyzer_configuration_index, old)
            self._listeners.notify(FrameProcessingStatusChangeListener.live_frame_analyzer_configuration_index_changed,
                                   event)
            self._build_live_analyzer()

    @property
    def static_analyzer_configurations(self) -> List[FrameAnalyzerConfiguration]:
        return self._static_analyzer_configurations

    def set_static_analyzer_configurations(self, static_analyzer_configurations: List[FrameAnalyzerConfiguration],
                                           index_selected: Optional[int] = None):
        if static_analyzer_configurations is None or static_analyzer_configurations == []:
            self._static_frame_analyzer = NoChangeFrameAnalyzer()
        else:
            old = self._static_analyzer_configurations
            self._static_analyzer_configurations = static_analyzer_configurations
            event = FrameProcessingStatusChangeEvent(self, self._static_analyzer_configurations, old)
            self._listeners.notify(FrameProcessingStatusChangeListener.static_frame_analyzer_configurations_changed,
                                   event)
        if index_selected is not None:
            self.active_static_analyzer_configuration_index = index_selected

    @property
    def active_static_analyzer_configuration_index(self) -> Optional[int]:
        return self._active_static_analyzer_configuration_index

    @active_static_analyzer_configuration_index.setter
    def active_static_analyzer_configuration_index(self, index: Optional[int] = None):
        if index is None:
            self._static_frame_analyzer = NoChangeFrameAnalyzer()
        else:
            old = self._active_static_analyzer_configuration_index
            self._active_static_analyzer_configuration_index = index
            event = FrameProcessingStatusChangeEvent(self, self._active_static_analyzer_configuration_index, old)
            self._listeners.notify(
                FrameProcessingStatusChangeListener.static_frame_analyzer_configuration_index_changed,
                event)
            self._build_static_analyzer()

    def change_live_analysis_activation(self, activate: bool):
        if activate:
            self.activate_live_analysis()
        else:
            self.deactivate_live_analysis()

    def is_live_analysis_active(self) -> bool:
        return self._frame_processor.frame_analyzer != FrameProcessingStatus.NO_CHANGE_LIVE_ANALYZER

    def activate_live_analysis(self):
        if self._frame_processor.frame_analyzer != self._live_frame_analyzer:
            self._frame_processor.frame_analyzer = self._live_frame_analyzer

            event = FrameProcessingStatusChangeEvent(self, True, False)
            self._listeners.notify(FrameProcessingStatusChangeListener.live_frame_analyzer_activation_changed, event)

    def deactivate_live_analysis(self):
        if self._frame_processor.frame_analyzer != FrameProcessingStatus.NO_CHANGE_LIVE_ANALYZER:
            self._frame_processor.frame_analyzer = FrameProcessingStatus.NO_CHANGE_LIVE_ANALYZER

            event = FrameProcessingStatusChangeEvent(self, False, True)
            self._listeners.notify(FrameProcessingStatusChangeListener.live_frame_analyzer_activation_changed, event)

    def add_frame_processing_status_change_listener(self, listener: FrameProcessingStatusChangeListener):
        self._listeners.append(listener)

    def remove_frame_processing_status_change_listener(self, listener: FrameProcessingStatusChangeListener):
        self._listeners.remove(listener)

    def has_frame_processing_status_change_listener(self, listener: FrameProcessingStatusChangeListener) -> bool:
        return listener in self._listeners

    def _on_input_changed(self, event: IOChangeEvent[FrameInput]):
        event = FrameProcessingStatusChangeEvent(self, event.new, event.old)
        self._listeners.notify(FrameProcessingStatusChangeListener.frame_input_changed, event)

    def _on_output_changed(self, event: IOChangeEvent[FrameOutput]):
        event = FrameProcessingStatusChangeEvent(self, event.new, event.old)
        self._listeners.notify(FrameProcessingStatusChangeListener.frame_output_changed, event)

    def _on_analyzer_changed(self, event: FrameAnalyzerChangeEvent):
        if event.new != FrameProcessingStatus.NO_CHANGE_LIVE_ANALYZER:
            self._live_frame_analyzer = event.new

            change_event = FrameProcessingStatusChangeEvent(self, event.new, event.old)
            self._listeners.notify(FrameProcessingStatusChangeListener.live_frame_analyzer_changed, change_event)

        if event.new == FrameProcessingStatus.NO_CHANGE_LIVE_ANALYZER:
            activation_event = FrameProcessingStatusChangeEvent(self, False, True)
            self._listeners.notify(FrameProcessingStatusChangeListener.live_frame_analyzer_activation_changed,
                                   activation_event)
        elif event.old == FrameProcessingStatus.NO_CHANGE_LIVE_ANALYZER:
            activation_event = FrameProcessingStatusChangeEvent(self, True, False)
            self._listeners.notify(FrameProcessingStatusChangeListener.live_frame_analyzer_activation_changed,
                                   activation_event)

    def _build_live_analyzer(self):
        if self._active_live_analyzer_configuration_index < len(self._live_analyzer_configurations):
            analyzer_metadata: FrameAnalyzerMetadata = FrameAnalyzerManager.get_metadata_by_id(
                self._live_analyzer_configurations[self._active_live_analyzer_configuration_index].analyzer_id)

            if analyzer_metadata in FrameAnalyzerManager.list_analyzers():
                analyzer = analyzer_metadata.analyzer_class()

                if isinstance(self._live_frame_analyzer, analyzer_metadata.analyzer_class):
                    analyzer_old = self._live_frame_analyzer

                    for prop in analyzer_metadata.properties:
                        prop.set_value(analyzer, prop.get_value(analyzer_old))

                for prop in analyzer_metadata.properties:
                    for modified_prop in self._live_analyzer_configurations[
                        self._active_live_analyzer_configuration_index].parameters:
                        if modified_prop[0].id == prop.id:
                            prop.set_value(analyzer, modified_prop[1])

                if self.is_live_analysis_active():
                    # self._live_frame_analyzer will be updated in _on_analyzer_changed event
                    self._frame_processor.frame_analyzer = analyzer
                else:
                    old = self._live_frame_analyzer
                    self._live_frame_analyzer = analyzer

                    event = FrameProcessingStatusChangeEvent(self, self._live_frame_analyzer, old)
                    self._listeners.notify(FrameProcessingStatusChangeListener.live_frame_analyzer_changed, event)

            else:
                LIVIA_GUI_LOGGER.exception("Error Configuring live analyzer")
        else:
            LIVIA_GUI_LOGGER.exception("Error Live analyzer configuration not found")

    def _build_static_analyzer(self):
        if self._active_static_analyzer_configuration_index < len(self._static_analyzer_configurations):
            analyzer_metadata: FrameAnalyzerMetadata = FrameAnalyzerManager.get_metadata_by_id(
                self._static_analyzer_configurations[self._active_static_analyzer_configuration_index].analyzer_id)

            if analyzer_metadata in FrameAnalyzerManager.list_analyzers():
                analyzer = analyzer_metadata.analyzer_class()

                if isinstance(self._static_frame_analyzer, analyzer_metadata.analyzer_class):
                    analyzer_old = self._static_frame_analyzer

                    for prop in analyzer_metadata.properties:
                        prop.set_value(analyzer, prop.get_value(analyzer_old))

                for prop in analyzer_metadata.properties:
                    for modified_prop in self._static_analyzer_configurations[
                        self._active_static_analyzer_configuration_index].parameters:
                        if modified_prop[0].id == prop.id:
                            prop.set_value(analyzer, modified_prop[1])

                old = self._static_frame_analyzer
                self._static_frame_analyzer = analyzer

                event = FrameProcessingStatusChangeEvent(self, self._static_frame_analyzer, old)
                self._listeners.notify(FrameProcessingStatusChangeListener.static_frame_analyzer_changed, event)

            else:
                LIVIA_GUI_LOGGER.exception("Error Configuring static analyzer")
        else:
            LIVIA_GUI_LOGGER.exception("Error static analyzer configuration not found")
