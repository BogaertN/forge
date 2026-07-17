"""Total fail-closed validators for Slice 38G candidate records."""

from __future__ import annotations

from typing import Any, Callable

from ...controlled_concept_sense_registry.built_in_registry import (
    built_in_registry,
)
from ...controlled_concept_sense_registry.sense_term_mapping_registry import (
    sense_term_mapping_registry,
)
from ..built_in_action_root_registry import built_in_action_root_registry
from ..capability_family_reference_registry import (
    capability_family_reference_registry,
)
from ..participant_role_registry import participant_role_registry
from ..predicate_frame_registry import predicate_frame_registry
from .authority import SLICE38G_NON_AUTHORITY_BOUNDARIES
from .schema import (
    ActionRootCompatibilityConflict,
    ActionRootCompatibilityRule,
    ActionRootPredicateCandidate,
    CandidateProposalStatus,
    CandidateStructuralState,
    CandidateValidationCode as C,
    CandidateValidationError,
    CandidateValidationIssue,
    CandidateValidationReport,
    CapabilityReferenceCandidate,
    CompatibilityLifecycleState,
    CompatibilityMatchMode,
    CompatibilityRegistrySnapshot,
    PredicateRoleFrameCandidateProposalResult,
    PredicateRoleFrameProposalProfile,
    RoleLayoutCandidate,
    ACTION_PREDICATE_CANDIDATE_SCHEMA_ID,
    CAPABILITY_REFERENCE_CANDIDATE_SCHEMA_ID,
    COMPATIBILITY_CONFLICT_SCHEMA_ID,
    COMPATIBILITY_RULE_SCHEMA_ID,
    COMPATIBILITY_SNAPSHOT_SCHEMA_ID,
    PROFILE_SCHEMA_ID,
    RESULT_SCHEMA_ID,
    ROLE_LAYOUT_CANDIDATE_SCHEMA_ID,
    SLICE38G_SCHEMA_VERSION,
    SLICE38G_SPEC_ID,
    SLICE38G_SPEC_VERSION,
    SLICE38_SNAPSHOT_SCHEMA_ID,
    Slice38RegistrySnapshotIdentity,
)


def _issue(
    issues: list[CandidateValidationIssue],
    path: str,
    code: C,
    detail: str,
) -> None:
    issues.append(CandidateValidationIssue(path=path, code=code, detail=detail))


def _report(issues: list[CandidateValidationIssue]) -> CandidateValidationReport:
    return CandidateValidationReport(ok=not issues, issues=tuple(issues))


def _total(
    validator: Callable[[object], CandidateValidationReport],
    value: object,
) -> CandidateValidationReport:
    try:
        return validator(value)
    except Exception as error:
        return CandidateValidationReport(
            ok=False,
            issues=(
                CandidateValidationIssue(
                    path="$",
                    code=C.VALIDATOR_FAILED_CLOSED,
                    detail=(
                        "validation failed closed without accepting malformed "
                        f"custody: {type(error).__name__}"
                    ),
                ),
            ),
        )


def _text(
    issues: list[CandidateValidationIssue],
    path: str,
    value: Any,
    *,
    allow_empty: bool = False,
) -> bool:
    if type(value) is not str:
        _issue(issues, path, C.TYPE_MISMATCH, "exact str required")
        return False
    if value != value.strip():
        _issue(issues, path, C.INVALID_TEXT, "text must be exactly trimmed")
        return False
    if not allow_empty and not value:
        _issue(issues, path, C.INVALID_TEXT, "non-empty text required")
        return False
    return True


def _bool(
    issues: list[CandidateValidationIssue],
    path: str,
    value: Any,
    expected: bool,
) -> None:
    if type(value) is not bool or value is not expected:
        _issue(
            issues,
            path,
            C.AUTHORITY_BOUNDARY_VIOLATION,
            f"exact bool {expected!r} required",
        )


def _count(
    issues: list[CandidateValidationIssue],
    path: str,
    value: Any,
    *,
    expected: int | None = None,
) -> bool:
    if type(value) is not int or value < 0:
        _issue(issues, path, C.TYPE_MISMATCH, "exact non-negative int required")
        return False
    if expected is not None and value != expected:
        _issue(issues, path, C.COUNT_MISMATCH, f"exact count {expected} required")
        return False
    return True


def _enum(
    issues: list[CandidateValidationIssue],
    path: str,
    value: Any,
    enum_type: type,
) -> bool:
    if type(value) is not enum_type:
        _issue(issues, path, C.INVALID_ENUM, f"exact {enum_type.__name__} required")
        return False
    return True


def _tuple(
    issues: list[CandidateValidationIssue],
    path: str,
    value: Any,
    *,
    item_type: type | None = str,
    allow_empty: bool = True,
    unique: bool = True,
) -> tuple[Any, ...]:
    if type(value) is not tuple:
        _issue(issues, path, C.INVALID_TUPLE, "exact tuple required")
        return ()
    safe: list[Any] = []
    for index, item in enumerate(value):
        if item_type is str:
            if _text(issues, f"{path}[{index}]", item):
                safe.append(item)
        elif item_type is not None:
            if type(item) is not item_type:
                _issue(
                    issues,
                    f"{path}[{index}]",
                    C.TYPE_MISMATCH,
                    f"exact {item_type.__name__} required",
                )
            else:
                safe.append(item)
        else:
            safe.append(item)
    if not allow_empty and not safe:
        _issue(issues, path, C.INVALID_TUPLE, "tuple must not be empty")
    if unique:
        try:
            if len(safe) != len(set(safe)):
                _issue(issues, path, C.DUPLICATE_VALUE, "duplicate values prohibited")
        except Exception:
            _issue(issues, path, C.VALIDATOR_FAILED_CLOSED, "uniqueness check failed closed")
    return tuple(safe)


