from typing import List

from PySide2.QtWidgets import QLineEdit

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory, WidgetWrapper


class ListStringWidgetWrapper(WidgetWrapper[List[str]]):
    def __init__(self, widget: QLineEdit):
        super(ListStringWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        def format_value(value: str) -> List[str]:
            return list(filter(None, value.replace(' ', '').replace('\'', '').replace('\"', '').split(',')))

        self._widget.textChanged.connect(lambda new_value: self._notify_listeners(format_value(new_value)))


class ListStringWidgetFactory(WidgetFactory[List[str]]):
    def can_manage(self, actual_value) -> bool:
        return type(actual_value) is list

    def build_widget(self, actual_value: List[str], prop: FrameAnalyzerPropertyMetadata) -> WidgetWrapper[List[str]]:
        widget = QLineEdit(str(actual_value)[1:-1].replace('\'', '').replace('\"', ''))

        return ListStringWidgetWrapper(widget)
