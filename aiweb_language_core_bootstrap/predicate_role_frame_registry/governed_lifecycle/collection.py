"""Collection-level integrity for Slice 38B predicate-governance records.

The validator detects duplicate and conflicting identities, broken references,
orphan versions, incomplete transition ancestry, unsafe supersession, active
state conflicts, and admission without review history.  It is an in-memory
proof operation only and performs no lookup, selection, persistence, routing,
invocation, or activation.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from ..schema import (
    ActionRootIdentity,
    PredicateIdentity,
    PredicateLifecycleState,
    PredicateNamespaceIdentity,
    PredicateProvenanceReference,
)
from .identity import (
    expected_resource_lineage_id,
    parse_resource_version,
    resource_id,
)
from .lifecycle import evaluate_lifecycle_transition
from .schema import (
    GovernedPredicateResource,
    PredicateGovernanceBatch,
    PredicateGovernanceValidationCode,
    PredicateGovernanceValidationError,
    PredicateGovernanceValidationIssue,
    PredicateGovernanceValidationReport,
    PredicateLifecycleAuthorityRecord,
    PredicateLifecycleTransitionKind,
    PredicateLifecycleTransitionRecord,
)
from .validation import (
    active_lifecycle_states,
    report_from_issues,
    validate_governance_batch_shape,
    validate_governed_resource,
    validate_lifecycle_authority_record,
    validate_lifecycle_transition_record_shape,
    validate_provenance_record,
)


_ALLOWED_INITIAL_STATES = frozenset(
    {
        PredicateLifecycleState.OBSERVED,
        PredicateLifecycleState.CANDIDATE,
        PredicateLifecycleState.UNKNOWN,
        PredicateLifecycleState.UNRESOLVED,
        PredicateLifecycleState.AMBIGUOUS,
        PredicateLifecycleState.UNSUPPORTED,
        PredicateLifecycleState.CONFLICTED,
        PredicateLifecycleState.IMPLEMENTATION_DEFERRED,
    }
)
_ADMISSION_KINDS = frozenset(
    {
        PredicateLifecycleTransitionKind.ADMISSION,
        PredicateLifecycleTransitionKind.ARCHITECTURE_ADMISSION,
    }
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


def _index_unique(
    values: Iterable[object],
    *,
    id_getter,
    path_prefix: str,
    duplicate_code: PredicateGovernanceValidationCode,
    issues: list[PredicateGovernanceValidationIssue],
) -> dict[str, object]:
    index: dict[str, object] = {}
    for position, value in enumerate(values):
        try:
            identity = id_getter(value)
        except Exception:
            _add(
                issues,
                f"{path_prefix}[{position}]",
                PredicateGovernanceValidationCode.TYPE_MISMATCH,
                "record identity could not be read",
            )
            continue
        if type(identity) is not str or not identity:
            _add(
                issues,
                f"{path_prefix}[{position}]",
                PredicateGovernanceValidationCode.TYPE_MISMATCH,
                "record identity must be a non-empty str",
            )
            continue
        existing = index.get(identity)
        if existing is not None:
            try:
                exact_duplicate = existing == value
            except Exception:
                exact_duplicate = False
            code = (
                PredicateGovernanceValidationCode.EXACT_DUPLICATE_RECORD
                if exact_duplicate
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
    resources_by_id: dict[str, GovernedPredicateResource],
    issues: list[PredicateGovernanceValidationIssue],
) -> GovernedPredicateResource | None:
    if type(reference) is not str or not reference:
        _add(
            issues,
            owner_path,
            PredicateGovernanceValidationCode.TYPE_MISMATCH,
            "resource reference must be a non-empty str",
        )
        return None
    target = resources_by_id.get(reference)
    if target is None:
        _add(
            issues,
            owner_path,
            PredicateGovernanceValidationCode.REFERENCE_NOT_FOUND,
            f"referenced resource {reference!r} is absent from the batch",
        )
        return None
    allowed = expected_type if isinstance(expected_type, tuple) else (expected_type,)
    if type(target) not in allowed:
        _add(
            issues,
            owner_path,
            PredicateGovernanceValidationCode.REFERENCE_KIND_MISMATCH,
            f"reference {reference!r} has type {type(target).__name__}",
        )
        return None
    return target


def _validate_resource_references(
    record: GovernedPredicateResource,
    *,
    path: str,
    resources_by_id: dict[str, GovernedPredicateResource],
    issues: list[PredicateGovernanceValidationIssue],
) -> None:
    if type(record) is PredicateNamespaceIdentity:
        return

    namespace = _require_ref(
        owner_path=f"{path}.namespace_id",
        reference=record.namespace_id,
        expected_type=PredicateNamespaceIdentity,
        resources_by_id=resources_by_id,
        issues=issues,
    )

    if type(record) is ActionRootIdentity:
        if namespace is not None and namespace.lifecycle_state in {
            PredicateLifecycleState.DEPRECATED,
            PredicateLifecycleState.REJECTED,
            PredicateLifecycleState.WITHDRAWN,
            PredicateLifecycleState.SUPERSEDED,
        }:
            _add(
                issues,
                f"{path}.namespace_id",
                PredicateGovernanceValidationCode.REFERENCE_KIND_MISMATCH,
                "action root cannot depend on a terminally unavailable namespace",
            )
        if (
            record.lifecycle_state in active_lifecycle_states()
            and namespace is not None
            and namespace.lifecycle_state not in active_lifecycle_states()
        ):
            _add(
                issues,
                f"{path}.namespace_id",
                PredicateGovernanceValidationCode.UNRESOLVED_DEPENDENCY,
                "admitted action root requires an admitted namespace dependency",
            )
        return

    if type(record) is PredicateIdentity:
        action_root = _require_ref(
            owner_path=f"{path}.action_root_id",
            reference=record.action_root_id,
            expected_type=ActionRootIdentity,
            resources_by_id=resources_by_id,
            issues=issues,
        )
        if action_root is not None and action_root.namespace_id != record.namespace_id:
            _add(
                issues,
                f"{path}.action_root_id",
                PredicateGovernanceValidationCode.CROSS_NAMESPACE_REFERENCE,
                "predicate and action root must use the same namespace identity",
            )
        unavailable_states = {
            PredicateLifecycleState.DEPRECATED,
            PredicateLifecycleState.REJECTED,
            PredicateLifecycleState.WITHDRAWN,
            PredicateLifecycleState.SUPERSEDED,
        }
        if action_root is not None and action_root.lifecycle_state in unavailable_states:
            _add(
                issues,
                f"{path}.action_root_id",
                PredicateGovernanceValidationCode.UNRESOLVED_DEPENDENCY,
                "predicate cannot depend on a deprecated or terminally unavailable action root",
            )
        if namespace is not None and namespace.lifecycle_state in unavailable_states:
            _add(
                issues,
                f"{path}.namespace_id",
                PredicateGovernanceValidationCode.UNRESOLVED_DEPENDENCY,
                "predicate cannot depend on a deprecated or terminally unavailable namespace",
            )
        if (
            record.lifecycle_state in active_lifecycle_states()
            and action_root is not None
            and action_root.lifecycle_state not in active_lifecycle_states()
        ):
            _add(
                issues,
                f"{path}.action_root_id",
                PredicateGovernanceValidationCode.UNRESOLVED_DEPENDENCY,
                "admitted predicate requires an admitted action-root dependency",
            )
        if (
            record.lifecycle_state in active_lifecycle_states()
            and namespace is not None
            and namespace.lifecycle_state not in active_lifecycle_states()
        ):
            _add(
                issues,
                f"{path}.namespace_id",
                PredicateGovernanceValidationCode.UNRESOLVED_DEPENDENCY,
                "admitted predicate requires an admitted namespace dependency",
            )


def validate_governance_batch(
    batch: object,
) -> PredicateGovernanceValidationReport:
    issues: list[PredicateGovernanceValidationIssue] = []
    shape = validate_governance_batch_shape(batch)
    _extend(issues, "batch", shape.issues)
    if type(batch) is not PredicateGovernanceBatch:
        return report_from_issues(issues)
    if not all(
        type(getattr(batch, field)) is tuple
        for field in (
            "provenance_records",
            "resources",
            "authority_records",
            "transitions",
        )
    ):
        return report_from_issues(issues)

    indexed_provenance = _index_unique(
        batch.provenance_records,
        id_getter=lambda item: item.provenance_id,
        path_prefix="provenance_records",
        duplicate_code=PredicateGovernanceValidationCode.DUPLICATE_PROVENANCE_ID,
        issues=issues,
    )
    indexed_resources = _index_unique(
        batch.resources,
        id_getter=resource_id,
        path_prefix="resources",
        duplicate_code=PredicateGovernanceValidationCode.DUPLICATE_RESOURCE_ID,
        issues=issues,
    )
    indexed_authorities = _index_unique(
        batch.authority_records,
        id_getter=lambda item: item.authority_id,
        path_prefix="authority_records",
        duplicate_code=PredicateGovernanceValidationCode.DUPLICATE_AUTHORITY_ID,
        issues=issues,
    )
    indexed_transitions = _index_unique(
        batch.transitions,
        id_getter=lambda item: item.transition_id,
        path_prefix="transitions",
        duplicate_code=PredicateGovernanceValidationCode.DUPLICATE_TRANSITION_ID,
        issues=issues,
    )

    typed_provenance: dict[str, PredicateProvenanceReference] = {}
    for position, provenance in enumerate(batch.provenance_records):
        provenance_report = validate_provenance_record(provenance)
        _extend(
            issues,
            f"provenance_records[{position}]",
            provenance_report.issues,
        )
        if (
            provenance_report.ok
            and type(provenance) is PredicateProvenanceReference
            and type(provenance.provenance_id) is str
            and indexed_provenance.get(provenance.provenance_id) is provenance
        ):
            typed_provenance[provenance.provenance_id] = provenance

    typed_resources: dict[str, GovernedPredicateResource] = {}
    for position, record in enumerate(batch.resources):
        report = validate_governed_resource(
            record,
            provenance_by_id=typed_provenance,
        )
        _extend(issues, f"resources[{position}]", report.issues)
        if (
            report.ok
            and type(record) in (
                PredicateNamespaceIdentity,
                ActionRootIdentity,
                PredicateIdentity,
            )
        ):
            identity = resource_id(record)
            if indexed_resources.get(identity) is record:
                typed_resources[identity] = record

    for position, record in enumerate(typed_resources.values()):
        _validate_resource_references(
            record,
            path=f"resources[{position}]",
            resources_by_id=typed_resources,
            issues=issues,
        )

    typed_authorities: dict[str, PredicateLifecycleAuthorityRecord] = {}
    for position, authority in enumerate(batch.authority_records):
        authority_report = validate_lifecycle_authority_record(
            authority,
            provenance_by_id=typed_provenance,
        )
        _extend(
            issues,
            f"authority_records[{position}]",
            authority_report.issues,
        )
        if (
            authority_report.ok
            and type(authority) is PredicateLifecycleAuthorityRecord
            and type(authority.authority_id) is str
            and indexed_authorities.get(authority.authority_id) is authority
        ):
            typed_authorities[authority.authority_id] = authority

    typed_transitions: dict[str, PredicateLifecycleTransitionRecord] = {}
    for position, transition in enumerate(batch.transitions):
        transition_report = validate_lifecycle_transition_record_shape(transition)
        _extend(
            issues,
            f"transitions[{position}]",
            transition_report.issues,
        )
        if (
            transition_report.ok
            and type(transition) is PredicateLifecycleTransitionRecord
            and type(transition.transition_id) is str
            and indexed_transitions.get(transition.transition_id) is transition
        ):
            typed_transitions[transition.transition_id] = transition

    lineage_version_index: dict[tuple[str, tuple[int, int, int]], object] = {}
    lineage_records: dict[str, list[GovernedPredicateResource]] = defaultdict(list)
    for position, record in enumerate(typed_resources.values()):
        try:
            lineage = expected_resource_lineage_id(record)
            parsed_version = parse_resource_version(record.version)
        except Exception:
            continue
        key = (lineage, parsed_version)
        existing = lineage_version_index.get(key)
        if existing is not None:
            code = (
                PredicateGovernanceValidationCode.EXACT_DUPLICATE_RECORD
                if existing == record
                else PredicateGovernanceValidationCode.CONFLICTING_LINEAGE_VERSION
            )
            _add(
                issues,
                f"resources[{position}]",
                code,
                f"lineage {lineage!r} already has version {record.version!r}",
            )
        else:
            lineage_version_index[key] = record
        lineage_records[lineage].append(record)

    incoming: dict[str, list[object]] = defaultdict(list)
    outgoing: dict[str, list[object]] = defaultdict(list)
    accepted_transitions: dict[str, object] = {}

    for position, transition in enumerate(typed_transitions.values()):
        path = f"transitions[{position}]"
        source = typed_resources.get(transition.source_resource_id)
        target = typed_resources.get(transition.target_resource_id)
        authority = typed_authorities.get(transition.authority_record_ref)

        if source is None:
            _add(
                issues,
                f"{path}.source_resource_id",
                PredicateGovernanceValidationCode.REFERENCE_NOT_FOUND,
                "source resource is absent",
            )
        if target is None:
            _add(
                issues,
                f"{path}.target_resource_id",
                PredicateGovernanceValidationCode.REFERENCE_NOT_FOUND,
                "target resource is absent",
            )
        if authority is None:
            _add(
                issues,
                f"{path}.authority_record_ref",
                PredicateGovernanceValidationCode.AUTHORITY_RECORD_NOT_FOUND,
                "authority record is absent",
            )
        if source is None or target is None or authority is None:
            continue

        decision = evaluate_lifecycle_transition(
            source,
            target,
            transition,
            authority,
            provenance_by_id=typed_provenance,
        )
        _extend(issues, path, decision.issues)
        if decision.allowed:
            incoming[resource_id(target)].append(transition)
            outgoing[resource_id(source)].append(transition)
            accepted_transitions[transition.transition_id] = transition

    for identity, records in incoming.items():
        if len(records) > 1:
            _add(
                issues,
                f"resource[{identity}].incoming",
                PredicateGovernanceValidationCode.MULTIPLE_INCOMING_TRANSITIONS,
                "a resource version may have only one incoming transition",
            )
    for identity, records in outgoing.items():
        if len(records) > 1:
            _add(
                issues,
                f"resource[{identity}].outgoing",
                PredicateGovernanceValidationCode.MULTIPLE_OUTGOING_TRANSITIONS,
                "a resource version may have only one outgoing transition",
            )

    for transition in accepted_transitions.values():
        if transition.transition_kind is PredicateLifecycleTransitionKind.REOPEN_REVIEW:
            prior = accepted_transitions.get(
                transition.prior_disposition_transition_ref or ""
            )
            if (
                prior is None
                or prior.target_resource_id != transition.source_resource_id
                or prior.transition_kind
                not in {
                    PredicateLifecycleTransitionKind.REJECTION,
                    PredicateLifecycleTransitionKind.WITHDRAWAL,
                }
                or prior.to_state
                not in {
                    PredicateLifecycleState.REJECTED,
                    PredicateLifecycleState.WITHDRAWN,
                }
            ):
                _add(
                    issues,
                    f"transition[{transition.transition_id}].prior_disposition_transition_ref",
                    PredicateGovernanceValidationCode.HISTORICAL_ANCESTRY_REQUIRED,
                    "reopening must reference the accepted transition that created the exact rejected or withdrawn source record",
                )
            elif prior.authority_record_ref == transition.authority_record_ref:
                _add(
                    issues,
                    f"transition[{transition.transition_id}].authority_record_ref",
                    PredicateGovernanceValidationCode.AUTHORITY_BINDING_MISMATCH,
                    "reopening requires a distinct new authority record",
                )

        if transition.transition_kind is PredicateLifecycleTransitionKind.RELEASE_TO_REVIEW:
            source_incoming = incoming.get(transition.source_resource_id, [])
            prior = source_incoming[0] if len(source_incoming) == 1 else None
            if (
                prior is None
                or prior.transition_kind
                not in {
                    PredicateLifecycleTransitionKind.QUARANTINE,
                    PredicateLifecycleTransitionKind.CONTINUE_QUARANTINE,
                }
                or prior.to_state is not PredicateLifecycleState.QUARANTINED
            ):
                _add(
                    issues,
                    f"transition[{transition.transition_id}].resolved_quarantine_cause_refs",
                    PredicateGovernanceValidationCode.QUARANTINE_CAUSE_UNRESOLVED,
                    "quarantine release requires accepted quarantine ancestry for the exact source record",
                )
            elif frozenset(transition.resolved_quarantine_cause_refs) != frozenset(
                prior.quarantine_cause_refs
            ):
                _add(
                    issues,
                    f"transition[{transition.transition_id}].resolved_quarantine_cause_refs",
                    PredicateGovernanceValidationCode.QUARANTINE_CAUSE_UNRESOLVED,
                    "release must resolve every current quarantine cause and may not substitute unrelated causes",
                )
            elif frozenset(
                transition.quarantine_release_requirement_refs
            ) != frozenset(prior.quarantine_release_requirement_refs):
                _add(
                    issues,
                    f"transition[{transition.transition_id}].quarantine_release_requirement_refs",
                    PredicateGovernanceValidationCode.QUARANTINE_RELEASE_REQUIREMENT_REQUIRED,
                    "release must satisfy every current quarantine release requirement and may not substitute unrelated requirements",
                )

    for identity, record in typed_resources.items():
        if record.lifecycle_state not in active_lifecycle_states():
            continue

        dependency_refs: tuple[tuple[str, str], ...]
        if type(record) is PredicateNamespaceIdentity:
            dependency_refs = ()
        elif type(record) is ActionRootIdentity:
            dependency_refs = (("namespace_id", record.namespace_id),)
        else:
            dependency_refs = (
                ("namespace_id", record.namespace_id),
                ("action_root_id", record.action_root_id),
            )

        for field_name, dependency_ref in dependency_refs:
            dependency = typed_resources.get(dependency_ref)
            if dependency is None:
                continue
            if outgoing.get(resource_id(dependency)):
                _add(
                    issues,
                    f"resource[{identity}].{field_name}",
                    PredicateGovernanceValidationCode.UNRESOLVED_DEPENDENCY,
                    "active resources must reference the current terminal version of every governed dependency",
                )

    for lineage, records in lineage_records.items():
        ordered = sorted(records, key=lambda item: parse_resource_version(item.version))
        for index, record in enumerate(ordered):
            identity = resource_id(record)
            if index == 0:
                if not incoming.get(identity) and record.lifecycle_state not in _ALLOWED_INITIAL_STATES:
                    _add(
                        issues,
                        f"lineage[{lineage}].{record.version}",
                        PredicateGovernanceValidationCode.ADMISSION_HISTORY_REQUIRED,
                        "initial admitted, reviewed, withdrawn, rejected, deprecated, or superseded state requires ancestry",
                    )
            elif not incoming.get(identity):
                _add(
                    issues,
                    f"lineage[{lineage}].{record.version}",
                    PredicateGovernanceValidationCode.ORPHAN_RESOURCE_VERSION,
                    "non-initial version has no incoming transition",
                )

        terminal = [record for record in ordered if not outgoing.get(resource_id(record))]
        if len(terminal) > 1:
            _add(
                issues,
                f"lineage[{lineage}]",
                PredicateGovernanceValidationCode.CURRENT_ACTIVE_CONFLICT,
                "lineage has multiple terminal versions",
            )
        active_terminal = [
            record
            for record in terminal
            if record.lifecycle_state in active_lifecycle_states()
        ]
        if len(active_terminal) > 1:
            _add(
                issues,
                f"lineage[{lineage}]",
                PredicateGovernanceValidationCode.CURRENT_ACTIVE_CONFLICT,
                "lineage has multiple active terminal versions",
            )

        for record in ordered:
            if record.lifecycle_state not in active_lifecycle_states():
                continue
            identity = resource_id(record)
            ancestry_kinds = set()
            cursor = identity
            seen: set[str] = set()
            while cursor in incoming and cursor not in seen:
                seen.add(cursor)
                transition = incoming[cursor][0]
                ancestry_kinds.add(transition.transition_kind)
                cursor = transition.source_resource_id
            if not (ancestry_kinds & _ADMISSION_KINDS):
                _add(
                    issues,
                    f"resource[{identity}]",
                    PredicateGovernanceValidationCode.ADMISSION_HISTORY_REQUIRED,
                    "active lifecycle state requires explicit reviewed admission ancestry",
                )

    for transition in batch.transitions:
        if type(transition) is not PredicateLifecycleTransitionRecord:
            continue
        if transition.transition_id not in accepted_transitions:
            continue
        if transition.superseding_resource_ref is None:
            continue
        successor = typed_resources.get(transition.superseding_resource_ref)
        source = typed_resources.get(transition.source_resource_id)
        if successor is None:
            _add(
                issues,
                f"transition[{transition.transition_id}].superseding_resource_ref",
                PredicateGovernanceValidationCode.REFERENCE_NOT_FOUND,
                "successor resource is absent from the batch",
            )
            continue
        if source is not None and type(successor) is not type(source):
            _add(
                issues,
                f"transition[{transition.transition_id}].superseding_resource_ref",
                PredicateGovernanceValidationCode.SUPERSEDING_RESOURCE_INVALID,
                "successor must have the same exact resource family",
            )
        if source is not None and expected_resource_lineage_id(successor) == expected_resource_lineage_id(source):
            _add(
                issues,
                f"transition[{transition.transition_id}].superseding_resource_ref",
                PredicateGovernanceValidationCode.SUPERSEDING_RESOURCE_INVALID,
                "successor must be a distinct canonical lineage",
            )
        if successor.lifecycle_state not in active_lifecycle_states():
            _add(
                issues,
                f"transition[{transition.transition_id}].superseding_resource_ref",
                PredicateGovernanceValidationCode.SUPERSEDING_RESOURCE_INVALID,
                "successor must already be explicitly admitted within the batch",
            )
        authority = typed_authorities.get(transition.authority_record_ref)
        if (
            type(authority) is PredicateLifecycleAuthorityRecord
            and transition.superseding_resource_ref
            not in authority.affected_record_refs
        ):
            _add(
                issues,
                f"transition[{transition.transition_id}].superseding_resource_ref",
                PredicateGovernanceValidationCode.AUTHORITY_BINDING_MISMATCH,
                "supersession authority must explicitly name the successor resource",
            )

    return report_from_issues(issues)


def assert_governance_batch(
    batch: object,
) -> PredicateGovernanceValidationReport:
    report = validate_governance_batch(batch)
    if not report.ok:
        raise PredicateGovernanceValidationError(report)
    return report
