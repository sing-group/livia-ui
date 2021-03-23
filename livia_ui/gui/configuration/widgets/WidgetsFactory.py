from PySide2.QtWidgets import QLabel, QWidget
from typing import Callable, List, Any

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia.process.listener import build_listener
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.configuration.widgets.BoolWidgetFactory import BoolWidgetFactory
from livia_ui.gui.configuration.widgets.ColorWidgetFactory import ColorWidgetFactory
from livia_ui.gui.configuration.widgets.FloatWidgetFactory import FloatWidgetFactory
from livia_ui.gui.configuration.widgets.IntWidgetFactory import IntWidgetFactory
from livia_ui.gui.configuration.widgets.ListStringWidgetFactory import ListStringWidgetFactory
from livia_ui.gui.configuration.widgets.SelectFileWidgetFactory import SelectFileWidgetFactory
from livia_ui.gui.configuration.widgets.StringWidgetFactory import StringWidgetFactory
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory
from livia_ui.gui.configuration.widgets.listener.WidgetChangeListener import WidgetChangeListener


class WidgetsFactory:
    def __init__(self, default_factories: List[WidgetFactory[Any]] = [ListStringWidgetFactory(),
                                                                      SelectFileWidgetFactory(),
                                                                      ColorWidgetFactory(),
                                                                      StringWidgetFactory(),
                                                                      IntWidgetFactory(),
                                                                      FloatWidgetFactory(),
                                                                      BoolWidgetFactory()]):
        self._widget_factories: List[WidgetFactory[Any]] = default_factories

    def register_factory(self, widget_factory: WidgetFactory[Any]):
        self._widget_factories.append(widget_factory)

    def get_widget(self, prop: FrameAnalyzerPropertyMetadata,
                   function: Callable[[FrameAnalyzerPropertyMetadata, Any], None], value=None) -> QWidget:
        for factory in self._widget_factories:
            if factory.can_manage(prop):
                widget_wrapper = factory.build_widget(prop, value)

                widget_wrapper.add_listener(build_listener(
                    WidgetChangeListener, value_changed=lambda event: function(prop, event.value())
                ))

                return widget_wrapper.widget

        widget = QLabel()
        widget.setText("Widget Not Defined")
        widget.setStyleSheet("font-weight: bold; color: red")
        LIVIA_GUI_LOGGER.exception(f"Widget not defined for data type: {prop.prop_type}")

        return widget
