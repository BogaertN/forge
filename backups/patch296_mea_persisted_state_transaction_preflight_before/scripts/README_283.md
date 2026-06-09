# Patch 283R — MEA Hard Gate Report POST Dispatch Hotfix

Patch 283 adds a non-mutating hard-gate report layer over Patch 282 candidate previews.

It adds:

- `rmc_engine_v1/mea/hard_gate_report.py`
- `GET /api/mea/hard-gate-report/status`
- `GET /api/mea/hard-gate-report-preview`
- `POST /api/mea/hard-gate-report-gate`
- alias `POST /api/mea/candidate-hard-gate`

Approval token:

`APPROVE_MEA_HARD_GATE_REPORT`

Hard boundaries:

- no live candidate commit
- no candidate sealing
- no memory promotion
- no file writes
- no Chroma writes
- no Identity Vault writes
- no LLM calls
- no shell execution
- no network I/O
- no Operator Console UI mutation
- no launcher mutation

The report enforces replay, tamper, claim status, proof debt, information gain, convergence, drift, render-scope, seal-block, and memory-promotion-block gates.


## Patch 283R hotfix note

Patch 283R fixes live POST dispatch for `/api/mea/hard-gate-report-gate` and `/api/mea/candidate-hard-gate`. Patch 283 module behavior was valid, but the HTTP `do_POST` dispatcher did not route the new hard-gate POST paths, causing curl to receive an empty/non-JSON response. The hotfix adds explicit dispatch coverage and verifier checks for the POST path.
