# __init__.py
# This file is used to send GPIO commands to Raspberry Pi

# Raspberry Pi GPIO framework
import RPi.GPIO as GPIO
import time
import spidev
from lib_nrf24 import NRF24


class GPIO_Commands:
    # Initialize Pins as outputs
    def __init__(self):
        GPIO.setwarnings(False)

        # Set GPIO Mode
        GPIO.setmode(GPIO.BCM)
        
        # !! Change this to reflect the API's GPIO pins
        GPIO.setup(17, GPIO.OUT)
        GPIO.setup(27, GPIO.OUT)
        GPIO.setup(22, GPIO.OUT)
        GPIO.setup(23, GPIO.OUT)

        # Initialize pipes to communicate with Arduino's
        self.pipes = [[0xE0, 0xE0, 0xF1, 0xF1, 0xE0], [0xF1, 0xF1, 0xF0, 0xF0, 0xE0]] # Main Arduino

        self.radio = NRF24(GPIO, spidev.SpiDev())
        self.radio.begin(0, 25) # Begin the Radio
        self.radio.setPayloadSize(32)
        self.radio.setChannel(0x76)
        self.radio.setDataRate(NRF24.BR_1MBPS)
        self.radio.setPALevel(NRF24.PA_MIN)
        self.radio.setAutoAck(True)       # set acknowledgement as true 
        self.radio.enableDynamicPayloads()
        self.radio.enableAckPayload()

    # Toggle a Pin HIGH or LOW
    def TogglePin(self, pin, status):
        if status == 0:
            GPIO.output(pin, GPIO.LOW)
        else:
            GPIO.output(pin, GPIO.HIGH)

    def CommunicateWithArduino(self):
        print("Communcating with arduino")
        # Open Writing Pipe
        self.radio.openWritingPipe(self.pipes[0])
        # prevent a message being sent larger than 32 bits by making it a list
        sendMessage = list("Hello World")
        # Prepare the Message in string form with only the first 32 letters
        while(len(sendMessage) < 32):
            sendMessage.append(0)

        step = 0    

        while True:
            print("Trying to Send Message to Arduino")
            if(step > 50):
                break
            step = step + 1

            start = time.time()
            self.radio.write(sendMessage)
            self.radio.startListening()

            while not self.radio.available(0):
                time.sleep(1/100)
                if(time.time() - start > 2):
                    print("Timed Out")
                    break
           # what = self.radio.whatHappened()
           # print(what)

        self.radio.stopListening()




