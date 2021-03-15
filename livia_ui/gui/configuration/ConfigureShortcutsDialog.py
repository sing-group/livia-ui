from functools import partial
from typing import Dict, Set, Tuple

from PySide2.QtCore import QCoreApplication, Qt
from PySide2.QtGui import QKeySequence, QPalette
from PySide2.QtWidgets import QDialog, QWidget, QFormLayout, QDialogButtonBox, QVBoxLayout, QTabWidget, QLabel, \
    QKeySequenceEdit, QHBoxLayout, QMessageBox

from livia_ui.gui.shortcuts.ShortcutAction import ShortcutAction
from livia_ui.gui.status.ShortcutStatus import ShortcutStatus


class ConfigureShortcutsDialog(QDialog):
    def __init__(self, shortcut_status: ShortcutStatus, *args, **kwargs):
        super(ConfigureShortcutsDialog, self).__init__(*args, *kwargs)
        self.setWindowTitle(QCoreApplication.translate(self.__class__.__name__, "Configure Shortcuts"))
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumSize(600, 400)

        self._shortcut_status: ShortcutStatus = shortcut_status
        self._shortcuts: Dict[ShortcutAction, Tuple[str, ...]] = self._shortcut_status.shortcuts

        self._modifications: Dict[ShortcutAction, str] = {}

        layout = QVBoxLayout()
        tabs_layout = QTabWidget()

        self._tabs: Dict[str, QWidget] = {}

        for group in self._shortcut_status.get_groups():
            self._tabs[group] = QWidget()
            tabs_layout.addTab(self._tabs[group], group)

            form_layout = QFormLayout()
            form_layout.setRowWrapPolicy(QFormLayout.WrapLongRows)
            actions = self._shortcut_status.get_actions_by_group(group)
            for action in actions:
                label_action = QLabel(action.get_label())
                label_action.setMinimumWidth(150)

                label_active_shortcut = QLabel(self._shortcuts[action][0])
                label_active_shortcut.setObjectName(action.get_label())

                editor = QKeySequenceEdit()
                editor.setObjectName(action.get_label())
                editor.setMinimumWidth(200)

                row_layout = QHBoxLayout()
                row_layout.addWidget(label_active_shortcut, 0, Qt.AlignCenter)
                row_layout.addWidget(editor, 0, Qt.AlignRight)

                form_layout.addRow(label_action, row_layout)
                editor.keySequenceChanged.connect(partial(self._on_shortcut_changed, action))

            self._tabs[group].setLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Ok | QDialogButtonBox.Cancel
                                      | QDialogButtonBox.Apply)

        self._apply_button = button_box.button(QDialogButtonBox.Apply)
        self._apply_button.setEnabled(False)

        button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self._restore_defaults)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self._apply_button.clicked.connect(self._apply)

        layout.addWidget(tabs_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def open(self):
        self._update_labels()
        super(ConfigureShortcutsDialog, self).open()

    def accept(self):
        self._apply()
        super(ConfigureShortcutsDialog, self).accept()

    def _apply(self):
        for action in self._modifications:
            self._shortcut_status.set_keys(action, self._modifications[action])
            self._tabs[action.get_group()].findChild(QLabel, action.get_label()).setText(self._modifications[action])
        self.__clear_key_inputs_text()

        self.__update_internal_shortcuts()
        self._modifications.clear()
        self._apply_button.setEnabled(False)

    def _restore_defaults(self):
        message = QMessageBox()
        message.setIcon(QMessageBox.Warning)

        message.setWindowTitle("Restore Default Shortcuts")
        message.setText("All changes done will be removed. Do you want to continue?")
        message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        if message.exec_() == QMessageBox.Ok:
            self.__update_internal_shortcuts()
            self._modifications.clear()
            for shortcut in self._shortcuts:
                self._modifications[shortcut] = shortcut.get_default_shortcut()
            self._apply()

    def _on_shortcut_changed(self, action: ShortcutAction, key_sequence: QKeySequence):
        key_sequence = key_sequence.toString()

        for shortcut in self._shortcuts.values():
            if key_sequence in shortcut:
                self._tabs[action.get_group()].findChild(QKeySequenceEdit, action.get_label()).setStyleSheet(
                    'background-color: red')

                if action in self._modifications:
                    self._modifications.pop(action)

                if len(self._modifications) == 0:
                    self._apply_button.setEnabled(False)
                return None

            elif self._tabs[action.get_group()].findChild(QKeySequenceEdit, action.get_label()).palette().color(
                    QPalette.Background).name() == '#ff0000':
                self._tabs[action.get_group()].findChild(QKeySequenceEdit, action.get_label()).setStyleSheet(
                    'background-color: white')

        self._modifications[action] = key_sequence
        self._apply_button.setEnabled(True)

    def _update_labels(self):
        self.__update_internal_shortcuts()
        for action in self._shortcuts:
            self._tabs[action.get_group()].findChild(QLabel, action.get_label()).setText(self._shortcuts[action][0])

    def __update_internal_shortcuts(self):
        self._shortcuts = self._shortcut_status.shortcuts

    def __clear_key_inputs_text(self):
        for shortcut in self._shortcuts:
            self._tabs[shortcut.get_group()].findChild(QKeySequenceEdit, shortcut.get_label()).clear()
