# __init__.py
# This file is used to send GPIO commands to Raspberry Pi

# Raspberry Pi GPIO framework
import RPi.GPIO as GPIO

class GPIO_Commands:
    # Initialize Pins as outputs
    def __init__(self):
        # Set GPIO Mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)
        GPIO.setup(27, GPIO.OUT)
        GPIO.setup(22, GPIO.OUT)
        GPIO.setup(23, GPIO.OUT)

    # Toggle a Pin HIGH or LOW
    def TogglePin(self, pin, status):
        if status == 0:
            GPIO.output(pin, GPIO.LOW)
        else:
            GPIO.output(pin, GPIO.HIGH)

