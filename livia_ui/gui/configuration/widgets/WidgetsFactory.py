from typing import Callable, List, Any

from PySide2.QtWidgets import QLabel, QWidget

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia.process.listener import build_listener
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.configuration.widgets.BoolWidgetFactory import BoolWidgetFactory
from livia_ui.gui.configuration.widgets.ColorWidgetFactory import ColorWidgetFactory
from livia_ui.gui.configuration.widgets.FloatWidgetFactory import FloatWidgetFactory
from livia_ui.gui.configuration.widgets.IntWidgetFactory import IntWidgetFactory
from livia_ui.gui.configuration.widgets.StringWidgetFactory import StringWidgetFactory
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory
from livia_ui.gui.configuration.widgets.listener.WidgetChangeListener import WidgetChangeListener


class WidgetsFactory:
    def __init__(self):
        self._widget_factories: List[WidgetFactory[Any]] = [StringWidgetFactory(),
                                                            IntWidgetFactory(),
                                                            FloatWidgetFactory(),
                                                            ColorWidgetFactory(),
                                                            BoolWidgetFactory()]

    def register_factory(self, widget_factory: WidgetFactory[Any]):
        self._widget_factories.append(widget_factory)

    def get_widget(self, prop: FrameAnalyzerPropertyMetadata, function: Callable, value = None) -> QWidget:
        if value is not None:
            actual_value = value
        else:
            actual_value = prop.default_value

        for factory in self._widget_factories:
            if factory.can_manage(actual_value):
                widget_wrapper = factory.build_widget(actual_value, prop)

                widget_wrapper.add_listener(build_listener(
                    WidgetChangeListener, value_changed=lambda event: function(prop, event.value())
                ))

                return widget_wrapper.widget

        widget = QLabel()
        widget.setText("Widget Not Defined")
        widget.setStyleSheet("font-weight: bold; color: red")
        LIVIA_GUI_LOGGER.exception("Widget not defined for data type: " + str(type(actual_value)))

        return widget
