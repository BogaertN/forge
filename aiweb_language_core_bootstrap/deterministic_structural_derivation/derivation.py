"""Deterministic Slice 36G structural-analysis construction."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from ..candidate_resonant_phase_trail import (
    CandidateResonantPhaseTrail,
    CandidateResonantPhaseTrailResult,
    PhaseTrailCompletionStatus,
    PhaseTrailConstructionStatus,
    PhaseTrailNonProgressReason,
)
from ..input_event_custody import (
    InputCustodyStatus,
    InputEventCaptureResult,
)
from ..resonant_operator_candidate_binding import (
    CandidateBindingStatus,
    ResonantOperatorBindingCandidate,
    ResonantOperatorCandidateBindingResult,
    UnboundStructuralSignal,
)
from ..scope_attachment_reference_constraints import (
    AttachmentStatus,
    ReferenceAnalysisStatus,
    ScopeAttachmentReferenceConstraintResult,
    ScopeConstraintStatus,
)
from ..source_field_projection import (
    SourceFieldProjectionResult,
    reconstruct_source_field,
)
from ..schema import stable_record_id
from .rules import (
    build_default_structural_derivation_rules,
    structural_derivation_rule_for_key,
)
from .schema import (
    ABSOLUTE_MAX_GRAPH_EDGES_PER_CANDIDATE,
    ABSOLUTE_MAX_GRAPH_NODES_PER_CANDIDATE,
    ABSOLUTE_MAX_RULE_TRACES_PER_CANDIDATE,
    ABSOLUTE_MAX_SOURCE_RANGES_PER_CANDIDATE,
    ABSOLUTE_MAX_STRUCTURAL_CANDIDATES,
    CANONICAL_ROADMAP_AUTHORITY_REF,
    DEFAULT_MAX_GRAPH_EDGES_PER_CANDIDATE,
    DEFAULT_MAX_GRAPH_NODES_PER_CANDIDATE,
    DEFAULT_MAX_RULE_TRACES_PER_CANDIDATE,
    DEFAULT_MAX_SOURCE_RANGES_PER_CANDIDATE,
    DEFAULT_MAX_STRUCTURAL_CANDIDATES,
    RMC_LANGUAGE_LAW_AUTHORITY_REF,
    SLICE36A_AUTHORITY_REF,
    SLICE36B_AUTHORITY_REF,
    SLICE36C_AUTHORITY_REF,
    SLICE36D_AUTHORITY_REF,
    SLICE36E_AUTHORITY_REF,
    SLICE36F_AUTHORITY_REF,
    SLICE39_AUTHORITY_REF,
    SLICE40_AUTHORITY_REF,
    STRUCTURAL_DERIVATION_SCHEMA_VERSION,
    STRUCTURAL_DERIVATION_SPEC_ID,
    STRUCTURAL_DERIVATION_SPEC_VERSION,
    STRUCTURAL_LIMITS_SCHEMA_ID,
    STRUCTURAL_POLICY_SCHEMA_ID,
    DeterministicStructuralDerivationResult,
    StructuralAnalysisCandidate,
    StructuralAnalysisCandidateSet,
    StructuralCompletenessStatus,
    StructuralCoverageStatus,
    StructuralDerivationLimits,
    StructuralDerivationPolicy,
    StructuralDerivationStatus,
    StructuralEdgeKind,
    StructuralNonProgressReason,
    StructuralNonProgressResult,
    StructuralOperatorEdge,
    StructuralOperatorGraph,
    StructuralOperatorNode,
    StructuralRuleApplicationTrace,
    StructuralSourceCoverageProof,
    StructuralTraceLayer,
    StructuralTraceStatus,
)


_DEFAULT = object()


@dataclass(frozen=True, slots=True)
class _Ancestry:
    source_event_id: str
    source_sha256: str
    custody_result_id: str
    input_event_id: str
    root_source_span_id: str
    projection_result_id: str
    projection_id: str
    binding_result_id: str
    binding_set_id: str
    phase_trail_result_id: str
    phase_trail_set_id: str
    constraint_result_id: str
    constraint_set_id: str


def build_default_structural_derivation_policy() -> StructuralDerivationPolicy:
    body = {
        "policy_version": "1.0.0",
        "deterministic_only": True,
        "exact_ancestry_required": True,
        "source_reconstruction_required": True,
        "preserve_all_structural_candidates": True,
        "preserve_all_non_progress_reasons": True,
        "preserve_scope_attachments": True,
        "preserve_reference_candidates": True,
        "hidden_fallback_allowed": False,
        "candidate_meaning_authorized": False,
        "selected_meaning_authorized": False,
        "intended_meaning_selection_authorized": False,
        "concept_resolution_authorized": False,
        "sense_resolution_authorized": False,
        "predicate_identity_authorized": False,
        "participant_role_assignment_authorized": False,
        "truth_determination_authorized": False,
        "evidence_validity_determination_authorized": False,
        "clarification_question_authorized": False,
        "semantic_rejection_authorized": False,
        "permission_inference_authorized": False,
        "capability_selection_authorized": False,
        "route_creation_authorized": False,
        "tool_routing_authorized": False,
        "action_execution_authorized": False,
        "memory_read_authorized": False,
        "memory_write_authorized": False,
        "protected_memory_retrieval_authorized": False,
        "outward_rendering_authorized": False,
        "delivery_authorized": False,
        "source_authority_refs": (
            CANONICAL_ROADMAP_AUTHORITY_REF,
            RMC_LANGUAGE_LAW_AUTHORITY_REF,
            SLICE36A_AUTHORITY_REF,
            SLICE36B_AUTHORITY_REF,
            SLICE36C_AUTHORITY_REF,
            SLICE36D_AUTHORITY_REF,
            SLICE36E_AUTHORITY_REF,
            SLICE36F_AUTHORITY_REF,
            SLICE39_AUTHORITY_REF,
            SLICE40_AUTHORITY_REF,
        ),
        "structural_derivation_spec_id": STRUCTURAL_DERIVATION_SPEC_ID,
        "structural_derivation_spec_version": STRUCTURAL_DERIVATION_SPEC_VERSION,
        "schema_version": STRUCTURAL_DERIVATION_SCHEMA_VERSION,
        "policy_schema_id": STRUCTURAL_POLICY_SCHEMA_ID,
    }
    return StructuralDerivationPolicy(
        policy_id=stable_record_id("structural_derivation_policy", body),
        **body,
    )


def build_structural_derivation_limits(
    *,
    max_structural_candidates: int = DEFAULT_MAX_STRUCTURAL_CANDIDATES,
    max_rule_traces_per_candidate: int = DEFAULT_MAX_RULE_TRACES_PER_CANDIDATE,
    max_graph_nodes_per_candidate: int = DEFAULT_MAX_GRAPH_NODES_PER_CANDIDATE,
    max_graph_edges_per_candidate: int = DEFAULT_MAX_GRAPH_EDGES_PER_CANDIDATE,
    max_source_ranges_per_candidate: int = DEFAULT_MAX_SOURCE_RANGES_PER_CANDIDATE,
) -> StructuralDerivationLimits:
    body = {
        "max_structural_candidates": max_structural_candidates,
        "max_rule_traces_per_candidate": max_rule_traces_per_candidate,
        "max_graph_nodes_per_candidate": max_graph_nodes_per_candidate,
        "max_graph_edges_per_candidate": max_graph_edges_per_candidate,
        "max_source_ranges_per_candidate": max_source_ranges_per_candidate,
        "structural_derivation_spec_id": STRUCTURAL_DERIVATION_SPEC_ID,
        "structural_derivation_spec_version": STRUCTURAL_DERIVATION_SPEC_VERSION,
        "schema_version": STRUCTURAL_DERIVATION_SCHEMA_VERSION,
        "limits_schema_id": STRUCTURAL_LIMITS_SCHEMA_ID,
    }
    return StructuralDerivationLimits(
        limits_id=stable_record_id("structural_derivation_limits", body),
        **body,
    )


def default_structural_derivation_limits() -> StructuralDerivationLimits:
    return build_structural_derivation_limits()


def _policy_issues(policy: object) -> tuple[str, ...]:
    if type(policy) is not StructuralDerivationPolicy:
        return ("invalid_structural_derivation_policy_type",)
    issues: list[str] = []
    required_true = (
        "deterministic_only",
        "exact_ancestry_required",
        "source_reconstruction_required",
        "preserve_all_structural_candidates",
        "preserve_all_non_progress_reasons",
        "preserve_scope_attachments",
        "preserve_reference_candidates",
    )
    required_false = (
        "hidden_fallback_allowed",
        "candidate_meaning_authorized",
        "selected_meaning_authorized",
        "intended_meaning_selection_authorized",
        "concept_resolution_authorized",
        "sense_resolution_authorized",
        "predicate_identity_authorized",
        "participant_role_assignment_authorized",
        "truth_determination_authorized",
        "evidence_validity_determination_authorized",
        "clarification_question_authorized",
        "semantic_rejection_authorized",
        "permission_inference_authorized",
        "capability_selection_authorized",
        "route_creation_authorized",
        "tool_routing_authorized",
        "action_execution_authorized",
        "memory_read_authorized",
        "memory_write_authorized",
        "protected_memory_retrieval_authorized",
        "outward_rendering_authorized",
        "delivery_authorized",
    )
    for name in required_true:
        if getattr(policy, name) is not True:
            issues.append(f"policy_{name}_must_be_true")
    for name in required_false:
        if getattr(policy, name) is not False:
            issues.append(f"policy_{name}_must_be_false")
    if policy.policy_id != policy.expected_id():
        issues.append("policy_stable_id_mismatch")
    return tuple(issues)


def _limits_issues(limits: object) -> tuple[str, ...]:
    if type(limits) is not StructuralDerivationLimits:
        return ("invalid_structural_derivation_limits_type",)
    issues: list[str] = []
    values = (
        ("max_structural_candidates", limits.max_structural_candidates, ABSOLUTE_MAX_STRUCTURAL_CANDIDATES),
        ("max_rule_traces_per_candidate", limits.max_rule_traces_per_candidate, ABSOLUTE_MAX_RULE_TRACES_PER_CANDIDATE),
        ("max_graph_nodes_per_candidate", limits.max_graph_nodes_per_candidate, ABSOLUTE_MAX_GRAPH_NODES_PER_CANDIDATE),
        ("max_graph_edges_per_candidate", limits.max_graph_edges_per_candidate, ABSOLUTE_MAX_GRAPH_EDGES_PER_CANDIDATE),
        ("max_source_ranges_per_candidate", limits.max_source_ranges_per_candidate, ABSOLUTE_MAX_SOURCE_RANGES_PER_CANDIDATE),
    )
    for name, value, maximum in values:
        if type(value) is not int or value < 1 or value > maximum:
            issues.append(f"invalid_{name}")
    if limits.limits_id != limits.expected_id():
        issues.append("limits_stable_id_mismatch")
    return tuple(issues)


def _unique_text(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value for value in values if value))


def _unique_reasons(
    values: Iterable[StructuralNonProgressReason],
) -> tuple[StructuralNonProgressReason, ...]:
    filtered = tuple(
        value for value in values
        if value is not StructuralNonProgressReason.NONE
    )
    if not filtered:
        return (StructuralNonProgressReason.NONE,)
    order = {value: index for index, value in enumerate(StructuralNonProgressReason)}
    return tuple(sorted(set(filtered), key=lambda value: order[value]))


def _merge_ranges(
    values: Iterable[tuple[int, int]],
    *,
    maximum: int,
) -> tuple[tuple[int, int], ...]:
    normalized = sorted(
        {
            (max(0, start), min(maximum, end))
            for start, end in values
            if type(start) is int and type(end) is int and start < end
            and end > 0 and start < maximum
        }
    )
    merged: list[tuple[int, int]] = []
    for start, end in normalized:
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
        else:
            previous_start, previous_end = merged[-1]
            merged[-1] = (previous_start, max(previous_end, end))
    return tuple(merged)


def _complement_ranges(
    covered: tuple[tuple[int, int], ...],
    *,
    maximum: int,
) -> tuple[tuple[int, int], ...]:
    gaps: list[tuple[int, int]] = []
    cursor = 0
    for start, end in covered:
        if cursor < start:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < maximum:
        gaps.append((cursor, maximum))
    return tuple(gaps)


def _byte_range(
    projection: object,
    code_point_range: tuple[int, int],
) -> tuple[int, int]:
    start, end = code_point_range
    offsets = {
        boundary.code_point_offset: boundary.utf8_byte_offset
        for boundary in projection.boundaries
    }
    if start not in offsets or end not in offsets:
        raise ValueError("source_field_boundary_offset_missing")
    return offsets[start], offsets[end]


def _ancestry(
    custody_result: InputEventCaptureResult,
    projection_result: SourceFieldProjectionResult,
    binding_result: ResonantOperatorCandidateBindingResult,
    phase_trail_result: CandidateResonantPhaseTrailResult,
    constraint_result: ScopeAttachmentReferenceConstraintResult,
) -> _Ancestry | None:
    event = custody_result.event
    projection = projection_result.projection
    binding_set = binding_result.binding_set
    phase_set = phase_trail_result.phase_trail_set
    constraint_set = constraint_result.constraint_set
    if (
        event is None
        or projection is None
        or binding_set is None
        or phase_set is None
        or constraint_set is None
    ):
        return None
    identities = {
        event.input_event_id,
        projection.source_event_id,
        binding_set.source_event_id,
        phase_set.source_event_id,
        constraint_set.source_event_id,
    }
    hashes = {
        event.source_sha256,
        projection.source_sha256,
        binding_set.source_sha256,
        phase_set.source_sha256,
        constraint_set.source_sha256,
    }
    if len(identities) != 1 or len(hashes) != 1:
        return None
    if not (
        projection.projection_id == binding_set.projection_id
        == phase_set.projection_id == constraint_set.projection_id
    ):
        return None
    if not (
        binding_set.binding_set_id == phase_set.binding_set_id
        == constraint_set.binding_set_id
    ):
        return None
    if phase_set.phase_trail_set_id != constraint_set.phase_trail_set_id:
        return None
    return _Ancestry(
        source_event_id=event.input_event_id,
        source_sha256=event.source_sha256,
        custody_result_id=custody_result.result_id,
        input_event_id=event.input_event_id,
        root_source_span_id=event.root_source_span_id,
        projection_result_id=projection_result.result_id,
        projection_id=projection.projection_id,
        binding_result_id=binding_result.result_id,
        binding_set_id=binding_set.binding_set_id,
        phase_trail_result_id=phase_trail_result.result_id,
        phase_trail_set_id=phase_set.phase_trail_set_id,
        constraint_result_id=constraint_result.result_id,
        constraint_set_id=constraint_set.constraint_set_id,
    )


def _result(
    *,
    status: StructuralDerivationStatus,
    reason_code: str,
    policy: StructuralDerivationPolicy | None,
    limits: StructuralDerivationLimits | None,
    ancestry: _Ancestry | None,
    structural_set: StructuralAnalysisCandidateSet | None,
    issue_codes: tuple[str, ...] = (),
) -> DeterministicStructuralDerivationResult:
    body = {
        "status": status,
        "reason_code": reason_code,
        "structural_set_created": structural_set is not None,
        "explicit_non_progress_created": bool(
            structural_set and structural_set.non_progress_result
        ),
        "source_preserved_in_custody": bool(ancestry),
        "source_event_id": ancestry.source_event_id if ancestry else "",
        "source_sha256": ancestry.source_sha256 if ancestry else "",
        "projection_id": ancestry.projection_id if ancestry else "",
        "binding_set_id": ancestry.binding_set_id if ancestry else "",
        "phase_trail_set_id": ancestry.phase_trail_set_id if ancestry else "",
        "constraint_set_id": ancestry.constraint_set_id if ancestry else "",
        "policy": policy,
        "limits": limits,
        "structural_set": structural_set,
        "validation_issue_codes": issue_codes,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "repository_history_search_performed": False,
        "network_access_performed": False,
        "environment_access_performed": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "protected_memory_retrieval_performed": False,
        "web_search_performed": False,
        "embedding_performed": False,
        "language_model_used": False,
        "similarity_search_performed": False,
        "candidate_meaning_created": False,
        "selected_meaning": False,
        "intended_meaning_selected": False,
        "concept_resolved": False,
        "sense_resolved": False,
        "predicate_identity_created": False,
        "participant_roles_assigned": False,
        "truth_determined": False,
        "evidence_validity_determined": False,
        "clarification_question_asked": False,
        "semantic_rejection_performed": False,
        "permission_inferred": False,
        "capability_selected": False,
        "route_registration_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "outward_answer_rendered": False,
        "delivery_performed": False,
        "structural_derivation_spec_id": STRUCTURAL_DERIVATION_SPEC_ID,
        "structural_derivation_spec_version": STRUCTURAL_DERIVATION_SPEC_VERSION,
        "schema_version": STRUCTURAL_DERIVATION_SCHEMA_VERSION,
    }
    result = DeterministicStructuralDerivationResult(
        result_id="",
        **body,
    )
    return DeterministicStructuralDerivationResult(
        result_id=result.expected_id(),
        **body,
    )


def _trace(
    *,
    candidate_id: str,
    ordinal: int,
    rule_key: str,
    status: StructuralTraceStatus,
    source_rule_ids: tuple[str, ...],
    source_rule_versions: tuple[str, ...],
    input_record_ids: tuple[str, ...],
    output_record_ids: tuple[str, ...],
    source_span_ids: tuple[str, ...],
    code_point_ranges: tuple[tuple[int, int], ...],
    reason_codes: tuple[str, ...] = (),
) -> StructuralRuleApplicationTrace:
    rule = structural_derivation_rule_for_key(rule_key)
    if rule is None:
        raise ValueError(f"structural_derivation_rule_missing:{rule_key}")
    body = {
        "structural_candidate_id": candidate_id,
        "trace_ordinal": ordinal,
        "trace_layer": rule.trace_layer,
        "trace_status": status,
        "derivation_rule_id": rule.rule_id,
        "derivation_rule_key": rule.rule_key,
        "derivation_rule_version": rule.rule_version,
        "source_rule_ids": source_rule_ids,
        "source_rule_versions": source_rule_versions,
        "input_record_ids": input_record_ids,
        "output_record_ids": output_record_ids,
        "source_span_ids": source_span_ids,
        "code_point_ranges": code_point_ranges,
        "reason_codes": reason_codes,
        "candidate_only": True,
        "selected": False,
        "semantic_authority": False,
        "clarification_question_asked": False,
        "semantic_rejection_performed": False,
    }
    record = StructuralRuleApplicationTrace(trace_id="", **body)
    return replace(record, trace_id=record.expected_id())


def _build_graph(
    *,
    candidate_id: str,
    phase_trail: CandidateResonantPhaseTrail,
    binding_lookup: dict[str, ResonantOperatorBindingCandidate],
    scope_occurrences: tuple[object, ...],
    reference_analyses: tuple[object, ...],
    limits: StructuralDerivationLimits,
) -> StructuralOperatorGraph:
    participating = phase_trail.participating_binding_ids
    nodes: list[StructuralOperatorNode] = []
    node_by_binding: dict[str, StructuralOperatorNode] = {}
    for binding_id in participating:
        binding = binding_lookup.get(binding_id)
        if binding is None:
            continue
        body = {
            "structural_candidate_id": candidate_id,
            "candidate_binding_id": binding.candidate_binding_id,
            "candidate_operator_key": binding.candidate_operator_key,
            "candidate_operator_version": binding.candidate_operator_version,
            "candidate_operator_definition_id": binding.candidate_operator_definition_id,
            "candidate_operator_family": binding.candidate_operator_family,
            "source_span_ids": binding.source_span_ids,
            "code_point_ranges": binding.code_point_ranges,
            "utf8_byte_ranges": binding.utf8_byte_ranges,
            "exact_source_fragments": binding.exact_source_fragments,
            "phase_application_ids": tuple(
                application.application_id
                for application in phase_trail.applications
                if application.candidate_binding_id == binding_id
            ),
            "scope_occurrence_ids": tuple(
                occurrence.occurrence_id
                for occurrence in scope_occurrences
                if occurrence.candidate_binding_id == binding_id
            ),
            "reference_analysis_ids": tuple(
                analysis.analysis_id
                for analysis in reference_analyses
                if analysis.reference_binding_id == binding_id
            ),
            "possible_parent_binding_ids": binding.possible_parent_binding_ids,
            "possible_child_binding_ids": binding.possible_child_binding_ids,
            "competing_binding_ids": binding.competing_candidate_binding_ids,
            "unresolved": binding.unresolved,
            "unsupported": binding.unsupported,
            "malformed": binding.malformed,
            "candidate_only": True,
            "selected": False,
            "concept_meaning_created": False,
            "predicate_identity_created": False,
        }
        node_record = StructuralOperatorNode(node_id="", **body)
        node = replace(node_record, node_id=node_record.expected_id())
        nodes.append(node)
        node_by_binding[binding_id] = node
    if len(nodes) > limits.max_graph_nodes_per_candidate:
        raise OverflowError("graph_node_limit_exceeded")

    edge_keys: set[tuple[str, str, StructuralEdgeKind, str]] = set()
    edges: list[StructuralOperatorEdge] = []

    def add_edge(
        source_binding_id: str,
        target_binding_id: str,
        kind: StructuralEdgeKind,
        relationship: str,
        evidence: tuple[str, ...],
    ) -> None:
        source = node_by_binding.get(source_binding_id)
        target = node_by_binding.get(target_binding_id)
        if source is None or target is None or source.node_id == target.node_id:
            return
        key = (source.node_id, target.node_id, kind, relationship)
        if key in edge_keys:
            return
        edge_keys.add(key)
        body = {
            "structural_candidate_id": candidate_id,
            "source_node_id": source.node_id,
            "target_node_id": target.node_id,
            "edge_kind": kind,
            "relationship_code": relationship,
            "evidence_record_ids": evidence,
            "candidate_only": True,
            "selected": False,
        }
        edge_record = StructuralOperatorEdge(edge_id="", **body)
        edges.append(replace(edge_record, edge_id=edge_record.expected_id()))

    for binding_id in participating:
        binding = binding_lookup.get(binding_id)
        if binding is None:
            continue
        for child_id in binding.possible_child_binding_ids:
            add_edge(
                binding_id,
                child_id,
                StructuralEdgeKind.POSSIBLE_PARENT_CHILD,
                "explicit_possible_parent_child",
                (binding.candidate_binding_id,),
            )
        for competitor_id in binding.competing_candidate_binding_ids:
            if binding_id < competitor_id:
                add_edge(
                    binding_id,
                    competitor_id,
                    StructuralEdgeKind.COMPETING_CANDIDATES,
                    "explicit_material_competition",
                    (binding.candidate_binding_id, competitor_id),
                )

    applications = tuple(sorted(phase_trail.applications, key=lambda item: item.application_ordinal))
    for previous, current in zip(applications, applications[1:]):
        if previous.candidate_binding_id != current.candidate_binding_id:
            add_edge(
                previous.candidate_binding_id,
                current.candidate_binding_id,
                StructuralEdgeKind.APPLICATION_SEQUENCE,
                "explicit_phase_application_sequence",
                (previous.application_id, current.application_id),
            )
    if len(edges) > limits.max_graph_edges_per_candidate:
        raise OverflowError("graph_edge_limit_exceeded")

    body = {
        "structural_candidate_id": candidate_id,
        "nodes": tuple(nodes),
        "edges": tuple(edges),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "participating_binding_ids": participating,
        "conflicting_binding_ids": _unique_text(
            competitor
            for binding_id in participating
            for competitor in (
                binding_lookup[binding_id].competing_candidate_binding_ids
                if binding_id in binding_lookup else ()
            )
        ),
        "unresolved_binding_ids": tuple(
            binding_id
            for binding_id in participating
            if binding_id in binding_lookup and binding_lookup[binding_id].unresolved
        ),
        "all_participating_bindings_represented": len(nodes) == len(participating),
        "only_explicit_edges_created": True,
        "candidate_only": True,
        "selected_graph": False,
    }
    graph_record = StructuralOperatorGraph(graph_id="", **body)
    return replace(graph_record, graph_id=graph_record.expected_id())


def _build_coverage(
    *,
    candidate_id: str,
    projection: object,
    reconstruction: object,
    bindings: tuple[ResonantOperatorBindingCandidate, ...],
    scope_occurrences: tuple[object, ...],
    unbound_signals: tuple[UnboundStructuralSignal, ...],
    limits: StructuralDerivationLimits,
) -> StructuralSourceCoverageProof:
    ranges: list[tuple[int, int]] = []
    span_ids: list[str] = []
    for binding in bindings:
        ranges.extend(binding.code_point_ranges)
        span_ids.extend(binding.source_span_ids)
    for occurrence in scope_occurrences:
        ranges.extend(occurrence.exact_code_point_ranges)
        span_ids.extend(occurrence.exact_source_span_ids)
        for governed in occurrence.possible_governed_spans:
            ranges.extend(governed.code_point_ranges)
            span_ids.extend(governed.source_span_ids)
    for signal in unbound_signals:
        ranges.extend(signal.code_point_ranges)
        span_ids.extend(signal.source_span_ids)

    covered = _merge_ranges(ranges, maximum=projection.source_code_point_length)
    uncovered = _complement_ranges(covered, maximum=projection.source_code_point_length)
    if len(covered) + len(uncovered) > limits.max_source_ranges_per_candidate:
        raise OverflowError("source_range_limit_exceeded")
    covered_bytes = tuple(_byte_range(projection, item) for item in covered)
    uncovered_bytes = tuple(_byte_range(projection, item) for item in uncovered)
    unconsumed_span_ids = _unique_text(
        atom.source_span_id
        for atom in projection.code_points
        if any(start <= atom.ordinal < end for start, end in uncovered)
    )
    unconsumed_fragments = tuple(
        reconstruction.reconstructed_text[start:end]
        for start, end in uncovered
    )
    complete = not uncovered
    status = (
        StructuralCoverageStatus.COMPLETE_SOURCE_COVERAGE
        if complete
        else (
            StructuralCoverageStatus.PARTIAL_SOURCE_COVERAGE
            if covered
            else StructuralCoverageStatus.NO_OPERATOR_DERIVATION_COVERAGE
        )
    )
    body = {
        "structural_candidate_id": candidate_id,
        "source_event_id": projection.source_event_id,
        "source_sha256": projection.source_sha256,
        "projection_id": projection.projection_id,
        "source_code_point_length": projection.source_code_point_length,
        "source_utf8_byte_length": projection.source_utf8_byte_length,
        "consumed_source_span_ids": _unique_text(span_ids),
        "consumed_code_point_ranges": covered,
        "consumed_utf8_byte_ranges": covered_bytes,
        "unconsumed_source_span_ids": unconsumed_span_ids,
        "unconsumed_code_point_ranges": uncovered,
        "unconsumed_utf8_byte_ranges": uncovered_bytes,
        "unconsumed_exact_fragments": unconsumed_fragments,
        "coverage_status": status,
        "source_coverage_complete": complete,
        "source_reconstruction_proven": bool(reconstruction.ok),
        "reconstructed_source_sha256": reconstruction.reconstructed_source_sha256,
        "reconstruction_hash_matches_custody": (
            reconstruction.reconstructed_source_sha256 == projection.source_sha256
        ),
        "exact_source_ancestry": True,
    }
    coverage_record = StructuralSourceCoverageProof(coverage_proof_id="", **body)
    return replace(
        coverage_record,
        coverage_proof_id=coverage_record.expected_id(),
    )


def _candidate_reasons(
    *,
    custody_result: InputEventCaptureResult,
    binding_result: ResonantOperatorCandidateBindingResult,
    phase_trail_result: CandidateResonantPhaseTrailResult,
    constraint_result: ScopeAttachmentReferenceConstraintResult,
    phase_trail: CandidateResonantPhaseTrail,
    participating_bindings: tuple[ResonantOperatorBindingCandidate, ...],
    unbound_signals: tuple[UnboundStructuralSignal, ...],
    scope_occurrences: tuple[object, ...],
    reference_analyses: tuple[object, ...],
) -> tuple[StructuralNonProgressReason, ...]:
    reasons: list[StructuralNonProgressReason] = []

    if custody_result.status is InputCustodyStatus.REJECTED_MALFORMED:
        reasons.extend((
            StructuralNonProgressReason.MALFORMED_SOURCE_STRUCTURE,
            StructuralNonProgressReason.INCOMPLETE_INPUT,
        ))
    elif custody_result.status is InputCustodyStatus.CAPTURED_UNSUPPORTED:
        reasons.append(StructuralNonProgressReason.UNSUPPORTED_SOURCE_STRUCTURE)

    if binding_result.status is CandidateBindingStatus.CANDIDATE_BINDINGS_MALFORMED_SOURCE:
        reasons.append(StructuralNonProgressReason.MALFORMED_SOURCE_STRUCTURE)
    if any(item.unresolved for item in participating_bindings) or any(
        item.unresolved for item in unbound_signals
    ):
        reasons.append(StructuralNonProgressReason.UNRESOLVED_OPERATOR_BINDING)
    if any(item.unsupported for item in participating_bindings) or any(
        item.unsupported for item in unbound_signals
    ):
        reasons.append(StructuralNonProgressReason.UNSUPPORTED_SOURCE_STRUCTURE)
    if any(item.malformed for item in participating_bindings) or any(
        item.malformed for item in unbound_signals
    ):
        reasons.append(StructuralNonProgressReason.MALFORMED_SOURCE_STRUCTURE)

    if phase_trail_result.status is PhaseTrailConstructionStatus.CONFLICTING_PHASE_TRAILS:
        reasons.append(StructuralNonProgressReason.CONFLICTING_PHASE_TRAILS)
    if phase_trail_result.status is PhaseTrailConstructionStatus.MALFORMED_PHASE_TRAIL:
        reasons.append(StructuralNonProgressReason.MALFORMED_SOURCE_STRUCTURE)
    if phase_trail_result.status is PhaseTrailConstructionStatus.UNSUPPORTED_OPERATOR_SEQUENCE:
        reasons.append(StructuralNonProgressReason.UNSUPPORTED_OPERATOR_SEQUENCE)
    if phase_trail_result.status is PhaseTrailConstructionStatus.DRIFT_CONTAINED:
        reasons.append(StructuralNonProgressReason.DRIFT_CONTAINED)
    if phase_trail_result.status is PhaseTrailConstructionStatus.RECURSION_SUSPENDED:
        reasons.append(StructuralNonProgressReason.RECURSION_SUSPENDED)

    phase_reason_map = {
        PhaseTrailNonProgressReason.NO_OPERATOR_CANDIDATES: StructuralNonProgressReason.NO_SUPPORTED_DERIVATION,
        PhaseTrailNonProgressReason.SOURCE_PROGRESSION_HELD: StructuralNonProgressReason.INCOMPLETE_INPUT,
        PhaseTrailNonProgressReason.NO_AUTHORIZED_OPERATOR_EFFECT: StructuralNonProgressReason.UNSUPPORTED_OPERATOR_SEQUENCE,
        PhaseTrailNonProgressReason.COMPATIBILITY_OR_COMMUTATION_NOT_INSTALLED: StructuralNonProgressReason.INCOMPLETE_OPERATOR_TRAIL,
        PhaseTrailNonProgressReason.OPERATOR_EFFECT_REJECTED_PROGRESSION: StructuralNonProgressReason.UNSUPPORTED_OPERATOR_SEQUENCE,
        PhaseTrailNonProgressReason.OPERATOR_EFFECT_SUSPENDED_PROGRESSION: StructuralNonProgressReason.RECURSION_SUSPENDED,
        PhaseTrailNonProgressReason.PHASE_TRANSITION_LAW_NOT_INSTALLED: StructuralNonProgressReason.INCOMPLETE_OPERATOR_TRAIL,
        PhaseTrailNonProgressReason.TRAIL_LIMIT_EXCEEDED: StructuralNonProgressReason.NO_SUPPORTED_DERIVATION,
        PhaseTrailNonProgressReason.MALFORMED_INPUT: StructuralNonProgressReason.MALFORMED_SOURCE_STRUCTURE,
    }
    mapped = phase_reason_map.get(phase_trail.non_progress_reason)
    if mapped is not None:
        reasons.append(mapped)
    if phase_trail.drift_indicator_codes:
        reasons.append(StructuralNonProgressReason.DRIFT_CONTAINED)
    if phase_trail.suspended_branch_ids:
        reasons.append(StructuralNonProgressReason.RECURSION_SUSPENDED)
    if phase_trail.conflict_branch_ids:
        reasons.append(StructuralNonProgressReason.CONFLICTING_PHASE_TRAILS)
    if phase_trail.completion_status in {
        PhaseTrailCompletionStatus.OPEN_UNRESOLVED,
        PhaseTrailCompletionStatus.SEALED_UNPROVEN,
    }:
        reasons.append(StructuralNonProgressReason.INCOMPLETE_OPERATOR_TRAIL)

    if constraint_result.status is ScopeConstraintStatus.MALFORMED_SCOPE_ATTACHMENT:
        reasons.extend((
            StructuralNonProgressReason.MALFORMED_SOURCE_STRUCTURE,
            StructuralNonProgressReason.INCOMPLETE_INPUT,
        ))
    if constraint_result.status is ScopeConstraintStatus.UNSUPPORTED_SCOPE_ATTACHMENT:
        reasons.append(StructuralNonProgressReason.UNSUPPORTED_SOURCE_STRUCTURE)
    if constraint_result.status is ScopeConstraintStatus.PROHIBITED_CONTEXT_DEPENDENCY:
        reasons.append(StructuralNonProgressReason.PROHIBITED_CONTEXT_DEPENDENCY)

    for occurrence in scope_occurrences:
        if occurrence.attachment_status is AttachmentStatus.MALFORMED_ATTACHMENT:
            reasons.append(StructuralNonProgressReason.MALFORMED_SOURCE_STRUCTURE)
        elif occurrence.attachment_status is AttachmentStatus.UNSUPPORTED_ATTACHMENT:
            reasons.append(StructuralNonProgressReason.UNSUPPORTED_SOURCE_STRUCTURE)
        elif occurrence.attachment_status is AttachmentStatus.UNRESOLVED_ATTACHMENT:
            reasons.append(StructuralNonProgressReason.INCOMPLETE_OPERATOR_TRAIL)

    unresolved_reference_statuses = {
        ReferenceAnalysisStatus.ONE_SOURCE_SUPPORTED_REFERENCE_CANDIDATE,
        ReferenceAnalysisStatus.MULTIPLE_REFERENCE_CANDIDATES,
        ReferenceAnalysisStatus.UNRESOLVED_REFERENCE,
        ReferenceAnalysisStatus.MISSING_CONTEXT_REFERENCE,
    }
    for analysis in reference_analyses:
        if analysis.status in unresolved_reference_statuses:
            reasons.append(StructuralNonProgressReason.UNRESOLVED_REFERENCE)
        elif analysis.status is ReferenceAnalysisStatus.UNSUPPORTED_REFERENCE_FORM:
            reasons.append(StructuralNonProgressReason.UNSUPPORTED_SOURCE_STRUCTURE)
        elif analysis.status is ReferenceAnalysisStatus.PROHIBITED_CONTEXT_DEPENDENCY:
            reasons.append(StructuralNonProgressReason.PROHIBITED_CONTEXT_DEPENDENCY)

    return _unique_reasons(reasons)


def _completion(
    *,
    reasons: tuple[StructuralNonProgressReason, ...],
    phase_trail: CandidateResonantPhaseTrail,
    scope_occurrences: tuple[object, ...],
    reference_analyses: tuple[object, ...],
    conflicting_bindings: tuple[str, ...],
) -> tuple[StructuralCompletenessStatus, dict[str, bool]]:
    reason_set = set(reasons)
    malformed = StructuralNonProgressReason.MALFORMED_SOURCE_STRUCTURE in reason_set
    unsupported = bool(reason_set.intersection({
        StructuralNonProgressReason.UNSUPPORTED_SOURCE_STRUCTURE,
        StructuralNonProgressReason.UNSUPPORTED_OPERATOR_SEQUENCE,
        StructuralNonProgressReason.NO_SUPPORTED_DERIVATION,
    }))
    suspended = StructuralNonProgressReason.RECURSION_SUSPENDED in reason_set
    drift = StructuralNonProgressReason.DRIFT_CONTAINED in reason_set
    incomplete = bool(reason_set.intersection({
        StructuralNonProgressReason.UNRESOLVED_REFERENCE,
        StructuralNonProgressReason.UNRESOLVED_OPERATOR_BINDING,
        StructuralNonProgressReason.INCOMPLETE_INPUT,
        StructuralNonProgressReason.INCOMPLETE_OPERATOR_TRAIL,
        StructuralNonProgressReason.PROHIBITED_CONTEXT_DEPENDENCY,
    }))
    ambiguous = bool(
        conflicting_bindings
        or phase_trail.conflict_branch_ids
        or any(item.multiple_attachment for item in scope_occurrences)
        or any(
            item.status is ReferenceAnalysisStatus.MULTIPLE_REFERENCE_CANDIDATES
            for item in reference_analyses
        )
    )
    if malformed:
        status = StructuralCompletenessStatus.MALFORMED_BOUNDED_STRUCTURE
    elif unsupported:
        status = StructuralCompletenessStatus.UNSUPPORTED_BOUNDED_STRUCTURE
    elif suspended:
        status = StructuralCompletenessStatus.RECURSION_SUSPENDED_STRUCTURE
    elif drift:
        status = StructuralCompletenessStatus.DRIFT_CONTAINED_STRUCTURE
    elif incomplete:
        status = StructuralCompletenessStatus.INCOMPLETE_BOUNDED_STRUCTURE
    elif ambiguous:
        status = StructuralCompletenessStatus.AMBIGUOUS_BOUNDED_STRUCTURE
    else:
        status = StructuralCompletenessStatus.COMPLETE_BOUNDED_STRUCTURE
    return status, {
        "structurally_complete": status is StructuralCompletenessStatus.COMPLETE_BOUNDED_STRUCTURE,
        "malformed": malformed,
        "unsupported": unsupported,
        "ambiguous": ambiguous,
        "incomplete": incomplete,
        "contained_drift": drift,
        "suspended_recursion": suspended,
    }


def _build_candidate(
    *,
    structural_set_id: str,
    ancestry: _Ancestry,
    custody_result: InputEventCaptureResult,
    projection_result: SourceFieldProjectionResult,
    binding_result: ResonantOperatorCandidateBindingResult,
    phase_trail_result: CandidateResonantPhaseTrailResult,
    constraint_result: ScopeAttachmentReferenceConstraintResult,
    constrained_trail: object,
    phase_trail: CandidateResonantPhaseTrail,
    reconstruction: object,
    limits: StructuralDerivationLimits,
) -> StructuralAnalysisCandidate:
    projection = projection_result.projection
    binding_set = binding_result.binding_set
    if projection is None or binding_set is None:
        raise ValueError("predecessor_set_missing")
    candidate_id = stable_record_id(
        "structural_analysis_candidate_seed",
        {
            "structural_set_id": structural_set_id,
            "constrained_trail_id": constrained_trail.constrained_trail_id,
            "phase_trail_id": phase_trail.phase_trail_id,
            "structural_derivation_spec_id": STRUCTURAL_DERIVATION_SPEC_ID,
            "structural_derivation_spec_version": STRUCTURAL_DERIVATION_SPEC_VERSION,
            "schema_version": STRUCTURAL_DERIVATION_SCHEMA_VERSION,
        },
    )
    binding_lookup = {
        item.candidate_binding_id: item
        for item in binding_set.candidates
    }
    participating_bindings = tuple(
        binding_lookup[binding_id]
        for binding_id in phase_trail.participating_binding_ids
        if binding_id in binding_lookup
    )
    scope_occurrences = constrained_trail.scope_occurrences
    reference_analyses = constrained_trail.reference_analyses
    attachments = tuple(
        span
        for occurrence in scope_occurrences
        for span in occurrence.possible_governed_spans
    )
    reference_candidates = tuple(
        candidate
        for analysis in reference_analyses
        for candidate in analysis.candidates
    )
    unbound_signals = binding_set.unbound_structural_signals

    graph = _build_graph(
        candidate_id=candidate_id,
        phase_trail=phase_trail,
        binding_lookup=binding_lookup,
        scope_occurrences=scope_occurrences,
        reference_analyses=reference_analyses,
        limits=limits,
    )
    coverage = _build_coverage(
        candidate_id=candidate_id,
        projection=projection,
        reconstruction=reconstruction,
        bindings=participating_bindings,
        scope_occurrences=scope_occurrences,
        unbound_signals=unbound_signals,
        limits=limits,
    )
    reasons = _candidate_reasons(
        custody_result=custody_result,
        binding_result=binding_result,
        phase_trail_result=phase_trail_result,
        constraint_result=constraint_result,
        phase_trail=phase_trail,
        participating_bindings=participating_bindings,
        unbound_signals=unbound_signals,
        scope_occurrences=scope_occurrences,
        reference_analyses=reference_analyses,
    )
    completion_status, flags = _completion(
        reasons=reasons,
        phase_trail=phase_trail,
        scope_occurrences=scope_occurrences,
        reference_analyses=reference_analyses,
        conflicting_bindings=graph.conflicting_binding_ids,
    )

    traces: list[StructuralRuleApplicationTrace] = []
    def add_trace(**kwargs: object) -> None:
        trace = _trace(candidate_id=candidate_id, ordinal=len(traces), **kwargs)
        traces.append(trace)
        if len(traces) > limits.max_rule_traces_per_candidate:
            raise OverflowError("rule_trace_limit_exceeded")

    event = custody_result.event
    if event is None:
        raise ValueError("input_event_missing")
    add_trace(
        rule_key="preserve_input_custody_ancestry",
        status=StructuralTraceStatus.PRESERVED,
        source_rule_ids=(event.custody_spec_id,),
        source_rule_versions=(event.custody_spec_version,),
        input_record_ids=(custody_result.result_id,),
        output_record_ids=(event.input_event_id, event.root_source_span_id),
        source_span_ids=(event.root_source_span_id,),
        code_point_ranges=((0, event.code_point_length),),
    )
    add_trace(
        rule_key="verify_source_field_reconstruction",
        status=StructuralTraceStatus.PRESERVED,
        source_rule_ids=(projection.projection_spec_id,),
        source_rule_versions=(projection.projection_spec_version,),
        input_record_ids=(projection_result.result_id, projection.projection_id),
        output_record_ids=(reconstruction.result_id, coverage.coverage_proof_id),
        source_span_ids=(projection.root_source_span_id,),
        code_point_ranges=((0, projection.source_code_point_length),),
        reason_codes=(reconstruction.reason_code,),
    )
    for binding in participating_bindings:
        add_trace(
            rule_key="preserve_operator_binding_ancestry",
            status=(
                StructuralTraceStatus.UNRESOLVED
                if binding.unresolved else StructuralTraceStatus.PRESERVED
            ),
            source_rule_ids=(binding.proposal_rule_id,),
            source_rule_versions=(binding.proposal_rule_version,),
            input_record_ids=(binding_result.result_id, binding_set.binding_set_id),
            output_record_ids=(binding.candidate_binding_id,),
            source_span_ids=binding.source_span_ids,
            code_point_ranges=binding.code_point_ranges,
            reason_codes=_unique_text(
                binding.missing_prerequisite_codes
                + binding.conflicting_evidence_codes
            ),
        )
    for signal in unbound_signals:
        add_trace(
            rule_key="preserve_operator_binding_ancestry",
            status=StructuralTraceStatus.UNRESOLVED,
            source_rule_ids=(signal.proposal_rule_id,),
            source_rule_versions=(signal.proposal_rule_version,),
            input_record_ids=(binding_result.result_id, binding_set.binding_set_id),
            output_record_ids=(signal.signal_id,),
            source_span_ids=signal.source_span_ids,
            code_point_ranges=signal.code_point_ranges,
            reason_codes=(signal.signal_code,),
        )
    for application in phase_trail.applications:
        binding = binding_lookup.get(application.candidate_binding_id)
        add_trace(
            rule_key="preserve_phase_trail_ancestry",
            status=(
                StructuralTraceStatus.SUSPENDED
                if application.suspended_branch_ids
                else (
                    StructuralTraceStatus.CONTAINED
                    if application.containment_condition_codes
                    else StructuralTraceStatus.CANDIDATE_APPLIED
                )
            ),
            source_rule_ids=(
                binding.proposal_rule_id if binding else application.phase_transition_code,
            ),
            source_rule_versions=(
                binding.proposal_rule_version if binding else phase_trail.phase_trail_spec_version,
            ),
            input_record_ids=(application.input_state_id,),
            output_record_ids=(application.application_id, application.successor_state_id),
            source_span_ids=application.source_span_ids,
            code_point_ranges=(
                binding.code_point_ranges if binding else ()
            ),
            reason_codes=_unique_text(
                application.containment_condition_codes
                + application.drift_indicator_codes
                + application.suspended_branch_ids
            ),
        )
    for occurrence in scope_occurrences:
        trace_status = StructuralTraceStatus.PRESERVED
        if occurrence.malformed_attachment:
            trace_status = StructuralTraceStatus.MALFORMED
        elif occurrence.unsupported_attachment:
            trace_status = StructuralTraceStatus.UNSUPPORTED
        elif occurrence.unresolved_attachment:
            trace_status = StructuralTraceStatus.UNRESOLVED
        add_trace(
            rule_key="preserve_scope_attachment_candidates",
            status=trace_status,
            source_rule_ids=(occurrence.attachment_rule_id,),
            source_rule_versions=(occurrence.attachment_rule_version,),
            input_record_ids=(constrained_trail.constrained_trail_id, occurrence.candidate_binding_id),
            output_record_ids=(
                occurrence.occurrence_id,
                *(span.governed_span_id for span in occurrence.possible_governed_spans),
            ),
            source_span_ids=occurrence.exact_source_span_ids,
            code_point_ranges=occurrence.exact_code_point_ranges,
            reason_codes=(occurrence.attachment_status.value,),
        )
    for analysis in reference_analyses:
        trace_status = (
            StructuralTraceStatus.UNSUPPORTED
            if analysis.unsupported_reference_form
            else StructuralTraceStatus.UNRESOLVED
        )
        add_trace(
            rule_key="preserve_reference_candidates",
            status=trace_status,
            source_rule_ids=(analysis.reference_analysis_schema_id,),
            source_rule_versions=(analysis.scope_constraint_spec_version,),
            input_record_ids=(analysis.reference_binding_id,),
            output_record_ids=(
                analysis.analysis_id,
                *(item.reference_candidate_id for item in analysis.candidates),
            ),
            source_span_ids=analysis.source_span_ids,
            code_point_ranges=tuple(
                binding_lookup[analysis.reference_binding_id].code_point_ranges
                if analysis.reference_binding_id in binding_lookup else ()
            ),
            reason_codes=(analysis.status.value,),
        )
    add_trace(
        rule_key="build_explicit_operator_graph",
        status=StructuralTraceStatus.PRESERVED,
        source_rule_ids=(phase_trail.phase_trail_schema_id,),
        source_rule_versions=(phase_trail.phase_trail_spec_version,),
        input_record_ids=phase_trail.participating_binding_ids,
        output_record_ids=(graph.graph_id,),
        source_span_ids=_unique_text(
            span_id for binding in participating_bindings for span_id in binding.source_span_ids
        ),
        code_point_ranges=_merge_ranges(
            (item for binding in participating_bindings for item in binding.code_point_ranges),
            maximum=projection.source_code_point_length,
        ),
    )
    add_trace(
        rule_key="compute_bounded_source_coverage",
        status=StructuralTraceStatus.PRESERVED,
        source_rule_ids=(projection.source_field_schema_id,),
        source_rule_versions=(projection.projection_spec_version,),
        input_record_ids=(graph.graph_id,),
        output_record_ids=(coverage.coverage_proof_id,),
        source_span_ids=coverage.consumed_source_span_ids,
        code_point_ranges=coverage.consumed_code_point_ranges,
        reason_codes=(coverage.coverage_status.value,),
    )
    add_trace(
        rule_key="construct_candidate_per_constrained_trail",
        status=StructuralTraceStatus.CANDIDATE_APPLIED,
        source_rule_ids=(constrained_trail.constrained_trail_schema_id,),
        source_rule_versions=(constrained_trail.scope_constraint_spec_version,),
        input_record_ids=(constrained_trail.constrained_trail_id, phase_trail.phase_trail_id),
        output_record_ids=(candidate_id,),
        source_span_ids=coverage.consumed_source_span_ids,
        code_point_ranges=coverage.consumed_code_point_ranges,
    )
    if reasons != (StructuralNonProgressReason.NONE,):
        add_trace(
            rule_key="classify_lawful_non_progress",
            status=StructuralTraceStatus.UNRESOLVED,
            source_rule_ids=tuple(reason.value for reason in reasons),
            source_rule_versions=(STRUCTURAL_DERIVATION_SPEC_VERSION,) * len(reasons),
            input_record_ids=(candidate_id,),
            output_record_ids=(),
            source_span_ids=_unique_text(
                signal_span
                for signal in unbound_signals
                for signal_span in signal.source_span_ids
            ),
            code_point_ranges=tuple(
                item
                for signal in unbound_signals
                for item in signal.code_point_ranges
            ),
            reason_codes=tuple(reason.value for reason in reasons),
        )

    incompleteness = tuple(
        reason.value
        for reason in reasons
        if reason in {
            StructuralNonProgressReason.UNRESOLVED_REFERENCE,
            StructuralNonProgressReason.UNRESOLVED_OPERATOR_BINDING,
            StructuralNonProgressReason.INCOMPLETE_INPUT,
            StructuralNonProgressReason.INCOMPLETE_OPERATOR_TRAIL,
            StructuralNonProgressReason.PROHIBITED_CONTEXT_DEPENDENCY,
        }
    )
    unsupported = tuple(
        reason.value
        for reason in reasons
        if reason in {
            StructuralNonProgressReason.UNSUPPORTED_SOURCE_STRUCTURE,
            StructuralNonProgressReason.UNSUPPORTED_OPERATOR_SEQUENCE,
            StructuralNonProgressReason.NO_SUPPORTED_DERIVATION,
        }
    )
    containment = _unique_text(
        phase_trail.containment_condition_codes
        + tuple(
            evidence
            for occurrence in scope_occurrences
            for span in occurrence.possible_governed_spans
            for evidence in span.exact_attachment_evidence_codes
            if "contain" in evidence
        )
    )
    suspension = _unique_text(
        phase_trail.suspended_branch_ids
        + tuple(
            application.application_id
            for application in phase_trail.applications
            if application.suspended_branch_ids
        )
    )

    body = {
        "structural_set_id": structural_set_id,
        "source_event_id": ancestry.source_event_id,
        "source_sha256": ancestry.source_sha256,
        "custody_result_id": ancestry.custody_result_id,
        "input_event_id": ancestry.input_event_id,
        "root_source_span_id": ancestry.root_source_span_id,
        "projection_result_id": ancestry.projection_result_id,
        "projection_id": ancestry.projection_id,
        "binding_result_id": ancestry.binding_result_id,
        "binding_set_id": ancestry.binding_set_id,
        "phase_trail_result_id": ancestry.phase_trail_result_id,
        "phase_trail_set_id": ancestry.phase_trail_set_id,
        "constraint_result_id": ancestry.constraint_result_id,
        "constraint_set_id": ancestry.constraint_set_id,
        "constrained_trail_id": constrained_trail.constrained_trail_id,
        "phase_trail_id": phase_trail.phase_trail_id,
        "participating_binding_ids": phase_trail.participating_binding_ids,
        "operator_graph": graph,
        "phase_trail": phase_trail,
        "rule_application_traces": tuple(traces),
        "source_coverage": coverage,
        "scope_occurrences": scope_occurrences,
        "attachment_candidates": attachments,
        "reference_analyses": reference_analyses,
        "reference_candidates": reference_candidates,
        "unbound_structural_signals": unbound_signals,
        "unresolved_operator_span_ids": _unique_text(
            span_id
            for signal in unbound_signals
            for span_id in signal.source_span_ids
        ),
        "conflicting_operator_binding_ids": graph.conflicting_binding_ids,
        "attachment_alternative_ids": tuple(item.governed_span_id for item in attachments),
        "reference_alternative_ids": tuple(item.reference_candidate_id for item in reference_candidates),
        "incompleteness_reasons": incompleteness,
        "unsupported_reasons": unsupported,
        "containment_reasons": containment,
        "suspension_reasons": suspension,
        "non_progress_reasons": reasons,
        "completeness_status": completion_status,
        **flags,
        "exact_ancestry_complete": True,
        "source_reconstruction_proven": bool(
            coverage.source_reconstruction_proven
            and coverage.reconstruction_hash_matches_custody
        ),
        "predecessor_records_preserved": True,
        "candidate_only": True,
        "selected_structure": False,
        "candidate_meaning_created": False,
        "selected_meaning": False,
        "concept_resolved": False,
        "sense_resolved": False,
        "predicate_identity_created": False,
        "participant_roles_assigned": False,
        "truth_determined": False,
        "evidence_validity_determined": False,
        "clarification_question_asked": False,
        "semantic_rejection_performed": False,
        "permission_inferred": False,
        "capability_selected": False,
        "route_created": False,
        "tool_routing_performed": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "protected_memory_retrieved": False,
        "action_performed": False,
        "outward_answer_rendered": False,
        "delivery_performed": False,
    }
    return StructuralAnalysisCandidate(
        structural_candidate_id=candidate_id,
        **body,
    )


def _zero_reasons(
    *,
    custody_result: InputEventCaptureResult,
    binding_result: ResonantOperatorCandidateBindingResult,
    phase_trail_result: CandidateResonantPhaseTrailResult,
    constraint_result: ScopeAttachmentReferenceConstraintResult,
) -> tuple[StructuralNonProgressReason, ...]:
    reasons: list[StructuralNonProgressReason] = []
    if custody_result.status is InputCustodyStatus.REJECTED_MALFORMED:
        reasons.extend((
            StructuralNonProgressReason.MALFORMED_SOURCE_STRUCTURE,
            StructuralNonProgressReason.INCOMPLETE_INPUT,
        ))
    elif custody_result.status is InputCustodyStatus.CAPTURED_UNSUPPORTED:
        reasons.append(StructuralNonProgressReason.UNSUPPORTED_SOURCE_STRUCTURE)
    if binding_result.status is CandidateBindingStatus.CANDIDATE_BINDINGS_MALFORMED_SOURCE:
        reasons.append(StructuralNonProgressReason.MALFORMED_SOURCE_STRUCTURE)
    if phase_trail_result.status is PhaseTrailConstructionStatus.UNSUPPORTED_OPERATOR_SEQUENCE:
        reasons.append(StructuralNonProgressReason.UNSUPPORTED_OPERATOR_SEQUENCE)
    if constraint_result.status is ScopeConstraintStatus.PROHIBITED_CONTEXT_DEPENDENCY:
        reasons.append(StructuralNonProgressReason.PROHIBITED_CONTEXT_DEPENDENCY)
    if not reasons:
        reasons.append(StructuralNonProgressReason.NO_SUPPORTED_DERIVATION)
    return _unique_reasons(reasons)


def _non_progress(
    *,
    structural_set_id: str,
    ancestry: _Ancestry,
    reasons: tuple[StructuralNonProgressReason, ...],
    candidates: tuple[StructuralAnalysisCandidate, ...],
) -> StructuralNonProgressResult | None:
    active = tuple(reason for reason in reasons if reason is not StructuralNonProgressReason.NONE)
    if not active:
        return None
    blocking = _unique_text(
        item
        for candidate in candidates
        for item in (
            candidate.constrained_trail_id,
            candidate.phase_trail_id,
            *candidate.unresolved_operator_span_ids,
            *candidate.attachment_alternative_ids,
            *candidate.reference_alternative_ids,
        )
    )
    unresolved_spans = _unique_text(
        span_id
        for candidate in candidates
        for span_id in candidate.unresolved_operator_span_ids
    )
    body = {
        "structural_set_id": structural_set_id,
        "source_event_id": ancestry.source_event_id,
        "projection_id": ancestry.projection_id,
        "binding_set_id": ancestry.binding_set_id,
        "phase_trail_set_id": ancestry.phase_trail_set_id,
        "constraint_set_id": ancestry.constraint_set_id,
        "reasons": active,
        "primary_reason": active[0],
        "structural_candidate_ids": tuple(item.structural_candidate_id for item in candidates),
        "blocking_record_ids": blocking,
        "unresolved_source_span_ids": unresolved_spans,
        "valid_result": True,
        "guessed_to_avoid_non_progress": False,
        "clarification_question_asked": False,
        "semantic_rejection_performed": False,
        "candidate_meaning_created": False,
        "selected_meaning": False,
    }
    non_progress_record = StructuralNonProgressResult(
        non_progress_id="",
        **body,
    )
    return replace(
        non_progress_record,
        non_progress_id=non_progress_record.expected_id(),
    )


def derive_deterministic_structural_analysis(
    custody_result: object,
    projection_result: object,
    binding_result: object,
    phase_trail_result: object,
    constraint_result: object,
    *,
    policy: object = _DEFAULT,
    limits: object = _DEFAULT,
) -> DeterministicStructuralDerivationResult:
    active_policy = (
        build_default_structural_derivation_policy()
        if policy is _DEFAULT else policy
    )
    active_limits = (
        default_structural_derivation_limits()
        if limits is _DEFAULT else limits
    )
    policy_issues = _policy_issues(active_policy)
    limits_issues = _limits_issues(active_limits)
    type_issues = []
    expected_types = (
        (custody_result, InputEventCaptureResult, "custody_result"),
        (projection_result, SourceFieldProjectionResult, "projection_result"),
        (binding_result, ResonantOperatorCandidateBindingResult, "binding_result"),
        (phase_trail_result, CandidateResonantPhaseTrailResult, "phase_trail_result"),
        (constraint_result, ScopeAttachmentReferenceConstraintResult, "constraint_result"),
    )
    for value, expected, name in expected_types:
        if type(value) is not expected:
            type_issues.append(f"invalid_{name}_type")
    issue_codes = tuple(type_issues) + policy_issues + limits_issues
    if issue_codes:
        return _result(
            status=StructuralDerivationStatus.STRUCTURAL_DERIVATION_FAILED,
            reason_code="invalid_structural_derivation_input",
            policy=(active_policy if type(active_policy) is StructuralDerivationPolicy else None),
            limits=(active_limits if type(active_limits) is StructuralDerivationLimits else None),
            ancestry=None,
            structural_set=None,
            issue_codes=issue_codes,
        )

    assert isinstance(custody_result, InputEventCaptureResult)
    assert isinstance(projection_result, SourceFieldProjectionResult)
    assert isinstance(binding_result, ResonantOperatorCandidateBindingResult)
    assert isinstance(phase_trail_result, CandidateResonantPhaseTrailResult)
    assert isinstance(constraint_result, ScopeAttachmentReferenceConstraintResult)
    assert isinstance(active_policy, StructuralDerivationPolicy)
    assert isinstance(active_limits, StructuralDerivationLimits)

    ancestry = _ancestry(
        custody_result,
        projection_result,
        binding_result,
        phase_trail_result,
        constraint_result,
    )
    if ancestry is None:
        return _result(
            status=StructuralDerivationStatus.STRUCTURAL_DERIVATION_FAILED,
            reason_code="predecessor_ancestry_mismatch_or_missing",
            policy=active_policy,
            limits=active_limits,
            ancestry=None,
            structural_set=None,
            issue_codes=("exact_predecessor_ancestry_required",),
        )

    projection = projection_result.projection
    phase_set = phase_trail_result.phase_trail_set
    constraint_set = constraint_result.constraint_set
    if projection is None or phase_set is None or constraint_set is None:
        return _result(
            status=StructuralDerivationStatus.STRUCTURAL_DERIVATION_FAILED,
            reason_code="predecessor_record_missing",
            policy=active_policy,
            limits=active_limits,
            ancestry=ancestry,
            structural_set=None,
            issue_codes=("required_predecessor_record_missing",),
        )

    reconstruction = reconstruct_source_field(projection)
    if (
        not reconstruction.ok
        or reconstruction.reconstructed_source_sha256 != ancestry.source_sha256
    ):
        return _result(
            status=StructuralDerivationStatus.STRUCTURAL_DERIVATION_FAILED,
            reason_code="source_reconstruction_proof_failed",
            policy=active_policy,
            limits=active_limits,
            ancestry=ancestry,
            structural_set=None,
            issue_codes=("exact_source_reconstruction_required",),
        )

    structural_set_id = stable_record_id(
        "structural_analysis_candidate_set",
        {
            "source_event_id": ancestry.source_event_id,
            "source_sha256": ancestry.source_sha256,
            "custody_result_id": ancestry.custody_result_id,
            "projection_result_id": ancestry.projection_result_id,
            "binding_result_id": ancestry.binding_result_id,
            "phase_trail_result_id": ancestry.phase_trail_result_id,
            "constraint_result_id": ancestry.constraint_result_id,
            "policy_id": active_policy.policy_id,
            "limits_id": active_limits.limits_id,
            "structural_derivation_spec_id": STRUCTURAL_DERIVATION_SPEC_ID,
            "structural_derivation_spec_version": STRUCTURAL_DERIVATION_SPEC_VERSION,
            "schema_version": STRUCTURAL_DERIVATION_SCHEMA_VERSION,
            "structural_set_schema_id": "aiweb.slice36g.structural_set.v1",
        },
    )

    constrained_trails = constraint_set.constrained_trails
    if len(constrained_trails) > active_limits.max_structural_candidates:
        return _result(
            status=StructuralDerivationStatus.STRUCTURAL_DERIVATION_LIMIT_EXCEEDED,
            reason_code="structural_candidate_limit_exceeded",
            policy=active_policy,
            limits=active_limits,
            ancestry=ancestry,
            structural_set=None,
            issue_codes=("max_structural_candidates_exceeded",),
        )

    phase_lookup = {item.phase_trail_id: item for item in phase_set.trails}
    candidates: list[StructuralAnalysisCandidate] = []
    try:
        for constrained in constrained_trails:
            phase_trail = phase_lookup.get(constrained.phase_trail_id)
            if phase_trail is None:
                raise ValueError("constrained_phase_trail_missing")
            candidates.append(
                _build_candidate(
                    structural_set_id=structural_set_id,
                    ancestry=ancestry,
                    custody_result=custody_result,
                    projection_result=projection_result,
                    binding_result=binding_result,
                    phase_trail_result=phase_trail_result,
                    constraint_result=constraint_result,
                    constrained_trail=constrained,
                    phase_trail=phase_trail,
                    reconstruction=reconstruction,
                    limits=active_limits,
                )
            )
    except (ValueError, OverflowError) as error:
        return _result(
            status=(
                StructuralDerivationStatus.STRUCTURAL_DERIVATION_LIMIT_EXCEEDED
                if isinstance(error, OverflowError)
                else StructuralDerivationStatus.STRUCTURAL_DERIVATION_FAILED
            ),
            reason_code=str(error),
            policy=active_policy,
            limits=active_limits,
            ancestry=ancestry,
            structural_set=None,
            issue_codes=(str(error),),
        )

    candidate_tuple = tuple(candidates)
    if not candidate_tuple:
        status = StructuralDerivationStatus.ZERO_STRUCTURAL_CANDIDATES
        aggregate_reasons = _zero_reasons(
            custody_result=custody_result,
            binding_result=binding_result,
            phase_trail_result=phase_trail_result,
            constraint_result=constraint_result,
        )
        reason_code = "no_supported_structural_derivation"
    elif len(candidate_tuple) == 1:
        status = StructuralDerivationStatus.ONE_STRUCTURAL_CANDIDATE
        aggregate_reasons = _unique_reasons(
            reason for candidate in candidate_tuple for reason in candidate.non_progress_reasons
        )
        reason_code = "one_structural_candidate_derived_without_meaning_selection"
    else:
        status = StructuralDerivationStatus.MULTIPLE_STRUCTURAL_CANDIDATES
        aggregate_reasons = _unique_reasons(
            (
                StructuralNonProgressReason.MULTIPLE_STRUCTURAL_CANDIDATES,
                *(reason for candidate in candidate_tuple for reason in candidate.non_progress_reasons),
            )
        )
        reason_code = "multiple_structural_candidates_preserved_without_selection"

    non_progress_result = _non_progress(
        structural_set_id=structural_set_id,
        ancestry=ancestry,
        reasons=aggregate_reasons,
        candidates=candidate_tuple,
    )
    all_scope_ids = {
        item.occurrence_id
        for constrained in constraint_set.constrained_trails
        for item in constrained.scope_occurrences
    }
    candidate_scope_ids = {
        item.occurrence_id
        for candidate in candidate_tuple
        for item in candidate.scope_occurrences
    }
    all_attachment_ids = {
        span.governed_span_id
        for constrained in constraint_set.constrained_trails
        for occurrence in constrained.scope_occurrences
        for span in occurrence.possible_governed_spans
    }
    candidate_attachment_ids = {
        item.governed_span_id
        for candidate in candidate_tuple
        for item in candidate.attachment_candidates
    }
    all_reference_ids = {
        item.reference_candidate_id
        for constrained in constraint_set.constrained_trails
        for analysis in constrained.reference_analyses
        for item in analysis.candidates
    }
    candidate_reference_ids = {
        item.reference_candidate_id
        for candidate in candidate_tuple
        for item in candidate.reference_candidates
    }

    set_body = {
        "source_event_id": ancestry.source_event_id,
        "source_sha256": ancestry.source_sha256,
        "custody_result_id": ancestry.custody_result_id,
        "projection_result_id": ancestry.projection_result_id,
        "projection_id": ancestry.projection_id,
        "binding_result_id": ancestry.binding_result_id,
        "binding_set_id": ancestry.binding_set_id,
        "phase_trail_result_id": ancestry.phase_trail_result_id,
        "phase_trail_set_id": ancestry.phase_trail_set_id,
        "constraint_result_id": ancestry.constraint_result_id,
        "constraint_set_id": ancestry.constraint_set_id,
        "policy_id": active_policy.policy_id,
        "limits_id": active_limits.limits_id,
        "status": status,
        "candidates": candidate_tuple,
        "candidate_count": len(candidate_tuple),
        "complete_candidate_count": sum(item.structurally_complete for item in candidate_tuple),
        "ambiguous_candidate_count": sum(item.ambiguous for item in candidate_tuple),
        "incomplete_candidate_count": sum(item.incomplete for item in candidate_tuple),
        "malformed_candidate_count": sum(item.malformed for item in candidate_tuple),
        "unsupported_candidate_count": sum(item.unsupported for item in candidate_tuple),
        "contained_drift_candidate_count": sum(item.contained_drift for item in candidate_tuple),
        "suspended_recursion_candidate_count": sum(item.suspended_recursion for item in candidate_tuple),
        "aggregate_non_progress_reasons": aggregate_reasons,
        "non_progress_result": non_progress_result,
        "all_source_ancestry_preserved": all(item.exact_ancestry_complete for item in candidate_tuple) if candidate_tuple else True,
        "all_source_reconstruction_proven": all(item.source_reconstruction_proven for item in candidate_tuple) if candidate_tuple else reconstruction.ok,
        "all_phase_trails_preserved": (
            {item.phase_trail_id for item in candidate_tuple}
            == {item.phase_trail_id for item in constraint_set.constrained_trails}
        ),
        "all_scope_occurrences_preserved": candidate_scope_ids == all_scope_ids,
        "all_attachment_candidates_preserved": candidate_attachment_ids == all_attachment_ids,
        "all_reference_candidates_preserved": candidate_reference_ids == all_reference_ids,
        "structural_candidate_plurality_preserved": len(candidate_tuple) == len(constraint_set.constrained_trails),
        "selected_structural_candidate_id": None,
        "candidate_meaning_created": False,
        "selected_meaning": False,
        "clarification_question_asked": False,
        "semantic_rejection_performed": False,
        "hidden_fallback_allowed": False,
    }
    structural_set = StructuralAnalysisCandidateSet(
        structural_set_id=structural_set_id,
        **set_body,
    )
    return _result(
        status=status,
        reason_code=reason_code,
        policy=active_policy,
        limits=active_limits,
        ancestry=ancestry,
        structural_set=structural_set,
    )
