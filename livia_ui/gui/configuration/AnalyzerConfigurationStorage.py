import os
from ast import literal_eval
from xml.etree.ElementTree import Element, SubElement, ParseError

from livia.process.analyzer.FrameAnalyzerManager import FrameAnalyzerManager
from livia.process.analyzer.NoChangeFrameAnalyzer import NoChangeFrameAnalyzer
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.status.FrameProcessingStatus import FrameProcessingStatus
from livia_ui.gui.views.utils.FileDataType import FileDataType


class AnalyzerConfigurationStorage:
    def __init__(self, processing_status: FrameProcessingStatus):
        self._processing_status: FrameProcessingStatus = processing_status

    def save_configuration(self) -> Element:
        actual_analyzer = self._processing_status.live_frame_analyzer
        root = Element("analyzers")
        live_configuration_write = SubElement(root, "live-analyzer")
        live_configuration_write.set("class", str(actual_analyzer.__class__.__name__))

        metadata = FrameAnalyzerManager.get_metadata_for(actual_analyzer)

        for prop in metadata.properties:
            value = getattr(actual_analyzer, prop.name)
            if type(prop.default_value) is FileDataType:
                if not prop.hidden and prop.default_value.path != value.path:
                    property_write = SubElement(live_configuration_write, "property")
                    property_write.set("name", prop.name)
                    property_write.text = str(value.path)
            elif not prop.hidden and prop.default_value != value:
                property_write = SubElement(live_configuration_write, "property")
                property_write.set("name", prop.name)
                property_write.text = str(value)
        return root

    def read_configuration(self, configuration_root: Element):
        try:
            live_analyzer_root = configuration_root.find("live-analyzer")

            live_analyzer = NoChangeFrameAnalyzer()
            live_analyzer_properties = None

            for analyzer in FrameAnalyzerManager.list_analyzers():
                if analyzer.analyzer_class.__name__ == live_analyzer_root.get("class"):
                    live_analyzer = analyzer.analyzer_class()
                    live_analyzer_properties = analyzer.properties
                    break

            for prop_readed in live_analyzer_root:
                for prop in live_analyzer_properties:
                    if prop.hidden:
                        continue

                    if prop_readed.get("name") == prop.name:
                        if FileDataType.can_manage(prop_readed.text):
                            setattr(live_analyzer, prop.name, FileDataType(prop_readed.text))
                        else:
                            setattr(live_analyzer, prop.name, literal_eval(prop_readed.text))
                        break

            self._processing_status.live_frame_analyzer = live_analyzer

        except ParseError:
            LIVIA_GUI_LOGGER.exception("Error parsing analyzer configuration file")
