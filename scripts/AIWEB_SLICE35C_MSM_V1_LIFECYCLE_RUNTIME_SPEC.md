# AI.Web Slice 35C - MeaningStructureManifest v1 Lifecycle Runtime Specification

**Specification ID:** `aiweb-msm-v1-lifecycle-transition-law`  
**Specification version:** `aiweb-msm-v1-lifecycle-v1`  
**Build increment:** Slice 35C  
**Runtime scope:** deterministic in-memory lifecycle transition evaluation and immutable successor construction only  
**Decision Owner:** Nicholas Jacob Bogaert / AI.Web  
**Decision status:** adopted for Slice 35C implementation after the Decision Owner directed the build to create the missing runtime specification rather than wait for a pre-existing one.

## 1. Source authority

This specification operationalizes, without expanding, the following architecture:

1. **MeaningStructureManifest v1, Document 2 of 10**
   - Part VI, Sections 30-34: lineage, required lifecycle stages, explicit transition discipline, immutability and ancestry preservation.
   - Sections 21-24: candidate plurality, non-selection, selected governed meaning, outward meaning and later expression/validation/delivery links.
   - Sections 35-47: preservation of negation, uncertainty, modality, evidence, permission, privacy, refusal, ambiguity, memory and non-LLM provenance.
2. **RMC Verbal Cognition Gate Engine v1, Document 6 of 10**
   - candidate existence does not authorize progression;
   - candidate evaluation may produce selection, ambiguity, clarification requirement, unsupported status, refusal relevance or understood-but-blocked status;
   - missing deterministic support remains missing support;
   - selected meaning is not action authority.
3. **Canonical Production Roadmap v1.0**
   - Slice 35C is limited to exact lifecycle states, permitted and prohibited transitions, ancestry preservation and immutable successor creation;
   - persistence, serialization, migration, bootstrap integration, memory, routes, APIs, UI and later language-kernel work remain excluded.

## 2. Binding runtime interpretation

Document 2 binds semantic distinctions but intentionally leaves the final transition algorithm to later implementation. Slice 35C supplies that missing algorithm under the following rules:

- The lifecycle is an **append-only semantic lineage**, not a mutable status variable.
- A direct transition is legal only if it appears in the closed allowlist in `lifecycle.py`.
- A transition does not perform the underlying gate, validation, rendering, delivery, action or evidence operation. It only records that an external authority record supports a semantic successor.
- Every authority-sensitive transition must name an existing `ExternalAuthorityReferenceRecord` already held by the manifest.
- The successor must carry the same authority reference or receipt where its record shape provides an authority field.
- The successor must prove direct ancestry through its own reference fields.
- A skipped stage is prohibited even if the final state would be convenient.
- Unsupported, ambiguous, refused and blocked outcomes remain visible and may be expressed outward only through a separately governed outward-meaning record.

## 3. Direct transition matrix

### 3.1 Lineage opening

- `lineage_origin -> candidate_meaning`
  - inward, source-bound lineage only;
  - no external authority record is required merely to preserve a candidate;
  - transition kind: `ancestry`.
- `lineage_origin -> unresolved`
  - source-bound lineage where no lawful candidate can yet be selected;
  - external authority required;
  - transition kind: `ancestry`.
- `lineage_origin -> clarification_required`
  - source-bound lineage with a material source-level clarification need;
  - external authority required;
  - transition kind: `ancestry`.
- `lineage_origin -> unsupported`
  - source-bound lineage with no admitted interpretation support;
  - external authority required;
  - transition kind: `ancestry`.
- `lineage_origin -> governed_outward_meaning`
  - outward-purpose lineage only;
  - external outward authority required;
  - transition kind: `ancestry`.

### 3.2 Candidate evaluation

- `candidate_meaning -> unresolved` using `ancestry`.
- `candidate_meaning -> clarification_required` using `ancestry`.
- `candidate_meaning -> refused` using `rejection`.
- `candidate_meaning -> unsupported` using `rejection`.
- `candidate_meaning -> authority_blocked` using `ancestry`.
- `candidate_meaning -> selected_governed_meaning` using `ancestry`.

All candidate-evaluation outcomes require an external gate-authority reference. The outcome or selected record must identify the candidate from which it derives.

### 3.3 Lawful re-entry

