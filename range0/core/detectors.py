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

from typing import List, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
from PySide2.QtCore import QObject, Signal
import cv2.cv2 as cv
import numpy as np


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class DetectionResult:
    points: List[Point]


class AbstractDetectionStrategy(ABC):

    @abstractmethod
    def detect(self, frame_bgr) -> DetectionResult:
        pass


class SimpleDetectionStrategy(AbstractDetectionStrategy):

    def detect(self, frame_bgr) -> DetectionResult:
        frame_hsv = cv.cvtColor(frame_bgr, cv.COLOR_BGR2HSV)
        lower_red = np.array([0, 0, 255])
        upper_red = np.array([255, 255, 255])
        mask = cv.inRange(frame_hsv, lower_red, upper_red)
        moments = cv.moments(mask)
        x = int(moments['m10'] / moments['m00'])
        y = int(moments['m01'] / moments['m00'])
        point = Point(x, y)
        return DetectionResult([point])


class DetectionStrategyQtAdapter(QObject):
    detection_result = Signal(DetectionResult)

    def __init__(self, target_strategy: AbstractDetectionStrategy,
                 slot: Callable[[DetectionResult], None],
                 parent: QObject = None):
        super().__init__(parent)
        self.__target_strategy = target_strategy
        self.detection_result.connect(slot)

    def detect(self, frame_bgr):
        if self.__target_strategy is not None:
            self.detection_result.emit(self.__target_strategy.detect(frame_bgr))


class AbstractDetector(ABC):

    @abstractmethod
    def start_detection(self) -> None:
        pass

    @abstractmethod
    def stop_detection(self) -> None:
        pass


class AsyncDetector(AbstractDetector):
    def start_detection(self) -> None:
        pass

    def stop_detection(self) -> None:
        pass
