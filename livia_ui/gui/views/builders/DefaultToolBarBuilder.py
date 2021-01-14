from collections import deque
from time import time
from typing import Deque, Callable, Tuple, Dict

from PyQt5.QtCore import QLocale, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QProgressBar, QLCDNumber, QLabel, QDoubleSpinBox, QAbstractSpinBox, QHBoxLayout, \
    QSizePolicy

from livia.input.FrameInput import FrameInput
from livia.input.SeekableFrameInput import SeekableFrameInput
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
from livia_ui.gui.views.builders.TopToolBarBuilder import TopToolBarBuilder
from livia_ui.gui.views.utils.BorderLayout import BorderLayout

_FRAMES_DEQUE_SIZE: int = 100
_MIN_FRAMES_IN_DEQUE: int = 5


class DefaultTopToolBarBuilder(TopToolBarBuilder):
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

    def _register_signals(self) -> Dict[str, Tuple[pyqtSignal, Callable[..., None]]]:
        return {
            "_update_progress_signal": (self._update_progress_signal, self._on_update_progress_signal),
            "_update_fps_signal": (self._update_fps_signal, self._on_update_fps_signal),
            "_show_threshold_signal": (self._show_threshold_signal, self._on_show_threshold_signal),
            "_hide_threshold_signal": (self._hide_threshold_signal, self._on_hide_threshold_signal),
            "_change_threshold_signal": (self._change_threshold_signal, self._on_change_threshold_signal),
            "_show_progress_signal": (self._show_progress_signal, self._on_show_progress_signal),
            "_hide_progress_signal": (self._hide_progress_signal, self._on_hide_progress_signal)
        }

    def _listen_livia(self):
        frame_processor = self._livia_window.status.video_stream_status.frame_processor
        frame_processor.add_process_change_listener(
            build_listener(ProcessChangeListener,
                           resumed=self._on_stream_resumed,
                           started=self._on_stream_started,
                           frame_outputted=self._on_frame_outputted)
        )

        frame_processor.add_io_change_listener(
            build_listener(IOChangeListener,
                           input_changed=self._on_input_changed)
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
        self._progress_bar.setObjectName("_top_tool_bar__progress_bar")
        self._progress_bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._progress_bar.setAlignment(Qt.AlignCenter)
        self._progress_bar.setStyleSheet("background-color: rgb(255, 255, 255);")
        self._progress_bar.setValue(0)
        self._progress_bar.raise_()

        frame_input = self._livia_window.status.video_stream_status.frame_input
        if isinstance(frame_input, SeekableFrameInput):
            self._progress_bar.setValue(frame_input.get_current_frame_index() + 1)
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
        self._threshold_label.setObjectName("_top_tool_bar__threshold_label")
        self._threshold_label.setText(self._translate("Threshold:"))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self._threshold_label.setFont(font)

        self._threshold_spin = QDoubleSpinBox(self._parent)
        self._threshold_spin.setObjectName("_top_tool_bar__threshold_spin")
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
        self._fps_label.setObjectName("_top_tool_bar__fps_label")
        self._fps_label.setText(self._translate("FPS:"))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self._fps_label.setFont(font)
        self._fps_label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self._fps_label.raise_()

        self._fps_counter = QLCDNumber(4, panel)
        self._fps_counter.setObjectName("_top_tool_bar__fps_counter")
        self._fps_counter.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._fps_counter.setStyleSheet("background-color: black")
        self._fps_counter.setSmallDecimalPoint(False)
        self._fps_counter.display(0.0)
        self._fps_counter.raise_()

        layout.addWidget(self._fps_label)
        layout.addWidget(self._fps_counter)

        return panel

    @pyqtSlot(int)
    def _on_update_progress_signal(self, value: int):
        self._progress_bar.setValue(value)

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

    def _on_stream_started(self, event: ProcessChangeEvent):
        self._reset_fps()

    def _on_stream_resumed(self, event: ProcessChangeEvent):
        self._reset_fps()

    def _on_frame_outputted(self, event: ProcessChangeEvent):
        self._last_frames_time.append(time())
        self._update_fps()
        self._emit_update_progress_signal(
            self._livia_window.status.video_stream_status.frame_input.get_current_frame_index() + 1)

    def _on_input_changed(self, event: IOChangeEvent[FrameInput]):
        self._reset_fps()

        if isinstance(event.old, SeekableFrameInput):
            self._emit_hide_progress_signal()
        if isinstance(event.new, SeekableFrameInput):
            self._emit_show_progress_signal(event.new.get_current_frame_index() + 1, event.new.get_length_in_frames())

    def _on_analyzer_changed(self, event: FrameAnalyzerChangeEvent):
        old_analyzer = event.old
        new_analyzer = event.new

        if isinstance(old_analyzer, HasThreshold):
            was_threshold_visible = True
            old_analyzer.remove_threshold_change_listener(self._threshold_change_listener)
        else:
            was_threshold_visible = False

        if isinstance(new_analyzer, HasThreshold):
            self._emit_show_threshold_signal(new_analyzer.threshold, new_analyzer.min_threshold,
                                             new_analyzer.max_threshold, new_analyzer.threshold_step)
            new_analyzer.add_threshold_change_listener(self._threshold_change_listener)
        else:
            if was_threshold_visible:
                self._emit_hide_threshold_signal()

    def _on_threshold_changed(self, event: ThresholdChangeEvent):
        self._emit_change_threshold_signal(event.new)

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
            self._emit_update_fps_signal(frames / elapsed)

    def _reset_fps(self):
        self._last_frames_time.clear()
        self._emit_update_fps_signal(0.0)
