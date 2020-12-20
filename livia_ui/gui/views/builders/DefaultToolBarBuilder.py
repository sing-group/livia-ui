from __future__ import annotations

from collections import deque
from time import time
from typing import TYPE_CHECKING, Deque

from PyQt5 import QtCore
from PyQt5.QtCore import QLocale, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QProgressBar, QLCDNumber, QLabel, QDoubleSpinBox, QAbstractSpinBox, QHBoxLayout, \
    QSizePolicy
from numpy import ndarray

from livia.output.CallbackFrameOutput import CallbackFrameOutput
from livia.output.CompositeFrameOutput import CompositeFrameOutput
from livia.process.listener import build_listener
from livia.process.listener.ProcessChangeEvent import ProcessChangeEvent
from livia.process.listener.ProcessChangeListener import ProcessChangeListener
from livia_ui.gui.views.builders.ToolBarBuilder import ToolBarBuilder
from livia_ui.gui.views.utils.BorderLayout import BorderLayout

if TYPE_CHECKING:
    from livia_ui.gui.LiviaWindow import LiviaWindow

_FRAMES_DEQUE_SIZE: int = 100
_MIN_FRAMES_IN_DEQUE: int = 5


class DefaultToolBarBuilder(ToolBarBuilder):
    def __init__(self):
        self._translate = QtCore.QCoreApplication.translate
        self._last_frames_time: Deque[float] = deque([], _FRAMES_DEQUE_SIZE)

        self._progress_bar: QProgressBar = None
        self._fps_counter: QLCDNumber = None
        self._fps_label: QLabel = None
        self._threshold_spin: QDoubleSpinBox = None
        self._threshold_label: QLabel = None

    def build(self, main_window: LiviaWindow, tool_bar: QWidget):
        layout = tool_bar.layout()

        layout.addWidget(self._add_widget_progress_bar(tool_bar), BorderLayout.West)
        layout.addWidget(self._add_threshold_controller(tool_bar), BorderLayout.Center)
        layout.addWidget(self._add_widget_fps_counter(tool_bar), BorderLayout.East)

        self._threshold_label.setFocus()

        main_window.status.video_stream_status.frame_processor.add_process_change_listener(
            build_listener(ProcessChangeListener,
                           started=self._on_stream_started,
                           resumed=self._on_stream_resumed)
        )

        main_window.status.video_stream_status.frame_output = CompositeFrameOutput(
            CallbackFrameOutput(
                show_frame_callback=self._on_show_frame,
                close_callback=self._on_close
            ),
            main_window.status.video_stream_status.frame_output
        )

    def _update_fps(self):
        frames = len(self._last_frames_time)
        if frames >= _MIN_FRAMES_IN_DEQUE:
            elapsed = self._last_frames_time[-1] - self._last_frames_time[0]
            self._fps_counter.display(frames / elapsed)

    def _on_show_frame(self, frame: ndarray):
        self._last_frames_time.append(time())
        self._update_fps()

    def _on_close(self):
        pass

    def _on_stream_started(self, event: ProcessChangeEvent):
        self._progress_bar.setDisabled(False)

    def _on_stream_resumed(self, event: ProcessChangeEvent):
        self._last_frames_time.clear()
        self._fps_counter.display(0.0)

    def _add_widget_progress_bar(self, parent: QWidget) -> QWidget:
        self._progress_bar = QProgressBar(parent)
        self._progress_bar.setObjectName("_tool_bar__progress_bar")
        self._progress_bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._progress_bar.setAlignment(Qt.AlignCenter)
        self._progress_bar.setStyleSheet("background-color: rgb(255, 255, 255);")
        self._progress_bar.setValue(24)
        self._progress_bar.raise_()

        return self._progress_bar

    def _add_widget_fps_counter(self, parent: QWidget) -> QWidget:
        panel = QWidget(parent)
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        self._fps_label = QLabel(panel)
        self._fps_label.setObjectName("_tool_bar__fps_label")
        self._fps_label.setText(self._translate("DefaultToolBarBuilder", "FPS:"))
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

    def _add_threshold_controller(self, parent: QWidget) -> QWidget:
        panel = QWidget(parent)
        layout = QHBoxLayout(panel)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        self._threshold_label = QLabel(panel)
        self._threshold_label.setObjectName("_tool_bar__threshold_label")
        self._threshold_label.setText(self._translate("DefaultToolBarBuilder", "Threshold:"))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self._threshold_label.setFont(font)

        self._threshold_spin = QDoubleSpinBox(panel)
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
        self._threshold_spin.setMaximum(1.0)
        self._threshold_spin.setSingleStep(0.01)
        self._threshold_spin.setLocale(QLocale(QLocale.C))

        layout.addWidget(self._threshold_label)
        layout.addWidget(self._threshold_spin)

        self._threshold_label.raise_()
        self._threshold_spin.raise_()

        return panel
