# Patch 262J1R-Preflight-B6R — Phase Parser Boundary + Trace Metadata Repair

Purpose: repair the live B6 phase-parser regression before Candidate Generator extraction.

The B6 live test showed `before` incorrectly emitted `keyword:or`, which made the parser choose Φ2 polarity for the input:

`How do we correct projection drift before naming?`

B6R fixes that by enforcing whole-word keyword boundaries, adding phrase/gate evidence for correction-before-naming and projection-drift language, and surfacing `confidence_status` plus `token_boundary_mode` in the phase state.

This patch is backend-only and side-effect free. It does not call the LLM, query Chroma, read DB files, execute shell commands, write memory, write files during runtime, approve output, render final language, or touch Identity Vault.

Files:

- `forge/main.py`
- `forge/rmc_engine_v1/phase_parser.py`
- `forge/scripts/patch262J1R_preflight_B6R_verify.py`
- `forge/scripts/test_rmc_phase_parser_boundary_B6R.py`

Expected verifier result:

`RESULT: PATCH_262J1R_PREFLIGHT_B6R_VERIFY_OK`
