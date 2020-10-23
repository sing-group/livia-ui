from livia.process.listener.EventListener import EventListener
from livia_ui.gui.status.listener.ShortcutStatusChangeEvent import ShortcutStatusChangeEvent


class ShortcutStatusChangeListener(EventListener):
    def toggle_video_changed(self, event: ShortcutStatusChangeEvent):
        pass

    def toggle_detection_changed(self, event: ShortcutStatusChangeEvent):
        pass

    def capture_image_changed(self, event: ShortcutStatusChangeEvent):
        pass

    def toggle_fullscreen_changed(self, event: ShortcutStatusChangeEvent):
        pass

    def toggle_resizable_changed(self, event: ShortcutStatusChangeEvent):
        pass
