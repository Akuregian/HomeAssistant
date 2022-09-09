# Class to interface with MAX7219 4x4 Dot Matrix
# Used in API __init__.py file
import random
import time
import RPi.GPIO as GPIO
from datetime import datetime
import pytz
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# MAX7219 Interface Class
class Matrix:
    # Initialize the Device
    def __init__(self, _port, _device):
        self._serial = spi(port=_port, device=_device, gpio=noop())
        self._device = max7219(self._serial, width=32, height=8, block_orientation=-90)
        self._device.contrast(1)
        self._virtual = viewport(self._device, width=32, height=16)
        self.start_time = -1
        self.message_dict = {
            "Activating " : "Deactivating ", "Turning On " : "Turning Off ", "Powering up " : "Powering down ",
            "Starting " : "Killing ", "Plugging in " : "Unplugging ", "Switching on " : "Switching off ",
            "Reviving " : "Slaughtering ", "Building " : "Destroying ", "Compiling " : "Decompiling"
            }

    # Displays a Message when a device is turned on/off
    def display_message(self, device_name, status):
        on_message, off_message = random.choice(list(self.message_dict.items()))
        if status == 0:
            message = off_message + " " + device_name
        else:
            message = on_message + " " + device_name

        show_message(self._device, message, fill="white", font=proportional(LCD_FONT))
        self.display_current_time(True)

    # Displays the current time
    def display_current_time(self, force):
        # Grab current timezone
        now = datetime.now(pytz.timezone('US/Pacific'))
        # Split into Hours:Minutes
        current_time = now.strftime("%H:%M")
        # Grab minutes to check against start minutes
        minutes = now.strftime("%M")

        # Update only when the minute has changed
        if(self.start_time != minutes or force):
            with canvas(self._virtual) as draw:
                text(draw, (0, 1), current_time, fill="white", font=proportional(CP437_FONT))
            self.start_time = minutes

    # @@ Make this loop until error is cleared...
    def display_error(self):
        show_message(self._device, "Error Connecting to Server", fill="white", font=proportional(LCD_FONT))
