"""Compatibility wrapper for logical module name drift_arbitrator."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

_impl_path = Path(__file__).resolve().parents[1] / "drift_detection" / "drift_detector.py"
_spec = spec_from_file_location("_rmc_drift_detector_impl", _impl_path)
_mod = module_from_spec(_spec)
assert _spec and _spec.loader
sys.modules["_rmc_drift_detector_impl"] = _mod
_spec.loader.exec_module(_mod)

DriftEvent = _mod.DriftEvent
DriftArbitrator = _mod.DriftArbitrator
