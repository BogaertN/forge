"""Deterministic evaluation of one proposed concept-resource lifecycle transition.

Evaluation is pure and read-only.  It validates exact immutable source and target
records, provenance, competent human-approved authority, the Document 4 state
matrix, version advancement, scope, quarantine/rejection/supersession duties,
and preservation of prior ancestry.  It never mutates a resource or performs a
transition on behalf of the caller.
"""

from __future__ import annotations

from ..schema import ConceptLifecycleState
from .identity import (
    expected_resource_lineage_id,
    resource_id,
    version_advances,
)
from .rules import transition_rule
from .schema import (
    SLICE37B_SCHEMA_VERSION,
    ConceptGovernanceValidationCode,
    ConceptGovernanceValidationError,
    ConceptGovernanceValidationIssue,
    ConceptLifecycleAuthorityRecord,
    ConceptLifecycleTransitionDecision,
    ConceptLifecycleTransitionKind,
    ConceptLifecycleTransitionRecord,
    GovernedConceptResource,
)
from .validation import (
    report_from_issues,
    resource_scope_tokens,
    validate_governed_resource,
    validate_lifecycle_authority_record,
)
from ..schema import ConceptProvenanceReference


_ADMISSION_TARGETS = frozenset(
    {
        ConceptLifecycleState.ADMITTED,
        ConceptLifecycleState.ARCHITECTURE_ADMITTED,
        ConceptLifecycleState.OPERATIONALLY_BOUNDED,
    }
)


def _add(
    issues: list[ConceptGovernanceValidationIssue],
    path: str,
    code: ConceptGovernanceValidationCode,
    detail: str,
) -> None:
    issues.append(
        ConceptGovernanceValidationIssue(
            path=path,
            code=code,
            detail=detail,
        )
    )


def _extend(
    issues: list[ConceptGovernanceValidationIssue],
    prefix: str,
    incoming: tuple[ConceptGovernanceValidationIssue, ...],
) -> None:
    for issue in incoming:
        _add(
            issues,
            f"{prefix}.{issue.path}",
            issue.code,
            issue.detail,
        )


