from typing import List

import cv2
from cv2 import VideoCapture

from livia_ui.gui.views.utils.Device import Device
from livia_ui.gui.views.utils.DeviceProvider import DeviceProvider


class DefaultDeviceProvider(DeviceProvider):

    def list(self) -> List[Device]:
        capture = VideoCapture()
        capture.setExceptionMode(True)

        index = 0
        devices = []
        while True:
            try:
                capture.open(index, cv2.CAP_VFW)
                devices.append(Device(f"Device {index}", index, cv2.CAP_VFW))
                capture.release()
                index += 1
            except cv2.error:
                break

        return devices
