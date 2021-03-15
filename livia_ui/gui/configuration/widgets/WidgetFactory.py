from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any

from PySide2.QtWidgets import QWidget

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia.process.listener.EventListeners import EventListeners
from livia_ui.gui.configuration.widgets.listener.WidgetChangeEvent import WidgetChangeEvent
from livia_ui.gui.configuration.widgets.listener.WidgetChangeListener import WidgetChangeListener

T = TypeVar("T")


class WidgetWrapper(ABC, Generic[T]):
    def __init__(self, widget: QWidget):
        self._widget: QWidget = widget
        self._listen_widget()

        self._widget_change_listeners: EventListeners[WidgetChangeListener] = \
            EventListeners[WidgetChangeListener]()

    @property
    def widget(self) -> QWidget:
        return self._widget

    @abstractmethod
    def _listen_widget(self):
        raise NotImplementedError()

    def _notify_listeners(self, value: T):
        event = WidgetChangeEvent(value)
        for listener in self._widget_change_listeners:
            listener.value_changed(event)

    def add_listener(self, listener: WidgetChangeListener):
        self._widget_change_listeners.append(listener)


class WidgetFactory(ABC, Generic[T]):
    @abstractmethod
    def can_manage(self, actual_value: Any) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def build_widget(self, actual_value: T, prop: FrameAnalyzerPropertyMetadata) -> WidgetWrapper[T]:
        raise NotImplementedError()
