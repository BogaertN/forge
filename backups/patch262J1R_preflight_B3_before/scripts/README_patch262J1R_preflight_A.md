# Patch 262J1R-Preflight-A — Phase Parser Engine Extraction

## One-sentence summary

Extracts Phase Parser logic from `forge/main.py` into `forge/rmc_engine_v1/phase_parser.py`
and delivers a complete, installable Forge patch tarball with the full patched `main.py`.

## Context

This is the first patch in the 262J1R-Preflight series. The build sequence is:

```
262J1R-Preflight-A  Phase Parser extraction            ← THIS PATCH
262J1R-Preflight-B  Real Drift Engine from design docs
262J1R-Preflight-C  Candidate Generator extraction
262J1R-Preflight-D  Behavioral test suite
262J1R              Containment Router
262J2               Correction/Naming gate
262K                Echo Validator
```

The Drift Engine redesign (B) requires the Phase Parser to have a clean contract first.
The design docs (Section 5.4, Appendix C, Section 6.3) were fully reviewed before this
patch sequence was finalized.

## What this patch does

### 1. Extracts Phase Parser to engine module

Creates: `forge/rmc_engine_v1/phase_parser.py`

The `_p262f_*` helper functions previously embedded in `main.py` (134 lines) are now
a pure Python engine module. The public API:

- `parse_phase(source_text, source_metadata=None) → dict`
- `phase_catalog() → dict` — read-only Φ1–Φ9 definitions
- `phase_parser_boundary() → dict` — engine boundary declaration

`main.py` becomes a thin adapter (`_p262f_resolve_source` + `_p262f_rmc_phase_parser_v1`)
that:
1. Resolves source_text from query params or memory-object fallback
2. Passes source_text to `rmc_engine_v1.phase_parser.parse_phase()`
3. Wraps the result in the HTTP envelope

Source resolution stays in `main.py` because it requires `_p262a_rmc_memory_object_view_v1`.
The engine module declares `calls_main_py_functions: False`.

### 2. Fixes coherence_math.py — circuit breaker zero-score

The math kernel previously produced a non-zero `coherence_score` (e.g., 0.201) when
`circuit_breaker=True`. The -0.50 B_circuit penalty was insufficient to zero out
high-confidence positive terms. A non-zero score for a blocked candidate is misleading.

Fix: `coherence_score` is forced to `0.0` whenever `circuit_breaker=True`.
The pre-override value is preserved in `score_components["raw_coherence_before_circuit_override"]`.

This was caught by the behavioral tests before any code shipped — tests working as designed.

### 3. Exports `clamp` and `phase_num` from coherence_math

The duplicate `_p262i1_clamp` and `_p262i1_phase_num` functions in `main.py` previously
diverged silently from the kernel equivalents. They are now transparent wrappers that
delegate to `rmc_engine_v1.coherence_math.clamp` and `rmc_engine_v1.coherence_math.phase_num`.

The kernel now exports these utilities so downstream modules can import them directly
rather than reinventing them.

### 4. Adds manifest compiler schema validation

`compile_manifest_dry_run()` now validates all 12 required manifest sections before
returning a `manifest_packet`. A partial manifest cannot be returned.

### 5. Updates rmc_engine_v1/__init__.py

Module registry reflects extraction status. Planned extractions documented.

## What this patch does NOT do

- Does not add Forge CLI commands (command surface stays at 852)
- Does not run shell, call LLM, query Chroma, read DB files
- Does not write files during endpoint execution
- Does not write Identity Vault, write RMC live memory
- Does not enable final language rendering or projection
- Does not extract Drift Analyzer (Patch B) or Candidate Generator (Patch C)

## Files changed

