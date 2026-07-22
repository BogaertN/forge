"""Closed deterministic Slice 43F Echo disposition rules."""

from __future__ import annotations

from ..schema import EchoDisposition
from ..drift_materiality_classification import (
    DriftClassificationPackage,
    DriftClassificationState,
    DriftKind,
    MaterialityState,
)
from .authority import (
    CONTAINMENT_LAW_REF_MAP,
    DETERMINISTIC_ECHO_LAW_VIOLATION_DRIFT_KIND_VALUES,
    DISPOSITION_LAW_REF_MAP,
    PRECEDENCE_RULE_REF,
    REJECTION_LAW_REF_MAP,
)
from .schema import (
    EchoDispositionCode,
    EchoDispositionExecutionStatus,
    EchoDispositionState,
)


def unique_values(*groups: tuple[str, ...]) -> tuple[str, ...]:
    values: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for value in group:
            if value not in seen:
                seen.add(value)
                values.append(value)
    return tuple(values)


def ordered_drift_kinds(values: set[DriftKind]) -> tuple[DriftKind, ...]:
    order = {
        value: index
        for index, value in enumerate(
            item.value for item in DriftKind
        )
    }
    return tuple(sorted(values, key=lambda item: order[item.value]))


def finding_refs_for_materiality(
    package: DriftClassificationPackage,
    materiality: MaterialityState,
) -> tuple[str, ...]:
    return tuple(
        item.drift_finding_id
        for item in package.drift_findings
        if item.materiality is materiality
    )


def material_violation_finding_refs(
    package: DriftClassificationPackage,
) -> tuple[str, ...]:
    registry = set(DETERMINISTIC_ECHO_LAW_VIOLATION_DRIFT_KIND_VALUES)
    return tuple(
        item.drift_finding_id
        for item in package.drift_findings
        if (
            item.materiality is MaterialityState.MATERIAL
            and any(kind.value in registry for kind in item.drift_kinds)
        )
    )


def incomplete_authority_finding_refs(
    package: DriftClassificationPackage,
) -> tuple[str, ...]:
    incomplete = {
        MaterialityState.UNSUPPORTED,
        MaterialityState.CONFLICTED,
        MaterialityState.INDETERMINATE,
    }
    return tuple(
        item.drift_finding_id
        for item in package.drift_findings
        if item.materiality in incomplete
    )


def retained_drift_kinds(
    package: DriftClassificationPackage,
) -> tuple[DriftKind, ...]:
    values: set[DriftKind] = set()
    for finding in package.drift_findings:
        values.update(finding.drift_kinds)
    return ordered_drift_kinds(values)


def preserved_ancestry_refs(
    package: DriftClassificationPackage,
) -> tuple[str, ...]:
    groups: list[tuple[str, ...]] = [
        (
            package.classification_request_ref,
            package.comparison_result_ref,
            package.comparison_package_ref,
        )
    ]
    for finding in package.drift_findings:
        groups.extend(
            (
                (
                    finding.drift_finding_id,
                    finding.comparison_finding_ref,
                    finding.source_snapshot_ref,
                    finding.proposed_snapshot_ref,
                ),
                finding.comparison_evidence_refs,
                finding.comparison_trace_refs,
                finding.materiality_ground_refs,
                finding.ancestry_mismatch_refs,
            )
        )
    return unique_values(*groups)


def decide_disposition(
    package: DriftClassificationPackage,
) -> tuple[
    EchoDisposition,
    EchoDispositionState,
    tuple[str, ...],
    tuple[str, ...],
    bool,
    bool,
    bool,
    bool,
]:
    """Return deterministic disposition and exact ground summaries.

    Incomplete authority takes precedence over rejection. This prevents a known
    material violation from erasing a separate unsupported, conflicted or
    indeterminate finding. When no incomplete authority remains, exact material
    Echo-law violations reject. Only the absence of both allows PASSED.
    """

    violation_refs = material_violation_finding_refs(package)
    incomplete_refs = incomplete_authority_finding_refs(package)
    coexistence = bool(violation_refs and incomplete_refs)

    if incomplete_refs:
        return (
            EchoDisposition.CONTAINED,
            EchoDispositionState.INCOMPLETE_AUTHORITY_CONTAINED,
            violation_refs,
            incomplete_refs,
            False,
            bool(violation_refs),
            True,
            coexistence,
        )
    if violation_refs:
        return (
            EchoDisposition.REJECTED,
            EchoDispositionState.DETERMINISTIC_ECHO_LAW_VIOLATION,
            violation_refs,
            (),
            False,
            True,
            False,
            False,
        )
    return (
        EchoDisposition.PASSED,
        EchoDispositionState.ALL_MATERIAL_OBLIGATIONS_PASS,
        (),
        (),
        True,
        False,
        False,
        False,
    )


