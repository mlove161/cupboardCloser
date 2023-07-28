#include "secrets.h"
#include "esp_camera.h"
#include <WiFiClientSecure.h>
#include <MQTTClient.h>
#include <ArduinoJson.h>
#include "WiFi.h"
#include <base64.h>
#include <EEPROM.h>


#define CAMERA_MODEL_AI_THINKER // Has PSRAM


#include "camera_pins.h"

#define HAND_DETECTED 12
#define CLOSE_CUPBOARD 13
#define TIMEOUT_CHANGE 15
#define DOOR_OPEN 14

#define FLASH_LED 4
#define WAIT_STATE 1
#define PUBLISH_PICS_STATE 2
#define HAND_DETECTED_STATE 3
#define CLOSE_CUPBOARD_STATE 4

#define on_board_LED 33

#define CLOSE 1
#define OPEN 0

// const char* ssid = "Fios-P8F8p";
// const char* password = "need23haw3898wax";
const char* password = "12345678";
const char* ssid = "Maddie iPhone 12";

const int bufferSize = 1024 * 23; // 23552 bytes
int door_open_sensor = HIGH;

// The MQTT topics that this device should publish/subscribe
#define AWS_IOT_PUBLISH_TOPIC   "esp32/pub"
#define AWS_IOT_SUBSCRIBE_TOPIC "esp32/receive"


WiFiClientSecure net = WiFiClientSecure();
MQTTClient client = MQTTClient(bufferSize);

int state = WAIT_STATE;
int next_state = WAIT_STATE;

void messageHandler(String &topic, String &message) {

  Serial.println("incoming: " + topic + " - " + message);

 StaticJsonDocument<200> doc;
 deserializeJson(doc, message);
 const char* payload = doc["payload"];
 Serial.print(payload);

  // Only act on hand messages if we're actively taking pictures.
 if (doc["type"] == "HAND_DETECTED" and state == PUBLISH_PICS_STATE) {
   if (doc["payload"] == "TRUE") {
    Serial.print("HAND DETECTED! Next state is setting pins.");
    next_state = HAND_DETECTED_STATE;
   }
   else if (doc["payload" == "FALSE"]) {
     Serial.print("HAND NOT DETECTED");
   }
 }
 


 if (doc["type"] == "TIMEOUT_CHANGE") {
   if (state != WAIT_STATE) {
     publishMessage("DEBUG", "Unable to set timeout, cupboard not in wait state.");
   }
   else if (doc["payload"] == "60s") {
     String test = doc["payload"];
     Serial.print("payload = " + test);
     digitalWrite(TIMEOUT_CHANGE, HIGH);
   }
   else if (doc["payload"] == "30s") {
     String test = doc["payload"];
     Serial.print("payload = " + test);
     digitalWrite(TIMEOUT_CHANGE, LOW);
   }
 }

 if (doc["type"] == "CLOSE_CUPBOARD") {
   next_state = CLOSE_CUPBOARD_STATE;
   digitalWrite(CLOSE_CUPBOARD, HIGH);
 }

//  if (doc["type"] == "TESTING") {
//    if (doc["payload"] == "DOOR_OPEN_LOW") {
//     door_open_sensor = LOW;
//    }
//    else if (doc["payload"] == "DOOR_OPEN_HIGH") {
//      door_open_sensor = HIGH;
//    }
//  }
}


void connectAWS()
{
  // Configure WiFiClientSecure to use the AWS IoT device credentials
  net.setCACert(AWS_CERT_CA);
  net.setCertificate(AWS_CERT_CRT);
  net.setPrivateKey(AWS_CERT_PRIVATE);

  // Connect to the MQTT broker on the AWS endpoint we defined earlier
  client.begin(AWS_IOT_ENDPOINT, 8883, net);

  // Create a message handler
  client.onMessage(messageHandler);

  Serial.print("Connecting to AWS IOT");

  while (!client.connect(THINGNAME)) {
    Serial.print(".AWS");
    delay(100);
  }

  if(!client.connected()){
    Serial.println("AWS IoT Timeout!");
    return;
  }

  // Subscribe to a topic
  client.subscribe(AWS_IOT_SUBSCRIBE_TOPIC);

  Serial.println("AWS IoT Connected!");
}

unsigned long getTime() 
{
  time_t now;
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    //Serial.println("Failed to obtain time");
    return(0);
  }
  time(&now);
  return now;
}

void publishMessage(String type, String payload)
{

  // formating json
  DynamicJsonDocument doc(20000);
  doc["type"] = type;
  doc["payload"] = payload;

  String jsonBuffer;
  Serial.println("Publishing to " + String(AWS_IOT_PUBLISH_TOPIC));
  serializeJson(doc, jsonBuffer);

  // publishing topic 
  if (!client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer)) {
    lwMQTTErr(client.lastError());
  }
  Serial.println("Published");

}