def _pairs(
    issues: list[CandidateValidationIssue],
    path: str,
    value: Any,
) -> tuple[tuple[str, str], ...]:
    if type(value) is not tuple:
        _issue(issues, path, C.INVALID_TUPLE, "exact tuple required")
        return ()
    safe: list[tuple[str, str]] = []
    for index, item in enumerate(value):
        if type(item) is not tuple or len(item) != 2:
            _issue(issues, f"{path}[{index}]", C.INVALID_TUPLE, "exact pair required")
            continue
        left, right = item
        if _text(issues, f"{path}[{index}][0]", left) and _text(
            issues, f"{path}[{index}][1]", right
        ):
            safe.append((left, right))
    try:
        if len(safe) != len(set(safe)):
            _issue(issues, path, C.DUPLICATE_VALUE, "duplicate pairs prohibited")
    except Exception:
        _issue(issues, path, C.VALIDATOR_FAILED_CLOSED, "pair uniqueness failed closed")
    return tuple(safe)


def _role_triples(
    issues: list[CandidateValidationIssue],
    path: str,
    value: Any,
) -> tuple[tuple[str, str, str], ...]:
    if type(value) is not tuple:
        _issue(issues, path, C.INVALID_TUPLE, "exact tuple required")
        return ()
    safe: list[tuple[str, str, str]] = []
    for index, item in enumerate(value):
        if type(item) is not tuple or len(item) != 3:
            _issue(issues, f"{path}[{index}]", C.INVALID_TUPLE, "exact role triple required")
            continue
        if all(
            _text(issues, f"{path}[{index}][{part}]", item[part])
            for part in range(3)
        ):
            safe.append(item)
    try:
        if len(safe) != len(set(safe)):
            _issue(issues, path, C.DUPLICATE_VALUE, "duplicate role triples prohibited")
    except Exception:
        _issue(issues, path, C.VALIDATOR_FAILED_CLOSED, "role uniqueness failed closed")
    return tuple(safe)


def _identity(
    issues: list[CandidateValidationIssue],
    path: str,
    record: object,
    field_name: str,
) -> None:
    try:
        expected = record.expected_id()  # type: ignore[attr-defined]
    except Exception as error:
        _issue(
            issues,
            path,
            C.IDENTITY_MISMATCH,
            f"canonical identity failed closed: {type(error).__name__}",
        )
        return
    actual = getattr(record, field_name, None)
    if type(actual) is not str or actual != expected:
        _issue(issues, path, C.IDENTITY_MISMATCH, "canonical identifier mismatch")


def _schema(issues: list[CandidateValidationIssue], path: str, record: object) -> None:
    if getattr(record, "schema_version", None) != SLICE38G_SCHEMA_VERSION:
        _issue(issues, path, C.SCHEMA_VERSION_MISMATCH, "Slice 38G schema required")


def _exact_constant(
    issues: list[CandidateValidationIssue],
    path: str,
    value: Any,
    expected: str,
) -> None:
    if type(value) is not str or value != expected:
        _issue(issues, path, C.SCHEMA_VERSION_MISMATCH, f"exact constant {expected!r} required")


def _validate_profile(value: object) -> CandidateValidationReport:
    issues: list[CandidateValidationIssue] = []
    if type(value) is not PredicateRoleFrameProposalProfile:
        _issue(issues, "$", C.TYPE_MISMATCH, "PredicateRoleFrameProposalProfile required")
        return _report(issues)
    _identity(issues, "profile_id", value, "profile_id")
    _schema(issues, "schema_version", value)
    _exact_constant(issues, "spec_id", value.spec_id, SLICE38G_SPEC_ID)
    _exact_constant(issues, "spec_version", value.spec_version, SLICE38G_SPEC_VERSION)
    _exact_constant(issues, "profile_schema_id", value.profile_schema_id, PROFILE_SCHEMA_ID)
    _text(issues, "profile_key", value.profile_key)
    _text(issues, "profile_version", value.profile_version)
    for name in (
        "explicit_invocation_required",
        "offline_only",
        "standard_library_only",
        "deterministic",
        "immutable_records",
        "exact_source_ancestry_required",
        "exact_registry_snapshot_required",
        "exact_identity_lookup_only",
        "zero_one_many_preserved",
        "unresolved_alternatives_preserved",
        "explicit_unknown_required",
        "explicit_unsupported_required",
        "incomplete_state_required",
        "conflict_state_required",
    ):
        _bool(issues, name, getattr(value, name), True)
    for name in (
        "caller_supplied_surface_hint_allowed",
        "normalization_allowed",
        "nearest_known_substitution_allowed",
        "semantic_similarity_allowed",
        "language_model_allowed",
        "selected_predicate_allowed",
        "selected_frame_allowed",
        "selected_participant_assignment_allowed",
        "candidate_meaning_creation_allowed",
        "selected_meaning_allowed",
        "permission_inference_allowed",
        "route_creation_allowed",
        "tool_invocation_allowed",
        "action_execution_allowed",
        "memory_access_allowed",
        "delivery_allowed",
        "evidence_validity_allowed",
        "truth_determination_allowed",
        "clarification_outcome_allowed",
        "refusal_outcome_allowed",
        "blocked_progression_outcome_allowed",
    ):
        _bool(issues, name, getattr(value, name), False)
    if value.non_authority_boundaries != SLICE38G_NON_AUTHORITY_BOUNDARIES:
        _issue(issues, "non_authority_boundaries", C.AUTHORITY_BOUNDARY_VIOLATION, "exact boundary set required")
    return _report(issues)


