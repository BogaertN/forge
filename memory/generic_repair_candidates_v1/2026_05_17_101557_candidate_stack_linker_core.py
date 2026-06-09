import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from core_breather.core_breather import breathe_phase as core_breathe
from recursive_field_breather.field_breather import breathe_phase as field_breathe
import time
import json

def unified_breathe_cycle():
    # simple combined breathing cycle
    for phase in range(1, 10):  # Full 1-9 breathing
        core_breathe(phase)
        field_breathe(phase)
        event = {
            "timestamp": time.time(),
            "phase": phase,
            "stack": "core_and_field",
            "status": "",
