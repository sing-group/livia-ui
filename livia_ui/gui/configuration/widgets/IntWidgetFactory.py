import re

from PySide2.QtWidgets import QLineEdit, QSpinBox

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory, WidgetWrapper


class IntWidgetWrapper(WidgetWrapper[int]):
    def __init__(self, widget: QSpinBox):
        super(IntWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        self._widget.valueChanged.connect(lambda new_value: self._notify_listeners(new_value))


class IntWidgetFactory(WidgetFactory[int]):
    def can_manage(self, actual_value) -> bool:
        return type(actual_value) is int

    def build_widget(self, actual_value: int, prop: FrameAnalyzerPropertyMetadata) -> WidgetWrapper[int]:
        widget = QSpinBox()
        widget.setValue(actual_value)

        if prop.hints is not None:
            pattern = '(\d+):(\d+)'
            results = re.findall(pattern, prop.hints)
            if len(results) > 0:
                widget.setRange(int(results[0][0]), int(results[0][1]))
        else:
            widget.setRange(0, 100)

        return IntWidgetWrapper(widget)
