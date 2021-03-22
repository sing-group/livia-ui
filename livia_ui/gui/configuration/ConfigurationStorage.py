import os
import shutil
from typing import Optional
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from livia.process.listener import build_listener
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.configuration.AnalyzerConfigurationStorage import AnalyzerConfigurationStorage
from livia_ui.gui.configuration.ShortcutsConfigurationStorage import ShortcutsConfigurationStorage
from livia_ui.gui.status.LiviaStatus import LiviaStatus
from livia_ui.gui.status.listener.FrameProcessingStatusChangeListener import FrameProcessingStatusChangeListener
from livia_ui.gui.status.listener.ShortcutStatusChangeEvent import ShortcutStatusChangeEvent
from livia_ui.gui.status.listener.ShortcutStatusChangeListener import ShortcutStatusChangeListener


class ConfigurationStorage:
    def __init__(self, livia_status: LiviaStatus, configuration_file: str):
        self._livia_status: LiviaStatus = livia_status
        self._file_path: str = configuration_file

        self._configuration_root: Element = None
        self._shortcuts_configuration_root: Element = None
        self._analyzer_configuration_root: Element = None

        self._shortcuts_configuration: ShortcutsConfigurationStorage = \
            ShortcutsConfigurationStorage(self._livia_status.shortcut_status)
        self._analyzer_configuration: AnalyzerConfigurationStorage = \
            AnalyzerConfigurationStorage(self._livia_status.video_stream_status)

        self._read_configuration()

        self._listen_livia()

    def _listen_livia(self):
        self._livia_status.shortcut_status.add_shortcut_configuration_change_listener(
            build_listener(ShortcutStatusChangeListener,
                           shortcut_added=self._save_configuration,
                           shortcut_modified=self._save_configuration,
                           shortcut_removed=self._save_configuration
                           )
        )
        self._livia_status.video_stream_status.add_frame_processing_status_change_listener(
            build_listener(FrameProcessingStatusChangeListener,
                           live_frame_analyzer_changed=self._save_configuration)
        )

    def _read_configuration(self):
        try:
            self._configuration_root = ElementTree.parse(self._file_path).getroot()
            self._shortcuts_configuration_root = self._configuration_root.find("shortcuts")
            self._analyzer_configuration_root = self._configuration_root.find("analyzers")

            if self._shortcuts_configuration_root is not None:
                self._shortcuts_configuration.read_configuration(self._shortcuts_configuration_root)
            if self._analyzer_configuration_root is not None:
                self._analyzer_configuration.read_configuration(self._analyzer_configuration_root)
        except FileNotFoundError:
            LIVIA_GUI_LOGGER.exception("Configuration file '" + self._file_path + "' not found")
        except ElementTree.ParseError:
            LIVIA_GUI_LOGGER.exception("Error parsing configuration file '" + self._file_path + "'")

    def _save_configuration(self, event: Optional[ShortcutStatusChangeEvent] = None):
        configuration = ElementTree.Element("configuration")

        shortcuts = self._shortcuts_configuration.save_configuration()
        analyzer = self._analyzer_configuration.save_configuration()

        configuration.append(shortcuts)
        configuration.append(analyzer)

        datastr = ElementTree.tostring(configuration)
        file = open(self._file_path + '.new', "wb")
        file.write(datastr)
        file.close()

        shutil.copy(self._file_path + '.new', self._file_path)

        os.remove(self._file_path + '.new')