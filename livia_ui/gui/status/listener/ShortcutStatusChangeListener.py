from livia.process.listener import EventListener
from livia_ui.gui.status.listener.ShortcutStatusChangeEvent import ShortcutStatusChangeEvent


class ShortcutStatusChangeListener(EventListener):
    def shortcut_added(self, event: ShortcutStatusChangeEvent) -> None:
        pass

    def shortcut_modified(self, event: ShortcutStatusChangeEvent) -> None:
        pass

    def shortcut_removed(self, event: ShortcutStatusChangeEvent) -> None:
        pass
