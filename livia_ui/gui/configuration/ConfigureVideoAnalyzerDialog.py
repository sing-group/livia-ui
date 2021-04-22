import os
from typing import List, Callable, Optional

from PySide2.QtCore import QCoreApplication, Qt, Signal
from PySide2.QtGui import QIcon, QHideEvent, QCloseEvent
from PySide2.QtWidgets import QDialog, QVBoxLayout, QComboBox, QFormLayout, QDialogButtonBox, QLabel, QWidget, \
    QHBoxLayout, QToolButton, QLineEdit, QGroupBox, QMessageBox

from livia.process.analyzer.FrameAnalyzerManager import FrameAnalyzerManager
from livia.process.analyzer.FrameAnalyzerMetadata import FrameAnalyzerPropertyMetadata
from livia_ui.gui.configuration.FrameAnalyzerConfiguration import FrameAnalyzerConfiguration
from livia_ui.gui.configuration.widgets.WidgetsFactory import WidgetsFactory
from livia_ui.gui.views.utils.BorderLayout import BorderLayout


class ConfigureVideoAnalyzerDialog(QDialog):
    _index_changed_signal: Signal = Signal(int)
    _configurations_changed_signal = Signal(list, int)

    def __init__(self, *args, **kwargs):
        super(ConfigureVideoAnalyzerDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle(QCoreApplication.translate(self.__class__.__name__, "Configure Analyzer"))
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumSize(600, 400)

        self._widgets_factory = WidgetsFactory()

        self._configurations: List[FrameAnalyzerConfiguration] = None
        self._configurations_received: List[FrameAnalyzerConfiguration] = None
        self._active_configuration_index: int = None
        self._selected_configuration_index: int = None
        self._update_analyzer_configurations()

        self._updating_configurations_combo_box: bool = False
        self._signals_disconnected: bool = False

        self._modifications: FrameAnalyzerConfiguration = None

        layout = QVBoxLayout()

        self._configuration_name_edit: QLineEdit = None

        self._analyzer_combo_box: QComboBox = QComboBox()

        self._add_configuration_button = QToolButton()
        path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self._add_configuration_button.setIcon(QIcon(os.path.join(path, 'views/icons', 'add.svg')))
        self._add_configuration_button.clicked.connect(self._on_add_configuration)

        form_panel_top = QWidget()
        form_layout_top = QFormLayout()
        widgets_layout = QHBoxLayout()
        widgets_layout.addWidget(self._analyzer_combo_box)
        widgets_layout.addWidget(self._add_configuration_button)
        form_layout_top.addRow(QLabel(QCoreApplication.translate(self.__class__.__name__, "Analyzer:")),
                               widgets_layout)
        form_panel_top.setLayout(form_layout_top)

        self._group_box_layout = QGroupBox()
        form_panel = QWidget()
        form_panel.setContentsMargins(0, 17, 0, 0)
        self._form_layout = QFormLayout()
        border_layout = BorderLayout()

        border_layout.addWidget(form_panel, BorderLayout.Center)
        inner_button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Discard)
        border_layout.addWidget(inner_button_box, BorderLayout.South)

        self._save_changes_button = inner_button_box.button(QDialogButtonBox.Save)
        self._save_changes_button.setEnabled(False)
        self._remove_configuration_button = inner_button_box.button(QDialogButtonBox.Discard)

        self._group_box_layout.setLayout(border_layout)
        form_panel.setLayout(self._form_layout)

        self._form_layout.setRowWrapPolicy(QFormLayout.WrapLongRows)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)

        self._apply_button = button_box.button(QDialogButtonBox.Apply)
        self._apply_button.setText("Activate")
        self._apply_button.setEnabled(False)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self._apply_button.clicked.connect(self._activate_config)
        self._save_changes_button.clicked.connect(self._on_save_changes)
        self._remove_configuration_button.clicked.connect(self._on_remove_configuration)

        layout.addWidget(form_panel_top)
        layout.addWidget(self._group_box_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)

        self._analyzer_combo_box.currentIndexChanged.connect(self._on_analyzer_changed)

    def _update_configurations_combo_box(self):
        self._updating_configurations_combo_box = True
        self._analyzer_combo_box.clear()
        for analyzer in self._configurations:
            self._analyzer_combo_box.addItem(analyzer.configuration_name, analyzer)
        self._updating_configurations_combo_box = False

        if self._selected_configuration_index is not None:
            self._analyzer_combo_box.setCurrentIndex(self._selected_configuration_index)

    def _update_analyzer_configurations(self):
        if self._configurations_received is not None:
            self._configurations = self._configurations_received.copy()

    def _on_save_changes(self):
        for prop_saved in self._configurations[self._selected_configuration_index].parameters:
            if len(self._modifications.parameters) != 0 and prop_saved[0] in self._modifications.parameters[0]:
                self._configurations[self._selected_configuration_index].parameters.remove(prop_saved)
        for prop_configured in self._modifications.parameters:
            self._configurations[self._selected_configuration_index].parameters.append(
                (prop_configured[0], prop_configured[1]))

        self._configurations[self._selected_configuration_index].configuration_name = \
            self._modifications.configuration_name
        if self._is_current_analyzer_selected():
            self._configurations_changed_signal.emit(self._configurations,
                                                     self._selected_configuration_index)
        else:
            self._configurations_changed_signal.emit(self._configurations,
                                                     self._active_configuration_index)

        self._update_configurations_combo_box()
        self._save_changes_button.setEnabled(False)

    def _on_remove_configuration(self):
        message = QMessageBox()
        message.setIcon(QMessageBox.Warning)

        message.setWindowTitle("Remove configuration")
        message.setText("Removing configuration. Do you want to continue?")
        message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        if message.exec_() == QMessageBox.Ok:
            self._configurations.remove(self._configurations[self._selected_configuration_index])
            if self._is_current_analyzer_selected():
                self._configurations_changed_signal.emit(self._configurations, 0)
                self._analyzer_combo_box.removeItem(self._selected_configuration_index)
                self._selected_configuration_index = self._active_configuration_index = 0

            else:
                self._analyzer_combo_box.removeItem(self._selected_configuration_index)
                self._configurations_changed_signal.emit(self._configurations, self._active_configuration_index)
                self._selected_configuration_index = self._active_configuration_index

            self._update_configurations_combo_box()
            self._update_form()

    def accept(self):
        if self._apply_button.isEnabled():
            self._activate_config()
        super(ConfigureVideoAnalyzerDialog, self).accept()

    def open(self,
             configurations: List[FrameAnalyzerConfiguration],
             active_configuration_index: int,
             index_changed_callback: Callable[[int], None],
             configurations_changed_callback: Callable[[List[FrameAnalyzerConfiguration], int], None],
             window_title: Optional[str] = None):
        if window_title is not None:
            self.setWindowTitle(window_title)

        self._configurations_received = configurations
        self._active_configuration_index = active_configuration_index

        self._index_changed_signal.connect(index_changed_callback)
        self._configurations_changed_signal.connect(configurations_changed_callback)
        self._analyzer_combo_box.clear()
        self._update_analyzer_configurations()
        self._selected_configuration_index = self._active_configuration_index

        self._update_configurations_combo_box()
        self._update_form()

        self._signals_disconnected = False

        super(ConfigureVideoAnalyzerDialog, self).open()

    def hideEvent(self, event: QHideEvent):
        if not self._signals_disconnected:
            self._configurations_changed_signal.disconnect()
            self._index_changed_signal.disconnect()

            self._signals_disconnected = True

        self._configurations_received = None
        self._active_configuration_index = None

    def _activate_config(self):
        self._index_changed_signal.emit(self._selected_configuration_index)
        self._active_configuration_index = self._selected_configuration_index

        self._apply_button.setEnabled(False)
        self._update_analyzer_configurations()

    def _on_analyzer_changed(self, index: int):
        if not self._updating_configurations_combo_box:
            self._modifications = FrameAnalyzerConfiguration(self._configurations[index].configuration_name,
                                                             self._configurations[index].analyzer_id,
                                                             [])
            self._selected_configuration_index = index
            self._apply_button.setEnabled(not self._is_current_analyzer_selected())
            self._update_form()

    def _on_parameter_changed(self, prop_modified: FrameAnalyzerPropertyMetadata, new_value):
        for prop in self._modifications.parameters:
            if prop_modified.id == prop[0].id:
                self._modifications.parameters.remove(prop)
                break
        self._modifications.parameters.append((prop_modified, new_value))

        self._save_changes_button.setEnabled(len(self._modifications.parameters) != 0)

    def _on_configuration_name_changed(self, new_name: str):
        self._modifications.configuration_name = new_name
        self._save_changes_button.setEnabled(True)

    def _on_add_configuration(self):
        def accepted():
            if len(name_input.text()) < 1:
                name_input.setStyleSheet('background-color: red')
                return
            self._configurations.append(FrameAnalyzerConfiguration(name_input.text(),
                                                                   combo_box_model.currentData().id,
                                                                   []))
            self._selected_configuration_index = self._analyzer_combo_box.count()
            self._update_configurations_combo_box()
            self._save_changes_button.setEnabled(True)
            select_model_dialog.accept()

        select_model_dialog = QDialog()
        select_model_dialog.setWindowTitle(QCoreApplication.translate(self.__class__.__name__, "Select Model"))
        select_model_dialog.setMinimumSize(400, 200)
        layout = QVBoxLayout()

        layout.addWidget(QLabel(QCoreApplication.translate(self.__class__.__name__, "Configuration name")))
        name_input = QLineEdit()
        layout.addWidget(name_input)

        layout.addStretch()

        layout.addWidget(QLabel(QCoreApplication.translate(self.__class__.__name__, "Select Model:")))

        combo_box_model = QComboBox()
        for analyzer in FrameAnalyzerManager.list_analyzers():
            combo_box_model.addItem(analyzer.name, analyzer)
        layout.addWidget(combo_box_model)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        buttons.accepted.connect(accepted)
        buttons.rejected.connect(select_model_dialog.reject)
        layout.addStretch()
        layout.addWidget(buttons)

        select_model_dialog.setLayout(layout)
        select_model_dialog.exec_()

    def _update_form(self):
        for row_num in range(0, self._form_layout.rowCount()):
            self._form_layout.removeRow(0)

        if self._active_configuration_index in range(0, len(self._configurations)):
            current_analyzer = self._configurations[self._active_configuration_index]

        selected_analyzer: FrameAnalyzerConfiguration = self._analyzer_combo_box.currentData()
        if selected_analyzer is not None:
            self._configuration_name_edit = QLineEdit(selected_analyzer.configuration_name)
            self._configuration_name_edit.textChanged.connect(self._on_configuration_name_changed)
            row_layout = QHBoxLayout()
            row_layout.addStretch()
            row_layout.addWidget(self._configuration_name_edit, 0, Qt.AlignRight)
            self._form_layout.addRow("Configuration Name:", row_layout)

            metadata = FrameAnalyzerManager.get_metadata_by_id(selected_analyzer.analyzer_id)
            self._group_box_layout.setTitle(metadata.name)

            for prop in metadata.properties:
                property_data = None
                property_value = None
                for prop_readed in selected_analyzer.parameters:
                    if prop.id == prop_readed[0].id:
                        property_data = prop_readed[0]
                        property_value = prop_readed[1]
                        break

                if property_data is None:
                    property_data = prop
                    property_value = prop.default_value

                if property_data.hidden:
                    continue

                label = property_data.descriptive_name

                if self._is_current_analyzer_selected():
                    current_value = None
                    for param in current_analyzer.parameters:
                        if param[0] == property_data:
                            current_value = property_value
                            break

                    widget = self._widgets_factory.get_widget(property_data, self._on_parameter_changed, current_value)
                else:
                    if property_value is not None:
                        widget = self._widgets_factory.get_widget(property_data, self._on_parameter_changed,
                                                                  property_value)
                    else:
                        widget = self._widgets_factory.get_widget(property_data, self._on_parameter_changed)

                row_layout = QHBoxLayout()
                row_layout.addStretch()
                row_layout.addWidget(widget, 0, Qt.AlignRight)
                self._form_layout.addRow(label, row_layout)

            self._apply_button.setEnabled(not self._is_current_analyzer_selected())

    def _is_current_analyzer_selected(self) -> bool:
        return self._selected_configuration_index == self._active_configuration_index
