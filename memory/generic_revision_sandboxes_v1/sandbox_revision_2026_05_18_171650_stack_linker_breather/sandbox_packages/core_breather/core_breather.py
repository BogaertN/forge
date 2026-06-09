# core_breather.py

import json
import time
from datetime import datetime

class CoreBreather:
    def __init__(self):
        self.phase = 1
        self.loop_count = 0
        self.trace_file = "core_trace.jsonl"

    def breathe(self):
        timestamp = datetime.utcnow().isoformat() + "Z"
        trace_entry = {
            "phase": self.phase,
            "timestamp": timestamp,
            "loop": self.loop_count,
            "drift": 0.0
        }

        with open(self.trace_file, "a") as f:
            f.write(json.dumps(trace_entry) + "\n")

        print(f"Breath Phase: {self.phase} | Loop: {self.loop_count} | Time: {timestamp}")

        self.phase += 1
        if self.phase > 9:
            self.phase = 1
            self.loop_count += 1
