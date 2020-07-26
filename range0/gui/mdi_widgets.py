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

from typing import Optional

import PySide2
from PySide2.QtWidgets import QWidget, QGraphicsView, QVBoxLayout, QGraphicsScene, QLabel
from PySide2.QtGui import QShowEvent, QPixmap
from PySide2.QtCore import Slot, Qt

from range0.core.renderers import AbstractRenderer, DefaultRendererBuilder


class CameraWidget(QWidget):

    __graphics_view: Optional[QGraphicsView] = None
    __graphics_scene: Optional[QGraphicsScene] = None
    __camera_output: Optional[QLabel] = None
    __renderer: Optional[AbstractRenderer] = None
    __fps_label: Optional[QLabel] = None

    def __init__(self, camera_id: str):
        super().__init__()
        self.__camera_id = camera_id
        self.__graphics_scene = QGraphicsScene(self)
        self.__graphics_view = QGraphicsView(self.__graphics_scene)
        self.__camera_output = QLabel()
        self.__graphics_scene.addWidget(self.__camera_output)
        self.__fps_label = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.__graphics_view)
        layout.addWidget(self.__fps_label)
        self.setLayout(layout)

    # Will be invoked whe widget becomes visible
    def showEvent(self, event: QShowEvent):
        self.__renderer = DefaultRendererBuilder()\
            .from_camera_id(self.__camera_id)\
            .to_camera_widget(self)\
            .build()

        self.__renderer.start_rendering()

        super().showEvent(event)

    def hideEvent(self, event: PySide2.QtGui.QHideEvent):
        if not (self.__renderer is None):
            self.__renderer.stop_rendering()

        super().hideEvent(event)

    @Slot(QPixmap, float)
    def update_camera_view(self, pixmap: QPixmap, fps: float):
        current_width = self.__graphics_view.width()
        current_height = self.__graphics_view.height()
        scaled_pixmap = pixmap.scaled(current_width, current_height, Qt.KeepAspectRatio, Qt.FastTransformation)

        self.__camera_output.setPixmap(scaled_pixmap)
        self.__camera_output.setGeometry(0, 0, current_width, current_height)
        self.__fps_label.setText('Fps: {:.2f}'.format(fps))
