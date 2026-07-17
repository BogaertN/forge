"""Pure deterministic evaluation of one Slice 38B lifecycle transition."""

from __future__ import annotations

from ..schema import (
    ActionRootIdentity,
    PredicateIdentity,
    PredicateLifecycleState,
    PredicateNamespaceIdentity,
    PredicateProvenanceReference,
)
from .identity import (
    expected_resource_lineage_id,
    resource_id,
    version_advances,
    version_compatible,
)
from .rules import transition_rule
from .schema import (
    SLICE38B_SCHEMA_VERSION,
    GovernedPredicateResource,
    PredicateGovernanceValidationCode,
    PredicateGovernanceValidationError,
    PredicateGovernanceValidationIssue,
    PredicateLifecycleAuthorityRecord,
    PredicateLifecycleTransitionDecision,
    PredicateLifecycleTransitionKind,
    PredicateLifecycleTransitionRecord,
)
from .validation import (
    report_from_issues,
    resource_scope_tokens,
    validate_governed_resource,
    validate_lifecycle_authority_record,
    validate_lifecycle_transition_record_shape,
)


_ADMISSION_TARGETS = frozenset(
    {
        PredicateLifecycleState.ADMITTED,
        PredicateLifecycleState.ARCHITECTURE_ADMITTED,
    }
)
_UNKNOWN_OR_UNSUPPORTED = frozenset(
    {
        PredicateLifecycleState.UNKNOWN,
        PredicateLifecycleState.UNSUPPORTED,
        PredicateLifecycleState.UNRESOLVED,
        PredicateLifecycleState.AMBIGUOUS,
    }
)
_RESOURCE_TYPES = (
    PredicateNamespaceIdentity,
    ActionRootIdentity,
    PredicateIdentity,
)


def _add(
    issues: list[PredicateGovernanceValidationIssue],
    path: str,
    code: PredicateGovernanceValidationCode,
    detail: str,
) -> None:
    issues.append(
        PredicateGovernanceValidationIssue(path=path, code=code, detail=detail)
    )


def _extend(
    issues: list[PredicateGovernanceValidationIssue],
    prefix: str,
    incoming: tuple[PredicateGovernanceValidationIssue, ...],
) -> None:
    for issue in incoming:
        _add(issues, f"{prefix}.{issue.path}", issue.code, issue.detail)


