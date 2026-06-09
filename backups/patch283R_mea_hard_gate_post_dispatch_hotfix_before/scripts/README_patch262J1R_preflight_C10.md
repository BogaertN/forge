# Patch 262J1R-Preflight-C10 — Manifest Contract + Echo Threshold + Renderer Guardrails

This patch implements the first three audit-priority production hardening items after C9:

1. `projection_status` is now a required manifest field in `manifest_compiler.py`.
2. Echo Validator now uses output-mode thresholds:
   - `formal_text`: 0.85
   - `text`: 0.82
   - `json_packet`: 0.90
   - `dashboard_state`: 0.80
   - `glyph_packet`: 0.80
   - `internal_debug`: 0.72
3. Output Renderer now builds and enforces a sentence plan containing:
   - `core_claim`
   - `required_qualifiers`
   - `required_definitions`
   - `forbidden_claims`
   - `allowed_claim_scope`
   - `audience`
   - `mode`

The renderer blocks forbidden projection/memory-write claims before echo validation. The echo validator still remains the downstream authority for render fidelity.

Read-only boundaries remain intact. No LLM calls, Chroma calls, DB reads, shell execution, Identity Vault writes, canonical reference mutation, or memory writes are added.

Expected verifier result:

```text
RESULT: PATCH_262J1R_PREFLIGHT_C10_VERIFY_OK
```
