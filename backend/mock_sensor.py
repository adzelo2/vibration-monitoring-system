import time
import json
import random
import math

class MockSensorStream:
    """
    Generates mock microvibration data to simulate a live ADC stream.
    Used for frontend UI development until the ADS1256 is integrated.
    """
    def __init__(self):
        self.start_time = time.time()
        
    def get_next_reading(self) -> str:
        """Returns a JSON string of the next mock data point."""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Simulate a primary vibration frequency (e.g., 5Hz motor)
        primary_freq = math.sin(2 * math.pi * 5 * elapsed)
        
        # Add some high-frequency noise
        noise = random.uniform(-0.2, 0.2)
        
        # Calculate final mock value
        value = primary_freq + noise
        
        data = {
            "timestamp": current_time,
            "value": value
        }
        return json.dumps(data)
