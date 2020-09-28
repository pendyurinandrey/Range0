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

import threading
from typing import Any, Callable
from abc import ABC, abstractmethod
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import QObject, Signal
from dataclasses import dataclass
import cv2.cv2 as cv

from range0.core.camera import AbstractCamera, get_camera_by_id, CameraListener


@dataclass(frozen=True)
class Frame:
    cv_image: Any
    fps: float


class AbstractRenderingStrategy(ABC):
    @abstractmethod
    def render(self, frame_bgr: Frame):
        pass


class ToQtSlotRenderingStrategy(QObject):
    next_frame = Signal(QPixmap, float)

    def __init__(self, slot: Callable[[QPixmap, float], None], parent: QObject = None):
        super().__init__(parent)
        self.next_frame.connect(slot)

    def render(self, frame_bgr: Frame):
        rgb_frame = cv.cvtColor(frame_bgr.cv_image, cv.COLOR_BGR2RGB)
        height, width, val = rgb_frame.shape
        pixmap = QPixmap.fromImage(QImage(rgb_frame.data, width, height, QImage.Format_RGB888))
        self.next_frame.emit(pixmap, frame_bgr.fps)


class AbstractRenderer(ABC):

    @abstractmethod
    def start_rendering(self):
        pass

    @abstractmethod
    def stop_rendering(self):
        pass


class AsyncRenderer(AbstractRenderer):
    __listener = None
    __worker = None

    def __init__(self, camera: AbstractCamera, strategy: AbstractRenderingStrategy):
        self.__strategy = strategy
        self.__camera = camera

    def start_rendering(self):
        self.__worker = AsyncRendererWorker(thread_name='renderer-worker-{}'.format(self.__camera.get_camera_id()),
                                            camera=self.__camera,
                                            strategy=self.__strategy)
        self.__worker.start()

    def stop_rendering(self):
        if not (self.__worker is None):
            self.__worker.stop()


class AsyncRendererWorker(threading.Thread):
    def __init__(self, thread_name: str, camera: AbstractCamera,
                 strategy: AbstractRenderingStrategy):
        super().__init__(name=thread_name)
        self.__strategy = strategy
        self.__camera = camera
        self.__stop_requested = threading.Event()

    def run(self) -> None:
        listener = CameraListener()
        self.__camera.add_camera_listener(listener)
        while not self.__stop_requested.is_set():
            frame_bgr = listener.get_frame(timeout_sec=10)
            fps = listener.get_fps()
            self.__strategy.render(Frame(frame_bgr, fps))

        self.__camera.remove_camera_listener(listener)

    def stop(self):
        self.__stop_requested.set()


class WithCameraAndStrategyRendererBuilder:
    def __init__(self, camera_id: str, strategy: AbstractRenderingStrategy):
        self.__camera_id = camera_id
        self.__strategy = strategy

    def build(self) -> AbstractRenderer:
        camera = get_camera_by_id(self.__camera_id)
        return AsyncRenderer(camera, self.__strategy)


class WithCameraRendererBuilder:
    def __init__(self, camera_id: str):
        self.__camera_id = camera_id

    def send_raw_frame_to_qt_slot(self, slot_func: Callable[[QPixmap, float], None]):
        return WithCameraAndStrategyRendererBuilder(self.__camera_id,
                                                    ToQtSlotRenderingStrategy(slot_func))


class DefaultRendererBuilder:
    def from_camera_id(self, camera_id: str) -> WithCameraRendererBuilder:
        return WithCameraRendererBuilder(camera_id)
