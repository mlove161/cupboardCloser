from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap, QIcon, QPalette, QColor, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QTabWidget, \
    QGridLayout, QStackedWidget, QGraphicsDropShadowEffect, QMenu, QHBoxLayout, QLineEdit

import base64
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QMetaObject, QByteArray
import json
from PyQt6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Signal, QObject

from awscrt import mqtt
from awsiot import mqtt_connection_builder

from uuid import uuid4
import numpy as np
import cv2
import skops.io as sio

from skimage.transform import resize
from skimage.feature import hog

import sys


endpoint = "a3fn6zbxkxmi7t-ats.iot.us-east-1.amazonaws.com"
cert_filepath = "./certs/device.pem.crt"
ca_filepath = "./certs/AmazonRootCA1.pem"
key_filepath = "./certs/private.pem.key"



event = {
  "type": "IMAGE",
  "payload": "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"

}

WELCOME_LABEL = "Welcome Home."
DEVICE_LABEL = "My Devices"
HEADER_FONT = QFont("Helvetica", 30, 700)
SUBHEADER_FONT = QFont("Helvetica", 24)

# TODO: design complete topics
image_receive_topic = "test/lambda"
esp32_pub_topic = "esp32/receive"
topics = [image_receive_topic, esp32_pub_topic]

Hmodel = 240  # 480 120
Wmodel = 320  # 640 160

Hmodel = 120
Wmodel = 160

Him = 480
Wim = 640

MOTION = "Motion Detected"
NO_MOTION = "No motion Detected"

HAND = "Hand Detected"
NO_HAND = "No hand Detected"

IMAGE_HAND = ['0']
IMAGE_NO_HAND = ['1']

hand_detected = {"device": "companionApp", "type": "HAND_DETECTED", "payload": "TRUE"}
hand_not_detected = {"device": "companionApp", "type": "HAND_DETECTED", "payload": "FALSE"}
close_command = {"device": "companionApp", "type": "CLOSE_CUPBOARD", "payload": "--"}


#
# # clf name: location to the classifier to load, should be a file in AWS I guess?
# # img: array of pixels that represents an image (hopefully feeding in the pixel array should work)
def ClassifyImage(clfName, img):
    # load model
    clf = sio.load(clfName, trusted=True)

    # read image (if given an image file)
    img = cv2.imread(img)

    # pre proccessing
    resized_img = resize(img, (Hmodel, Wmodel))
    fd, hog_image = hog(resized_img,
                        orientations=9,
                        pixels_per_cell=(8, 8),
                        cells_per_block=(2, 2),
                        visualize=True,
                        channel_axis=-1)
    (x,) = fd.shape
    fd = np.reshape(fd, (1, x))

    # predict if hand or not
    guess = clf.predict(fd)  # if this fails it is probably bc HW of model is wrong

    # get probability (never figured out how to do it out)
    # probs = clf.predict_proba(fd)

    print(guess)
    return guess


class DeviceSignals(QObject):
    name_change = Signal(str)
    hand_detected = Signal()
    no_hand_detected = Signal()
    close_command_issued = Signal()
    cabinet_open = Signal()
    cabinet_closed = Signal()
    motion_detected = Signal()
    no_motion_detected = Signal()
    image_received = Signal(str)
    door_open = Signal()


class Device:
    def __init__(self, name, parent):
        self.parent = parent
        self.name = name
        self.motion_status = NO_MOTION
        self.hand_status = NO_HAND
        self.signals = DeviceSignals()

    def set_name(self, name):
        self.name = name
        print("name = " + name)
        self.signals.name_change.emit(name)


