"""Deterministic Slice 39B lifecycle transition evaluation."""

from __future__ import annotations

from .rules import lifecycle_transition_allowed
from .schema import (
    CandidateMeaningGovernanceBundle,
    CandidateMeaningLifecycleDecision,
    CandidateMeaningLifecycleRecord,
    CandidateMeaningLifecycleTransitionRecord,
    CandidateMeaningValidationCode,
    CandidateMeaningValidationIssue,
)
from .validation import (
    validate_lifecycle_record,
    validate_lifecycle_transition_record,
)


def _prefixed(
    prefix: str,
    issues: tuple[CandidateMeaningValidationIssue, ...],
) -> list[CandidateMeaningValidationIssue]:
    return [
        CandidateMeaningValidationIssue(
            path=f"{prefix}.{issue.path}",
            code=issue.code,
            detail=issue.detail,
        )
        for issue in issues
    ]


def evaluate_lifecycle_transition(
    source: CandidateMeaningLifecycleRecord,
    target: CandidateMeaningLifecycleRecord,
    transition: CandidateMeaningLifecycleTransitionRecord,
    *,
    bundle: CandidateMeaningGovernanceBundle | None = None,
) -> CandidateMeaningLifecycleDecision:
    """Evaluate one immutable transition without applying or persisting it."""

    issues: list[CandidateMeaningValidationIssue] = []
    issues.extend(
        _prefixed(
            "source",
            validate_lifecycle_record(source, bundle=bundle).issues,
        )
    )
    issues.extend(
        _prefixed(
            "target",
            validate_lifecycle_record(target, bundle=bundle).issues,
        )
    )
    issues.extend(
        _prefixed(
            "transition",
            validate_lifecycle_transition_record(transition).issues,
        )
    )

    if transition.source_lifecycle_record_id != source.lifecycle_record_id:
        issues.append(
            CandidateMeaningValidationIssue(
                path="transition.source_lifecycle_record_id",
                code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                detail="transition source reference does not match source record",
            )
        )
    if transition.target_lifecycle_record_id != target.lifecycle_record_id:
        issues.append(
            CandidateMeaningValidationIssue(
                path="transition.target_lifecycle_record_id",
                code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                detail="transition target reference does not match target record",
            )
        )
    if transition.candidate_meaning_id != source.candidate_meaning_id:
        issues.append(
            CandidateMeaningValidationIssue(
                path="transition.candidate_meaning_id",
                code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                detail="transition candidate identity does not match source",
            )
        )
    if target.candidate_meaning_id != source.candidate_meaning_id:
        issues.append(
            CandidateMeaningValidationIssue(
                path="target.candidate_meaning_id",
                code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                detail="target candidate identity does not match source",
            )
        )
    if transition.from_stage is not source.stage:
        issues.append(
            CandidateMeaningValidationIssue(
                path="transition.from_stage",
                code=CandidateMeaningValidationCode.LIFECYCLE_STAGE_INVALID,
                detail="from_stage does not match source lifecycle stage",
            )
        )
    if transition.to_stage is not target.stage:
        issues.append(
            CandidateMeaningValidationIssue(
                path="transition.to_stage",
                code=CandidateMeaningValidationCode.LIFECYCLE_STAGE_INVALID,
                detail="to_stage does not match target lifecycle stage",
            )
        )
    if not lifecycle_transition_allowed(
        source.stage,
        target.stage,
        transition.transition_kind,
    ):
        issues.append(
            CandidateMeaningValidationIssue(
                path="transition.transition_kind",
                code=CandidateMeaningValidationCode.LIFECYCLE_TRANSITION_NOT_PERMITTED,
                detail="closed lifecycle matrix rejects this progression",
            )
        )
    if target.predecessor_lifecycle_record_ids != (
        source.lifecycle_record_id,
    ):
        issues.append(
            CandidateMeaningValidationIssue(
                path="target.predecessor_lifecycle_record_ids",
                code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                detail="target must preserve exact source lifecycle ancestry",
            )
        )
    if transition.version_custody_ref != source.version_custody_ref:
        issues.append(
            CandidateMeaningValidationIssue(
                path="transition.version_custody_ref",
                code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                detail="transition custody reference does not match source",
            )
        )
    if target.version_custody_ref != source.version_custody_ref:
        issues.append(
            CandidateMeaningValidationIssue(
                path="target.version_custody_ref",
                code=CandidateMeaningValidationCode.CROSS_RECORD_IDENTITY_MISMATCH,
                detail="target custody reference does not match source",
            )
        )

    return CandidateMeaningLifecycleDecision(
        allowed=not issues,
        issues=tuple(issues),
        candidate_meaning_id=transition.candidate_meaning_id,
        source_lifecycle_record_id=source.lifecycle_record_id,
        target_lifecycle_record_id=target.lifecycle_record_id,
        transition_id=transition.transition_id,
        from_stage=transition.from_stage,
        to_stage=transition.to_stage,
        transition_kind=transition.transition_kind,
    )


def assert_lifecycle_transition(
    source: CandidateMeaningLifecycleRecord,
    target: CandidateMeaningLifecycleRecord,
    transition: CandidateMeaningLifecycleTransitionRecord,
    *,
    bundle: CandidateMeaningGovernanceBundle | None = None,
) -> CandidateMeaningLifecycleTransitionRecord:
    decision = evaluate_lifecycle_transition(
        source,
        target,
        transition,
        bundle=bundle,
    )
    if not decision.allowed:
        summary = "; ".join(
            f"{item.path}:{item.code.value}:{item.detail}"
            for item in decision.issues
        )
        raise ValueError(summary or "Slice 39B lifecycle transition rejected")
    return transition


__all__ = (
    "assert_lifecycle_transition",
    "evaluate_lifecycle_transition",
)
