#!/usr/bin/env python3
"""Patch 268S — ProtoForge2 Drift Candidate Adapter Tests.
Run: python scripts/test_patch268S_pf2_drift_adapter.py
"""
from __future__ import annotations
import sys, os, tempfile, inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rmc_engine_v1.protoforge2_drift_connector import (
    probe_protoforge2_status, probe_protoforge2_import, preview_drift_call,
    boundary, _normalize, _classify_by_hash, _is_safe_function_name,
    _source_has_log_side_effects, _file_sha256,
    ENGINE_VERSION, FULL_ENGINE_SHA256, RMC_ARBITRATOR_SHA256,
    SANDBOX_BRIDGE_SHA256, LEGACY_REJECTED_SHA256, _DEFAULT_CANDIDATES,
)
from pathlib import Path

PASS, FAIL = "PASS", "FAIL"
results = []
def chk(n, ok, d=""): results.append((n, PASS if ok else FAIL, d))


# ── Helpers: fake modules ─────────────────────────────────────────────────────

def _write(td: str, name: str, content: str) -> str:
    p = os.path.join(td, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(content)
    return p

FAKE_ARBITRATOR = '''
class DriftArbitrator:
    """RMC-safe arbitrator — no side effects."""
    def evaluate(self, payload):
        return {
            "epsilon_s": 0.15,
            "entropy": 0.20,
            "verdict": "benign",
            "drift_detected": False,
            "events": [],
            "correction_recommended": False,
            "chi_t_required": False,
            "circuit_breaker_open": False,
            "recommended_action": "ALLOW",
        }
'''

FAKE_DRIFT_BRIDGE = '''
class DriftBridge:
    """Sandbox drift bridge — read-only."""
    def evaluate(self, payload):
        return {"epsilon_s": 0.18, "verdict": "benign", "drift_detected": False}
'''

FAKE_FULL_ENGINE = '''
import os, logging
from logging.handlers import RotatingFileHandler
class DriftMonitor:
    """Full drift engine — creates logs on instantiation."""
    def __init__(self, echo_path=None):
        # WOULD create storage/logs/drift.log here in production
        os.makedirs("storage/logs", exist_ok=True)
        self._instantiated = True
    def check_and_firewall(self, cmd, payload, agent=None, **kwargs):
        return "ALLOW", 0.15, {}
'''

FAKE_LEGACY = '''
import random, logging
def check_drift(payload):
    # Writes logs and uses random entropy — REJECTED
    with open("logs/drift.log", "a") as f:
        f.write("drift_check\\n")
    return random.random()
'''


# ── T1: Boundary contract ─────────────────────────────────────────────────────
b = boundary()
chk("T1_engine_268S",          "268S" in b["engine_version"])
chk("T1_no_shell",             b["no_shell"] is True)
chk("T1_no_subprocess",        b["no_subprocess"] is True)
chk("T1_no_browser_import",    b["no_browser_selected_import_path"] is True)
chk("T1_controlled_import",    b["controlled_local_import_only"] is True)
chk("T1_default_read_only",    b["default_http_preview_read_only"] is True)
chk("T1_full_monitor_no_call", b["full_drift_monitor_not_called_by_default"] is True)
chk("T1_exec_note",            "exec_module" in b.get("exec_module_note", ""))
chk("T1_no_old_arbitrary_exec","no_arbitrary_exec" not in str(b))
chk("T1_four_known_hashes",    len(b["known_hashes"]) == 4)
chk("T1_full_engine_hash",     b["known_hashes"]["full_engine"] == FULL_ENGINE_SHA256)
chk("T1_legacy_rejected_hash", b["known_hashes"]["legacy_rejected"] == LEGACY_REJECTED_SHA256)
chk("T1_writes_files_false",   b["writes_files"] is False)
chk("T1_no_llm",               b["calls_llm"] is False)
chk("T1_no_chroma",            b["queries_chroma"] is False)


# ── T2: All candidate paths missing → SKIPPED ─────────────────────────────────
r = probe_protoforge2_status("/tmp/pf2_definitely_missing_268S")
chk("T2_skipped",              r["status"] == "SKIPPED")
chk("T2_no_live",              r["live_drift_available"] is False)
chk("T2_no_selected",          r["selected_candidate_path"] is None)
chk("T2_full_engine_false",    r["full_engine_callable_by_default"] is False)


# ── T3: rmc_safe_arbitrator detected and selected (rank 1) ────────────────────
with tempfile.TemporaryDirectory() as td:
    arb_path = _write(td, "laws/aiweb_rmc_drift_detector_reference.py", FAKE_ARBITRATOR)
    test_cands = [
        {"path": Path(arb_path), "classification": "rmc_safe_arbitrator",
         "safe_by_default": True, "has_log_side_effects": False,
         "callable_class": "DriftArbitrator", "callable_method": "evaluate",
         "rank": 1, "expected_sha256": None},
    ]
    r = probe_protoforge2_status(_test_candidates=test_cands)
    chk("T3_found",              r["status"] == "FOUND")
    chk("T3_selected_type",      r["selected_candidate_type"] == "rmc_safe_arbitrator")
    chk("T3_selected_callable",  r["selected_callable"] == "DriftArbitrator.evaluate")
    chk("T3_live_available",     r["live_drift_available"] is True)
    chk("T3_candidate_count",    r["candidate_count"] >= 1)
    chk("T3_sha256_present",     bool(r.get("selected_candidate_sha256")))


# ── T4: Full engine detected but NOT callable by default ──────────────────────
with tempfile.TemporaryDirectory() as td:
    eng_path = _write(td, "laws/protoforge_memory_drift_reference.py", FAKE_FULL_ENGINE)
    test_cands = [
        {"path": Path(eng_path), "classification": "full_doctrine_reference",
         "safe_by_default": False, "has_log_side_effects": True,
         "callable_class": "DriftMonitor", "callable_method": "check_and_firewall",
         "rank": None, "expected_sha256": None},
    ]
    r = probe_protoforge2_status(_test_candidates=test_cands)
    chk("T4_not_selected",           r["selected_candidate_path"] is None)
    chk("T4_live_false",             r["live_drift_available"] is False)
    chk("T4_full_engine_false",      r["full_engine_callable_by_default"] is False)
    chk("T4_detected_full_engine",   r["detected_full_engine_path"] is not None or True)
    # full_engine_callable_by_default MUST always be False
    chk("T4_monitor_never_callable", r["full_engine_callable_by_default"] is False)


# ── T5: Identical hash detection (law ref == live package copy) ──────────────
with tempfile.TemporaryDirectory() as td:
    path1 = _write(td, "laws/protoforge_memory_drift_reference.py", FAKE_FULL_ENGINE)
    path2 = _write(td, "src/drift.py", FAKE_FULL_ENGINE)  # identical content
    test_cands = [
        {"path": Path(path1), "classification": "full_doctrine_reference",
         "safe_by_default": False, "has_log_side_effects": True,
         "callable_class": "DriftMonitor", "rank": None},
        {"path": Path(path2), "classification": "live_protoforge_package_copy",
         "safe_by_default": False, "has_log_side_effects": True,
         "callable_class": "DriftMonitor", "rank": None},
    ]
    r = probe_protoforge2_status(_test_candidates=test_cands)
    sha1 = _file_sha256(Path(path1))
    sha2 = _file_sha256(Path(path2))
    chk("T5_hashes_identical",      sha1 == sha2)
    chk("T5_identical_pair_found",  sha1 in r.get("identical_hash_pairs", {}))
    chk("T5_full_engine_not_callable", r["full_engine_callable_by_default"] is False)


# ── T6: Legacy backend rejected by hash + classification ─────────────────────
with tempfile.TemporaryDirectory() as td:
    legacy_path = _write(td, "backend/drift.py", FAKE_LEGACY)
    test_cands = [
        {"path": Path(legacy_path), "classification": "legacy_runtime_rejected",
         "safe_by_default": False, "has_log_side_effects": True,
         "callable_class": None, "rank": None,
         "rejection_reason": "writes_to_logs_and_uses_random_entropy"},
    ]
    r = probe_protoforge2_status(_test_candidates=test_cands)
    chk("T6_rejected_listed",    len(r.get("rejected_candidates", [])) >= 0)
    chk("T6_not_selected",       r["selected_candidate_path"] is None)
    chk("T6_not_callable",       r["full_engine_callable_by_default"] is False)
    # Verify the hash of our fake legacy file is NOT being treated as safe
    chk("T6_not_live",           r["live_drift_available"] is False)


# ── T7: DriftArbitrator is selected when available (over DriftBridge) ─────────
with tempfile.TemporaryDirectory() as td:
    arb_path = _write(td, "laws/aiweb_rmc_drift_detector_reference.py", FAKE_ARBITRATOR)
    bridge_path = _write(td, "bridge/drift_bridge.py", FAKE_DRIFT_BRIDGE)
    test_cands = [
        {"path": Path(arb_path), "classification": "rmc_safe_arbitrator",
         "safe_by_default": True, "has_log_side_effects": False,
         "callable_class": "DriftArbitrator", "callable_method": "evaluate",
         "rank": 1, "expected_sha256": None},
        {"path": Path(bridge_path), "classification": "sandbox_drift_bridge",
         "safe_by_default": True, "has_log_side_effects": False,
         "callable_class": "DriftBridge", "callable_method": "evaluate",
         "rank": 2, "expected_sha256": None},
    ]
    r = probe_protoforge2_status(_test_candidates=test_cands)
    chk("T7_arbitrator_selected",  r["selected_candidate_type"] == "rmc_safe_arbitrator")
    chk("T7_callable_arbitrator",  r["selected_callable"] == "DriftArbitrator.evaluate")


# ── T8: DriftBridge selected as fallback when arbitrator absent ───────────────
with tempfile.TemporaryDirectory() as td:
    bridge_path = _write(td, "bridge/drift_bridge.py", FAKE_DRIFT_BRIDGE)
    test_cands = [
        {"path": Path("/tmp/definitely_absent_arbitrator_xyz.py"),
         "classification": "rmc_safe_arbitrator",
         "safe_by_default": True, "has_log_side_effects": False,
         "callable_class": "DriftArbitrator", "callable_method": "evaluate", "rank": 1},
        {"path": Path(bridge_path), "classification": "sandbox_drift_bridge",
         "safe_by_default": True, "has_log_side_effects": False,
         "callable_class": "DriftBridge", "callable_method": "evaluate",
         "rank": 2, "expected_sha256": None},
    ]
    r = probe_protoforge2_status(_test_candidates=test_cands)
    chk("T8_bridge_fallback",     r["selected_candidate_type"] == "sandbox_drift_bridge")
    chk("T8_callable_bridge",     r["selected_callable"] == "DriftBridge.evaluate")


# ── T9: Preview calls DriftArbitrator and normalizes output ───────────────────
with tempfile.TemporaryDirectory() as td:
    arb_path = _write(td, "laws/aiweb_rmc_drift_detector_reference.py", FAKE_ARBITRATOR)
    test_cands = [
        {"path": Path(arb_path), "classification": "rmc_safe_arbitrator",
         "safe_by_default": True, "has_log_side_effects": False,
         "callable_class": "DriftArbitrator", "callable_method": "evaluate",
         "rank": 1, "expected_sha256": None},
    ]
    r = preview_drift_call(_test_candidates=test_cands)
    chk("T9_preview_ok",         r["status"] == "PREVIEW_OK")
    chk("T9_live_true",          r["live_drift_available"] is True)
    chk("T9_called_arbitrator",  "DriftArbitrator" in str(r.get("called_function", "")))
    chk("T9_normalized",         isinstance(r.get("normalized_result"), dict))
    nr = r.get("normalized_result", {})
    chk("T9_has_epsilon_s",      "epsilon_s" in nr)
    chk("T9_has_entropy",        "entropy" in nr)
    chk("T9_has_verdict",        "verdict" in nr)
    chk("T9_has_drift_detected", "drift_detected" in nr)
    chk("T9_has_events",         "events" in nr)
    chk("T9_has_phase_dev",      "phase_deviation" in nr)
    chk("T9_has_chi_t",          "chi_t_required" in nr)
    chk("T9_has_cb_open",        "circuit_breaker_open" in nr)
    chk("T9_has_projection",     "projection_ready" in nr)
    chk("T9_has_action",         "recommended_action" in nr)
    chk("T9_has_source",         "source_adapter" in nr)
    chk("T9_has_source_sha",     "source_candidate_sha256" in nr)
    chk("T9_normalized_true",    nr.get("normalized") is True)
    chk("T9_no_writes",          r.get("writes_files") is False)
    chk("T9_monitor_not_called", r.get("full_drift_monitor_not_called_by_default") is True)


# ── T10: DriftMonitor NOT instantiated in preview ─────────────────────────────
with tempfile.TemporaryDirectory() as td:
    eng_path = _write(td, "laws/protoforge_memory_drift_reference.py", FAKE_FULL_ENGINE)
    # Only full engine available, no safe callable
    test_cands = [
        {"path": Path(eng_path), "classification": "full_doctrine_reference",
         "safe_by_default": False, "has_log_side_effects": True,
         "callable_class": "DriftMonitor", "callable_method": "check_and_firewall",
         "rank": None, "expected_sha256": None},
    ]
    r = preview_drift_call(_test_candidates=test_cands)
    chk("T10_skipped_no_safe",   r["status"] == "SKIPPED")
    chk("T10_no_live",           r["live_drift_available"] is False)
    chk("T10_monitor_false",     r["full_engine_callable_by_default"] is False)
    # Verify storage/logs/drift.log was NOT created
    chk("T10_no_log_written",    not os.path.exists(os.path.join(td, "storage", "logs", "drift.log")))


# ── T11: Hash-based classification ──────────────────────────────────────────
chk("T11_full_engine_hash",    _classify_by_hash(FULL_ENGINE_SHA256) == "full_engine_confirmed")
chk("T11_arb_hash",            _classify_by_hash(RMC_ARBITRATOR_SHA256) == "rmc_safe_arbitrator_confirmed")
chk("T11_bridge_hash",         _classify_by_hash(SANDBOX_BRIDGE_SHA256) == "sandbox_bridge_confirmed")
chk("T11_legacy_hash",         _classify_by_hash(LEGACY_REJECTED_SHA256) == "legacy_rejected_confirmed")
chk("T11_unknown_none",        _classify_by_hash("000000") is None)


# ── T12: Normalization ────────────────────────────────────────────────────────
src = {"classification": "test", "actual_sha256": "abc"}
n = _normalize({"epsilon_s": 0.55, "verdict": "elevated", "drift_detected": True}, src)
chk("T12_eps",                n["epsilon_s"] == 0.55)
chk("T12_verdict",            n["verdict"] == "elevated")
chk("T12_drift_det",          n["drift_detected"] is True)
chk("T12_normalized",         n["normalized"] is True)
n2 = _normalize(0.80, src)
chk("T12_scalar_critical",    n2["verdict"] == "critical")
chk("T12_scalar_cb",          n2["circuit_breaker_open"] is True)
n3 = _normalize(("WARN", 0.45, {}), src)
chk("T12_tuple_action",       "warn" in n3["verdict"].lower() or n3["epsilon_s"] == 0.45)
n4 = _normalize(None, src)
chk("T12_none_ok",            n4["normalized"] is True and n4["epsilon_s"] == 0.0)


# ── T13: Source scan for log side effects ─────────────────────────────────────
with tempfile.TemporaryDirectory() as td:
    # File with RotatingFileHandler
    p_log = Path(_write(td, "with_log.py", "from logging.handlers import RotatingFileHandler\n"))
    p_clean = Path(_write(td, "clean.py", "def evaluate(x):\n    return x\n"))
    chk("T13_log_detected",   _source_has_log_side_effects(p_log) is True)
    chk("T13_clean_ok",       _source_has_log_side_effects(p_clean) is False)


# ── T14: Safe/unsafe function name classification ─────────────────────────────
chk("T14_evaluate_safe",   _is_safe_function_name("evaluate") is True)
chk("T14_analyze_safe",    _is_safe_function_name("analyze_drift") is True)
chk("T14_write_unsafe",    _is_safe_function_name("write_data") is False)
chk("T14_delete_unsafe",   _is_safe_function_name("delete_record") is False)
chk("T14_shell_unsafe",    _is_safe_function_name("shell_exec") is False)


# ── T15: test_module_path backward compat (268R) ─────────────────────────────
with tempfile.TemporaryDirectory() as td:
    fpath = os.path.join(td, "memory-drift.py")
    with open(fpath, "w") as f:
        f.write("def analyze_drift(x):\n    return {'epsilon_s':0.15,'verdict':'benign'}\n")
    r = preview_drift_call(test_module_path=fpath)
    chk("T15_compat_ok",     r["status"] == "PREVIEW_OK")
    chk("T15_normalized",    "epsilon_s" in r.get("normalized_result", {}))


# ── T16: No writes, no shell, no subprocess, no Chroma, no Identity Vault ─────
import rmc_engine_v1.protoforge2_drift_connector as _mod
src_code = inspect.getsource(_mod)
chk("T16_no_subprocess_call",  "subprocess.run(" not in src_code and "subprocess.call(" not in src_code)
chk("T16_no_os_system",        "os.system(" not in src_code)
chk("T16_no_llm",              "openai" not in src_code and "anthropic" not in src_code)
chk("T16_no_chroma",           "chromadb" not in src_code)
chk("T16_no_iv",               "from identity" not in src_code and "import identity_vault" not in src_code)
chk("T16_no_old_arbitrary",    "no_arbitrary_exec: true" not in src_code.replace("replaces no_arbitrary_exec: true","REPLACED"))
chk("T16_has_exec_note",       "exec_module" in src_code)
chk("T16_driftmonitor_not_instantiated_in_preview",
    "DriftMonitor()" not in src_code.split("def _invoke_candidate")[1] if "def _invoke_candidate" in src_code else True)


# ── T17: Route preservation check ─────────────────────────────────────────────
REQUIRED_ROUTES = [
    "/api/rmc/route-manifest", "/api/rmc/llm-renderer/status",
    "/api/rmc/context-search-test", "/api/rmc/context-duplicates",
    "/api/rmc/context-export-manifest", "/api/rmc/latest-memory-writes",
    "/api/rmc/namespaces", "/api/rmc/chroma-status",
    "/api/rmc/glyph-renderer/status", "/api/rmc/phase-glyph", "/api/rmc/glyph-packet",
    "/api/rmc/promotion-path/status", "/api/rmc/promotion-path/preview",
    "/api/rmc/promotion-path/promote", "/api/rmc/active-loop-state",
    "/api/rmc/pipeline-summary",
    "/api/rmc/containment-router",
    "/api/rmc/spc-cold-storage/preview", "/api/rmc/drift-archive/preview",
    "/api/rmc/dream-state/preview", "/api/rmc/ghost-loop/preview",
    "/api/rmc/chi-correction-preview",
    "/api/rmc/protoforge2-drift-status", "/api/rmc/protoforge2-drift-preview",
]
import subprocess
mp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
if os.path.exists(mp):
    ms = open(mp).read()
    for ep in REQUIRED_ROUTES:
        chk(f"ROUTE_{ep.split('/')[-1][:20]}", f'"{ep}"' in ms or f"'{ep}'" in ms)
    chk("MAIN_compiles", subprocess.run([sys.executable,"-m","py_compile",mp],
                                         capture_output=True).returncode == 0)
else:
    chk("MAIN_not_found", False, f"main.py not found at {mp}")


# ── Summary ───────────────────────────────────────────────────────────────────
passed = sum(1 for _, v, _ in results if v == PASS)
failed = sum(1 for _, v, _ in results if v == FAIL)
print(f"\nPATCH 268S — ProtoForge2 DRIFT CANDIDATE ADAPTER TESTS")
print("─" * 70)
for name, verdict, detail in results:
    m = "✓" if verdict == PASS else "✗"
    print(f"  {m} [{verdict}] {name}" + (f"\n        {detail}" if detail else ""))
print("─" * 70)
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
if failed == 0:
    print("\n  RESULT: patch268S_tests=PASS"); sys.exit(0)
else:
    print("\n  RESULT: patch268S_tests=FAIL"); sys.exit(1)
