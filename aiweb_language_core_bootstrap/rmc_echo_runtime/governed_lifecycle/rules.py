"""Closed explicit Slice 43B lifecycle transition law."""

from __future__ import annotations

from dataclasses import dataclass

from .schema import (
    RmcEchoLifecycleStage,
    RmcEchoLifecycleTransitionKind,
)


@dataclass(frozen=True, slots=True)
class RmcEchoLifecycleTransitionRule:
    from_stage: RmcEchoLifecycleStage
    to_stage: RmcEchoLifecycleStage
    allowed_kinds: tuple[RmcEchoLifecycleTransitionKind, ...]
    automatic_transition_allowed: bool
    purpose: str


def _rule(
    from_stage: RmcEchoLifecycleStage,
    to_stage: RmcEchoLifecycleStage,
    transition_kind: RmcEchoLifecycleTransitionKind,
    *,
    purpose: str,
) -> RmcEchoLifecycleTransitionRule:
    return RmcEchoLifecycleTransitionRule(
        from_stage=from_stage,
        to_stage=to_stage,
        allowed_kinds=(transition_kind,),
        automatic_transition_allowed=False,
        purpose=purpose,
    )


_BASE_STAGES = (
    RmcEchoLifecycleStage.SCHEMA_DECLARED,
    RmcEchoLifecycleStage.VERSION_BOUND,
    RmcEchoLifecycleStage.PREDECESSORS_BOUND,
    RmcEchoLifecycleStage.CROSS_RECORD_VALIDATED,
    RmcEchoLifecycleStage.RECORD_VALIDATED,
)

RMC_ECHO_LIFECYCLE_TRANSITION_RULES = (
    _rule(
        RmcEchoLifecycleStage.SCHEMA_DECLARED,
        RmcEchoLifecycleStage.VERSION_BOUND,
        RmcEchoLifecycleTransitionKind.BIND_VERSION,
        purpose="bind supported Slice 43A schema and Slice 43B profile versions",
    ),
    _rule(
        RmcEchoLifecycleStage.VERSION_BOUND,
        RmcEchoLifecycleStage.PREDECESSORS_BOUND,
        RmcEchoLifecycleTransitionKind.BIND_PREDECESSORS,
        purpose="bind exact immutable predecessor references",
    ),
    _rule(
        RmcEchoLifecycleStage.PREDECESSORS_BOUND,
        RmcEchoLifecycleStage.CROSS_RECORD_VALIDATED,
        RmcEchoLifecycleTransitionKind.VALIDATE_CROSS_RECORDS,
        purpose="validate exact internal RMC Echo custody references",
    ),
    _rule(
        RmcEchoLifecycleStage.CROSS_RECORD_VALIDATED,
        RmcEchoLifecycleStage.RECORD_VALIDATED,
        RmcEchoLifecycleTransitionKind.VALIDATE_RECORD,
        purpose="validate canonical structure and deterministic identities",
    ),
    _rule(
        RmcEchoLifecycleStage.RECORD_VALIDATED,
        RmcEchoLifecycleStage.RECORD_SEALED,
        RmcEchoLifecycleTransitionKind.SEAL_RECORD,
        purpose="seal an immutable validation-only successor",
    ),
    *tuple(
        _rule(
            stage,
            RmcEchoLifecycleStage.VALIDATION_INCOMPLETE,
            RmcEchoLifecycleTransitionKind.MARK_INCOMPLETE,
            purpose="preserve incomplete validation without inferred success",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            RmcEchoLifecycleStage.UNKNOWN_VERSION_BLOCKED,
            RmcEchoLifecycleTransitionKind.BLOCK_UNKNOWN_VERSION,
            purpose="fail closed on unsupported schema or profile version",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            RmcEchoLifecycleStage.MALFORMED_RECORD_BLOCKED,
            RmcEchoLifecycleTransitionKind.BLOCK_MALFORMED_RECORD,
            purpose="fail closed on malformed record structure",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            RmcEchoLifecycleStage.PREDECESSOR_INVALID_BLOCKED,
            RmcEchoLifecycleTransitionKind.BLOCK_INVALID_PREDECESSOR,
            purpose="fail closed on missing or inconsistent predecessor custody",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            RmcEchoLifecycleStage.DUPLICATE_RECORD_BLOCKED,
            RmcEchoLifecycleTransitionKind.BLOCK_DUPLICATE_RECORD,
            purpose="fail closed on duplicate deterministic record identity",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            RmcEchoLifecycleStage.IDENTITY_COLLISION_BLOCKED,
            RmcEchoLifecycleTransitionKind.BLOCK_IDENTITY_COLLISION,
            purpose="fail closed on same identity with different canonical bytes",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            blocked,
            RmcEchoLifecycleStage.SCHEMA_DECLARED,
            RmcEchoLifecycleTransitionKind.RESUME_VALIDATION,
            purpose="begin an explicit immutable successor validation chain",
        )
        for blocked in (
            RmcEchoLifecycleStage.VALIDATION_INCOMPLETE,
            RmcEchoLifecycleStage.UNKNOWN_VERSION_BLOCKED,
            RmcEchoLifecycleStage.MALFORMED_RECORD_BLOCKED,
            RmcEchoLifecycleStage.PREDECESSOR_INVALID_BLOCKED,
            RmcEchoLifecycleStage.DUPLICATE_RECORD_BLOCKED,
            RmcEchoLifecycleStage.IDENTITY_COLLISION_BLOCKED,
        )
    ),
)


def lifecycle_transition_rule(
    from_stage: RmcEchoLifecycleStage,
    to_stage: RmcEchoLifecycleStage,
) -> RmcEchoLifecycleTransitionRule | None:
    for rule in RMC_ECHO_LIFECYCLE_TRANSITION_RULES:
        if rule.from_stage is from_stage and rule.to_stage is to_stage:
            return rule
    return None


def lifecycle_transition_allowed(
    from_stage: RmcEchoLifecycleStage,
    to_stage: RmcEchoLifecycleStage,
    transition_kind: RmcEchoLifecycleTransitionKind,
) -> bool:
    rule = lifecycle_transition_rule(from_stage, to_stage)
    return rule is not None and transition_kind in rule.allowed_kinds


__all__ = (
    "RMC_ECHO_LIFECYCLE_TRANSITION_RULES",
    "RmcEchoLifecycleTransitionRule",
    "lifecycle_transition_allowed",
    "lifecycle_transition_rule",
)
