"""Explicit Slice 38B predicate-resource lifecycle transition matrix.

Only listed state pairs and transition kinds may pass.  The matrix is
validation law only; it performs no transition and changes no resource.
"""

from __future__ import annotations

from typing import Final

from ..schema import PredicateLifecycleState
from .schema import (
    PredicateLifecycleTransitionKind,
    PredicateLifecycleTransitionRule,
)


def _rule(
    from_state: PredicateLifecycleState,
    to_state: PredicateLifecycleState,
    *allowed_kinds: PredicateLifecycleTransitionKind,
    conflict_review_required: bool = False,
    unknown_review_required: bool = False,
    dependency_review_required: bool = False,
    purpose: str,
) -> PredicateLifecycleTransitionRule:
    return PredicateLifecycleTransitionRule(
        from_state=from_state,
        to_state=to_state,
        allowed_kinds=tuple(allowed_kinds),
        authority_required=True,
        human_approval_required=True,
        conflict_review_required=conflict_review_required,
        unknown_review_required=unknown_review_required,
        dependency_review_required=dependency_review_required,
        purpose=purpose,
    )


PREDICATE_LIFECYCLE_TRANSITION_RULES: Final[
    tuple[PredicateLifecycleTransitionRule, ...]
] = (
    _rule(
        PredicateLifecycleState.OBSERVED,
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleTransitionKind.PROPOSAL,
        purpose="Preserve a source observation as a non-operative proposal candidate.",
    ),
    _rule(
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleTransitionKind.REVIEW,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Record completed bounded review without admitting the resource.",
    ),
    _rule(
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleState.ADMITTED,
        PredicateLifecycleTransitionKind.ADMISSION,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Admit one reviewed resource within exact scope.",
    ),
    _rule(
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleState.ARCHITECTURE_ADMITTED,
        PredicateLifecycleTransitionKind.ARCHITECTURE_ADMISSION,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Admit architecture authority without claiming runtime behavior.",
    ),
    _rule(
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleState.IMPLEMENTATION_DEFERRED,
        PredicateLifecycleTransitionKind.DEFERMENT,
        dependency_review_required=True,
        purpose="Preserve a proposal whose implementation remains deferred.",
    ),
    _rule(
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleState.IMPLEMENTATION_DEFERRED,
        PredicateLifecycleTransitionKind.DEFERMENT,
        dependency_review_required=True,
        purpose="Preserve a reviewed requirement whose implementation remains deferred.",
    ),
    _rule(
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleState.UNKNOWN,
        PredicateLifecycleTransitionKind.MARK_UNKNOWN,
        unknown_review_required=True,
        purpose="Preserve that identity or meaning is not lawfully known.",
    ),
    _rule(
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleState.UNKNOWN,
        PredicateLifecycleTransitionKind.MARK_UNKNOWN,
        unknown_review_required=True,
        purpose="Return reviewed material to explicit unknown state.",
    ),
    _rule(
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleState.UNRESOLVED,
        PredicateLifecycleTransitionKind.MARK_UNRESOLVED,
        unknown_review_required=True,
        purpose="Preserve a known question pending competent authority.",
    ),
    _rule(
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleState.UNRESOLVED,
        PredicateLifecycleTransitionKind.MARK_UNRESOLVED,
        unknown_review_required=True,
        purpose="Preserve an unresolved reviewed question without selection.",
    ),
    _rule(
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleState.AMBIGUOUS,
        PredicateLifecycleTransitionKind.MARK_AMBIGUOUS,
        unknown_review_required=True,
        purpose="Preserve multiple materially supported possibilities.",
    ),
    _rule(
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleState.AMBIGUOUS,
        PredicateLifecycleTransitionKind.MARK_AMBIGUOUS,
        unknown_review_required=True,
        purpose="Preserve reviewed ambiguity without narrowing it.",
    ),
    _rule(
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleState.UNSUPPORTED,
        PredicateLifecycleTransitionKind.MARK_UNSUPPORTED,
        unknown_review_required=True,
        purpose="Preserve missing support without forced substitution.",
    ),
    _rule(
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleState.UNSUPPORTED,
        PredicateLifecycleTransitionKind.MARK_UNSUPPORTED,
        unknown_review_required=True,
        purpose="Record that review found support insufficient.",
    ),
    _rule(
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleState.CONFLICTED,
        PredicateLifecycleTransitionKind.MARK_CONFLICTED,
        conflict_review_required=True,
        purpose="Preserve a material conflict that blocks admission.",
    ),
    _rule(
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleState.CONFLICTED,
        PredicateLifecycleTransitionKind.MARK_CONFLICTED,
        conflict_review_required=True,
        purpose="Preserve conflict discovered during review.",
    ),
    _rule(
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleState.WITHDRAWN,
        PredicateLifecycleTransitionKind.WITHDRAWAL,
        purpose="Withdraw a proposal without erasing its ancestry.",
    ),
    _rule(
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleState.WITHDRAWN,
        PredicateLifecycleTransitionKind.WITHDRAWAL,
        purpose="Withdraw reviewed material before admission.",
    ),
    _rule(
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleTransitionKind.CORRECTION,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Correct reviewed material under a new immutable version.",
    ),
    _rule(
        PredicateLifecycleState.ADMITTED,
        PredicateLifecycleState.ADMITTED,
        PredicateLifecycleTransitionKind.CORRECTION,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Correct admitted material without changing lineage or broadening scope.",
    ),
    _rule(
        PredicateLifecycleState.ARCHITECTURE_ADMITTED,
        PredicateLifecycleState.ARCHITECTURE_ADMITTED,
        PredicateLifecycleTransitionKind.CORRECTION,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Correct architecture-admitted material without runtime claim.",
    ),
    _rule(
        PredicateLifecycleState.ADMITTED,
        PredicateLifecycleState.DEPRECATED,
        PredicateLifecycleTransitionKind.DEPRECATION,
        conflict_review_required=True,
        purpose="Stop new use while preserving admitted ancestry.",
    ),
    _rule(
        PredicateLifecycleState.ARCHITECTURE_ADMITTED,
        PredicateLifecycleState.DEPRECATED,
        PredicateLifecycleTransitionKind.DEPRECATION,
        conflict_review_required=True,
        purpose="Deprecate architecture authority without deleting history.",
    ),
    _rule(
        PredicateLifecycleState.ADMITTED,
        PredicateLifecycleState.SUPERSEDED,
        PredicateLifecycleTransitionKind.SUPERSESSION,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Replace admitted authority with an explicit successor.",
    ),
    _rule(
        PredicateLifecycleState.ARCHITECTURE_ADMITTED,
        PredicateLifecycleState.SUPERSEDED,
        PredicateLifecycleTransitionKind.SUPERSESSION,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Replace architecture authority with an explicit successor.",
    ),
    _rule(
        PredicateLifecycleState.DEPRECATED,
        PredicateLifecycleState.SUPERSEDED,
        PredicateLifecycleTransitionKind.SUPERSESSION,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Identify a successor while preserving deprecated ancestry.",
    ),
    _rule(
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleState.QUARANTINED,
        PredicateLifecycleTransitionKind.QUARANTINE,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Contain a proposal pending authority or safety resolution.",
    ),
    _rule(
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleState.QUARANTINED,
        PredicateLifecycleTransitionKind.QUARANTINE,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Contain reviewed material after a material defect.",
    ),
    _rule(
        PredicateLifecycleState.ADMITTED,
        PredicateLifecycleState.QUARANTINED,
        PredicateLifecycleTransitionKind.QUARANTINE,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Suspend admitted use after a material authority defect.",
    ),
    _rule(
        PredicateLifecycleState.ARCHITECTURE_ADMITTED,
        PredicateLifecycleState.QUARANTINED,
        PredicateLifecycleTransitionKind.QUARANTINE,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Suspend architecture use after a material authority defect.",
    ),
    _rule(
        PredicateLifecycleState.CONFLICTED,
        PredicateLifecycleState.QUARANTINED,
        PredicateLifecycleTransitionKind.QUARANTINE,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Contain an unresolved conflict.",
    ),
    _rule(
        PredicateLifecycleState.UNSUPPORTED,
        PredicateLifecycleState.QUARANTINED,
        PredicateLifecycleTransitionKind.QUARANTINE,
        dependency_review_required=True,
        purpose="Contain unsupported material pending lawful disposition.",
    ),
    _rule(
        PredicateLifecycleState.QUARANTINED,
        PredicateLifecycleState.QUARANTINED,
        PredicateLifecycleTransitionKind.CONTINUE_QUARANTINE,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Continue quarantine while causes remain unresolved.",
    ),
    _rule(
        PredicateLifecycleState.QUARANTINED,
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleTransitionKind.RELEASE_TO_REVIEW,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Release only to reviewed state after quarantine causes resolve.",
    ),
    _rule(
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleState.REJECTED,
        PredicateLifecycleTransitionKind.REJECTION,
        conflict_review_required=True,
        purpose="Reject a proposal within explicit scope.",
    ),
    _rule(
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleState.REJECTED,
        PredicateLifecycleTransitionKind.REJECTION,
        conflict_review_required=True,
        purpose="Reject reviewed material within explicit scope.",
    ),
    _rule(
        PredicateLifecycleState.ADMITTED,
        PredicateLifecycleState.REJECTED,
        PredicateLifecycleTransitionKind.REJECTION,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Invalidate prior admission within explicit scope.",
    ),
    _rule(
        PredicateLifecycleState.ARCHITECTURE_ADMITTED,
        PredicateLifecycleState.REJECTED,
        PredicateLifecycleTransitionKind.REJECTION,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Invalidate prior architecture admission within explicit scope.",
    ),
    _rule(
        PredicateLifecycleState.QUARANTINED,
        PredicateLifecycleState.REJECTED,
        PredicateLifecycleTransitionKind.REJECTION,
        conflict_review_required=True,
        purpose="Reject quarantined material after review.",
    ),
    _rule(
        PredicateLifecycleState.DEPRECATED,
        PredicateLifecycleState.REJECTED,
        PredicateLifecycleTransitionKind.REJECTION,
        conflict_review_required=True,
        purpose="Reject future use while preserving prior lawful history.",
    ),
    _rule(
        PredicateLifecycleState.REJECTED,
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleTransitionKind.REOPEN_REVIEW,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Reopen rejected material only under new explicit authority.",
    ),
    _rule(
        PredicateLifecycleState.WITHDRAWN,
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleTransitionKind.REOPEN_REVIEW,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Reopen withdrawn material only through a new proposal review.",
    ),
    _rule(
        PredicateLifecycleState.UNKNOWN,
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleTransitionKind.NEW_SUPPORT_REVIEW,
        unknown_review_required=True,
        purpose="Review the same unknown lineage after new support appears.",
    ),
    _rule(
        PredicateLifecycleState.UNRESOLVED,
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleTransitionKind.NEW_SUPPORT_REVIEW,
        unknown_review_required=True,
        purpose="Return unresolved material to proposal review after new support.",
    ),
    _rule(
        PredicateLifecycleState.AMBIGUOUS,
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleTransitionKind.NEW_SUPPORT_REVIEW,
        unknown_review_required=True,
        purpose="Return ambiguity to review without selecting a nearest meaning.",
    ),
    _rule(
        PredicateLifecycleState.UNSUPPORTED,
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleTransitionKind.NEW_SUPPORT_REVIEW,
        unknown_review_required=True,
        purpose="Review the same unsupported lineage after new authority appears.",
    ),
    _rule(
        PredicateLifecycleState.IMPLEMENTATION_DEFERRED,
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleTransitionKind.REOPEN_REVIEW,
        dependency_review_required=True,
        purpose="Reopen deferred material after dependencies change.",
    ),
    _rule(
        PredicateLifecycleState.CONFLICTED,
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleTransitionKind.CONFLICT_RESOLUTION,
        conflict_review_required=True,
        purpose="Return a preserved conflict to candidate review.",
    ),
    _rule(
        PredicateLifecycleState.CONFLICTED,
        PredicateLifecycleState.REVIEWED,
        PredicateLifecycleTransitionKind.CONFLICT_RESOLUTION,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Resolve conflict into reviewed non-operative state.",
    ),
    _rule(
        PredicateLifecycleState.CONFLICTED,
        PredicateLifecycleState.DEPRECATED,
        PredicateLifecycleTransitionKind.CONFLICT_RESOLUTION,
        conflict_review_required=True,
        purpose="Resolve conflict by restricting future use.",
    ),
    _rule(
        PredicateLifecycleState.CONFLICTED,
        PredicateLifecycleState.REJECTED,
        PredicateLifecycleTransitionKind.CONFLICT_RESOLUTION,
        conflict_review_required=True,
        purpose="Resolve conflict through explicit rejection.",
    ),
)

_RULE_INDEX: Final[
    dict[
        tuple[PredicateLifecycleState, PredicateLifecycleState],
        PredicateLifecycleTransitionRule,
    ]
] = {
    (rule.from_state, rule.to_state): rule
    for rule in PREDICATE_LIFECYCLE_TRANSITION_RULES
}


def transition_rule(
    from_state: PredicateLifecycleState,
    to_state: PredicateLifecycleState,
) -> PredicateLifecycleTransitionRule | None:
    return _RULE_INDEX.get((from_state, to_state))
