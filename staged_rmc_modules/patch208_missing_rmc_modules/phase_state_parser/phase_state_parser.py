"""Compatibility wrapper for logical module name phase_state_parser."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

_impl_path = Path(__file__).resolve().parents[1] / "phase_parser" / "phase_state_parser.py"
_spec = spec_from_file_location("_rmc_phase_parser_impl", _impl_path)
_mod = module_from_spec(_spec)
assert _spec and _spec.loader
sys.modules["_rmc_phase_parser_impl"] = _mod
_spec.loader.exec_module(_mod)

PHASES = _mod.PHASES
TOKEN_TO_PHASE = _mod.TOKEN_TO_PHASE
PhaseCue = _mod.PhaseCue
PhaseState = _mod.PhaseState
PhaseStateParser = _mod.PhaseStateParser
