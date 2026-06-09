# Patch 277 — MEA Convergence / Ancestry / Cost Scoring

## Purpose

Patch 277 adds the next read-only MEA scoring foundations for the Forge Discovery Kernel:

- `rmc_engine_v1/mea/convergence_scorer.py`
- `rmc_engine_v1/mea/goal_ancestry_scorer.py`
- `rmc_engine_v1/mea/operator_cost_scorer.py`

These modules compute:

- `Omega(c_i)` — convergence toward `M_t.success_conditions`
- `A(c_i)` — goal ancestry coherence back to the original problem root
- `K(c_i)` — normalized resource cost of the operator chain

## Boundary

This patch is still foundation-only. It does not activate live MEA problem solving.

It does not:

- create POST routes
- seed live problem manifests
- seal candidates
- write files
- write RMC memory
- write Chroma
- write Identity Vault data
- call an LLM
- execute shell commands
- alter RMC deep dry-run behavior
- alter launcher/appctl behavior
- alter Operator Console UI

## Endpoint

The existing read-only endpoint remains:

`GET /api/mea/foundation-status`

Patch 277 extends the status payload so it reports:

- `convergence_scorer: true`
- `goal_ancestry_scorer: true`
- `operator_cost_scorer: true`
- convergence, ancestry, and operator-cost formulas
- read-only self-score probes for the 144 Hz fixture

## Tests

Run from `~`:

```bash
python forge/scripts/patch277_verify.py
python forge/scripts/test_patch277_mea_convergence_ancestry_cost.py
```

Expected:

```text
RESULT: PATCH_277_VERIFY PASS
RESULT: PATCH_277_BEHAVIOR PASS
```

## Next Patch

Patch 278 should add:

- `operator_registry.py`
- `replay_engine.py`

Patch 278 is the first replay foundation. It should still be read-only unless explicitly approved otherwise.
