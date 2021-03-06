#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################
## This file has been modified for this project
from typing import Optional, Dict

from PySide2.QtCore import QRect, QSize, Qt, QObject, QEvent
from PySide2.QtWidgets import (QLayout, QWidgetItem, QWidget)

_EMPTY_RECT = QRect(0, 0, 0, 0)


class BorderLayout(QLayout):
    West, North, South, East, Center = range(5)
    MinimumSize, SizeHint = range(2)

    def __init__(self, parent: QWidget = None, margin: int = None, spacing: int = -1):
        super(BorderLayout, self).__init__(parent)

        if margin is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)
        self.__items: Dict[int, QWidgetItem] = {}

    def __del__(self):
        layout_item = self.takeAt(0)
        while layout_item is not None:
            layout_item = self.takeAt(0)

    def addItem(self, item: QWidgetItem):
        self.__add(item, self.West)

    def addWidget(self, widget: QWidget, position):
        self.__add(QWidgetItem(widget), position)

    def expandingDirections(self) -> int:
        return Qt.Horizontal | Qt.Vertical

    def hasHeightForWidth(self) -> bool:
        return False

    def count(self) -> int:
        return len(self.__items)

    def itemAt(self, index) -> Optional[QWidget]:
        if index < len(self.__items):
            key = list(self.__items.keys())[index]
            return self.__items[key]

        return None

    def minimumSize(self) -> QSize:
        return self.__calculate_size(self.MinimumSize)

    def sizeHint(self) -> QSize:
        return self.__calculate_size(self.SizeHint)

    def _place_north(self, rect: QRect) -> int:
        if self.North not in self.__items:
            return 0
        else:
            item = self.__items[self.North]
            widget = item.widget()

            if widget.isVisible():
                item.setGeometry(QRect(rect.x(), 0, rect.width(), item.sizeHint().height()))
                return item.geometry().height() + self.spacing()
            else:
                item.setGeometry(_EMPTY_RECT)
                return 0

    def _place_south(self, rect: QRect) -> int:
        if self.South not in self.__items:
            return 0
        else:
            item = self.__items[self.South]
            widget = item.widget()

            if widget.isVisible():
                item.setGeometry(QRect(item.geometry().x(), item.geometry().y(),
                                       rect.width(), item.sizeHint().height()))

                height = item.geometry().height() + self.spacing()

                item.setGeometry(QRect(rect.x(), rect.y() + rect.height() - height + self.spacing(),
                                       item.geometry().width(), item.geometry().height()))
                return height
            else:
                item.setGeometry(_EMPTY_RECT)
                return 0

    def _place_west(self, rect: QRect, north_height: int, center_height: int) -> int:
        if self.West not in self.__items:
            return 0
        else:
            item = self.__items[self.West]
            widget = item.widget()

            if widget.isVisible():
                item.setGeometry(QRect(rect.x(), north_height, item.sizeHint().width(), center_height))

                return item.geometry().width() + self.spacing()
            else:
                item.setGeometry(_EMPTY_RECT)
                return 0

    def _place_east(self, rect: QRect, north_height: int, center_height: int) -> int:
        if self.East not in self.__items:
            return 0
        else:
            item = self.__items[self.East]
            widget = item.widget()

            if widget.isVisible():
                item.setGeometry(
                    QRect(item.geometry().x(), item.geometry().y(), item.sizeHint().width(), center_height))

                east_width = item.geometry().width() + self.spacing()

                item.setGeometry(
                    QRect(rect.x() + rect.width() - east_width + self.spacing(), north_height, item.geometry().width(),
                          item.geometry().height()))

                return east_width
            else:
                item.setGeometry(_EMPTY_RECT)
                return 0

    def _place_center(self, rect: QRect, north_height: int, center_height: int, west_width: int,
                      east_width: int) -> int:
        if self.Center not in self.__items:
            return 0
        else:
            item = self.__items[self.Center]
            widget = item.widget()
            if widget.isVisible():
                item.setGeometry(
                    QRect(west_width, north_height, rect.width() - east_width - west_width, center_height))
            else:
                item.setGeometry(_EMPTY_RECT)

    def setGeometry(self, rect: QRect):
        super(BorderLayout, self).setGeometry(rect)

        north_height = self._place_north(rect)
        south_height = self._place_south(rect)
        center_height = rect.height() - north_height - south_height
        west_width = self._place_west(rect, north_height, center_height)
        east_width = self._place_east(rect, north_height, center_height)
        self._place_center(rect, north_height, center_height, west_width, east_width)

    def takeAt(self, index: int) -> Optional[QWidget]:
        if 0 <= index < len(self.__items):
            key = list(self.__items.keys())[index]
            item = self.__items[key]
            del self.__items[key]
            item.widget().removeEventFilter(self)

            return item

        return None

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Hide or event.type() == QEvent.Show:
            self.update()
            return True
        else:
            return super().eventFilter(watched, event)

    def __add(self, item: QWidgetItem, position: int):
        item.widget().installEventFilter(self)
        self.__items[position] = item

    def __calculate_size(self, size_type: int) -> QSize:
        total_size = QSize()

        for position, item in self.__items.items():
            if size_type == self.MinimumSize:
                item_size = item.minimumSize()
            else:  # sizeType == self.SizeHint
                item_size = item.sizeHint()

            if position in (self.North, self.South, self.Center):
                total_size.setHeight(total_size.height() + item_size.height())

            if position in (self.West, self.East, self.Center):
                total_size.setWidth(total_size.width() + item_size.width())

        return total_size
