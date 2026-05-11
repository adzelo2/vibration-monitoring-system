import os
import time
import json
import csv
from datetime import datetime

class SessionManager:
    """Manages recording sessions, saving raw data and metadata."""
    def __init__(self):
        # Base path relative to this script's directory
        self.base_recordings_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "recordings"))
        self.active_session_id = None
        self.session_dir = None
        self.csv_file_path = None
        
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
            "status": "recording"
        }
        with open(os.path.join(self.session_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=4)
            
        # Create and initialize raw_data.csv
        self.csv_file_path = os.path.join(self.session_dir, "raw_data.csv")
        with open(self.csv_file_path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "value"]) # Header
            
        print(f"Started session: {self.active_session_id}")
        return self.active_session_id

    def stop_session(self) -> str:
        """Stop the active session and update metadata."""
        if self.active_session_id is None:
            return None
        
        # Update metadata
        metadata_path = os.path.join(self.session_dir, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                
            metadata["end_time"] = datetime.now().isoformat()
            metadata["status"] = "completed"
            
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=4)
                
        stopped_session_id = self.active_session_id
        
        print(f"Stopped session: {self.active_session_id}")
        self.active_session_id = None
        self.session_dir = None
        self.csv_file_path = None
        
        return stopped_session_id

    def append_data(self, timestamp: float, value: float):
        """Append a single data point to the active session CSV."""
        if self.active_session_id and self.csv_file_path:
            with open(self.csv_file_path, "a", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, value])

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
