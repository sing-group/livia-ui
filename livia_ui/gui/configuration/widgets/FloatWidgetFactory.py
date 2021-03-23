import re
from PySide2.QtWidgets import QDoubleSpinBox
from typing import Optional

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory, WidgetWrapper


class FloatWidgetWrapper(WidgetWrapper[float]):
    def __init__(self, widget: QDoubleSpinBox):
        super(FloatWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        self._widget.valueChanged.connect(lambda new_value: self._notify_listeners(new_value))


class FloatWidgetFactory(WidgetFactory[float]):
    __PATTERN_RANGE: str = "((\\d*\\.\\d+)|(\\d+)):((\\d*\\.\\d+)|(\\d+))"
    __PATTERN_STEP: str = "(\\d*\\.\\d+)"

    def can_manage(self, prop: FrameAnalyzerPropertyMetadata) -> bool:
        return prop.prop_type is float

    def build_widget(self, prop: FrameAnalyzerPropertyMetadata, actual_value: Optional[float] = None) -> \
        WidgetWrapper[float]:
        widget = QDoubleSpinBox()

        value = prop.default_value if actual_value is None else actual_value
        if value is not None:
            widget.setValue(value)

        widget.setRange(0, 1)
        widget.setSingleStep(0.01)

        for hint in prop.hints:
            if re.match(FloatWidgetFactory.__PATTERN_RANGE, hint):
                float_range = hint.split(':')
                widget.setRange(float(float_range[0]), float(float_range[1]))
            elif re.match(FloatWidgetFactory.__PATTERN_STEP, hint):
                widget.setSingleStep(float(hint))

        return FloatWidgetWrapper(widget)
