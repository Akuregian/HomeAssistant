#include <Adafruit_NeoPixel.h>
#include <MD_Parola.h>
#include <MD_MAX72xx.h>
#include <SPI.h>
#include <RF24.h>
#include <RF24_config.h>
#include <nRF24L01.h>
#include <printf.h>

// NEO Pixel Ring
#define NEO_PIN 2
#define NUMPIXELS 12

// Relay Board
#define LED_PIN1 36
#define LED_PIN2 37
#define LED_PIN3 38
#define LED_PIN4 39
#define LED_PIN5 40
#define LED_PIN6 41

// Setup for LED Matrix Display
#define HARDWARE_TYPE MD_MAX72XX::FC16_HW
#define MAX_DEVICES 4
#define CS_PIN 10
#define MOSI 11
#define SCLK 13
#define BUF_SIZE 75
#define SCROLL_SPEED 30

// Master Control class to handle all the logic for the arduino
class MasterControl {
  public: 
    MasterControl();
    void InitialSetup(); 
    String GenerateRandomMessage(int toggle);
    void ParseMessage();
    void DisplayMessage(String device_name, int toggle);
    void RecieveMessage();
    void DisplayLEDS();
    void StrobeLEDS();

  private:
    RF24* _radio;
    MD_Parola* _myDisplay;
    Adafruit_NeoPixel* _NeoPixel;
    String _currTime;
    String _onMessages[9] = {  "Activating ",  "Turning On ",  "Powering up ", "Starting ",  "Plugging in ",  "Switching on ", "Reviving ",  "Building ", "Compiling "  };
    String _offMessages[9] = { "Deactivating ",  "Turning Off ", "Powering down ", "Killing ", "Unplugging ", "Switching off ", "Slaughtering ", "Destroying ", "Decompiling " };
    enum Devices { DEVICE1, DEIVCE2, DEIVCE3, DEIVCE4, DEIVCE5, DEIVCE6 };
    enum Status { ON, OFF };
    int _index = 0;
    unsigned long PreviousMillis = 0;
    unsigned long Interval = 40; // milliseconds
};

MasterControl::MasterControl() :  _radio(new RF24(7, 8)), 
                                  _myDisplay(new MD_Parola(HARDWARE_TYPE, MOSI, SCLK, CS_PIN, MAX_DEVICES)), 
                                  _NeoPixel(new Adafruit_NeoPixel(NUMPIXELS, NEO_PIN, NEO_GRB + NEO_KHZ800))  {};

// Setup all the required states
void MasterControl::InitialSetup() {
  Serial.begin(9600);
  pinMode(LED_PIN1, OUTPUT);
  pinMode(LED_PIN2, OUTPUT);
  pinMode(LED_PIN3, OUTPUT);
  pinMode(LED_PIN4, OUTPUT);
  pinMode(LED_PIN5, OUTPUT);
  pinMode(LED_PIN6, OUTPUT);
  _radio->begin();
  _radio->setPALevel(RF24_PA_MAX);
  _radio->setChannel(0x76);
  const uint64_t pipe = (0xE8E8F0F0E1LL);
  _radio->openReadingPipe(1, pipe);
  _radio->enableDynamicPayloads();
  _radio->enableAckPayload();
  _radio->startListening();
  _radio->powerUp();

  _myDisplay->begin(); // Intialize the object
	_myDisplay->setIntensity(5); // Set the intensity (brightness) of the display (0-15)
	_myDisplay->displayClear(); // Clear the display
  _NeoPixel->begin();
}

// Messaged Recieved, Turn on Relay
void MasterControl::ParseMessage() {
    char recieved_message[32] = { 0 };
    _radio->read(recieved_message, sizeof(recieved_message));
    // recieve message
    String response_string = String(recieved_message);

    // Time update request sent from server
    if(response_string.substring(0, 4) == "Time") {
      String time_string = response_string.substring(6, 11);
      _currTime = time_string;
      return;
    }

    // Message to change color of LED ring from user
    if(response_string.substring(0, 3) == "LED") {
      // Change color of LED ring
      //_NeoPixel
      return;
    }

    // parse out the device_name
    String device_name = response_string.substring(4);
    // remove the device_name from response_string
    response_string.remove(3, device_name.length() + 1);

    int device = response_string[0] - '0';
    int status = response_string[2] - '0';

    switch(device) {
      case 1: { digitalWrite(LED_PIN1, status); break; }
      case 2: { digitalWrite(LED_PIN2, status); break; }    
      case 3: { digitalWrite(LED_PIN3, status); break; }      
      case 4: { digitalWrite(LED_PIN4, status); break; }      
      case 5: { digitalWrite(LED_PIN5, status); break; }      
      case 6: { digitalWrite(LED_PIN6, status); break; }
      default: { Serial.println("Not Found"); } 
    }

    // DisplayMessage(String device_name, int toggle)
    DisplayMessage(device_name, (response_string[2] - '0'));
    //DisplayLEDS();
}

// returns either an off or on message
String MasterControl::GenerateRandomMessage(int toggle) {
  if(toggle) {
    int r_on = random(0, 9);
    return _onMessages[r_on];

  }else if(!toggle) {
    int r_off = random(0, 9);
    return _offMessages[r_off];
  }
}

// Displays a message to the MAX7219
void MasterControl::DisplayMessage(String device_name, int toggle) {
  // Create a buffer to convert str to char array
  char Buf[BUF_SIZE];
  // Generate random message from array
  String r_msg = GenerateRandomMessage(toggle);
  // concat
  String to_buffer = r_msg + " " + device_name;
  // convert to charArray
  to_buffer.toCharArray(Buf, BUF_SIZE); 
  // display to MAX7219
  _myDisplay->displayText(Buf, PA_CENTER, SCROLL_SPEED, 0, PA_SCROLL_LEFT, PA_SCROLL_LEFT);
  _myDisplay->displayClear();
  // animate.. @Todo: This needs to be threaded somehow
  while(!_myDisplay->displayAnimate()) {
    StrobeLEDS();
  }
  _NeoPixel->clear();
  _NeoPixel->show();
}

// Recieve the Message from the RaspberryPi
void MasterControl::RecieveMessage() {
  while (!_radio->available()) {
    _myDisplay->setTextAlignment(PA_CENTER);
    _myDisplay->print(_currTime);
    delay(25/100);
  }

  if (_radio->available()) {
    ParseMessage();
    delay(25);
  }
}

void MasterControl::DisplayLEDS() {
  _NeoPixel->fill(_NeoPixel->Color(255, 255, 0));
  _NeoPixel->show();
}

void MasterControl::StrobeLEDS() {
  unsigned long currentMillis = millis();
  if(_index > NUMPIXELS) { _index = 0; _NeoPixel->clear(); _NeoPixel->show(); }
  if(currentMillis - PreviousMillis > Interval) {
    PreviousMillis = currentMillis;
    _NeoPixel->setPixelColor(_index++, _NeoPixel->Color(0, 255, 255));
  //delay(20); // !!!...THIS DELAY CAUSES THE DISPLAY LED TO LAG SLIGHTLY...!!!!
    _NeoPixel->show();
  }
}

// Initialize the class 'MasterControl'
MasterControl* master_control = new MasterControl(); 

// Start (Setup)
void setup() {
  master_control->InitialSetup();
}

// Main Loop
void loop() {
  master_control->RecieveMessage(); 
}