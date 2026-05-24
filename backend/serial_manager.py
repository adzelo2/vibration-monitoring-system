import serial
import time
import os
import threading
import queue
from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE = 500
BATCH_TIMEOUT = 0.033


class SerialManager:
    """Manages the serial connection to the ESP32 with ASCII line parsing at 921600."""
    def __init__(self):
        self.port = os.getenv("ESP32_PORT", "COM7")
        self.baudrate = 115200
        self.serial_conn = None
        self.is_connected = False
        self.read_thread = None
        self.running = False
        self.data_queue = queue.Queue()
        self._samples_received = 0

    def connect(self):
        """Establish serial connection WITHOUT resetting the ESP32."""
        try:
            self.serial_conn = serial.Serial()
            self.serial_conn.port = self.port
            self.serial_conn.baudrate = self.baudrate
            self.serial_conn.timeout = 0.1
            self.serial_conn.dtr = False
            self.serial_conn.rts = False
            self.serial_conn.open()

            time.sleep(0.1)
            self.serial_conn.reset_input_buffer()

            self.is_connected = True
            self.running = True
            print(f"Connected to ESP32 on {self.port} @ {self.baudrate} baud (DTR/RTS disabled)")

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
            print(f"Disconnected from ESP32 ({self._samples_received} samples total)")

    async def send_command_async(self, command: str) -> bool:
        """Send a text command to the ESP32."""
        if not self.is_connected or not self.serial_conn:
            print(f"Mock send command '{command}' (Serial not connected)")
            return True

        try:
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
        """Background loop: read ASCII lines from ESP32, batch and enqueue."""
        batch_values = []
        batch_start_time = time.time()
        last_stats_time = time.time()

        while self.running and self.serial_conn and self.serial_conn.is_open:
            try:
                # Print stats every 5 seconds
                now = time.time()
                if now - last_stats_time >= 5.0:
                    print(f"[Serial] Samples received: {self._samples_received}, Queue size: {self.data_queue.qsize()}")
                    last_stats_time = now

                # Flush partial batch on timeout
                if batch_values and (now - batch_start_time) >= BATCH_TIMEOUT:
                    self.data_queue.put({
                        "timestamp": batch_start_time,
                        "values": batch_values
                    })
                    batch_values = []
                    batch_start_time = time.time()

                # Read lines (readline is efficient for ASCII protocol)
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        try:
                            value = int(line)
                            self._samples_received += 1
                            batch_values.append(value)

                            if len(batch_values) >= BATCH_SIZE:
                                self.data_queue.put({
                                    "timestamp": batch_start_time,
                                    "values": batch_values
                                })
                                batch_values = []
                                batch_start_time = time.time()
                        except ValueError:
                            # Non-numeric line (debug message from ESP32)
                            print(f"ESP32: {line}")
                else:
                    time.sleep(0.001)

            except Exception as e:
                print(f"Error reading from serial: {e}")
                self.is_connected = False
                break
