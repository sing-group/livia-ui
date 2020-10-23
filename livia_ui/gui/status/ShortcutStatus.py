from livia.process.listener.EventListeners import EventListeners
from livia_ui.gui.status.listener.ShortcutStatusChangeEvent import ShortcutStatusChangeEvent
from livia_ui.gui.status.listener.ShortcutStatusChangeListener import ShortcutStatusChangeListener

DEFAULT_TOGGLE_VIDEO_SHORTCUT = "P"
DEFAULT_TOGGLE_DETECTION_SHORTCUT = "D"
DEFAULT_CAPTURE_IMAGE_SHORTCUT = "C"
DEFAULT_TOGGLE_FULLSCREEN_SHORTCUT = "F"
DEFAULT_TOGGLE_RESIZABLE_SHORTCUT = "R"


class ShortcutStatus:
    def __init__(self,
                 toggle_video: str = DEFAULT_TOGGLE_VIDEO_SHORTCUT,
                 toggle_detection: str = DEFAULT_TOGGLE_DETECTION_SHORTCUT,
                 capture_image: str = DEFAULT_CAPTURE_IMAGE_SHORTCUT,
                 toggle_fullscreen: str = DEFAULT_TOGGLE_FULLSCREEN_SHORTCUT,
                 toggle_resizable: str = DEFAULT_TOGGLE_RESIZABLE_SHORTCUT):
        self._toggle_video: str = toggle_video
        self._toggle_detection: str = toggle_detection
        self._capture_image: str = capture_image
        self._toggle_fullscreen: str = toggle_fullscreen
        self._toggle_resizable: str = toggle_resizable

        self._listeners: EventListeners[ShortcutStatusChangeListener] = EventListeners[ShortcutStatusChangeListener]()

    @property
    def toggle_video(self) -> str:
        return self._toggle_video

    @toggle_video.setter
    def toggle_video(self, toggle_video: str):
        if self._toggle_video != toggle_video:
            old = self._toggle_video
            self._toggle_video = toggle_video

            event = ShortcutStatusChangeEvent(self, old, self._toggle_video)
            for listener in self._listeners:
                listener.toggle_video_changed(event)

    @property
    def toggle_detection(self) -> str:
        return self._toggle_detection

    @toggle_detection.setter
    def toggle_detection(self, toggle_detection: str):
        if self._toggle_detection != toggle_detection:
            old = self._toggle_detection
            self._toggle_detection = toggle_detection

            event = ShortcutStatusChangeEvent(self, old, self._toggle_detection)
            for listener in self._listeners:
                listener.toggle_detection_changed(event)

    @property
    def capture_image(self) -> str:
        return self._capture_image

    @capture_image.setter
    def capture_image(self, capture_image: str):
        if self._capture_image != capture_image:
            old = self._capture_image
            self._capture_image = capture_image

            event = ShortcutStatusChangeEvent(self, old, self._capture_image)
            for listener in self._listeners:
                listener.capture_image_changed(event)

    @property
    def toggle_fullscreen(self) -> str:
        return self._toggle_fullscreen

    @toggle_fullscreen.setter
    def toggle_fullscreen(self, toggle_fullscreen: str):
        if self._toggle_fullscreen != toggle_fullscreen:
            old = self._toggle_fullscreen
            self._toggle_fullscreen = toggle_fullscreen

            event = ShortcutStatusChangeEvent(self, old, self._toggle_fullscreen)
            for listener in self._listeners:
                listener.toggle_fullscreen_changed(event)

    @property
    def toggle_resizable(self) -> str:
        return self._toggle_resizable

    @toggle_resizable.setter
    def toggle_resizable(self, toggle_resizable: str):
        if self._toggle_resizable != toggle_resizable:
            old = self._toggle_resizable
            self._toggle_resizable = toggle_resizable

            event = ShortcutStatusChangeEvent(self, old, self._toggle_resizable)
            for listener in self._listeners:
                listener.toggle_resizable_changed(event)