def validate_profile(value: object) -> CandidateValidationReport:
    return _total(_validate_profile, value)


def _current_maps() -> dict[str, dict[str, object]]:
    concepts = built_in_registry().admitted_concepts
    senses = sense_term_mapping_registry().senses
    action = built_in_action_root_registry()
    roles = participant_role_registry().admitted_roles
    frames = predicate_frame_registry().admitted_frames
    caps = capability_family_reference_registry()
    return {
        "concept": {item.concept_id: item for item in concepts},
        "sense": {item.sense_id: item for item in senses},
        "root": {item.action_root_id: item for item in action.admitted_action_roots},
        "predicate": {item.predicate_id: item for item in action.admitted_predicates},
        "role": {item.role_id: item for item in roles},
        "frame": {item.frame_id: item for item in frames},
        "effect": {item.effect_boundary_id: item for item in caps.effect_boundaries},
        "capability": {item.capability_family_id: item for item in caps.capability_families},
        "frame_effect": {
            item.frame_effect_reference_id: item for item in caps.frame_effect_references
        },
        "frame_cap": {
            item.frame_capability_reference_id: item
            for item in caps.frame_capability_references
        },
    }


def _validate_rule(value: object) -> CandidateValidationReport:
    issues: list[CandidateValidationIssue] = []
    if type(value) is not ActionRootCompatibilityRule:
        _issue(issues, "$", C.TYPE_MISMATCH, "ActionRootCompatibilityRule required")
        return _report(issues)
    _identity(issues, "rule_id", value, "rule_id")
    _schema(issues, "schema_version", value)
    _exact_constant(issues, "rule_schema_id", value.rule_schema_id, COMPATIBILITY_RULE_SCHEMA_ID)
    _text(issues, "rule_key", value.rule_key)
    _enum(issues, "match_mode", value.match_mode, CompatibilityMatchMode)
    _enum(issues, "lifecycle_state", value.lifecycle_state, CompatibilityLifecycleState)
    _text(issues, "version", value.version)
    _tuple(issues, "allowed_frame_ids", value.allowed_frame_ids, allow_empty=False)
    _tuple(issues, "scope_tags", value.scope_tags, allow_empty=False)
    _tuple(issues, "provenance_refs", value.provenance_refs, allow_empty=False)
    _tuple(issues, "conflict_refs", value.conflict_refs)
    for name, expected in (
        ("candidate_only", True),
        ("selection_authority", False),
        ("permission_authority", False),
        ("route_authority", False),
        ("execution_authority", False),
    ):
        _bool(issues, name, getattr(value, name), expected)

    maps = _current_maps()
    concept = maps["concept"].get(value.concept_id) if type(value.concept_id) is str else None
    sense = maps["sense"].get(value.sense_id) if type(value.sense_id) is str else None
    root = maps["root"].get(value.action_root_id) if type(value.action_root_id) is str else None
    predicate = maps["predicate"].get(value.predicate_id) if type(value.predicate_id) is str else None

    if value.match_mode is CompatibilityMatchMode.EXACT_CONCEPT:
        if concept is None or value.sense_id is not None or value.sense_version is not None:
            _issue(issues, "match_mode", C.CROSS_REGISTRY_MISMATCH, "exact concept mode requires concept only")
    elif value.match_mode is CompatibilityMatchMode.EXACT_SENSE:
        if sense is None or value.concept_id is not None or value.concept_version is not None:
            _issue(issues, "match_mode", C.CROSS_REGISTRY_MISMATCH, "exact sense mode requires sense only")
    elif value.match_mode is CompatibilityMatchMode.EXACT_CONCEPT_AND_SENSE:
        if concept is None or sense is None or getattr(sense, "concept_id", None) != value.concept_id:
            _issue(issues, "match_mode", C.CROSS_REGISTRY_MISMATCH, "exact concept-and-sense pair required")

    if concept is not None and getattr(concept, "version", None) != value.concept_version:
        _issue(issues, "concept_version", C.REFERENCE_VERSION_MISMATCH, "concept version mismatch")
    if sense is not None and getattr(sense, "version", None) != value.sense_version:
        _issue(issues, "sense_version", C.REFERENCE_VERSION_MISMATCH, "sense version mismatch")
    if root is None:
        _issue(issues, "action_root_id", C.REFERENCE_NOT_FOUND, "admitted action root required")
    else:
        if root.action_root_key != value.action_root_key or root.version != value.action_root_version:
            _issue(issues, "action_root", C.CROSS_REGISTRY_MISMATCH, "action-root identity/key/version mismatch")
    if predicate is None:
        _issue(issues, "predicate_id", C.REFERENCE_NOT_FOUND, "admitted predicate required")
    else:
        if (
            predicate.predicate_key != value.predicate_key
            or predicate.version != value.predicate_version
            or predicate.action_root_id != value.action_root_id
        ):
            _issue(issues, "predicate", C.CROSS_REGISTRY_MISMATCH, "predicate identity/key/version/root mismatch")
    for index, frame_id in enumerate(value.allowed_frame_ids if type(value.allowed_frame_ids) is tuple else ()):
        frame = maps["frame"].get(frame_id)
        if frame is None:
            _issue(issues, f"allowed_frame_ids[{index}]", C.REFERENCE_NOT_FOUND, "admitted frame required")
        elif frame.linked_action_root_id != value.action_root_id or frame.linked_predicate_id != value.predicate_id:
            _issue(issues, f"allowed_frame_ids[{index}]", C.CROSS_REGISTRY_MISMATCH, "frame must link exact root and predicate")
    return _report(issues)


