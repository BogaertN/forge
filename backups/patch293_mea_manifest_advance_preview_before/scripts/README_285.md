# Patch 285 — MEA Seal Packet Preview / Future Seal Payload Normalizer

Patch 285 adds a deterministic, non-mutating seal-packet preview layer on top of Patch 284R seal readiness.

It does not create `/api/mea/seal`, execute a seal, write files, write RMC memory, write Chroma, touch Identity Vault, call an LLM, execute shell commands, perform network I/O, promote memory, or render user output.

## Added module

- `rmc_engine_v1/mea/seal_packet_preview.py`

## Added routes

- `GET /api/mea/seal-packet/status`
- `GET /api/mea/seal-packet-preview`
- `POST /api/mea/seal-packet-gate`
- `POST /api/mea/future-seal-payload-gate`

## Approval token

`APPROVE_MEA_SEAL_PACKET_PREVIEW`

## Expected canonical result

The canonical fixture produces two normalized future seal packet previews:

- `c_hypothesis_001` as the best packet candidate, claim status `hypothesis`.
- `c_branch_derive_001` as a bounded speculative branch packet.

Reference-only recall and rejected/tampered candidates remain blocked.

## Hard boundary

- `seals_candidates = false`
- `promotes_to_memory = false`
- `writes_files = false`
- `writes_memory = false`
- `writes_chroma = false`
- `writes_identity_vault = false`
- `calls_llm = false`
- `executes_shell = false`
- `seal_route_available = false`
