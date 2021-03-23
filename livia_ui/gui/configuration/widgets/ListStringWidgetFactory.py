import re
from PySide2.QtWidgets import QLineEdit
from typing import List, Optional

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory, WidgetWrapper


class ListStringWidgetWrapper(WidgetWrapper[List[str]]):
    def __init__(self, widget: QLineEdit):
        super(ListStringWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        def format_value(value: str) -> List[str]:
            return re.sub("[ '\"]", "", value).split(",")

        self._widget.textChanged.connect(lambda new_value: self._notify_listeners(format_value(new_value)))


class ListStringWidgetFactory(WidgetFactory[List[str]]):
    def can_manage(self, prop: FrameAnalyzerPropertyMetadata) -> bool:
        return prop.prop_type is List[str]

    def build_widget(self, prop: FrameAnalyzerPropertyMetadata, actual_value: Optional[List[str]] = None) -> \
        WidgetWrapper[List[str]]:
        value = prop.default_value if actual_value is None else actual_value

        if value is None:
            widget = QLineEdit()
        else:
            widget = QLineEdit(",".join(value))

        return ListStringWidgetWrapper(widget)
