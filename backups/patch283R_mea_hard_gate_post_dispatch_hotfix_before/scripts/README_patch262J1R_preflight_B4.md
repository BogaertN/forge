# Patch 262J1R-Preflight-B4 — Lexicon Expansion + Gold Standard Dataset Hardening

This patch expands the B2/B3 resonance lexicon from a seed foundation into a production-readiness reference corpus.

It adds:

- `rmc_engine_v1/lexicon_audit.py`
- expanded `word_loop_seed_lexicon_v1.jsonl`
- expanded `operator_phrase_lexicon_v1.jsonl`
- expanded `gold_reference_v1.jsonl`
- expanded `transition_law_examples_v1.jsonl`
- expanded `syntactic_firewall_examples_v1.jsonl`
- expanded `scripture_phase_archetypes_v1.jsonl`
- `/api/rmc/lexicon-audit`
- production coverage tests and expanded gold behavior tests

Hard minimums enforced by verifier:

- word lexicon >= 250 entries
- operator phrase lexicon >= 150 entries
- gold references >= 150 examples
- transition law examples >= 75 examples
- syntactic firewall examples >= 50 examples
- scripture archetypes >= 30 examples
- all nine phases have at least 25 word-level examples
- safe and dangerous phrase families are both represented
- duplicate keys fail the audit
- schema failures fail the audit

Boundary:

- read-only
- no writes
- no Chroma
- no DB reads
- no LLM
- no shell execution
- no memory mutation
- no projection
- no approved output

The purpose is to prevent Candidate Generator extraction from building on a shallow or decorative lexicon.
