from xml.dom import minidom
from xml.etree import ElementTree

import os
import shutil
from typing import Optional, TextIO

from livia.process.listener import build_listener
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.configuration.AnalyzerConfigurationStorage import AnalyzerConfigurationStorage
from livia_ui.gui.configuration.ShortcutsConfigurationStorage import ShortcutsConfigurationStorage
from livia_ui.gui.status.LiviaStatus import LiviaStatus
from livia_ui.gui.status.listener.FrameProcessingStatusChangeListener import FrameProcessingStatusChangeListener
from livia_ui.gui.status.listener.ShortcutStatusChangeEvent import ShortcutStatusChangeEvent
from livia_ui.gui.status.listener.ShortcutStatusChangeListener import ShortcutStatusChangeListener


class ConfigurationStorage:
    def __init__(self,
                 livia_status: LiviaStatus,
                 configuration_file: Optional[TextIO],
                 load_configuration: bool = False,
                 auto_update: bool = True):
        self._livia_status: LiviaStatus = livia_status
        self._configuration_file: Optional[TextIO] = configuration_file

        self._shortcuts_configuration: ShortcutsConfigurationStorage = \
            ShortcutsConfigurationStorage(self._livia_status.shortcut_status)
        self._analyzer_configuration: AnalyzerConfigurationStorage = \
            AnalyzerConfigurationStorage(self._livia_status.video_stream_status)

        if configuration_file is not None:
            if load_configuration:
                self.load_configuration()

            if auto_update:
                self._livia_status.shortcut_status.add_shortcut_configuration_change_listener(
                    build_listener(ShortcutStatusChangeListener,
                                   shortcut_added=self._on_save_configuration,
                                   shortcut_modified=self._on_save_configuration,
                                   shortcut_removed=self._on_save_configuration
                                   )
                )
                self._livia_status.video_stream_status.add_frame_processing_status_change_listener(
                    build_listener(FrameProcessingStatusChangeListener,
                                   live_frame_analyzer_changed=self._on_save_configuration,
                                   live_frame_analyzer_configurations_changed=self._on_save_configuration,
                                   live_frame_analyzer_configuration_index_changed=self._on_save_configuration)
                )

    def _on_save_configuration(self, event: ShortcutStatusChangeEvent) -> None:
        self.save_configuration()

    def load_configuration(self, file: Optional[TextIO] = None) -> None:
        file = file if file is not None else self._configuration_file

        if file is None:
            raise FileNotFoundError("No file available to load configuration")

        try:
            configuration_root = ElementTree.parse(file).getroot()

            self._shortcuts_configuration.load_configuration(configuration_root)
            self._analyzer_configuration.load_configuration(configuration_root)
        except FileNotFoundError:
            LIVIA_GUI_LOGGER.exception(f"Configuration file '{file}' not found")
        except ElementTree.ParseError:
            LIVIA_GUI_LOGGER.exception(f"Error parsing configuration file '{file}'")

    def save_configuration(self, file: Optional[TextIO] = None) -> None:
        file = file if file is not None else self._configuration_file

        if file is None:
            raise FileNotFoundError("No file available to save configuration")

        configuration_root = ElementTree.Element("configuration")

        self._shortcuts_configuration.save_configuration(configuration_root)
        self._analyzer_configuration.save_configuration(configuration_root)

        tmp_file_name = file.name + ".new"
        with open(tmp_file_name, "wb") as tmp_file:
            encoding = "utf-8"
            xml = ElementTree.tostring(configuration_root, encoding=encoding)
            formatted_xml = minidom.parseString(xml).toprettyxml()
            tmp_file.write(formatted_xml.encode(encoding))

        shutil.copy(tmp_file_name, file.name)

        os.remove(tmp_file_name)
