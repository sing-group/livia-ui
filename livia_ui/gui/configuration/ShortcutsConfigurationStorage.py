from xml.etree import ElementTree

from typing import Dict, Tuple
from xml.etree.ElementTree import Element

from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction
from livia_ui.gui.status.ShortcutStatus import ShortcutStatus


class ShortcutsConfigurationStorage:
    def __init__(self, shortcut_status: ShortcutStatus):
        self._shortcut_status: ShortcutStatus = shortcut_status
        self._shortcuts: Dict[ShortcutAction, Tuple[str, ...]] = self._shortcut_status.shortcuts

    def load_configuration(self, configuration_root: Element) -> None:
        try:
            shortcuts_element = configuration_root.find("shortcuts")
            if shortcuts_element is None:
                return

            for shortcut_read in shortcuts_element:
                keys = shortcut_read.findall("keys")
                for shortcut in self._shortcuts:
                    if shortcut.name == shortcut_read.attrib["name"]:
                        for key in keys:
                            if key.text is not None:
                                self._shortcut_status.set_keys(shortcut, key.text)
                        break

        except ElementTree.ParseError:
            LIVIA_GUI_LOGGER.exception("Error parsing shortcuts configuration file")

    def save_configuration(self, configuration_root: Element) -> None:
        self._shortcuts = self._shortcut_status.shortcuts
        shortcuts_written = ElementTree.Element("shortcuts")

        for shortcut in self._shortcuts:
            if self._shortcuts[shortcut][0] != shortcut.get_default_shortcut():
                shortcut_written = ElementTree.SubElement(shortcuts_written, "shortcut")
                shortcut_written.set("name", shortcut.name)
                for keys in self._shortcuts[shortcut]:
                    combination = ElementTree.SubElement(shortcut_written, "keys")
                    combination.text = keys

        configuration_root.append(shortcuts_written)
