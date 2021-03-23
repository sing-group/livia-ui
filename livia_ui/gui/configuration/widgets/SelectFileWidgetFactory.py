import os
from PySide2.QtWidgets import QToolButton, QFileDialog
from io import open
from typing import Optional, TextIO

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetWrapper, WidgetFactory


class SelectFileWidgetWrapper(WidgetWrapper[TextIO]):
    def __init__(self, widget: QToolButton):
        super(SelectFileWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        self._widget.children()[0].fileSelected.connect(lambda new_path: self._notify_listeners(open(new_path, "r")))


class SelectFileWidgetFactory(WidgetFactory[TextIO]):
    def can_manage(self, prop: FrameAnalyzerPropertyMetadata) -> bool:
        return prop.prop_type is TextIO or prop.prop_type is Optional[TextIO]

    def build_widget(self, prop: FrameAnalyzerPropertyMetadata, actual_value: Optional[TextIO] = None) -> \
        WidgetWrapper[TextIO]:
        value = prop.default_value if actual_value is None else actual_value.name

        widget = QToolButton()
        widget.setMaximumWidth(300)
        widget.setPopupMode(QToolButton.InstantPopup)
        widget.setAutoRaise(False)

        file_filter = "Params Files (*.params)"
        file_widget = QFileDialog(parent=widget)
        file_widget.setWindowTitle("Select File")
        file_widget.setDefaultSuffix("params")
        file_widget.setNameFilters([file_filter])

        if value is not None:
            widget.setText(os.path.basename(value))
            widget.setToolTip(value)
            file_widget.setDirectory(os.path.dirname(value))

        widget.clicked.connect(lambda: file_widget.open())

        file_widget.fileSelected.connect(lambda new_path: widget.setText(new_path.split('/')[-1]))

        return SelectFileWidgetWrapper(widget)