def validate_rule(value: object) -> CandidateValidationReport:
    return _total(_validate_rule, value)


def _validate_conflict(value: object) -> CandidateValidationReport:
    issues: list[CandidateValidationIssue] = []
    if type(value) is not ActionRootCompatibilityConflict:
        _issue(issues, "$", C.TYPE_MISMATCH, "ActionRootCompatibilityConflict required")
        return _report(issues)
    _identity(issues, "conflict_id", value, "conflict_id")
    _schema(issues, "schema_version", value)
    _exact_constant(issues, "conflict_schema_id", value.conflict_schema_id, COMPATIBILITY_CONFLICT_SCHEMA_ID)
    _text(issues, "conflict_key", value.conflict_key)
    _text(issues, "conflict_kind", value.conflict_kind)
    _text(issues, "reason", value.reason)
    _text(issues, "version", value.version)
    _tuple(issues, "rule_refs", value.rule_refs, allow_empty=False)
    if type(value.rule_refs) is tuple and len(value.rule_refs) < 2:
        _issue(issues, "rule_refs", C.INVALID_TUPLE, "at least two rule refs required")
    _tuple(issues, "concept_refs", value.concept_refs)
    _tuple(issues, "sense_refs", value.sense_refs)
    _tuple(issues, "action_root_refs", value.action_root_refs, allow_empty=False)
    _tuple(issues, "scope_tags", value.scope_tags, allow_empty=False)
    _tuple(issues, "provenance_refs", value.provenance_refs, allow_empty=False)
    _enum(issues, "lifecycle_state", value.lifecycle_state, CompatibilityLifecycleState)
    _bool(issues, "operative", value.operative, False)
    _bool(issues, "resolved", value.resolved, False)
    if value.selected_rule_ref is not None:
        _issue(issues, "selected_rule_ref", C.AUTHORITY_BOUNDARY_VIOLATION, "conflict may not select a rule")
    return _report(issues)


def validate_conflict(value: object) -> CandidateValidationReport:
    return _total(_validate_conflict, value)


def _validate_compatibility_snapshot(value: object) -> CandidateValidationReport:
    issues: list[CandidateValidationIssue] = []
    if type(value) is not CompatibilityRegistrySnapshot:
        _issue(issues, "$", C.TYPE_MISMATCH, "CompatibilityRegistrySnapshot required")
        return _report(issues)
    _identity(issues, "snapshot_id", value, "snapshot_id")
    _schema(issues, "schema_version", value)
    _exact_constant(issues, "snapshot_schema_id", value.snapshot_schema_id, COMPATIBILITY_SNAPSHOT_SCHEMA_ID)
    _text(issues, "registry_key", value.registry_key)
    _text(issues, "registry_version", value.registry_version)
    rules = _tuple(issues, "rules", value.rules, item_type=ActionRootCompatibilityRule)
    conflicts = _tuple(issues, "conflicts", value.conflicts, item_type=ActionRootCompatibilityConflict)
    rule_refs = _tuple(issues, "rule_refs", value.rule_refs)
    conflict_refs = _tuple(issues, "conflict_refs", value.conflict_refs)
    _count(issues, "rule_count", value.rule_count, expected=len(rules))
    _count(issues, "conflict_count", value.conflict_count, expected=len(conflicts))
    if value.rule_refs != tuple(item.rule_id for item in rules):
        _issue(issues, "rule_refs", C.COUNT_MISMATCH, "rule refs must match rules exactly")
    if value.conflict_refs != tuple(item.conflict_id for item in conflicts):
        _issue(issues, "conflict_refs", C.COUNT_MISMATCH, "conflict refs must match conflicts exactly")
    for index, rule in enumerate(rules):
        report = validate_rule(rule)
        for item in report.issues:
            _issue(issues, f"rules[{index}].{item.path}", item.code, item.detail)
    known_rule_refs = set(rule_refs)
    for index, conflict in enumerate(conflicts):
        report = validate_conflict(conflict)
        for item in report.issues:
            _issue(issues, f"conflicts[{index}].{item.path}", item.code, item.detail)
        try:
            if not set(conflict.rule_refs).issubset(known_rule_refs):
                _issue(issues, f"conflicts[{index}].rule_refs", C.REFERENCE_NOT_FOUND, "conflict references unknown rule")
        except Exception:
            _issue(issues, f"conflicts[{index}].rule_refs", C.VALIDATOR_FAILED_CLOSED, "conflict reference comparison failed closed")
    known_conflicts = set(conflict_refs)
    for index, rule in enumerate(rules):
        try:
            if not set(rule.conflict_refs).issubset(known_conflicts):
                _issue(issues, f"rules[{index}].conflict_refs", C.REFERENCE_NOT_FOUND, "rule references unknown conflict")
        except Exception:
            _issue(issues, f"rules[{index}].conflict_refs", C.VALIDATOR_FAILED_CLOSED, "rule conflict comparison failed closed")
    for name, expected in (
        ("exact_identity_lookup_only", True),
        ("closed_world", True),
        ("runtime_mutation_allowed", False),
        ("automatic_mapping_allowed", False),
        ("nearest_known_substitution_allowed", False),
        ("semantic_similarity_allowed", False),
        ("language_model_allowed", False),
        ("selection_authority", False),
        ("permission_authority", False),
        ("route_authority", False),
        ("execution_authority", False),
    ):
        _bool(issues, name, getattr(value, name), expected)
    _tuple(issues, "provenance_refs", value.provenance_refs, allow_empty=False)
    return _report(issues)