void connectWifi() 
{
// ** if using access pt, comment this out

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  int count = 0;
  int delay_time = 500;

  while (WiFi.status() != WL_CONNECTED) {
    delay(delay_time);
    Serial.print(".");
    count += delay_time;
    if (count == 5000) {
      Serial.print("Unable to connect to WiFi. Restarting. ");
      ESP.restart();
      // reset after 5 seconds
    }
  }

  Serial.println("WiFi connected");


  // ** access pt only
  // WiFi.softAP(ssid, password);
}

void cameraSetup() 
{
  // Serial.begin(115200);
  // Serial.setDebugOutput(true);
  // Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
  if(psramFound()){
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  // #if defined(CAMERA_MODEL_ESP_EYE)
  //   pinMode(13, INPUT_PULLUP);
  //   pinMode(14, INPUT_PULLUP);
  // #endif

    // camera init
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
      Serial.printf("Camera init failed with error 0x%x", err);
      return;
    }


    sensor_t * s = esp_camera_sensor_get();
    // initial sensors are flipped vertically and colors are a bit saturated
    if (s->id.PID == OV3660_PID) {
      s->set_vflip(s, 1); // flip it back
      s->set_brightness(s, 1); // up the brightness just a bit
      s->set_saturation(s, -2); // lower the saturation
    }
    // drop down frame size for higher initial frame rate
    s->set_framesize(s, FRAMESIZE_QVGA);

  #if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
    s->set_vflip(s, 1);
    s->set_hmirror(s, 1);
  #endif



  
}



void takePicAndPublish() {
  digitalWrite(FLASH_LED, HIGH);

  // Take Picture with Camera
  Serial.println("Taking picture");
  camera_fb_t * fb = NULL;
  fb = esp_camera_fb_get();  
  if(!fb) {
    Serial.println("Camera capture failed");
    ESP.restart();
    return;
  }

  const char *data = (const char *)fb->buf;
  // Image metadata.  Yes it should be cleaned up to use printf if the function is available
  Serial.print("Size of image:");
  Serial.println(fb->len);
  Serial.print("Shape->width:");
  Serial.print(fb->width);
  Serial.print("height:");
  Serial.println(fb->height);

  String encoded = base64::encode(fb->buf, fb->len);
  Serial.println("data:");
  Serial.println(encoded);

  publishMessage("IMAGE", encoded);
  // publishMessage("test produce img", "test");


    // Killing cam resource
  esp_camera_fb_return(fb);

}

bool lwMQTTErr(lwmqtt_err_t reason)
{
  if (reason == lwmqtt_err_t::LWMQTT_SUCCESS)
  {
    Serial.print("Success");
    return 1;
  }
  else 
    return 0;
}




void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  pinMode(HAND_DETECTED, OUTPUT);
  pinMode(CLOSE_CUPBOARD, OUTPUT);
  pinMode(TIMEOUT_CHANGE, OUTPUT);
  pinMode(DOOR_OPEN, INPUT);
  pinMode(FLASH_LED, OUTPUT);


  connectWifi();

  connectAWS();

  cameraSetup();
  


 // TESTING
  
  Serial.println("BEFORE THE LOOP");




}


void loop(){
  client.loop();
  state = next_state;
  digitalWrite(HAND_DETECTED, HIGH);
  int door_open_sensor = digitalRead(DOOR_OPEN);

  if (door_open_sensor == LOW)
  {
    digitalWrite(16, LOW);
  }
  else if (door_open_sensor == HIGH) {
    digitalWrite(16, HIGH);
  }

  if (state == WAIT_STATE)
  {
    digitalWrite(CLOSE_CUPBOARD, LOW);
    digitalWrite(FLASH_LED, LOW);


    Serial.println("in waiting state");
    int door_open_sensor = digitalRead(DOOR_OPEN);
    Serial.println("door = ");
    Serial.print(door_open_sensor);
    if (door_open_sensor == LOW) 
    {
      next_state = PUBLISH_PICS_STATE;
    }
  }

  else if (state == PUBLISH_PICS_STATE)
  {
    Serial.print("in publish pics state");
    digitalWrite(HAND_DETECTED, HIGH );
    digitalWrite(FLASH_LED, HIGH);
    takePicAndPublish();
    int door_open_sensor = digitalRead(DOOR_OPEN);
  }

  else if (state == HAND_DETECTED_STATE)
  {
    
    Serial.print("in hand detected state, next state = take pics state");
    digitalWrite(HAND_DETECTED, LOW);
    delay(500);
    next_state = PUBLISH_PICS_STATE;
  }
  else if (state == CLOSE_CUPBOARD_STATE) 
  {
    Serial.print("Closing cupboard, next state = wait state");
    digitalWrite(CLOSE_CUPBOARD, HIGH);
    digitalWrite(FLASH_LED, LOW);
    delay(500);
    
  }

  if (digitalRead(DOOR_OPEN) == CLOSE) {
    next_state = WAIT_STATE;
  }



}

