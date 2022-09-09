#include <OneWire.h>
#include <DallasTemperature.h>
#include <RF24.h>
#include <RF24_config.h>
#include <nRF24L01.h>
#include <printf.h>

// Relay Board
#define LED_PIN1 36
#define LED_PIN2 37
#define LED_PIN3 38
#define LED_PIN4 39
#define LED_PIN5 40
#define LED_PIN6 41
// Temp Sensor
#define TEMP_SENSE_PIN 31
#define ONE_MIN  1000 //60000 // 1 Minute Delay for Temp Sensor
#define MAX_TEMP 29 // 50C
#define MIN_TEMP 28 // 40C
// Fan Pins
#define FAN_PIN1 35
#define FAN_PIN2 34

// NRF24L01: CE, CSN
RF24 radio(7, 8);
// OneWire for Temperature Sensors
OneWire oneWire(TEMP_SENSE_PIN);
// Temperature Sensors
DallasTemperature sensors(&oneWire);

// Master Control class to handle all the logic for the arduino
class MasterControl {
  public: 
    MasterControl(RF24 radio_instance, DallasTemperature temp_sensors) : _radio(&radio_instance), _tempSensors(&temp_sensors)  {};
    void InitialSetup(); 
    void RecieveMessage();
    void ToggleFans(int toggle);
  private:
    RF24* _radio;
    DallasTemperature* _tempSensors;
    unsigned long _prevMillis = 0;
    unsigned long _interval = ONE_MIN;
    bool _fansActivated = false;
};

// Setup all the required states
void MasterControl::InitialSetup() {
  Serial.begin(9600);
  pinMode(LED_PIN1, OUTPUT);
  pinMode(LED_PIN2, OUTPUT);
  pinMode(LED_PIN3, OUTPUT);
  pinMode(LED_PIN4, OUTPUT);
  pinMode(LED_PIN5, OUTPUT);
  pinMode(LED_PIN6, OUTPUT);
  pinMode(FAN_PIN1, OUTPUT);
  pinMode(FAN_PIN2, OUTPUT);
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(0x76);
  const uint64_t pipe = (0xE8E8F0F0E1LL);
  radio.openReadingPipe(1, pipe);
  radio.enableDynamicPayloads();
  radio.enableAckPayload();
  radio.startListening();
  radio.powerUp();
  _tempSensors->begin();
}

// Recieve the Message from the RaspberryPi
void MasterControl::RecieveMessage() {
  while (!radio.available()) {
    unsigned long currentMillis = millis();
    // create a timer to check the temperature sensor every x minutes/seconds..
    if((currentMillis - _prevMillis) > _interval) {
      // call sensors.requestTemperatures() to issue a global temperature 
      _prevMillis = currentMillis;
      sensors.requestTemperatures(); // Send the command to get temperature readings 
      float currentTemp = sensors.getTempCByIndex(0);
      // If the Temperature is above 50C, Initiate Fans
      if(currentTemp > MAX_TEMP && !_fansActivated) {
        ToggleFans(HIGH);
        _fansActivated = true;
      }
      else if(currentTemp < MIN_TEMP && _fansActivated) {
        ToggleFans(LOW);
        _fansActivated = false;
      }
      
      // If Fans Initiated and Temp falls below 40C, Deactivate Fans
    }
    delay(25 / 100);
  }

  if (radio.available()) {
    char recieved_message[32] = { 0 };
    radio.read(recieved_message, sizeof(recieved_message));
    String response_string = String(recieved_message);

    if (response_string == "Master-Socket-1 0") {
      Serial.println("Turning off Master-Socket-1");
      digitalWrite(LED_PIN1, LOW);
    } else if (response_string == "Master-Socket-1 1") {
      digitalWrite(LED_PIN1, HIGH);
    } else if (response_string == "Master-Socket-2 0") {
      digitalWrite(LED_PIN2, LOW);
    } else if (response_string == "Master-Socket-2 1") {
      digitalWrite(LED_PIN2, HIGH);
    } else if (response_string == "Master-Socket-3 0") {
      digitalWrite(LED_PIN3, LOW);
    } else if (response_string == "Master-Socket-3 1") {
      digitalWrite(LED_PIN3, HIGH);
    } else if (response_string == "Master-Socket-4 1") {
      digitalWrite(LED_PIN4, HIGH);
    } else if (response_string == "Master-Socket-4 0") {
      digitalWrite(LED_PIN4, LOW);
    } else if (response_string == "Master-Socket-5 1") {
      digitalWrite(LED_PIN5, HIGH);
    } else if (response_string == "Master-Socket-5 0") {
      digitalWrite(LED_PIN5, LOW);
    } else if (response_string == "Master-Socket-6 1") {
      digitalWrite(LED_PIN6, HIGH);
    } else if (response_string == "Master-Socket-6 0") { 
      digitalWrite(LED_PIN6, LOW);
    } else {
      Serial.println("Error, Recieved a different Message...");
    }
    delay(25);
  }
}

void MasterControl::ToggleFans(int toggle) {
  digitalWrite(FAN_PIN1, toggle);
  digitalWrite(FAN_PIN2, toggle);
}

// Initialize the class 'MasterControl'
MasterControl* master_control = new MasterControl(radio, sensors); 

// Start (Setup)
void setup() {
  master_control->InitialSetup();
}

// Main Loop
void loop() {
  master_control->RecieveMessage(); 
}