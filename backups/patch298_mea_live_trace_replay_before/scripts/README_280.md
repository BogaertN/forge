# Patch 280 — MEA Read-Only API / Operator Console Visibility

## Purpose

Patch 280 exposes the accepted MEA foundation stack through four backend-owned, GET-only preview routes so the Operator Console can inspect MEA state without gaining authority over it.

## Added routes

- `/api/mea/problem-manifest-preview`
- `/api/mea/unknown-vector-preview`
- `/api/mea/claim-status-preview`
- `/api/mea/replay-preview`

These routes are inspection surfaces only. They do not seed live manifests, seal candidates, promote memory, call LLMs, execute shell commands, write files, write Chroma, write Identity Vault, or mutate existing RMC behavior.

## Added module

- `forge/rmc_engine_v1/mea/api_preview.py`

## Updated files

- `forge/main.py`
- `forge/rmc_engine_v1/mea/__init__.py`
- `forge/rmc_engine_v1/mea/discovery_kernel.py`
- `forge/scripts/patch280_verify.py`
- `forge/scripts/test_patch280_mea_read_only_api_visibility.py`
- `forge/scripts/README_280.md`
- `forge/SHA256SUMS.txt`

## Boundary

Patch 280 is read-only. It creates GET routes only. It does not create any POST route under `/api/mea`.

Forbidden in this patch:

- `/api/mea/problem-manifest` live seed route
- `/api/mea/candidates` live candidate set route
- `/api/mea/seal` route
- `/api/mea/replay` POST verification route
- any live memory promotion
- any renderer integration

## Expected verification

```bash
cd ~
python forge/scripts/patch280_verify.py
python forge/scripts/test_patch280_mea_read_only_api_visibility.py
```

Expected:

```text
RESULT: PATCH_280_VERIFY PASS
RESULT: PATCH_280_BEHAVIOR PASS
```

## Live endpoint checks

After restart:

```bash
~/forge/scripts/aiweb-os-restart
curl -s http://localhost:7477/api/mea/foundation-status | python -m json.tool | grep -E '"current_patch"|"api_preview"|"read_only_api_visible"|"sealing_active"'
curl -s http://localhost:7477/api/mea/problem-manifest-preview | python -m json.tool | head -80
curl -s http://localhost:7477/api/mea/unknown-vector-preview | python -m json.tool | head -80
curl -s http://localhost:7477/api/mea/claim-status-preview | python -m json.tool | head -120
curl -s http://localhost:7477/api/mea/replay-preview | python -m json.tool | head -120
```
