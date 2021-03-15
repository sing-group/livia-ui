from typing import Dict, Any

from PySide2.QtCore import QCoreApplication, Qt
from PySide2.QtWidgets import QDialog, QVBoxLayout, QComboBox, QFormLayout, QDialogButtonBox, QLabel, QWidget, \
    QHBoxLayout

from livia.process.analyzer.FrameAnalyzerManager import FrameAnalyzerManager
from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.status.FrameProcessingStatus import FrameProcessingStatus
from livia_ui.gui.configuration.widgets.WidgetsFactory import WidgetsFactory


class ConfigureVideoAnalyzerDialog(QDialog):
    def __init__(self, frame_processing_status: FrameProcessingStatus, *args, **kwargs):
        super(ConfigureVideoAnalyzerDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle(QCoreApplication.translate(self.__class__.__name__, "Configure Video Analyzer"))
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumSize(600, 400)

        self._widgets_factory = WidgetsFactory()

        self._frame_processing_status = frame_processing_status
        self._modifications: Dict[FrameAnalyzerPropertyMetadata, Any] = {}

        layout = QVBoxLayout()

        self._analyzer_combo_box: QComboBox = QComboBox()

        form_panel_top = QWidget()
        form_layout_top = QFormLayout()
        form_layout_top.addRow(QLabel(QCoreApplication.translate(self.__class__.__name__, "Analyzer:")),
                               self._analyzer_combo_box)
        form_panel_top.setLayout(form_layout_top)

        for analyzer in FrameAnalyzerManager.list_analyzers():
            self._analyzer_combo_box.addItem(analyzer.name, analyzer)     

        form_panel = QWidget()
        self._form_layout = QFormLayout()
        form_panel.setLayout(self._form_layout)
        self._form_layout.setRowWrapPolicy(QFormLayout.WrapLongRows)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)

        self._apply_button = button_box.button(QDialogButtonBox.Apply)
        self._apply_button.setEnabled(False)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self._apply_button.clicked.connect(self._apply)

        layout.addWidget(form_panel_top)
        layout.addWidget(form_panel)
        layout.addStretch()
        layout.addWidget(button_box)

        self.setLayout(layout)

        self._update_form()

        self._analyzer_combo_box.currentIndexChanged.connect(self._on_analyzer_changed)

    def accept(self):
        if self._apply_button.isEnabled():
            self._apply()
        super(ConfigureVideoAnalyzerDialog, self).accept()
        
    def open(self):
        for analyzer in FrameAnalyzerManager.list_analyzers():
            if analyzer.analyzer_class is self._frame_processing_status.live_frame_analyzer.__class__:
                index = self._analyzer_combo_box.findData(analyzer)
                self._analyzer_combo_box.setCurrentIndex(index)
        super(ConfigureVideoAnalyzerDialog, self).open()

    def _apply(self):
        self._build_analyzer()
        self._modifications.clear()
        self._apply_button.setEnabled(False)

    def _on_analyzer_changed(self, index: int):
        self._update_form()
        self._modifications.clear()

    def _on_parameter_changed(self, prop: FrameAnalyzerPropertyMetadata, new_value):
        self._modifications[prop] = new_value
        self._apply_button.setEnabled(True)

    def _update_form(self):
        for row_num in range(0, self._form_layout.rowCount()):
            self._form_layout.removeRow(0)

        actual_analyzer = self._frame_processing_status.live_frame_analyzer

        for prop in self._analyzer_combo_box.currentData().properties:
            label = prop.descriptive_name

            if actual_analyzer.__class__ is self._analyzer_combo_box.currentData().analyzer_class and not prop.hidden:
                widget = self._widgets_factory.get_widget(prop, self._on_parameter_changed,
                                                          getattr(actual_analyzer, prop.name))
            elif not prop.hidden:
                widget = self._widgets_factory.get_widget(prop, self._on_parameter_changed)
            else:
                continue

            row_layout = QHBoxLayout()
            row_layout.addStretch()
            row_layout.addWidget(widget, 0, Qt.AlignRight)
            self._form_layout.addRow(label, row_layout)

        if actual_analyzer.__class__ is self._analyzer_combo_box.currentData().analyzer_class:
            self._apply_button.setEnabled(False)
        else:
            self._apply_button.setEnabled(True)

    def _build_analyzer(self):
        def arg(arg_id):
            return f"{arg_id}".replace("-", "_")

        if self._analyzer_combo_box.currentData() in FrameAnalyzerManager.list_analyzers():

            analyzer = self._analyzer_combo_box.currentData().analyzer_class()
            analyzer_metadata = self._analyzer_combo_box.currentData()

            for prop in analyzer_metadata.properties:
                for modified_prop in self._modifications:
                    if modified_prop == prop:
                        setattr(analyzer, arg(prop.id), self._modifications[modified_prop])

            self._frame_processing_status.live_frame_analyzer = analyzer
        else:
            LIVIA_GUI_LOGGER.exception("Error Configuring live analyzer")
