// !!Upload this code to the arduino using ArduinoIDE!!

#include <RF24.h>
#include <RF24_config.h>
#include <nRF24L01.h>
#include <printf.h>

RF24 radio(9, 10);

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(0x76);
  radio.openWritingPipe(0xF0F0F0F0E1LL);
  const uint64_t pipe = (0xE8E8F0F0E1LL);
  radio.openReadingPipe(1, pipe);
  radio.enableDynamicPayloads();
  radio.startListening();
  radio.powerUp();
}

void loop() {

  while(!radio.available()) {
    delay(1/100);
  }

  char recieved_message[32] = {0};
  radio.read(recieved_message, sizeof(recieved_message));
  Serial.println(recieved_message);
  delay(1000);
}
