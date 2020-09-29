#   Range0 - the software for practical shooting training
#   Copyright (C) 2020 pendyurinandrey
#  #
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#  #
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#  #
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import Callable
from PySide2.QtCore import QObject, Signal

from range0.core.detectors import DetectionResult
from range0.core.camera import CameraFpsListener


# It's impossible to inherit this class from AbstractDetectionResultSender, because of limitations
# of Qt Meta Object Compiler. Just repeat signature of AbstractDetectionResultSender.
class QtDetectionResultSender(QObject):
    detection_result = Signal(DetectionResult)

    def __init__(self, slot: Callable[[DetectionResult], None],
                 parent: QObject = None):
        super().__init__(parent)
        self.detection_result.connect(slot)

    def send(self, result: DetectionResult):
        self.detection_result.emit(result)


class QtFpsSender(QObject):
    __wrapped_fps_listener: CameraFpsListener = CameraFpsListener()
    __fps_is_ready = Signal(float)

    def __init__(self, slot_func: Callable[[float], None], parent: QObject = None):
        super().__init__(parent)
        self.__fps_is_ready.connect(slot_func)

    def get_fps(self):
        return self.__wrapped_fps_listener.get_fps()

    def set_fps(self, fps: float):
        self.__wrapped_fps_listener.set_fps(fps)
        self.__fps_is_ready.emit(fps)

    def get_id(self) -> str:
        return self.__wrapped_fps_listener.get_id()