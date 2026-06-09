# Patch 275R — MEA / Forge Discovery Kernel Foundation Visibility

Patch 275R supersedes Patch 275 and begins the Manifest Evolution Algebra (MEA) / Forge Discovery Kernel build in Forge.

This is a foundation patch only. It does not make Forge solve problems yet. It does not seed live problem manifests. It does not write RMC memory. It does not write Chroma. It does not touch Identity Vault. It does not call an LLM. It does not create shell execution routes.

## What this patch adds

- `forge/rmc_engine_v1/mea/__init__.py`
- `forge/rmc_engine_v1/mea/manifest_schema.py`
- `forge/rmc_engine_v1/mea/unknown_detector.py`
- `forge/rmc_engine_v1/mea/discovery_kernel.py`
- `forge/scripts/patch275_verify.py`
- `forge/scripts/test_patch275_mea_foundation.py`
- `forge/scripts/README_275.md`
- `forge/SHA256SUMS.txt`

It is based on the Claude MEA Foundation Patch A source packet, then rebased and production-packaged against the uploaded Patch 274R current-state packet. It also rebases `forge/main.py` from the uploaded Patch 274R current-state packet and adds one read-only GET endpoint:

- `/api/mea/foundation-status`

The endpoint reports module presence, schema version, explicit Forge Discovery Kernel foundation identity, 144 Hz fixture availability, and boundary status only.

## What this patch does not do

- No POST routes.
- No full live Discovery Kernel runtime.
- No controlled seed manifest route.
- No seal candidate route.
- No memory writer integration.
- No RMC renderer integration.
- No UI changes.
- No launcher/appctl changes.
- No deep-dry-run behavior changes.

## Verification commands

Run from home so relative paths resolve correctly:

```bash
cd ~
python forge/scripts/patch275_verify.py
python forge/scripts/test_patch275_mea_foundation.py
```

Expected:

- `RESULT: PATCH_275R_VERIFY PASS`
- `RESULT: PATCH_275R_BEHAVIOR PASS`

## Live endpoint check after restart

```bash
curl -s 'http://localhost:7477/api/mea/foundation-status' | python -m json.tool | head -120
```

Expected core fields:

- `status: OK`
- `endpoint: /api/mea/foundation-status`
- `modules.discovery_kernel: true`
- `kernel.kernel_name: Forge Discovery Kernel`
- `kernel.full_runtime_active: false`
- `kernel.foundation_visible: true`
- `read_only: true`
- `writes_files: false`
- `calls_llm: false`
- `test_fixture.problem_id: 144hz_substrate_status`
- `test_fixture.expected_future_classification: hypothesis_not_verified_claim`

## Rollback

Patch 275 is additive except for the read-only route insertion in `main.py`. If rollback is required:

```bash
cd ~/forge
cp backups/patch275_mea_foundation_before/main.py main.py
rm -rf rmc_engine_v1/mea
rm -rf rmc_engine_v1/mea
rm -f scripts/patch275_verify.py scripts/test_patch275_mea_foundation.py scripts/README_275.md
```

Then restart AI.Web OS if it was running.

## Next patch

Patch 276 should add MEA scoring foundations:

- `proof_debt_scorer.py`
- `information_gain_scorer.py`

Those modules compute `B(c_i) = 1 - E(c_i)` and `I(c_i) = delta-K + delta-Q + delta-X`.
