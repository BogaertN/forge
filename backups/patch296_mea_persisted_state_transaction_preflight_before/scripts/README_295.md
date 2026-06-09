# Patch 295 — MEA Controlled Live Candidate API

## Purpose

Patch 295 exposes `GET /api/mea/candidates` as the first read-only downstream consumer of the persisted MEA problem manifest created by Patch 294. It reads the integrity-verified stored `M_t`, generates candidate previews through the existing operator engine and candidate generator, scores through the coherence extension, and applies the reusable gate engine.

## Runtime Chain

```text
verified persisted M_t (Patch 294)
  -> operator_engine.py creates drafts d_i
  -> candidate_generator.py verifies candidate previews c_i
  -> coherence_extension.py ranks previews only
  -> gate_engine.py decides preview eligibility
  -> GET /api/mea/candidates returns a read-only report
```

## Hard Boundary

This patch is read-only. It does not commit any candidate, advance a manifest, execute a seal, write MEA state, write memory, write Chroma, touch Identity Vault, call an LLM, execute shell, perform network I/O, or render user output.

`Score can rank; score cannot override gates.`

## Persisted-State Integrity Requirement

The route refuses to generate candidates if Patch 294 state is absent or if its state hash, manifest hash, receipt, rollback plan, or manifest validation fails. Tampered persisted state produces `SOURCE_STATE_BLOCKED` and no candidate rows.

## Provenance Boundary

Patch 294 stored `state_core.source` as the canonical manifest source. It did not store the caller-supplied request source string as a separate provenance field. Patch 295 reports the stored canonical source and explicitly does not infer missing invocation provenance.

## Canonical 144 Hz Expected Behavior

```text
cg_recall_001     -> recall / REFERENCE_ONLY
cg_hypothesis_001 -> hypothesis / PASS_PREVIEW_ONLY
cg_branch_001     -> speculative_branch / PASS_BOUNDED_PREVIEW_ONLY
cg_tamper_001     -> rejected / REJECTED / containment preview
```

Current ranking can report the bounded branch above the harmonic hypothesis. That is not selection or state advance: `selection_executed=false` and `selected_candidate_id=null` remain enforced.

## New Route

```text
GET /api/mea/candidates
```

## Verification

```bash
python forge/scripts/patch295_verify.py
python forge/scripts/test_patch295_mea_live_candidates.py
```
