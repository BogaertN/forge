#!/usr/bin/env python3
"""Patch 268 — ProtoForge2 Drift Connector Tests.
Run: python scripts/test_patch268_pf2_drift_connector.py
"""
from __future__ import annotations
import sys, os, tempfile, inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rmc_engine_v1.protoforge2_drift_connector import (
    probe_protoforge2_status, probe_protoforge2_import,
    preview_drift_call, boundary, _is_safe_function_name,
    _is_suspicious_path, _normalize_pf2_output, DEFAULT_PF2_ROOT,
    SAFE_FUNCTION_PATTERNS, UNSAFE_FUNCTION_PATTERNS,
)
from pathlib import Path as _Path

PASS, FAIL = "PASS", "FAIL"
results = []
def chk(n, ok, d=""): results.append((n, PASS if ok else FAIL, d))

# ── Boundary ──────────────────────────────────────────────────────────────────
b = boundary()
chk("B_read_only",             b["read_only"] is True)
chk("B_no_writes",             b["writes_files"] is False)
chk("B_no_shell",              b["executes_shell"] is False)
chk("B_no_llm",                b["calls_llm"] is False)
chk("B_no_iv",                 b["writes_identity_vault"] is False)
chk("B_importlib_method",      "importlib" in b["import_method"])
chk("B_hyphen_handled",        "hyphen" in b["import_method"].lower())
chk("B_three_adapter_modes",   set(b["adapter_modes"]) == {"LIVE","SKIPPED","FALLBACK"})
chk("B_no_modify_pf2",         b["safety_rules"]["no_modify_pf2"] is True)
chk("B_path_traversal_check",  b["safety_rules"]["path_traversal_check"] is True)

# ── T1: Missing ProtoForge2 root → SKIPPED ────────────────────────────────────
r = probe_protoforge2_status("/tmp/pf2_definitely_missing_12345")
chk("T1_skipped",              r["status"] == "SKIPPED")
chk("T1_root_false",           r["protoforge2_root_exists"] is False)
chk("T1_module_false",         r["drift_module_found"] is False)
chk("T1_not_live",             r["live_drift_available"] is False)
chk("T1_fallback_structural",  "structural" in str(r.get("fallback_mode","")).lower())

# ── T2: Root exists but no drift module → SKIPPED ────────────────────────────
with tempfile.TemporaryDirectory() as tmpdir:
    r = probe_protoforge2_status(tmpdir)
    chk("T2_root_found",           r["protoforge2_root_exists"] is True)
    chk("T2_module_not_found",     r["drift_module_found"] is False)
    chk("T2_skipped",              r["status"] == "SKIPPED")
    chk("T2_has_root_contents",    "root_contents" in r)

# ── T3: Hyphen filename import path handled ───────────────────────────────────
with tempfile.TemporaryDirectory() as tmpdir:
    # Create a fake memory-drift.py with a hyphen in the name
    fake_module = os.path.join(tmpdir, "memory-drift.py")
    with open(fake_module, "w") as f:
        f.write('''"""Fake ProtoForge2 drift module for testing."""
def analyze_drift(payload):
    """Harmless probe function."""
    return {"epsilon_s": 0.15, "drift_type": "test_low_drift", "circuit_breaker": False}
def compute_epsilon(payload):
    return 0.15
def write_data(data):   # this should be blocked as unsafe
    pass
''')
    # probe_protoforge2_status should find it
    r = probe_protoforge2_status(tmpdir)
    chk("T3_module_found",         r["drift_module_found"] is True)
    chk("T3_found_hyphen_file",    "memory-drift" in str(r.get("drift_module_path","")))
    chk("T3_has_sha256",           bool(r.get("module_sha256")))
    chk("T3_has_functions",        len(r.get("available_functions",[])) > 0)
    chk("T3_unsafe_blocked",       "write_data" in r.get("unsafe_blocked_functions",[]) or
                                   "write_data" not in r.get("safe_callable_functions",[]))

    # probe_protoforge2_import should succeed
    ri = probe_protoforge2_import(tmpdir)
    chk("T3_importable",           ri.get("importable") is True)
    chk("T3_adapter_live",         ri.get("adapter_mode") == "LIVE")
    chk("T3_live_available",       ri.get("live_drift_available") is True)

    # preview_drift_call should normalise output
    rp = preview_drift_call(test_module_path=fake_module)
    chk("T3_preview_ok",           rp["status"] == "PREVIEW_OK")
    chk("T3_normalized",           isinstance(rp.get("normalized_result"), dict))
    chk("T3_eps_normalized",       "epsilon_s" in rp.get("normalized_result", {}))
    chk("T3_live_drift_true",      rp.get("live_drift_available") is True)
    chk("T3_called_function",      bool(rp.get("called_function")))