def evaluate_lifecycle_transition(
    source: GovernedConceptResource,
    target: GovernedConceptResource,
    transition: ConceptLifecycleTransitionRecord,
    authority: ConceptLifecycleAuthorityRecord,
    *,
    provenance_by_id: dict[str, ConceptProvenanceReference],
) -> ConceptLifecycleTransitionDecision:
    """Evaluate an exact proposed transition and return a deterministic decision."""

    issues: list[ConceptGovernanceValidationIssue] = []

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

    _extend(issues, "source", source_report.issues)
    _extend(issues, "target", target_report.issues)
    _extend(issues, "authority", authority_report.issues)

    source_state = getattr(
        source,
        "lifecycle_state",
        ConceptLifecycleState.UNKNOWN,
    )
    if not isinstance(source_state, ConceptLifecycleState):
        source_state = ConceptLifecycleState.UNKNOWN

    target_state = getattr(
        target,
        "lifecycle_state",
        ConceptLifecycleState.UNKNOWN,
    )
    if not isinstance(target_state, ConceptLifecycleState):
        target_state = ConceptLifecycleState.UNKNOWN

    try:
        safe_source_id = resource_id(source)
        safe_source_lineage = expected_resource_lineage_id(source)
    except (TypeError, AttributeError, ValueError):
        safe_source_id = ""
        safe_source_lineage = ""

    try:
        safe_target_id = resource_id(target)
    except (TypeError, AttributeError, ValueError):
        safe_target_id = ""

    safe_transition_kind = getattr(
        transition,
        "transition_kind",
        ConceptLifecycleTransitionKind.NEW_SUPPORT_REVIEW,
    )
    if not isinstance(
        safe_transition_kind,
        ConceptLifecycleTransitionKind,
    ):
        safe_transition_kind = (
            ConceptLifecycleTransitionKind.NEW_SUPPORT_REVIEW
        )

    if (
        not source_report.ok
        and any(
            issue.code is ConceptGovernanceValidationCode.TYPE_MISMATCH
            for issue in source_report.issues
        )
    ) or (
        not target_report.ok
        and any(
            issue.code is ConceptGovernanceValidationCode.TYPE_MISMATCH
            for issue in target_report.issues
        )
    ) or type(authority) is not ConceptLifecycleAuthorityRecord:
        ordered = report_from_issues(issues).issues
        return ConceptLifecycleTransitionDecision(
            allowed=False,
            issues=ordered,
            source_resource_id=safe_source_id,
            target_resource_id=safe_target_id,
            transition_id=getattr(transition, "transition_id", ""),
            lineage_id=safe_source_lineage,
            from_state=source_state,
            to_state=target_state,
            transition_kind=safe_transition_kind,
        )

    if type(transition) is not ConceptLifecycleTransitionRecord:
        _add(
            issues,
            "transition",
            ConceptGovernanceValidationCode.TYPE_MISMATCH,
            "exact ConceptLifecycleTransitionRecord required",
        )
        ordered = report_from_issues(issues).issues
        return ConceptLifecycleTransitionDecision(
            allowed=False,
            issues=ordered,
            source_resource_id=safe_source_id,
            target_resource_id=safe_target_id,
            transition_id="",
            lineage_id=safe_source_lineage,
            from_state=source_state,
            to_state=target_state,
            transition_kind=safe_transition_kind,
        )

    if transition.schema_version != SLICE37B_SCHEMA_VERSION:
        _add(
            issues,
            "transition.schema_version",
            ConceptGovernanceValidationCode.SCHEMA_VERSION_MISMATCH,
            f"expected {SLICE37B_SCHEMA_VERSION}",
        )

    if transition.transition_id != transition.expected_id():
        _add(
            issues,
            "transition.transition_id",
            ConceptGovernanceValidationCode.IDENTITY_MISMATCH,
            "transition identity does not match its canonical body",
        )

    source_id = resource_id(source)
    target_id = resource_id(target)
    source_lineage = expected_resource_lineage_id(source)
    target_lineage = expected_resource_lineage_id(target)

    if type(source) is not type(target):
        _add(
            issues,
            "target",
            ConceptGovernanceValidationCode.RESOURCE_KIND_MISMATCH,
            "source and target must have the same exact resource type",
        )

    if source.resource_kind != target.resource_kind:
        _add(
            issues,
            "target.resource_kind",
            ConceptGovernanceValidationCode.RESOURCE_KIND_MISMATCH,
            "source and target resource kinds differ",
        )

    if source_lineage != target_lineage:
        _add(
            issues,
            "target",
            ConceptGovernanceValidationCode.LINEAGE_MISMATCH,
            "source and target do not preserve the same material identity lineage",
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
        ("transition.authority_record_ref", transition.authority_record_ref, authority.authority_id),
    )

    for path, actual, expected in expected_bindings:
        if actual != expected:
            _add(
                issues,
                path,
                ConceptGovernanceValidationCode.AUTHORITY_BINDING_MISMATCH,
                f"expected exact binding {expected!r}",
            )

    try:
        advances = version_advances(source.version, target.version)
    except (TypeError, ValueError):
        advances = False

    if not advances:
        _add(
            issues,
            "target.version",
            ConceptGovernanceValidationCode.VERSION_NOT_ADVANCING,
            "target version must strictly advance the source version",
        )

    if transition.prior_record_preserved is not True:
        _add(
            issues,
            "transition.prior_record_preserved",
            ConceptGovernanceValidationCode.PRIOR_RECORD_NOT_PRESERVED,
            "every transition must preserve the prior immutable record",
        )

    if transition.automatic_transition is not False:
        _add(
            issues,
            "transition.automatic_transition",
            ConceptGovernanceValidationCode.AUTOMATIC_TRANSITION_PROHIBITED,
            "automatic lifecycle transitions are prohibited",
        )

    if source_id not in authority.affected_record_refs:
        _add(
            issues,
            "authority.affected_record_refs",
            ConceptGovernanceValidationCode.AUTHORITY_BINDING_MISMATCH,
            "source resource identity must be named by the authority record",
        )

    if target_id not in authority.affected_record_refs:
        _add(
            issues,
            "authority.affected_record_refs",
            ConceptGovernanceValidationCode.AUTHORITY_BINDING_MISMATCH,
            "target resource identity must be named by the authority record",
        )

    target_scope = frozenset(resource_scope_tokens(target))
    authority_scope = frozenset(authority.scope)

    if not target_scope:
        _add(
            issues,
            "target.scope",
            ConceptGovernanceValidationCode.SCOPE_REQUIRED,
            "target resource requires explicit bounded scope",
        )
    elif not target_scope.issubset(authority_scope):
        _add(
            issues,
            "authority.scope",
            ConceptGovernanceValidationCode.SCOPE_EXPANSION,
            "authority scope must contain every target scope token",
        )

    rule = transition_rule(source.lifecycle_state, target.lifecycle_state)

    if rule is None:
        _add(
            issues,
            "transition",
            ConceptGovernanceValidationCode.TRANSITION_NOT_PERMITTED,
            "no accepted Slice 37B rule permits this state transition",
        )
    else:
        if transition.transition_kind not in rule.allowed_kinds:
            _add(
                issues,
                "transition.transition_kind",
                ConceptGovernanceValidationCode.TRANSITION_KIND_MISMATCH,
                "transition kind is not permitted for this state pair",
            )

        required_reviews = (
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

        for required, complete, path in required_reviews:
            if required and not complete:
                _add(
                    issues,
                    path,
                    ConceptGovernanceValidationCode.REVIEW_INCOMPLETE,
                    "transition rule requires this review to be complete",
                )

    if target.lifecycle_state in _ADMISSION_TARGETS:
        if authority.unresolved_dependency_refs:
            _add(
                issues,
                "authority.unresolved_dependency_refs",
                ConceptGovernanceValidationCode.UNRESOLVED_DEPENDENCY,
                "active authority state is blocked while dependencies remain unresolved",
            )
        if authority.missing_authority_refs:
            _add(
                issues,
                "authority.missing_authority_refs",
                ConceptGovernanceValidationCode.UNRESOLVED_DEPENDENCY,
                "active authority state is blocked while authority remains missing",
            )

    if target.lifecycle_state is ConceptLifecycleState.OPERATIONALLY_BOUNDED:
        if not transition.verified_scope_refs:
            _add(
                issues,
                "transition.verified_scope_refs",
                ConceptGovernanceValidationCode.VERIFIED_SCOPE_REQUIRED,
                "operationally bounded state requires exact verified-scope references",
            )
    elif transition.verified_scope_refs:
        _add(
            issues,
            "transition.verified_scope_refs",
            ConceptGovernanceValidationCode.VERIFIED_SCOPE_REQUIRED,
            "verified-scope references are reserved for operational bounding",
        )

    if target.lifecycle_state is ConceptLifecycleState.QUARANTINED:
        if not transition.quarantine_cause_refs:
            _add(
                issues,
                "transition.quarantine_cause_refs",
                ConceptGovernanceValidationCode.QUARANTINE_CAUSE_REQUIRED,
                "quarantine requires at least one exact cause reference",
            )
        if not transition.quarantine_release_requirement_refs:
            _add(
                issues,
                "transition.quarantine_release_requirement_refs",
                ConceptGovernanceValidationCode.QUARANTINE_RELEASE_REQUIREMENT_REQUIRED,
                "quarantine requires explicit release conditions or an explicit no-release condition",
            )
    elif transition.transition_kind is not ConceptLifecycleTransitionKind.RELEASE_FROM_QUARANTINE:
        if transition.quarantine_cause_refs:
            _add(
                issues,
                "transition.quarantine_cause_refs",
                ConceptGovernanceValidationCode.QUARANTINE_CAUSE_REQUIRED,
                "quarantine causes are not permitted on a non-quarantine transition",
            )
        if transition.quarantine_release_requirement_refs:
            _add(
                issues,
                "transition.quarantine_release_requirement_refs",
                ConceptGovernanceValidationCode.QUARANTINE_RELEASE_REQUIREMENT_REQUIRED,
                "release requirements are not permitted on a non-quarantine transition",
            )

    if transition.transition_kind is ConceptLifecycleTransitionKind.RELEASE_FROM_QUARANTINE:
        if source.lifecycle_state is not ConceptLifecycleState.QUARANTINED:
            _add(
                issues,
                "transition.transition_kind",
                ConceptGovernanceValidationCode.TRANSITION_KIND_MISMATCH,
                "only a quarantined resource may be released",
            )
        if not transition.resolved_quarantine_cause_refs:
            _add(
                issues,
                "transition.resolved_quarantine_cause_refs",
                ConceptGovernanceValidationCode.QUARANTINE_CAUSE_UNRESOLVED,
                "release must identify resolved quarantine causes",
            )
    elif transition.resolved_quarantine_cause_refs:
        _add(
            issues,
            "transition.resolved_quarantine_cause_refs",
            ConceptGovernanceValidationCode.QUARANTINE_CAUSE_UNRESOLVED,
            "resolved causes are reserved for quarantine release",
        )

    if target.lifecycle_state is ConceptLifecycleState.REJECTED:
        if not transition.blocked_reentry_keys:
            _add(
                issues,
                "transition.blocked_reentry_keys",
                ConceptGovernanceValidationCode.BLOCKED_REENTRY_REQUIRED,
                "rejection must preserve materially equivalent blocked reentry keys",
            )
    elif transition.blocked_reentry_keys:
        _add(
            issues,
            "transition.blocked_reentry_keys",
            ConceptGovernanceValidationCode.BLOCKED_REENTRY_REQUIRED,
            "blocked reentry keys are reserved for a rejection record",
        )

    if target.lifecycle_state is ConceptLifecycleState.SUPERSEDED:
        if not transition.superseding_resource_ref:
            _add(
                issues,
                "transition.superseding_resource_ref",
                ConceptGovernanceValidationCode.SUPERSEDING_RESOURCE_REQUIRED,
                "supersession requires an explicit successor resource",
            )
    elif transition.transition_kind is not ConceptLifecycleTransitionKind.HISTORICAL_ONLY:
        if transition.superseding_resource_ref is not None:
            _add(
                issues,
                "transition.superseding_resource_ref",
                ConceptGovernanceValidationCode.SUPERSEDING_RESOURCE_INVALID,
                "a successor reference is reserved for supersession ancestry",
            )

    if transition.transition_kind is ConceptLifecycleTransitionKind.HISTORICAL_ONLY:
        if target.lifecycle_state is not ConceptLifecycleState.SUPERSEDED:
            _add(
                issues,
                "transition.to_state",
                ConceptGovernanceValidationCode.TRANSITION_KIND_MISMATCH,
                "historical-only disposition preserves superseded state",
            )
        if transition.historical_only_after_transition is not True:
            _add(
                issues,
                "transition.historical_only_after_transition",
                ConceptGovernanceValidationCode.HISTORICAL_ANCESTRY_REQUIRED,
                "historical-only transition must explicitly preserve historical status",
            )
    elif transition.historical_only_after_transition:
        _add(
            issues,
            "transition.historical_only_after_transition",
            ConceptGovernanceValidationCode.HISTORICAL_ANCESTRY_REQUIRED,
            "historical-only flag requires the matching transition kind",
        )

    if transition.transition_kind is ConceptLifecycleTransitionKind.REOPEN_REVIEW:
        if source.lifecycle_state is ConceptLifecycleState.REJECTED and not transition.prior_disposition_transition_ref:
            _add(
                issues,
                "transition.prior_disposition_transition_ref",
                ConceptGovernanceValidationCode.HISTORICAL_ANCESTRY_REQUIRED,
                "reopening rejected material must reference the prior rejection transition",
            )
    elif transition.prior_disposition_transition_ref is not None:
        _add(
            issues,
            "transition.prior_disposition_transition_ref",
            ConceptGovernanceValidationCode.HISTORICAL_ANCESTRY_REQUIRED,
            "prior disposition reference is reserved for an explicit reopening",
        )

    ordered = report_from_issues(issues).issues

    return ConceptLifecycleTransitionDecision(
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
    source: GovernedConceptResource,
    target: GovernedConceptResource,
    transition: ConceptLifecycleTransitionRecord,
    authority: ConceptLifecycleAuthorityRecord,
    *,
    provenance_by_id: dict[str, ConceptProvenanceReference],
) -> ConceptLifecycleTransitionDecision:
    decision = evaluate_lifecycle_transition(
        source,
        target,
        transition,
        authority,
        provenance_by_id=provenance_by_id,
    )
    if not decision.allowed:
        raise ConceptGovernanceValidationError(
            report_from_issues(list(decision.issues))
        )
    return decision
