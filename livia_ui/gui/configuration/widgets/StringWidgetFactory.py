from PySide2.QtWidgets import QLineEdit
from typing import Optional

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory, WidgetWrapper


class StringWidgetWrapper(WidgetWrapper[str]):
    def __init__(self, widget: QLineEdit):
        super(StringWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        self._widget.textChanged.connect(lambda new_value: self._notify_listeners(new_value))


class StringWidgetFactory(WidgetFactory[str]):
    def can_manage(self, prop: FrameAnalyzerPropertyMetadata) -> bool:
        return prop.prop_type is str

    def build_widget(self, prop: FrameAnalyzerPropertyMetadata, actual_value: Optional[str] = None) -> \
        WidgetWrapper[str]:
        value = prop.default_value if actual_value is None else actual_value

        if value is None:
            widget = QLineEdit()
        else:
            widget = QLineEdit(actual_value)

        return StringWidgetWrapper(widget)
