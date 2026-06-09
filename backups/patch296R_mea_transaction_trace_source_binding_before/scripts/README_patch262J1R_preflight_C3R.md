# Patch 262J1R-Preflight-C3R — Correction/Naming Calibration + Route Consistency Repair

C3R reinforces C3 before manifest compilation.

It keeps the Correction/Naming stage read-only and adds calibration so the engine does not confuse a projection-gated score with candidate validity.

## Key changes

- Separates `candidate_validity_score` from `projection_gated_score`.
- Penalizes high semantic distance, high novelty delta, and low memory fit.
- Forces `recommended_route` and `chi_t_action` to agree.
- Prevents `stable_naming` unless measured support, corrected drift, phase legality, and naming confidence all pass.
- Derives proposed names from candidate text, memory anchors, and phase role.
- Keeps manifest, rendering, projection, memory write, LLM, shell, and Identity Vault actions blocked.

## Main verifier

```bash
python scripts/patch262J1R_preflight_C3R_verify.py
```

Expected:

```text
RESULT: PATCH_262J1R_PREFLIGHT_C3R_VERIFY_OK
```
