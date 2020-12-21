from typing import Tuple

from livia.process.listener.EventListener import EventListener

from livia_ui.gui.status.listener.DisplayStatusChangeEvent import DisplayStatusChangeEvent


class DisplayStatusChangeListener(EventListener):
    def fullscreen_changed(self, event: DisplayStatusChangeEvent[bool]):
        pass

    def resizable_changed(self, event: DisplayStatusChangeEvent[bool]):
        pass

    def status_message_changed(self, event: DisplayStatusChangeEvent[str]):
        pass

    def window_size_changed(self, event: DisplayStatusChangeEvent[Tuple[int, int]]):
        pass

    def detect_objects_changed(self, event: DisplayStatusChangeEvent[bool]):
        pass
