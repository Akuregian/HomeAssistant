# Class to interface with MAX7219 4x4 Dot Matrix
# Used in API __init__.py file

import time
import RPi.GPIO as GPIO
from datetime import datetime
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
        self._device.contrast(5)
        self._virtual = viewport(self._device, width=32, height=16)

    # Displays a Message when a device is turned on/off
    def display_message(self, device_name, status):
        if status == 0:
            message = "Turning off {}".format(device_name)
        else:
            message = "Turning on {}".format(device_name)

        show_message(self._device, message, fill="white", font=proportional(LCD_FONT))


    # Displays the current time
    def display_current_time(self, time_display):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        timeout = time_display
        start = time.time()
        try:
            while (time.time() < start + timeout):
                with canvas(self._virtual) as draw:
                    text(draw, (0, 1), current_time, fill="white", font=proportional(CP437_FONT))

        except KeyboardInterrupt:
            GPIO.cleanup()

    # @@ Make this loop until error is cleared...
    def display_error(self):
        show_message(self._device, "Error Connecting to Server", fill="white", font=proportional(LCD_FONT))

mat = Matrix(0, 1)
if __name__ == "__main__":
    print("Displaying Message")
    mat.display_message("Device", 0)
    print("End of Message")
