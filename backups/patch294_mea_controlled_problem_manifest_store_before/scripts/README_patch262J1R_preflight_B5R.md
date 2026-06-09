# Patch 262J1R-Preflight-B5R — Dataset Growth Route Repair

Purpose: repair the live `/api/rmc/dataset-growth/capture` route so missing approval returns structured JSON instead of a Python traceback. This patch also hardens B5A query parsing for LLM/document dataset hooks by making URL parsing local to the helper.

Boundary:
- No canonical reference mutation.
- No Identity Vault writes.
- No RMC live memory writes.
- No shell execution.
- Growth-dataset writes remain explicit-approval only.

Key fixed failure:
- `NameError: name '_pp_url' is not defined` in `main.py` dataset-growth capture route.

Expected verifier:
- `RESULT: PATCH_262J1R_PREFLIGHT_B5R_VERIFY_OK`
