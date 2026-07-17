"""Closed Slice 38E predicate-frame lifecycle transition law."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .schema import PredicateFrameLifecycleState as S, PredicateFrameTransitionKind as K


@dataclass(frozen=True, slots=True)
class PredicateFrameLifecycleRule:
    from_state: S
    to_state: S
    transition_kind: K
    human_approval_required: bool
    prior_record_preservation_required: bool
    automatic_transition_allowed: bool


ROLE_LIFECYCLE_RULES: Final[tuple[PredicateFrameLifecycleRule, ...]] = (
    PredicateFrameLifecycleRule(S.OBSERVED, S.CANDIDATE, K.PROPOSE, True, True, False),
    PredicateFrameLifecycleRule(S.CANDIDATE, S.ARCHITECTURE_ADMITTED, K.ARCHITECTURE_ADMIT, True, True, False),
    PredicateFrameLifecycleRule(S.ARCHITECTURE_ADMITTED, S.ADMITTED, K.ADMIT, True, True, False),
    PredicateFrameLifecycleRule(S.ADMITTED, S.OPERATIONALLY_BOUNDED, K.BOUND, True, True, False),
    PredicateFrameLifecycleRule(S.CANDIDATE, S.IMPLEMENTATION_DEFERRED, K.DEFER, True, True, False),
    PredicateFrameLifecycleRule(S.ARCHITECTURE_ADMITTED, S.IMPLEMENTATION_DEFERRED, K.DEFER, True, True, False),
    PredicateFrameLifecycleRule(S.CANDIDATE, S.UNKNOWN, K.MARK_UNKNOWN, True, True, False),
    PredicateFrameLifecycleRule(S.CANDIDATE, S.UNRESOLVED, K.MARK_UNRESOLVED, True, True, False),
    PredicateFrameLifecycleRule(S.CANDIDATE, S.STRUCTURALLY_INCOMPLETE, K.MARK_INCOMPLETE, True, True, False),
    PredicateFrameLifecycleRule(S.CANDIDATE, S.AMBIGUOUS, K.MARK_AMBIGUOUS, True, True, False),
    PredicateFrameLifecycleRule(S.CANDIDATE, S.UNSUPPORTED, K.MARK_UNSUPPORTED, True, True, False),
    PredicateFrameLifecycleRule(S.CANDIDATE, S.CONFLICTED, K.MARK_CONFLICTED, True, True, False),
    PredicateFrameLifecycleRule(S.CANDIDATE, S.QUARANTINED, K.QUARANTINE, True, True, False),
    PredicateFrameLifecycleRule(S.ARCHITECTURE_ADMITTED, S.DEPRECATED, K.DEPRECATE, True, True, False),
    PredicateFrameLifecycleRule(S.ADMITTED, S.DEPRECATED, K.DEPRECATE, True, True, False),
    PredicateFrameLifecycleRule(S.DEPRECATED, S.SUPERSEDED, K.SUPERSEDE, True, True, False),
    PredicateFrameLifecycleRule(S.CANDIDATE, S.REJECTED, K.REJECT, True, True, False),
    PredicateFrameLifecycleRule(S.NON_CONFORMING, S.REVIEW_REQUIRED, K.REQUIRE_REVIEW, True, True, False),
    PredicateFrameLifecycleRule(S.DEPRECATED, S.HISTORICAL_ONLY, K.MARK_HISTORICAL, True, True, False),
    PredicateFrameLifecycleRule(S.SUPERSEDED, S.HISTORICAL_ONLY, K.MARK_HISTORICAL, True, True, False),
)


def transition_rule(from_state: object, to_state: object, transition_kind: object) -> PredicateFrameLifecycleRule | None:
    if type(from_state) is not S or type(to_state) is not S or type(transition_kind) is not K:
        return None
    for rule in ROLE_LIFECYCLE_RULES:
        if (
            rule.from_state is from_state
            and rule.to_state is to_state
            and rule.transition_kind is transition_kind
        ):
            return rule
    return None


def transition_allowed(from_state: object, to_state: object, transition_kind: object) -> bool:
    return transition_rule(from_state, to_state, transition_kind) is not None
