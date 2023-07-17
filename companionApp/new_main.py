from awscrt import mqtt, http
from awsiot import mqtt_connection_builder
from uuid import uuid4

from enum import Enum
from PyQt6.QtCore import Qt, QObject
from PyQt6.QtGui import QPixmap, QIcon, QPalette, QColor, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QTabWidget, \
    QGridLayout, QStackedWidget, QGraphicsDropShadowEffect, QMenu, QHBoxLayout, QLineEdit
from PySide6.QtCore import QObject,Signal


import sys
import threading
import time
import json

import certs

WELCOME_LABEL = "Welcome Home."
DEVICE_LABEL = "My Devices"
HEADER_FONT = QFont("Helvetica", 30, 700)
SUBHEADER_FONT = QFont("Helvetica", 24)

class MotionStatus(Enum):
    MOTION = "Motion Detected.",
    NO_MOTION = "No motion Detected."


class HandStatus(Enum):
    HAND = "Hand Detected.",
    NO_HAND = "No hand Detected."


class DeviceSignals(QObject):
    name_change = Signal(str)


class Device:
    def __init__(self, name, parent):
        self.parent = parent
        self.name = name
        self.motion_status = MotionStatus.NO_MOTION
        self.hand_status = HandStatus.NO_HAND
        self.signals = DeviceSignals()

    def set_name(self, name):
        self.name = name
        print("name = " + name)
        self.signals.name_change.emit(name)




class DeviceWidget(QWidget):
    def __init__(self, parent, page_name, index):
        super().__init__(parent)
        self.device = Device(page_name, self)
        self.index = index
        item_layout = QVBoxLayout()

        self.context_menu = QMenu(self)
        delete_device = self.context_menu.addAction("Delete Device")
        delete_device.triggered.connect(lambda: parent.remove_device(self))

        ## Create Device Layout
        cabinet_image = QPixmap('res/cabinet.png')
        cabinet_image = cabinet_image.scaledToHeight(250)
        self.cabinet_label = QLabel()
        self.cabinet_label.setPixmap(cabinet_image)
        self.cabinet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        item_layout.addWidget(self.cabinet_label)
        device_label = QLabel(str(self.device.name))
        self.device.signals.name_change.connect(device_label.setText)
        device_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_layout.addWidget(device_label)

        ## Create container for styling
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #FFD9D9D9; border-radius: 10px;")
        effect = QGraphicsDropShadowEffect(self.container, enabled=True, blurRadius=5)
        effect.setColor(QColor(63, 63, 63, 100))
        self.container.setGraphicsEffect(effect)

        # Add container items to screen
        self.container.setLayout(item_layout)

        whole_layout = QVBoxLayout()
        whole_layout.addWidget(self.container)
        self.setLayout(whole_layout)
        self.mouseReleaseEvent = lambda event: parent.open_new_screen(self.device)

    def contextMenuEvent(self, event):
        # Show the context menu
        self.context_menu.exec(event.globalPos())


