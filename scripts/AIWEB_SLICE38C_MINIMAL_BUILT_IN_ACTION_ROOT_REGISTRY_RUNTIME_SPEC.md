# AI.Web Slice 38C Runtime Specification

**Slice:** 38C — Minimal Built-In Action-Root Registry
**Accepted parent HEAD:** `c502b74ada70ed0bc551fb591c49fd119191f52f`
**Accepted parent tree:** `77d349f51a617eab98d1fddeef7ba9e57f52dec6`
**Source-authority packet SHA-256:** `1e9d44dfbe256f2438baa24357b65741462b294b0ef120021a0cd73e8a59ee3e`

## Installed boundary

Slice 38C installs one immutable in-memory namespace, five admitted action-root identities, five one-to-one admitted predicate identities, complete Slice 38B lifecycle histories, and a closed read-only registry manifest.

The exact admitted action-root keys are:

1. `inspect`
2. `report`
3. `request`
4. `verify`
5. `simulate`

These roots were selected as the smallest set that proves materially different Document 5 boundaries:

- read-only examination is not modification;
- reporting is not observation, evidence, or proof;
- requesting is not permission or execution;
- verification meaning is not verified status or proof;
- simulation is not live execution.

## Explicitly deferred candidates

`approve`, `install`, `send`, `remember`, and `rollback` remain outside the registry. Their consequence boundaries depend on participant roles, frames, effect classifications, and capability-reference law deferred to Slices 38D through 38F.

## Permitted operations

The registry permits only exact stable-ID retrieval, exact internal namespace-and-key retrieval, exact action-root-to-predicate linkage, deterministic inspection, and validation.

## Prohibited operations

The registry performs no surface lookup, normalization, aliasing, fuzzy matching, nearest-root substitution, semantic similarity, LLM inference, occurrence interpretation, predicate selection, role assignment, frame completion, effect satisfaction, capability routing, invocation, execution, evidence validation, memory access, rendering, delivery, external-resource loading, or release.

## Authority law

Registry population is authorized only by the Slice 38C manifest. The embedded Slice 38B governance batch keeps its population, lookup, selection, routing, and runtime flags false. Admission history is not runtime authority.
