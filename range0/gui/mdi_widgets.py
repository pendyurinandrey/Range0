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

from typing import Optional, List

import PySide2
from PySide2.QtWidgets import QWidget, QGraphicsView, QVBoxLayout, QGraphicsScene, QLabel
from PySide2.QtGui import QShowEvent, QPixmap, QImage, QPen, QColor
from PySide2.QtCore import Slot, Qt
import cv2.cv2 as cv

from range0.core.training_builder import DefaultTrainingBuilder, Training
from range0.core.detectors import DetectionResult, Point


class CameraWidget(QWidget):
    __graphics_view: Optional[QGraphicsView] = None
    __graphics_scene: Optional[QGraphicsScene] = None
    __camera_output: Optional[QLabel] = None
    __training: Optional[Training] = None
    __fps_label: Optional[QLabel] = None

    def __init__(self, camera_id: str):
        super().__init__()
        self.__camera_id = camera_id
        self.__graphics_scene: QGraphicsScene = QGraphicsScene(self)
        self.__graphics_view = QGraphicsView(self.__graphics_scene)
        self.__camera_output = QLabel()
        self.__graphics_scene.addWidget(self.__camera_output)
        self.__fps_label = QLabel()
        self.__graphics_view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.__graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.__graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout = QVBoxLayout()
        layout.addWidget(self.__graphics_view)
        layout.addWidget(self.__fps_label)
        self.setLayout(layout)

    @Slot(float)
    def render_fps(self, fps: float):
        self.__fps_label.setText('Fps: {:.2f}'.format(fps))

    @Slot(DetectionResult)
    def render_shot_detection_result(self, result: DetectionResult):
        rgb_frame = cv.cvtColor(result.frame_bgr, cv.COLOR_BGR2RGB)
        height, width, _ = rgb_frame.shape
        pixmap = QPixmap.fromImage(QImage(rgb_frame.data, width, height, QImage.Format_RGB888))
        current_width = self.__graphics_view.width()
        current_height = self.__graphics_view.height()
        scaled_pixmap = pixmap.scaled(current_width, current_height, Qt.KeepAspectRatio,
                                      Qt.FastTransformation)
        self.__camera_output.setPixmap(scaled_pixmap)
        self.__camera_output.setGeometry(0, 0, scaled_pixmap.width(), scaled_pixmap.height())
        self.__graphics_scene.setSceneRect(0, 0, scaled_pixmap.width(), scaled_pixmap.height())
        if width != 0:
            self.render_shots(result.points, scaled_pixmap.width() / width)
        else:
            self.render_shots(result.points, 1)

    def render_shots(self, shots: List[Point], scaling_factor: float):
        if shots:
            for shot in shots:
                color = QColor().black()
                self.__graphics_scene.addEllipse(shot.x * scaling_factor, shot.y * scaling_factor,
                                                 10, 10, QPen(color))

    # Will be invoked whe widget becomes visible
    def showEvent(self, event: QShowEvent):
        self.__training = DefaultTrainingBuilder() \
            .from_camera_id(self.__camera_id) \
            .with_default_detector() \
            .send_detection_result_to_qt_slot(self.render_shot_detection_result) \
            .send_fps_to_qt_slot(self.render_fps) \
            .build()

        self.__training.start()

        super().showEvent(event)

    def hideEvent(self, event: PySide2.QtGui.QHideEvent):
        if self.__training is not None:
            self.__training.stop()

        super().hideEvent(event)