## TODO: add mqtt listeners/publishers
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.device_screen = None
        self.setWindowTitle("Cupboard Closer")
        self.resize(500, 600)
        self.current_screen = None
        self.settings_screen = None
        self.devices = [DeviceWidget(self, "Pantry", 0)]
        self.device_count = len(self.devices)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.South)
        self.setCentralWidget(self.tab_widget)

        self.stacked_widget = QStackedWidget()

        checklist_page = QWidget()
        progress_page = QWidget()

        home_icon = QIcon("./res/home_icon.png")
        checklist_icon = QIcon("./res/checklist_icon.png")
        progress_icon = QIcon("./res/progress_icon.png")
        self.tab_widget.addTab(self.stacked_widget, home_icon, "")
        self.tab_widget.addTab(checklist_page, checklist_icon, "")
        self.tab_widget.addTab(progress_page, progress_icon, "")

        ## Headers
        self.home_layout = QVBoxLayout()

        self.welcome_label = QLabel(WELCOME_LABEL)
        self.welcome_label.setFont(HEADER_FONT)
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.home_layout.addWidget(self.welcome_label)
        self.device_label = QLabel(DEVICE_LABEL)
        self.device_label.setFont(SUBHEADER_FONT)
        self.device_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.home_layout.addWidget(self.device_label)

        self.grid_layout = QGridLayout()
        self.home_layout.addLayout(self.grid_layout)

        ## Add button
        self.add_item_widget = AddItem(self)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.home_layout)
        self.stacked_widget.addWidget(self.main_widget)

        self.show_main_screen()

    def show_main_screen(self):
        row = 0
        col = 0
        if len(self.devices) > 0:
            for device in self.devices:
                if (col == 2):
                    col = 0
                    row += 1
                self.grid_layout.addWidget(device, row, col)
                col += 1

            if col == 2:
                col = 0
                row += 1
        self.grid_layout.addWidget(self.add_item_widget, row, col)

    # TODO: addItem button press func
    def add_device(self, device_name="New Device"):
        self.devices.append(DeviceWidget(self, "New Device", self.device_count))
        self.device_count += 1
        self.show_main_screen()

    def remove_device(self, device: DeviceWidget):
        self.devices.remove(device)
        self.device_count -= 1
        self.grid_layout.removeWidget(self.add_item_widget)
        self.show_main_screen()

    def open_new_screen(self, device: Device):
        # if self.current_screen:
        #     self.stacked_widget.removeWidget(self.current_screen)

        self.device_screen = DeviceScreen(self, device)
        self.current_screen = self.device_screen
        self.stacked_widget.addWidget(self.current_screen)
        self.stacked_widget.setCurrentWidget(self.current_screen)

    def go_back(self):
        self.stacked_widget.setCurrentWidget(self.main_widget)
        self.current_screen = None

    def go_back_device_help(self):
        print("back called")
        self.stacked_widget.setCurrentWidget(self.device_screen)
        self.current_screen = None

    # TODO: implement troubleshooting
    def open_question_screen(self, device):
        self.current_screen = QuestionScreen(self, device)
        self.stacked_widget.addWidget(self.current_screen)
        self.stacked_widget.setCurrentWidget(self.current_screen)

    def open_settings_screen(self, device):
        # if self.current_screen:
        #     self.stacked_widget.removeWidget(self.current_screen)
        self.current_screen = SettingsScreen(self, device)
        self.stacked_widget.addWidget(self.current_screen)
        self.stacked_widget.setCurrentWidget(self.current_screen)