def rejection_law_refs(
    package: DriftClassificationPackage,
    violation_refs: tuple[str, ...],
) -> tuple[str, ...]:
    selected = set(violation_refs)
    kinds: set[DriftKind] = set()
    for finding in package.drift_findings:
        if finding.drift_finding_id in selected:
            kinds.update(
                kind
                for kind in finding.drift_kinds
                if kind.value in REJECTION_LAW_REF_MAP
            )
    return tuple(
        REJECTION_LAW_REF_MAP[kind.value]
        for kind in ordered_drift_kinds(kinds)
    )


def containment_law_refs(
    package: DriftClassificationPackage,
    incomplete_refs: tuple[str, ...],
    *,
    coexistence: bool,
) -> tuple[str, ...]:
    selected = set(incomplete_refs)
    states: list[str] = []
    for value in ("unsupported", "conflicted", "indeterminate"):
        if any(
            item.drift_finding_id in selected
            and item.materiality.value == value
            for item in package.drift_findings
        ):
            states.append(value)
    refs = tuple(CONTAINMENT_LAW_REF_MAP[value] for value in states)
    if coexistence:
        refs += (PRECEDENCE_RULE_REF,)
    return refs


def disposition_law_refs(disposition: EchoDisposition) -> tuple[str, ...]:
    return (DISPOSITION_LAW_REF_MAP[disposition.value],)


def blocking_materiality_states(
    package: DriftClassificationPackage,
    incomplete_refs: tuple[str, ...],
) -> tuple[MaterialityState, ...]:
    selected = set(incomplete_refs)
    order = (
        MaterialityState.UNSUPPORTED,
        MaterialityState.CONFLICTED,
        MaterialityState.INDETERMINATE,
    )
    present = {
        item.materiality
        for item in package.drift_findings
        if item.drift_finding_id in selected
    }
    return tuple(value for value in order if value in present)


_STATUS_PRIORITY = (
    EchoDispositionCode.RAW_TEXT_PROHIBITED,
    EchoDispositionCode.REQUEST_TYPE_INVALID,
    EchoDispositionCode.REQUEST_ID_INVALID,
    EchoDispositionCode.REQUEST_OPERATION_INVALID,
    EchoDispositionCode.EXPLICIT_REQUEST_REQUIRED,
    EchoDispositionCode.CLASSIFICATION_RESULT_TYPE_INVALID,
    EchoDispositionCode.CLASSIFICATION_NOT_READY,
    EchoDispositionCode.CLASSIFICATION_PACKAGE_MISSING,
    EchoDispositionCode.UNSUPPORTED_VERSION,
    EchoDispositionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
    EchoDispositionCode.INCONSISTENT_ANCESTRY,
    EchoDispositionCode.MISSING_REQUIRED_VALUE,
    EchoDispositionCode.CLASSIFICATION_RESULT_INVALID,
    EchoDispositionCode.CLASSIFICATION_FINDING_INVALID,
)

_STATUS_BY_CODE = {
    EchoDispositionCode.CLASSIFICATION_RESULT_TYPE_INVALID:
        EchoDispositionExecutionStatus.HELD_CLASSIFICATION_NOT_READY,
    EchoDispositionCode.CLASSIFICATION_NOT_READY:
        EchoDispositionExecutionStatus.HELD_CLASSIFICATION_NOT_READY,
    EchoDispositionCode.CLASSIFICATION_PACKAGE_MISSING:
        EchoDispositionExecutionStatus.HELD_CLASSIFICATION_NOT_READY,
    EchoDispositionCode.UNSUPPORTED_VERSION:
        EchoDispositionExecutionStatus.HELD_UNSUPPORTED_VERSION,
    EchoDispositionCode.RECOMPUTED_OR_FABRICATED_IDENTITY:
        EchoDispositionExecutionStatus.HELD_IDENTITY_INVALID,
    EchoDispositionCode.INCONSISTENT_ANCESTRY:
        EchoDispositionExecutionStatus.HELD_INCONSISTENT_ANCESTRY,
    EchoDispositionCode.MISSING_REQUIRED_VALUE:
        EchoDispositionExecutionStatus.HELD_MISSING_REQUIRED_VALUE,
}


def status_for_codes(
    codes: tuple[EchoDispositionCode, ...],
) -> EchoDispositionExecutionStatus:
    code_set = set(codes)
    for code in _STATUS_PRIORITY:
        if code in code_set:
            return _STATUS_BY_CODE.get(
                code,
                EchoDispositionExecutionStatus.HELD_INVALID_REQUEST,
            )
    return EchoDispositionExecutionStatus.HELD_INVALID_REQUEST


__all__ = (
    "blocking_materiality_states",
    "containment_law_refs",
    "decide_disposition",
    "disposition_law_refs",
    "finding_refs_for_materiality",
    "incomplete_authority_finding_refs",
    "material_violation_finding_refs",
    "ordered_drift_kinds",
    "preserved_ancestry_refs",
    "rejection_law_refs",
    "retained_drift_kinds",
    "status_for_codes",
    "unique_values",
)
