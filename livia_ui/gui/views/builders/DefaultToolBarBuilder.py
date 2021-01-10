from collections import deque
from time import time
from typing import Deque

from PyQt5.QtCore import QLocale, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QProgressBar, QLCDNumber, QLabel, QDoubleSpinBox, QAbstractSpinBox, QHBoxLayout, \
    QSizePolicy
from numpy import ndarray

from livia.input.FrameInput import FrameInput
from livia.input.SeekableFrameInput import SeekableFrameInput
from livia.output.CallbackFrameOutput import CallbackFrameOutput
from livia.output.CompositeFrameOutput import CompositeFrameOutput
from livia.output.FrameOutput import FrameOutput
from livia.process.analyzer.HasThreshold import HasThreshold
from livia.process.analyzer.listener.FrameAnalyzerChangeEvent import FrameAnalyzerChangeEvent
from livia.process.analyzer.listener.FrameAnalyzerChangeListener import FrameAnalyzerChangeListener
from livia.process.analyzer.listener.ThresholdChangeEvent import ThresholdChangeEvent
from livia.process.analyzer.listener.ThresholdChangeListener import ThresholdChangeListener
from livia.process.listener import build_listener
from livia.process.listener.IOChangeEvent import IOChangeEvent
from livia.process.listener.IOChangeListener import IOChangeListener
from livia.process.listener.ProcessChangeEvent import ProcessChangeEvent
from livia.process.listener.ProcessChangeListener import ProcessChangeListener
from livia_ui.gui import LIVIA_GUI_LOGGER
from livia_ui.gui.views.builders.ToolBarBuilder import ToolBarBuilder
from livia_ui.gui.views.utils.BorderLayout import BorderLayout

_FRAMES_DEQUE_SIZE: int = 100
_MIN_FRAMES_IN_DEQUE: int = 5


