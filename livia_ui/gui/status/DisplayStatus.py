from typing import Tuple

from livia.process.listener.EventListeners import EventListeners
from livia_ui.gui.status.listener.DisplayStatusChangeEvent import DisplayStatusChangeEvent
from livia_ui.gui.status.listener.DisplayStatusChangeListener import DisplayStatusChangeListener


class DisplayStatus:
    def __init__(self,
                 window_size: Tuple[int, int] = (800, 600),
                 fullscreen: bool = False,
                 resizable: bool = True,
                 status_message: str = ""):
        self._window_size: Tuple[int, int] = window_size
        self._fullscreen: bool = fullscreen
        self._resizable: bool = resizable
        self._status_message: str = status_message

        self._listeners: EventListeners[DisplayStatusChangeListener] =\
            EventListeners[DisplayStatusChangeListener]()

    @property
    def window_size(self) -> Tuple[int, int]:
        return self._window_size

    @window_size.setter
    def window_size(self, window_size: Tuple[int, int]):
        if self._window_size != window_size:
            self._window_size = window_size

            event = DisplayStatusChangeEvent(self, self._window_size)
            for listener in self._listeners:
                listener.window_size_changed(event)

    @property
    def fullscreen(self) -> bool:
        return self._fullscreen

    @fullscreen.setter
    def fullscreen(self, fullscreen: bool):
        if self._fullscreen != fullscreen:
            self._fullscreen = fullscreen

            event = DisplayStatusChangeEvent(self, self._fullscreen)
            for listener in self._listeners:
                listener.fullscreen_changed(event)

    @property
    def resizable(self) -> bool:
        return self._resizable

    @resizable.setter
    def resizable(self, resizable: bool):
        if self._resizable != resizable:
            self._resizable = resizable

            event = DisplayStatusChangeEvent(self, self._resizable)
            for listener in self._listeners:
                listener.resizable_changed(event)

    @property
    def status_message(self) -> str:
        return self._status_message

    @status_message.setter
    def status_message(self, status_message: str):
        if self._status_message != status_message:
            self._status_message = status_message

            event = DisplayStatusChangeEvent(self, self._status_message)
            for listener in self._listeners:
                listener.status_message_changed(event)

    def add_display_status_change_listener(self, listener: DisplayStatusChangeListener):
        self._listeners.append(listener)

    def remove_display_status_change_listener(self, listener: DisplayStatusChangeListener):
        self._listeners.remove(listener)

    def has_display_status_change_listener(self, listener: DisplayStatusChangeListener) -> bool:
        return listener in self._listeners
