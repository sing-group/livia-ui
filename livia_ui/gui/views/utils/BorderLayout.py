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

from typing import List, Optional

from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtWidgets import (QLayout, QWidgetItem, QWidget)


class ItemWrapper(object):
    def __init__(self, item: QWidget, position: int):
        self.item: QWidget = item
        self.position: int = position


class BorderLayout(QLayout):
    West, North, South, East, Center = range(5)
    MinimumSize, SizeHint = range(2)

    def __init__(self, parent: QWidget = None, margin: int = None, spacing: int = -1):
        super(BorderLayout, self).__init__(parent)

        if margin is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)
        self.list: List[ItemWrapper] = []

    def __del__(self):
        layout_item = self.takeAt(0)
        while layout_item is not None:
            layout_item = self.takeAt(0)

    def addItem(self, item: QWidget):
        self.__add(item, self.West)

    def addWidget(self, widget: QWidget, position):
        self.__add(QWidgetItem(widget), position)

    def expandingDirections(self) -> int:
        return Qt.Horizontal | Qt.Vertical

    def hasHeightForWidth(self) -> bool:
        return False

    def count(self) -> int:
        return len(self.list)

    def itemAt(self, index) -> Optional[QWidget]:
        if index < len(self.list):
            return self.list[index].item

        return None

    def minimumSize(self) -> QSize:
        return self.__calculate_size(self.MinimumSize)

    def sizeHint(self) -> QSize:
        return self.__calculate_size(self.SizeHint)

    def setGeometry(self, rect: QRect):
        center = None
        east_width = 0
        west_width = 0
        north_height = 0
        south_height = 0

        super(BorderLayout, self).setGeometry(rect)

        for wrapper in self.list:
            item = wrapper.item
            position = wrapper.position

            if position == self.North:
                item.setGeometry(QRect(rect.x(), north_height,
                                       rect.width(), item.sizeHint().height()))

                north_height += item.geometry().height() + self.spacing()

            elif position == self.South:
                item.setGeometry(QRect(item.geometry().x(),
                                       item.geometry().y(), rect.width(),
                                       item.sizeHint().height()))

                south_height += item.geometry().height() + self.spacing()

                item.setGeometry(QRect(rect.x(),
                                       rect.y() + rect.height() - south_height + self.spacing(),
                                       item.geometry().width(), item.geometry().height()))

            elif position == self.Center:
                center = wrapper

        center_height = rect.height() - north_height - south_height

        for wrapper in self.list:
            item = wrapper.item
            position = wrapper.position

            if position == self.West:
                item.setGeometry(QRect(rect.x() + west_width,
                                       north_height, item.sizeHint().width(), center_height))

                west_width += item.geometry().width() + self.spacing()

            elif position == self.East:
                item.setGeometry(QRect(item.geometry().x(),
                                       item.geometry().y(), item.sizeHint().width(),
                                       center_height))

                east_width += item.geometry().width() + self.spacing()

                item.setGeometry(QRect(rect.x() + rect.width() - east_width + self.spacing(),
                                       north_height, item.geometry().width(),
                                       item.geometry().height()))

        if center:
            center.item.setGeometry(QRect(west_width, north_height,
                                          rect.width() - east_width - west_width, center_height))

    def takeAt(self, index: int) -> Optional[QWidget]:
        if 0 <= index < len(self.list):
            item_wrapper = self.list.pop(index)
            return item_wrapper.item

        return None

    def __add(self, item: QWidget, position: int):
        self.list.append(ItemWrapper(item, position))

    def __calculate_size(self, size_type: int) -> QSize:
        total_size = QSize()

        for wrapper in self.list:
            position = wrapper.position

            if size_type == self.MinimumSize:
                item_size = wrapper.item.minimumSize()
            else:  # sizeType == self.SizeHint
                item_size = wrapper.item.sizeHint()

            if position in (self.North, self.South, self.Center):
                total_size.setHeight(total_size.height() + item_size.height())

            if position in (self.West, self.East, self.Center):
                total_size.setWidth(total_size.width() + item_size.width())

        return total_size