def validate_compatibility_snapshot(value: object) -> CandidateValidationReport:
    return _total(_validate_compatibility_snapshot, value)


def _validate_slice38_snapshot(value: object) -> CandidateValidationReport:
    issues: list[CandidateValidationIssue] = []
    if type(value) is not Slice38RegistrySnapshotIdentity:
        _issue(issues, "$", C.TYPE_MISMATCH, "Slice38RegistrySnapshotIdentity required")
        return _report(issues)
    _identity(issues, "snapshot_id", value, "snapshot_id")
    _schema(issues, "schema_version", value)
    _exact_constant(issues, "snapshot_schema_id", value.snapshot_schema_id, SLICE38_SNAPSHOT_SCHEMA_ID)
    from .snapshot import build_slice38_registry_snapshot
    expected = build_slice38_registry_snapshot()
    if value != expected:
        _issue(issues, "$", C.SNAPSHOT_MISMATCH, "exact accepted Slice 38 registry snapshot required")
    return _report(issues)


def validate_slice38_snapshot(value: object) -> CandidateValidationReport:
    return _total(_validate_slice38_snapshot, value)


def _validate_capability_candidate(value: object) -> CandidateValidationReport:
    issues: list[CandidateValidationIssue] = []
    if type(value) is not CapabilityReferenceCandidate:
        _issue(issues, "$", C.TYPE_MISMATCH, "CapabilityReferenceCandidate required")
        return _report(issues)
    _identity(issues, "candidate_id", value, "candidate_id")
    _schema(issues, "schema_version", value)
    _exact_constant(issues, "candidate_schema_id", value.candidate_schema_id, CAPABILITY_REFERENCE_CANDIDATE_SCHEMA_ID)
    for name in (
        "frame_id", "frame_key", "frame_version",
        "frame_capability_reference_id", "frame_capability_reference_version",
        "capability_family_id", "capability_family_key", "capability_family_version",
        "effect_boundary_id", "effect_boundary_key", "effect_boundary_version",
        "availability_status", "relevance_mode",
    ):
        _text(issues, name, getattr(value, name))
    maps = _current_maps()
    frame = maps["frame"].get(value.frame_id) if type(value.frame_id) is str else None
    reference = maps["frame_cap"].get(value.frame_capability_reference_id) if type(value.frame_capability_reference_id) is str else None
    family = maps["capability"].get(value.capability_family_id) if type(value.capability_family_id) is str else None
    effect = maps["effect"].get(value.effect_boundary_id) if type(value.effect_boundary_id) is str else None
    if frame is None or reference is None or family is None or effect is None:
        _issue(issues, "references", C.REFERENCE_NOT_FOUND, "exact frame/capability/effect references required")
    else:
        if (
            frame.frame_key != value.frame_key
            or frame.version != value.frame_version
            or reference.frame_id != value.frame_id
            or reference.capability_family_id != value.capability_family_id
            or reference.effect_boundary_id != value.effect_boundary_id
            or family.capability_family_key != value.capability_family_key
            or family.version != value.capability_family_version
            or effect.effect_boundary_key != value.effect_boundary_key
            or effect.version != value.effect_boundary_version
            or reference.version != value.frame_capability_reference_version
            or reference.availability_status.value != value.availability_status
            or reference.relevance_mode.value != value.relevance_mode
        ):
            _issue(issues, "references", C.CROSS_REGISTRY_MISMATCH, "candidate references do not match accepted registries")
    _tuple(issues, "source_concept_candidate_proposal_ids", value.source_concept_candidate_proposal_ids)
    _tuple(issues, "source_sense_candidate_proposal_ids", value.source_sense_candidate_proposal_ids)
    _bool(issues, "candidate_only", value.candidate_only, True)
    for name in (
        "capability_available",
        "route_created",
        "invocation_proposed",
        "invocation_authorized",
        "arguments_constructed",
        "permission_granted",
        "execution_performed",
        "result_verified",
        "memory_operation_performed",
        "delivery_performed",
        "evidence_validated",
        "truth_determined",
    ):
        _bool(issues, name, getattr(value, name), False)
    return _report(issues)


def validate_capability_candidate(value: object) -> CandidateValidationReport:
    return _total(_validate_capability_candidate, value)


