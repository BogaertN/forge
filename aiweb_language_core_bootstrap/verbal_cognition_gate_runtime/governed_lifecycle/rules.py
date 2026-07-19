"""Closed Slice 40B verbal-cognition gate lifecycle transition law."""

from __future__ import annotations

from dataclasses import dataclass

from .schema import GateLifecycleStage, GateLifecycleTransitionKind


@dataclass(frozen=True, slots=True)
class GateLifecycleTransitionRule:
    from_stage: GateLifecycleStage
    to_stage: GateLifecycleStage
    allowed_kinds: tuple[GateLifecycleTransitionKind, ...]
    purpose: str


def _rule(
    from_stage: GateLifecycleStage,
    to_stage: GateLifecycleStage,
    *allowed_kinds: GateLifecycleTransitionKind,
    purpose: str,
) -> GateLifecycleTransitionRule:
    return GateLifecycleTransitionRule(
        from_stage=from_stage,
        to_stage=to_stage,
        allowed_kinds=tuple(allowed_kinds),
        purpose=purpose,
    )


_BASE_STAGES = (
    GateLifecycleStage.SCHEMA_DECLARED,
    GateLifecycleStage.PROFILE_VERSION_BOUND,
    GateLifecycleStage.CANDIDATE_REFERENCE_BOUND,
    GateLifecycleStage.PROVENANCE_VALIDATED,
    GateLifecycleStage.RECORD_VALIDATED,
)

GATE_LIFECYCLE_TRANSITION_RULES = (
    _rule(
        GateLifecycleStage.SCHEMA_DECLARED,
        GateLifecycleStage.PROFILE_VERSION_BOUND,
        GateLifecycleTransitionKind.BIND_PROFILE_VERSION,
        purpose="bind exact approved gate and profile versions",
    ),
    _rule(
        GateLifecycleStage.PROFILE_VERSION_BOUND,
        GateLifecycleStage.CANDIDATE_REFERENCE_BOUND,
        GateLifecycleTransitionKind.BIND_CANDIDATE_REFERENCE,
        purpose="bind the exact immutable candidate reference",
    ),
    _rule(
        GateLifecycleStage.CANDIDATE_REFERENCE_BOUND,
        GateLifecycleStage.PROVENANCE_VALIDATED,
        GateLifecycleTransitionKind.VALIDATE_PROVENANCE,
        purpose="validate exact source, candidate, schema, and authority provenance",
    ),
    _rule(
        GateLifecycleStage.PROVENANCE_VALIDATED,
        GateLifecycleStage.RECORD_VALIDATED,
        GateLifecycleTransitionKind.VALIDATE_RECORD,
        purpose="validate the complete cross-record gate custody bundle",
    ),
    _rule(
        GateLifecycleStage.RECORD_VALIDATED,
        GateLifecycleStage.RECORD_SEALED,
        GateLifecycleTransitionKind.SEAL_RECORD,
        purpose="seal immutable validation custody without evaluating a gate",
    ),
    *tuple(
        _rule(
            stage,
            GateLifecycleStage.VALIDATION_INCOMPLETE,
            GateLifecycleTransitionKind.MARK_INCOMPLETE,
            purpose="preserve incomplete validation without gate disposition",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            GateLifecycleStage.UNKNOWN_VERSION_BLOCKED,
            GateLifecycleTransitionKind.BLOCK_UNKNOWN_VERSION,
            purpose="fail closed on an unknown schema, gate, or profile version",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            GateLifecycleStage.MALFORMED_RECORD_BLOCKED,
            GateLifecycleTransitionKind.BLOCK_MALFORMED_RECORD,
            purpose="fail closed on malformed immutable record content",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            GateLifecycleStage.PROVENANCE_INVALID_BLOCKED,
            GateLifecycleTransitionKind.BLOCK_INVALID_PROVENANCE,
            purpose="fail closed on missing or inconsistent provenance",
        )
        for stage in _BASE_STAGES
    ),
    _rule(
        GateLifecycleStage.VALIDATION_INCOMPLETE,
        GateLifecycleStage.SCHEMA_DECLARED,
        GateLifecycleTransitionKind.RESUME_VALIDATION,
        purpose="begin a new immutable successor validation chain",
    ),
    _rule(
        GateLifecycleStage.UNKNOWN_VERSION_BLOCKED,
        GateLifecycleStage.SCHEMA_DECLARED,
        GateLifecycleTransitionKind.RESUME_VALIDATION,
        purpose="begin a new chain under a separately admitted version",
    ),
    _rule(
        GateLifecycleStage.MALFORMED_RECORD_BLOCKED,
        GateLifecycleStage.SCHEMA_DECLARED,
        GateLifecycleTransitionKind.RESUME_VALIDATION,
        purpose="begin a new chain for a corrected immutable record",
    ),
    _rule(
        GateLifecycleStage.PROVENANCE_INVALID_BLOCKED,
        GateLifecycleStage.SCHEMA_DECLARED,
        GateLifecycleTransitionKind.RESUME_VALIDATION,
        purpose="begin a new chain with corrected provenance custody",
    ),
)


def lifecycle_transition_rule(
    from_stage: GateLifecycleStage,
    to_stage: GateLifecycleStage,
) -> GateLifecycleTransitionRule | None:
    for rule in GATE_LIFECYCLE_TRANSITION_RULES:
        if rule.from_stage is from_stage and rule.to_stage is to_stage:
            return rule
    return None


def lifecycle_transition_allowed(
    from_stage: GateLifecycleStage,
    to_stage: GateLifecycleStage,
    transition_kind: GateLifecycleTransitionKind,
) -> bool:
    rule = lifecycle_transition_rule(from_stage, to_stage)
    return rule is not None and transition_kind in rule.allowed_kinds


__all__ = (
    "GATE_LIFECYCLE_TRANSITION_RULES",
    "GateLifecycleTransitionRule",
    "lifecycle_transition_allowed",
    "lifecycle_transition_rule",
)
