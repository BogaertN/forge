# AI.Web Slice 37D — Controlled Sense and Exact Term-Mapping Registry

Slice 37D is an additive, standard-library-only, deterministic package located at:

`aiweb_language_core_bootstrap/controlled_concept_sense_registry/sense_term_mapping_registry`

It contains immutable schema records, authority definitions, deterministic identities, lifecycle-backed static records, validation, a closed registry, and exact lookup functions.

## What it does

- exposes five controlled senses;
- exposes eleven case-sensitive lexical references;
- exposes ten exact mappings;
- preserves one-to-one, one-to-many ambiguous, unmapped, and unsupported conditions;
- exposes four outward-expression eligibility references without rendering authority;
- exposes explicit refusal records for every prohibited expansion method;
- supports exact ID inspection and exact five-field term lookup.

## What it does not do

It does not normalize text, repair spelling, stem, expand synonyms, find nearest matches, rank by frequency, calculate semantic similarity, load embeddings, call models, consult dictionaries, interpret source occurrences, select senses, consume Slice 36 structures, create CandidateMeaning, create semantic classes or graph edges, route tools, access memory, execute actions, render language, deliver output, access networks, or load external resources.

## Local verification

Run with Python bytecode disabled:

```text
/usr/bin/python3 -B scripts/test_aiweb_slice37d_controlled_sense_exact_term_mapping_registry.py
/usr/bin/python3 -B scripts/aiweb_slice37d_controlled_sense_exact_term_mapping_registry_verify.py /home/nic/forge --mode precommit
```

The verifier also supports `source_only` for disposable packet-derived trees and `committed` after a separately authorized commit.

## Required commit subject

`Slice 37D controlled sense and exact term mapping registry`
