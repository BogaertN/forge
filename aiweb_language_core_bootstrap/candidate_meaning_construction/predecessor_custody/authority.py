"""Slice 39C permanent provenance and predecessor-custody boundaries."""

from __future__ import annotations

SLICE39C_REQUIRED_STAGES = (
    "input_event_custody",
    "source_field_projection",
    "operator_candidate_binding",
    "candidate_phase_trails",
    "scope_attachment_reference_constraints",
    "deterministic_structural_derivation",
    "slice37_concept_sense_candidates",
    "slice38_predicate_role_frame_candidates",
)

SLICE39C_PERMANENT_BOUNDARIES = (
    "predecessor custody is not semantic payload construction",
    "predecessor custody is not candidate ranking",
    "predecessor custody is not candidate selection",
    "provenance binding is not gate progression",
    "source ancestry is not truth",
    "registry identity is not evidence validity",
    "role-layout ancestry is not participant assignment",
    "frame ancestry is not selected frame",
    "effect-boundary ancestry is not permission",
    "capability-family reference is not availability",
    "capability-family reference is not route",
    "route reference is not invocation",
    "request ancestry is not authorization",
    "report ancestry is not evidence",
    "generated substitute ancestry is prohibited",
    "cross-lineage candidate merging is prohibited",
    "timestamps and environment state are not semantic identity",
)

SLICE39C_DEFERRED_SCOPE = (
    "candidate semantic payload construction",
    "candidate-set construction",
    "candidate ranking",
    "candidate selection",
    "verbal cognition gates",
    "selected meaning",
    "truth determination",
    "evidence validation",
    "permission",
    "capability availability",
    "route construction",
    "invocation",
    "tool use",
    "action execution",
    "memory access",
    "rendering",
    "delivery",
)

__all__ = (
    "SLICE39C_DEFERRED_SCOPE",
    "SLICE39C_PERMANENT_BOUNDARIES",
    "SLICE39C_REQUIRED_STAGES",
)
