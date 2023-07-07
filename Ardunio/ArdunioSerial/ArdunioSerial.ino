#include <SoftwareSerial.h>
SoftwareSerial mySerial(0, 1); // RX, TX pins for SoftwareSerial
void setup() {
  Serial.begin(9600); // Initialize the hardware serial port for debugging
  mySerial.begin(115200); // Initialize the software serial port
}
void loop() {
  if (mySerial.available()) {
    String data = mySerial.readString();
    // Process the received data here
    // Echo back the data to the serial port
    //mySerial.write(data);
    Serial.println(data);
    Serial.println("can serial");
  }
  Serial.println("test");
}
