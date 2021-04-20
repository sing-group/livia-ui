from ast import literal_eval
from typing import List, Any
from typing import TextIO, Optional
from xml.etree.ElementTree import Element, SubElement, ParseError

from livia.process.analyzer.FrameAnalyzerManager import FrameAnalyzerManager
from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.configuration.FrameAnalyzerConfiguration import FrameAnalyzerConfiguration
from livia_ui.gui.status.FrameProcessingStatus import FrameProcessingStatus


class AnalyzerConfigurationStorage:
    def __init__(self, processing_status: FrameProcessingStatus):
        self._processing_status: FrameProcessingStatus = processing_status
        self._live_analyzer_configurations: List[FrameAnalyzerConfiguration] = []

    def load_configuration(self, configuration_root: Element) -> None:
        try:
            analyzers_root = configuration_root.find("analyzers")
            if analyzers_root is None:
                return

            live_analyzer_root = analyzers_root.find("live-analyzer")
            if live_analyzer_root is None:
                return

            configurations_root = live_analyzer_root.find("configurations")
            if configurations_root is None:
                return

            active_id = live_analyzer_root.get("active")

            for configuration in configurations_root:
                analyzer_id = configuration.get("analyzer-id")
                config_name = configuration.get("config-name")

                metadata = FrameAnalyzerManager.get_metadata_by_id(analyzer_id)

                params: List[(FrameAnalyzerPropertyMetadata, Any)] = []
                for param_read in configuration:
                    prop = metadata.get_property_by_id(param_read.get("id"))
                    prop_value = param_read.text

                    if prop is not None and prop_value is not None:
                        # TODO: generalize this
                        if prop.prop_type is TextIO or prop.prop_type is Optional[TextIO]:
                            value = open(prop_value, "r")
                        else:
                            try:
                                value = literal_eval(prop_value)
                            except SyntaxError:
                                value = prop_value
                        params.append((prop, value))
                self._live_analyzer_configurations.append(FrameAnalyzerConfiguration(config_name, analyzer_id, params))

            self._processing_status.set_live_analyzer_configurations(self._live_analyzer_configurations, int(active_id))
        except ParseError:
            LIVIA_GUI_LOGGER.exception("Error parsing analyzer configuration file")

    def save_configuration(self, configuration_root: Element) -> None:
        self._live_analyzer_configurations = self._processing_status.live_analyzer_configurations
        root = SubElement(configuration_root, "analyzers")
        live_configuration_write = SubElement(root, "live-analyzer")
        live_configuration_write.set("active", str(self._processing_status.active_live_analyzer_configuration_index))
        configurations_write = SubElement(live_configuration_write, "configurations")

        i = 0
        for configuration in self._live_analyzer_configurations:
            analyzer_configuration_write = SubElement(configurations_write, "live-analyzer-configuration")
            analyzer_configuration_write.set("id", str(i))
            analyzer_configuration_write.set("analyzer-id", configuration.analyzer_id)
            analyzer_configuration_write.set("config-name", configuration.configuration_name)

            for parameter in configuration.parameters:
                if not parameter[0].hidden:
                    if parameter[0].prop_type is TextIO or parameter[0].prop_type is Optional[TextIO]:
                        if parameter[0].default_value != parameter[1].name:
                            parameter_write = SubElement(analyzer_configuration_write, "parameter")
                            parameter_write.set("id", parameter[0].id)
                            parameter_write.text = parameter[1].name

                    elif parameter[0].default_value != parameter[1]:
                        parameter_write = SubElement(analyzer_configuration_write, "parameter")
                        parameter_write.set("id", parameter[0].id)
                        parameter_write.text = str(parameter[1])
            i += 1



