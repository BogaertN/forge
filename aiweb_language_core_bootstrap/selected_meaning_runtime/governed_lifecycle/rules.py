"""Closed Slice 41B selected-meaning lifecycle transition law."""

from __future__ import annotations

from dataclasses import dataclass

from .schema import (
    SelectedMeaningLifecycleStage,
    SelectedMeaningLifecycleTransitionKind,
)


@dataclass(frozen=True, slots=True)
class SelectedMeaningLifecycleTransitionRule:
    from_stage: SelectedMeaningLifecycleStage
    to_stage: SelectedMeaningLifecycleStage
    allowed_kinds: tuple[SelectedMeaningLifecycleTransitionKind, ...]
    purpose: str


def _rule(
    from_stage: SelectedMeaningLifecycleStage,
    to_stage: SelectedMeaningLifecycleStage,
    *allowed_kinds: SelectedMeaningLifecycleTransitionKind,
    purpose: str,
) -> SelectedMeaningLifecycleTransitionRule:
    return SelectedMeaningLifecycleTransitionRule(
        from_stage=from_stage,
        to_stage=to_stage,
        allowed_kinds=tuple(allowed_kinds),
        purpose=purpose,
    )


_BASE_STAGES = (
    SelectedMeaningLifecycleStage.SCHEMA_DECLARED,
    SelectedMeaningLifecycleStage.VERSION_BOUND,
    SelectedMeaningLifecycleStage.PREDECESSORS_BOUND,
    SelectedMeaningLifecycleStage.CROSS_RECORD_VALIDATED,
    SelectedMeaningLifecycleStage.RECORD_VALIDATED,
)

SELECTED_MEANING_LIFECYCLE_TRANSITION_RULES = (
    _rule(
        SelectedMeaningLifecycleStage.SCHEMA_DECLARED,
        SelectedMeaningLifecycleStage.VERSION_BOUND,
        SelectedMeaningLifecycleTransitionKind.BIND_VERSION,
        purpose="bind exact admitted Slice 41A and Slice 41B versions",
    ),
    _rule(
        SelectedMeaningLifecycleStage.VERSION_BOUND,
        SelectedMeaningLifecycleStage.PREDECESSORS_BOUND,
        SelectedMeaningLifecycleTransitionKind.BIND_PREDECESSORS,
        purpose="bind exact immutable candidate, gate, and manifest ancestry",
    ),
    _rule(
        SelectedMeaningLifecycleStage.PREDECESSORS_BOUND,
        SelectedMeaningLifecycleStage.CROSS_RECORD_VALIDATED,
        SelectedMeaningLifecycleTransitionKind.VALIDATE_CROSS_RECORDS,
        purpose="validate exact cross-record references without eligibility evaluation",
    ),
    _rule(
        SelectedMeaningLifecycleStage.CROSS_RECORD_VALIDATED,
        SelectedMeaningLifecycleStage.RECORD_VALIDATED,
        SelectedMeaningLifecycleTransitionKind.VALIDATE_RECORD,
        purpose="validate canonical identities and fail-closed record constraints",
    ),
    _rule(
        SelectedMeaningLifecycleStage.RECORD_VALIDATED,
        SelectedMeaningLifecycleStage.RECORD_SEALED,
        SelectedMeaningLifecycleTransitionKind.SEAL_RECORD,
        purpose="seal immutable validation custody without selecting meaning",
    ),
    *tuple(
        _rule(
            stage,
            SelectedMeaningLifecycleStage.VALIDATION_INCOMPLETE,
            SelectedMeaningLifecycleTransitionKind.MARK_INCOMPLETE,
            purpose="preserve incomplete validation without semantic consequence",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            SelectedMeaningLifecycleStage.UNKNOWN_VERSION_BLOCKED,
            SelectedMeaningLifecycleTransitionKind.BLOCK_UNKNOWN_VERSION,
            purpose="fail closed on an unknown schema or specification version",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            SelectedMeaningLifecycleStage.MALFORMED_RECORD_BLOCKED,
            SelectedMeaningLifecycleTransitionKind.BLOCK_MALFORMED_RECORD,
            purpose="fail closed on malformed immutable record content",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            SelectedMeaningLifecycleStage.PREDECESSOR_INVALID_BLOCKED,
            SelectedMeaningLifecycleTransitionKind.BLOCK_INVALID_PREDECESSOR,
            purpose="fail closed on missing or inconsistent predecessor custody",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            stage,
            SelectedMeaningLifecycleStage.IDENTITY_COLLISION_BLOCKED,
            SelectedMeaningLifecycleTransitionKind.BLOCK_IDENTITY_COLLISION,
            purpose="fail closed on duplicate or colliding deterministic identity",
        )
        for stage in _BASE_STAGES
    ),
    *tuple(
        _rule(
            blocked,
            SelectedMeaningLifecycleStage.SCHEMA_DECLARED,
            SelectedMeaningLifecycleTransitionKind.RESUME_VALIDATION,
            purpose="begin a new immutable successor validation chain",
        )
        for blocked in (
            SelectedMeaningLifecycleStage.VALIDATION_INCOMPLETE,
            SelectedMeaningLifecycleStage.UNKNOWN_VERSION_BLOCKED,
            SelectedMeaningLifecycleStage.MALFORMED_RECORD_BLOCKED,
            SelectedMeaningLifecycleStage.PREDECESSOR_INVALID_BLOCKED,
            SelectedMeaningLifecycleStage.IDENTITY_COLLISION_BLOCKED,
        )
    ),
)


def lifecycle_transition_rule(
    from_stage: SelectedMeaningLifecycleStage,
    to_stage: SelectedMeaningLifecycleStage,
) -> SelectedMeaningLifecycleTransitionRule | None:
    for rule in SELECTED_MEANING_LIFECYCLE_TRANSITION_RULES:
        if rule.from_stage is from_stage and rule.to_stage is to_stage:
            return rule
    return None


def lifecycle_transition_allowed(
    from_stage: SelectedMeaningLifecycleStage,
    to_stage: SelectedMeaningLifecycleStage,
    transition_kind: SelectedMeaningLifecycleTransitionKind,
) -> bool:
    rule = lifecycle_transition_rule(from_stage, to_stage)
    return rule is not None and transition_kind in rule.allowed_kinds


__all__ = (
    "SELECTED_MEANING_LIFECYCLE_TRANSITION_RULES",
    "SelectedMeaningLifecycleTransitionRule",
    "lifecycle_transition_allowed",
    "lifecycle_transition_rule",
)
