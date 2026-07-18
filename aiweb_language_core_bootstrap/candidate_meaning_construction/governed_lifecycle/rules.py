"""Closed Slice 39B candidate-meaning lifecycle transition law."""

from __future__ import annotations

from dataclasses import dataclass

from .schema import (
    CandidateMeaningLifecycleStage,
    CandidateMeaningLifecycleTransitionKind,
)


@dataclass(frozen=True, slots=True)
class CandidateMeaningLifecycleTransitionRule:
    from_stage: CandidateMeaningLifecycleStage
    to_stage: CandidateMeaningLifecycleStage
    allowed_kinds: tuple[CandidateMeaningLifecycleTransitionKind, ...]
    purpose: str


def _rule(
    from_stage: CandidateMeaningLifecycleStage,
    to_stage: CandidateMeaningLifecycleStage,
    *allowed_kinds: CandidateMeaningLifecycleTransitionKind,
    purpose: str,
) -> CandidateMeaningLifecycleTransitionRule:
    return CandidateMeaningLifecycleTransitionRule(
        from_stage=from_stage,
        to_stage=to_stage,
        allowed_kinds=tuple(allowed_kinds),
        purpose=purpose,
    )


CANDIDATE_MEANING_LIFECYCLE_TRANSITION_RULES = (
    _rule(
        CandidateMeaningLifecycleStage.SCHEMA_DECLARED,
        CandidateMeaningLifecycleStage.PROVENANCE_BOUND,
        CandidateMeaningLifecycleTransitionKind.BIND_PROVENANCE,
        purpose="Bind exact provenance to the declared schema.",
    ),
    _rule(
        CandidateMeaningLifecycleStage.PROVENANCE_BOUND,
        CandidateMeaningLifecycleStage.CONTENT_CONSTRUCTED,
        CandidateMeaningLifecycleTransitionKind.CONSTRUCT_CONTENT,
        purpose="Record deterministic candidate-only content construction.",
    ),
    _rule(
        CandidateMeaningLifecycleStage.CONTENT_CONSTRUCTED,
        CandidateMeaningLifecycleStage.CANDIDATE_SEALED,
        CandidateMeaningLifecycleTransitionKind.SEAL_CANDIDATE,
        purpose="Seal an immutable candidate record set after validation.",
    ),
    _rule(
        CandidateMeaningLifecycleStage.CANDIDATE_SEALED,
        CandidateMeaningLifecycleStage.CANDIDATE_SET_REFERENCED,
        CandidateMeaningLifecycleTransitionKind.REFERENCE_CANDIDATE_SET,
        purpose="Reference the sealed candidate from a later candidate set.",
    ),
    _rule(
        CandidateMeaningLifecycleStage.SCHEMA_DECLARED,
        CandidateMeaningLifecycleStage.CONSTRUCTION_INCOMPLETE,
        CandidateMeaningLifecycleTransitionKind.MARK_INCOMPLETE,
        purpose="Preserve incomplete construction without inventing ancestry.",
    ),
    _rule(
        CandidateMeaningLifecycleStage.PROVENANCE_BOUND,
        CandidateMeaningLifecycleStage.CONSTRUCTION_INCOMPLETE,
        CandidateMeaningLifecycleTransitionKind.MARK_INCOMPLETE,
        purpose="Preserve incomplete construction after provenance binding.",
    ),
    _rule(
        CandidateMeaningLifecycleStage.CONTENT_CONSTRUCTED,
        CandidateMeaningLifecycleStage.CONSTRUCTION_INCOMPLETE,
        CandidateMeaningLifecycleTransitionKind.MARK_INCOMPLETE,
        purpose="Preserve incomplete sealing without gate interpretation.",
    ),
    _rule(
        CandidateMeaningLifecycleStage.SCHEMA_DECLARED,
        CandidateMeaningLifecycleStage.PREDECESSOR_INVALID,
        CandidateMeaningLifecycleTransitionKind.BLOCK_INVALID_PREDECESSOR,
        purpose="Fail closed when a predecessor is invalid.",
    ),
    _rule(
        CandidateMeaningLifecycleStage.PROVENANCE_BOUND,
        CandidateMeaningLifecycleStage.PREDECESSOR_INVALID,
        CandidateMeaningLifecycleTransitionKind.BLOCK_INVALID_PREDECESSOR,
        purpose="Fail closed after provenance exposes an invalid predecessor.",
    ),
    _rule(
        CandidateMeaningLifecycleStage.CONTENT_CONSTRUCTED,
        CandidateMeaningLifecycleStage.PREDECESSOR_INVALID,
        CandidateMeaningLifecycleTransitionKind.BLOCK_INVALID_PREDECESSOR,
        purpose="Block sealing when a predecessor is invalid.",
    ),
    _rule(
        CandidateMeaningLifecycleStage.CONSTRUCTION_INCOMPLETE,
        CandidateMeaningLifecycleStage.PROVENANCE_BOUND,
        CandidateMeaningLifecycleTransitionKind.RESUME_CONSTRUCTION,
        purpose="Resume only from explicit incomplete ancestry.",
    ),
)


_RULE_INDEX = {
    (rule.from_stage, rule.to_stage): rule
    for rule in CANDIDATE_MEANING_LIFECYCLE_TRANSITION_RULES
}


def lifecycle_transition_rule(
    from_stage: CandidateMeaningLifecycleStage,
    to_stage: CandidateMeaningLifecycleStage,
) -> CandidateMeaningLifecycleTransitionRule | None:
    return _RULE_INDEX.get((from_stage, to_stage))


def lifecycle_transition_allowed(
    from_stage: CandidateMeaningLifecycleStage,
    to_stage: CandidateMeaningLifecycleStage,
    kind: CandidateMeaningLifecycleTransitionKind,
) -> bool:
    rule = lifecycle_transition_rule(from_stage, to_stage)
    return rule is not None and kind in rule.allowed_kinds


__all__ = (
    "CANDIDATE_MEANING_LIFECYCLE_TRANSITION_RULES",
    "CandidateMeaningLifecycleTransitionRule",
    "lifecycle_transition_allowed",
    "lifecycle_transition_rule",
)
