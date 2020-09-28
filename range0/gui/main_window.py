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

import sys
from typing import Dict
from PySide2.QtWidgets import QMainWindow, QAction, QMdiArea, QDialog, QRadioButton, \
    QButtonGroup, QVBoxLayout, QPushButton, QMessageBox, QMdiSubWindow
from PySide2.QtCore import Qt

from range0.core import camera
from range0.gui import mdi_widgets


class MainWindow(QMainWindow):

    __mdi_area = None

    def __init__(self):
        super().__init__()

        self.__create_main_menu()

        self.__mdi_area = QMdiArea(parent=self)
        self.setCentralWidget(self.__mdi_area)

    def __create_main_menu(self) -> None:
        menu = self.menuBar()
        menu.setNativeMenuBar(False)

        file_menu = menu.addMenu('File')
        quit_action = QAction(text='Quit', parent=self)
        quit_action.triggered.connect(self.__quit_action_on_click)
        file_menu.addAction(quit_action)

        training_menu = menu.addMenu('Training')
        quick_training_item = QAction(text='Start quick training', parent=self)
        quick_training_item.triggered.connect(self.__start_quick_training_action_on_click)
        training_menu.addAction(quick_training_item)

    def __quit_action_on_click(self):
        sys.exit(0)

    def __start_quick_training_action_on_click(self):
        choose_camera_dialog = ChooseCameraDialog(self)
        choose_camera_dialog.setModal(True)
        if choose_camera_dialog.exec_() == QDialog.Accepted:
            camera_widget = mdi_widgets.CameraWidget(choose_camera_dialog.get_chosen_camera_id())
            camera_window = QMdiSubWindow()
            camera_window.setWidget(camera_widget)
            camera_window.setAttribute(Qt.WA_DeleteOnClose)
            self.__mdi_area.addSubWindow(camera_window)
            camera_window.show()


class ChooseCameraDialog(QDialog):
    __cameras_button_group = None
    __camera_button_index_to_cameraId: Dict[int, str] = {}
    __choose_button = None

    __chosen_camera_id: str = None

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Choose camera")

        layout = QVBoxLayout()
        self.__create_cameras_list(layout)

        self.__choose_button = QPushButton(text='Choose', parent=self)
        self.__choose_button.setEnabled(False)
        self.__choose_button.clicked.connect(self.__choose_button_on_click)
        layout.addWidget(self.__choose_button)

        self.setLayout(layout)

    def __create_cameras_list(self, layout):
        self.__cameras_button_group = QButtonGroup()
        self.__cameras_button_group.setExclusive(True)

        self.__cameras_button_group.buttonClicked.connect(lambda b: self.__choose_button.setEnabled(True))

        camera_info = camera.get_available_camera_info()

        for i in range(0, len(camera_info)):
            label = '{} ({})'.format(camera_info[i].description, camera_info[i].device_name)
            self.__camera_button_index_to_cameraId[i] = camera_info[i].id
            button = QRadioButton(text=label, parent=self)
            self.__cameras_button_group.addButton(button, i)
            layout.addWidget(button)

    def __choose_button_on_click(self):
        checked_id = self.__cameras_button_group.checkedId()
        if checked_id == -1:
            msg = QMessageBox(parent=self)
            msg.setIcon(QMessageBox.Warning)
            msg.setText('Camera was not chosen')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            self.__chosen_camera_id = self.__camera_button_index_to_cameraId[checked_id]
            self.accept()

    def get_chosen_camera_id(self):
        return self.__chosen_camera_id