- `unresolved -> candidate_meaning` using `ancestry` or `narrowing`.
- `clarification_required -> candidate_meaning` using `narrowing`.
- `unsupported -> candidate_meaning` using `ancestry` or `narrowing`.
- `refused -> candidate_meaning` using `narrowing` only.
- `authority_blocked -> selected_governed_meaning` using `ancestry` only.

Re-entry requires new deterministic authority. The earlier outcome remains in the lineage and is not rewritten.

### 3.4 Outward meaning from governed semantic outcomes

- `unresolved -> governed_outward_meaning`
- `clarification_required -> governed_outward_meaning`
- `refused -> governed_outward_meaning`
- `unsupported -> governed_outward_meaning`
- `authority_blocked -> governed_outward_meaning`
- `selected_governed_meaning -> governed_outward_meaning`
- `governed_result_referenced -> governed_outward_meaning`

Each uses `ancestry`, requires an external authority record and requires the outward record to cite the source outcome or selected/result basis.

### 3.5 Governed result and expression chain

- `selected_governed_meaning -> refused` using `rejection` when meaning is understood but the requested consequence is prohibited.
- `selected_governed_meaning -> authority_blocked` using `ancestry` when meaning is selected but external permission remains absent.
- `selected_governed_meaning -> governed_result_referenced` using `ancestry`.
- `governed_outward_meaning -> expression_linked` using `ancestry`.
- `expression_linked -> validation_linked` using `ancestry`.
- `expression_linked -> containment_linked` using `containment`.
- `validation_linked -> delivery_linked` using `ancestry`.
- `validation_linked -> containment_linked` using `containment`.

Every transition requires a separate external authority record or receipt. A render does not become validation, and validation does not become delivery by implication.

## 4. Correction and supersession

Document 2 requires a corrected or superseded semantic state while also prohibiting overwrite of the prior state. The existing MSM-v1 schema has no standalone `CorrectedRecord` or `SupersededRecord`. Slice 35C therefore adopts the following precise representation:

- `SemanticLifecycleState.CORRECTED` and `SemanticLifecycleState.SUPERSEDED` remain reserved semantic distinctions and are **not direct target records**.
- A correction is represented by `transition_kind=correction` from an existing record to a new record of the **same concrete record type and same concrete lifecycle state**.
- A supersession is represented by `transition_kind=supersession` under the same same-kind/same-state rule.
- The predecessor remains unchanged.
- The successor receives a new record identifier.
- The trace names the authority and the reason.
- Correction and supersession cannot be used to skip lifecycle stages or escalate authority.

This makes “corrected” and “superseded” inspectable historical dispositions while preserving the actual state carried by the successor.

## 5. Explicitly prohibited transitions

The closed allowlist rejects every unlisted pair. Important examples include:

- `candidate_meaning -> expression_linked`
- `candidate_meaning -> delivery_linked`
- `candidate_meaning -> governed_result_referenced`
- `selected_governed_meaning -> expression_linked`
- `selected_governed_meaning -> delivery_linked`
- `governed_result_referenced -> expression_linked`
- `governed_outward_meaning -> validation_linked`
- `expression_linked -> delivery_linked`
- `delivery_linked -> any later operational state`
- `containment_linked -> delivery_linked`
- any direct target of `corrected` or `superseded` as a synthetic state-only record.

## 6. Immutable successor operation

`append_lifecycle_successor(...)` performs one bounded operation:

1. Validate the existing manifest under Slice 35B.
2. Validate the proposed successor intrinsically.
3. Resolve the predecessor and authority records.
4. Evaluate the direct transition under this specification.
5. Append the successor to its typed manifest collection.
6. Append one `SemanticTransitionTraceRecord`.
7. Validate the resulting manifest under Slice 35B.
8. Return a new frozen manifest, the trace and the deterministic decision.

The function performs no filesystem access, serialization, persistence, network access, model inference, tool invocation, memory operation, rendering, validation, delivery or action.

## 7. Slice boundary

Slice 35C does not implement:

- a parser or candidate generator;
- Document 6 gate evaluation itself;
- evidence or truth determination;
- capability or action authorization;
- serialization or deserialization;
- persistence or database mutation;
- migration or version conversion;
- bootstrap connection;
- memory, resources, routes, APIs or UI;
- controlled expression or RMC Echo runtime.

Those remain separate later increments.
