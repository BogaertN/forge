"""Explicit Slice 37B concept-resource lifecycle transition matrix.

Only listed state pairs and transition kinds may pass.  The matrix is
architecture-law validation data; it performs no transition and changes no
resource.
"""

from __future__ import annotations

from typing import Final

from ..schema import ConceptLifecycleState
from .schema import (
    ConceptLifecycleTransitionKind,
    ConceptLifecycleTransitionRule,
)


def _rule(
    from_state: ConceptLifecycleState,
    to_state: ConceptLifecycleState,
    *allowed_kinds: ConceptLifecycleTransitionKind,
    conflict_review_required: bool = False,
    unknown_review_required: bool = False,
    dependency_review_required: bool = False,
    purpose: str,
) -> ConceptLifecycleTransitionRule:
    return ConceptLifecycleTransitionRule(
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


CONCEPT_LIFECYCLE_TRANSITION_RULES: Final[
    tuple[ConceptLifecycleTransitionRule, ...]
] = (
    _rule(
        ConceptLifecycleState.OBSERVED,
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleTransitionKind.OBSERVATION_REVIEW,
        purpose="Move a preserved source observation into non-operative review.",
    ),
    _rule(
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleState.ADMITTED,
        ConceptLifecycleTransitionKind.ADMISSION,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Admit one bounded resource within explicit semantic scope.",
    ),
    _rule(
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleState.ARCHITECTURE_ADMITTED,
        ConceptLifecycleTransitionKind.ARCHITECTURE_ADMISSION,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Admit architecture law without claiming live runtime behavior.",
    ),
    _rule(
        ConceptLifecycleState.ADMITTED,
        ConceptLifecycleState.OPERATIONALLY_BOUNDED,
        ConceptLifecycleTransitionKind.OPERATIONAL_BOUNDING,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Preserve exact verified operational scope without generalization.",
    ),
    _rule(
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleState.IMPLEMENTATION_DEFERRED,
        ConceptLifecycleTransitionKind.DEFERMENT,
        dependency_review_required=True,
        purpose="Preserve a material requirement whose implementation is deferred.",
    ),
    _rule(
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleState.UNKNOWN,
        ConceptLifecycleTransitionKind.MARK_UNKNOWN,
        purpose="Preserve that identity or authority is not lawfully established.",
    ),
    _rule(
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleState.UNRESOLVED,
        ConceptLifecycleTransitionKind.MARK_UNRESOLVED,
        purpose="Preserve a known question pending competent decision.",
    ),
    _rule(
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleState.AMBIGUOUS,
        ConceptLifecycleTransitionKind.MARK_AMBIGUOUS,
        purpose="Preserve multiple materially supported possibilities.",
    ),
    _rule(
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleState.UNSUPPORTED,
        ConceptLifecycleTransitionKind.MARK_UNSUPPORTED,
        purpose="Preserve missing support without converting it into rejection.",
    ),
    _rule(
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleState.CONFLICTED,
        ConceptLifecycleTransitionKind.MARK_CONFLICTED,
        conflict_review_required=True,
        purpose="Preserve a material conflict that blocks active use.",
    ),
    _rule(
        ConceptLifecycleState.ADMITTED,
        ConceptLifecycleState.ADMITTED,
        ConceptLifecycleTransitionKind.CORRECTION,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Correct an admitted resource while preserving stable lineage.",
    ),
    _rule(
        ConceptLifecycleState.ARCHITECTURE_ADMITTED,
        ConceptLifecycleState.ARCHITECTURE_ADMITTED,
        ConceptLifecycleTransitionKind.CORRECTION,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Correct architecture-admitted meaning without runtime claim.",
    ),
    _rule(
        ConceptLifecycleState.OPERATIONALLY_BOUNDED,
        ConceptLifecycleState.OPERATIONALLY_BOUNDED,
        ConceptLifecycleTransitionKind.CORRECTION,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Correct a bounded operational record without expanding scope.",
    ),
    _rule(
        ConceptLifecycleState.ADMITTED,
        ConceptLifecycleState.DEPRECATED,
        ConceptLifecycleTransitionKind.DEPRECATION,
        conflict_review_required=True,
        purpose="Restrict new use while preserving lawful legacy ancestry.",
    ),
    _rule(
        ConceptLifecycleState.ARCHITECTURE_ADMITTED,
        ConceptLifecycleState.DEPRECATED,
        ConceptLifecycleTransitionKind.DEPRECATION,
        conflict_review_required=True,
        purpose="Deprecate architecture authority without deleting history.",
    ),
    _rule(
        ConceptLifecycleState.OPERATIONALLY_BOUNDED,
        ConceptLifecycleState.DEPRECATED,
        ConceptLifecycleTransitionKind.DEPRECATION,
        conflict_review_required=True,
        purpose="Deprecate bounded operational use within exact scope.",
    ),
    _rule(
        ConceptLifecycleState.ADMITTED,
        ConceptLifecycleState.SUPERSEDED,
        ConceptLifecycleTransitionKind.SUPERSESSION,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Replace admitted authority with an identified successor.",
    ),
    _rule(
        ConceptLifecycleState.ARCHITECTURE_ADMITTED,
        ConceptLifecycleState.SUPERSEDED,
        ConceptLifecycleTransitionKind.SUPERSESSION,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Replace architecture authority with an identified successor.",
    ),
    _rule(
        ConceptLifecycleState.OPERATIONALLY_BOUNDED,
        ConceptLifecycleState.SUPERSEDED,
        ConceptLifecycleTransitionKind.SUPERSESSION,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Replace bounded operational authority without rewriting history.",
    ),
    _rule(
        ConceptLifecycleState.DEPRECATED,
        ConceptLifecycleState.SUPERSEDED,
        ConceptLifecycleTransitionKind.SUPERSESSION,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Identify a successor while preserving deprecated legacy state.",
    ),
    _rule(
        ConceptLifecycleState.SUPERSEDED,
        ConceptLifecycleState.SUPERSEDED,
        ConceptLifecycleTransitionKind.HISTORICAL_ONLY,
        purpose="Mark superseded material historical-only without reactivation.",
    ),
    _rule(
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleState.QUARANTINED,
        ConceptLifecycleTransitionKind.QUARANTINE,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Block active use pending authority or safety resolution.",
    ),
    _rule(
        ConceptLifecycleState.ADMITTED,
        ConceptLifecycleState.QUARANTINED,
        ConceptLifecycleTransitionKind.QUARANTINE,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Suspend admitted use after a material authority defect.",
    ),
    _rule(
        ConceptLifecycleState.ARCHITECTURE_ADMITTED,
        ConceptLifecycleState.QUARANTINED,
        ConceptLifecycleTransitionKind.QUARANTINE,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Suspend architecture use after a material authority defect.",
    ),
    _rule(
        ConceptLifecycleState.OPERATIONALLY_BOUNDED,
        ConceptLifecycleState.QUARANTINED,
        ConceptLifecycleTransitionKind.QUARANTINE,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Suspend bounded operational use after a material defect.",
    ),
    _rule(
        ConceptLifecycleState.CONFLICTED,
        ConceptLifecycleState.QUARANTINED,
        ConceptLifecycleTransitionKind.QUARANTINE,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Contain an unresolved material conflict.",
    ),
    _rule(
        ConceptLifecycleState.UNSUPPORTED,
        ConceptLifecycleState.QUARANTINED,
        ConceptLifecycleTransitionKind.QUARANTINE,
        dependency_review_required=True,
        purpose="Contain unsupported material pending lawful disposition.",
    ),
    _rule(
        ConceptLifecycleState.QUARANTINED,
        ConceptLifecycleState.QUARANTINED,
        ConceptLifecycleTransitionKind.CONTINUE_QUARANTINE,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Continue quarantine while preserving missing authority.",
    ),
    _rule(
        ConceptLifecycleState.QUARANTINED,
        ConceptLifecycleState.ADMITTED,
        ConceptLifecycleTransitionKind.RELEASE_FROM_QUARANTINE,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Release into bounded admission after causes are resolved.",
    ),
    _rule(
        ConceptLifecycleState.QUARANTINED,
        ConceptLifecycleState.ARCHITECTURE_ADMITTED,
        ConceptLifecycleTransitionKind.RELEASE_FROM_QUARANTINE,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Release into architecture admission after causes are resolved.",
    ),
    _rule(
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleState.REJECTED,
        ConceptLifecycleTransitionKind.REJECTION,
        conflict_review_required=True,
        purpose="Deny a candidate within explicit scope.",
    ),
    _rule(
        ConceptLifecycleState.ADMITTED,
        ConceptLifecycleState.REJECTED,
        ConceptLifecycleTransitionKind.REJECTION,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Invalidate prior admission within explicit scope.",
    ),
    _rule(
        ConceptLifecycleState.ARCHITECTURE_ADMITTED,
        ConceptLifecycleState.REJECTED,
        ConceptLifecycleTransitionKind.REJECTION,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Invalidate prior architecture admission within explicit scope.",
    ),
    _rule(
        ConceptLifecycleState.OPERATIONALLY_BOUNDED,
        ConceptLifecycleState.REJECTED,
        ConceptLifecycleTransitionKind.REJECTION,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Invalidate prior bounded operation within explicit scope.",
    ),
    _rule(
        ConceptLifecycleState.QUARANTINED,
        ConceptLifecycleState.REJECTED,
        ConceptLifecycleTransitionKind.REJECTION,
        conflict_review_required=True,
        purpose="Deny a quarantined resource after review.",
    ),
    _rule(
        ConceptLifecycleState.DEPRECATED,
        ConceptLifecycleState.REJECTED,
        ConceptLifecycleTransitionKind.REJECTION,
        conflict_review_required=True,
        purpose="Reject new or stated use while preserving prior lawful legacy.",
    ),
    _rule(
        ConceptLifecycleState.REJECTED,
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleTransitionKind.REOPEN_REVIEW,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Rarely reopen review under a new explicit authority basis.",
    ),
    _rule(
        ConceptLifecycleState.UNKNOWN,
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleTransitionKind.NEW_SUPPORT_REVIEW,
        purpose="Review an unknown resource after new source support appears.",
    ),
    _rule(
        ConceptLifecycleState.UNRESOLVED,
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleTransitionKind.NEW_SUPPORT_REVIEW,
        purpose="Return a pending resource to review after new support appears.",
    ),
    _rule(
        ConceptLifecycleState.UNSUPPORTED,
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleTransitionKind.NEW_SUPPORT_REVIEW,
        purpose="Return unsupported material to review after new authority appears.",
    ),
    _rule(
        ConceptLifecycleState.AMBIGUOUS,
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleTransitionKind.NEW_SUPPORT_REVIEW,
        purpose="Return ambiguity to review without selecting a meaning.",
    ),
    _rule(
        ConceptLifecycleState.IMPLEMENTATION_DEFERRED,
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleTransitionKind.REOPEN_REVIEW,
        dependency_review_required=True,
        purpose="Reopen a deferred resource after dependencies change.",
    ),
    _rule(
        ConceptLifecycleState.CONFLICTED,
        ConceptLifecycleState.CANDIDATE,
        ConceptLifecycleTransitionKind.CONFLICT_RESOLUTION,
        conflict_review_required=True,
        purpose="Return a preserved conflict to candidate review.",
    ),
    _rule(
        ConceptLifecycleState.CONFLICTED,
        ConceptLifecycleState.ADMITTED,
        ConceptLifecycleTransitionKind.CONFLICT_RESOLUTION,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Resolve conflict into bounded admission under competent authority.",
    ),
    _rule(
        ConceptLifecycleState.CONFLICTED,
        ConceptLifecycleState.ARCHITECTURE_ADMITTED,
        ConceptLifecycleTransitionKind.CONFLICT_RESOLUTION,
        conflict_review_required=True,
        unknown_review_required=True,
        dependency_review_required=True,
        purpose="Resolve conflict into architecture admission only.",
    ),
    _rule(
        ConceptLifecycleState.CONFLICTED,
        ConceptLifecycleState.DEPRECATED,
        ConceptLifecycleTransitionKind.CONFLICT_RESOLUTION,
        conflict_review_required=True,
        purpose="Resolve conflict by restricting future use.",
    ),
    _rule(
        ConceptLifecycleState.CONFLICTED,
        ConceptLifecycleState.SUPERSEDED,
        ConceptLifecycleTransitionKind.CONFLICT_RESOLUTION,
        conflict_review_required=True,
        dependency_review_required=True,
        purpose="Resolve conflict through an identified successor.",
    ),
    _rule(
        ConceptLifecycleState.CONFLICTED,
        ConceptLifecycleState.REJECTED,
        ConceptLifecycleTransitionKind.CONFLICT_RESOLUTION,
        conflict_review_required=True,
        purpose="Resolve conflict through explicit rejection.",
    ),
)

_RULE_INDEX: Final[
    dict[
        tuple[ConceptLifecycleState, ConceptLifecycleState],
        ConceptLifecycleTransitionRule,
    ]
] = {
    (rule.from_state, rule.to_state): rule
    for rule in CONCEPT_LIFECYCLE_TRANSITION_RULES
}


def transition_rule(
    from_state: ConceptLifecycleState,
    to_state: ConceptLifecycleState,
) -> ConceptLifecycleTransitionRule | None:
    return _RULE_INDEX.get((from_state, to_state))
