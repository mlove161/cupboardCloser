#define Motion 2
#define DoorContact 3
#define AlgClass 4
#define buzzer 11
#define blueLED 12
#define greenLED 13
int pinStateCurrent   = LOW; // current state of pin
int pinStatePrevious  = LOW; // previous state of pin
int currState  = 0; // current state of closing
int nextState  = 0; // current state of closing

int doorState;
int motionState;

int timeoutTime = 10;
int okHandTime = 6;

int cameraAlgOut = 0;
int counter = 0;
int counter2 = 0;

void setup() {
  Serial.begin(9600);
  pinMode(Motion, INPUT);
  pinMode(DoorContact, INPUT);
  pinMode(AlgClass, INPUT);

  pinMode(buzzer, OUTPUT);
  pinMode(blueLED, OUTPUT);
  pinMode(greenLED, OUTPUT);

}

void loop() {
  pinStatePrevious = pinStateCurrent; // store old state
  pinStateCurrent = digitalRead(Motion);   // read new state
  /*
  if (pinStatePrevious == LOW && pinStateCurrent == HIGH) {   // pin state change: LOW -> HIGH
    Serial.println("Motion detected!");
    // TODO: turn on alarm, light or activate a device ... here
    digitalWrite(greenLED, HIGH);
  }
  else
  if (pinStatePrevious == HIGH && pinStateCurrent == LOW) {   // pin state change: HIGH -> LOW
    Serial.println("Motion stopped!");
    // TODO: turn off alarm, light or deactivate a device ... here
    digitalWrite(greenLED, LOW);
  }
  */
  motionState = digitalRead(Motion);
  if (motionState == HIGH) {
    // turn LED on:
    digitalWrite(greenLED, HIGH);
  } else {
    // turn LED off:
    digitalWrite(greenLED, LOW);
  }
  cameraAlgOut = digitalRead(AlgClass);
  if (cameraAlgOut == HIGH) {
    // turn LED on:
    digitalWrite(blueLED, LOW);
  } else {
    // turn LED off:
    digitalWrite(blueLED, HIGH);
  }
  //------------------------------
  currState = nextState;

  if(currState == 0)
  {
    Serial.println("State is 0");
    doorState = digitalRead(DoorContact);
    if(doorState == LOW)
    {
      nextState = 1;
      Serial.println("Next State: 1");
    }
  }
  else if(currState == 1)
  {
    Serial.println("State is 1");
    nextState = 2;
    Serial.println("Next State: 2");
    //TODO power on camera?
  }
  else if(currState == 2)
  {
    Serial.println("State is 2");
    //TODO get camera Alg  - cameraAlgOut = ?
    cameraAlgOut = digitalRead(AlgClass);
    if(false) //cameraAlgOut == 2
    {
      counter2 += 2;
    }
    else
    {
      counter2 = 0;
      motionState = digitalRead(Motion);
      if(motionState == HIGH or cameraAlgOut == LOW)
      {
        counter = 0;
        Serial.println("Activity Detected");
      }
      else
      {
        counter++;
        Serial.println("No Activity Detected");
      }
    }

    //---
    doorState = digitalRead(DoorContact);
    if(doorState == 1)
    {
      nextState = 0;
      Serial.println("Next State: 0");
    }
    else if (counter >=timeoutTime or counter2>=okHandTime)
    {
      counter = 0;
      counter2 = 0;

      nextState = 3;
      Serial.println("Next State: 3");
      digitalWrite(buzzer, HIGH);
    }
    else
    {
      nextState = 2;
    }
  }
  else if(currState == 3)
  {
    digitalWrite(buzzer, LOW);
    Serial.println("State is 3");
    //TODO Buzz buzzer
    //TODO give command to motor
    nextState = 4; 
    Serial.println("Next State: 4");
  }
  else if(currState == 4)
  {
    Serial.println("State is 4");
    doorState = digitalRead(DoorContact);
    if(doorState == 0)
    {
      nextState = 4;
      Serial.println("Next State: 4");
    }
    else
    {
      nextState = 0;
      Serial.println("Next State: 0");
    }
  }
  delay(1000);
}
