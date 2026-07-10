# AI.Web Slice 17 Output / Expression Boundary Scaffold

Slice 17 is an additive, boundary-only scaffold. It represents how an already
selected meaning may become a deterministic, human-readable **unapproved preview**
without granting any new authority.

## Hard laws

- Readable output is not proof.
- Fluent output is not authority.
- A good answer is not acceptance.
- Expression is not truth, permission, delivery, or execution.
- Rendering does not create or alter meaning.
- Negation, conditions, modality, attribution, scope, refusal relevance, and
  uncertainty must remain explicit.
- Structural validity and fidelity do not approve output.

## Records

The scaffold defines:

1. `ExpressionSourceRecord`
2. `ExpressionPreservationContractRecord`
3. `ExpressionPlanRecord`
4. `ExpressionPreviewRecord`
5. `ExpressionFidelityRecord`
6. `ExpressionReceiptRecord`

The source record binds exact supplied selected-meaning and upstream snapshots.
The preservation contract makes all seven preservation dimensions explicit. The
plan is finite and deterministic. The preview is always unapproved. The fidelity
record uses mandatory hard gates; no aggregate score can override a failed gate.
The receipt records structure only.

## Status mapping

- `selected_meaning_boundary_recorded` permits explanation, status, or
  clarification previews.
- `selection_held_boundary` permits held, clarification, or uncertainty previews.
- `selection_blocked_boundary` permits blocked or refusal previews.
- `selection_refused_boundary` permits refusal previews only.

A held, blocked, or refused selection cannot become a positive selected claim.

## Explicit exclusions

This scaffold does not modify or call:

- `main.py`
- `rmc_engine_v1/output_renderer.py`
- `rmc_engine_v1/renderer/*`
- GP-014
- GP-015
- frozen `llm_renderer.py`
- frozen `chroma_connector.py`
- configuration, registry, dependency, route, UI, memory, tool, network, model,
  vector, retrieval, RAG, release, or production paths

GP-014 remains protected regression evidence. Any wrapper or supersession decision
belongs to a separately authorized later Slice 18 decision.
