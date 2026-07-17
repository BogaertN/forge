"""Pure Slice 38D participant-role lifecycle law."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .schema import ParticipantRoleLifecycleState as S, ParticipantRoleTransitionKind as K


@dataclass(frozen=True, slots=True)
class ParticipantRoleLifecycleRule:
    from_state: S
    to_state: S
    allowed_kinds: tuple[K, ...]
    human_approval_required: bool
    ancestry_required: bool


ROLE_LIFECYCLE_RULES: Final[tuple[ParticipantRoleLifecycleRule, ...]] = (
    ParticipantRoleLifecycleRule(S.OBSERVED, S.CANDIDATE, (K.PROPOSE,), False, True),
    ParticipantRoleLifecycleRule(S.CANDIDATE, S.ADMITTED, (K.ADMIT,), True, True),
    ParticipantRoleLifecycleRule(S.CANDIDATE, S.ARCHITECTURE_ADMITTED, (K.ARCHITECTURE_ADMIT,), True, True),
    ParticipantRoleLifecycleRule(S.ADMITTED, S.ARCHITECTURE_ADMITTED, (K.ARCHITECTURE_ADMIT,), True, True),
    ParticipantRoleLifecycleRule(S.ARCHITECTURE_ADMITTED, S.OPERATIONALLY_BOUNDED, (K.BOUND,), True, True),
    ParticipantRoleLifecycleRule(S.ARCHITECTURE_ADMITTED, S.IMPLEMENTATION_DEFERRED, (K.DEFER,), True, True),
    ParticipantRoleLifecycleRule(S.CANDIDATE, S.UNKNOWN, (K.MARK_UNKNOWN,), False, True),
    ParticipantRoleLifecycleRule(S.CANDIDATE, S.UNRESOLVED, (K.MARK_UNRESOLVED,), False, True),
    ParticipantRoleLifecycleRule(S.CANDIDATE, S.AMBIGUOUS, (K.MARK_AMBIGUOUS,), False, True),
    ParticipantRoleLifecycleRule(S.CANDIDATE, S.UNSUPPORTED, (K.MARK_UNSUPPORTED,), False, True),
    ParticipantRoleLifecycleRule(S.CANDIDATE, S.CONFLICTED, (K.MARK_CONFLICTED,), False, True),
    ParticipantRoleLifecycleRule(S.CANDIDATE, S.QUARANTINED, (K.QUARANTINE,), True, True),
    ParticipantRoleLifecycleRule(S.CANDIDATE, S.REJECTED, (K.REJECT,), True, True),
    ParticipantRoleLifecycleRule(S.ARCHITECTURE_ADMITTED, S.REVIEW_REQUIRED, (K.REQUIRE_REVIEW,), False, True),
    ParticipantRoleLifecycleRule(S.ARCHITECTURE_ADMITTED, S.CONFLICTED, (K.MARK_CONFLICTED,), False, True),
    ParticipantRoleLifecycleRule(S.CONFLICTED, S.REVIEW_REQUIRED, (K.REQUIRE_REVIEW,), False, True),
    ParticipantRoleLifecycleRule(S.REVIEW_REQUIRED, S.ARCHITECTURE_ADMITTED, (K.CORRECT, K.RESOLVE_CONFLICT), True, True),
    ParticipantRoleLifecycleRule(S.ARCHITECTURE_ADMITTED, S.DEPRECATED, (K.DEPRECATE,), True, True),
    ParticipantRoleLifecycleRule(S.ARCHITECTURE_ADMITTED, S.SUPERSEDED, (K.SUPERSEDE,), True, True),
    ParticipantRoleLifecycleRule(S.ARCHITECTURE_ADMITTED, S.REJECTED, (K.REJECT,), True, True),
)


def transition_rule(from_state: object, to_state: object) -> ParticipantRoleLifecycleRule | None:
    if type(from_state) is not S or type(to_state) is not S:
        return None
    for rule in ROLE_LIFECYCLE_RULES:
        if rule.from_state is from_state and rule.to_state is to_state:
            return rule
    return None


def transition_allowed(from_state: object, to_state: object, kind: object) -> bool:
    rule = transition_rule(from_state, to_state)
    return rule is not None and type(kind) is K and kind in rule.allowed_kinds