def _validate_role_layout_candidate(value: object) -> CandidateValidationReport:
    issues: list[CandidateValidationIssue] = []
    if type(value) is not RoleLayoutCandidate:
        _issue(issues, "$", C.TYPE_MISMATCH, "RoleLayoutCandidate required")
        return _report(issues)
    _identity(issues, "candidate_id", value, "candidate_id")
    _schema(issues, "schema_version", value)
    _exact_constant(issues, "candidate_schema_id", value.candidate_schema_id, ROLE_LAYOUT_CANDIDATE_SCHEMA_ID)
    for name in (
        "frame_id", "frame_key", "frame_version",
        "action_root_id", "action_root_key", "action_root_version",
        "predicate_id", "predicate_key", "predicate_version",
        "effect_boundary_id", "effect_boundary_key", "effect_boundary_version",
        "frame_effect_reference_id", "frame_effect_reference_version",
    ):
        _text(issues, name, getattr(value, name))
    _enum(issues, "structural_state", value.structural_state, CandidateStructuralState)
    required = _role_triples(issues, "required_roles", value.required_roles)
    optional = _role_triples(issues, "optional_roles", value.optional_roles)
    prohibited = _role_triples(issues, "prohibited_roles", value.prohibited_roles)
    conditional = _role_triples(issues, "conditional_roles", value.conditional_roles)
    missing = _tuple(issues, "missing_required_role_ids", value.missing_required_role_ids)
    _tuple(issues, "conflicting_role_ids", value.conflicting_role_ids)
    _tuple(issues, "unresolved_alternative_role_ids", value.unresolved_alternative_role_ids)
    _tuple(issues, "capability_reference_candidate_ids", value.capability_reference_candidate_ids)
    _tuple(issues, "source_structural_ancestry_ids", value.source_structural_ancestry_ids)
    _tuple(issues, "source_concept_candidate_proposal_ids", value.source_concept_candidate_proposal_ids)
    _tuple(issues, "source_sense_candidate_proposal_ids", value.source_sense_candidate_proposal_ids)
    maps = _current_maps()
    frame = maps["frame"].get(value.frame_id) if type(value.frame_id) is str else None
    root = maps["root"].get(value.action_root_id) if type(value.action_root_id) is str else None
    predicate = maps["predicate"].get(value.predicate_id) if type(value.predicate_id) is str else None
    effect = maps["effect"].get(value.effect_boundary_id) if type(value.effect_boundary_id) is str else None
    effect_ref = maps["frame_effect"].get(value.frame_effect_reference_id) if type(value.frame_effect_reference_id) is str else None
    if None in (frame, root, predicate, effect, effect_ref):
        _issue(issues, "references", C.REFERENCE_NOT_FOUND, "exact root/predicate/frame/effect references required")
    else:
        if (
            frame.frame_key != value.frame_key
            or frame.version != value.frame_version
            or frame.linked_action_root_id != value.action_root_id
            or frame.linked_predicate_id != value.predicate_id
            or root.action_root_key != value.action_root_key
            or root.version != value.action_root_version
            or predicate.predicate_key != value.predicate_key
            or predicate.version != value.predicate_version
            or effect.effect_boundary_key != value.effect_boundary_key
            or effect.version != value.effect_boundary_version
            or effect_ref.frame_id != value.frame_id
            or effect_ref.effect_boundary_id != value.effect_boundary_id
            or effect_ref.version != value.frame_effect_reference_version
        ):
            _issue(issues, "references", C.CROSS_REGISTRY_MISMATCH, "layout references mismatch accepted registries")
    role_map = maps["role"]
    for category, triples in (
        ("required_roles", required),
        ("optional_roles", optional),
        ("prohibited_roles", prohibited),
        ("conditional_roles", conditional),
    ):
        for index, (role_id, role_key, version) in enumerate(triples):
            role = role_map.get(role_id)
            if role is None or role.role_key != role_key or role.version != version:
                _issue(issues, f"{category}[{index}]", C.CROSS_REGISTRY_MISMATCH, "role identity/key/version mismatch")
    if tuple(item[0] for item in required) != missing:
        _issue(issues, "missing_required_role_ids", C.ANCESTRY_MISMATCH, "Slice 38G creates no assignments; every required role must remain missing")
    if value.structural_state is CandidateStructuralState.STRUCTURALLY_COMPLETE:
        _issue(issues, "structural_state", C.STATUS_MISMATCH, "no role assignments exist, so complete state is unsupported")
    _bool(issues, "candidate_only", value.candidate_only, True)
    for name in (
        "frame_selected",
        "participant_assignments_created",
        "frame_completed",
        "permission_inferred",
        "gate_outcome_created",
        "route_created",
        "execution_performed",
    ):
        _bool(issues, name, getattr(value, name), False)
    return _report(issues)


def validate_role_layout_candidate(value: object) -> CandidateValidationReport:
    return _total(_validate_role_layout_candidate, value)


