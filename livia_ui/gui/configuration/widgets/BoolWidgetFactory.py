from PySide2.QtWidgets import QLineEdit, QCheckBox
from typing import Optional

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory, WidgetWrapper


class BoolWidgetWrapper(WidgetWrapper[bool]):
    def __init__(self, widget: QLineEdit):
        super(BoolWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        self._widget.stateChanged.connect(lambda new_value: self._notify_listeners(True) if new_value > 0
        else self._notify_listeners(False))


class BoolWidgetFactory(WidgetFactory[bool]):
    def can_manage(self, prop: FrameAnalyzerPropertyMetadata) -> bool:
        return prop.prop_type is bool

    def build_widget(self, prop: FrameAnalyzerPropertyMetadata, actual_value: Optional[bool] = None) -> WidgetWrapper[
        bool]:
        value = prop.default_value if actual_value is None else actual_value

        widget = QCheckBox()
        widget.setChecked(value is True)

        return BoolWidgetWrapper(widget)
