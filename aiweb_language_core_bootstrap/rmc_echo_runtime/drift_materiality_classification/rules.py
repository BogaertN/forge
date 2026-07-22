"""Closed deterministic Slice 43E drift and materiality rules."""

from __future__ import annotations

import re

from .authority import (
    CLASSIFICATION_RULE_REF_MAP,
    CONTROLLED_NON_MATERIAL_SURFACE_PREFIXES,
    DRIFT_KIND_VALUES,
    MATERIAL_DRIFT_KIND_VALUES,
    MATERIALITY_RULE_REF_MAP,
)
from .schema import (
    DriftClassificationCode,
    DriftClassificationExecutionStatus,
    DriftClassificationState,
    DriftKind,
    MaterialityState,
)
from ..meaning_preservation_comparison import (
    FindingOutcome,
    MeaningPreservationDimension,
    MeaningPreservationFinding,
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
    order = {value: index for index, value in enumerate(DRIFT_KIND_VALUES)}
    return tuple(sorted(values, key=lambda item: order[item.value]))


def _missing_and_added(
    source_values: tuple[str, ...],
    proposed_values: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    proposed_set = set(proposed_values)
    source_set = set(source_values)
    missing = tuple(value for value in source_values if value not in proposed_set)
    added = tuple(value for value in proposed_values if value not in source_set)
    return missing, added


def _normalized_words(value: str) -> str:
    return " " + re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip() + " "


def _contains(values: tuple[str, ...], markers: tuple[str, ...]) -> bool:
    normalized_values = tuple(_normalized_words(value) for value in values)
    normalized_markers = tuple(
        _normalized_words(marker).strip() for marker in markers
    )
    return any(
        f" {marker} " in value
        for value in normalized_values
        for marker in normalized_markers
    )


def _fact_values(values: tuple[str, ...]) -> tuple[str, ...]:
    markers = (
        "fact:",
        "claim:fact",
        "assertion:",
        "truth_status:",
        "invented_fact",
    )
    return tuple(value for value in values if _contains((value,), markers))


def _evidence_values(values: tuple[str, ...]) -> tuple[str, ...]:
    markers = (
        "evidence:",
        "evidence_ref:",
        "verified_source:",
        "citation:",
        "proof:",
        "invented_evidence",
    )
    return tuple(value for value in values if _contains((value,), markers))


def _authority_values(values: tuple[str, ...]) -> tuple[str, ...]:
    markers = (
        "authorized",
        "permission_granted",
        "execution_authorized",
        "executed",
        "performed",
        "installed",
        "delivered",
        "sent",
        "memory_written",
        "memory_accessed",
        "approved",
        "validated",
        "proceed",
    )
    return tuple(value for value in values if _contains((value,), markers))


def _rank(values: tuple[str, ...], levels: tuple[tuple[str, ...], ...]) -> int:
    rank = -1
    for index, markers in enumerate(levels):
        if _contains(values, markers):
            rank = max(rank, index)
    return rank


def _claim_rank(values: tuple[str, ...]) -> int:
    return _rank(
        values,
        (
            (
                "nonaffirmative",
                "blocked",
                "unvalidated",
                "not_authorized",
                "proposal",
                "draft",
            ),
            ("qualified", "conditional", "supported"),
            ("affirmative", "validated", "approved", "verified", "fact"),
        ),
    )


def _certainty_rank(values: tuple[str, ...]) -> int:
    return _rank(
        values,
        (
            ("unknown", "uncertain", "indeterminate", "unresolved"),
            ("possible", "tentative", "conditional"),
            ("probable", "confident"),
            ("certain", "definitive", "confirmed"),
        ),
    )


def _evidence_rank(values: tuple[str, ...]) -> int:
    return _rank(
        values,
        (
            ("no_evidence", "unverified", "unsupported", "unknown"),
            ("referenced", "reported", "claimed"),
            ("supported", "corroborated"),
            ("verified", "validated", "proven"),
        ),
    )


def _refusal_rank(values: tuple[str, ...]) -> int:
    return _rank(
        values,
        (
            ("allowed", "authorized", "permission", "proceed"),
            ("conditional", "qualified"),
            ("held", "deferred", "pending"),
            (
                "refusal",
                "refused",
                "blocked",
                "prohibited",
                "not_authorized",
                "not_performed",
                "denied",
            ),
        ),
    )


def _ambiguity_values(values: tuple[str, ...]) -> tuple[str, ...]:
    markers = ("ambigu", "alternative", "multiple_candidate")
    return tuple(value for value in values if _contains((value,), markers))


def _unresolved_values(values: tuple[str, ...]) -> tuple[str, ...]:
    markers = (
        "unresolved",
        "unknown",
        "unsupported",
        "indeterminate",
        "held",
        "deferred",
        "pending",
        "required_next_step",
        "hold",
    )
    return tuple(value for value in values if _contains((value,), markers))


def _controlled_non_material_additions(values: tuple[str, ...]) -> bool:
    return bool(values) and all(
        any(value.startswith(prefix) for prefix in CONTROLLED_NON_MATERIAL_SURFACE_PREFIXES)
        for value in values
    )


def classify_finding(
    finding: MeaningPreservationFinding,
) -> tuple[
    DriftClassificationState,
    tuple[DriftKind, ...],
    MaterialityState,
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
]:
    """Return state, kinds, materiality, rules, grounds and ancestry mismatches."""

    source = finding.source_snapshot
    proposed = finding.proposed_snapshot
    missing, added = _missing_and_added(source.values, proposed.values)
    kinds: set[DriftKind] = set()
    grounds: list[str] = []
    ancestry_mismatches: list[str] = []

    if source.trace_refs != proposed.trace_refs:
        kinds.add(DriftKind.ANCESTRY_MISMATCH)
        ancestry_mismatches.extend(
            value
            for value in unique_values(source.trace_refs, proposed.trace_refs)
        )
        grounds.append("slice43e-ground:source-proposed-trace-custody-mismatch")

    if source.evidence_refs != proposed.evidence_refs:
        kinds.add(DriftKind.ANCESTRY_MISMATCH)
        ancestry_mismatches.extend(
            value
            for value in unique_values(source.evidence_refs, proposed.evidence_refs)
        )
        grounds.append("slice43e-ground:source-proposed-evidence-custody-mismatch")

    outcome = finding.outcome
    dimension = finding.dimension

    if outcome is FindingOutcome.PRESERVED and not kinds:
        return (
            DriftClassificationState.NO_DRIFT,
            (),
            MaterialityState.NOT_APPLICABLE,
            (),
            ("slice43e-ground:exact-comparison-finding-preserved",),
            (),
        )
    if outcome is FindingOutcome.UNSUPPORTED and not kinds:
        return (
            DriftClassificationState.CLASSIFICATION_UNSUPPORTED,
            (),
            MaterialityState.UNSUPPORTED,
            (),
            ("slice43e-ground:comparison-finding-unsupported",),
            (),
        )
    if outcome is FindingOutcome.CONFLICTED and not kinds:
        return (
            DriftClassificationState.CLASSIFICATION_CONFLICTED,
            (),
            MaterialityState.CONFLICTED,
            (),
            ("slice43e-ground:comparison-finding-conflicted",),
            (),
        )
    if outcome is FindingOutcome.INDETERMINATE and not kinds:
        return (
            DriftClassificationState.CLASSIFICATION_INDETERMINATE,
            (),
            MaterialityState.INDETERMINATE,
            (),
            ("slice43e-ground:comparison-finding-indeterminate",),
            (),
        )

    if missing:
        grounds.extend(f"slice43e-ground:missing:{value}" for value in missing)
    if added:
        grounds.extend(f"slice43e-ground:added:{value}" for value in added)

    if dimension is MeaningPreservationDimension.SEMANTIC_CONTENT:
        if missing:
            kinds.add(DriftKind.OMITTED_MEANING)
        if added:
            kinds.add(DriftKind.UNSUPPORTED_SURFACE_ADDITION)
        if _fact_values(added):
            kinds.add(DriftKind.INVENTED_FACT)
        if _evidence_values(added):
            kinds.add(DriftKind.INVENTED_EVIDENCE)

    elif dimension is MeaningPreservationDimension.COMMUNICATIVE_PURPOSE:
        if missing:
            kinds.add(DriftKind.OMITTED_MEANING)
        if added:
            kinds.add(DriftKind.UNSUPPORTED_SURFACE_ADDITION)
        if _authority_values(added):
            kinds.add(DriftKind.AUTHORITY_ESCALATION)

    elif dimension is MeaningPreservationDimension.CLAIM_STATUS:
        if missing:
            kinds.add(DriftKind.OMITTED_MEANING)
        if _claim_rank(proposed.values) > _claim_rank(source.values):
            kinds.add(DriftKind.CLAIM_STRENGTHENING)
        if _fact_values(added):
            kinds.add(DriftKind.INVENTED_FACT)
        if _evidence_values(added):
            kinds.add(DriftKind.INVENTED_EVIDENCE)
        if _authority_values(added):
            kinds.add(DriftKind.AUTHORITY_ESCALATION)
        if added and not kinds.intersection({
            DriftKind.CLAIM_STRENGTHENING,
            DriftKind.INVENTED_FACT,
            DriftKind.INVENTED_EVIDENCE,
            DriftKind.AUTHORITY_ESCALATION,
        }):
            kinds.add(DriftKind.UNSUPPORTED_SURFACE_ADDITION)

    elif dimension is MeaningPreservationDimension.SCOPE:
        if missing:
            kinds.add(DriftKind.OMITTED_MEANING)
        if added:
            kinds.add(DriftKind.SCOPE_EXPANSION)

    elif dimension is MeaningPreservationDimension.CERTAINTY:
        if missing:
            kinds.add(DriftKind.OMITTED_MEANING)
        if _certainty_rank(proposed.values) > _certainty_rank(source.values):
            kinds.add(DriftKind.CERTAINTY_UPGRADE)
        elif added:
            kinds.add(DriftKind.UNSUPPORTED_SURFACE_ADDITION)

    elif dimension is MeaningPreservationDimension.EVIDENCE_STATUS:
        if missing:
            kinds.add(DriftKind.OMITTED_MEANING)
        if _evidence_rank(proposed.values) > _evidence_rank(source.values):
            kinds.add(DriftKind.EVIDENCE_STATUS_UPGRADE)
        if _evidence_values(added):
            kinds.add(DriftKind.INVENTED_EVIDENCE)
        elif added:
            kinds.add(DriftKind.UNSUPPORTED_SURFACE_ADDITION)

    elif dimension is MeaningPreservationDimension.CAVEATS_AND_LIMITATIONS:
        if missing:
            kinds.add(DriftKind.CAVEAT_OMISSION)
        if added:
            kinds.add(DriftKind.UNSUPPORTED_SURFACE_ADDITION)

    elif dimension is MeaningPreservationDimension.REFUSAL_STATE:
        if missing or _refusal_rank(proposed.values) < _refusal_rank(source.values):
            kinds.add(DriftKind.REFUSAL_SOFTENING)
        if _authority_values(added):
            kinds.add(DriftKind.AUTHORITY_ESCALATION)
        elif added:
            kinds.add(DriftKind.UNSUPPORTED_SURFACE_ADDITION)

    elif dimension is MeaningPreservationDimension.UNRESOLVED_CONDITIONS:
        missing_ambiguity = _ambiguity_values(missing)
        missing_unresolved = _unresolved_values(missing)
        if missing_ambiguity:
            kinds.add(DriftKind.AMBIGUITY_ERASURE)
        if missing_unresolved:
            kinds.add(DriftKind.UNRESOLVED_STATE_ERASURE)
        if _contains(added, ("resolved", "no_ambiguity", "complete", "cleared")):
            kinds.add(DriftKind.UNRESOLVED_STATE_ERASURE)
        elif added:
            kinds.add(DriftKind.UNSUPPORTED_SURFACE_ADDITION)

    elif dimension is MeaningPreservationDimension.ACTION_STATUS:
        if missing or added:
            kinds.add(DriftKind.ACTION_STATUS_DISTORTION)
        if _authority_values(added):
            kinds.add(DriftKind.AUTHORITY_ESCALATION)

    elif dimension is MeaningPreservationDimension.MEMORY_STATUS:
        if missing or added:
            kinds.add(DriftKind.MEMORY_STATUS_DISTORTION)
        if _authority_values(added):
            kinds.add(DriftKind.AUTHORITY_ESCALATION)

    elif dimension is MeaningPreservationDimension.DELIVERY_STATUS:
        if missing or added:
            kinds.add(DriftKind.DELIVERY_STATUS_DISTORTION)
        if _authority_values(added):
            kinds.add(DriftKind.AUTHORITY_ESCALATION)

    elif dimension is MeaningPreservationDimension.REQUIRED_NEXT_STEP_OR_HOLD_STATUS:
        if missing and _unresolved_values(missing):
            kinds.add(DriftKind.UNRESOLVED_STATE_ERASURE)
        elif missing:
            kinds.add(DriftKind.OMITTED_MEANING)
        if _authority_values(added):
            kinds.add(DriftKind.AUTHORITY_ESCALATION)
        elif added:
            kinds.add(DriftKind.UNSUPPORTED_SURFACE_ADDITION)

    if outcome in (FindingOutcome.CHANGED, FindingOutcome.MISSING) and not kinds:
        if missing:
            kinds.add(DriftKind.OMITTED_MEANING)
        elif added:
            kinds.add(DriftKind.UNSUPPORTED_SURFACE_ADDITION)

    ordered = ordered_drift_kinds(kinds)
    classification_rules = tuple(
        CLASSIFICATION_RULE_REF_MAP[item.value] for item in ordered
    )

    if not ordered:
        state = DriftClassificationState.CLASSIFICATION_INDETERMINATE
        materiality = MaterialityState.INDETERMINATE
        grounds.append("slice43e-ground:no-admitted-drift-kind-determinable")
    else:
        state = DriftClassificationState.DRIFT_CLASSIFIED
        material_values = set(MATERIAL_DRIFT_KIND_VALUES)
        if any(item.value in material_values for item in ordered):
            materiality = MaterialityState.MATERIAL
            grounds.append("slice43e-ground:admitted-material-drift-kind")
        elif (
            set(ordered) == {DriftKind.UNSUPPORTED_SURFACE_ADDITION}
            and _controlled_non_material_additions(added)
        ):
            materiality = MaterialityState.NON_MATERIAL
            grounds.append("slice43e-ground:controlled-non-material-surface-only")
        else:
            materiality = MaterialityState.INDETERMINATE
            grounds.append("slice43e-ground:surface-addition-materiality-indeterminate")

    return (
        state,
        ordered,
        materiality,
        classification_rules,
        unique_values(tuple(grounds)),
        unique_values(tuple(ancestry_mismatches)),
    )


_STATUS_PRIORITY = (
    DriftClassificationCode.RAW_TEXT_PROHIBITED,
    DriftClassificationCode.REQUEST_TYPE_INVALID,
    DriftClassificationCode.REQUEST_ID_INVALID,
    DriftClassificationCode.REQUEST_OPERATION_INVALID,
    DriftClassificationCode.EXPLICIT_REQUEST_REQUIRED,
    DriftClassificationCode.COMPARISON_RESULT_TYPE_INVALID,
    DriftClassificationCode.COMPARISON_NOT_READY,
    DriftClassificationCode.COMPARISON_PACKAGE_MISSING,
    DriftClassificationCode.UNSUPPORTED_VERSION,
    DriftClassificationCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
    DriftClassificationCode.INCONSISTENT_ANCESTRY,
    DriftClassificationCode.MISSING_REQUIRED_VALUE,
    DriftClassificationCode.COMPARISON_RESULT_INVALID,
    DriftClassificationCode.COMPARISON_FINDING_INVALID,
)


_STATUS_BY_CODE = {
    DriftClassificationCode.COMPARISON_RESULT_TYPE_INVALID:
        DriftClassificationExecutionStatus.HELD_COMPARISON_NOT_READY,
    DriftClassificationCode.COMPARISON_NOT_READY:
        DriftClassificationExecutionStatus.HELD_COMPARISON_NOT_READY,
    DriftClassificationCode.COMPARISON_PACKAGE_MISSING:
        DriftClassificationExecutionStatus.HELD_COMPARISON_NOT_READY,
    DriftClassificationCode.UNSUPPORTED_VERSION:
        DriftClassificationExecutionStatus.HELD_UNSUPPORTED_VERSION,
    DriftClassificationCode.RECOMPUTED_OR_FABRICATED_IDENTITY:
        DriftClassificationExecutionStatus.HELD_IDENTITY_INVALID,
    DriftClassificationCode.INCONSISTENT_ANCESTRY:
        DriftClassificationExecutionStatus.HELD_INCONSISTENT_ANCESTRY,
    DriftClassificationCode.MISSING_REQUIRED_VALUE:
        DriftClassificationExecutionStatus.HELD_MISSING_REQUIRED_VALUE,
}


def status_for_codes(
    codes: tuple[DriftClassificationCode, ...],
) -> DriftClassificationExecutionStatus:
    code_set = set(codes)
    for code in _STATUS_PRIORITY:
        if code in code_set:
            return _STATUS_BY_CODE.get(
                code,
                DriftClassificationExecutionStatus.HELD_INVALID_REQUEST,
            )
    return DriftClassificationExecutionStatus.HELD_INVALID_REQUEST


def materiality_rule_ref(materiality: MaterialityState) -> str:
    return MATERIALITY_RULE_REF_MAP[materiality.value]


__all__ = (
    "classify_finding",
    "materiality_rule_ref",
    "ordered_drift_kinds",
    "status_for_codes",
    "unique_values",
)
