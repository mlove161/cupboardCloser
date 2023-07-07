// this sample code provided by www.programmingboss.com

#include <Arduino.h>
#define testPin 15
int t =0;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(testPin, OUTPUT);
  //Serial2.begin(9600, SERIAL_8N1, RXp2, TXp2);
}
void loop() {
  //Serial.println("hey");

  if(t==0)
  {
    digitalWrite(testPin, LOW);
    t++;
  }
  else
  {
    digitalWrite(testPin, HIGH);
    t--;
  }
  

  delay(1000);
}
/*
#include <Arduino.h>
void setup() {
  Serial.begin(115200); // Initialize the hardware serial port
}
void loop() {
  if (Serial.available()) {
    //char data = Serial.read();
    // Process the received data here
    // Echo back the data to the serial port
    Serial.write("Hi Mommy");
  }
}
*/