# Patch 282 — MEA Candidate Set Preview/Gate

This patch adds the first non-mutating MEA candidate-set preview gate.

It does **not** seal candidates, write files, write memory, write Chroma, touch Identity Vault, call an LLM, execute shell commands, seed live manifests, promote memory, render user output, mutate launcher behavior, or mutate the Operator Console UI.

## Added module

- `rmc_engine_v1/mea/candidate_set_gate.py`

## Added routes

- `GET /api/mea/candidate-set-gate/status`
- `GET /api/mea/candidate-set-preview`
- `POST /api/mea/candidate-set-gate`
- `POST /api/mea/candidate-preview-gate` alias

POST requests require:

```json
{"approval_token":"APPROVE_MEA_CANDIDATE_SET_GATE"}
```

The seed manifest is still validated through the Patch 281 seed gate. Candidate-set generation is preview-only.

## Hard laws preserved

- Candidate generation does not approve itself.
- Replay confirmation is required but does not equal verification.
- Hypothesis cannot render as verified claim.
- Recall cannot render as discovery.
- Rejected candidates are not user-visible.
- No `/api/mea/seal` route exists in this patch.
