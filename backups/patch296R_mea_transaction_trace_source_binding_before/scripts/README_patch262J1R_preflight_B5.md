# Patch 262J1R-Preflight-B5 — RMC Dataset Growth + Promotion Pipeline

This patch adds the dataset growth layer that keeps the RMC resonance/gold reference corpus expandable without poisoning canonical reference truth.

## New module

- `forge/rmc_engine_v1/dataset_growth.py`

## New endpoints

- `GET /api/rmc/dataset-growth/status`
- `GET /api/rmc/dataset-growth/capture-preview?input=...`
- `GET /api/rmc/dataset-growth/capture?input=...&approval=CAPTURE_RMC_DATASET_OBSERVATION`
- `GET /api/rmc/dataset-growth/capture?input=...&approval=CAPTURE_AND_QUEUE_RMC_DATASET_CANDIDATE`
- `GET /api/rmc/dataset-growth/coverage`

## Growth root

`/home/nic/forge/memory/rmc_dataset_v1/`

Normal runtime can write observations and review-queue candidate examples only after explicit approval. Normal runtime cannot mutate canonical reference files under `forge/rmc_engine_v1/reference/`.

## Law

Raw input becomes observation, not gold truth. Observation can become candidate. Candidate enters review. Reviewed candidates may be promoted only by a future approved patch.
