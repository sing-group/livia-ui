from PySide2.QtWidgets import QWidget
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

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
        self._widget_change_listeners.notify(WidgetChangeListener.value_changed, event)

    def add_listener(self, listener: WidgetChangeListener):
        self._widget_change_listeners.append(listener)


class WidgetFactory(ABC, Generic[T]):
    @abstractmethod
    def can_manage(self, prop: FrameAnalyzerPropertyMetadata) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def build_widget(self, prop: FrameAnalyzerPropertyMetadata, actual_value: Optional[T] = None) -> WidgetWrapper[T]:
        raise NotImplementedError()
