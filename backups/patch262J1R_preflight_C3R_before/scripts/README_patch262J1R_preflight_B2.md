# Patch 262J1R-Preflight-B2 — RMC Resonance Lexicon + Gold Reference Foundation

## Purpose

This patch adds the calibration layer between raw English and the RMC Drift Engine.
It creates a read-only `resonance_lexicon.py` module and a gold reference fixture set.

The goal is to stop treating words as simple keyword weights. The engine now emits
resonance events that include operator, target gate, polarity, phase vector, scope,
confidence, and evidence span.

## New engine module

`forge/rmc_engine_v1/resonance_lexicon.py`

Endpoint:

`GET /api/rmc/resonance-lexicon?input=...`

Mode:

`read_only_resonance_lexicon_dry_run`

## New reference folder

`forge/rmc_engine_v1/reference/`

Files:

- `letter_phase_map_v1.json`
- `word_loop_seed_lexicon_v1.jsonl`
- `operator_phrase_lexicon_v1.jsonl`
- `transition_law_examples_v1.jsonl`
- `syntactic_firewall_examples_v1.jsonl`
- `gold_reference_v1.jsonl`
- `scripture_phase_archetypes_v1.jsonl`
- `README_rmc_resonance_reference_v1.md`

## Authority hierarchy

1. Letter resonance = weak signal. It may not trigger circuit breaker alone.
2. Word loop seed = medium signal.
3. Phrase/operator resonance = strong signal.
4. Sentence transition law and manifest/trace gates remain final authority.

## Critical behavior

- `bypass correction` = violation, projection blocked.
- `do not bypass correction` = safe/supportive, no violation.
- `project now without validation` = projection-law violation.
- `validate before projection` = lawful.
- Random malformed junk triggers syntactic firewall.
- Wide lawful phase paths are not punished only because they mention many phases.

## Boundary

Read-only only. No writes. No DB. No Chroma. No LLM. No shell. No memory mutation. No projection. No approved output.

## Verify

```bash
cd ~/forge
source .venv/bin/activate
python -m py_compile main.py rmc_engine_v1/resonance_lexicon.py rmc_engine_v1/drift_engine.py
python scripts/patch262J1R_preflight_B2_verify.py
python scripts/test_rmc_resonance_lexicon_behavior.py
python scripts/test_rmc_gold_reference_behavior.py
```