class DeviceWidget(QWidget):
    def __init__(self, parent, page_name, index):
        super().__init__(parent)
        # AHGHHHH
        self.device = Device(page_name, self)
        # self.device = None
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
        self.setStyleSheet("background-color: #FFFFFF;")
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

        checklist_page = CheckListScreen()
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
        self.add_item_widget = AddItem(self, self.add_device)

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

    def open_new_screen(self, device):
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

    def create_json_message(self, device_name, type, payload):
        pass

    def on_message_received(self, topic, payload):
        event = json.loads(payload)
        print("Message received. Payload: '{}".format(event))

        if event["type"] == "IMAGE":
            print("Image received.")
            img_data = event["payload"]
            decode_img = base64.b64decode(img_data)
            filename = "test_image.jpeg"
            if self.device_screen is not None:
                self.device_screen.device.signals.image_received.emit(img_data)
            with open(filename, 'wb') as f:
                f.write(decode_img)
            result = ClassifyImage("model7-NN-CabPeople-acc90.skops", "test_image.jpeg")
            if result == IMAGE_HAND:
                print("Success! Hand Found. Restarting timer.")
                if self.device_screen is not None:
                    self.device_screen.device.signals.hand_detected.emit()
                ## TODO: broadcast signal to change UI
                hand_detected_json = json.dumps(hand_detected)
                self.MQTT_connection.publish(topic=esp32_pub_topic,
                                             payload=hand_detected_json,
                                             qos=mqtt.QoS.AT_LEAST_ONCE)
            elif result == IMAGE_NO_HAND:
                if self.device_screen is not None:
                    self.device_screen.device.signals.no_hand_detected.emit()
                hand_not_detected_json = json.dumps(hand_not_detected)
                self.MQTT_connection.publish(topic=esp32_pub_topic,
                                             payload=hand_not_detected,
                                             qos=mqtt.QoS.AT_LEAST_ONCE)

                ## TODO: broadcast signal to change UI
                print("No hand detected.")

        if event["type"] == "DOOR_CLOSED":
            print("Cabinet door closed")
            self.device_screen.device.signals.cabinet_closed.emit()
        if event["type"] == "DOOR_OPEN":
            print("Cabinet door open")
            self.device_screen.device.signals.cabinet_open.emit()
        if event["type"] == "MOTION_DETECTED":
            print("Motion Detected")
            self.device_screen.device.signals.motion_detected.emit()
        if event["type"] == "NO_MOTION_DETECTED":
            print("No motion detected")
            self.device_screen.device.signals.no_motion_detected.emit()

    def create_MQTT_connection(self):
        # Necessary for an MQTT Connection:
        # topic to subscribe to
        # Endpoint (server address), key, cert, ca filepaths
        self.MQTT_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            port=8883,
            cert_filepath=cert_filepath,
            pri_key_filepath=key_filepath,
            ca_filepath=ca_filepath,
            client_id="test-" + str(uuid4())
        )
        # Create connection, wait until connection established
        connection = self.MQTT_connection.connect()
        connection.result()
        print("Connected!")

        ## TODO: device setup screen
        ## TODO: sub to multiple topics? for each device?

        topic = "esp32/pub"
        print("Subscribing to topic '{}'...".format(topic))
        # QOS protocol, will publish messages until the PUBACK signal is sent back
        subscribe_future, packet_id = self.MQTT_connection.subscribe(
            topic=topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self.on_message_received)
        subscribe_result = subscribe_future.result()
        print("Subscribed with {}".format(str(subscribe_result['qos'])))


