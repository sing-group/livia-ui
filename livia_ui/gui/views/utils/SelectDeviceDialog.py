from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QShowEvent
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QFormLayout, QLabel, QComboBox, \
    QHBoxLayout, QWidget, QSizePolicy

from livia_ui.gui.views.utils import list_devices
from livia_ui.gui.views.utils.DevicePanel import DevicePanel


class SelectDeviceDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(SelectDeviceDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle(QCoreApplication.translate(self.__class__.__name__, "Select device"))
        self.setWindowModality(Qt.ApplicationModal)

        form_panel = QWidget()
        form_layout = QFormLayout()
        self._device_combo_box: QComboBox = QComboBox()
        for index, device in list_devices().items():
            self._device_combo_box.addItem(device, index)
        form_layout.addRow(QLabel(QCoreApplication.translate(self.__class__.__name__, "Device:")),
                           self._device_combo_box)
        form_panel.setLayout(form_layout)

        self._device_panel: DevicePanel = DevicePanel(
            self._device_combo_box.currentData(), False
        )

        self._device_panel.setMinimumSize(600, 400)
        self._device_panel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(form_panel)
        layout.addWidget(self._device_panel)
        layout.addWidget(button_box)

        self.setLayout(layout)

        self._device_combo_box.currentIndexChanged.connect(self._on_device_changed)

    def hideEvent(self, event: QShowEvent):
        self._device_panel.stop()
        super(SelectDeviceDialog, self).hideEvent(event)

    def showEvent(self, event: QShowEvent):
        self._device_panel.play()
        super(SelectDeviceDialog, self).showEvent(event)

    def get_device(self) -> int:
        return self._device_combo_box.currentData()

    def _on_device_changed(self, index: int):
        self._device_panel.change_device(self._device_combo_box.currentData())

    def _on_show(self):
        self._device_panel.stop()

    def _on_play(self):
        self._device_panel.play()
