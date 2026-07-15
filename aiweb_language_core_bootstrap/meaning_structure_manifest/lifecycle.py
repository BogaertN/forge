"""Deterministic MSM-v1 lifecycle transition law for Slice 35C.

This module turns the architectural lifecycle constraints into a bounded,
inspectable runtime specification. It does not parse language, choose candidate
meaning, evaluate evidence, authorize actions, serialize manifests, persist
state, access files, use networks, invoke tools, or connect the bootstrap.

A transition is permitted only when:

* both records already conform to the Slice 35A constructor contract;
* the existing manifest conforms to Slice 35B validation;
* source and successor belong to one lineage;
* the direct state pair and transition kind are explicitly admitted;
* the record-level references prove the intended ancestry;
* every authority-sensitive transition names an existing external-authority
  reference record from the same manifest; and
* immutable successor construction preserves the predecessor and appends one
  explicit SemanticTransitionTraceRecord.

Document 2 names CORRECTED and SUPERSEDED as lifecycle distinctions but also
requires the prior record to remain historically stable while a later record
governs. This runtime specification therefore represents correction and
supersession through transition_kind=CORRECTION or SUPERSESSION from a prior
record to a new same-kind, same-state successor. It does not manufacture a
mutable replacement or a synthetic state-only record.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any

from ._enums import (
    DeliveryContainmentKind,
    LineageOriginKind,
    SemanticLifecycleState,
    SemanticTransitionKind,
)
from ._identity import SCHEMA_VERSION
from ._records import (
    CandidateMeaningRecord,
    DeliveryContainmentLinkRecord,
    ExpressionLinkRecord,
    ExternalAuthorityReferenceRecord,
    GovernedOutwardMeaningRecord,
    GovernedResultReferenceRecord,
    LineageRootRecord,
    MeaningStructureManifestV1,
    NonSelectionOutcomeRecord,
    SelectedGovernedMeaningRecord,
    SemanticTransitionTraceRecord,
    ValidationLinkRecord,
)
from .validation import assert_valid_manifest, validate_manifest, validate_record

LIFECYCLE_SPEC_ID = "aiweb-msm-v1-lifecycle-transition-law"
LIFECYCLE_SPEC_VERSION = "aiweb-msm-v1-lifecycle-v1"


class LifecycleTransitionCode(str, Enum):
    MANIFEST_INVALID = "manifest_invalid"
    RECORD_INVALID = "record_invalid"
    SOURCE_NOT_FOUND = "source_not_found"
    TARGET_ID_EXISTS = "target_id_exists"
    TRACE_ID_EXISTS = "trace_id_exists"
    LINEAGE_MISMATCH = "lineage_mismatch"
    STATE_UNAVAILABLE = "state_unavailable"
    RESERVED_DISPOSITION_STATE = "reserved_disposition_state"
    TRANSITION_NOT_PERMITTED = "transition_not_permitted"
    TRANSITION_KIND_NOT_PERMITTED = "transition_kind_not_permitted"
    AUTHORITY_REQUIRED = "authority_required"
    AUTHORITY_NOT_FOUND = "authority_not_found"
    AUTHORITY_KIND_MISMATCH = "authority_kind_mismatch"
    AUTHORITY_BINDING_MISMATCH = "authority_binding_mismatch"
    TARGET_SHAPE_MISMATCH = "target_shape_mismatch"
    RELATIONSHIP_MISMATCH = "relationship_mismatch"
    REASON_REQUIRED = "reason_required"
    SUCCESSOR_TYPE_UNSUPPORTED = "successor_type_unsupported"
    RESULT_MANIFEST_INVALID = "result_manifest_invalid"


@dataclass(frozen=True, slots=True)
class LifecycleTransitionIssue:
    code: LifecycleTransitionCode
    detail: str


@dataclass(frozen=True, slots=True)
class LifecycleTransitionRule:
    from_state: SemanticLifecycleState
    to_state: SemanticLifecycleState
    allowed_kinds: tuple[SemanticTransitionKind, ...]
    authority_required: bool
    purpose: str


@dataclass(frozen=True, slots=True)
class LifecycleTransitionDecision:
    specification_id: str
    specification_version: str
    allowed: bool
    from_state: SemanticLifecycleState | None
    to_state: SemanticLifecycleState | None
    transition_kind: SemanticTransitionKind
    issues: tuple[LifecycleTransitionIssue, ...]


@dataclass(frozen=True, slots=True)
class LifecycleAppendResult:
    manifest: MeaningStructureManifestV1
    trace: SemanticTransitionTraceRecord
    decision: LifecycleTransitionDecision


class LifecycleTransitionError(ValueError):
    """Raised when immutable lifecycle successor construction fails closed."""

    def __init__(self, decision: LifecycleTransitionDecision) -> None:
        self.decision = decision
        summary = "; ".join(
            f"{issue.code.value}:{issue.detail}" for issue in decision.issues
        )
        super().__init__(summary or "MSM-v1 lifecycle transition denied")


LIFECYCLE_TRANSITION_RULES = (
    LifecycleTransitionRule(
        SemanticLifecycleState.LINEAGE_ORIGIN,
        SemanticLifecycleState.CANDIDATE_MEANING,
        (SemanticTransitionKind.ANCESTRY,),
        False,
        "Open an inward candidate from a source-bound lineage origin.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.LINEAGE_ORIGIN,
        SemanticLifecycleState.UNRESOLVED,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Preserve that no lawful candidate can yet be selected.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.LINEAGE_ORIGIN,
        SemanticLifecycleState.CLARIFICATION_REQUIRED,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Preserve a source-level clarification requirement.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.LINEAGE_ORIGIN,
        SemanticLifecycleState.UNSUPPORTED,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Preserve that source language is not lawfully supported.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.LINEAGE_ORIGIN,
        SemanticLifecycleState.GOVERNED_OUTWARD_MEANING,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Open outward semantic custody from an authorized outward purpose.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.CANDIDATE_MEANING,
        SemanticLifecycleState.UNRESOLVED,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Hold materially viable meanings without arbitrary selection.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.CANDIDATE_MEANING,
        SemanticLifecycleState.CLARIFICATION_REQUIRED,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Request missing information without guessing.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.CANDIDATE_MEANING,
        SemanticLifecycleState.REFUSED,
        (SemanticTransitionKind.REJECTION,),
        True,
        "Record a refusal-relevant gate outcome without erasing meaning.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.CANDIDATE_MEANING,
        SemanticLifecycleState.UNSUPPORTED,
        (SemanticTransitionKind.REJECTION,),
        True,
        "Record unsupported interpretation or relationship.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.CANDIDATE_MEANING,
        SemanticLifecycleState.AUTHORITY_BLOCKED,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Preserve understood meaning whose consequence lacks authority.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.CANDIDATE_MEANING,
        SemanticLifecycleState.SELECTED_GOVERNED_MEANING,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Select one bounded candidate for lawful next-step consideration.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.UNRESOLVED,
        SemanticLifecycleState.CANDIDATE_MEANING,
        (SemanticTransitionKind.ANCESTRY, SemanticTransitionKind.NARROWING),
        True,
        "Re-enter candidate review when new deterministic support appears.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.CLARIFICATION_REQUIRED,
        SemanticLifecycleState.CANDIDATE_MEANING,
        (SemanticTransitionKind.NARROWING,),
        True,
        "Create a clarified candidate while retaining prior ambiguity.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.UNSUPPORTED,
        SemanticLifecycleState.CANDIDATE_MEANING,
        (SemanticTransitionKind.ANCESTRY, SemanticTransitionKind.NARROWING),
        True,
        "Re-enter only after new admitted support or narrower scope exists.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.REFUSED,
        SemanticLifecycleState.CANDIDATE_MEANING,
        (SemanticTransitionKind.NARROWING,),
        True,
        "Re-open a materially narrowed request without erasing refusal.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.AUTHORITY_BLOCKED,
        SemanticLifecycleState.SELECTED_GOVERNED_MEANING,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Permit later selected custody only after new authority is recorded.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.UNRESOLVED,
        SemanticLifecycleState.GOVERNED_OUTWARD_MEANING,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Authorize outward communication of unresolved status.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.CLARIFICATION_REQUIRED,
        SemanticLifecycleState.GOVERNED_OUTWARD_MEANING,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Authorize outward clarification language.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.REFUSED,
        SemanticLifecycleState.GOVERNED_OUTWARD_MEANING,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Authorize outward refusal meaning without weakening it.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.UNSUPPORTED,
        SemanticLifecycleState.GOVERNED_OUTWARD_MEANING,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Authorize outward unsupported-status meaning.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.AUTHORITY_BLOCKED,
        SemanticLifecycleState.GOVERNED_OUTWARD_MEANING,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Authorize outward communication of the authority block.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.SELECTED_GOVERNED_MEANING,
        SemanticLifecycleState.REFUSED,
        (SemanticTransitionKind.REJECTION,),
        True,
        "Preserve selected meaning while refusing its requested consequence.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.SELECTED_GOVERNED_MEANING,
        SemanticLifecycleState.AUTHORITY_BLOCKED,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Preserve selected meaning whose consequence lacks external authority.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.SELECTED_GOVERNED_MEANING,
        SemanticLifecycleState.GOVERNED_RESULT_REFERENCED,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Link selected meaning to an externally governed result.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.SELECTED_GOVERNED_MEANING,
        SemanticLifecycleState.GOVERNED_OUTWARD_MEANING,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Create bounded outward meaning when no separate result is required.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.GOVERNED_RESULT_REFERENCED,
        SemanticLifecycleState.GOVERNED_OUTWARD_MEANING,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Derive outward meaning from the governed result reference.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.GOVERNED_OUTWARD_MEANING,
        SemanticLifecycleState.EXPRESSION_LINKED,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Link a candidate expression without implying validation.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.EXPRESSION_LINKED,
        SemanticLifecycleState.VALIDATION_LINKED,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Link an external deterministic validation receipt.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.EXPRESSION_LINKED,
        SemanticLifecycleState.CONTAINMENT_LINKED,
        (SemanticTransitionKind.CONTAINMENT,),
        True,
        "Contain an expression before validation or delivery.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.VALIDATION_LINKED,
        SemanticLifecycleState.DELIVERY_LINKED,
        (SemanticTransitionKind.ANCESTRY,),
        True,
        "Link a separate authorized delivery receipt.",
    ),
    LifecycleTransitionRule(
        SemanticLifecycleState.VALIDATION_LINKED,
        SemanticLifecycleState.CONTAINMENT_LINKED,
        (SemanticTransitionKind.CONTAINMENT,),
        True,
        "Link containment after validation disposition.",
    ),
)

_RULE_INDEX = {
    (rule.from_state, rule.to_state): rule for rule in LIFECYCLE_TRANSITION_RULES
}

_SUBSTANTIVE_SUCCESSOR_TYPES = (
    CandidateMeaningRecord,
    NonSelectionOutcomeRecord,
    SelectedGovernedMeaningRecord,
    GovernedResultReferenceRecord,
    GovernedOutwardMeaningRecord,
    ExpressionLinkRecord,
    ValidationLinkRecord,
    DeliveryContainmentLinkRecord,
)


_STATE_TYPES = {
    SemanticLifecycleState.LINEAGE_ORIGIN: (LineageRootRecord,),
    SemanticLifecycleState.CANDIDATE_MEANING: (CandidateMeaningRecord,),
    SemanticLifecycleState.UNRESOLVED: (NonSelectionOutcomeRecord,),
    SemanticLifecycleState.CLARIFICATION_REQUIRED: (NonSelectionOutcomeRecord,),
    SemanticLifecycleState.REFUSED: (NonSelectionOutcomeRecord,),
    SemanticLifecycleState.UNSUPPORTED: (NonSelectionOutcomeRecord,),
    SemanticLifecycleState.AUTHORITY_BLOCKED: (NonSelectionOutcomeRecord,),
    SemanticLifecycleState.SELECTED_GOVERNED_MEANING: (
        SelectedGovernedMeaningRecord,
    ),
    SemanticLifecycleState.GOVERNED_RESULT_REFERENCED: (
        GovernedResultReferenceRecord,
    ),
    SemanticLifecycleState.GOVERNED_OUTWARD_MEANING: (
        GovernedOutwardMeaningRecord,
    ),
    SemanticLifecycleState.EXPRESSION_LINKED: (ExpressionLinkRecord,),
    SemanticLifecycleState.VALIDATION_LINKED: (ValidationLinkRecord,),
    SemanticLifecycleState.DELIVERY_LINKED: (DeliveryContainmentLinkRecord,),
    SemanticLifecycleState.CONTAINMENT_LINKED: (
        DeliveryContainmentLinkRecord,
    ),
}


_COLLECTION_BY_TYPE = {
    CandidateMeaningRecord: "candidate_meanings",
    NonSelectionOutcomeRecord: "non_selection_outcomes",
    SelectedGovernedMeaningRecord: "selected_governed_meanings",
    GovernedResultReferenceRecord: "governed_result_references",
    GovernedOutwardMeaningRecord: "governed_outward_meanings",
    ExpressionLinkRecord: "expression_links",
    ValidationLinkRecord: "validation_links",
    DeliveryContainmentLinkRecord: "delivery_or_containment_links",
}


def _issue(
    issues: list[LifecycleTransitionIssue],
    code: LifecycleTransitionCode,
    detail: str,
) -> None:
    issues.append(LifecycleTransitionIssue(code=code, detail=detail))


def _record_reference(record: Any) -> str | None:
    if isinstance(record, LineageRootRecord):
        return record.lineage_id
    record_id = getattr(record, "record_id", None)
    return record_id if isinstance(record_id, str) else None


def _state_for_record(record: Any) -> SemanticLifecycleState | None:
    state = getattr(record, "lifecycle_state", None)
    return state if isinstance(state, SemanticLifecycleState) else None


def _iter_manifest_records(manifest: MeaningStructureManifestV1) -> tuple[Any, ...]:
    return (
        manifest.lineage_root,
        *manifest.candidate_meanings,
        *manifest.non_selection_outcomes,
        *manifest.selected_governed_meanings,
        *manifest.governed_result_references,
        *manifest.governed_outward_meanings,
        *manifest.expression_links,
        *manifest.validation_links,
        *manifest.delivery_or_containment_links,
        *manifest.external_authority_references,
        *manifest.semantic_transition_traces,
    )


def _record_index(manifest: MeaningStructureManifestV1) -> dict[str, Any]:
    index: dict[str, Any] = {}
    for record in _iter_manifest_records(manifest):
        reference = _record_reference(record)
        if reference is not None:
            index[reference] = record
    return index


def _expected_type_matches(record: Any, state: SemanticLifecycleState) -> bool:
    expected = _STATE_TYPES.get(state)
    if expected is None or not isinstance(record, expected):
        return False
    if isinstance(record, NonSelectionOutcomeRecord):
        return record.lifecycle_state is state
    if isinstance(record, DeliveryContainmentLinkRecord):
        return record.lifecycle_state is state
    return True


def _authority_record(
    authority_reference_ref: str | None,
    *,
    index: dict[str, Any],
    required: bool,
    issues: list[LifecycleTransitionIssue],
) -> ExternalAuthorityReferenceRecord | None:
    if authority_reference_ref is None:
        if required:
            _issue(
                issues,
                LifecycleTransitionCode.AUTHORITY_REQUIRED,
                "this transition requires an external-authority reference record",
            )
        return None
    authority = index.get(authority_reference_ref)
    if authority is None:
        _issue(
            issues,
            LifecycleTransitionCode.AUTHORITY_NOT_FOUND,
            f"no manifest record found for authority {authority_reference_ref!r}",
        )
        return None
    if not isinstance(authority, ExternalAuthorityReferenceRecord):
        _issue(
            issues,
            LifecycleTransitionCode.AUTHORITY_KIND_MISMATCH,
            "authority reference must identify ExternalAuthorityReferenceRecord",
        )
        return None
    return authority


def _authority_binding_matches(
    successor: Any,
    authority: ExternalAuthorityReferenceRecord | None,
) -> bool:
    if authority is None:
        return True
    authority_values = {authority.record_id, authority.external_object_ref}
    if isinstance(successor, NonSelectionOutcomeRecord):
        return authority.record_id in successor.external_authority_refs
    if isinstance(successor, SelectedGovernedMeaningRecord):
        return successor.selection_authority_ref in authority_values
    if isinstance(successor, GovernedResultReferenceRecord):
        return successor.external_authority_ref == authority.record_id
    if isinstance(successor, GovernedOutwardMeaningRecord):
        return (
            authority.record_id in successor.outward_basis_refs
            or authority.record_id in successor.external_dependency_refs
        )
    if isinstance(successor, ExpressionLinkRecord):
        return successor.expression_candidate_ref in authority_values
    if isinstance(successor, ValidationLinkRecord):
        return successor.external_validation_receipt_ref in authority_values
    if isinstance(successor, DeliveryContainmentLinkRecord):
        return successor.external_receipt_ref in authority_values
    return True


def _relationship_matches(source: Any, successor: Any) -> bool:
    if isinstance(source, LineageRootRecord):
        if isinstance(successor, CandidateMeaningRecord):
            return (
                source.origin_kind
                is LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION
                and successor.source_expression_ref == source.origin_ref
            )
        if isinstance(successor, NonSelectionOutcomeRecord):
            return (
                source.origin_kind
                is LineageOriginKind.SOURCE_BOUND_HUMAN_EXPRESSION
                and not successor.candidate_refs
            )
        if isinstance(successor, GovernedOutwardMeaningRecord):
            return (
                source.origin_kind
                is LineageOriginKind.AUTHORIZED_OUTWARD_EXPRESSION_PURPOSE
            )
        return False
    if isinstance(source, CandidateMeaningRecord):
        if isinstance(successor, NonSelectionOutcomeRecord):
            return source.record_id in successor.candidate_refs
        if isinstance(successor, SelectedGovernedMeaningRecord):
            return successor.selected_candidate_ref == source.record_id
    if isinstance(source, NonSelectionOutcomeRecord):
        if isinstance(successor, CandidateMeaningRecord):
            return True
        if isinstance(successor, SelectedGovernedMeaningRecord):
            return successor.selected_candidate_ref in source.candidate_refs
        if isinstance(successor, GovernedOutwardMeaningRecord):
            return source.record_id in successor.outward_basis_refs
    if isinstance(source, SelectedGovernedMeaningRecord):
        if isinstance(successor, NonSelectionOutcomeRecord):
            return source.selected_candidate_ref in successor.candidate_refs
        if isinstance(successor, GovernedResultReferenceRecord):
            return successor.selected_meaning_ref == source.record_id
        if isinstance(successor, GovernedOutwardMeaningRecord):
            return (
                source.record_id in successor.outward_basis_refs
                or successor.prior_selected_meaning_ref == source.record_id
            )
    if isinstance(source, GovernedResultReferenceRecord) and isinstance(
        successor, GovernedOutwardMeaningRecord
    ):
        return source.record_id in successor.outward_basis_refs
    if isinstance(source, GovernedOutwardMeaningRecord) and isinstance(
        successor, ExpressionLinkRecord
    ):
        return successor.governed_outward_meaning_ref == source.record_id
    if isinstance(source, ExpressionLinkRecord):
        if isinstance(successor, ValidationLinkRecord):
            return successor.expression_link_ref == source.record_id
        if isinstance(successor, DeliveryContainmentLinkRecord):
            return successor.prior_link_ref == source.record_id
    if isinstance(source, ValidationLinkRecord) and isinstance(
        successor, DeliveryContainmentLinkRecord
    ):
        return successor.prior_link_ref == source.record_id
    return False


def evaluate_lifecycle_transition(
    manifest: Any,
    *,
    from_record_ref: str,
    successor: Any,
    transition_kind: SemanticTransitionKind,
    reason: str,
    authority_reference_ref: str | None,
) -> LifecycleTransitionDecision:
    """Evaluate one proposed immutable successor without changing the manifest."""

    issues: list[LifecycleTransitionIssue] = []
    from_state: SemanticLifecycleState | None = None
    to_state: SemanticLifecycleState | None = _state_for_record(successor)

    manifest_report = validate_manifest(manifest)
    if not manifest_report.ok:
        _issue(
            issues,
            LifecycleTransitionCode.MANIFEST_INVALID,
            "existing manifest does not pass Slice 35B validation",
        )
        return LifecycleTransitionDecision(
            LIFECYCLE_SPEC_ID,
            LIFECYCLE_SPEC_VERSION,
            False,
            from_state,
            to_state,
            transition_kind,
            tuple(issues),
        )

    assert isinstance(manifest, MeaningStructureManifestV1)
    index = _record_index(manifest)
    source = index.get(from_record_ref)
    if source is None:
        _issue(
            issues,
            LifecycleTransitionCode.SOURCE_NOT_FOUND,
            f"no manifest record found for source {from_record_ref!r}",
        )
    else:
        from_state = _state_for_record(source)

    successor_report = validate_record(successor)
    if not successor_report.ok:
        _issue(
            issues,
            LifecycleTransitionCode.RECORD_INVALID,
            "successor does not pass Slice 35B intrinsic validation",
        )

    successor_ref = _record_reference(successor)
    if successor_ref is not None and successor_ref in index:
        _issue(
            issues,
            LifecycleTransitionCode.TARGET_ID_EXISTS,
            f"successor reference {successor_ref!r} already exists",
        )

    if not isinstance(transition_kind, SemanticTransitionKind):
        _issue(
            issues,
            LifecycleTransitionCode.TRANSITION_KIND_NOT_PERMITTED,
            "transition_kind must be SemanticTransitionKind",
        )

    if not isinstance(reason, str) or not reason.strip() or reason != reason.strip():
        _issue(
            issues,
            LifecycleTransitionCode.REASON_REQUIRED,
            "reason must be non-empty trimmed text",
        )

    successor_lineage = getattr(successor, "lineage_id", None)
    if successor_lineage != manifest.lineage_root.lineage_id:
        _issue(
            issues,
            LifecycleTransitionCode.LINEAGE_MISMATCH,
            "successor must remain in the manifest lineage",
        )

    if from_state is None or to_state is None:
        _issue(
            issues,
            LifecycleTransitionCode.STATE_UNAVAILABLE,
            "source and successor must expose lifecycle states",
        )
        rule = None
    elif to_state in {
        SemanticLifecycleState.CORRECTED,
        SemanticLifecycleState.SUPERSEDED,
    }:
        _issue(
            issues,
            LifecycleTransitionCode.RESERVED_DISPOSITION_STATE,
            "correction and supersession are trace kinds to an immutable successor, not synthetic target records",
        )
        rule = None
    else:
        rule = _RULE_INDEX.get((from_state, to_state))

    correction_overlay = transition_kind in {
        SemanticTransitionKind.CORRECTION,
        SemanticTransitionKind.SUPERSESSION,
    }

    if correction_overlay:
        if source is None or not isinstance(successor, _SUBSTANTIVE_SUCCESSOR_TYPES):
            _issue(
                issues,
                LifecycleTransitionCode.SUCCESSOR_TYPE_UNSUPPORTED,
                "correction or supersession requires a substantive successor record",
            )
        elif isinstance(source, LineageRootRecord) or type(source) is not type(successor):
            _issue(
                issues,
                LifecycleTransitionCode.TRANSITION_NOT_PERMITTED,
                "correction and supersession require the same concrete record type",
            )
        elif from_state is not to_state:
            _issue(
                issues,
                LifecycleTransitionCode.TRANSITION_NOT_PERMITTED,
                "correction and supersession preserve the concrete lifecycle state while replacing content immutably",
            )
        authority_required = True
    else:
        if rule is None and from_state is not None and to_state is not None:
            _issue(
                issues,
                LifecycleTransitionCode.TRANSITION_NOT_PERMITTED,
                f"direct transition {from_state.value}->{to_state.value} is not admitted",
            )
            authority_required = True
        elif rule is not None:
            authority_required = rule.authority_required
            if transition_kind not in rule.allowed_kinds:
                _issue(
                    issues,
                    LifecycleTransitionCode.TRANSITION_KIND_NOT_PERMITTED,
                    f"{transition_kind.value} is not admitted for {from_state.value}->{to_state.value}",
                )
        else:
            authority_required = True

    if to_state is not None and not _expected_type_matches(successor, to_state):
        _issue(
            issues,
            LifecycleTransitionCode.TARGET_SHAPE_MISMATCH,
            "successor record type does not match its lifecycle state",
        )

    authority = _authority_record(
        authority_reference_ref,
        index=index,
        required=authority_required,
        issues=issues,
    )

    if authority is not None and not correction_overlay:
        if not _authority_binding_matches(successor, authority):
            _issue(
                issues,
                LifecycleTransitionCode.AUTHORITY_BINDING_MISMATCH,
                "successor does not carry the named authority reference or receipt",
            )

    if source is not None and not correction_overlay and rule is not None:
        if not _relationship_matches(source, successor):
            _issue(
                issues,
                LifecycleTransitionCode.RELATIONSHIP_MISMATCH,
                "successor fields do not prove the proposed direct ancestry",
            )

    return LifecycleTransitionDecision(
        LIFECYCLE_SPEC_ID,
        LIFECYCLE_SPEC_VERSION,
        not issues,
        from_state,
        to_state,
        transition_kind,
        tuple(issues),
    )


def append_lifecycle_successor(
    manifest: Any,
    *,
    trace_record_id: str,
    from_record_ref: str,
    successor: Any,
    transition_kind: SemanticTransitionKind,
    reason: str,
    authority_reference_ref: str | None,
) -> LifecycleAppendResult:
    """Return a new manifest with one successor and one explicit trace appended."""

    decision = evaluate_lifecycle_transition(
        manifest,
        from_record_ref=from_record_ref,
        successor=successor,
        transition_kind=transition_kind,
        reason=reason,
        authority_reference_ref=authority_reference_ref,
    )
    if not decision.allowed:
        raise LifecycleTransitionError(decision)

    assert isinstance(manifest, MeaningStructureManifestV1)
    index = _record_index(manifest)
    if trace_record_id in index:
        denied = LifecycleTransitionDecision(
            LIFECYCLE_SPEC_ID,
            LIFECYCLE_SPEC_VERSION,
            False,
            decision.from_state,
            decision.to_state,
            transition_kind,
            (
                LifecycleTransitionIssue(
                    LifecycleTransitionCode.TRACE_ID_EXISTS,
                    f"trace reference {trace_record_id!r} already exists",
                ),
            ),
        )
        raise LifecycleTransitionError(denied)

    collection_name = _COLLECTION_BY_TYPE.get(type(successor))
    if collection_name is None:
        denied = LifecycleTransitionDecision(
            LIFECYCLE_SPEC_ID,
            LIFECYCLE_SPEC_VERSION,
            False,
            decision.from_state,
            decision.to_state,
            transition_kind,
            (
                LifecycleTransitionIssue(
                    LifecycleTransitionCode.SUCCESSOR_TYPE_UNSUPPORTED,
                    "successor type has no MSM-v1 manifest collection",
                ),
            ),
        )
        raise LifecycleTransitionError(denied)

    source = index[from_record_ref]
    source_state = _state_for_record(source)
    successor_state = _state_for_record(successor)
    successor_ref = _record_reference(successor)
    assert source_state is not None
    assert successor_state is not None
    assert successor_ref is not None

    trace = SemanticTransitionTraceRecord(
        record_id=trace_record_id,
        lineage_id=manifest.lineage_root.lineage_id,
        from_record_ref=from_record_ref,
        to_record_ref=successor_ref,
        from_state=source_state,
        to_state=successor_state,
        transition_kind=transition_kind,
        reason=reason,
        authority_reference_ref=authority_reference_ref,
    )

    current_collection = getattr(manifest, collection_name)
    updated = replace(
        manifest,
        **{
            collection_name: (*current_collection, successor),
            "semantic_transition_traces": (
                *manifest.semantic_transition_traces,
                trace,
            ),
        },
    )

    result_report = validate_manifest(updated)
    if not result_report.ok:
        denied = LifecycleTransitionDecision(
            LIFECYCLE_SPEC_ID,
            LIFECYCLE_SPEC_VERSION,
            False,
            source_state,
            successor_state,
            transition_kind,
            (
                LifecycleTransitionIssue(
                    LifecycleTransitionCode.RESULT_MANIFEST_INVALID,
                    "appended manifest does not pass Slice 35B validation",
                ),
            ),
        )
        raise LifecycleTransitionError(denied)

    assert_valid_manifest(updated)
    return LifecycleAppendResult(manifest=updated, trace=trace, decision=decision)


__all__ = (
    "LIFECYCLE_SPEC_ID",
    "LIFECYCLE_SPEC_VERSION",
    "LIFECYCLE_TRANSITION_RULES",
    "LifecycleAppendResult",
    "LifecycleTransitionCode",
    "LifecycleTransitionDecision",
    "LifecycleTransitionError",
    "LifecycleTransitionIssue",
    "LifecycleTransitionRule",
    "append_lifecycle_successor",
    "evaluate_lifecycle_transition",
)
