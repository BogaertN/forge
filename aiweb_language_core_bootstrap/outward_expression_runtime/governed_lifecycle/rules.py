"""Closed Slice 42B outward-expression lifecycle transition law."""

from __future__ import annotations

from dataclasses import dataclass

from .schema import (
    OutwardExpressionLifecycleStage,
    OutwardExpressionLifecycleTransitionKind,
)


@dataclass(frozen=True, slots=True)
class OutwardExpressionLifecycleTransitionRule:
    from_stage: OutwardExpressionLifecycleStage
    to_stage: OutwardExpressionLifecycleStage
    allowed_kinds: tuple[OutwardExpressionLifecycleTransitionKind, ...]
    purpose: str


def _rule(
    from_stage: OutwardExpressionLifecycleStage,
    to_stage: OutwardExpressionLifecycleStage,
    *allowed_kinds: OutwardExpressionLifecycleTransitionKind,
    purpose: str,
) -> OutwardExpressionLifecycleTransitionRule:
    return OutwardExpressionLifecycleTransitionRule(
        from_stage=from_stage,
        to_stage=to_stage,
        allowed_kinds=tuple(allowed_kinds),
        purpose=purpose,
    )


_BASE_STAGES = (
    OutwardExpressionLifecycleStage.SCHEMA_DECLARED,
    OutwardExpressionLifecycleStage.VERSION_BOUND,
    OutwardExpressionLifecycleStage.PREDECESSORS_BOUND,
    OutwardExpressionLifecycleStage.CROSS_RECORD_VALIDATED,
    OutwardExpressionLifecycleStage.RECORD_VALIDATED,
)

OUTWARD_EXPRESSION_LIFECYCLE_TRANSITION_RULES = (
    _rule(
        OutwardExpressionLifecycleStage.SCHEMA_DECLARED,
        OutwardExpressionLifecycleStage.VERSION_BOUND,
        OutwardExpressionLifecycleTransitionKind.BIND_VERSION,
        purpose="bind exact admitted Slice 42A and Slice 42B versions",
    ),
    _rule(
        OutwardExpressionLifecycleStage.VERSION_BOUND,
        OutwardExpressionLifecycleStage.PREDECESSORS_BOUND,
        OutwardExpressionLifecycleTransitionKind.BIND_PREDECESSORS,
        purpose="bind exact selected-meaning and expression-boundary ancestry",
    ),
    _rule(
        OutwardExpressionLifecycleStage.PREDECESSORS_BOUND,
        OutwardExpressionLifecycleStage.CROSS_RECORD_VALIDATED,
        OutwardExpressionLifecycleTransitionKind.VALIDATE_CROSS_RECORDS,
        purpose="validate exact cross-record references without authority admission",
    ),
    _rule(
        OutwardExpressionLifecycleStage.CROSS_RECORD_VALIDATED,
        OutwardExpressionLifecycleStage.RECORD_VALIDATED,
        OutwardExpressionLifecycleTransitionKind.VALIDATE_RECORD,
        purpose="validate canonical identities and fail-closed constraints",
    ),
    _rule(
        OutwardExpressionLifecycleStage.RECORD_VALIDATED,
        OutwardExpressionLifecycleStage.RECORD_SEALED,
        OutwardExpressionLifecycleTransitionKind.SEAL_RECORD,
        purpose="seal immutable validation custody without authorizing expression",
    ),
    *tuple(
        _rule(
            stage,
            OutwardExpressionLifecycleStage.VALIDATION_INCOMPLETE,
            OutwardExpressionLifecycleTransitionKind.MARK_INCOMPLETE,
            purpose="preserve incomplete validation without semantic consequence",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            OutwardExpressionLifecycleStage.UNKNOWN_VERSION_BLOCKED,
            OutwardExpressionLifecycleTransitionKind.BLOCK_UNKNOWN_VERSION,
            purpose="fail closed on unknown schema, spec, or profile version",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            OutwardExpressionLifecycleStage.MALFORMED_RECORD_BLOCKED,
            OutwardExpressionLifecycleTransitionKind.BLOCK_MALFORMED_RECORD,
            purpose="fail closed on malformed immutable record content",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            OutwardExpressionLifecycleStage.PREDECESSOR_INVALID_BLOCKED,
            OutwardExpressionLifecycleTransitionKind.BLOCK_INVALID_PREDECESSOR,
            purpose="fail closed on missing or inconsistent predecessor custody",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            OutwardExpressionLifecycleStage.DUPLICATE_RECORD_BLOCKED,
            OutwardExpressionLifecycleTransitionKind.BLOCK_DUPLICATE_RECORD,
            purpose="fail closed on duplicate deterministic record identity",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            OutwardExpressionLifecycleStage.IDENTITY_COLLISION_BLOCKED,
            OutwardExpressionLifecycleTransitionKind.BLOCK_IDENTITY_COLLISION,
            purpose="fail closed on same identity with different canonical bytes",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            blocked,
            OutwardExpressionLifecycleStage.SCHEMA_DECLARED,
            OutwardExpressionLifecycleTransitionKind.RESUME_VALIDATION,
            purpose="begin an explicit immutable successor validation chain",
        )
        for blocked in (
            OutwardExpressionLifecycleStage.VALIDATION_INCOMPLETE,
            OutwardExpressionLifecycleStage.UNKNOWN_VERSION_BLOCKED,
            OutwardExpressionLifecycleStage.MALFORMED_RECORD_BLOCKED,
            OutwardExpressionLifecycleStage.PREDECESSOR_INVALID_BLOCKED,
            OutwardExpressionLifecycleStage.DUPLICATE_RECORD_BLOCKED,
            OutwardExpressionLifecycleStage.IDENTITY_COLLISION_BLOCKED,
        )
    ),
)


def lifecycle_transition_rule(
    from_stage: OutwardExpressionLifecycleStage,
    to_stage: OutwardExpressionLifecycleStage,
) -> OutwardExpressionLifecycleTransitionRule | None:
    for rule in OUTWARD_EXPRESSION_LIFECYCLE_TRANSITION_RULES:
        if rule.from_stage is from_stage and rule.to_stage is to_stage:
            return rule
    return None


def lifecycle_transition_allowed(
    from_stage: OutwardExpressionLifecycleStage,
    to_stage: OutwardExpressionLifecycleStage,
    transition_kind: OutwardExpressionLifecycleTransitionKind,
) -> bool:
    rule = lifecycle_transition_rule(from_stage, to_stage)
    return rule is not None and transition_kind in rule.allowed_kinds


__all__ = (
    "OUTWARD_EXPRESSION_LIFECYCLE_TRANSITION_RULES",
    "OutwardExpressionLifecycleTransitionRule",
    "lifecycle_transition_allowed",
    "lifecycle_transition_rule",
)
