from ast import literal_eval
from typing import List, Any, Callable
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
        self._static_analyzer_configurations: List[FrameAnalyzerConfiguration] = []

    def load_configuration(self, configuration_root: Element) -> None:
        self._load_analyzers_configuration(configuration_root,
                                           self._live_analyzer_configurations,
                                           self._processing_status.set_live_analyzer_configurations,
                                           "live-analyzer")
        self._load_analyzers_configuration(configuration_root,
                                           self._static_analyzer_configurations,
                                           self._processing_status.set_static_analyzer_configurations,
                                           "static-analyzer")

    def _load_analyzers_configuration(self,
                                      configuration_root: Element,
                                      configurations_list: List[FrameAnalyzerConfiguration],
                                      set_configurations_callback: Callable[[List[FrameAnalyzerConfiguration], int],
                                                                            None],
                                      label: str
                                      ) -> None:
        try:
            analyzers_root = configuration_root.find("analyzers")
            if analyzers_root is None:
                return

            live_analyzer_root = analyzers_root.find(label)
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
                configurations_list.append(FrameAnalyzerConfiguration(config_name, analyzer_id, params))

            if active_id is None or active_id == "None":
                set_configurations_callback(configurations_list, None)
            else:
                set_configurations_callback(configurations_list, int(active_id))
        except ParseError:
            LIVIA_GUI_LOGGER.exception("Error parsing analyzer configuration file, " + label + " section")

    def save_configuration(self, configuration_root: Element) -> None:
        root = SubElement(configuration_root, "analyzers")
        self._save_analyzer_configuration(root,
                                          self._processing_status.live_analyzer_configurations,
                                          self._processing_status.active_live_analyzer_configuration_index,
                                          "live-analyzer")
        self._save_analyzer_configuration(root,
                                          self._processing_status.static_analyzer_configurations,
                                          self._processing_status.active_static_analyzer_configuration_index,
                                          "static-analyzer")

    def _save_analyzer_configuration(self,
                                     configuration_root: Element,
                                     configurations: List[FrameAnalyzerConfiguration],
                                     index: int,
                                     label: str) -> None:
        self._live_analyzer_configurations = configurations
        live_configuration_write = SubElement(configuration_root, label)
        live_configuration_write.set("active", str(index))
        configurations_write = SubElement(live_configuration_write, "configurations")

        i = 0
        for configuration in self._live_analyzer_configurations:
            analyzer_configuration_write = SubElement(configurations_write, label + "-configuration")
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
