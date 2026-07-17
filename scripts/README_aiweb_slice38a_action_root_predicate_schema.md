# Slice 38A — Action-Root and Predicate-Identity Core Schema

This additive package establishes the schema-only beginning of the RMC
Predicate–Role Frame Registry v1.

## What it contains

- exact authority profile;
- zero-population schema contract;
- provenance reference shape;
- predicate namespace shape;
- action-root identity shape;
- predicate identity shape;
- deterministic canonical IDs;
- fail-closed structural validation.

## What it does not contain

It contains no admitted action roots, predicate lookup, predicate selection,
role assignments, predicate frames, capability routes, tool calls, actions,
memory access, evidence decisions, CandidateMeaning, selected meaning,
rendering, delivery, or production route.

## Architectural line

`surface verb ≠ action root ≠ predicate identity ≠ predicate frame ≠ action`

The package is standard-library only, immutable, deterministic, disabled by
default and safe to inspect without creating runtime authority.

Registry scale is not capability, and scale is not authority.

## Verification modes

- `source-only`: package and boundary inspection with the direct inherited subset.
- `applied`: exact untracked application state plus the complete inherited suite.
- `precommit`: exact staged additions plus the complete inherited suite.
- `committed`: exact committed state plus the complete inherited suite.

Only results produced on the live `/home/nic/forge` repository are authoritative.
