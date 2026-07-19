"""Fail-closed Slice 40B lifecycle evaluation for validation custody only."""

from __future__ import annotations

from .rules import lifecycle_transition_allowed
from .schema import (
    GateGovernanceBundle,
    GateLifecycleDecision,
    GateLifecycleRecord,
    GateLifecycleTransitionRecord,
    GateValidationCode,
    GateValidationError,
    GateValidationIssue,
    GateValidationReport,
)


def _issue(
    path: str,
    code: GateValidationCode,
    detail: str,
) -> GateValidationIssue:
    return GateValidationIssue(path=path, code=code, detail=detail)


def evaluate_lifecycle_transition(
    source: GateLifecycleRecord,
    target: GateLifecycleRecord,
    transition: GateLifecycleTransitionRecord,
    *,
    bundle: GateGovernanceBundle | None = None,
) -> GateLifecycleDecision:
    """Evaluate an explicit immutable validation-custody transition.

    This function does not evaluate expectancy, congruity, connectedness, or
    recoverable purpose and cannot create any gate outcome.
    """

    from .validation import (
        validate_lifecycle_record,
        validate_lifecycle_transition_record,
    )

    issues = list(validate_lifecycle_record(source).issues)
    issues.extend(validate_lifecycle_record(target).issues)
    issues.extend(validate_lifecycle_transition_record(transition).issues)

    if source.review_record_id != target.review_record_id:
        issues.append(
            _issue(
                "target.review_record_id",
                GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "source and target must govern the same review record",
            )
        )
    if transition.review_record_id != source.review_record_id:
        issues.append(
            _issue(
                "transition.review_record_id",
                GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "transition must govern the source review record",
            )
        )
    if transition.source_lifecycle_record_id != source.lifecycle_record_id:
        issues.append(
            _issue(
                "transition.source_lifecycle_record_id",
                GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "transition source reference does not match source record",
            )
        )
    if transition.target_lifecycle_record_id != target.lifecycle_record_id:
        issues.append(
            _issue(
                "transition.target_lifecycle_record_id",
                GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "transition target reference does not match target record",
            )
        )
    if transition.from_stage is not source.stage:
        issues.append(
            _issue(
                "transition.from_stage",
                GateValidationCode.LIFECYCLE_STAGE_INVALID,
                "transition from-stage does not match source",
            )
        )
    if transition.to_stage is not target.stage:
        issues.append(
            _issue(
                "transition.to_stage",
                GateValidationCode.LIFECYCLE_STAGE_INVALID,
                "transition to-stage does not match target",
            )
        )
    if transition.version_custody_ref != source.version_custody_ref:
        issues.append(
            _issue(
                "transition.version_custody_ref",
                GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "transition version custody must match source",
            )
        )
    if target.version_custody_ref != source.version_custody_ref:
        issues.append(
            _issue(
                "target.version_custody_ref",
                GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "a transition cannot silently change version custody",
            )
        )
    if not lifecycle_transition_allowed(
        source.stage,
        target.stage,
        transition.transition_kind,
    ):
        issues.append(
            _issue(
                "transition.transition_kind",
                GateValidationCode.LIFECYCLE_TRANSITION_NOT_PERMITTED,
                (
                    f"{source.stage.value}->{target.stage.value} is not "
                    f"permitted for {transition.transition_kind.value}"
                ),
            )
        )

    if target.stage.value != "schema_declared":
        if source.lifecycle_record_id not in target.predecessor_lifecycle_record_ids:
            issues.append(
                _issue(
                    "target.predecessor_lifecycle_record_ids",
                    GateValidationCode.REFERENCE_NOT_FOUND,
                    "target must preserve the immediate source as ancestry",
                )
            )

    if bundle is not None:
        if bundle.review_record.review_record_id != source.review_record_id:
            issues.append(
                _issue(
                    "bundle.review_record.review_record_id",
                    GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                    "bundle review record does not match transition chain",
                )
            )
        if bundle.version_custody.custody_id != source.version_custody_ref:
            issues.append(
                _issue(
                    "bundle.version_custody.custody_id",
                    GateValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                    "bundle version custody does not match transition chain",
                )
            )

    ordered = tuple(
        sorted(
            issues,
            key=lambda item: (item.path, item.code.value, item.detail),
        )
    )
    return GateLifecycleDecision(
        allowed=not ordered,
        issues=ordered,
        review_record_id=transition.review_record_id,
        source_lifecycle_record_id=source.lifecycle_record_id,
        target_lifecycle_record_id=target.lifecycle_record_id,
        transition_id=transition.transition_id,
        from_stage=transition.from_stage,
        to_stage=transition.to_stage,
        transition_kind=transition.transition_kind,
    )


def assert_lifecycle_transition(
    source: GateLifecycleRecord,
    target: GateLifecycleRecord,
    transition: GateLifecycleTransitionRecord,
    *,
    bundle: GateGovernanceBundle | None = None,
) -> GateLifecycleTransitionRecord:
    decision = evaluate_lifecycle_transition(
        source,
        target,
        transition,
        bundle=bundle,
    )
    if not decision.allowed:
        raise GateValidationError(
            GateValidationReport(issues=decision.issues)
        )
    return transition


__all__ = (
    "assert_lifecycle_transition",
    "evaluate_lifecycle_transition",
)
