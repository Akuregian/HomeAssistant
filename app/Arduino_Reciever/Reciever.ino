#include <MD_Parola.h>
#include <MD_MAX72xx.h>
#include <SPI.h>
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

// Setup for LED Matrix Display
#define HARDWARE_TYPE MD_MAX72XX::FC16_HW
#define MAX_DEVICES 4
#define CS_PIN 10
#define MOSI 11
#define SCLK 13
#define BUF_SIZE 75
#define SCROLL_SPEED 30


// NRF24L01: CE, CSN
RF24 radio(7, 8);

// MAX7219 Display
MD_Parola myDisplay = MD_Parola(HARDWARE_TYPE, MOSI, SCLK, CS_PIN, MAX_DEVICES);

// Master Control class to handle all the logic for the arduino
class MasterControl {
  public: 
    MasterControl(RF24 radio_instance) : _radio(&radio_instance)  {};
    void InitialSetup(); 
    String GenerateRandomMessage(int toggle);
    void DisplayMessage(String device_name, int toggle);
    void RecieveMessage();

  private:
    RF24* _radio;
    unsigned long _prevMillis = 0;
    unsigned long _interval = ONE_MIN;
    String _currTime;

    String _onMessages[9] = {  "Activating ",  "Turning On ",  "Powering up ", "Starting ",  "Plugging in ",  "Switching on ", "Reviving ",  "Building ", "Compiling "  };
    String _offMessages[9] = { "Deactivating ",  "Turning Off ", "Powering down ", "Killing ", "Unplugging ", "Switching off ", "Slaughtering ", "Destroying ", "Decompiling " };    
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
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(0x76);
  const uint64_t pipe = (0xE8E8F0F0E1LL);
  radio.openReadingPipe(1, pipe);
  radio.enableDynamicPayloads();
  radio.enableAckPayload();
  radio.startListening();
  radio.powerUp();

  myDisplay.begin(); // Intialize the object
	myDisplay.setIntensity(5); // Set the intensity (brightness) of the display (0-15)
	myDisplay.displayClear(); // Clear the display
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
  myDisplay.displayText(Buf, PA_CENTER, SCROLL_SPEED, 0, PA_SCROLL_LEFT, PA_SCROLL_LEFT);
}

// Recieve the Message from the RaspberryPi
void MasterControl::RecieveMessage() {
  while (!radio.available()) {
    myDisplay.print(_currTime);
    delay(25/100);
  }

  if (radio.available()) {
    char recieved_message[32] = { 0 };
    radio.read(recieved_message, sizeof(recieved_message));
    // recieve message
    String response_string = String(recieved_message);

    if(response_string.substring(0, 4) == "Time") {
      String time_string = response_string.substring(6, 11);
      _currTime = time_string;
      return;
    }
 
    // parse out the device_name
    String device_name = response_string.substring(4);
    // remove the device_name from response_string
    response_string.remove(3, device_name.length() + 1);
    if (response_string == "1 0") {
      digitalWrite(LED_PIN1, LOW);
    } else if (response_string == "1 1") {
      digitalWrite(LED_PIN1, HIGH);
    } else if (response_string == "2 0") {
      digitalWrite(LED_PIN2, LOW);
    } else if (response_string == "2 1") {
      digitalWrite(LED_PIN2, HIGH);
    } else if (response_string == "3 0") {
      digitalWrite(LED_PIN3, LOW);
    } else if (response_string == "3 1") {
      digitalWrite(LED_PIN3, HIGH);
    } else if (response_string == "4 1") {
      digitalWrite(LED_PIN4, HIGH);
    } else if (response_string == "4 0") {
      digitalWrite(LED_PIN4, LOW);
    } else if (response_string == "5 1") {
      digitalWrite(LED_PIN5, HIGH);
    } else if (response_string == "5 0") {
      digitalWrite(LED_PIN5, LOW);
    } else if (response_string == "6 1") {
      digitalWrite(LED_PIN6, HIGH);
    } else if (response_string == "6 0") {       
      digitalWrite(LED_PIN6, LOW);
    } else {
      Serial.println("Error, Recieved a different Message...");
      return;
    }
        // DisplayMessage(String device_name, int toggle)
    DisplayMessage(device_name, (response_string[2] - '0'));
    myDisplay.displayClear();
    while(!myDisplay.displayAnimate()) {

    }
    delay(25);
  }
}

// Initialize the class 'MasterControl'
MasterControl* master_control = new MasterControl(radio); 

// Start (Setup)
void setup() {
  master_control->InitialSetup();
}

// Main Loop
void loop() {
  master_control->RecieveMessage(); 
}