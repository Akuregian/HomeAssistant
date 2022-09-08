#include <RF24.h>
#include <RF24_config.h>
#include <nRF24L01.h>
#include <printf.h>

// TEST
#define LED_PIN1 2
#define LED_PIN2 3
#define LED_PIN3 4
#define LED_PIN4 5
#define LED_PIN5 6
#define LED_PIN6 7

RF24 radio(9, 10);

// Master Control class to handle all the logic for the arduino
class MasterControl {
  public: 
    MasterControl(RF24 radio_instance) : _radio(&radio_instance) {};
    void InitialSetup(); 
    void RecieveMessage();
  private:
    RF24* _radio;
};

// Setup all the required states
void MasterControl::InitialSetup() {
  pinMode(LED_PIN1, OUTPUT);
  pinMode(LED_PIN2, OUTPUT);
  pinMode(LED_PIN3, OUTPUT);
  pinMode(LED_PIN4, OUTPUT);
  pinMode(LED_PIN5, OUTPUT);
  pinMode(LED_PIN6, OUTPUT);
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(0x76);
  const uint64_t pipe = (0xE8E8F0F0E1LL);
  radio.openReadingPipe(1, pipe);
  radio.enableDynamicPayloads();
  radio.enableAckPayload();
  radio.startListening();
  radio.powerUp();
}

// Recieve the Message from the RaspberryPi
void MasterControl::RecieveMessage() {
  while (!radio.available()) {
    delay(25 / 100);
  }
  if (radio.available()) {
    Serial.println("Message Recieved");
    char recieved_message[32] = { 0 };
    radio.read(recieved_message, sizeof(recieved_message));
    String response_string = String(recieved_message);

    if (response_string == "Master-Socket-1 0") {
      Serial.println("Turning off Master-Socket-1");
      digitalWrite(LED_PIN1, LOW);
    } else if (response_string == "Master-Socket-1 1") {
        Serial.println("Turning on Master-Socket-1");
      digitalWrite(LED_PIN1, HIGH);
    } else if (response_string == "Master-Socket-2 0") {
        Serial.println("Turning off Master-Socket-2");
      digitalWrite(LED_PIN2, LOW);
    } else if (response_string == "Master-Socket-2 1") {
        Serial.println("Turning on Master-Socket-2");
      digitalWrite(LED_PIN2, HIGH);
    } else if (response_string == "Master-Socket-3 0") {
        Serial.println("Turning off Master-Socket-3");
      digitalWrite(LED_PIN3, LOW);
    } else if (response_string == "Master-Socket-3 1") {
        Serial.println("Turning on Master-Socket-3"); 
        digitalWrite(LED_PIN3, HIGH);
    } else if (response_string == "Master-Socket-4 1") {
        Serial.println("Turning on Master-Socket-4"); 
        digitalWrite(LED_PIN4, HIGH);
    } else if (response_string == "Master-Socket-4 0") {
        Serial.println("Turning off Master-Socket-4"); 
        digitalWrite(LED_PIN4, LOW);
    } else if (response_string == "Master-Socket-5 1") {
        Serial.println("Turning on Master-Socket-5"); 
        digitalWrite(LED_PIN5, HIGH);
    } else if (response_string == "Master-Socket-5 0") {
        Serial.println("Turning off Master-Socket-5"); 
        digitalWrite(LED_PIN5, LOW);
    } else if (response_string == "Master-Socket-6 1") {
        Serial.println("Turning on Master-Socket-6"); 
        digitalWrite(LED_PIN6, HIGH);
    } else if (response_string == "Master-Socket-6 0") {
        Serial.println("Turning off Master-Socket-6"); 
        digitalWrite(LED_PIN6, LOW);
    } else {
      Serial.println("Error");
    }
    delay(1000);
  }
}

// Initialize the class 'MasterControl'
MasterControl* master_control = new MasterControl(radio); 

void setup() {
  Serial.begin(9600);
  master_control->InitialSetup();
}

void loop() {
  master_control->RecieveMessage();
}