def evaluate_lifecycle_transition(
    source: GovernedPredicateResource,
    target: GovernedPredicateResource,
    transition: PredicateLifecycleTransitionRecord,
    authority: PredicateLifecycleAuthorityRecord,
    *,
    provenance_by_id: dict[str, PredicateProvenanceReference],
) -> PredicateLifecycleTransitionDecision:
    """Evaluate an exact proposed transition without performing it."""

    issues: list[PredicateGovernanceValidationIssue] = []

    source_report = validate_governed_resource(
        source,
        provenance_by_id=provenance_by_id,
    )
    target_report = validate_governed_resource(
        target,
        provenance_by_id=provenance_by_id,
    )
    authority_report = validate_lifecycle_authority_record(
        authority,
        provenance_by_id=provenance_by_id,
    )
    transition_report = validate_lifecycle_transition_record_shape(transition)
    _extend(issues, "source", source_report.issues)
    _extend(issues, "target", target_report.issues)
    _extend(issues, "authority", authority_report.issues)
    _extend(issues, "transition", transition_report.issues)

    if type(source) not in _RESOURCE_TYPES:
        _add(
            issues,
            "source",
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            "exact governed predicate resource required",
        )
    if type(target) not in _RESOURCE_TYPES:
        _add(
            issues,
            "target",
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            "exact governed predicate resource required",
        )

    source_state = getattr(source, "lifecycle_state", PredicateLifecycleState.UNKNOWN)
    if not isinstance(source_state, PredicateLifecycleState):
        source_state = PredicateLifecycleState.UNKNOWN
    target_state = getattr(target, "lifecycle_state", PredicateLifecycleState.UNKNOWN)
    if not isinstance(target_state, PredicateLifecycleState):
        target_state = PredicateLifecycleState.UNKNOWN

    safe_kind = getattr(
        transition,
        "transition_kind",
        PredicateLifecycleTransitionKind.NEW_SUPPORT_REVIEW,
    )
    if not isinstance(safe_kind, PredicateLifecycleTransitionKind):
        safe_kind = PredicateLifecycleTransitionKind.NEW_SUPPORT_REVIEW

    try:
        safe_source_id = resource_id(source)
        safe_lineage = expected_resource_lineage_id(source)
    except Exception:
        safe_source_id = ""
        safe_lineage = ""
    try:
        safe_target_id = resource_id(target)
    except Exception:
        safe_target_id = ""

    if (
        type(source) not in _RESOURCE_TYPES
        or type(target) not in _RESOURCE_TYPES
        or type(transition) is not PredicateLifecycleTransitionRecord
        or type(authority) is not PredicateLifecycleAuthorityRecord
        or not source_report.ok
        or not target_report.ok
        or not transition_report.ok
        or not authority_report.ok
    ):
        ordered = report_from_issues(issues).issues
        return PredicateLifecycleTransitionDecision(
            allowed=False,
            issues=ordered,
            source_resource_id=safe_source_id,
            target_resource_id=safe_target_id,
            transition_id=(
                transition.transition_id
                if type(transition) is PredicateLifecycleTransitionRecord
                and isinstance(transition.transition_id, str)
                else ""
            ),
            lineage_id=safe_lineage,
            from_state=source_state,
            to_state=target_state,
            transition_kind=safe_kind,
        )

    if type(source) is not type(target):
        _add(
            issues,
            "target",
            PredicateGovernanceValidationCode.RESOURCE_KIND_MISMATCH,
            "source and target must have the same exact resource type",
        )

    try:
        source_id = resource_id(source)
        target_id = resource_id(target)
        source_lineage = expected_resource_lineage_id(source)
        target_lineage = expected_resource_lineage_id(target)
    except Exception:
        ordered = report_from_issues(issues).issues
        return PredicateLifecycleTransitionDecision(
            allowed=False,
            issues=ordered,
            source_resource_id=safe_source_id,
            target_resource_id=safe_target_id,
            transition_id=transition.transition_id,
            lineage_id=safe_lineage,
            from_state=source_state,
            to_state=target_state,
            transition_kind=safe_kind,
        )

    if source.resource_kind != target.resource_kind:
        _add(
            issues,
            "target.resource_kind",
            PredicateGovernanceValidationCode.RESOURCE_KIND_MISMATCH,
            "source and target resource kinds differ",
        )
    if source_lineage != target_lineage:
        _add(
            issues,
            "target",
            PredicateGovernanceValidationCode.LINEAGE_MISMATCH,
            "source and target do not preserve the same canonical lineage",
        )

    expected_bindings = (
        ("transition.lineage_id", transition.lineage_id, source_lineage),
        ("transition.source_resource_id", transition.source_resource_id, source_id),
        ("transition.target_resource_id", transition.target_resource_id, target_id),
        ("transition.source_version", transition.source_version, source.version),
        ("transition.target_version", transition.target_version, target.version),
        ("transition.from_state", transition.from_state, source.lifecycle_state),
        ("transition.to_state", transition.to_state, target.lifecycle_state),
        ("transition.resource_kind", transition.resource_kind, source.resource_kind),
        (
            "transition.authority_record_ref",
            transition.authority_record_ref,
            authority.authority_id,
        ),
    )
    for path, actual, expected in expected_bindings:
        if actual != expected:
            _add(
                issues,
                path,
                PredicateGovernanceValidationCode.AUTHORITY_BINDING_MISMATCH,
                f"expected exact binding {expected!r}",
            )

    try:
        advances = version_advances(source.version, target.version)
        compatible = version_compatible(source.version, target.version)
    except Exception:
        advances = False
        compatible = False
    if not advances:
        _add(
            issues,
            "target.version",
            PredicateGovernanceValidationCode.VERSION_NOT_ADVANCING,
            "target version must strictly advance the source version",
        )
    elif not compatible:
        _add(
            issues,
            "target.version",
            PredicateGovernanceValidationCode.VERSION_INCOMPATIBLE,
            "Slice 38B requires same-major compatible version advancement",
        )

    if transition.prior_record_preserved is not True:
        _add(
            issues,
            "transition.prior_record_preserved",
            PredicateGovernanceValidationCode.PRIOR_RECORD_NOT_PRESERVED,
            "every transition must preserve the prior immutable record",
        )
    if transition.automatic_transition is not False:
        _add(
            issues,
            "transition.automatic_transition",
            PredicateGovernanceValidationCode.AUTOMATIC_TRANSITION_PROHIBITED,
            "automatic lifecycle transitions are prohibited",
        )
    if transition.in_place_mutation_performed is not False:
        _add(
            issues,
            "transition.in_place_mutation_performed",
            PredicateGovernanceValidationCode.IN_PLACE_MUTATION_PROHIBITED,
            "in-place mutation is prohibited; create a new immutable version",
        )
    if transition.nearest_known_substitution_performed is not False:
        _add(
            issues,
            "transition.nearest_known_substitution_performed",
            PredicateGovernanceValidationCode.NEAREST_KNOWN_SUBSTITUTION_PROHIBITED,
            "unknown or unsupported material cannot become the nearest known root",
        )
    if transition.similarity_authority_used is not False:
        _add(
            issues,
            "transition.similarity_authority_used",
            PredicateGovernanceValidationCode.SIMILARITY_AUTHORITY_PROHIBITED,
            "similarity cannot become predicate or lifecycle authority",
        )

    if source_id not in authority.affected_record_refs:
        _add(
            issues,
            "authority.affected_record_refs",
            PredicateGovernanceValidationCode.AUTHORITY_BINDING_MISMATCH,
            "source resource identity must be named by authority",
        )
    if target_id not in authority.affected_record_refs:
        _add(
            issues,
            "authority.affected_record_refs",
            PredicateGovernanceValidationCode.AUTHORITY_BINDING_MISMATCH,
            "target resource identity must be named by authority",
        )

    target_scope = frozenset(resource_scope_tokens(target))
    source_scope = frozenset(resource_scope_tokens(source))
    authority_scope = frozenset(authority.scope)
    if not target_scope:
        _add(
            issues,
            "target.scope",
            PredicateGovernanceValidationCode.SCOPE_REQUIRED,
            "target requires explicit bounded scope",
        )
    if not target_scope.issubset(authority_scope):
        _add(
            issues,
            "authority.scope",
            PredicateGovernanceValidationCode.SCOPE_EXPANSION,
            "authority scope must contain every target scope token",
        )
    if not target_scope.issubset(source_scope):
        _add(
            issues,
            "target.scope",
            PredicateGovernanceValidationCode.SCOPE_EXPANSION,
            "Slice 38B transitions may narrow but may not broaden scope",
        )

    source_non_scope = frozenset(source.non_scope)
    target_non_scope = frozenset(target.non_scope)
    if not source_non_scope.issubset(target_non_scope):
        _add(
            issues,
            "target.non_scope",
            PredicateGovernanceValidationCode.NON_SCOPE_NARROWING,
            "a transition may not remove predecessor non-scope boundaries",
        )

    if not frozenset(source.prohibited_uses).issubset(
        frozenset(target.prohibited_uses)
    ):
        _add(
            issues,
            "target.prohibited_uses",
            PredicateGovernanceValidationCode.PROHIBITED_USE_REMOVED,
            "a transition may not remove predecessor prohibited uses",
        )

    added_permitted_uses = frozenset(target.permitted_uses) - frozenset(
        source.permitted_uses
    )
    if added_permitted_uses:
        _add(
            issues,
            "target.permitted_uses",
            PredicateGovernanceValidationCode.PERMITTED_USE_ADDED,
            "a Slice 38B transition may not add permitted uses: "
            f"{sorted(added_permitted_uses)}",
        )

    rule = transition_rule(source.lifecycle_state, target.lifecycle_state)
    if rule is None:
        _add(
            issues,
            "transition",
            PredicateGovernanceValidationCode.TRANSITION_NOT_PERMITTED,
            "no accepted Slice 38B rule permits this state transition",
        )
    else:
        if transition.transition_kind not in rule.allowed_kinds:
            _add(
                issues,
                "transition.transition_kind",
                PredicateGovernanceValidationCode.TRANSITION_KIND_MISMATCH,
                "transition kind is not permitted for this state pair",
            )
        reviews = (
            (
                rule.conflict_review_required,
                authority.conflict_review_complete,
                "authority.conflict_review_complete",
            ),
            (
                rule.unknown_review_required,
                authority.unknown_state_review_complete,
                "authority.unknown_state_review_complete",
            ),
            (
                rule.dependency_review_required,
                authority.later_dependency_review_complete,
                "authority.later_dependency_review_complete",
            ),
        )
        for required, complete, path in reviews:
            if required and not complete:
                _add(
                    issues,
                    path,
                    PredicateGovernanceValidationCode.REVIEW_INCOMPLETE,
                    "transition rule requires this review to be complete",
                )

    if target.lifecycle_state in _ADMISSION_TARGETS:
        if authority.unresolved_dependency_refs:
            _add(
                issues,
                "authority.unresolved_dependency_refs",
                PredicateGovernanceValidationCode.UNRESOLVED_DEPENDENCY,
                "admission is blocked while dependencies remain unresolved",
            )
        if authority.missing_authority_refs:
            _add(
                issues,
                "authority.missing_authority_refs",
                PredicateGovernanceValidationCode.UNRESOLVED_DEPENDENCY,
                "admission is blocked while authority remains missing",
            )
        if source.lifecycle_state in _UNKNOWN_OR_UNSUPPORTED:
            _add(
                issues,
                "transition",
                PredicateGovernanceValidationCode.UNKNOWN_STATE_PROMOTION_PROHIBITED,
                "unknown or unsupported state must return through candidate and reviewed states",
            )

    if target.lifecycle_state is PredicateLifecycleState.QUARANTINED:
        if not transition.quarantine_cause_refs:
            _add(
                issues,
                "transition.quarantine_cause_refs",
                PredicateGovernanceValidationCode.QUARANTINE_CAUSE_REQUIRED,
                "quarantine requires exact cause references",
            )
        if not transition.quarantine_release_requirement_refs:
            _add(
                issues,
                "transition.quarantine_release_requirement_refs",
                PredicateGovernanceValidationCode.QUARANTINE_RELEASE_REQUIREMENT_REQUIRED,
                "quarantine requires exact release requirements",
            )
    elif transition.transition_kind is not PredicateLifecycleTransitionKind.RELEASE_TO_REVIEW:
        if transition.quarantine_cause_refs:
            _add(
                issues,
                "transition.quarantine_cause_refs",
                PredicateGovernanceValidationCode.QUARANTINE_CAUSE_REQUIRED,
                "quarantine causes are reserved for quarantine transitions",
            )
        if transition.quarantine_release_requirement_refs:
            _add(
                issues,
                "transition.quarantine_release_requirement_refs",
                PredicateGovernanceValidationCode.QUARANTINE_RELEASE_REQUIREMENT_REQUIRED,
                "release requirements are reserved for quarantine transitions",
            )

    if transition.transition_kind is PredicateLifecycleTransitionKind.RELEASE_TO_REVIEW:
        if source.lifecycle_state is not PredicateLifecycleState.QUARANTINED:
            _add(
                issues,
                "transition.transition_kind",
                PredicateGovernanceValidationCode.TRANSITION_KIND_MISMATCH,
                "only quarantined material may be released to review",
            )
        if not transition.resolved_quarantine_cause_refs:
            _add(
                issues,
                "transition.resolved_quarantine_cause_refs",
                PredicateGovernanceValidationCode.QUARANTINE_CAUSE_UNRESOLVED,
                "release must identify resolved quarantine causes",
            )
        if transition.quarantine_cause_refs:
            _add(
                issues,
                "transition.quarantine_cause_refs",
                PredicateGovernanceValidationCode.QUARANTINE_CAUSE_REQUIRED,
                "release cannot introduce or restate quarantine causes",
            )
        if not transition.quarantine_release_requirement_refs:
            _add(
                issues,
                "transition.quarantine_release_requirement_refs",
                PredicateGovernanceValidationCode.QUARANTINE_RELEASE_REQUIREMENT_REQUIRED,
                "release must identify every satisfied quarantine release requirement",
            )
    elif transition.resolved_quarantine_cause_refs:
        _add(
            issues,
            "transition.resolved_quarantine_cause_refs",
            PredicateGovernanceValidationCode.QUARANTINE_CAUSE_UNRESOLVED,
            "resolved causes are reserved for quarantine release",
        )

    if target.lifecycle_state is PredicateLifecycleState.REJECTED:
        if not transition.blocked_reentry_keys:
            _add(
                issues,
                "transition.blocked_reentry_keys",
                PredicateGovernanceValidationCode.BLOCKED_REENTRY_REQUIRED,
                "rejection requires materially equivalent blocked reentry keys",
            )
        elif transition.lineage_id not in transition.blocked_reentry_keys:
            _add(
                issues,
                "transition.blocked_reentry_keys",
                PredicateGovernanceValidationCode.BLOCKED_REENTRY_REQUIRED,
                "rejection must block reentry of the exact canonical lineage",
            )
    elif transition.blocked_reentry_keys:
        _add(
            issues,
            "transition.blocked_reentry_keys",
            PredicateGovernanceValidationCode.BLOCKED_REENTRY_REQUIRED,
            "blocked reentry keys are reserved for rejection",
        )

    if target.lifecycle_state is PredicateLifecycleState.SUPERSEDED:
        if not transition.superseding_resource_ref:
            _add(
                issues,
                "transition.superseding_resource_ref",
                PredicateGovernanceValidationCode.SUPERSEDING_RESOURCE_REQUIRED,
                "supersession requires an explicit successor",
            )
    elif transition.superseding_resource_ref is not None:
        _add(
            issues,
            "transition.superseding_resource_ref",
            PredicateGovernanceValidationCode.SUPERSEDING_RESOURCE_INVALID,
            "successor reference is reserved for supersession",
        )

    if transition.transition_kind is PredicateLifecycleTransitionKind.REOPEN_REVIEW:
        if source.lifecycle_state in {
            PredicateLifecycleState.REJECTED,
            PredicateLifecycleState.WITHDRAWN,
        } and not transition.prior_disposition_transition_ref:
            _add(
                issues,
                "transition.prior_disposition_transition_ref",
                PredicateGovernanceValidationCode.HISTORICAL_ANCESTRY_REQUIRED,
                "reopening must reference the prior rejection or withdrawal",
            )
    elif transition.prior_disposition_transition_ref is not None:
        _add(
            issues,
            "transition.prior_disposition_transition_ref",
            PredicateGovernanceValidationCode.HISTORICAL_ANCESTRY_REQUIRED,
            "prior disposition reference is reserved for explicit reopening",
        )

    ordered = report_from_issues(issues).issues
    return PredicateLifecycleTransitionDecision(
        allowed=not ordered,
        issues=ordered,
        source_resource_id=source_id,
        target_resource_id=target_id,
        transition_id=transition.transition_id,
        lineage_id=source_lineage,
        from_state=source.lifecycle_state,
        to_state=target.lifecycle_state,
        transition_kind=transition.transition_kind,
    )


def assert_lifecycle_transition(
    source: GovernedPredicateResource,
    target: GovernedPredicateResource,
    transition: PredicateLifecycleTransitionRecord,
    authority: PredicateLifecycleAuthorityRecord,
    *,
    provenance_by_id: dict[str, PredicateProvenanceReference],
) -> PredicateLifecycleTransitionDecision:
    decision = evaluate_lifecycle_transition(
        source,
        target,
        transition,
        authority,
        provenance_by_id=provenance_by_id,
    )
    if not decision.allowed:
        raise PredicateGovernanceValidationError(
            report_from_issues(list(decision.issues))
        )
    return decision
