import os

from PySide2.QtWidgets import QToolButton, QFileDialog

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetWrapper, WidgetFactory
from livia_ui.gui.views.utils.FileDataType import FileDataType


class SelectFileWidgetWrapper(WidgetWrapper[FileDataType]):
    def __init__(self, widget: QToolButton):
        super(SelectFileWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        self._widget.children()[0].fileSelected.connect(lambda new_path: self._notify_listeners(FileDataType(new_path)))


class SelectFileWidgetFactory(WidgetFactory[FileDataType]):
    def can_manage(self, actual_value) -> bool:
        return type(actual_value) is FileDataType

    def build_widget(self, actual_value: FileDataType, prop: FrameAnalyzerPropertyMetadata) -> \
            WidgetWrapper[FileDataType]:
        widget = QToolButton()
        widget.setMaximumWidth(300)
        widget.setPopupMode(QToolButton.InstantPopup)
        widget.setAutoRaise(False)
        widget.setText(actual_value.path.split('/')[-1])

        file_filter = "Params Files (*.params)"
        file_widget = QFileDialog(parent=widget)
        file_widget.setWindowTitle("Select File")
        file_widget.setDirectory(os.path.dirname(actual_value.path))
        file_widget.setDefaultSuffix('params')
        file_widget.setNameFilters([file_filter])

        widget.clicked.connect(lambda: file_widget.open())

        file_widget.fileSelected.connect(lambda new_path: widget.setText(new_path.split('/')[-1]))

        return SelectFileWidgetWrapper(widget)