```
forge/main.py                                 CHANGED — Phase Parser block replaced with thin adapter
forge/rmc_engine_v1/__init__.py               CHANGED — updated module registry
forge/rmc_engine_v1/phase_parser.py           NEW
forge/rmc_engine_v1/coherence_math.py         CHANGED — circuit breaker zero-score fix + exports
forge/rmc_engine_v1/manifest_compiler.py      CHANGED — schema validation guard
forge/scripts/test_rmc_phase_parser_behavior.py        NEW — 41 behavioral tests
forge/scripts/test_rmc_coherence_math_behavior.py      CHANGED — now tests clamp export
forge/scripts/patch262J1R_preflight_A_verify.py        NEW — verifier
forge/scripts/README_patch262J1R_preflight_A.md        NEW — this file
SHA256SUMS.txt                                NEW
```

## Install steps

```bash
# 1. Move patch to home and inspect
cd ~
tar -tf patch262J1R_preflight_A_YYYYMMDD.tar.gz

# 2. Safety grep (must return 0 hits)
tar -xOf patch262J1R_preflight_A_YYYYMMDD.tar.gz forge/main.py | \
  grep -c "os.system\|subprocess.call\|exec(\|eval(" || true

# 3. Backup current files
cp /home/nic/forge/main.py /home/nic/forge/main.py.bak_pre_262J1R_preflight_A
cp -r /home/nic/forge/rmc_engine_v1 /home/nic/forge/rmc_engine_v1.bak_pre_262J1R_preflight_A

# 4. Apply tarball (from forge root)
cd /home/nic
tar -xzf ~/patch262J1R_preflight_A_YYYYMMDD.tar.gz

# 5. Syntax check
cd /home/nic/forge
python3 -m py_compile main.py && echo "py_compile OK"
python3 -m py_compile rmc_engine_v1/phase_parser.py && echo "phase_parser OK"
python3 -m py_compile rmc_engine_v1/coherence_math.py && echo "coherence_math OK"
python3 -m py_compile rmc_engine_v1/manifest_compiler.py && echo "manifest_compiler OK"

# 6. Run verifier
python3 scripts/patch262J1R_preflight_A_verify.py

# 7. Run behavioral tests
python3 scripts/test_rmc_phase_parser_behavior.py
python3 scripts/test_rmc_coherence_math_behavior.py

# 8. Restart Forge
# (use your normal Forge restart command)

# 9. Verify command surface
# Expected: Found: 852, Missing: 0, Result: FORGE_COMMAND_SURFACE_OK

# 10. curl endpoint test
curl -s http://localhost:7477/api/rmc/phase-parser | python3 -m json.tool | \
  grep -E '"mode"|"engine_module_location"|"main_py_is_thin_adapter"'
# Expected:
#   "mode": "read_only_phase_parser_dry_run"
#   "engine_module_location": "forge/rmc_engine_v1/phase_parser.py"
#   "main_py_is_thin_adapter": true
```

## Expected verifier output

```
MACHINE_READABLE_VERDICTS:
  phase_parser_module_importable=True
  phase_parser_main_py_is_thin_adapter=True
  phase_parser_no_side_effects=True
  coherence_math_circuit_breaker_zeroes_score=True
  manifest_compiler_schema_validation_active=True
  main_py_old_phase_catalog_gone=True
  main_py_thin_adapter_present=True
  main_py_imports_phase_parser=True
  phase_parser_behavior_tests_pass=True
  coherence_math_behavior_tests_pass=True
  adds_forge_commands=True

RESULT: PATCH_262J1R_PREFLIGHT_A_VERIFY_OK
```

## What comes next

**Patch 262J1R-Preflight-B — Real Drift Engine**

This is the substantive redesign. The design docs (Appendix C Drift Taxonomy, Section 5.4,
Section 6.3) specify a proper drift architecture:

- Typed `DriftReport` and `DriftEvent` data structures
- Real `D_score` from rule-based taxonomy classification (not keyword counting)
- `σ_res` from phase coherence spread (not a fixed formula)
- `|ΔΦ|` from phase path deviation
- `ε_s = (σ_res + D_score + |ΔΦ|) / n` computed correctly
- Temporal drift trend tracking
- Honest mode label until real ProtoForge2 engine is connected
- Full behavioral test suite

The endpoint (`/api/rmc/drift-analyzer`) will be rewired to the real engine in the same patch.
