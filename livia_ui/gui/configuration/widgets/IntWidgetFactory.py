import re
from PySide2.QtWidgets import QSpinBox
from typing import Optional

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory, WidgetWrapper


class IntWidgetWrapper(WidgetWrapper[int]):
    def __init__(self, widget: QSpinBox):
        super(IntWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        self._widget.valueChanged.connect(lambda new_value: self._notify_listeners(new_value))


class IntWidgetFactory(WidgetFactory[int]):
    __PATTERN: str = "(\\d+):(\\d+)"

    def can_manage(self, prop: FrameAnalyzerPropertyMetadata) -> bool:
        return prop.prop_type is int

    def build_widget(self, prop: FrameAnalyzerPropertyMetadata, actual_value: Optional[int] = None) -> \
        WidgetWrapper[int]:
        widget = QSpinBox()
        value = prop.default_value if actual_value is None else actual_value
        if value is not None:
            widget.setValue(value)
            widget.setRange(0, max(100, value))
        else:
            widget.setRange(0, 100)

        for hint in prop.hints:
            match = re.match(IntWidgetFactory.__PATTERN, hint)
            if match is not None:
                widget.setRange(int(match[1]), int(match[2]))

        return IntWidgetWrapper(widget)
