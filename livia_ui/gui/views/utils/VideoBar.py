import os
from typing import Tuple

from PyQt5.QtCore import Qt, QTime, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QTimeEdit, QAbstractSpinBox

from livia.input.SeekableFrameInput import SeekableFrameInput
from livia.process.FrameProcessor import FrameProcessor
from livia.process.listener import build_listener
from livia.process.listener.IOChangeEvent import IOChangeEvent
from livia.process.listener.IOChangeListener import IOChangeListener
from livia.process.listener.ProcessChangeEvent import ProcessChangeEvent
from livia.process.listener.ProcessChangeListener import ProcessChangeListener


class VideoBar(QWidget):
    _show_frame_signal: pyqtSignal = pyqtSignal(int, int)
    _check_frame_input_signal: pyqtSignal = pyqtSignal()
    _enable_stop_button_signal: pyqtSignal = pyqtSignal(bool)
    _set_play_icon_signal: pyqtSignal = pyqtSignal(QIcon)

    def __init__(self, frame_processor: FrameProcessor, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._frame_processor: FrameProcessor = frame_processor

        self._play_bar_slider_pressed: bool = False

        path: str = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        layout = QHBoxLayout()

        self._play_icon: QIcon = QIcon(os.path.join(path, "icons", "play.svg"))
        self._pause_icon: QIcon = QIcon(os.path.join(path, "icons", "pause.svg"))
        self._resume_icon: QIcon = QIcon(os.path.join(path, "icons", "resume.svg"))
        self._stop_icon: QIcon = QIcon(os.path.join(path, "icons", "stop.svg"))

        self._play_button = QPushButton(self)
        self._play_button.setMinimumSize(24, 24)

        self._stop_button = QPushButton(QIcon(os.path.join(path, "icons", "stop.svg")), None, self)
        self._stop_button.setMinimumSize(24, 24)

        self._play_bar_slider: QSlider = QSlider(Qt.Horizontal, self)
        self._play_bar_slider.setMinimum(0)

        self._time_display = QTimeEdit(self)
        self._time_display.setReadOnly(True)
        self._time_display.setDisplayFormat("hh:mm:ss.zzz")
        self._time_display.setAlignment(Qt.AlignCenter)
        self._time_display.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self._time_display.setKeyboardTracking(False)
        self._time_display.setProperty("showGroupSeparator", False)

        layout.addWidget(self._play_button)
        layout.addWidget(self._stop_button)
        layout.addWidget(self._play_bar_slider)
        layout.addWidget(self._time_display)

        self.setLayout(layout)

        self._play_button.clicked.connect(self._on_click_play)
        self._stop_button.clicked.connect(self._on_click_stop)
        self._play_bar_slider.sliderPressed.connect(self._on_slider_pressed)
        self._play_bar_slider.sliderReleased.connect(self._on_slider_released)

        self._process_change_listener: ProcessChangeListener = \
            build_listener(ProcessChangeListener,
                           started=self._on_stream_started,
                           stopped=self._on_stream_stopped,
                           paused=self._on_stream_paused,
                           resumed=self._on_stream_resumed,
                           finished=self._on_stream_finished,
                           frame_outputted=self._on_stream_outputted_frame
                           )

        self._frame_processor.add_io_change_listener(
            build_listener(IOChangeListener,
                           input_changed=self._on_frame_input_changed
                           )
        )

        self._check_frame_input_signal.connect(self._on_check_frame_input_signal)
        self._check_frame_input_signal.emit()

    @property
    def frame_processor(self) -> FrameProcessor:
        return self._frame_processor

    def _is_playing(self) -> bool:
        return self._frame_processor.is_alive()

    def _is_paused(self) -> bool:
        return self._frame_processor.is_paused()

    @pyqtSlot(int, int)
    def _on_show_frame_signal(self, time: int, frame: int):
        if self._is_frame_input_seekable():
            self._time_display.setTime(QTime(*VideoBar._split_time(time)))

            if not self._play_bar_slider_pressed:
                self._play_bar_slider.setValue(frame)

    @pyqtSlot()
    def _on_check_frame_input_signal(self):
        frame_input = self._frame_processor.input

        if self._is_frame_input_seekable():
            self._play_button.setIcon(self._play_icon)
            self._time_display.setTime(QTime(*VideoBar._split_time(frame_input.get_current_msec())))
            self._play_bar_slider.setMaximum(frame_input.get_length_in_frames())
            self._play_bar_slider.setValue(frame_input.get_current_frame_index() + 1)

            self._play_button.setEnabled(True)
            self._stop_button.setEnabled(True)
            self._play_bar_slider.setEnabled(True)
            self._time_display.setEnabled(True)
            self.setEnabled(True)

            if not self._frame_processor.has_process_change_listener(self._process_change_listener):
                self._frame_processor.add_process_change_listener(self._process_change_listener)
            self._show_frame_signal.connect(self._on_show_frame_signal)
            self._enable_stop_button_signal.connect(self._on_enable_stop_button_signal)
            self._set_play_icon_signal.connect(self._on_set_play_icon_signal)
        else:
            if self._frame_processor.has_process_change_listener(self._process_change_listener):
                self._frame_processor.remove_process_change_listener(self._process_change_listener)
            try:
                self._show_frame_signal.disconnect(self._on_show_frame_signal)
                self._enable_stop_button_signal.disconnect(self._on_enable_stop_button_signal)
                self._set_play_icon_signal.disconnect(self._on_set_play_icon_signal)
            except TypeError:
                pass

            self._play_button.setIcon(self._play_icon)
            self._time_display.setTime(QTime(0, 0))
            self._play_bar_slider.setValue(0)

            self._play_button.setEnabled(False)
            self._stop_button.setEnabled(False)
            self._play_bar_slider.setEnabled(False)
            self._time_display.setEnabled(False)
            self.setEnabled(False)

    @pyqtSlot(bool)
    def _on_enable_stop_button_signal(self, enabled: bool):
        self._stop_button.setEnabled(enabled)

    def _on_set_play_icon_signal(self, icon: QIcon):
        self._play_button.setIcon(icon)

    def _on_stream_started(self, event: ProcessChangeEvent):
        self._enable_stop_button_signal.emit(True)
        self._set_play_icon_signal.emit(self._pause_icon)

    def _on_stream_stopped(self, event: ProcessChangeEvent):
        self._enable_stop_button_signal.emit(False)
        self._set_play_icon_signal.emit(self._play_icon)

    def _on_stream_paused(self, event: ProcessChangeEvent):
        self._set_play_icon_signal.emit(self._resume_icon)

    def _on_stream_resumed(self, event: ProcessChangeEvent):
        self._set_play_icon_signal.emit(self._pause_icon)

    def _on_stream_finished(self, event: ProcessChangeEvent):
        self._enable_stop_button_signal.emit(False)
        self._set_play_icon_signal.emit(self._play_icon)

    def _on_stream_outputted_frame(self, event: ProcessChangeEvent):
        time = self._frame_processor.input.get_current_msec()
        frame = self._frame_processor.input.get_current_frame_index()

        if time != self._play_bar_slider.value():
            self._show_frame_signal.emit(time, frame + 1)

    def _on_frame_input_changed(self, event: IOChangeEvent):
        self._check_frame_input_signal.emit()

    def _on_slider_pressed(self):
        self._play_bar_slider_pressed = True

    def _on_slider_released(self):
        self._play_bar_slider_pressed = False
        self._frame_processor.input.go_to_frame(self._play_bar_slider.value())

    def _on_click_play(self, checked: bool):
        if self._is_playing():
            if self._is_paused():
                self.frame_processor.resume()
            else:
                self.frame_processor.pause()
        else:
            self.frame_processor.input.go_to_frame(0)
            self.frame_processor.start()

    def _on_click_stop(self, checked: bool):
        self._frame_processor.stop()

    def _is_frame_input_seekable(self) -> bool:
        return isinstance(self._frame_processor.input, SeekableFrameInput)

    @staticmethod
    def _split_time(time: int) -> Tuple[int, int, int, int]:
        total_secs = int(time / 1000)

        hours = int(total_secs / (60 * 60))
        minutes = int((total_secs - hours * 60 * 60) / 60)
        secs = int((total_secs - hours * 60 * 60 - minutes * 60))
        msecs = time % 1000

        return hours, minutes, secs, msecs