# ── T4: Module SHA256 reported ────────────────────────────────────────────────
with tempfile.TemporaryDirectory() as tmpdir:
    fpath = os.path.join(tmpdir, "drift.py")
    with open(fpath, "w") as f:
        f.write("def analyze(x): return {'epsilon_s': 0.2}\n")
    r = probe_protoforge2_status(tmpdir)
    chk("T4_sha_present",   bool(r.get("module_sha256")) and len(r.get("module_sha256","")) == 64)

# ── T5: Unsafe path refused ───────────────────────────────────────────────────
from pathlib import Path
chk("T5_suspicious_etc",       _is_suspicious_path(Path("/etc/passwd")) is True)
chk("T5_suspicious_root",      _is_suspicious_path(Path("/root/data")) is True)
chk("T5_ok_home",              _is_suspicious_path(Path("/home/nic/something")) is False)
chk("T5_ok_tmp",               _is_suspicious_path(Path("/tmp/anything")) is False)
r = probe_protoforge2_status("/etc/passwd")
chk("T5_refused",              r["status"] == "REFUSED_UNSAFE_PATH")

# ── T6: Normalization ─────────────────────────────────────────────────────────
n = _normalize_pf2_output({"epsilon_s": 0.55, "drift_type": "semantic_drift"}, "analyze")
chk("T6_eps_normalized",        n["epsilon_s"] == 0.55)
chk("T6_dtype_normalized",      n["drift_type"] == "semantic_drift")
chk("T6_cb_inferred",           n["circuit_breaker"] is False)  # 0.55 < 0.72

n2 = _normalize_pf2_output(0.80, "compute")
chk("T6_scalar_normalized",     n2["status"] == "NORMALIZED_SCALAR")
chk("T6_scalar_cb",             n2["circuit_breaker"] is True)  # 0.80 >= 0.72

n3 = _normalize_pf2_output(None, "broken")
chk("T6_failed_normalization",  n3["status"] == "NORMALIZATION_FAILED")

# ── T7: Safe/unsafe function name classification ──────────────────────────────
chk("T7_analyze_safe",          _is_safe_function_name("analyze_drift") is True)
chk("T7_compute_safe",          _is_safe_function_name("compute_epsilon") is True)
chk("T7_write_unsafe",          _is_safe_function_name("write_data") is False)
chk("T7_delete_unsafe",         _is_safe_function_name("delete_record") is False)
chk("T7_shell_unsafe",          _is_safe_function_name("shell_exec") is False)
chk("T7_run_unsafe",            _is_safe_function_name("run_command") is False)

# ── T8: Fallback on call failure ──────────────────────────────────────────────
with tempfile.TemporaryDirectory() as tmpdir:
    fpath = os.path.join(tmpdir, "drift.py")
    with open(fpath, "w") as f:
        f.write("def analyze(x): raise RuntimeError('simulated pf2 error')\n")
    r = preview_drift_call(test_module_path=fpath)
    chk("T8_call_fail_fallback",   r["status"] in ("CALL_FAILED", "FALLBACK"))
    chk("T8_not_live",             r.get("live_drift_available") is not True)
    chk("T8_no_crash",             True)

# ── T9: No writes, no shell, no Chroma, no Identity Vault, no LLM ─────────────
import rmc_engine_v1.protoforge2_drift_connector as _mod
src = inspect.getsource(_mod)
chk("T9_no_subprocess_call",   "subprocess.run(" not in src and "subprocess.call(" not in src)
chk("T9_no_os_system",         "os.system(" not in src)
chk("T9_no_llm",               "openai" not in src and "anthropic" not in src)
chk("T9_no_chroma",            "chromadb" not in src)
chk("T9_no_iv",           "from identity" not in src and "import identity_vault" not in src)
chk("T9_no_open_write",        'open(' not in src or '"w"' not in src)

# ── T10: Real PF2 root — handles gracefully if absent ─────────────────────────
r = probe_protoforge2_status(DEFAULT_PF2_ROOT)
chk("T10_real_path_no_crash",  "status" in r)
chk("T10_real_path_reads_false_or_found",
    r["status"] in ("SKIPPED", "FOUND", "REFUSED_UNSAFE_PATH"))
# If FOUND, must have sha256 and functions
if r["status"] == "FOUND":
    chk("T10_found_has_sha256",  bool(r.get("module_sha256")))
    chk("T10_found_has_funcs",   isinstance(r.get("available_functions"), list))

# Summary
passed = sum(1 for _,v,_ in results if v==PASS)
failed = sum(1 for _,v,_ in results if v==FAIL)
print(f"\nPATCH 268 — ProtoForge2 DRIFT CONNECTOR TESTS")
print("─"*65)
for name, verdict, detail in results:
    m = "✓" if verdict == PASS else "✗"
    print(f"  {m} [{verdict}] {name}" + (f"\n        {detail}" if detail else ""))
print("─"*65)
print(f"  Total: {len(results)}  Passed: {passed}  Failed: {failed}")
if failed==0: print("\n  RESULT: patch268_pf2_drift_connector_tests=PASS"); sys.exit(0)
else: print("\n  RESULT: patch268_pf2_drift_connector_tests=FAIL"); sys.exit(1)
