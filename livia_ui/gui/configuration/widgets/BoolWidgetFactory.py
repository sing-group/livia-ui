from PySide2.QtWidgets import QLineEdit, QCheckBox

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory, WidgetWrapper


class BoolWidgetWrapper(WidgetWrapper[bool]):
    def __init__(self, widget: QLineEdit):
        super(BoolWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        self._widget.stateChanged.connect(lambda new_value: self._notify_listeners(True) if new_value > 0
                                          else self._notify_listeners(False))


class BoolWidgetFactory(WidgetFactory[bool]):
    def can_manage(self, actual_value) -> bool:
        return type(actual_value) is bool

    def build_widget(self, actual_value: bool, prop: FrameAnalyzerPropertyMetadata) -> WidgetWrapper[bool]:
        widget = QCheckBox()
        widget.setChecked(actual_value)

        return BoolWidgetWrapper(widget)
