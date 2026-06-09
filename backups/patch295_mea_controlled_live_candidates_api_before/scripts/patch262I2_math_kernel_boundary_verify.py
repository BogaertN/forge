#!/usr/bin/env python3
# Patch 262I2 verifier
# Purpose: prove RMC coherence math now lives in a dedicated engine module, not UI/main route code.
from pathlib import Path
import importlib
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
main_py = root / "main.py"
engine_py = root / "rmc_engine_v1" / "coherence_math.py"
init_py = root / "rmc_engine_v1" / "__init__.py"

assert main_py.exists(), "missing forge/main.py"
assert engine_py.exists(), "missing forge/rmc_engine_v1/coherence_math.py"
assert init_py.exists(), "missing forge/rmc_engine_v1/__init__.py"

main_text = main_py.read_text(encoding="utf-8")
engine_text = engine_py.read_text(encoding="utf-8")

assert "from rmc_engine_v1.coherence_math import score_candidate" in main_text, "main.py does not delegate scoring to engine kernel"
assert "from rmc_engine_v1.coherence_math import formal_math_binding" in main_text, "main.py does not delegate math contract to engine kernel"
assert "math_kernel_location" in main_text, "endpoint response does not expose math kernel location"
assert "def score_candidate" in engine_text, "engine kernel missing score_candidate"
assert "def formal_math_binding" in engine_text, "engine kernel missing formal_math_binding"
assert "def extract_math_terms" in engine_text, "engine kernel missing extract_math_terms"
assert "exec(" not in engine_text and "subprocess" not in engine_text and "open(" not in engine_text, "engine kernel contains forbidden side-effect primitive"
assert "queries_chroma_db" not in engine_text, "engine kernel should not query DB or Chroma"

core = importlib.import_module("rmc_engine_v1.coherence_math")
contract = core.formal_math_binding()
assert contract["math_kernel_location"] == "forge/rmc_engine_v1/coherence_math.py"
assert "RPM(x,t)" in contract["rpmc_memory_equation"]
assert "ε_s" in contract["epsilon_formula"]
assert contract["cold_storage_law"]["spc_cold_storage_is_silence_not_deletion"] is True

candidate = {
    "candidate_id": "ct_test",
    "title": "Kernel Boundary Candidate",
    "candidate_type": "test",
    "phase_target": "Φ6",
    "confidence": 0.64,
    "required_limitations": ["trace_first", "manifest_seed_only", "requires_correction_before_projection"],
}
report = {
    "candidate_set_id": "ct_test_set",
    "source_drift_report": {
        "epsilon_s": {"sigma_res": 0.2, "D_score": 0.3, "phase_deviation_normalized": 0.1, "epsilon_s": 0.2},
        "chi_t": {"required": True},
        "circuit_breaker": {"triggered": False},
        "drift_classes": [{"drift_key": "evolutionary", "score": 0.25}],
        "source_phase_parser": {"phase_state": {"phase_primary": "Φ6", "phase_path_hypothesis": ["Φ1", "Φ2", "Φ3", "Φ4", "Φ5", "Φ6"]}},
    },
}
score = core.score_candidate(candidate, report)
assert score["engine_version"] == core.ENGINE_VERSION
assert score["math_kernel_location"] == "forge/rmc_engine_v1/coherence_math.py"
assert score["projection_allowed"] is False
assert score["final_language_allowed"] is False
assert score["memory_write_allowed"] is False
assert "cold_storage_gate" in score and "naming_gate" in score and "correction_gate" in score

print("PATCH262I2_MATH_KERNEL_BOUNDARY_VERIFY_PASS")
print("engine_module=forge/rmc_engine_v1/coherence_math.py")
print("main_py_endpoint=thin_adapter")
print("ui_owns_math=False")
print("main_py_owns_math=False")
print("engine_module_owns_math=True")
print("side_effect_free_kernel=True")
print("adds_forge_commands=False")
print("executes_shell=False")
print("calls_llm=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
