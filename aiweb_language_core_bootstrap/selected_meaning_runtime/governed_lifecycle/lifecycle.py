"""Explicit immutable Slice 41B lifecycle transition evaluation."""

from __future__ import annotations

from .rules import lifecycle_transition_allowed
from .schema import (
    SelectedMeaningGovernanceBundle,
    SelectedMeaningLifecycleDecision,
    SelectedMeaningLifecycleRecord,
    SelectedMeaningLifecycleStage,
    SelectedMeaningLifecycleTransitionRecord,
    SelectedMeaningValidationCode,
    SelectedMeaningValidationError,
    SelectedMeaningValidationIssue,
    SelectedMeaningValidationReport,
)


def _issue(
    path: str,
    code: SelectedMeaningValidationCode,
    detail: str,
) -> SelectedMeaningValidationIssue:
    return SelectedMeaningValidationIssue(path=path, code=code, detail=detail)


def evaluate_lifecycle_transition(
    source: SelectedMeaningLifecycleRecord,
    target: SelectedMeaningLifecycleRecord,
    transition: SelectedMeaningLifecycleTransitionRecord,
    *,
    bundle: SelectedMeaningGovernanceBundle | None = None,
) -> SelectedMeaningLifecycleDecision:
    """Evaluate one explicit transition without semantic or action authority."""

    from .validation import (
        validate_lifecycle_record,
        validate_lifecycle_transition_record,
    )

    issues = list(validate_lifecycle_record(source).issues)
    issues.extend(validate_lifecycle_record(target).issues)
    issues.extend(validate_lifecycle_transition_record(transition).issues)

    if source.runtime_schema_record_id != target.runtime_schema_record_id:
        issues.append(
            _issue(
                "target.runtime_schema_record_id",
                SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "source and target must govern the same runtime schema record",
            )
        )
    if transition.runtime_schema_record_id != source.runtime_schema_record_id:
        issues.append(
            _issue(
                "transition.runtime_schema_record_id",
                SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "transition must govern the source runtime record",
            )
        )
    if transition.source_lifecycle_record_id != source.lifecycle_record_id:
        issues.append(
            _issue(
                "transition.source_lifecycle_record_id",
                SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "transition source reference does not match source record",
            )
        )
    if transition.target_lifecycle_record_id != target.lifecycle_record_id:
        issues.append(
            _issue(
                "transition.target_lifecycle_record_id",
                SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "transition target reference does not match target record",
            )
        )
    if transition.from_stage is not source.stage:
        issues.append(
            _issue(
                "transition.from_stage",
                SelectedMeaningValidationCode.LIFECYCLE_STAGE_INVALID,
                "transition from-stage does not match source",
            )
        )
    if transition.to_stage is not target.stage:
        issues.append(
            _issue(
                "transition.to_stage",
                SelectedMeaningValidationCode.LIFECYCLE_STAGE_INVALID,
                "transition to-stage does not match target",
            )
        )
    if transition.version_custody_ref != source.version_custody_ref:
        issues.append(
            _issue(
                "transition.version_custody_ref",
                SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "transition version custody must match source",
            )
        )
    if target.version_custody_ref != source.version_custody_ref:
        issues.append(
            _issue(
                "target.version_custody_ref",
                SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                "a lifecycle transition cannot silently change version custody",
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
                SelectedMeaningValidationCode.LIFECYCLE_TRANSITION_NOT_PERMITTED,
                (
                    f"{source.stage.value}->{target.stage.value} is not "
                    f"permitted for {transition.transition_kind.value}"
                ),
            )
        )

    if target.stage is not SelectedMeaningLifecycleStage.SCHEMA_DECLARED:
        if source.lifecycle_record_id not in target.predecessor_lifecycle_record_ids:
            issues.append(
                _issue(
                    "target.predecessor_lifecycle_record_ids",
                    SelectedMeaningValidationCode.PREDECESSOR_REFERENCE_MISSING,
                    "target must preserve the immediate source lifecycle record",
                )
            )

    if bundle is not None:
        runtime_id = bundle.runtime_schema_record.selected_meaning_runtime_schema_record_id
        if runtime_id != source.runtime_schema_record_id:
            issues.append(
                _issue(
                    "bundle.runtime_schema_record",
                    SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                    "bundle runtime record does not match transition chain",
                )
            )
        if bundle.version_custody.custody_id != source.version_custody_ref:
            issues.append(
                _issue(
                    "bundle.version_custody.custody_id",
                    SelectedMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                    "bundle version custody does not match transition chain",
                )
            )

    ordered = tuple(
        sorted(issues, key=lambda item: (item.path, item.code.value, item.detail))
    )
    return SelectedMeaningLifecycleDecision(
        allowed=not ordered,
        issues=ordered,
        runtime_schema_record_id=transition.runtime_schema_record_id,
        source_lifecycle_record_id=source.lifecycle_record_id,
        target_lifecycle_record_id=target.lifecycle_record_id,
        transition_id=transition.transition_id,
        from_stage=transition.from_stage,
        to_stage=transition.to_stage,
        transition_kind=transition.transition_kind,
    )


def assert_lifecycle_transition(
    source: SelectedMeaningLifecycleRecord,
    target: SelectedMeaningLifecycleRecord,
    transition: SelectedMeaningLifecycleTransitionRecord,
    *,
    bundle: SelectedMeaningGovernanceBundle | None = None,
) -> SelectedMeaningLifecycleTransitionRecord:
    decision = evaluate_lifecycle_transition(
        source,
        target,
        transition,
        bundle=bundle,
    )
    if not decision.allowed:
        raise SelectedMeaningValidationError(
            SelectedMeaningValidationReport(issues=decision.issues)
        )
    return transition


__all__ = (
    "assert_lifecycle_transition",
    "evaluate_lifecycle_transition",
)
