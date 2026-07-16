"""Collection-level integrity for Slice 37B concept-governance records.

The batch validator detects duplicate and conflicting identities, broken
references, orphan versions, incomplete transition ancestry, invalid quarantine
release, unsafe supersession, and active-state records lacking admission
history.  It is an in-memory proof operation only; it does not persist, admit,
lookup, map, select, or activate any resource.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from typing import Iterable

from ..schema import (
    ConceptLifecycleState,
    ConceptNamespaceIdentity,
    ConceptProvenanceReference,
    ControlledConceptIdentity,
    ControlledLexicalReference,
    ControlledSenseIdentity,
    SemanticClassIdentity,
    SemanticRelationFamilyIdentity,
    SemanticRelationTypeIdentity,
    TermConceptMappingIdentity,
)
from .identity import (
    expected_resource_lineage_id,
    parse_resource_version,
    resource_id,
)
from .lifecycle import evaluate_lifecycle_transition
from .schema import (
    ConceptGovernanceBatch,
    ConceptGovernanceValidationCode,
    ConceptGovernanceValidationError,
    ConceptGovernanceValidationIssue,
    ConceptGovernanceValidationReport,
    ConceptLifecycleTransitionKind,
    GovernedConceptResource,
)
from .validation import (
    active_lifecycle_states,
    report_from_issues,
    resource_scope_tokens,
    validate_governance_batch_shape,
    validate_governed_resource,
    validate_lifecycle_authority_record,
    validate_provenance_record,
)


_ALLOWED_INITIAL_STATES = frozenset(
    {
        ConceptLifecycleState.OBSERVED,
        ConceptLifecycleState.UNKNOWN,
        ConceptLifecycleState.UNRESOLVED,
        ConceptLifecycleState.AMBIGUOUS,
        ConceptLifecycleState.UNSUPPORTED,
        ConceptLifecycleState.CONFLICTED,
        ConceptLifecycleState.IMPLEMENTATION_DEFERRED,
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


def _index_unique(
    values: Iterable[object],
    *,
    id_getter,
    path_prefix: str,
    duplicate_code: ConceptGovernanceValidationCode,
    issues: list[ConceptGovernanceValidationIssue],
) -> dict[str, object]:
    index: dict[str, object] = {}

    for position, value in enumerate(values):
        identity = id_getter(value)
        existing = index.get(identity)

        if existing is not None:
            code = (
                ConceptGovernanceValidationCode.EXACT_DUPLICATE_RECORD
                if existing == value
                else duplicate_code
            )
            _add(
                issues,
                f"{path_prefix}[{position}]",
                code,
                f"duplicate identity {identity!r}",
            )
            continue

        index[identity] = value

    return index


def _require_ref(
    *,
    owner_path: str,
    reference: str,
    expected_type: type | tuple[type, ...],
    resources_by_id: dict[str, GovernedConceptResource],
    issues: list[ConceptGovernanceValidationIssue],
) -> None:
    target = resources_by_id.get(reference)

    if target is None:
        _add(
            issues,
            owner_path,
            ConceptGovernanceValidationCode.REFERENCE_NOT_FOUND,
            f"referenced resource {reference!r} is absent from the batch",
        )
        return

    if type(target) not in (
        expected_type
        if isinstance(expected_type, tuple)
        else (expected_type,)
    ):
        _add(
            issues,
            owner_path,
            ConceptGovernanceValidationCode.REFERENCE_KIND_MISMATCH,
            f"reference {reference!r} has type {type(target).__name__}",
        )


def _validate_resource_references(
    record: GovernedConceptResource,
    *,
    path: str,
    resources_by_id: dict[str, GovernedConceptResource],
    issues: list[ConceptGovernanceValidationIssue],
) -> None:
    if isinstance(record, ConceptNamespaceIdentity):
        return

    if hasattr(record, "namespace_id"):
        _require_ref(
            owner_path=f"{path}.namespace_id",
            reference=record.namespace_id,
            expected_type=ConceptNamespaceIdentity,
            resources_by_id=resources_by_id,
            issues=issues,
        )

    if isinstance(record, ControlledConceptIdentity):
        for index, reference in enumerate(record.semantic_class_refs):
            _require_ref(
                owner_path=f"{path}.semantic_class_refs[{index}]",
                reference=reference,
                expected_type=SemanticClassIdentity,
                resources_by_id=resources_by_id,
                issues=issues,
            )
        for index, reference in enumerate(record.sense_refs):
            _require_ref(
                owner_path=f"{path}.sense_refs[{index}]",
                reference=reference,
                expected_type=ControlledSenseIdentity,
                resources_by_id=resources_by_id,
                issues=issues,
            )
        for index, reference in enumerate(record.relation_type_refs):
            _require_ref(
                owner_path=f"{path}.relation_type_refs[{index}]",
                reference=reference,
                expected_type=SemanticRelationTypeIdentity,
                resources_by_id=resources_by_id,
                issues=issues,
            )

    elif isinstance(record, ControlledSenseIdentity):
        _require_ref(
            owner_path=f"{path}.concept_id",
            reference=record.concept_id,
            expected_type=ControlledConceptIdentity,
            resources_by_id=resources_by_id,
            issues=issues,
        )
        for index, reference in enumerate(record.lexical_reference_refs):
            _require_ref(
                owner_path=f"{path}.lexical_reference_refs[{index}]",
                reference=reference,
                expected_type=ControlledLexicalReference,
                resources_by_id=resources_by_id,
                issues=issues,
            )

    elif isinstance(record, TermConceptMappingIdentity):
        _require_ref(
            owner_path=f"{path}.lexical_reference_id",
            reference=record.lexical_reference_id,
            expected_type=ControlledLexicalReference,
            resources_by_id=resources_by_id,
            issues=issues,
        )
        for index, reference in enumerate(record.concept_candidate_refs):
            _require_ref(
                owner_path=f"{path}.concept_candidate_refs[{index}]",
                reference=reference,
                expected_type=ControlledConceptIdentity,
                resources_by_id=resources_by_id,
                issues=issues,
            )
        for index, reference in enumerate(record.sense_candidate_refs):
            _require_ref(
                owner_path=f"{path}.sense_candidate_refs[{index}]",
                reference=reference,
                expected_type=ControlledSenseIdentity,
                resources_by_id=resources_by_id,
                issues=issues,
            )

    elif isinstance(record, SemanticClassIdentity):
        for index, reference in enumerate(record.parent_class_refs):
            _require_ref(
                owner_path=f"{path}.parent_class_refs[{index}]",
                reference=reference,
                expected_type=SemanticClassIdentity,
                resources_by_id=resources_by_id,
                issues=issues,
            )

    elif isinstance(record, SemanticRelationTypeIdentity):
        _require_ref(
            owner_path=f"{path}.relation_family_id",
            reference=record.relation_family_id,
            expected_type=SemanticRelationFamilyIdentity,
            resources_by_id=resources_by_id,
            issues=issues,
        )
        for index, reference in enumerate(record.domain_class_refs):
            _require_ref(
                owner_path=f"{path}.domain_class_refs[{index}]",
                reference=reference,
                expected_type=SemanticClassIdentity,
                resources_by_id=resources_by_id,
                issues=issues,
            )
        for index, reference in enumerate(record.range_class_refs):
            _require_ref(
                owner_path=f"{path}.range_class_refs[{index}]",
                reference=reference,
                expected_type=SemanticClassIdentity,
                resources_by_id=resources_by_id,
                issues=issues,
            )
        if record.inverse_relation_type_ref is not None:
            _require_ref(
                owner_path=f"{path}.inverse_relation_type_ref",
                reference=record.inverse_relation_type_ref,
                expected_type=SemanticRelationTypeIdentity,
                resources_by_id=resources_by_id,
                issues=issues,
            )


def validate_governance_batch(
    batch: ConceptGovernanceBatch,
) -> ConceptGovernanceValidationReport:
    """Validate an immutable governance batch without applying any transition."""

    issues: list[ConceptGovernanceValidationIssue] = []
    shape_report = validate_governance_batch_shape(batch)
    _extend(issues, "batch", shape_report.issues)

    if type(batch) is not ConceptGovernanceBatch:
        return report_from_issues(issues)

    provenance_by_id = _index_unique(
        batch.provenance_records,
        id_getter=lambda item: item.provenance_id,
        path_prefix="provenance_records",
        duplicate_code=ConceptGovernanceValidationCode.PROVENANCE_INVALID,
        issues=issues,
    )
    resources_by_id = _index_unique(
        batch.resources,
        id_getter=resource_id,
        path_prefix="resources",
        duplicate_code=ConceptGovernanceValidationCode.DUPLICATE_RESOURCE_ID,
        issues=issues,
    )
    authority_by_id = _index_unique(
        batch.authority_records,
        id_getter=lambda item: item.authority_id,
        path_prefix="authority_records",
        duplicate_code=ConceptGovernanceValidationCode.AUTHORITY_BINDING_MISMATCH,
        issues=issues,
    )
    transitions_by_id = _index_unique(
        batch.transitions,
        id_getter=lambda item: item.transition_id,
        path_prefix="transitions",
        duplicate_code=ConceptGovernanceValidationCode.DUPLICATE_TRANSITION_ID,
        issues=issues,
    )

    for index, provenance in enumerate(batch.provenance_records):
        report = validate_provenance_record(provenance)
        _extend(issues, f"provenance_records[{index}]", report.issues)

    for index, resource in enumerate(batch.resources):
        report = validate_governed_resource(
            resource,
            provenance_by_id=provenance_by_id,
        )
        _extend(issues, f"resources[{index}]", report.issues)
        _validate_resource_references(
            resource,
            path=f"resources[{index}]",
            resources_by_id=resources_by_id,
            issues=issues,
        )

    for index, authority in enumerate(batch.authority_records):
        report = validate_lifecycle_authority_record(
            authority,
            provenance_by_id=provenance_by_id,
        )
        _extend(issues, f"authority_records[{index}]", report.issues)

    lineage_version_records: dict[
        tuple[str, tuple[int, int, int]],
        list[GovernedConceptResource],
    ] = defaultdict(list)
    lineage_records: dict[str, list[GovernedConceptResource]] = defaultdict(list)

    for resource in batch.resources:
        try:
            parsed_version = parse_resource_version(resource.version)
        except (TypeError, ValueError):
            continue
        lineage = expected_resource_lineage_id(resource)
        lineage_version_records[(lineage, parsed_version)].append(resource)
        lineage_records[lineage].append(resource)

    for (lineage, parsed_version), records in lineage_version_records.items():
        if len(records) <= 1:
            continue
        bodies = {repr(asdict(record)) for record in records}
        code = (
            ConceptGovernanceValidationCode.DUPLICATE_LINEAGE_VERSION
            if len(bodies) == 1
            else ConceptGovernanceValidationCode.CONFLICTING_LINEAGE_VERSION
        )
        _add(
            issues,
            f"lineages[{lineage}].versions[{parsed_version}]",
            code,
            "more than one resource record occupies the same lineage version",
        )

    incoming: dict[str, list[object]] = defaultdict(list)
    outgoing: dict[str, list[object]] = defaultdict(list)

    for index, transition in enumerate(batch.transitions):
        source = resources_by_id.get(transition.source_resource_id)
        target = resources_by_id.get(transition.target_resource_id)
        authority = authority_by_id.get(transition.authority_record_ref)

        if source is None:
            _add(
                issues,
                f"transitions[{index}].source_resource_id",
                ConceptGovernanceValidationCode.REFERENCE_NOT_FOUND,
                "source resource is absent from the batch",
            )
        if target is None:
            _add(
                issues,
                f"transitions[{index}].target_resource_id",
                ConceptGovernanceValidationCode.REFERENCE_NOT_FOUND,
                "target resource is absent from the batch",
            )
        if authority is None:
            _add(
                issues,
                f"transitions[{index}].authority_record_ref",
                ConceptGovernanceValidationCode.AUTHORITY_RECORD_NOT_FOUND,
                "authority record is absent from the batch",
            )

        if source is None or target is None or authority is None:
            continue

        decision = evaluate_lifecycle_transition(
            source,
            target,
            transition,
            authority,
            provenance_by_id=provenance_by_id,
        )
        _extend(issues, f"transitions[{index}]", decision.issues)
        incoming[target.resource_kind.value + ":" + resource_id(target)].append(transition)
        outgoing[source.resource_kind.value + ":" + resource_id(source)].append(transition)

    for key, values in incoming.items():
        if len(values) > 1:
            _add(
                issues,
                f"incoming[{key}]",
                ConceptGovernanceValidationCode.MULTIPLE_INCOMING_TRANSITIONS,
                "a version record may have at most one incoming transition",
            )

    for key, values in outgoing.items():
        if len(values) > 1:
            _add(
                issues,
                f"outgoing[{key}]",
                ConceptGovernanceValidationCode.MULTIPLE_OUTGOING_TRANSITIONS,
                "a version record may have at most one outgoing transition",
            )

    for lineage, records in lineage_records.items():
        ordered = sorted(records, key=lambda record: parse_resource_version(record.version))
        for position, record in enumerate(ordered):
            key = record.resource_kind.value + ":" + resource_id(record)
            incoming_count = len(incoming.get(key, ()))

            if position == 0:
                if incoming_count:
                    _add(
                        issues,
                        f"lineages[{lineage}].initial",
                        ConceptGovernanceValidationCode.ORPHAN_RESOURCE_VERSION,
                        "the lowest version cannot have an incoming transition from outside its lineage",
                    )
                if record.lifecycle_state not in _ALLOWED_INITIAL_STATES:
                    _add(
                        issues,
                        f"lineages[{lineage}].initial.lifecycle_state",
                        ConceptGovernanceValidationCode.ADMISSION_HISTORY_REQUIRED,
                        "initial active, candidate, quarantined, deprecated, superseded, or rejected records require preserved prior transition history",
                    )
            elif incoming_count != 1:
                _add(
                    issues,
                    f"lineages[{lineage}].versions[{record.version}]",
                    ConceptGovernanceValidationCode.ORPHAN_RESOURCE_VERSION,
                    "every later version requires exactly one incoming transition",
                )

        latest = ordered[-1]
        active_records = [
            record
            for record in records
            if record.lifecycle_state in active_lifecycle_states()
            and record is not latest
            and not outgoing.get(
                record.resource_kind.value + ":" + resource_id(record),
                (),
            )
        ]
        if active_records:
            _add(
                issues,
                f"lineages[{lineage}]",
                ConceptGovernanceValidationCode.CURRENT_ACTIVE_CONFLICT,
                "a non-current historical version remains marked active",
            )

    for index, transition in enumerate(batch.transitions):
        if transition.transition_kind is ConceptLifecycleTransitionKind.RELEASE_FROM_QUARANTINE:
            source_incoming = incoming.get(
                transition.resource_kind.value + ":" + transition.source_resource_id,
                (),
            )
            quarantine_transitions = [
                item
                for item in source_incoming
                if item.to_state is ConceptLifecycleState.QUARANTINED
            ]
            if len(quarantine_transitions) != 1:
                _add(
                    issues,
                    f"transitions[{index}].resolved_quarantine_cause_refs",
                    ConceptGovernanceValidationCode.HISTORICAL_ANCESTRY_REQUIRED,
                    "release requires the exact incoming quarantine transition",
                )
            else:
                required = set(quarantine_transitions[0].quarantine_cause_refs)
                resolved = set(transition.resolved_quarantine_cause_refs)
                if not required.issubset(resolved):
                    _add(
                        issues,
                        f"transitions[{index}].resolved_quarantine_cause_refs",
                        ConceptGovernanceValidationCode.QUARANTINE_CAUSE_UNRESOLVED,
                        "every prior quarantine cause must be explicitly resolved",
                    )

        if transition.transition_kind in {
            ConceptLifecycleTransitionKind.SUPERSESSION,
            ConceptLifecycleTransitionKind.HISTORICAL_ONLY,
        }:
            successor_ref = transition.superseding_resource_ref
            successor = (
                resources_by_id.get(successor_ref)
                if successor_ref is not None
                else None
            )
            source = resources_by_id.get(transition.source_resource_id)
            target = resources_by_id.get(transition.target_resource_id)

            if successor is None:
                _add(
                    issues,
                    f"transitions[{index}].superseding_resource_ref",
                    ConceptGovernanceValidationCode.SUPERSEDING_RESOURCE_INVALID,
                    "successor resource is absent from the batch",
                )
            elif source is not None and target is not None:
                if type(successor) is not type(source):
                    _add(
                        issues,
                        f"transitions[{index}].superseding_resource_ref",
                        ConceptGovernanceValidationCode.SUPERSEDING_RESOURCE_INVALID,
                        "successor must have the same exact resource type",
                    )
                if successor.lifecycle_state not in active_lifecycle_states():
                    _add(
                        issues,
                        f"transitions[{index}].superseding_resource_ref",
                        ConceptGovernanceValidationCode.SUPERSEDING_RESOURCE_INVALID,
                        "successor must be active within an explicit bounded scope",
                    )
                if not resource_scope_tokens(successor).issubset(
                    resource_scope_tokens(target)
                ):
                    _add(
                        issues,
                        f"transitions[{index}].superseding_resource_ref",
                        ConceptGovernanceValidationCode.SCOPE_EXPANSION,
                        "successor scope cannot silently exceed the supersession scope",
                    )
                if expected_resource_lineage_id(successor) == expected_resource_lineage_id(source):
                    _add(
                        issues,
                        f"transitions[{index}].superseding_resource_ref",
                        ConceptGovernanceValidationCode.SUPERSEDING_RESOURCE_INVALID,
                        "successor must be a distinct material identity lineage",
                    )

    # Rejected identities remain negative authority unless the exact rejection
    # transition is named by a later reopen record.
    rejection_by_target: dict[str, object] = {
        transition.target_resource_id: transition
        for transition in batch.transitions
        if transition.to_state is ConceptLifecycleState.REJECTED
    }
    for index, transition in enumerate(batch.transitions):
        if (
            transition.transition_kind
            is ConceptLifecycleTransitionKind.REOPEN_REVIEW
        ):
            rejection = rejection_by_target.get(transition.source_resource_id)
            if rejection is not None and (
                transition.prior_disposition_transition_ref
                != rejection.transition_id
            ):
                _add(
                    issues,
                    f"transitions[{index}].prior_disposition_transition_ref",
                    ConceptGovernanceValidationCode.HISTORICAL_ANCESTRY_REQUIRED,
                    "reopened review must name the exact prior rejection transition",
                )

    return report_from_issues(issues)


def assert_governance_batch(
    batch: ConceptGovernanceBatch,
) -> ConceptGovernanceBatch:
    report = validate_governance_batch(batch)
    if not report.ok:
        raise ConceptGovernanceValidationError(report)
    return batch
