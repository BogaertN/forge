import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from core_breather.core_breather import CoreBreather
from recursive_field_breather.field_breather import FieldBreather
import time
import json

_field_breather_instance = FieldBreather()
def field_breathe(phase=None):
    return _field_breather_instance.breathe()


_core_breather_instance = CoreBreather()
def core_breathe(phase=None):
    return _core_breather_instance.breathe()

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
        }