class DefaultToolBarBuilder(ToolBarBuilder):
    _update_progress_signal: pyqtSignal = pyqtSignal(int)
    _update_fps_signal: pyqtSignal = pyqtSignal(float)
    _show_threshold_signal: pyqtSignal = pyqtSignal(float, float, float, float)
    _hide_threshold_signal: pyqtSignal = pyqtSignal()
    _change_threshold_signal: pyqtSignal = pyqtSignal(float)
    _show_progress_signal: pyqtSignal = pyqtSignal(int, int)
    _hide_progress_signal: pyqtSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._last_frames_time: Deque[float] = deque([], _FRAMES_DEQUE_SIZE)

        self._progress_bar: QProgressBar = None
        self._fps_counter: QLCDNumber = None
        self._fps_label: QLabel = None
        self._threshold_spin: QDoubleSpinBox = None
        self._threshold_label: QLabel = None
        self._threshold_panel: QWidget = None

        self._callback_output: CallbackFrameOutput = CallbackFrameOutput(
            show_frame_callback=self._on_show_frame
        )
        self._threshold_change_listener: ThresholdChangeListener = build_listener(
            ThresholdChangeListener, threshold_changed=self._on_threshold_changed
        )

    def _build_widgets(self):
        layout = self._parent.layout()

        layout.addWidget(self._build_widget_progress_bar(), BorderLayout.West)
        layout.addWidget(self._build_threshold_panel(), BorderLayout.Center)
        layout.addWidget(self._build_widget_fps_counter(), BorderLayout.East)

    def _connect_widgets(self):
        self._threshold_spin.valueChanged.connect(self._on_threshold_spin_value_changed)

    def _connect_signals(self):
        self._update_progress_signal.connect(self._on_update_progress_signal)
        self._update_fps_signal.connect(self._on_update_fps_signal)
        self._show_threshold_signal.connect(self._on_show_threshold_signal)
        self._hide_threshold_signal.connect(self._on_hide_threshold_signal)
        self._change_threshold_signal.connect(self._on_change_threshold_signal)
        self._show_progress_signal.connect(self._on_show_progress_signal)
        self._hide_progress_signal.connect(self._on_hide_progress_signal)

    def _listen_livia(self):
        self.__add_output_callback()

        frame_processor = self._livia_window.status.video_stream_status.frame_processor
        frame_processor.add_process_change_listener(
            build_listener(ProcessChangeListener,
                           resumed=self._on_stream_resumed)
        )

        frame_processor.add_io_change_listener(
            build_listener(IOChangeListener,
                           input_changed=self._on_input_changed,
                           output_changed=self._on_output_changed)
        )

        frame_processor.add_frame_analyzer_change_listener(
            build_listener(FrameAnalyzerChangeListener,
                           analyzer_changed=self._on_analyzer_changed)
        )

    def _disconnect_signals(self):
        self._update_progress_signal.disconnect(self._on_update_progress_signal)
        self._update_fps_signal.disconnect(self._on_update_fps_signal)
        self._show_threshold_signal.disconnect(self._on_show_threshold_signal)
        self._hide_threshold_signal.disconnect(self._on_hide_threshold_signal)
        self._change_threshold_signal.disconnect(self._on_change_threshold_signal)
        self._show_progress_signal.disconnect(self._on_show_progress_signal)
        self._hide_progress_signal.disconnect(self._on_hide_progress_signal)

    def _build_widget_progress_bar(self) -> QWidget:
        self._progress_bar = QProgressBar(self._parent)
        self._progress_bar.setObjectName("_tool_bar__progress_bar")
        self._progress_bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._progress_bar.setAlignment(Qt.AlignCenter)
        self._progress_bar.setStyleSheet("background-color: rgb(255, 255, 255);")
        self._progress_bar.setValue(0)
        self._progress_bar.raise_()

        frame_input = self._livia_window.status.video_stream_status.frame_input
        if isinstance(frame_input, SeekableFrameInput):
            self._progress_bar.setValue(frame_input.get_current_frame_index())
            self._progress_bar.setMaximum(frame_input.get_length_in_frames())
        else:
            self._progress_bar.hide()

        return self._progress_bar

    def _build_threshold_panel(self) -> QWidget:
        self._threshold_panel = QWidget(self._parent)
        layout = QHBoxLayout(self._threshold_panel)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        self._threshold_label = QLabel(self._threshold_panel)
        self._threshold_label.setObjectName("_tool_bar__threshold_label")
        self._threshold_label.setText(self._translate("Threshold:"))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self._threshold_label.setFont(font)

        self._threshold_spin = QDoubleSpinBox(self._parent)
        self._threshold_spin.setObjectName("_tool_bar__threshold_spin")
        font = QFont()
        font.setPointSize(10)
        self._threshold_spin.setFont(font)
        self._threshold_spin.setWrapping(False)
        self._threshold_spin.setFrame(True)
        self._threshold_spin.setAlignment(Qt.AlignCenter)
        self._threshold_spin.setReadOnly(False)
        self._threshold_spin.setButtonSymbols(QAbstractSpinBox.PlusMinus)
        self._threshold_spin.setAccelerated(True)
        self._threshold_spin.setKeyboardTracking(False)
        self._threshold_spin.setProperty("showGroupSeparator", False)
        self._threshold_spin.setLocale(QLocale(QLocale.C))

        layout.addWidget(self._threshold_label)
        layout.addWidget(self._threshold_spin)

        analyzer = self._livia_window.status.video_stream_status.frame_processor.frame_analyzer
        if isinstance(analyzer, HasThreshold):
            self._threshold_spin.setValue(analyzer.threshold)
            self._threshold_spin.setMaximum(analyzer.max_threshold)
            self._threshold_spin.setMinimum(analyzer.min_threshold)
            self._threshold_spin.setSingleStep(analyzer.threshold_step)
        else:
            self._threshold_spin.setValue(0.0)
            self._threshold_spin.setMaximum(1.0)
            self._threshold_spin.setMinimum(0.0)
            self._threshold_spin.setSingleStep(0.01)
            self._threshold_panel.hide()

        return self._threshold_panel

    def _build_widget_fps_counter(self) -> QWidget:
        panel = QWidget(self._parent)
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        self._fps_label = QLabel(panel)
        self._fps_label.setObjectName("_tool_bar__fps_label")
        self._fps_label.setText(self._translate("FPS:"))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self._fps_label.setFont(font)
        self._fps_label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._fps_label.raise_()

        self._fps_counter = QLCDNumber(4, panel)
        self._fps_counter.setObjectName("_tool_bar__fps_counter")
        self._fps_counter.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._fps_counter.setStyleSheet("background-color: black")
        self._fps_counter.setSmallDecimalPoint(False)
        self._fps_counter.display(0.0)
        self._fps_counter.raise_()

        layout.addWidget(self._fps_label)
        layout.addWidget(self._fps_counter)

        return panel

    @pyqtSlot(int)
    def _on_update_progress_signal(self, current_frame_index: int):
        self._progress_bar.setValue(current_frame_index)

    @pyqtSlot(float)
    def _on_update_fps_signal(self, fps: float):
        self._fps_counter.display(fps)

    @pyqtSlot(float, float, float, float)
    def _on_show_threshold_signal(self, threshold: float, min_threshold: float, max_threshold: float,
                                  threshold_step: float):
        self._threshold_spin.setValue(threshold)
        self._threshold_spin.setMinimum(min_threshold)
        self._threshold_spin.setMaximum(max_threshold)
        self._threshold_spin.setSingleStep(threshold_step)
        self._threshold_panel.show()

    @pyqtSlot()
    def _on_hide_threshold_signal(self):
        self._threshold_panel.hide()

    @pyqtSlot(int, int)
    def _on_show_progress_signal(self, progress: int, maximum: int):
        self._progress_bar.setValue(progress)
        self._progress_bar.setMaximum(maximum)
        self._progress_bar.show()

    @pyqtSlot(float)
    def _on_change_threshold_signal(self, threshold: float):
        if threshold != self._threshold_spin.value():
            self._threshold_spin.setValue(threshold)

    @pyqtSlot()
    def _on_hide_progress_signal(self):
        self._progress_bar.hide()

    def _on_show_frame(self, frame: ndarray):
        self._last_frames_time.append(time())
        self._update_fps()
        self._update_progress_signal.emit(
            self._livia_window.status.video_stream_status.frame_input.get_current_frame_index())

    def _on_stream_resumed(self, event: ProcessChangeEvent):
        self._reset_fps()

    def _on_input_changed(self, event: IOChangeEvent[FrameInput]):
        self._reset_fps()

        if isinstance(event.old, SeekableFrameInput):
            self._hide_progress_signal.emit()
        if isinstance(event.new, SeekableFrameInput):
            self._show_progress_signal.emit(event.new.get_current_frame_index(), event.new.get_length_in_frames())

    def _on_output_changed(self, event: IOChangeEvent[FrameOutput]):
        if not self.__is_callback_in_frame_output(event.new):
            self.__add_output_callback()

    def _on_analyzer_changed(self, event: FrameAnalyzerChangeEvent):
        if isinstance(event.old, HasThreshold) != isinstance(event.new, HasThreshold):
            if isinstance(event.new, HasThreshold):
                print(event.new.threshold)
                self._show_threshold_signal.emit(event.new.threshold, event.new.min_threshold, event.new.max_threshold,
                                                 event.new.threshold_step)
            else:
                self._hide_threshold_signal.emit()

    def _on_threshold_changed(self, event: ThresholdChangeEvent):
        self._change_threshold_signal.emit(event.new)

    def _on_threshold_spin_value_changed(self):
        analyzer = self._livia_window.status.video_stream_status.frame_processor.frame_analyzer
        if isinstance(analyzer, HasThreshold):
            analyzer.threshold = self._threshold_spin.value()
        else:
            LIVIA_GUI_LOGGER.warning("Attempt to change threshold in an analyzer (%s) that is not a subclass of %s",
                                     analyzer.__class__.__name__, HasThreshold.__class__.__name__)

    def _update_fps(self):
        frames = len(self._last_frames_time)
        if frames >= _MIN_FRAMES_IN_DEQUE:
            elapsed = self._last_frames_time[-1] - self._last_frames_time[0]
            self._update_fps_signal.emit(frames / elapsed)

    def _reset_fps(self):
        self._last_frames_time.clear()
        self._update_fps_signal.emit(0.0)

    def __is_callback_in_frame_output(self, output: FrameOutput) -> bool:
        if output == self._callback_output:
            return True
        elif isinstance(output, CompositeFrameOutput):
            for child_output in output.outputs:
                if self.__is_callback_in_frame_output(child_output):
                    return True
            return False
        else:
            return False

    def __add_output_callback(self):
        self._livia_window.status.video_stream_status.frame_output = CompositeFrameOutput(
            self._callback_output,
            self._livia_window.status.video_stream_status.frame_output
        )
