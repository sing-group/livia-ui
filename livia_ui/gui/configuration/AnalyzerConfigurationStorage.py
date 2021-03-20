from ast import literal_eval
from xml.etree.ElementTree import Element, SubElement, ParseError

from livia.process.analyzer.FrameAnalyzerManager import FrameAnalyzerManager
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.status.FrameProcessingStatus import FrameProcessingStatus
from livia_ui.gui.views.utils.FileDataType import FileDataType


class AnalyzerConfigurationStorage:
    def __init__(self, processing_status: FrameProcessingStatus):
        self._processing_status: FrameProcessingStatus = processing_status

    def load_configuration(self, configuration_root: Element) -> None:
        try:
            analyzers_root = configuration_root.find("analyzers")
            if analyzers_root is None:
                return

            live_analyzer_root = analyzers_root.find("live-analyzer")
            if live_analyzer_root is None:
                return

            analyzer_id = live_analyzer_root.get("id")

            metadata = FrameAnalyzerManager.get_metadata_by_id(analyzer_id)
            live_analyzer = metadata.analyzer_class()

            for property_read in live_analyzer_root:
                prop = metadata.get_property_by_id(property_read.get("id"))
                prop_value = property_read.text

                if prop_value is not None:
                    try:
                        if FileDataType.can_manage(prop_value):
                            setattr(live_analyzer, prop.name, FileDataType(prop_value))
                        else:
                            setattr(live_analyzer, prop.name, literal_eval(prop_value))
                    except SyntaxError:
                        setattr(live_analyzer, prop.name, prop_value)

            self._processing_status.live_frame_analyzer = live_analyzer
        except ParseError:
            LIVIA_GUI_LOGGER.exception("Error parsing analyzer configuration file")

    def save_configuration(self, configuration_root: Element) -> None:
        actual_analyzer = self._processing_status.live_frame_analyzer
        metadata = FrameAnalyzerManager.get_metadata_for(actual_analyzer)

        root = SubElement(configuration_root, "analyzers")
        live_configuration_write = SubElement(root, "live-analyzer")
        live_configuration_write.set("id", metadata.id)

        metadata = FrameAnalyzerManager.get_metadata_for(actual_analyzer)

        for prop in metadata.properties:
            if not prop.hidden:
                value = getattr(actual_analyzer, prop.name)
                if type(prop.default_value) is FileDataType:
                    if prop.default_value.path != value.path:
                        property_write = SubElement(live_configuration_write, "property")
                        property_write.set("id", prop.id)
                        property_write.text = str(value.path)
                elif prop.default_value != value:
                    property_write = SubElement(live_configuration_write, "property")
                    property_write.set("id", prop.id)
                    property_write.text = str(value)
