"""Compatibility wrapper for logical module name echo_gate."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

_impl_path = Path(__file__).resolve().parents[1] / "echo_validator" / "echo_validator.py"
_spec = spec_from_file_location("_rmc_echo_validator_impl", _impl_path)
_mod = module_from_spec(_spec)
assert _spec and _spec.loader
sys.modules["_rmc_echo_validator_impl"] = _mod
_spec.loader.exec_module(_mod)

EchoCheck = _mod.EchoCheck
EchoReport = _mod.EchoReport
EchoGate = _mod.EchoGate
