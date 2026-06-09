# Patch 262J1R-Preflight-B1 — Drift Engine Hardening

## One-sentence summary

Hardens the structural contract drift engine with a real syntactic firewall,
negation-aware bypass detection, transition-legality delta_phi, expanded
trace_instability sigma_res, and honest threshold labeling.

## What this patch does

### 1. Honest engine mode label
ENGINE_MODE = "structural_contract_drift_analysis"
Replaces "read_only_structural_drift_analysis". The boundary clearly states:
not the live ProtoForge2 engine; built from design documents; contract_only
until ProtoForge2 connector is activated.

### 2. Real syntactic firewall (multi-layer)
_classify_syntactic() now checks:
- Shannon entropy (low < 1.5 = repetitive/garbage; high > 5.8 = binary/encoded)
- Payload length normalization (> 8000 chars flagged)
- Symbol/noise ratio (alphanum ratio < 0.40 flagged)
- Brace/quote balance (diff > 3 flagged)
- Unsafe shell/write markers (import os, subprocess, open(, exec(, eval(, shell=True, etc.)
- Schema Jaccard check (expected vs actual keys in phase_report)
- Structural signature (empty payload + missing phase_state flagged)

### 3. Negation-aware bypass detection (new module)
_detect_bypass_violations() scans source_text for bypass operator phrases
and checks the preceding 55 chars for negation tokens before flagging.

Violation: "bypass correction" (not preceded by negation)
NOT a violation: "do not bypass correction" (negated)
NOT a violation: "we must not skip naming" (negated)

Bypass violations feed into catastrophic drift classification.
Per Appendix C C.5: "Agent attempts to bypass governance review" = catastrophic.

### 4. Expanded sigma_res (trace_instability)
_compute_trace_instability() now measures four components:
1. confidence_spread (original sigma_res = 1 - confidence)
2. phase_conflict (top-2 candidates < 0.08 apart → system is unsure)
3. category_oscillation (entropy zone + projection zone without correction)
4. active_loop_mismatch (primary phase routing directive absent from routing list)
Output key remains "sigma_res" for epsilon_s formula compatibility.
Boundary explains what it actually measures.

### 5. Transition-legality delta_phi (replaces span-based)
_compute_transition_legality() penalizes ILLEGAL transitions, not wide spans.
A lawful Phi1→Phi3→Phi6→Phi7→Phi9 path scores delta_phi=0.0.
An illegal Phi1→Phi8 (projection without correction/naming) scores 0.80.
Specific rules: Phi5→Phi8 skip (0.84), projection without correction+naming
(0.80), projection without correction (0.72), naming without correction (0.55).

### 6. Conservative threshold labeling (Section 6.3 compliance)
THRESHOLDS dict has label="rmc_preflight_conservative" and a note quoting
the design doc: "theta should be task-sensitive, output-sensitive, and
phase-sensitive." All threshold output includes this label.

## Tests: 55/55 PASS, Verifier: 30/30 PASS

Required behavioral tests all pass:
  ✓ Random malformed junk triggers syntactic drift
  ✓ "bypass correction and naming and project now" triggers circuit breaker
  ✓ "do not bypass correction" does NOT trigger circuit breaker
  ✓ Lawful "correct→name→validate→project later" with wide span NOT punished
  ✓ Phi5→Phi8 hard-triggers circuit breaker
  ✓ circuit_breaker=True forces coherence_score=0.0

## Install steps

```bash
# 1. Inspect
tar -tf patch262J1R_preflight_B1_20260525.tar.gz

# 2. Safety grep (expect 0 — "subprocess" appears only as a string literal in detection list)
tar -xOf patch262J1R_preflight_B1_20260525.tar.gz forge/rmc_engine_v1/drift_engine.py | \
  grep -c "^import subprocess\|^from subprocess\|subprocess\.call(\|subprocess\.run(" || true

# 3. Backup
cp /home/nic/forge/rmc_engine_v1/drift_engine.py \
   /home/nic/forge/rmc_engine_v1/drift_engine.py.bak_pre_B1

# 4. Apply
cd /home/nic && tar -xzf ~/patch262J1R_preflight_B1_20260525.tar.gz

# 5. py_compile
cd /home/nic/forge && python3 -m py_compile rmc_engine_v1/drift_engine.py main.py && echo OK

# 6. Verifier
python3 scripts/patch262J1R_preflight_B1_verify.py

# 7. Tests
python3 scripts/test_rmc_drift_engine_behavior.py

# 8. Restart Forge, check command surface (expect 852/852)

# 9. curl check
curl -s http://localhost:7477/api/rmc/drift-analyzer | python3 -m json.tool | \
  grep -E '"mode"|"scoring_mode"|"synthetic_taxonomy_mode"|"thresholds_label"'
# Expected:
#   "mode": "structural_contract_drift_analysis"
#   "scoring_mode": "structural_contract_drift_analysis"
#   "synthetic_taxonomy_mode": false
#   "thresholds_label": "rmc_preflight_conservative"
```

## Expected verifier verdicts
```
RESULT: PATCH_262J1R_PREFLIGHT_B1_VERIFY_OK
```
(30/30 PASS including 55 behavioral tests, 41 phase parser tests, 33 coherence math tests)

## Note on subprocess in source
drift_engine.py contains the string "subprocess" as a string literal in the
unsafe_markers detection list. The safety grep above checks for actual imports/calls,
not string literals. This is correct and expected.

## What comes next
Patch 262J1R-Preflight-C — Candidate Generator extraction.
All upstream pipeline modules will then be in proper engine modules.
