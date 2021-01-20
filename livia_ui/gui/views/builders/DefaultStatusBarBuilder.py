import os

from PyQt5.QtCore import Qt, QSize, QTime, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QLabel, QToolButton, QTimeEdit, QAbstractSpinBox, QDateTimeEdit, \
    QWidget, QHBoxLayout

from livia.process.listener import build_listener
from livia.process.listener.ProcessChangeEvent import ProcessChangeEvent
from livia.process.listener.ProcessChangeListener import ProcessChangeListener
from livia_ui.gui.status.listener.DisplayStatusChangeEvent import DisplayStatusChangeEvent
from livia_ui.gui.status.listener.DisplayStatusChangeListener import DisplayStatusChangeListener
from livia_ui.gui.views.builders.StatusBarBuilder import StatusBarBuilder


class DefaultStatusBarBuilder(StatusBarBuilder):
    _update_status_signal: pyqtSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._status_label: QLabel = None
        self._recording_panel: QWidget = None
        self._record_button: QToolButton = None
        self._record_settings_button: QToolButton = None
        self._time_recording: QTimeEdit = None

    def _build_widgets(self):
        self._build_status_label()

        self._parent.addWidget(self._status_label)
        self._parent.addPermanentWidget(self._build_recording_panel())

    def _connect_signals(self):
        self._update_status_signal.connect(self._on_update_status_signal)

    def _listen_livia(self):
        self._livia_status.video_stream_status.frame_processor.add_process_change_listener(
            build_listener(ProcessChangeListener,
                           started=self._on_video_stream_started,
                           paused=self._on_video_stream_paused,
                           resumed=self._on_video_stream_resumed,
                           stopped=self._on_video_stream_stopped,
                           finished=self._on_video_stream_finished
                           )
        )

        self._livia_status.display_status.add_display_status_change_listener(
            build_listener(DisplayStatusChangeListener, status_message_changed=self._on_status_message_change)
        )

    def _disconnect_signals(self):
        self._update_status_signal.disconnect(self._on_update_status_signal)

    def _build_status_label(self):
        self._status_label = QLabel()
        self._status_label.setObjectName("_status_bar__status_label")
        self._status_label.setText(self._translate("Starting System"))

    def _build_recording_panel(self) -> QWidget:
        path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        self._recording_panel = QWidget()
        self._recording_panel.setObjectName("_status_bar__recording_panel")
        layout = QHBoxLayout(self._recording_panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._record_button = QToolButton()
        self._record_button.setObjectName("_status_bar__record_button")
        self._record_button.setEnabled(False)
        self._record_button.setText("")
        self._record_button.setIcon(self._get_icon("record.png"))
        self._record_button.setIconSize(QSize(16, 16))

        self._record_settings_button = QToolButton()
        self._record_settings_button.setObjectName("_status_bar__record_settings_button")
        self._record_settings_button.setText(self._translate("..."))
        self._record_settings_button.setPopupMode(QToolButton.InstantPopup)
        self._record_settings_button.setAutoRaise(False)
        self._record_settings_button.setArrowType(Qt.NoArrow)

        self._time_recording = QTimeEdit()
        self._time_recording.setObjectName("_status_bar__time_recording")
        self._time_recording.setDisplayFormat("mm:ss")
        self._time_recording.setAlignment(Qt.AlignCenter)
        self._time_recording.setReadOnly(True)
        self._time_recording.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self._time_recording.setKeyboardTracking(False)
        self._time_recording.setProperty("showGroupSeparator", False)
        self._time_recording.setCurrentSection(QDateTimeEdit.MinuteSection)
        self._time_recording.setTime(QTime(0, 0, 0))

        layout.addWidget(self._record_button)
        layout.addWidget(self._record_settings_button)
        layout.addWidget(self._time_recording)

        return self._recording_panel

    @pyqtSlot(str)
    def _on_update_status_signal(self, status: str):
        self._status_label.setText(self._translate(status))

    def _on_video_stream_started(self, event: ProcessChangeEvent):
        self._livia_status.display_status.status_message = "Video started"

    def _on_video_stream_paused(self, event: ProcessChangeEvent):
        self._livia_status.display_status.status_message = "Video paused"

    def _on_video_stream_resumed(self, event: ProcessChangeEvent):
        self._livia_status.display_status.status_message = "Video resumed"

    def _on_video_stream_stopped(self, event: ProcessChangeEvent):
        self._livia_status.display_status.status_message = "Video stopped"

    def _on_video_stream_finished(self, event: ProcessChangeEvent):
        self._livia_status.display_status.status_message = "Video finished"

    def _on_status_message_change(self, event: DisplayStatusChangeEvent[str]):
        self._update_status_signal.emit(event.value)
