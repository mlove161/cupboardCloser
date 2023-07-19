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

#define HAND_DETECTED 3
#define CLOSE_CUPBOARD 4
#define TIMEOUT_CHANGE 5
#define DOOR_OPEN 6

// const char* ssid = "Fios-P8F8p";
// const char* password = "need23haw3898wax";
const char* password = "12345678";
const char* ssid = "Maddie iPhone 12";

const int bufferSize = 1024 * 23; // 23552 bytes


// The MQTT topics that this device should publish/subscribe
#define AWS_IOT_PUBLISH_TOPIC   "esp32/pub"
#define AWS_IOT_SUBSCRIBE_TOPIC "esp32/receive"

WiFiClientSecure net = WiFiClientSecure();
MQTTClient client = MQTTClient(bufferSize);

void messageHandler(String &topic, String &message) {
  Serial.println("incoming: " + topic + " - " + message);

 StaticJsonDocument<200> doc;
 deserializeJson(doc, message);
 const char* payload = doc["payload"];
 Serial.print(payload);

 if (doc["type"] == "IMAGE" and doc["payload"] == "1") {
   digitalWrite(HAND_DETECTED, HIGH);
 }

 if (doc["type"] == "TIMEOUT_CHANGE") {
   if (doc["payload"] == "60s") {
     digitalWrite(TIMEOUT_CHANGE, HIGH);
   }
   else {
     digitalWrite(TIMEOUT_CHANGE, LOW);
   }
 }

 if (doc["type"] == "CLOSE_CUPBOARD") {
   digitalWrite(CLOSE_CUPBOARD, HIGH);
 }

 
  
 


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
    Serial.print(".A");
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

unsigned long getTime() {
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


void connectWifi() {
// ** if using access pt, comment this out

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  // *** end comment

  // ** access pt only
  // WiFi.softAP(ssid, password);
}

void cameraSetup() {
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

  #if defined(CAMERA_MODEL_ESP_EYE)
    pinMode(13, INPUT_PULLUP);
    pinMode(14, INPUT_PULLUP);
  #endif

    // camera init
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
      Serial.printf("Camera init failed with error 0x%x", err);
      return;
    }

    Serial.print("made it");

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

  Serial.print("made it");


  
}



void takePicAndPublish() {

  // Take Picture with Camera
  Serial.println("Taking picture");
  camera_fb_t * fb = NULL;
  fb = esp_camera_fb_get();  
  if(!fb) {
    Serial.println("Camera capture failed");
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

  connectWifi();

  connectAWS();

  cameraSetup();
  Serial.println("HERE WE MADE IT HERE");
  
  pinMode(HAND_DETECTED, OUTPUT);
  pinMode(CLOSE_CUPBOARD, OUTPUT);
  pinMode(TIMEOUT_CHANGE, OUTPUT);

  pinMode(DOOR_OPEN, INPUT);

  Serial.println("BEFORE THE LOOP");


  for (int i = 0; i<5; i++)
  {
    Serial.println("IN THE LOOP");

    takePicAndPublish();
    delay(2000);
  }


  // delay(2000);
  // Serial.println("Going to sleep now");
  // delay(2000);
  // esp_deep_sleep_start();
  // Serial.println("This will never be printed");




}


void loop(){
    client.loop();
    delay(1000);

}