def _validate_action_candidate(value: object) -> CandidateValidationReport:
    issues: list[CandidateValidationIssue] = []
    if type(value) is not ActionRootPredicateCandidate:
        _issue(issues, "$", C.TYPE_MISMATCH, "ActionRootPredicateCandidate required")
        return _report(issues)
    _identity(issues, "candidate_id", value, "candidate_id")
    _schema(issues, "schema_version", value)
    _exact_constant(issues, "candidate_schema_id", value.candidate_schema_id, ACTION_PREDICATE_CANDIDATE_SCHEMA_ID)
    for name in (
        "compatibility_rule_id", "compatibility_rule_version",
        "action_root_id", "action_root_key", "action_root_version",
        "predicate_id", "predicate_key", "predicate_version",
    ):
        _text(issues, name, getattr(value, name))
    _enum(issues, "structural_state", value.structural_state, CandidateStructuralState)
    _tuple(issues, "source_concept_candidate_proposal_ids", value.source_concept_candidate_proposal_ids)
    _tuple(issues, "source_sense_candidate_proposal_ids", value.source_sense_candidate_proposal_ids)
    _pairs(issues, "source_concept_ids_and_versions", value.source_concept_ids_and_versions)
    _pairs(issues, "source_sense_ids_and_versions", value.source_sense_ids_and_versions)
    _pairs(issues, "frame_ids_and_versions", value.frame_ids_and_versions)
    _tuple(issues, "role_layout_candidate_ids", value.role_layout_candidate_ids, allow_empty=False)
    _tuple(issues, "capability_reference_candidate_ids", value.capability_reference_candidate_ids)
    _tuple(issues, "unresolved_alternative_candidate_ids", value.unresolved_alternative_candidate_ids)
    maps = _current_maps()
    root = maps["root"].get(value.action_root_id) if type(value.action_root_id) is str else None
    predicate = maps["predicate"].get(value.predicate_id) if type(value.predicate_id) is str else None
    if root is None or predicate is None:
        _issue(issues, "references", C.REFERENCE_NOT_FOUND, "exact root and predicate required")
    elif (
        root.action_root_key != value.action_root_key
        or root.version != value.action_root_version
        or predicate.predicate_key != value.predicate_key
        or predicate.version != value.predicate_version
        or predicate.action_root_id != root.action_root_id
    ):
        _issue(issues, "references", C.CROSS_REGISTRY_MISMATCH, "root/predicate mismatch")
    for index, (frame_id, version) in enumerate(value.frame_ids_and_versions if type(value.frame_ids_and_versions) is tuple else ()):
        frame = maps["frame"].get(frame_id)
        if frame is None or frame.version != version or frame.linked_action_root_id != value.action_root_id:
            _issue(issues, f"frame_ids_and_versions[{index}]", C.CROSS_REGISTRY_MISMATCH, "frame mismatch")
    _bool(issues, "candidate_only", value.candidate_only, True)
    for name in (
        "predicate_selected",
        "frame_selected",
        "participant_assignment_selected",
        "candidate_meaning_created",
        "selected_meaning_created",
        "permission_inferred",
        "route_created",
        "action_performed",
        "memory_accessed",
        "delivered",
        "evidence_validity_determined",
        "truth_determined",
    ):
        _bool(issues, name, getattr(value, name), False)
    return _report(issues)


def validate_action_candidate(value: object) -> CandidateValidationReport:
    return _total(_validate_action_candidate, value)