class DeviceScreen(QWidget):
    def __init__(self, parent, device):
        super().__init__(parent)
        self.device = device
        self.parent = parent

        back_button_layout = QVBoxLayout()
        # layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        ## Back Button
        back_label = QLabel()
        back_icon = QPixmap('res/back_arrow.png')
        back_label.setPixmap(back_icon)
        back_label.setGeometry(0, 0, 60, 10)
        back_label.mousePressEvent = lambda event: parent.go_back()
        # back_label.setStyleSheet("border-width: 1px; border-style: solid; border-radius: 4px;")
        back_label.setMaximumSize(50, 30)
        back_button_layout.addWidget(back_label)

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

        ## Device Name/Label
        self.label = QLabel(device.name)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(SUBHEADER_FONT)
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
        self.whole_layout = QVBoxLayout()
        self.whole_layout.addLayout(back_button_layout)
        self.whole_layout.addWidget(container)
        self.whole_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add Motion/Hand Detectors to screen
        self.hand_label = QLabel()
        self.hand_detected_icon = QPixmap('./res/hand_detected.png')
        self.no_hand_detected_icon = QPixmap('./res/no_hand_detected.png')
        self.hand_label.setPixmap(self.no_hand_detected_icon)
        device.signals.hand_detected.connect(lambda: self.change_hand_icon(self.hand_detected_icon))
        device.signals.no_hand_detected.connect(lambda: self.change_hand_icon(self.no_hand_detected_icon))

        self.motion_label = QLabel()
        self.motion_detected_icon = QPixmap('./res/motion_detected.png')
        self.no_motion_detected_icon = QPixmap('./res/no_motion_detected.png')
        self.motion_label.setPixmap(self.no_motion_detected_icon)
        device.signals.motion_detected.connect(lambda: self.change_motion_icon(self.motion_detected_icon))
        device.signals.no_motion_detected.connect(lambda: self.change_motion_icon(self.no_motion_detected_icon))

        status_layout = QHBoxLayout()
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.motion_label)
        status_layout.addSpacing(120)
        status_layout.addWidget(self.hand_label)

        self.whole_layout.addLayout(status_layout)

        # Close Button
        self.close_button = QLabel()
        self.close_icon_inactive = QPixmap('./res/close_inactive')
        self.close_icon_active = QPixmap('./res/close_active.png')
        self.close_button.setPixmap(self.close_icon_inactive)
        self.close_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.close_button.mousePressEvent = None

        device.signals.cabinet_open.connect(lambda: self.activate_close_button())
        device.signals.cabinet_closed.connect(lambda: self.deactivate_close_button())
        self.whole_layout.addWidget(self.close_button)

        ## Receive Images and display in new window
        self.image_display = QLabel()
        self.img_window = QWidget()
        self.img_layout = QVBoxLayout()
        self.img_display = QLabel()
        self.img_layout.addWidget(self.img_display)
        self.img_window.setLayout(self.img_layout)

        def set_image(img: str):
            decode_img = base64.b64decode(img)
            pixmap = QPixmap()
            pixmap.loadFromData(decode_img)
            self.img_display.setPixmap(pixmap)
            self.img_window.show()

        device.signals.image_received.connect(set_image)

        self.setLayout(self.whole_layout)

    def change_hand_icon(self, hand_icon: QLabel):
        self.hand_label.setPixmap(hand_icon)

    def change_motion_icon(self, motion_icon: QLabel):
        self.motion_label.setPixmap(motion_icon)

    def activate_close_button(self):
        self.close_button.setPixmap(self.close_icon_active)
        self.close_button.mousePressEvent = lambda event: self.close_button_pressed()

    def deactivate_close_button(self):
        self.close_button.setPixmap(self.close_icon_inactive)
        self.close_button.mousePressEvent = lambda event: None

    def close_button_pressed(self):
        print("close button pressed")
        close_command_json = json.dumps(close_command)
        self.parent.MQTT_connection.publish(topic=esp32_pub_topic,
                                            payload=close_command_json,
                                            qos=mqtt.QoS.AT_LEAST_ONCE)

        self.close_button.setPixmap(self.close_icon_inactive)
        self.device.signals.close_command_issued.emit()


## TODO: implemxent troubleshooting layout, for now its just developer settings
class SettingsScreen(QWidget):
    def __init__(self, parent, device):
        super().__init__(parent)
        self.parent = parent
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


        ## Add temp JSON publishing
        message_entry = QTextEdit()
        event = json.dumps(event)
        message_entry.setText(event)
        message_send = QPushButton("Send Message")
        def publish_message(msg):
            if isinstance(msg, str):
            ## Convert from string, to JSON, back to string to publish to AWS
                msg = json.loads(msg)

            msg_json = json.dumps(msg)
            parent.MQTT_connection.publish(topic=esp32_pub_topic,
                                     payload=msg_json,
                                     qos=mqtt.QoS.AT_LEAST_ONCE)


        ## TODO: testing, add timeouts / accuracy
        message_send.clicked.connect(lambda: publish_message(message_entry.toPlainText()))
        message_layout = QHBoxLayout()
        message_layout.addWidget(message_entry)
        message_layout.addWidget(message_send)

        ## Timeout changes
        timeout = QComboBox()
        timeout_choices = ["30s", "60s"]
        for choice in timeout_choices:
            timeout.addItem(choice)

        timeout_json = {"device": "companionApp", "type": "TIMEOUT", "payload": "30s"}
        def broadcast_timeout():
            timeout_json["payload"] = timeout.currentText()
            publish_message(timeout_json)
        timeout.currentIndexChanged.connect(broadcast_timeout)
        timeout_label = QLabel("Set Timeout")
        timeout_layout = QVBoxLayout()
        timeout_layout.addWidget(timeout)
        timeout_layout.addWidget(timeout_label)

        layout = QVBoxLayout()
        layout.addWidget(back_label)

        layout.addLayout(message_layout)

        layout.addLayout(name_layout)
        layout.addLayout(timeout_layout)
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

        ## Header
        icon = QLabel()
        icon.setPixmap(QPixmap('res/question_header.png'))
        icon.resize(80,80)
        header_layout = QHBoxLayout()
        header_layout.addWidget(icon)
        header = QLabel("Troubleshooting")
        header.setFont(SUBHEADER_FONT)
        header_layout.addWidget(header)


        layout = QVBoxLayout()
        layout.addWidget(back_label)
        layout.addLayout(header_layout)

        layout.addWidget(self.add_help_tab())



        self.setLayout(layout)

    def add_help_tab(self, text = "", next_screen = None):
        container = QWidget()

        help_label = QLabel("test")
        help_label.setStyleSheet("padding: 5px;")
        right_arrow = QLabel()
        right_arrow.setPixmap(QPixmap("res/chevron_right.png"))
        container_layout = QHBoxLayout()
        container_layout.addWidget(help_label)
        container.setStyleSheet("border: 2px solid blue; border-radius: 10px; padding: 0px;")

        container_layout.addWidget(right_arrow)
        container.setLayout(container_layout)
        return container

