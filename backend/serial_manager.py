import serial
import time
import os
import threading
from dotenv import load_dotenv

load_dotenv()

class SerialManager:
    """Manages the serial connection to the ESP32."""
    def __init__(self):
        self.port = os.getenv("ESP32_PORT", "COM7")
        self.baudrate = 115200
        self.serial_conn = None
        self.is_connected = False
        self.read_thread = None
        self.running = False

    def connect(self):
        """Establish serial connection."""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            self.is_connected = True
            self.running = True
            print(f"Connected to ESP32 on {self.port}")
            
            # Start background thread for reading responses (if needed later)
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
        except serial.SerialException as e:
            print(f"Warning: Could not connect to ESP32 on {self.port}. Error: {e}")
            self.is_connected = False

    def disconnect(self):
        """Close serial connection."""
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.is_connected = False
            print("Disconnected from ESP32")

    def send_command(self, command: str) -> bool:
        """Send a string command to the ESP32."""
        if not self.is_connected or not self.serial_conn:
            print(f"Mock send command '{command}' (Serial not connected)")
            return True # Return true even if mocked for UI testing

        try:
            # Send command with newline character which Micropython print/sys.stdin reads
            formatted_cmd = f"{command}\n".encode('utf-8')
            self.serial_conn.write(formatted_cmd)
            self.serial_conn.flush()
            print(f"Sent: {command}")
            return True
        except Exception as e:
            print(f"Failed to send command: {e}")
            self.is_connected = False
            return False

    def _read_loop(self):
        """Background loop to read responses from ESP32."""
        while self.running and self.serial_conn and self.serial_conn.is_open:
            try:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    if line:
                        print(f"ESP32: {line}")
            except Exception as e:
                print(f"Error reading from serial: {e}")
                self.is_connected = False
                break
            time.sleep(0.01)