def _validate_result(value: object) -> CandidateValidationReport:
    issues: list[CandidateValidationIssue] = []
    if type(value) is not PredicateRoleFrameCandidateProposalResult:
        _issue(issues, "$", C.TYPE_MISMATCH, "PredicateRoleFrameCandidateProposalResult required")
        return _report(issues)
    _identity(issues, "result_id", value, "result_id")
    _schema(issues, "schema_version", value)
    _exact_constant(issues, "spec_id", value.spec_id, SLICE38G_SPEC_ID)
    _exact_constant(issues, "spec_version", value.spec_version, SLICE38G_SPEC_VERSION)
    _exact_constant(issues, "result_schema_id", value.result_schema_id, RESULT_SCHEMA_ID)
    _enum(issues, "status", value.status, CandidateProposalStatus)
    _text(issues, "reason_code", value.reason_code)
    predecessor_rejected = value.status is CandidateProposalStatus.PREDECESSOR_REJECTED
    for name in (
        "source_slice37_result_id",
        "source_slice37_status",
        "source_event_id",
        "source_sha256",
        "input_event_id",
        "root_source_span_id",
        "projection_id",
        "structural_result_id",
        "structural_set_id",
        "slice37_registry_snapshot_id",
    ):
        _text(issues, name, getattr(value, name), allow_empty=predecessor_rejected)
    for report, prefix in (
        (validate_profile(value.profile), "profile"),
        (validate_slice38_snapshot(value.slice38_registry_snapshot), "slice38_registry_snapshot"),
        (validate_compatibility_snapshot(value.compatibility_registry_snapshot), "compatibility_registry_snapshot"),
    ):
        for item in report.issues:
            _issue(issues, f"{prefix}.{item.path}", item.code, item.detail)
    tuple_fields = (
        "source_span_ids",
        "structural_ancestry_ids",
        "phase_trail_ids",
        "constrained_trail_ids",
        "operator_graph_ids",
        "operator_node_ids",
        "operator_definition_ids",
        "scope_occurrence_ids",
        "attachment_candidate_ids",
        "reference_analysis_ids",
        "reference_candidate_ids",
        "concept_candidate_proposal_ids",
        "sense_candidate_proposal_ids",
        "unresolved_alternative_candidate_ids",
        "missing_role_ids",
        "conflicting_role_ids",
        "unsupported_reasons",
        "unknown_reasons",
    )
    for name in tuple_fields:
        _tuple(issues, name, getattr(value, name))
    _pairs(issues, "operator_keys_and_versions", value.operator_keys_and_versions)
    _pairs(issues, "concept_ids_and_versions", value.concept_ids_and_versions)
    _pairs(issues, "sense_ids_and_versions", value.sense_ids_and_versions)

    actions = _tuple(issues, "action_predicate_candidates", value.action_predicate_candidates, item_type=ActionRootPredicateCandidate)
    layouts = _tuple(issues, "role_layout_candidates", value.role_layout_candidates, item_type=RoleLayoutCandidate)
    caps = _tuple(issues, "capability_reference_candidates", value.capability_reference_candidates, item_type=CapabilityReferenceCandidate)
    _count(issues, "action_predicate_candidate_count", value.action_predicate_candidate_count, expected=len(actions))
    _count(issues, "role_layout_candidate_count", value.role_layout_candidate_count, expected=len(layouts))
    _count(issues, "capability_reference_candidate_count", value.capability_reference_candidate_count, expected=len(caps))
    _count(
        issues,
        "unresolved_alternative_count",
        value.unresolved_alternative_count,
        expected=len(value.unresolved_alternative_candidate_ids if type(value.unresolved_alternative_candidate_ids) is tuple else ()),
    )
    _count(
        issues,
        "missing_role_count",
        value.missing_role_count,
        expected=len(value.missing_role_ids if type(value.missing_role_ids) is tuple else ()),
    )
    _count(
        issues,
        "conflicting_role_count",
        value.conflicting_role_count,
        expected=len(value.conflicting_role_ids if type(value.conflicting_role_ids) is tuple else ()),
    )

    action_ids = {item.candidate_id for item in actions}
    layout_ids = {item.candidate_id for item in layouts}
    cap_ids = {item.candidate_id for item in caps}
    for index, item in enumerate(actions):
        report = validate_action_candidate(item)
        for issue in report.issues:
            _issue(issues, f"action_predicate_candidates[{index}].{issue.path}", issue.code, issue.detail)
        if not set(item.role_layout_candidate_ids).issubset(layout_ids):
            _issue(issues, f"action_predicate_candidates[{index}].role_layout_candidate_ids", C.REFERENCE_NOT_FOUND, "unknown layout candidate")
        if not set(item.capability_reference_candidate_ids).issubset(cap_ids):
            _issue(issues, f"action_predicate_candidates[{index}].capability_reference_candidate_ids", C.REFERENCE_NOT_FOUND, "unknown capability candidate")
    for index, item in enumerate(layouts):
        report = validate_role_layout_candidate(item)
        for issue in report.issues:
            _issue(issues, f"role_layout_candidates[{index}].{issue.path}", issue.code, issue.detail)
        if not set(item.capability_reference_candidate_ids).issubset(cap_ids):
            _issue(issues, f"role_layout_candidates[{index}].capability_reference_candidate_ids", C.REFERENCE_NOT_FOUND, "unknown capability candidate")
    for index, item in enumerate(caps):
        report = validate_capability_candidate(item)
        for issue in report.issues:
            _issue(issues, f"capability_reference_candidates[{index}].{issue.path}", issue.code, issue.detail)

    if value.status in (
        CandidateProposalStatus.CANDIDATES_PROPOSED,
        CandidateProposalStatus.STRUCTURALLY_INCOMPLETE,
        CandidateProposalStatus.AMBIGUOUS,
        CandidateProposalStatus.CONFLICTED,
    ) and not actions:
        _issue(issues, "status", C.STATUS_MISMATCH, "candidate-bearing status requires candidates")
    if value.status is CandidateProposalStatus.STRUCTURALLY_INCOMPLETE and not value.missing_role_ids:
        _issue(issues, "status", C.STATUS_MISMATCH, "incomplete status requires missing roles")
    if value.status is CandidateProposalStatus.AMBIGUOUS and len(actions) < 2 and len(layouts) < 2:
        _issue(issues, "status", C.STATUS_MISMATCH, "ambiguous status requires alternatives")
    if value.status is CandidateProposalStatus.CONFLICTED and not value.unresolved_alternative_candidate_ids:
        _issue(issues, "status", C.STATUS_MISMATCH, "conflicted status requires unresolved alternatives")
    if value.status is CandidateProposalStatus.EXPLICIT_UNSUPPORTED and not value.unsupported_reasons:
        _issue(issues, "unsupported_reasons", C.STATUS_MISMATCH, "unsupported reason required")
    if value.status is CandidateProposalStatus.EXPLICIT_UNKNOWN and not value.unknown_reasons:
        _issue(issues, "unknown_reasons", C.STATUS_MISMATCH, "unknown reason required")

    for name in (
        "source_ancestry_preserved",
        "operator_ancestry_preserved",
        "phase_trail_ancestry_preserved",
        "scope_attachment_ancestry_preserved",
        "registry_snapshots_preserved",
        "zero_one_many_preserved",
        "capability_non_invocation_boundary_preserved",
    ):
        _bool(issues, name, getattr(value, name), True)
    for name in (
        "candidate_order_is_ranked",
        "selected_predicate_created",
        "selected_frame_created",
        "selected_participant_assignment_created",
        "candidate_meaning_created",
        "selected_meaning_created",
        "permission_inferred",
        "tool_route_created",
        "tool_invoked",
        "action_performed",
        "memory_read_performed",
        "memory_write_performed",
        "delivered",
        "evidence_validity_determined",
        "truth_determined",
        "clarification_outcome_created",
        "refusal_outcome_created",
        "blocked_progression_outcome_created",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "external_resource_loaded",
        "language_model_used",
        "embedding_used",
        "semantic_similarity_used",
    ):
        _bool(issues, name, getattr(value, name), False)
    if value.non_authority_boundaries != SLICE38G_NON_AUTHORITY_BOUNDARIES:
        _issue(issues, "non_authority_boundaries", C.AUTHORITY_BOUNDARY_VIOLATION, "exact boundary set required")
    return _report(issues)


def validate_result(value: object) -> CandidateValidationReport:
    return _total(_validate_result, value)


def assert_valid_result(value: object) -> PredicateRoleFrameCandidateProposalResult:
    report = validate_result(value)
    if not report.ok:
        detail = "; ".join(f"{item.path}:{item.code.value}" for item in report.issues)
        raise CandidateValidationError(detail)
    return value  # type: ignore[return-value]


PUBLIC_VALIDATORS = (
    validate_profile,
    validate_rule,
    validate_conflict,
    validate_compatibility_snapshot,
    validate_slice38_snapshot,
    validate_action_candidate,
    validate_role_layout_candidate,
    validate_capability_candidate,
    validate_result,
)
