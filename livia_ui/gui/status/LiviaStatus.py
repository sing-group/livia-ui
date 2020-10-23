from livia_ui.gui.status.DisplayStatus import DisplayStatus
from livia_ui.gui.status.FrameProcessingStatus import FrameProcessingStatus
from livia_ui.gui.status.ShortcutStatus import ShortcutStatus


class LiviaStatus:
    def __init__(self, frame_processing_status: FrameProcessingStatus, display_status: DisplayStatus,
                 shortcut_status: ShortcutStatus):
        self._frame_processing_status: FrameProcessingStatus = frame_processing_status
        self._display_status: DisplayStatus = display_status
        self._shortcut_status: ShortcutStatus = shortcut_status

    @property
    def display_status(self) -> DisplayStatus:
        return self._display_status

    @property
    def shortcut_status(self) -> ShortcutStatus:
        return self._shortcut_status

    @property
    def video_stream_status(self) -> FrameProcessingStatus:
        return self._frame_processing_status
