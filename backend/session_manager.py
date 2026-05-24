import os
import time
import json
import csv
import io
from datetime import datetime

SAMPLE_RATE = 15000
FLUSH_INTERVAL = 1.0  # Flush CSV buffer every 1 second


class SessionManager:
    """Manages recording sessions, saving raw data and metadata."""
    def __init__(self):
        # Base path relative to this script's directory
        self.base_recordings_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "recordings"))
        self.active_session_id = None
        self.session_dir = None
        self.csv_file_path = None
        self._csv_file = None
        self._csv_writer = None
        self._last_flush = 0
        self._sample_count = 0

        # Ensure recordings dir exists
        if not os.path.exists(self.base_recordings_dir):
            os.makedirs(self.base_recordings_dir)

    def start_session(self) -> str:
        """Start a new session and create necessary files."""
        if self.active_session_id is not None:
            return None # Already active

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.active_session_id = f"session_{timestamp_str}"
        self.session_dir = os.path.join(self.base_recordings_dir, self.active_session_id)

        os.makedirs(self.session_dir)

        # Create metadata.json
        metadata = {
            "session_id": self.active_session_id,
            "start_time": datetime.now().isoformat(),
            "sample_rate": SAMPLE_RATE,
            "status": "recording"
        }
        with open(os.path.join(self.session_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=4)

        # Open CSV file with buffered writer (keep open for session duration)
        self.csv_file_path = os.path.join(self.session_dir, "raw_data.csv")
        self._csv_file = open(self.csv_file_path, "w", newline='', buffering=65536)
        self._csv_writer = csv.writer(self._csv_file)
        self._csv_writer.writerow(["timestamp", "value"])  # Header
        self._last_flush = time.time()
        self._sample_count = 0

        print(f"Started session: {self.active_session_id}")
        return self.active_session_id

    def stop_session(self) -> str:
        """Stop the active session and update metadata."""
        if self.active_session_id is None:
            return None

        # Close CSV file
        if self._csv_file:
            self._csv_file.flush()
            self._csv_file.close()
            self._csv_file = None
            self._csv_writer = None

        # Update metadata
        metadata_path = os.path.join(self.session_dir, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            metadata["end_time"] = datetime.now().isoformat()
            metadata["status"] = "completed"
            metadata["total_samples"] = self._sample_count

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=4)

        stopped_session_id = self.active_session_id

        print(f"Stopped session: {self.active_session_id} ({self._sample_count} samples)")
        self.active_session_id = None
        self.session_dir = None
        self.csv_file_path = None
        self._sample_count = 0

        return stopped_session_id

    def append_data(self, timestamp: float, value: float):
        """Append a single data point to the active session CSV."""
        if self._csv_writer:
            self._csv_writer.writerow([timestamp, value])
            self._sample_count += 1
            self._maybe_flush()

    def append_batch(self, base_timestamp: float, values: list):
        """Append a batch of samples to the active session CSV.
        
        Args:
            base_timestamp: Timestamp of the first sample in the batch.
            values: List of integer ADC values.
        """
        if not self._csv_writer:
            return

        dt = 1.0 / SAMPLE_RATE
        for i, val in enumerate(values):
            t = base_timestamp + i * dt
            self._csv_writer.writerow([t, val])

        self._sample_count += len(values)
        self._maybe_flush()

    def _maybe_flush(self):
        """Flush CSV buffer periodically."""
        now = time.time()
        if now - self._last_flush >= FLUSH_INTERVAL:
            if self._csv_file:
                self._csv_file.flush()
            self._last_flush = now

    def list_sessions(self) -> list:
        """Return a list of all recorded sessions."""
        sessions = []
        if not os.path.exists(self.base_recordings_dir):
            return sessions

        for item in os.listdir(self.base_recordings_dir):
            item_path = os.path.join(self.base_recordings_dir, item)
            if os.path.isdir(item_path):
                metadata_path = os.path.join(item_path, "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as f:
                        try:
                            metadata = json.load(f)
                            sessions.append(metadata)
                        except json.JSONDecodeError:
                            pass

        # Sort by start_time descending
        sessions.sort(key=lambda x: x.get("start_time", ""), reverse=True)
        return sessions
