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

from typing import List, Dict, TypeVar, Callable, Optional
from functools import lru_cache
from abc import ABC, abstractmethod
from dataclasses import dataclass
from PySide2.QtMultimedia import QCameraInfo
from cv2 import cv2 as cv
import uuid
import threading
import queue
import time


@dataclass(frozen=True)
class CameraInfo:
    id: str
    device_name: str
    description: str


def get_available_camera_info() -> List[CameraInfo]:
    cameras = QCameraInfo.availableCameras()

    info = []
    for i in range(0, len(cameras)):
        c = CameraInfo(id=str(i), device_name=cameras[i].deviceName(), description=cameras[i].description())
        info.append(c)

    return info


class CameraListener(ABC):
    __id: str = None
    __fps: float = 0

    def __init__(self, queue_size=100):
        self.__queue = queue.Queue(queue_size)

    def get_frame(self, blocking=True, timeout_sec: int = None) -> Optional:
        try:
            return self.__queue.get(blocking, timeout_sec)
        except queue.Empty:
            return None

    def get_fps(self):
        return self.__fps

    def offer_frame(self, frame_bgr):
        try:
            self.__queue.put_nowait(frame_bgr)
        except queue.Full:
            pass

    def set_fps(self, fps: float):
        self.__fps = fps

    def get_id(self) -> str:
        if self.__id is None:
            self.__id = str(uuid.uuid4())
        return self.__id


class AbstractCamera(ABC):
    _listeners: Dict[str, CameraListener] = {}

    def __init__(self, camera_id: str):
        self._camera_id = camera_id

    def get_camera_id(self):
        return self._camera_id

    def add_camera_listener(self, listener: CameraListener) -> None:
        self._listeners[listener.get_id()] = listener
        self._on_listener_added()

    def _on_listener_added(self):
        pass

    def remove_camera_listener(self, listener: CameraListener) -> None:
        if listener.get_id() in self._listeners.keys():
            self._listeners.pop(listener.get_id(), None)

        if not self._listeners:
            self._on_all_listeners_removed()

    def _on_all_listeners_removed(self):
        pass


class DefaultCameraWorker(threading.Thread):
    __max_retry_count = 30

    def __init__(self, thread_name: str, camera_index: int, listeners: Dict[str, CameraListener]):
        super().__init__(name=thread_name)
        self.__listeners = listeners
        self.__camera_index = camera_index
        self.__stop_requested = threading.Event()

    def run(self) -> None:
        camera = cv.VideoCapture(self.__camera_index)
        retry_count = 0
        frame_count = 0
        start_time = time.time()
        while (not self.__stop_requested.is_set()) and retry_count < self.__max_retry_count:
            ret, frame_bgr = camera.read()
            # Frame was captured successfully
            if ret:
                # Reset retry_count if a camera is able to return frames now
                retry_count = 0
                for listener in self.__listeners.values():
                    listener.offer_frame(frame_bgr)
                frame_count+=1
                if frame_count > 100:
                    fps = frame_count / (time.time() - start_time)
                    for listener in self.__listeners.values():
                        listener.set_fps(fps)
                    frame_count = 0
                    start_time = time.time()
            else:
                retry_count += 1

    def stop(self):
        self.__stop_requested.set()


class DefaultCamera(AbstractCamera):
    __is_running = False
    __worker = None
    __thread_name_pattern = 'camera-worker-{}'

    def __init__(self, camera_id):
        super().__init__(camera_id)

    def _on_listener_added(self):
        if not self.__is_running:
            self.__worker = DefaultCameraWorker(thread_name=self.__thread_name_pattern.format(self._camera_id),
                                                camera_index=int(self._camera_id),  # TODO: fix me
                                                listeners=self._listeners)
            self.__worker.start()
            self.__is_running = True

    def _on_all_listeners_removed(self):
        if not (self.__worker is None):
            self.__worker.stop()
        self.__is_running = False


@lru_cache(maxsize=10)
def get_camera_by_id(camera_id: str) -> AbstractCamera:
    return DefaultCamera(camera_id)
