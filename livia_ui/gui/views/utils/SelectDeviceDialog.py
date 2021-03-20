from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtGui import QShowEvent
from PySide2.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QFormLayout, QLabel, QComboBox, \
    QWidget, QSizePolicy

from livia.input.DeviceFrameInput import Device
from livia_ui.gui.views.utils.DevicePanel import DevicePanel
from livia_ui.gui.views.utils.DeviceProvider import DeviceProvider


class SelectDeviceDialog(QDialog):
    def __init__(self, device_provider: DeviceProvider, *args, **kwargs):
        super(SelectDeviceDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle(QCoreApplication.translate(self.__class__.__name__, "Select device"))
        self.setWindowModality(Qt.ApplicationModal)

        form_panel = QWidget()
        form_layout = QFormLayout()
        self._device_combo_box: QComboBox = QComboBox()
        self._device_provider: DeviceProvider = device_provider

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
        self._list_devices()
        self._device_panel.play()
        super(SelectDeviceDialog, self).showEvent(event)

    def get_device(self) -> Device:
        return self._device_combo_box.currentData()

    def _on_device_changed(self, index: int):
        self._device_panel.change_device(self._device_combo_box.currentData())

    def _on_show(self):
        self._device_panel.stop()

    def _on_play(self):
        self._device_panel.play()

    def _list_devices(self):
        self._device_combo_box.clear()
        for device in self._device_provider.list():
            self._device_combo_box.addItem(device.name, device)
