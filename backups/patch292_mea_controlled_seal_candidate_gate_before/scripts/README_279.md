# Patch 279R — MEA Claim Status Classifier Export Hotfix

## Purpose

Patch 279 adds the read-only MEA claim status classifier:

`forge/rmc_engine_v1/mea/claim_status_classifier.py`

It classifies replay-confirmed candidate manifests structurally as:

- `recall`
- `verified_claim`
- `derived_claim`
- `hypothesis`
- `speculative_branch`
- `contradiction_exposed`
- `test_required`
- `rejected`
- `cold_stored`
- `named_concept`
- `partial_resolution`
- `resolved_manifest`

## Hard laws

- Replay confirmed does not automatically mean verified.
- A recall must not render as discovery.
- A hypothesis must not render as a verified claim.
- A rejected candidate must not be user-visible.

## Boundary

Patch 279 is read-only and additive.

It does not:

- create POST routes
- seed live manifests
- seal candidates
- write files or memory
- write Chroma
- write Identity Vault
- call an LLM
- execute shell commands
- mutate the Operator Console UI
- mutate launcher/appctl behavior

## Verification

Run from home:

```bash
cd ~
python forge/scripts/patch279_verify.py
python forge/scripts/test_patch279_mea_claim_status_classifier.py
```

Expected:

```text
RESULT: PATCH_279_VERIFY PASS
RESULT: PATCH_279_BEHAVIOR PASS
```

## Live endpoint check

```bash
curl -s http://localhost:7477/api/mea/foundation-status | python -m json.tool | grep -E '"current_patch"|"claim_status_classifier"|"classifier_formula"|"expected_self_classification"|"expected_144hz_d1_classification"'
```

Expected signs:

```text
"current_patch": "Patch 279R — MEA Claim Status Classifier Export Hotfix"
"claim_status_classifier": true
"classifier_formula": "ClaimStatus(c*) = f(B, I, Replay, Omega, D, gates)"
"expected_self_classification": "recall"
"expected_144hz_d1_classification": "hypothesis_not_verified_claim"
```


## Patch 279R Hotfix Note

Patch 279R fixes the package-root export expected by the live `/api/mea/foundation-status` endpoint. Patch 279 imported `classifier_boundary` from `rmc_engine_v1.mea`, while `__init__.py` only exported `claim_status_classifier_boundary`. Patch 279R binds `classifier_boundary = claim_status_classifier_boundary` and verifies both names are available.
