# __init__.py
# This file is used to send GPIO commands to Raspberry Pi
# which in turn, communicates with the Arduino Mega

# Raspberry Pi GPIO framework
import RPi.GPIO as GPIO
import time
import spidev
from lib_nrf24 import NRF24
import time
import pytz
from datetime import datetime

class GPIO_Commands:
    # Initialize Pins as outputs
    def __init__(self):
        GPIO.setwarnings(False)

        # Set GPIO Mode
        GPIO.setmode(GPIO.BCM)

        self.pipes = [ [0xE8, 0xE8, 0xF0, 0xF0, 0xE1] ]
        self.radio = NRF24(GPIO, spidev.SpiDev())
        self.radio.begin(0, 25, 4000000) # SPI-0: ce-0, csn 
        self.radio.setPayloadSize(32)
        self.radio.setChannel(0x76)
        self.radio.setDataRate(NRF24.BR_1MBPS)
        self.radio.setPALevel(NRF24.PA_MAX)
        self.radio.setAutoAck(True)
        self.radio.enableDynamicPayloads()
        self.radio.openWritingPipe(self.pipes[0])
        self.radio.printDetails()

    def CommunicateWithArduino(self, device_identifier, device_name, pipe_address, status):
        # Open Writing Pipe
        #self.radio.openWritingPipe(pipe_address)

        # prevent a message being sent larger than 32 bits by making it a list
        sendMessage = list(device_identifier + " " + str(status) + " " + device_name)

        # Prepare the Message in string form with only the first 32 letters
        while(len(sendMessage) < 32):
            sendMessage.append(0)

        # Send the Message
        self.radio.write(sendMessage)

    def SendCurrentTime(self):
        now = datetime.now(pytz.timezone('US/Pacific'))
        current_time = now.strftime("%H:%M")
        time_msg = list('Time: ' + current_time)
        while(len(time_msg) < 32):
            time_msg.append(0)
        self.radio.write(time_msg)