class DeviceScreen(QWidget):
    def __init__(self, parent, device: Device):
        super().__init__(parent)

        layout = QVBoxLayout()
        # layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        ## Back Button
        back_label = QLabel()
        back_icon = QPixmap('res/back_arrow.png')
        back_label.setPixmap(back_icon)
        back_label.setGeometry(0, 0, 60, 10)
        back_label.mousePressEvent = lambda event: parent.go_back()
        # back_label.setStyleSheet("border-width: 1px; border-style: solid; border-radius: 4px;")
        back_label.setMaximumSize(50, 30)
        layout.addWidget(back_label)

        ## Device Screen
        q_button = QLabel()
        q_icon = QPixmap('res/question.png')
        q_button.setPixmap(q_icon)
        q_button.mousePressEvent = lambda event: parent.open_question_screen(device)

        settings_button = QLabel()
        settings_icon = QPixmap('res/settings.png')
        settings_button.setPixmap(settings_icon)
        settings_button.mousePressEvent = lambda event: parent.open_settings_screen(device)
        settings_button.resize(settings_button.sizeHint())

        ## Create cabinet container for styling
        cabinet_layout = QVBoxLayout()
        cabinet_label = QLabel()
        cabinet_icon = QPixmap('res/cabinet.png')
        cabinet_icon = cabinet_icon.scaledToHeight(300)

        cabinet_label.setPixmap(cabinet_icon)
        cabinet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(q_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(settings_button)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Device Name/Label
        self.label = QLabel(device.name)
        device.signals.name_change.connect(self.label.setText)

        # Cabinet Button Layout
        cabinet_layout.addLayout(buttons_layout)
        cabinet_layout.addWidget(cabinet_label)
        cabinet_layout.addWidget(self.label)
        cabinet_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QWidget()
        container.setMaximumWidth(cabinet_icon.width() + 10)
        container.setStyleSheet("background-color: #FFD9D9D9; border-radius: 10px;")
        container.setLayout(cabinet_layout)

        # Add Cabinet Widget to screen
        whole_layout = QVBoxLayout()
        whole_layout.addWidget(container)
        whole_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add Motion/Hand Detectors to screen
        hand_detected_label = QLabel()
        hand_detected_icon = QPixmap('./res/hand_detected.png')
        hand_detected_label.setPixmap(hand_detected_icon)

        no_hand_detected_label = QLabel()
        no_hand_detected_icon = QPixmap('./res/no_hand_detected.png')
        no_hand_detected_label.setPixmap(no_hand_detected_icon)

        motion_detected_label = QLabel()
        motion_detected_icon = QPixmap('./res/motion_detected.png')
        motion_detected_label.setPixmap(motion_detected_icon)

        no_motion_detected_label = QLabel()
        no_motion_detected_icon = QPixmap('./res/no_motion_detected.png')
        no_motion_detected_label.setPixmap(no_motion_detected_icon)

        status_layout = QHBoxLayout()
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # status_layout.addWidget()

        if device.motion_status == MotionStatus.NO_MOTION:
            status_layout.addWidget(no_motion_detected_label)
        else:
            status_layout.addWidget(motion_detected_label)

        status_layout.addSpacing(120)

        if device.hand_status == HandStatus.NO_HAND:
            status_layout.addWidget(no_hand_detected_label)
        else:
            status_layout.addWidget(hand_detected_label)

        whole_layout.addLayout(status_layout)

        layout.addLayout(whole_layout)

        self.setLayout(layout)


## TODO: implement troubleshooting layout, for now its just developer settings
class SettingsScreen(QWidget):
    def __init__(self, parent, device):
        super().__init__(parent)
        input_device_name = QLineEdit()
        input_device_name.setText(device.name)
        device.signals.name_change.connect(input_device_name.setText)
        input_device_button = QPushButton("Set")
        input_device_button.clicked.connect(lambda: device.set_name(input_device_name.text()))
        name_layout = QHBoxLayout()
        name_layout.addWidget(input_device_name)
        name_layout.addWidget(input_device_button)

        ## Back Button
        back_label = QLabel()
        back_icon = QPixmap('res/back_arrow.png')
        back_label.setPixmap(back_icon)
        back_label.setGeometry(0, 0, 60, 10)
        back_label.mousePressEvent = lambda event: parent.go_back_device_help()
        # back_label.setStyleSheet("border-width: 1px; border-style: solid; border-radius: 4px;")
        back_label.setMaximumSize(50, 30)

        layout = QVBoxLayout()
        layout.addWidget(back_label)

        layout.addLayout(name_layout)
        self.setLayout(layout)


class QuestionScreen(QWidget):
    def __init__(self, parent, device):
        super().__init__(parent)
        ## Back Button
        back_label = QLabel()
        back_icon = QPixmap('res/back_arrow.png')
        back_label.setPixmap(back_icon)
        back_label.setGeometry(0, 0, 60, 10)
        back_label.mousePressEvent = lambda event: parent.go_back_device_help()
        # back_label.setStyleSheet("border-width: 1px; border-style: solid; border-radius: 4px;")
        back_label.setMaximumSize(50, 30)

        layout = QVBoxLayout()
        layout.addWidget(back_label)
        layout.addWidget(QLabel("Troubleshooting"))
        self.setLayout(layout)


class AddItem(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        item_layout = QVBoxLayout()

        ## Create Device Layout
        add_image = QPixmap('res/add_device.png')
        self.add_label = QLabel()
        self.add_label.setPixmap(add_image)
        self.add_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        item_layout.addWidget(self.add_label)

        ## Create container for styling
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #FFD9D9D9; border-radius: 10px;")
        effect = QGraphicsDropShadowEffect(self.container, enabled=True, blurRadius=5)
        effect.setColor(QColor(63, 63, 63, 100))
        self.container.setGraphicsEffect(effect)

        # Add container items to screen
        self.container.setLayout(item_layout)

        whole_layout = QVBoxLayout()
        whole_layout.addWidget(self.container)
        self.setLayout(whole_layout)
        self.mouseReleaseEvent = parent.add_device


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())