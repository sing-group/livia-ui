from typing import Dict, Tuple
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction
from livia_ui.gui.status.ShortcutStatus import ShortcutStatus


class ShortcutsConfiguration:
    def __init__(self, shortcut_status: ShortcutStatus):
        self._shortcut_status: ShortcutStatus = shortcut_status
        self._shortcuts: Dict[ShortcutAction, Tuple[str, ...]] = self._shortcut_status.shortcuts

    def save_configuration(self) -> Element:
        self._shortcuts = self._shortcut_status.shortcuts
        shortcuts_writed = ElementTree.Element("shortcuts")

        for shortcut in self._shortcuts:
            if self._shortcuts[shortcut][0] != shortcut.get_default_shortcut():
                shortcut_writed = ElementTree.SubElement(shortcuts_writed, "shortcut")
                shortcut_writed.set("name", shortcut.name)
                for keys in self._shortcuts[shortcut]:
                    combination = ElementTree.SubElement(shortcut_writed, "keys")
                    combination.text = keys

        return shortcuts_writed

    def read_configuration(self, configuration_root: Element):
        try:
            for shortcut_readed in configuration_root:
                keys = shortcut_readed.findall("keys")
                for shortcut in self._shortcuts:
                    if shortcut.name == shortcut_readed.attrib["name"]:
                        for key in keys:
                            self._shortcut_status.set_keys(shortcut, key.text)
                        break

        except ElementTree.ParseError:
            LIVIA_GUI_LOGGER.exception("Error parsing shortcuts configuration file")
