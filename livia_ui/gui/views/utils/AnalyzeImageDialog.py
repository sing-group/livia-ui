from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtWidgets import QDialog, QVBoxLayout

from livia_ui.gui.status.FrameProcessingStatus import FrameProcessingStatus
from livia_ui.gui.views.utils.ImagePanel import ImagePanel


class AnalyzeImageDialog(QDialog):
    def __init__(self, video_stream_status: FrameProcessingStatus, *args, **kwargs):
        super(AnalyzeImageDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle(QCoreApplication.translate(self.__class__.__name__, "Image Analysis"))
        self.setWindowModality(Qt.ApplicationModal)

        self._video_stream_status: FrameProcessingStatus = video_stream_status
        self._image_panel: ImagePanel = ImagePanel()

        layout = QVBoxLayout()
        layout.addWidget(self._image_panel)

        self.setLayout(layout)

    def open(self):
        super(AnalyzeImageDialog, self).open()
        self._analyze_image()

    def _analyze_image(self):
        frame_input = self._video_stream_status.frame_input
        frame = frame_input.get_current_frame()
        frame_index = frame_input.get_current_frame_index()

        if frame is not None and frame_index is not None:
            analyzer = self._video_stream_status.static_frame_analyzer

            modification = analyzer.analyze(frame_index, frame)

            frame_modified = modification.modify(frame_index, frame)

            self._image_panel.show_frame(frame_modified)
