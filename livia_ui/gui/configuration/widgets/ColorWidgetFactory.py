from typing import Tuple

from PySide2.QtGui import QColor
from PySide2.QtWidgets import QLineEdit, QToolButton, QColorDialog

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory, WidgetWrapper


class ColorWidgetWrapper(WidgetWrapper[Tuple[int, int, int]]):
    def __init__(self, widget: QToolButton):
        super(ColorWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        self._widget.children()[0].colorSelected.connect(lambda new_value: self._notify_listeners(
            (new_value.blue(), new_value.green(), new_value.red())))


class ColorWidgetFactory(WidgetFactory[Tuple[int, int, int]]):
    def can_manage(self, actual_value) -> bool:
        if type(actual_value) is tuple:
            for i in range(0, len(actual_value)):
                if type(actual_value[i]) is not int:
                    return False
            return True
        else:
            return False

    def build_widget(self, actual_value: Tuple[int, int, int], prop: FrameAnalyzerPropertyMetadata) -> \
            WidgetWrapper[Tuple[int, int, int]]:
        widget = QToolButton()
        widget.setPopupMode(QToolButton.InstantPopup)
        widget.setAutoRaise(False)
        widget.setStyleSheet('QToolButton{background-color: rgb(' + str(actual_value[2]) + ',' + str(actual_value[1]) + ',' +
                             str(actual_value[0]) + ');}')

        color_dialog = QColorDialog(parent=widget)
        color_dialog.setCurrentColor(QColor(actual_value[2], actual_value[1], actual_value[0]))

        color_dialog.colorSelected.connect(lambda: widget.setStyleSheet(
            'QToolButton{background-color: rgb(' + str(color_dialog.currentColor().red()) + ',' + str(
                color_dialog.currentColor().green()) + ',' +
            str(color_dialog.currentColor().blue()) + ');}'))

        widget.clicked.connect(lambda: color_dialog.exec_())

        return ColorWidgetWrapper(widget)
