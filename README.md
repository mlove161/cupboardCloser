# Cupboard Closer
ECE 1896 - Cupboard Closer

# Design Introduction
The Cupboard Closer is Group 2’s solution to a common frustration: to the chagrin of mothers everywhere, cupboard doors are often left open after use. Our solution is twofold; one system, driven by a motor, closes the cupboard as required in the system, the other is a companion app that monitors the status of the cupboard. The system, once the cupboard door is open, captures images, and uses an image classification algorithm to determine if a hand is present, such that it does not close early. Additinoally, the companion app bridges the gap between the physical system, and the algorithm, while presenting information about the system to the user. 

# Design Overview
At a high level, the physical cupboard closer contains a motion sensor, a contact sensor, an ESP32-Cam, which contains a Wi-Fi transceiver and a camera, motors, an ATMega microcontroller, to control logic within the sensors, and a power regeneration circuit. These physical components drive the logic for the cupboard closer, ensuring the device can take pictures when the door is open, in order to determine if a hand is present in order to close.

 We have a companion app, that houses an image classification algorithm, in order to determine if a hand is present before automatically closing the door. This is set on a timer within the ATMega, and is reset if motion is detected, or if a hand is present. In order to determine if a hand is present, the ESP32-Cam takes a picture when the contact sensor is disconnected and keeps taking pictures until the door is closed. After this picture is taken, it is packaged into a JSON message, to be broadcast over Amazon Web Services (AWS) in an MQTT protocol. This image is then received in our companion app, processed by an image classification algorithm, and the result of the algorithm is broadcasted back to the ESP32-Cam. There, it will tell the ATMega that a hand has been detected, and the timer resets. If the timer expires, the motors will automatically close the cabinet door, and the ESP32-Cam will stop taking pictures. 
 
These modules are illustrated in the figure below, where the functionality of each component is highlighted in the diagram.

<img width="578" alt="image" src="https://github.com/mlove161/cupboardCloser/assets/107860847/3885c621-9935-46e4-9b19-cf54f3266a1a">

# Design Demos
The final functionality of the companion app is a live video of the images as seen by the ESP32-Cam. This is demonstrated at the following link: 

[![IMAGE ALT TEXT](http://img.youtube.com/vi/9qUVGNG4FbY/0.jpg)](https://youtube.com/shorts/9qUVGNG4FbY?feature=share
)

An overview of the system is demonstrated in the video below.
[![IMAGE ALT TEXT](http://img.youtube.com/vi/pi--MnRigwQ/0.jpg)](https://youtu.be/pi--MnRigwQ)
