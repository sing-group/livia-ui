from typing import Dict

from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction


class DefaultShortcutAction(ShortcutAction):
    QUIT = 0
    OPEN_FILE = 1
    OPEN_DEVICE = 2
    RELEASE_DEVICE = 3
    TOGGLE_PLAY = 1001
    TOGGLE_FULLSCREEN = 2001
    TOGGLE_HIDE_CONTROLS_FULLSCREEN = 2002
    TOGGLE_RESIZABLE = 2003
    TOGGLE_VIDEO_ANALYSIS = 3001
    ANALYZE_IMAGE = 3002
    CONFIGURE_VIDEO_ANALYZER = 10001
    CONFIGURE_IMAGE_ANALYZER = 10002
    CONFIGURE_SHORTCUTS = 10003

    def get_default_shortcut(self) -> str:
        return DEFAULT_SHORTCUTS[self]

    def get_label(self):
        return self.name[0] + self.name[1:].lower().replace("_", " ")

    def get_order(self) -> int:
        return self.value

    def get_group(self) -> str:
        return GROUPS[self]


DEFAULT_SHORTCUTS: Dict[ShortcutAction, str] = {
    DefaultShortcutAction.QUIT: "Ctrl+Q",
    DefaultShortcutAction.OPEN_FILE: "Ctrl+O",
    DefaultShortcutAction.OPEN_DEVICE: "Ctrl+D",
    DefaultShortcutAction.RELEASE_DEVICE: "Ctrl+R",
    DefaultShortcutAction.TOGGLE_PLAY: "P",
    DefaultShortcutAction.TOGGLE_FULLSCREEN: "F",
    DefaultShortcutAction.TOGGLE_HIDE_CONTROLS_FULLSCREEN: "M",
    DefaultShortcutAction.TOGGLE_RESIZABLE: "R",
    DefaultShortcutAction.TOGGLE_VIDEO_ANALYSIS: "V",
    DefaultShortcutAction.ANALYZE_IMAGE: "I",
    DefaultShortcutAction.CONFIGURE_VIDEO_ANALYZER: "Alt+V",
    DefaultShortcutAction.CONFIGURE_IMAGE_ANALYZER: "Alt+I",
    DefaultShortcutAction.CONFIGURE_SHORTCUTS: "Alt+S"
}

GROUPS: Dict[ShortcutAction, str] = {
    DefaultShortcutAction.QUIT: "File",
    DefaultShortcutAction.OPEN_FILE: "File",
    DefaultShortcutAction.OPEN_DEVICE: "File",
    DefaultShortcutAction.RELEASE_DEVICE: "File",
    DefaultShortcutAction.TOGGLE_PLAY: "Video",
    DefaultShortcutAction.TOGGLE_FULLSCREEN: "View",
    DefaultShortcutAction.TOGGLE_HIDE_CONTROLS_FULLSCREEN: "View",
    DefaultShortcutAction.TOGGLE_RESIZABLE: "View",
    DefaultShortcutAction.TOGGLE_VIDEO_ANALYSIS: "Analysis",
    DefaultShortcutAction.ANALYZE_IMAGE: "Analysis",
    DefaultShortcutAction.CONFIGURE_VIDEO_ANALYZER: "Configuration",
    DefaultShortcutAction.CONFIGURE_IMAGE_ANALYZER: "Configuration",
    DefaultShortcutAction.CONFIGURE_SHORTCUTS: "Configuration"
}
