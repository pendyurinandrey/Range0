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
from __future__ import annotations

from typing import Optional, Callable

from range0.core.camera import AbstractCamera, get_camera_by_id, CameraFpsListener
from range0.core.detectors import AbstractShotDetector, AsyncShotDetector, \
    AbstractDetectionResultSender, SimpleShotDetectionStrategy, DetectionResult
from range0.core.qt_adapters import QtFpsSender, QtDetectionResultSender


class Training:
    def __init__(self, camera: AbstractCamera, detector: AbstractShotDetector,
                 fps_listener: Optional[CameraFpsListener]):
        self.__fps_listener = fps_listener
        self.__detector = detector
        self.__camera = camera

    def start(self):
        if self.__fps_listener is not None:
            self.__camera.add_fps_listener(self.__fps_listener)
        self.__detector.start_detection()

    def stop(self):
        if self.__fps_listener is not None:
            self.__camera.remove_fps_listener(self.__fps_listener)
        self.__detector.stop_detection()


class DefaultTrainingBuilder:
    __camera: Optional[AbstractCamera] = None
    __detector_creator: Optional[
        Callable[[AbstractCamera, AbstractDetectionResultSender], AbstractShotDetector]] = None
    __fps_listener = None
    __detection_result_sender = None

    def from_camera_id(self, camera_id: str) -> DefaultTrainingBuilder:
        self.__camera = get_camera_by_id(camera_id)
        return self

    def with_default_detector(self) -> DefaultTrainingBuilder:
        def detector_creator(camera: AbstractCamera, result_sender: AbstractDetectionResultSender):
            return AsyncShotDetector(camera, SimpleShotDetectionStrategy(), result_sender)

        self.__detector_creator = detector_creator
        return self

    def send_fps_to_qt_slot(self, slot_func: Callable[[float], None]) -> DefaultTrainingBuilder:
        self.__fps_listener = QtFpsSender(slot_func)
        return self

    def send_detection_result_to_qt_slot(self, slot_func: Callable[
        [DetectionResult], None]) -> DefaultTrainingBuilder:
        self.__detection_result_sender = QtDetectionResultSender(slot_func)
        return self

    def build(self) -> Training:
        if self.__camera is None:
            raise ValueError('Camera id was not provided')
        if self.__detector_creator is None:
            raise ValueError('Detector was not provided')
        detector = self.__detector_creator(self.__camera, self.__detection_result_sender)
        return Training(self.__camera, detector, self.__fps_listener)
