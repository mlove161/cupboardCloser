//close logic
#define Motion 3//2
#define DoorContact 2//3

//debugging
#define buzzer 4//11
#define blueLED 12
#define greenLED 13
#define LED3 A2
#define LED2 A1
#define LED1 A0

//ESP
#define doorIsOpenToESP 11
#define timeOutFromESP 10
#define sendCloseFromESP 9
#define HandDetected 8//AlgClass 4

//Motor
#define EnableMotor  6
#define doorPwm 5
//oc0b

//Relay
#define relay_2 A5
#define relay_1 A4
#define det_relay A3

int currState  = 0; // current state of closing
int nextState  = 0; // current state of closing

int doorState;
int motionState;

int timeoutTime = 6000;
int okHandTime = 100;
int delayTime = 10;

int oneSec = 25;
int delayCount = 0;

int cameraAlgOut = 0;
int closeIt = 0;
int counter = 0;
int counter2 = 0;
int relayDetVolt = 0;

bool manuelCloseFlag = false;

void setup() {
  Serial.begin(9600);

  //close logic
  pinMode(Motion, INPUT);
  pinMode(DoorContact, INPUT);
  
  //debugging
  pinMode(buzzer, OUTPUT);
  pinMode(blueLED, OUTPUT);
  pinMode(greenLED, OUTPUT);
  pinMode(LED3, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED1, OUTPUT);

  //ESP
  pinMode(doorIsOpenToESP, OUTPUT);
  pinMode(timeOutFromESP, INPUT);
  pinMode(sendCloseFromESP, INPUT);
  pinMode(HandDetected, INPUT);

  //Motor
  pinMode(EnableMotor, OUTPUT);
  pinMode(doorPwm, OUTPUT);

  //Relay
  pinMode(relay_2, OUTPUT);
  pinMode(relay_1, OUTPUT);
  pinMode(det_relay, INPUT);
}

void loop() {
  digitalWrite(EnableMotor, HIGH);

  int doorOp = digitalRead(DoorContact);
  motionState = digitalRead(Motion);
  digitalWrite(doorIsOpenToESP, doorOp);

  if (motionState == HIGH) {
    digitalWrite(greenLED, HIGH);
  } else {
    digitalWrite(greenLED, LOW);
  }
  cameraAlgOut = digitalRead(HandDetected);
  if (cameraAlgOut == HIGH) {
    digitalWrite(blueLED, LOW);
  } else {
    digitalWrite(blueLED, HIGH);
  }

  int timeout = digitalRead(timeOutFromESP);
  if(timeout == 0 )
  {
    timeoutTime = 3000;//6000; //30 sec really 25 sec
  }
  else
  {
    timeoutTime = 12000; //60 sec really 50 sec
  }

  //------------------------------
  currState = nextState;

  if(currState == 0) //closed
  {
    analogWrite(relay_2, 255);
    analogWrite(relay_1, 0);
    analogWrite(doorPwm, 0);

    Serial.println("State is 0");
    doorState = digitalRead(DoorContact);
    if(doorState == LOW)
    {
      if(manuelCloseFlag == true)
      {
        nextState = 2;
        Serial.println("Next State: 2");
        manuelCloseFlag = false;
      }
      else
      {
        nextState = 1;
        Serial.println("Next State: 1");
      }
    }
  }
  else if(currState == 1) //opening
  {
    analogWrite(relay_2, 0);
    analogWrite(relay_1, 0);
    analogWrite(doorPwm, 0);

    Serial.println("State is 1");

    relayDetVolt = analogRead(det_relay);
    if(relayDetVolt <=150) //TODO Input level
    {
      nextState = 2;
      Serial.println("Next State: 2");
    }
    else
    {
      nextState = 1;
      Serial.println("Next State: 1");
    }
  }
  else if(currState == 2) //open 
  {
    analogWrite(relay_2, 255);
    //analogWrite(relay_1, 0); don't care
    analogWrite(doorPwm, 0);

    Serial.println("State is 2");
    //TODO get camera Alg  - cameraAlgOut = ?
    cameraAlgOut = digitalRead(HandDetected); //0 is hand 1 is not
    motionState = digitalRead(Motion);
    closeIt = digitalRead(sendCloseFromESP);

    if(closeIt) 
    {
      counter2 += delayTime;
    }
    else
    {
      counter2 = 0;
      
      if(motionState == HIGH or cameraAlgOut == LOW)
      {
        counter = 0;
        Serial.println("Activity Detected");
      }
      else
      {
        counter += delayTime;
        Serial.println("No Activity Detected");
      }
    }

    //---
    doorState = digitalRead(DoorContact);
    if(doorState == 1)
    {
      manuelCloseFlag = true;
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
  else if(currState == 3) //closing
  {
    delayCount++;

    //Give command to motor
    analogWrite(relay_2, 0);
    analogWrite(relay_1, 255);

    if(delayCount <= oneSec)
    {
      analogWrite(doorPwm, 255); //60% duty cycle TODO, correct?
    }
    else
    {
      analogWrite(doorPwm, 0);
    }
    if(delayCount >= 2*oneSec)
    {
      delayCount = 0;
    }
    //TCCR0B = TCCR0B & B11111000 | B00000101; // for PWM frequency of 61.04 Hz

    digitalWrite(buzzer, LOW);

    Serial.println("State is 3");
    
    doorState = digitalRead(DoorContact);
    if(doorState == 0)
    {
      nextState = 3;
      Serial.println("Next State: 3");
    }
    else
    {
      nextState = 0;
      Serial.println("Next State: 0");
      analogWrite(doorPwm, 0);
    }
  }
  delay(delayTime);
}
