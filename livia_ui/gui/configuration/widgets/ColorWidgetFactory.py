from PySide2.QtGui import QColor
from PySide2.QtWidgets import QToolButton, QColorDialog
from typing import Tuple, Optional

from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.widgets.WidgetFactory import WidgetFactory, WidgetWrapper


class ColorWidgetWrapper(WidgetWrapper[Tuple[int, int, int]]):
    def __init__(self, widget: QToolButton):
        super(ColorWidgetWrapper, self).__init__(widget)

    def _listen_widget(self):
        self._widget.children()[0].colorSelected.connect(lambda new_value: self._notify_listeners(
            (new_value.blue(), new_value.green(), new_value.red())))


class ColorWidgetFactory(WidgetFactory[Tuple[int, int, int]]):
    def can_manage(self, prop: FrameAnalyzerPropertyMetadata) -> bool:
        return prop.prop_type is Tuple[int, int, int]

    def build_widget(self,
                     prop: FrameAnalyzerPropertyMetadata,
                     actual_value: Optional[Tuple[int, int, int]] = None) -> WidgetWrapper[Tuple[int, int, int]]:
        widget = QToolButton()
        widget.setPopupMode(QToolButton.InstantPopup)
        widget.setAutoRaise(False)

        color_dialog = QColorDialog(parent=widget)

        value = prop.default_value if actual_value is None else actual_value
        if value is not None:
            widget.setStyleSheet(ColorWidgetFactory.__to_style_sheet(value[2], value[1], value[0]))
            color_dialog.setCurrentColor(QColor(value[2], value[1], value[0]))

        color_dialog.colorSelected.connect(lambda current_color: widget.setStyleSheet(
            ColorWidgetFactory.__to_style_sheet(current_color.red(), current_color.green(), current_color.blue())))

        widget.clicked.connect(lambda: color_dialog.exec_())

        return ColorWidgetWrapper(widget)

    @staticmethod
    def __to_style_sheet(red: int, green: int, blue: int) -> str:
        return f"QToolButton{{ background-color: rgb({red}, {green}, {blue}); }}"
