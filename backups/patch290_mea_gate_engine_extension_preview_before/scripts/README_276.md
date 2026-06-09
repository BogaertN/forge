# Patch 276 — MEA Scoring Foundations

This patch adds the first read-only Manifest Evolution Algebra scoring layer to Forge.

## New modules

- `forge/rmc_engine_v1/mea/proof_debt_scorer.py`
- `forge/rmc_engine_v1/mea/information_gain_scorer.py`

## Equations implemented

- `B(c_i) = 1 - E(c_i)`
- `I(c_i) = delta-K + delta-Q + delta-X`

## Boundary

Patch 276 is additive and read-only.

It does not:

- create MEA POST routes
- seed live manifests
- seal candidates
- write files
- write memory
- write Chroma
- write Identity Vault data
- call an LLM
- execute shell commands
- change Operator Console UI
- change launcher/appctl behavior

## Why this patch exists

Patch 275R made the Forge Discovery Kernel visible as a foundation surface. Patch 276 adds the first scoring modules required before MEA can classify or seal anything. It still does not solve problems or render MEA output.

## 144 Hz anti-confabulation fixture

The canonical 144 Hz test fixture must remain proof-debt constrained:

- proof debt: `0.85`
- evidence support: `0.15`
- information gain against itself: `0.0`
- later classifier expectation: `hypothesis`, not `verified_claim`

That protects Forge from treating a useful harmonic hypothesis as an empirically verified claim.

## Verification

Run from home or from the Forge root:

```bash
cd ~
python forge/scripts/patch276_verify.py
python forge/scripts/test_patch276_mea_scoring_foundations.py
```

Expected:

```text
RESULT: PATCH_276_VERIFY PASS
RESULT: PATCH_276_BEHAVIOR PASS
```
