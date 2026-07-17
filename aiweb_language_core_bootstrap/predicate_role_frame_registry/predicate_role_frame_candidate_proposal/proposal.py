"""Deterministic Slice 37F-to-Slice 38G candidate proposal operation."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from ...structural_concept_candidate_proposal import (
    ProposalResultStatus as Slice37ProposalStatus,
    StructuralConceptCandidateProposalResult,
    validate_proposal_result as validate_slice37_result,
)
from ..built_in_action_root_registry import built_in_action_root_registry
from ..capability_family_reference_registry import (
    capability_family_reference_registry,
)
from ..participant_role_registry import participant_role_registry
from ..predicate_frame_registry import predicate_frame_registry
from .authority import SLICE38G_NON_AUTHORITY_BOUNDARIES
from .compatibility import CANONICAL_COMPATIBILITY_SNAPSHOT
from .identity import with_expected_id
from .records import DEFAULT_PROPOSAL_PROFILE, SLICE38_REGISTRY_SNAPSHOT
from .schema import (
    ActionRootCompatibilityConflict,
    ActionRootCompatibilityRule,
    ActionRootPredicateCandidate,
    CandidateProposalStatus,
    CandidateStructuralState,
    CapabilityReferenceCandidate,
    CompatibilityMatchMode,
    CompatibilityRegistrySnapshot,
    PredicateRoleFrameCandidateProposalResult,
    PredicateRoleFrameProposalProfile,
    RoleLayoutCandidate,
    Slice38RegistrySnapshotIdentity,
)


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _unique_pairs(values: Iterable[tuple[str, str]]) -> tuple[tuple[str, str], ...]:
    return tuple(dict.fromkeys(values))


def _source_ancestry(
    source: StructuralConceptCandidateProposalResult,
) -> dict[str, tuple]:
    ancestries = source.structural_ancestries
    return {
        "source_span_ids": _unique(
            span_id
            for occurrence in source.lexical_occurrences
            for span_id in occurrence.source_span_ids
        ),
        "structural_ancestry_ids": tuple(item.ancestry_id for item in ancestries),
        "phase_trail_ids": _unique(item.phase_trail_id for item in ancestries),
        "constrained_trail_ids": _unique(
            item.constrained_trail_id for item in ancestries
        ),
        "operator_graph_ids": _unique(item.operator_graph_id for item in ancestries),
        "operator_node_ids": _unique(
            value for item in ancestries for value in item.operator_node_ids
        ),
        "operator_definition_ids": _unique(
            value
            for item in ancestries
            for value in item.operator_definition_ids
        ),
        "operator_keys_and_versions": _unique_pairs(
            value
            for item in ancestries
            for value in item.operator_keys_and_versions
        ),
        "scope_occurrence_ids": _unique(
            value
            for item in ancestries
            for value in item.scope_occurrence_ids
        ),
        "attachment_candidate_ids": _unique(
            value
            for item in ancestries
            for value in item.attachment_candidate_ids
        ),
        "reference_analysis_ids": _unique(
            value
            for item in ancestries
            for value in item.reference_analysis_ids
        ),
        "reference_candidate_ids": _unique(
            value
            for item in ancestries
            for value in item.reference_candidate_ids
        ),
    }


def _rule_matches(
    rule: ActionRootCompatibilityRule,
    source: StructuralConceptCandidateProposalResult,
) -> tuple[tuple[object, ...], tuple[object, ...]]:
    concepts = tuple(
        item
        for item in source.concept_candidates
        if (
            rule.concept_id is not None
            and item.concept_id == rule.concept_id
            and item.concept_version == rule.concept_version
        )
    )
    senses = tuple(
        item
        for item in source.sense_candidates
        if (
            rule.sense_id is not None
            and item.sense_id == rule.sense_id
            and item.sense_version == rule.sense_version
        )
    )

    if rule.match_mode is CompatibilityMatchMode.EXACT_CONCEPT:
        return concepts, ()
    if rule.match_mode is CompatibilityMatchMode.EXACT_SENSE:
        return (), senses
    if rule.match_mode is CompatibilityMatchMode.EXACT_CONCEPT_AND_SENSE:
        if not concepts or not senses:
            return (), ()
        concept_ids = {item.concept_id for item in concepts}
        matching_senses = tuple(
            item for item in senses if item.concept_id in concept_ids
        )
        return (concepts, matching_senses) if matching_senses else ((), ())
    return (), ()


def _conflicts_for_rule(
    rule: ActionRootCompatibilityRule,
    snapshot: CompatibilityRegistrySnapshot,
) -> tuple[ActionRootCompatibilityConflict, ...]:
    refs = set(rule.conflict_refs)
    return tuple(
        item
        for item in snapshot.conflicts
        if item.conflict_id in refs or rule.rule_id in item.rule_refs
    )


def _role_tuple(role_id: str) -> tuple[str, str, str]:
    role_registry = participant_role_registry()
    for role in role_registry.admitted_roles:
        if role.role_id == role_id:
            return (role.role_id, role.role_key, role.version)
    raise ValueError(f"unknown exact participant role id: {role_id}")


def _build_capability_candidates(
    *,
    frame: object,
    concept_proposal_ids: tuple[str, ...],
    sense_proposal_ids: tuple[str, ...],
) -> tuple[CapabilityReferenceCandidate, ...]:
    registry = capability_family_reference_registry()
    family_by_id = {
        item.capability_family_id: item for item in registry.capability_families
    }
    effect_by_id = {
        item.effect_boundary_id: item for item in registry.effect_boundaries
    }
    records = tuple(
        item
        for item in registry.frame_capability_references
        if item.frame_id == frame.frame_id
    )
    candidates: list[CapabilityReferenceCandidate] = []
    for reference in records:
        family = family_by_id[reference.capability_family_id]
        effect = effect_by_id[reference.effect_boundary_id]
        raw = CapabilityReferenceCandidate(
            candidate_id="",
            frame_id=frame.frame_id,
            frame_key=frame.frame_key,
            frame_version=frame.version,
            frame_capability_reference_id=reference.frame_capability_reference_id,
            frame_capability_reference_version=reference.version,
            capability_family_id=family.capability_family_id,
            capability_family_key=family.capability_family_key,
            capability_family_version=family.version,
            effect_boundary_id=effect.effect_boundary_id,
            effect_boundary_key=effect.effect_boundary_key,
            effect_boundary_version=effect.version,
            availability_status=reference.availability_status.value,
            relevance_mode=reference.relevance_mode.value,
            source_concept_candidate_proposal_ids=concept_proposal_ids,
            source_sense_candidate_proposal_ids=sense_proposal_ids,
            candidate_only=True,
            capability_available=False,
            route_created=False,
            invocation_proposed=False,
            invocation_authorized=False,
            arguments_constructed=False,
            permission_granted=False,
            execution_performed=False,
            result_verified=False,
            memory_operation_performed=False,
            delivery_performed=False,
            evidence_validated=False,
            truth_determined=False,
        )
        candidates.append(with_expected_id(raw, "candidate_id"))
    return tuple(candidates)


def _build_role_layout_candidate(
    *,
    frame: object,
    root: object,
    predicate: object,
    capability_candidates: tuple[CapabilityReferenceCandidate, ...],
    source_ancestry_ids: tuple[str, ...],
    concept_proposal_ids: tuple[str, ...],
    sense_proposal_ids: tuple[str, ...],
    conflicted: bool,
) -> RoleLayoutCandidate:
    frame_registry = predicate_frame_registry()
    capability_registry = capability_family_reference_registry()
    constraints = tuple(
        item for item in frame_registry.role_constraints if item.frame_key == frame.frame_key
    )

    required = tuple(
        _role_tuple(item.role_id)
        for item in constraints
        if item.requirement.value == "required"
    )
    optional = tuple(
        _role_tuple(item.role_id)
        for item in constraints
        if item.requirement.value == "optional"
    )
    prohibited = tuple(
        _role_tuple(item.role_id)
        for item in constraints
        if item.requirement.value == "prohibited"
    )
    conditional = tuple(
        _role_tuple(item.role_id)
        for item in constraints
        if item.requirement.value == "conditional"
    )

    effect_ref = next(
        item
        for item in capability_registry.frame_effect_references
        if item.frame_id == frame.frame_id
    )
    effect = next(
        item
        for item in capability_registry.effect_boundaries
        if item.effect_boundary_id == effect_ref.effect_boundary_id
    )

    missing = tuple(item[0] for item in required)
    state = (
        CandidateStructuralState.CONFLICTED
        if conflicted
        else (
            CandidateStructuralState.STRUCTURALLY_INCOMPLETE
            if missing
            else CandidateStructuralState.STRUCTURALLY_COMPLETE
        )
    )

    raw = RoleLayoutCandidate(
        candidate_id="",
        frame_id=frame.frame_id,
        frame_key=frame.frame_key,
        frame_version=frame.version,
        action_root_id=root.action_root_id,
        action_root_key=root.action_root_key,
        action_root_version=root.version,
        predicate_id=predicate.predicate_id,
        predicate_key=predicate.predicate_key,
        predicate_version=predicate.version,
        required_roles=required,
        optional_roles=optional,
        prohibited_roles=prohibited,
        conditional_roles=conditional,
        missing_required_role_ids=missing,
        conflicting_role_ids=(),
        unresolved_alternative_role_ids=(),
        effect_boundary_id=effect.effect_boundary_id,
        effect_boundary_key=effect.effect_boundary_key,
        effect_boundary_version=effect.version,
        frame_effect_reference_id=effect_ref.frame_effect_reference_id,
        frame_effect_reference_version=effect_ref.version,
        capability_reference_candidate_ids=tuple(
            item.candidate_id for item in capability_candidates
        ),
        structural_state=state,
        source_structural_ancestry_ids=source_ancestry_ids,
        source_concept_candidate_proposal_ids=concept_proposal_ids,
        source_sense_candidate_proposal_ids=sense_proposal_ids,
        candidate_only=True,
        frame_selected=False,
        participant_assignments_created=False,
        frame_completed=False,
        permission_inferred=False,
        gate_outcome_created=False,
        route_created=False,
        execution_performed=False,
    )
    return with_expected_id(raw, "candidate_id")


def _base_result(
    *,
    source: object,
    status: CandidateProposalStatus,
    reason_code: str,
    profile: PredicateRoleFrameProposalProfile,
    slice38_snapshot: Slice38RegistrySnapshotIdentity,
    compatibility_snapshot: CompatibilityRegistrySnapshot,
    unsupported_reasons: tuple[str, ...] = (),
    unknown_reasons: tuple[str, ...] = (),
) -> PredicateRoleFrameCandidateProposalResult:
    valid_source = type(source) is StructuralConceptCandidateProposalResult
    ancestry = _source_ancestry(source) if valid_source else {
        "source_span_ids": (),
        "structural_ancestry_ids": (),
        "phase_trail_ids": (),
        "constrained_trail_ids": (),
        "operator_graph_ids": (),
        "operator_node_ids": (),
        "operator_definition_ids": (),
        "operator_keys_and_versions": (),
        "scope_occurrence_ids": (),
        "attachment_candidate_ids": (),
        "reference_analysis_ids": (),
        "reference_candidate_ids": (),
    }
    concept_candidates = getattr(source, "concept_candidates", ()) if valid_source else ()
    sense_candidates = getattr(source, "sense_candidates", ()) if valid_source else ()
    registry_snapshot = getattr(source, "registry_snapshot", None)

    raw = PredicateRoleFrameCandidateProposalResult(
        result_id="",
        status=status,
        reason_code=reason_code,
        source_slice37_result_id=getattr(source, "result_id", ""),
        source_slice37_status=(
            getattr(getattr(source, "status", None), "value", "")
        ),
        source_event_id=getattr(source, "source_event_id", ""),
        source_sha256=getattr(source, "source_sha256", ""),
        input_event_id=getattr(source, "input_event_id", ""),
        root_source_span_id=getattr(source, "root_source_span_id", ""),
        projection_id=getattr(source, "projection_id", ""),
        structural_result_id=getattr(source, "structural_result_id", ""),
        structural_set_id=getattr(source, "structural_set_id", ""),
        source_span_ids=ancestry["source_span_ids"],
        structural_ancestry_ids=ancestry["structural_ancestry_ids"],
        phase_trail_ids=ancestry["phase_trail_ids"],
        constrained_trail_ids=ancestry["constrained_trail_ids"],
        operator_graph_ids=ancestry["operator_graph_ids"],
        operator_node_ids=ancestry["operator_node_ids"],
        operator_definition_ids=ancestry["operator_definition_ids"],
        operator_keys_and_versions=ancestry["operator_keys_and_versions"],
        scope_occurrence_ids=ancestry["scope_occurrence_ids"],
        attachment_candidate_ids=ancestry["attachment_candidate_ids"],
        reference_analysis_ids=ancestry["reference_analysis_ids"],
        reference_candidate_ids=ancestry["reference_candidate_ids"],
        concept_candidate_proposal_ids=tuple(
            item.proposal_id for item in concept_candidates
        ),
        sense_candidate_proposal_ids=tuple(
            item.proposal_id for item in sense_candidates
        ),
        concept_ids_and_versions=tuple(
            (item.concept_id, item.concept_version) for item in concept_candidates
        ),
        sense_ids_and_versions=tuple(
            (item.sense_id, item.sense_version) for item in sense_candidates
        ),
        slice37_registry_snapshot_id=getattr(registry_snapshot, "snapshot_id", ""),
        slice38_registry_snapshot=slice38_snapshot,
        compatibility_registry_snapshot=compatibility_snapshot,
        action_predicate_candidates=(),
        role_layout_candidates=(),
        capability_reference_candidates=(),
        unresolved_alternative_candidate_ids=(),
        missing_role_ids=(),
        conflicting_role_ids=(),
        unsupported_reasons=unsupported_reasons,
        unknown_reasons=unknown_reasons,
        action_predicate_candidate_count=0,
        role_layout_candidate_count=0,
        capability_reference_candidate_count=0,
        unresolved_alternative_count=0,
        missing_role_count=0,
        conflicting_role_count=0,
        source_ancestry_preserved=True,
        operator_ancestry_preserved=True,
        phase_trail_ancestry_preserved=True,
        scope_attachment_ancestry_preserved=True,
        registry_snapshots_preserved=True,
        zero_one_many_preserved=True,
        capability_non_invocation_boundary_preserved=True,
        candidate_order_is_ranked=False,
        selected_predicate_created=False,
        selected_frame_created=False,
        selected_participant_assignment_created=False,
        candidate_meaning_created=False,
        selected_meaning_created=False,
        permission_inferred=False,
        tool_route_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        delivered=False,
        evidence_validity_determined=False,
        truth_determined=False,
        clarification_outcome_created=False,
        refusal_outcome_created=False,
        blocked_progression_outcome_created=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        external_resource_loaded=False,
        language_model_used=False,
        embedding_used=False,
        semantic_similarity_used=False,
        profile=profile,
        non_authority_boundaries=SLICE38G_NON_AUTHORITY_BOUNDARIES,
    )
    return with_expected_id(raw, "result_id")


def propose_predicate_role_frame_candidates(
    source: object,
    *,
    compatibility_snapshot: CompatibilityRegistrySnapshot = (
        CANONICAL_COMPATIBILITY_SNAPSHOT
    ),
    profile: PredicateRoleFrameProposalProfile = DEFAULT_PROPOSAL_PROFILE,
    slice38_snapshot: Slice38RegistrySnapshotIdentity = SLICE38_REGISTRY_SNAPSHOT,
) -> PredicateRoleFrameCandidateProposalResult:
    """Propose exact predicate/frame/role-layout candidates without selection."""

    from .validation import (
        validate_compatibility_snapshot,
        validate_profile,
        validate_result,
        validate_slice38_snapshot,
    )

    if not validate_profile(profile).ok:
        return _base_result(
            source=source,
            status=CandidateProposalStatus.PREDECESSOR_REJECTED,
            reason_code="invalid_slice38g_profile",
            profile=DEFAULT_PROPOSAL_PROFILE,
            slice38_snapshot=SLICE38_REGISTRY_SNAPSHOT,
            compatibility_snapshot=CANONICAL_COMPATIBILITY_SNAPSHOT,
            unsupported_reasons=("invalid_slice38g_profile",),
        )
    if not validate_slice38_snapshot(slice38_snapshot).ok:
        return _base_result(
            source=source,
            status=CandidateProposalStatus.PREDECESSOR_REJECTED,
            reason_code="invalid_slice38_registry_snapshot",
            profile=profile,
            slice38_snapshot=SLICE38_REGISTRY_SNAPSHOT,
            compatibility_snapshot=compatibility_snapshot,
            unsupported_reasons=("invalid_slice38_registry_snapshot",),
        )
    if not validate_compatibility_snapshot(compatibility_snapshot).ok:
        return _base_result(
            source=source,
            status=CandidateProposalStatus.PREDECESSOR_REJECTED,
            reason_code="invalid_compatibility_registry_snapshot",
            profile=profile,
            slice38_snapshot=slice38_snapshot,
            compatibility_snapshot=CANONICAL_COMPATIBILITY_SNAPSHOT,
            unsupported_reasons=("invalid_compatibility_registry_snapshot",),
        )
    if type(source) is not StructuralConceptCandidateProposalResult:
        return _base_result(
            source=source,
            status=CandidateProposalStatus.PREDECESSOR_REJECTED,
            reason_code="invalid_slice37_result_type",
            profile=profile,
            slice38_snapshot=slice38_snapshot,
            compatibility_snapshot=compatibility_snapshot,
            unsupported_reasons=("invalid_slice37_result_type",),
        )
    if not validate_slice37_result(source).ok:
        return _base_result(
            source=source,
            status=CandidateProposalStatus.PREDECESSOR_REJECTED,
            reason_code="invalid_slice37_result",
            profile=profile,
            slice38_snapshot=slice38_snapshot,
            compatibility_snapshot=compatibility_snapshot,
            unsupported_reasons=("invalid_slice37_result",),
        )

    if not source.concept_candidates and not source.sense_candidates:
        if source.explicit_unsupported_count:
            status = CandidateProposalStatus.EXPLICIT_UNSUPPORTED
            reason = "slice37_explicit_unsupported_preserved"
            unsupported = (reason,)
            unknown = ()
        else:
            status = CandidateProposalStatus.EXPLICIT_UNKNOWN
            reason = "slice37_explicit_unknown_preserved"
            unsupported = ()
            unknown = (reason,)
        result = _base_result(
            source=source,
            status=status,
            reason_code=reason,
            profile=profile,
            slice38_snapshot=slice38_snapshot,
            compatibility_snapshot=compatibility_snapshot,
            unsupported_reasons=unsupported,
            unknown_reasons=unknown,
        )
        return result

    matches: list[tuple[ActionRootCompatibilityRule, tuple, tuple]] = []
    for rule in compatibility_snapshot.rules:
        concepts, senses = _rule_matches(rule, source)
        if concepts or senses:
            matches.append((rule, concepts, senses))

    if not matches:
        result = _base_result(
            source=source,
            status=CandidateProposalStatus.EXPLICIT_UNSUPPORTED,
            reason_code="no_exact_action_root_compatibility_rule",
            profile=profile,
            slice38_snapshot=slice38_snapshot,
            compatibility_snapshot=compatibility_snapshot,
            unsupported_reasons=(
                "no exact governed Slice 37 concept/sense to Slice 38 action-root compatibility rule",
            ),
        )
        return result

    action_registry = built_in_action_root_registry()
    frame_registry = predicate_frame_registry()
    roots_by_id = {
        item.action_root_id: item for item in action_registry.admitted_action_roots
    }
    predicates_by_id = {
        item.predicate_id: item for item in action_registry.admitted_predicates
    }
    frames_by_id = {item.frame_id: item for item in frame_registry.admitted_frames}

    all_caps: list[CapabilityReferenceCandidate] = []
    all_layouts: list[RoleLayoutCandidate] = []
    action_candidates: list[ActionRootPredicateCandidate] = []

    for rule, concepts, senses in matches:
        root = roots_by_id[rule.action_root_id]
        predicate = predicates_by_id[rule.predicate_id]
        frames = tuple(frames_by_id[item] for item in rule.allowed_frame_ids)
        concept_proposal_ids = tuple(item.proposal_id for item in concepts)
        sense_proposal_ids = tuple(item.proposal_id for item in senses)
        conflicts = _conflicts_for_rule(rule, compatibility_snapshot)
        conflicted = bool(conflicts)

        local_caps: list[CapabilityReferenceCandidate] = []
        local_layouts: list[RoleLayoutCandidate] = []
        for frame in frames:
            cap_candidates = _build_capability_candidates(
                frame=frame,
                concept_proposal_ids=concept_proposal_ids,
                sense_proposal_ids=sense_proposal_ids,
            )
            local_caps.extend(cap_candidates)
            layout = _build_role_layout_candidate(
                frame=frame,
                root=root,
                predicate=predicate,
                capability_candidates=cap_candidates,
                source_ancestry_ids=tuple(
                    item.ancestry_id for item in source.structural_ancestries
                ),
                concept_proposal_ids=concept_proposal_ids,
                sense_proposal_ids=sense_proposal_ids,
                conflicted=conflicted,
            )
            local_layouts.append(layout)

        if conflicted:
            state = CandidateStructuralState.CONFLICTED
        elif len(matches) > 1 or len(frames) > 1:
            state = CandidateStructuralState.AMBIGUOUS
        elif any(
            item.structural_state is CandidateStructuralState.STRUCTURALLY_INCOMPLETE
            for item in local_layouts
        ):
            state = CandidateStructuralState.STRUCTURALLY_INCOMPLETE
        else:
            state = CandidateStructuralState.STRUCTURALLY_COMPLETE

        raw_candidate = ActionRootPredicateCandidate(
            candidate_id="",
            compatibility_rule_id=rule.rule_id,
            compatibility_rule_version=rule.version,
            source_concept_candidate_proposal_ids=concept_proposal_ids,
            source_sense_candidate_proposal_ids=sense_proposal_ids,
            source_concept_ids_and_versions=tuple(
                (item.concept_id, item.concept_version) for item in concepts
            ),
            source_sense_ids_and_versions=tuple(
                (item.sense_id, item.sense_version) for item in senses
            ),
            action_root_id=root.action_root_id,
            action_root_key=root.action_root_key,
            action_root_version=root.version,
            predicate_id=predicate.predicate_id,
            predicate_key=predicate.predicate_key,
            predicate_version=predicate.version,
            frame_ids_and_versions=tuple(
                (item.frame_id, item.version) for item in frames
            ),
            role_layout_candidate_ids=tuple(item.candidate_id for item in local_layouts),
            capability_reference_candidate_ids=tuple(
                item.candidate_id for item in local_caps
            ),
            unresolved_alternative_candidate_ids=(),
            structural_state=state,
            candidate_only=True,
            predicate_selected=False,
            frame_selected=False,
            participant_assignment_selected=False,
            candidate_meaning_created=False,
            selected_meaning_created=False,
            permission_inferred=False,
            route_created=False,
            action_performed=False,
            memory_accessed=False,
            delivered=False,
            evidence_validity_determined=False,
            truth_determined=False,
        )
        action_candidate = with_expected_id(raw_candidate, "candidate_id")
        action_candidates.append(action_candidate)
        all_caps.extend(local_caps)
        all_layouts.extend(local_layouts)

    conflict_present = any(
        item.structural_state is CandidateStructuralState.CONFLICTED
        for item in action_candidates
    )
    ambiguous = len(action_candidates) > 1 or len(all_layouts) > len(action_candidates)
    incomplete = any(item.missing_required_role_ids for item in all_layouts)

    if conflict_present:
        status = CandidateProposalStatus.CONFLICTED
        reason_code = "exact_compatibility_conflict_preserved"
    elif ambiguous:
        status = CandidateProposalStatus.AMBIGUOUS
        reason_code = "multiple_exact_candidates_preserved"
    elif incomplete:
        status = CandidateProposalStatus.STRUCTURALLY_INCOMPLETE
        reason_code = "required_roles_unfilled_candidate_only"
    else:
        status = CandidateProposalStatus.CANDIDATES_PROPOSED
        reason_code = "exact_candidates_proposed_without_selection"

    unresolved = (
        tuple(item.candidate_id for item in action_candidates)
        if ambiguous or conflict_present
        else ()
    )
    missing_roles = _unique(
        role_id for item in all_layouts for role_id in item.missing_required_role_ids
    )
    conflicting_roles = _unique(
        role_id for item in all_layouts for role_id in item.conflicting_role_ids
    )
    ancestry = _source_ancestry(source)

    raw_result = PredicateRoleFrameCandidateProposalResult(
        result_id="",
        status=status,
        reason_code=reason_code,
        source_slice37_result_id=source.result_id,
        source_slice37_status=source.status.value,
        source_event_id=source.source_event_id,
        source_sha256=source.source_sha256,
        input_event_id=source.input_event_id,
        root_source_span_id=source.root_source_span_id,
        projection_id=source.projection_id,
        structural_result_id=source.structural_result_id,
        structural_set_id=source.structural_set_id,
        source_span_ids=ancestry["source_span_ids"],
        structural_ancestry_ids=ancestry["structural_ancestry_ids"],
        phase_trail_ids=ancestry["phase_trail_ids"],
        constrained_trail_ids=ancestry["constrained_trail_ids"],
        operator_graph_ids=ancestry["operator_graph_ids"],
        operator_node_ids=ancestry["operator_node_ids"],
        operator_definition_ids=ancestry["operator_definition_ids"],
        operator_keys_and_versions=ancestry["operator_keys_and_versions"],
        scope_occurrence_ids=ancestry["scope_occurrence_ids"],
        attachment_candidate_ids=ancestry["attachment_candidate_ids"],
        reference_analysis_ids=ancestry["reference_analysis_ids"],
        reference_candidate_ids=ancestry["reference_candidate_ids"],
        concept_candidate_proposal_ids=tuple(
            item.proposal_id for item in source.concept_candidates
        ),
        sense_candidate_proposal_ids=tuple(
            item.proposal_id for item in source.sense_candidates
        ),
        concept_ids_and_versions=tuple(
            (item.concept_id, item.concept_version)
            for item in source.concept_candidates
        ),
        sense_ids_and_versions=tuple(
            (item.sense_id, item.sense_version)
            for item in source.sense_candidates
        ),
        slice37_registry_snapshot_id=source.registry_snapshot.snapshot_id,
        slice38_registry_snapshot=slice38_snapshot,
        compatibility_registry_snapshot=compatibility_snapshot,
        action_predicate_candidates=tuple(action_candidates),
        role_layout_candidates=tuple(all_layouts),
        capability_reference_candidates=tuple(all_caps),
        unresolved_alternative_candidate_ids=unresolved,
        missing_role_ids=missing_roles,
        conflicting_role_ids=conflicting_roles,
        unsupported_reasons=(),
        unknown_reasons=(),
        action_predicate_candidate_count=len(action_candidates),
        role_layout_candidate_count=len(all_layouts),
        capability_reference_candidate_count=len(all_caps),
        unresolved_alternative_count=len(unresolved),
        missing_role_count=len(missing_roles),
        conflicting_role_count=len(conflicting_roles),
        source_ancestry_preserved=True,
        operator_ancestry_preserved=True,
        phase_trail_ancestry_preserved=True,
        scope_attachment_ancestry_preserved=True,
        registry_snapshots_preserved=True,
        zero_one_many_preserved=True,
        capability_non_invocation_boundary_preserved=True,
        candidate_order_is_ranked=False,
        selected_predicate_created=False,
        selected_frame_created=False,
        selected_participant_assignment_created=False,
        candidate_meaning_created=False,
        selected_meaning_created=False,
        permission_inferred=False,
        tool_route_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        delivered=False,
        evidence_validity_determined=False,
        truth_determined=False,
        clarification_outcome_created=False,
        refusal_outcome_created=False,
        blocked_progression_outcome_created=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        external_resource_loaded=False,
        language_model_used=False,
        embedding_used=False,
        semantic_similarity_used=False,
        profile=profile,
        non_authority_boundaries=SLICE38G_NON_AUTHORITY_BOUNDARIES,
    )
    result = with_expected_id(raw_result, "result_id")
    report = validate_result(result)
    if not report.ok:
        # Public proposal is total and fail-closed.  A construction defect may
        # not escape as a partially authoritative candidate object.
        return _base_result(
            source=source,
            status=CandidateProposalStatus.PREDECESSOR_REJECTED,
            reason_code="slice38g_internal_validation_failed_closed",
            profile=profile,
            slice38_snapshot=slice38_snapshot,
            compatibility_snapshot=compatibility_snapshot,
            unsupported_reasons=(
                "slice38g_internal_validation_failed_closed",
            ),
        )
    return result