class AddItem(QWidget):
    def __init__(self, parent, on_release):
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
        self.mouseReleaseEvent = on_release


class CheckListScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.checklists = [CheckListItem()]
        for checklist in self.checklists:
            layout.addWidget(checklist)

        ## Add button
        self.add_item_widget = AddItem(self, self.add_list)
        self.add_item_widget.container.setStyleSheet("background-color: #FFFFFFFF; border-radius: 0px; ")
        self.add_item_widget.container.setGraphicsEffect(None)

        add_layout = QVBoxLayout()
        add_layout.addWidget(self.add_item_widget)

        layout.addLayout(add_layout)

        self.setLayout(layout)
        # self.add_button =

    def add_list(self):
        new_list = []
        self.checklists.append(new_list)

class CheckListItem(QFrame):

    def __init__(self):
        super().__init__()
        collapse_signal = Signal()

        layout = QVBoxLayout()
        self.collapsed = False
        ## Header
        header_layout = QHBoxLayout()

        self.header = QLabel("Groceries")
        self.header.setFont(SUBHEADER_FONT)
        self.arrow = QLabel()
        arrow_down = QPixmap('res/chevron_down.png')
        arrow_up = QPixmap('res/chevron_up.png')
        self.arrow.setPixmap(arrow_up)


        header_layout.addWidget(self.header)
        header_layout.addStretch()
        header_layout.addWidget(self.arrow)
        layout.addLayout(header_layout)

        self.checklist_container = QWidget()
        self.checklist_content = QVBoxLayout()
        self.items = ["Bread", "Milk"]
        self.item_size = len(self.items)

        for item in self.items:
            self.checklist_content.addWidget(QCheckBox(item))

        self.checklist_container.setLayout(self.checklist_content)
        layout.addWidget(self.checklist_container)





        ## Create container for styling
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #FFD9D9D9; border-radius: 10px; padding: 10px")
        effect = QGraphicsDropShadowEffect(self.container, enabled=True, blurRadius=5)
        effect.setColor(QColor(63, 63, 63, 100))
        self.container.setGraphicsEffect(effect)
        self.container.setMaximumHeight(400)

        def toggle_content():
            ## if currently collapsed, open
            if self.collapsed:
                self.checklist_container.setVisible(True)
                self.container.setMaximumHeight(400)
                self.container.adjustSize()
                self.arrow.setPixmap(arrow_up)
            else:
                self.checklist_container.setVisible(False)
                self.container.setMaximumHeight(80)
                self.container.adjustSize()

                self.arrow.setPixmap(arrow_down)
            self.collapsed = not self.collapsed
            self.container.adjustSize()

        self.arrow.mousePressEvent = lambda event: toggle_content()



        # Add container items to screen
        self.container.setLayout(layout)

        whole_layout = QVBoxLayout()
        whole_layout.addWidget(self.container)
        self.setMinimumSize(100,100)

        self.setLayout(whole_layout)

    def title(self, title):
        pass

    def get_check_item(self, item: str):
        # item_layout = QHBoxLayout()
        check_box = QCheckBox(item)

        return check_box




def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.create_MQTT_connection()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
