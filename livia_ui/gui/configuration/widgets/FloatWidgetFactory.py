import re

from PySide2.QtWidgets import QLineEdit, QDoubleSpinBox

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory, WidgetWrapper


class FloatWidgetWrapper(WidgetWrapper[float]):
    def __init__(self, widget: QDoubleSpinBox):
        super(FloatWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        self._widget.valueChanged.connect(lambda new_value: self._notify_listeners(new_value))


class FloatWidgetFactory(WidgetFactory[float]):
    def can_manage(self, actual_value) -> bool:
        return type(actual_value) is float

    def build_widget(self, actual_value: float, prop: FrameAnalyzerPropertyMetadata) -> WidgetWrapper[float]:
        widget = QDoubleSpinBox()
        widget.setValue(actual_value)

        if prop.hints is not None:
            parameters = prop.hints.split('|')
            for param in parameters:
                pattern_range = '((\d*\.\d+)|(\d+)):((\d*\.\d+)|(\d+))'
                pattern_step = '(\d*\.\d+)'

                if re.match(pattern_range, param):
                    param = param.split(':')
                    widget.setRange(float(param[0]), float(param[1]))
                elif re.match(pattern_step, param):
                    widget.setSingleStep(float(param))
        else:
            widget.setRange(0, 1)
            widget.setSingleStep(0.01)

        return FloatWidgetWrapper(widget)
