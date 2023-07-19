#include <SoftwareSerial.h>

// constants won't change. They're used here to set pin numbers:
const int YellowbuttonPin = 2;  // the number of the pushbutton pin
const int BlackbuttonPin = 3;
const int BluebuttonPin = 4;

const int BlueledPin = 12;    // the number of the LED pin

// variables will change:
int buttonState = 0;  // variable for reading the pushbutton status


void setup() {
  Serial.begin(115200); // Initialize the hardware serial port for debugging

  // initialize the LED pin as an output:
  pinMode(BlueledPin, OUTPUT);
  // initialize the pushbutton pin as an input:
  pinMode(YellowbuttonPin, INPUT);
  pinMode(BlackbuttonPin, INPUT);
  pinMode(BluebuttonPin, INPUT);
}

void loop() {
  // read the state of the pushbutton value:
  buttonState = digitalRead(BlackbuttonPin);

  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  if (buttonState == HIGH) {
    // turn LED on:
    digitalWrite(BlueledPin, HIGH);
  } else {
    // turn LED off:
    digitalWrite(BlueledPin, LOW);
  }
}



