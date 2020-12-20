#      This file is part of PolyDeep CAD.
#
#      Foobar is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      Foobar is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with PolyDeep CAD.  If not, see <https://www.gnu.org/licenses/>.

import cv2
import numpy

from livia.output.FrameOutput import FrameOutput


class AppFrameOutput(FrameOutput):
    def __init__(self, application):
        self.application = application
        super().__init__()

    def show_frame(self, frame: numpy.ndarray):
        print(frame)
        self.application.update_frame(frame)

    def close_output(self):
        self.application.stop_movie()
