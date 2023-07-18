import base64
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QObject
import sys
import json
from PyQt6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Signal, QObject
from PIL import Image
import certs


from awscrt import mqtt
from awsiot import mqtt_connection_builder
from uuid import uuid4
import numpy as np
from sklearn import svm
import cv2
import skops.io as sio

from skimage.transform import resize
from skimage.feature import hog

Hmodel =   240#480 120
Wmodel =  320#640 160

Hmodel =   120
Wmodel =   160

Him = 480
Wim = 640

topic = "test/lambda"

# clf name: location to the classifier to load, should be a file in AWS I guess?
# img: array of pixels that represents an image (hopefully feeding in the pixel array should work)
def ClassifyImage(clfName, img):
    #load model
    clf = sio.load(clfName, trusted=True)

    #read image (if given an image file)
    img = cv2.imread(img)

    # pre proccessing
    resized_img = resize(img, (Hmodel, Wmodel))
    fd, hog_image = hog(resized_img,
                    orientations=9,
                    pixels_per_cell=(8, 8),
                    cells_per_block=(2, 2),
                    visualize=True,
                    channel_axis = -1)
    (x,) = fd.shape
    fd = np.reshape(fd, (1, x))

    #predict if hand or not
    guess = clf.predict(fd) # if this fails it is probably bc HW of model is wrong

    #get probability (never figured out how to do it out)
    #probs = clf.predict_proba(fd)

    print(guess)
    return guess

class UISignals(QObject):
    received_message = Signal(str)
    enter_device_screen = Signal()


class Device(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.device_widget = QPushButton()
        device_icon = QIcon("./res/cabinet.png")
        self.device_widget.setIcon(device_icon)
        self.device_widget.clicked.connect(self.on_device_clicked)

    def get_device_widget(self):
        return self.device_widget

    def show_device_page(self):

        self.device_page = QWidget()
        self.device_layout = QVBoxLayout()
        self.device_page.setLayout(self.device_layout)
        # TODO: hide and show windows as buttons are pressed
        # parent.setCentralWidget(self.device_page)

    def on_device_clicked(self):
        print("Opening Device")
        self.show_device_page()


class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.status = None

    def home_page(self):

        home = QWidget()
        layout = QVBoxLayout()
        main_message = QLabel("Welcome Home, Madeline")
        layout.addWidget(main_message)
        self.status = QTextEdit()
        self.status.setReadOnly(True)

        layout.addWidget(self.status)
        # self.devices.append(Device(self))
        device_layout = QGridLayout()
        # for device in self.devices:
        #     if device is not None:
        #         device_layout.addWidget(device.get_device_widget())

        # TODO: on device click, go to page for device

        layout.addLayout(device_layout)

        home.setLayout(layout)
        return home


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.home_screen = None
        self.devices = []
        self.setWindowTitle("My Application")
        self.resize(800, 600)
        self.current_screen = None

        # create home bar
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.South)

        # create and add pages, TODO: separate into functions
        # page1 = self.show_home_screen()
        page1 = QWidget()
        page2 = QWidget()
        page3 = QWidget()
        page4 = QWidget()

        home_icon = QIcon("./res/home_icon.png")
        checklist_icon = QIcon("./res/checklist_icon.png")
        progress_icon = QIcon("./res/progress_icon.png")
        # self.tab_widget.setStyleSheet("::tab{padding-left: -15px;}")
        self.tab_widget.addTab(page1, home_icon, "")
        self.tab_widget.addTab(page2, checklist_icon, "")
        self.tab_widget.addTab(page3, progress_icon, "")

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)


        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def show_home_screen(self):
        self.home_screen = HomeScreen(self)
        self.setCentralWidget(self.current_screen)




    def create_MQTT_connection(self):

        MQTT_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=certs.endpoint,
            port=8883,
            cert_filepath=certs.cert_filepath,
            pri_key_filepath=certs.key_filepath,
            ca_filepath=certs.ca_filepath,
            client_id="test-" + str(uuid4())

        )

        # Create connection, wait until connection established
        connection = MQTT_connection.connect()
        connection.result()
        print("Connected!")


        print("Subscribing to topic '{}'...".format(topic))
        # QOS protocol, will publish messages until the PUBACK signal is sent back

        def on_message_received(topic, payload):
            event = json.loads(payload)

            print("Message received. Payload: '{}".format(event))
            img_data = event["payload"]
            decode_img = base64.b64decode(img_data)
            filename = "test_image.jpeg"
            with open(filename, 'wb') as f:
                f.write(decode_img)
            ClassifyImage("model7-NN-CabPeople-acc90.skops", "test_image.jpeg")

        subscribe_future, packet_id = MQTT_connection.subscribe(
            topic=topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_message_received)

        subscribe_result = subscribe_future.result()
        print("Subscribed with {}".format(str(subscribe_result['qos'])))



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.create_MQTT_connection()
    # mock_receiver(certs.event)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

