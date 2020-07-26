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
from typing import Any
from abc import ABC, abstractmethod
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import QObject, Signal
from range0.core.camera import AbstractCamera, get_camera_by_id, CameraListener
from range0.gui.mdi_widgets import *
from dataclasses import dataclass


@dataclass(frozen=True)
class Frame:
    cv_image: Any
    fps: float


class AbstractRenderingStrategy(QObject):

    def render(self, frame: Frame):
        pass


class CameraWidgetRenderingStrategy(AbstractRenderingStrategy):
    next_frame = Signal(QPixmap, float)

    def __init__(self, camera_widget, parent: QObject = None):
        super().__init__(parent=parent)
        self.__camera_widget = camera_widget
        self.next_frame.connect(camera_widget.update_camera_view)

    def render(self, frame: Frame):
        height, width, val = frame.cv_image.shape
        pixmap = QPixmap.fromImage(QImage(frame.cv_image.data, width, height, QImage.Format_RGB888))
        self.next_frame.emit(pixmap, frame.fps)


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
    def __init__(self, thread_name: str, camera: AbstractCamera, strategy: AbstractRenderingStrategy):
        super().__init__(name=thread_name)
        self.__strategy = strategy
        self.__camera = camera
        self.__stop_requested = threading.Event()

    def run(self) -> None:
        listener = CameraListener()
        self.__camera.add_camera_listener(listener)
        while not self.__stop_requested.is_set():
            frame = listener.get_frame(timeout_sec=10)
            fps = listener.get_fps()
            self.__strategy.render(Frame(frame, fps))

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

    def to_camera_widget(self, camera_widget):
        return WithCameraAndStrategyRendererBuilder(self.__camera_id, CameraWidgetRenderingStrategy(camera_widget))


class DefaultRendererBuilder:
    def from_camera_id(self, camera_id: str) -> WithCameraRendererBuilder:
        return WithCameraRendererBuilder(camera_id)
