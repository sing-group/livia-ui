from PySide2.QtWidgets import QLineEdit

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory, WidgetWrapper


class StringWidgetWrapper(WidgetWrapper[str]):
    def __init__(self, widget: QLineEdit):
        super(StringWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        self._widget.textChanged.connect(lambda new_value: self._notify_listeners(new_value))


class StringWidgetFactory(WidgetFactory[str]):
    def can_manage(self, actual_value) -> bool:
        return type(actual_value) is str

    def build_widget(self, actual_value: str, prop: FrameAnalyzerPropertyMetadata) -> WidgetWrapper[str]:
        widget = QLineEdit(actual_value)

        return StringWidgetWrapper(widget)
