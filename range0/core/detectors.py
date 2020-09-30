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

from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
import cv2.cv2 as cv
import numpy as np
import threading

from range0.core.camera import AbstractCamera, CameraFrameListener


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True)
class DetectionResult:
    points: List[Point]
    detection_time: datetime
    frame_bgr: np.ndarray


class AbstractDetectionResultSender(ABC):
    @abstractmethod
    def send(self, result: DetectionResult):
        pass


class AbstractShotDetectionStrategy(ABC):

    @abstractmethod
    def detect(self, frame_bgr) -> DetectionResult:
        pass


class SimpleShotDetectionStrategy(AbstractShotDetectionStrategy):

    def detect(self, frame_bgr) -> DetectionResult:
        detection_time = datetime.now()
        frame_inv = cv.bitwise_not(frame_bgr)
        frame_hsv = cv.cvtColor(frame_inv, cv.COLOR_BGR2HSV)

        lower_red = np.array([80, 70, 50])
        upper_red = np.array([100, 255, 255])
        mask = cv.inRange(frame_hsv, lower_red, upper_red)
        #cv.imwrite('mask.jpg', mask)
        smoothed = cv.GaussianBlur(mask, (7, 7), sigmaX=1.5, sigmaY=1.5)
        #cv.imwrite('smoothed_mask.jpg', smoothed)
        detected_circles: np.ndarray = cv.HoughCircles(image=smoothed,
                                                       method=cv.HOUGH_GRADIENT_ALT,
                                                       dp=1.5,
                                                       minDist=10,
                                                       param1=300,
                                                       param2=0.9,
                                                       minRadius=2,
                                                       maxRadius=50)
        det_result = []
        if detected_circles is not None:
            circles = np.round(detected_circles[0, :]).astype("int")
            for (x, y, _) in circles:
                det_result.append(Point(x, y))

        return DetectionResult(det_result, detection_time, frame_bgr)


class DetectionWorker(threading.Thread):
    def __init__(self, thread_name: str, camera: AbstractCamera,
                 detection_strategy: AbstractShotDetectionStrategy,
                 detection_result_sender: AbstractDetectionResultSender):
        super(DetectionWorker, self).__init__(name=thread_name)
        self.__detection_result_sender = detection_result_sender
        self.__camera = camera
        self.__detection_strategy = detection_strategy
        self.__stop_requested = threading.Event()

    def run(self) -> None:
        listener = CameraFrameListener()
        self.__camera.add_frame_listener(listener)
        try:
            while not self.__stop_requested.is_set():
                frame_bgr = listener.get_frame(timeout_sec=1)
                if frame_bgr is not None:
                    result = self.__detection_strategy.detect(frame_bgr)
                    self.__detection_result_sender.send(result)
        finally:
            self.__camera.remove_frame_listener(listener)

    def stop(self):
        self.__stop_requested.set()


class AbstractShotDetector(ABC):

    @abstractmethod
    def start_detection(self) -> None:
        pass

    @abstractmethod
    def stop_detection(self) -> None:
        pass


class AsyncShotDetector(AbstractShotDetector):
    __thread_name_pattern = 'detector-worker-{}'
    __is_running = False
    __worker: Optional[DetectionWorker] = None

    def __init__(self, camera: AbstractCamera,
                 detection_strategy: AbstractShotDetectionStrategy,
                 detection_result_sender: AbstractDetectionResultSender):
        self.__detection_result_sender = detection_result_sender
        self.__camera = camera
        self.__detection_strategy = detection_strategy

    def start_detection(self) -> None:
        if not self.__is_running:
            self.__worker = DetectionWorker(thread_name=self.__thread_name_pattern,
                                            camera=self.__camera,
                                            detection_strategy=self.__detection_strategy,
                                            detection_result_sender=self.__detection_result_sender)
            self.__worker.daemon = True
            self.__worker.start()

    def stop_detection(self) -> None:
        if self.__worker is not None:
            self.__worker.stop()
            self.__worker = None
