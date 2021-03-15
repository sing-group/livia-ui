from livia.process.listener.EventListener import EventListener
from livia_ui.gui.configuration.widgets.listener.WidgetChangeEvent import WidgetChangeEvent


class WidgetChangeListener(EventListener):
    def value_changed(self, event: WidgetChangeEvent):
        pass
