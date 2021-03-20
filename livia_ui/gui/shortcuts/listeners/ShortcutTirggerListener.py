from livia.process.listener.EventListener import EventListener
from livia_ui.gui.shortcuts.listeners.ShortcutTriggerEvent import ShortcutTriggerEvent


class ShortcutTriggerListener(EventListener):
    def shortcut_triggered(self, event: ShortcutTriggerEvent) -> None:
        pass
