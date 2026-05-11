import sys
from machine import Pin
import time

# Configure GPIO 14 as output
# This will be used to demonstrate hardware control from the frontend
led_pin = Pin(14, Pin.OUT)

print("Microvibration System - ESP32 Firmware Started")
print("Ready to receive commands...")

# The backend will send strings terminated by a newline.
# We use sys.stdin.readline() to read these commands.

while True:
    try:
        # Read a line from standard input (serial connection via USB)
        line = sys.stdin.readline().strip()
        
        if line:
            if line == "ON":
                led_pin.value(1)
                print("GPIO14 is now HIGH")
            elif line == "OFF":
                led_pin.value(0)
                print("GPIO14 is now LOW")
            else:
                print("Unknown command:", line)
                
    except Exception as e:
        print("Error reading serial:", e)
        
    time.sleep(0.01)
