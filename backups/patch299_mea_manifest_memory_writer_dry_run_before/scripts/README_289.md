# Patch 289 — MEA Coherence Scorer Extension Preview

Patch 289 adds a preview-only coherence adapter for generated MEA candidates. It ranks candidates using available MEA terms and declared RMC fallback terms, while proving that scores cannot override hard gates.

## Adds

- `rmc_engine_v1/mea/coherence_extension.py`
- `GET /api/mea/coherence-extension/status`
- `GET /api/mea/coherence-extension-preview`
- `POST /api/mea/coherence-extension-gate`

## Approval token

`APPROVE_MEA_COHERENCE_EXTENSION_PREVIEW`

## Hard law

- Score can rank.
- Score cannot override gates.
- Score cannot promote claim status.
- Score cannot permit render.
- Score cannot permit seal.
- Score cannot promote memory.

## Still blocked

- No `/api/mea/seal` route.
- No live candidate commit.
- No live manifest advance.
- No candidate sealing.
- No memory promotion.
- No Chroma writes.
- No Identity Vault writes.
- No LLM calls.
- No shell execution.
- No network I/O.
- No Operator Console UI mutation.

## Verify

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile main.py rmc_engine_v1/mea/*.py scripts/patch289_verify.py scripts/test_patch289_mea_coherence_extension.py
cd ~
python forge/scripts/patch289_verify.py
python forge/scripts/test_patch289_mea_coherence_extension.py
```
