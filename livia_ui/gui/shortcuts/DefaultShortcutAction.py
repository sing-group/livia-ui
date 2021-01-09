from typing import Dict

from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction


class DefaultShortcutAction(ShortcutAction):
    OPEN_FILE = 1
    OPEN_DEVICE = 2
    TOGGLE_PLAY = 1001
    TOGGLE_FULLSCREEN = 2001
    TOGGLE_RESIZABLE = 2002
    CONFIGURE_SHORTCUTS = 3001
    CONFIGURE_DETECTOR = 10001
    TOGGLE_DETECTION = 10002
    CONFIGURE_CLASSIFIER = 20001
    CLASSIFY = 20002

    def get_default_shortcut(self) -> str:
        return DEFAULT_SHORTCUTS[self]


DEFAULT_SHORTCUTS: Dict[ShortcutAction, str] = {
    DefaultShortcutAction.OPEN_FILE: "Ctrl+O",
    DefaultShortcutAction.OPEN_DEVICE: "Ctrl+D",
    DefaultShortcutAction.TOGGLE_PLAY: "P",
    DefaultShortcutAction.TOGGLE_FULLSCREEN: "F",
    DefaultShortcutAction.TOGGLE_RESIZABLE: "R",
    DefaultShortcutAction.CONFIGURE_SHORTCUTS: "Alt+S",
    DefaultShortcutAction.CONFIGURE_DETECTOR: "Alt+D",
    DefaultShortcutAction.TOGGLE_DETECTION: "D",
    DefaultShortcutAction.CONFIGURE_CLASSIFIER: "Alt+C",
    DefaultShortcutAction.CLASSIFY: "C"
}
