"""Deterministic validators for Slice 36G records."""

from __future__ import annotations

from ..schema import SCHEMA_VERSION, ValidationIssue, ValidationReport, issue
from .rules import build_default_structural_derivation_rules
from .schema import (
    ABSOLUTE_MAX_GRAPH_EDGES_PER_CANDIDATE,
    ABSOLUTE_MAX_GRAPH_NODES_PER_CANDIDATE,
    ABSOLUTE_MAX_RULE_TRACES_PER_CANDIDATE,
    ABSOLUTE_MAX_SOURCE_RANGES_PER_CANDIDATE,
    ABSOLUTE_MAX_STRUCTURAL_CANDIDATES,
    STRUCTURAL_CANDIDATE_SCHEMA_ID,
    STRUCTURAL_COVERAGE_SCHEMA_ID,
    STRUCTURAL_DERIVATION_SCHEMA_VERSION,
    STRUCTURAL_DERIVATION_SPEC_ID,
    STRUCTURAL_DERIVATION_SPEC_VERSION,
    STRUCTURAL_EDGE_SCHEMA_ID,
    STRUCTURAL_GRAPH_SCHEMA_ID,
    STRUCTURAL_LIMITS_SCHEMA_ID,
    STRUCTURAL_NODE_SCHEMA_ID,
    STRUCTURAL_NON_PROGRESS_SCHEMA_ID,
    STRUCTURAL_POLICY_SCHEMA_ID,
    STRUCTURAL_RESULT_SCHEMA_ID,
    STRUCTURAL_RULE_SCHEMA_ID,
    STRUCTURAL_SET_SCHEMA_ID,
    STRUCTURAL_TRACE_SCHEMA_ID,
    DeterministicStructuralDerivationResult,
    StructuralAnalysisCandidate,
    StructuralAnalysisCandidateSet,
    StructuralCompletenessStatus,
    StructuralDerivationLimits,
    StructuralDerivationPolicy,
    StructuralDerivationRule,
    StructuralDerivationStatus,
    StructuralNonProgressReason,
    StructuralNonProgressResult,
    StructuralOperatorEdge,
    StructuralOperatorGraph,
    StructuralOperatorNode,
    StructuralRuleApplicationTrace,
    StructuralSourceCoverageProof,
)


def _report(issues: list[ValidationIssue] | tuple[ValidationIssue, ...]) -> ValidationReport:
    items = tuple(issues)
    return ValidationReport(
        schema_version=SCHEMA_VERSION,
        ok=not items,
        issues=items,
    )


def _common(
    issues: list[ValidationIssue],
    record: object,
    schema_field: str,
    expected_schema_id: str,
) -> None:
    if getattr(record, "structural_derivation_spec_id", None) != STRUCTURAL_DERIVATION_SPEC_ID:
        issues.append(issue("structural_derivation_spec_id", "unexpected_value"))
    if (
        getattr(record, "structural_derivation_spec_version", None)
        != STRUCTURAL_DERIVATION_SPEC_VERSION
    ):
        issues.append(issue("structural_derivation_spec_version", "unexpected_value"))
    if getattr(record, "schema_version", None) != STRUCTURAL_DERIVATION_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unexpected_value"))
    if getattr(record, schema_field, None) != expected_schema_id:
        issues.append(issue(schema_field, "unexpected_value"))


def _must_false(
    issues: list[ValidationIssue],
    record: object,
    names: tuple[str, ...],
) -> None:
    for name in names:
        if getattr(record, name, None) is not False:
            issues.append(issue(name, "must_remain_false"))


def _must_true(
    issues: list[ValidationIssue],
    record: object,
    names: tuple[str, ...],
) -> None:
    for name in names:
        if getattr(record, name, None) is not True:
            issues.append(issue(name, "must_remain_true"))


def _text_tuple(
    issues: list[ValidationIssue],
    name: str,
    value: object,
    *,
    allow_empty: bool = True,
) -> None:
    if type(value) is not tuple:
        issues.append(issue(name, "invalid_tuple_type"))
        return
    if not allow_empty and not value:
        issues.append(issue(name, "required_non_empty_tuple"))
    if any(not isinstance(item, str) or not item for item in value):
        issues.append(issue(name, "invalid_text_tuple"))
    if len(value) != len(set(value)):
        issues.append(issue(name, "duplicate_values"))


def validate_structural_derivation_policy(policy: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(policy) is not StructuralDerivationPolicy:
        return _report((issue("policy", "invalid_type"),))
    if policy.policy_id != policy.expected_id():
        issues.append(issue("policy_id", "stable_id_mismatch"))
    _common(issues, policy, "policy_schema_id", STRUCTURAL_POLICY_SCHEMA_ID)
    _must_true(
        issues,
        policy,
        (
            "deterministic_only",
            "exact_ancestry_required",
            "source_reconstruction_required",
            "preserve_all_structural_candidates",
            "preserve_all_non_progress_reasons",
            "preserve_scope_attachments",
            "preserve_reference_candidates",
        ),
    )
    _must_false(
        issues,
        policy,
        (
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
        ),
    )
    _text_tuple(issues, "source_authority_refs", policy.source_authority_refs, allow_empty=False)
    return _report(issues)


def validate_structural_derivation_limits(limits: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(limits) is not StructuralDerivationLimits:
        return _report((issue("limits", "invalid_type"),))
    if limits.limits_id != limits.expected_id():
        issues.append(issue("limits_id", "stable_id_mismatch"))
    _common(issues, limits, "limits_schema_id", STRUCTURAL_LIMITS_SCHEMA_ID)
    absolute_limits = {
        "max_structural_candidates": ABSOLUTE_MAX_STRUCTURAL_CANDIDATES,
        "max_rule_traces_per_candidate": ABSOLUTE_MAX_RULE_TRACES_PER_CANDIDATE,
        "max_graph_nodes_per_candidate": ABSOLUTE_MAX_GRAPH_NODES_PER_CANDIDATE,
        "max_graph_edges_per_candidate": ABSOLUTE_MAX_GRAPH_EDGES_PER_CANDIDATE,
        "max_source_ranges_per_candidate": ABSOLUTE_MAX_SOURCE_RANGES_PER_CANDIDATE,
    }
    for name, absolute_maximum in absolute_limits.items():
        value = getattr(limits, name)
        if type(value) is not int or value < 1:
            issues.append(issue(name, "invalid_limit"))
        elif value > absolute_maximum:
            issues.append(issue(name, "exceeds_absolute_limit"))
    return _report(issues)


def validate_structural_derivation_rule(rule: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(rule) is not StructuralDerivationRule:
        return _report((issue("rule", "invalid_type"),))
    if rule.rule_id != rule.expected_id():
        issues.append(issue("rule_id", "stable_id_mismatch"))
    _common(issues, rule, "rule_schema_id", STRUCTURAL_RULE_SCHEMA_ID)
    _must_true(issues, rule, ("exact_predecessor_record_required",))
    _must_false(
        issues,
        rule,
        (
            "creates_selected_meaning",
            "asks_clarification_question",
            "performs_semantic_rejection",
        ),
    )
    _text_tuple(issues, "source_authority_refs", rule.source_authority_refs, allow_empty=False)
    return _report(issues)


def validate_default_structural_derivation_rules() -> ValidationReport:
    issues: list[ValidationIssue] = []
    rules = build_default_structural_derivation_rules()
    if len(rules) != 10:
        issues.append(issue("rules", "expected_exactly_ten_rules"))
    if len({item.rule_id for item in rules}) != len(rules):
        issues.append(issue("rules", "duplicate_rule_id"))
    if len({item.rule_key for item in rules}) != len(rules):
        issues.append(issue("rules", "duplicate_rule_key"))
    if sum(item.creates_structural_candidate for item in rules) != 1:
        issues.append(issue("rules", "exactly_one_candidate_construction_rule_required"))
    for index, rule in enumerate(rules):
        report = validate_structural_derivation_rule(rule)
        for item in report.issues:
            issues.append(issue(f"rules[{index}].{item.field}", item.code, item.detail))
    return _report(issues)


def validate_structural_rule_application_trace(trace: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(trace) is not StructuralRuleApplicationTrace:
        return _report((issue("trace", "invalid_type"),))
    if trace.trace_id != trace.expected_id():
        issues.append(issue("trace_id", "stable_id_mismatch"))
    _common(issues, trace, "trace_schema_id", STRUCTURAL_TRACE_SCHEMA_ID)
    if type(trace.trace_ordinal) is not int or trace.trace_ordinal < 0:
        issues.append(issue("trace_ordinal", "invalid_ordinal"))
    _must_true(issues, trace, ("candidate_only",))
    _must_false(
        issues,
        trace,
        (
            "selected",
            "semantic_authority",
            "clarification_question_asked",
            "semantic_rejection_performed",
        ),
    )
    if len(trace.source_rule_ids) != len(trace.source_rule_versions):
        issues.append(issue("source_rule_versions", "rule_identity_version_count_mismatch"))
    return _report(issues)


def validate_structural_operator_node(node: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(node) is not StructuralOperatorNode:
        return _report((issue("node", "invalid_type"),))
    if node.node_id != node.expected_id():
        issues.append(issue("node_id", "stable_id_mismatch"))
    _common(issues, node, "node_schema_id", STRUCTURAL_NODE_SCHEMA_ID)
    _must_true(issues, node, ("candidate_only",))
    _must_false(
        issues,
        node,
        ("selected", "concept_meaning_created", "predicate_identity_created"),
    )
    _text_tuple(issues, "source_span_ids", node.source_span_ids, allow_empty=False)
    return _report(issues)


def validate_structural_operator_edge(edge: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(edge) is not StructuralOperatorEdge:
        return _report((issue("edge", "invalid_type"),))
    if edge.edge_id != edge.expected_id():
        issues.append(issue("edge_id", "stable_id_mismatch"))
    _common(issues, edge, "edge_schema_id", STRUCTURAL_EDGE_SCHEMA_ID)
    _must_true(issues, edge, ("candidate_only",))
    _must_false(issues, edge, ("selected",))
    if edge.source_node_id == edge.target_node_id:
        issues.append(issue("target_node_id", "self_edge_prohibited"))
    return _report(issues)


def validate_structural_operator_graph(graph: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(graph) is not StructuralOperatorGraph:
        return _report((issue("graph", "invalid_type"),))
    if graph.graph_id != graph.expected_id():
        issues.append(issue("graph_id", "stable_id_mismatch"))
    _common(issues, graph, "graph_schema_id", STRUCTURAL_GRAPH_SCHEMA_ID)
    if graph.node_count != len(graph.nodes):
        issues.append(issue("node_count", "count_mismatch"))
    if graph.edge_count != len(graph.edges):
        issues.append(issue("edge_count", "count_mismatch"))
    if len({item.node_id for item in graph.nodes}) != len(graph.nodes):
        issues.append(issue("nodes", "duplicate_node_id"))
    if len({item.edge_id for item in graph.edges}) != len(graph.edges):
        issues.append(issue("edges", "duplicate_edge_id"))
    node_ids = {item.node_id for item in graph.nodes}
    for index, node in enumerate(graph.nodes):
        report = validate_structural_operator_node(node)
        if node.structural_candidate_id != graph.structural_candidate_id:
            issues.append(issue(f"nodes[{index}].structural_candidate_id", "ancestry_mismatch"))
        for item in report.issues:
            issues.append(issue(f"nodes[{index}].{item.field}", item.code, item.detail))
    for index, edge in enumerate(graph.edges):
        report = validate_structural_operator_edge(edge)
        if edge.structural_candidate_id != graph.structural_candidate_id:
            issues.append(issue(f"edges[{index}].structural_candidate_id", "ancestry_mismatch"))
        if edge.source_node_id not in node_ids or edge.target_node_id not in node_ids:
            issues.append(issue(f"edges[{index}]", "edge_node_missing"))
        for item in report.issues:
            issues.append(issue(f"edges[{index}].{item.field}", item.code, item.detail))
    _must_true(
        issues,
        graph,
        (
            "all_participating_bindings_represented",
            "only_explicit_edges_created",
            "candidate_only",
        ),
    )
    _must_false(issues, graph, ("selected_graph",))
    if tuple(item.candidate_binding_id for item in graph.nodes) != graph.participating_binding_ids:
        issues.append(issue("participating_binding_ids", "node_binding_order_mismatch"))
    return _report(issues)


def validate_structural_source_coverage_proof(proof: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(proof) is not StructuralSourceCoverageProof:
        return _report((issue("proof", "invalid_type"),))
    if proof.coverage_proof_id != proof.expected_id():
        issues.append(issue("coverage_proof_id", "stable_id_mismatch"))
    _common(issues, proof, "coverage_schema_id", STRUCTURAL_COVERAGE_SCHEMA_ID)
    _must_true(
        issues,
        proof,
        (
            "source_reconstruction_proven",
            "reconstruction_hash_matches_custody",
            "exact_source_ancestry",
        ),
    )
    if proof.source_coverage_complete != (not proof.unconsumed_code_point_ranges):
        issues.append(issue("source_coverage_complete", "coverage_flag_mismatch"))
    if len(proof.unconsumed_code_point_ranges) != len(proof.unconsumed_utf8_byte_ranges):
        issues.append(issue("unconsumed_utf8_byte_ranges", "range_count_mismatch"))
    if len(proof.unconsumed_code_point_ranges) != len(proof.unconsumed_exact_fragments):
        issues.append(issue("unconsumed_exact_fragments", "range_count_mismatch"))
    return _report(issues)


def validate_structural_analysis_candidate(candidate: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(candidate) is not StructuralAnalysisCandidate:
        return _report((issue("candidate", "invalid_type"),))
    if candidate.structural_candidate_id != candidate.expected_id():
        issues.append(issue("structural_candidate_id", "stable_id_mismatch"))
    _common(issues, candidate, "candidate_schema_id", STRUCTURAL_CANDIDATE_SCHEMA_ID)
    if candidate.operator_graph.structural_candidate_id != candidate.structural_candidate_id:
        issues.append(issue("operator_graph", "candidate_ancestry_mismatch"))
    if candidate.source_coverage.structural_candidate_id != candidate.structural_candidate_id:
        issues.append(issue("source_coverage", "candidate_ancestry_mismatch"))
    if candidate.phase_trail.phase_trail_id != candidate.phase_trail_id:
        issues.append(issue("phase_trail", "phase_trail_id_mismatch"))
    if candidate.phase_trail.participating_binding_ids != candidate.participating_binding_ids:
        issues.append(issue("participating_binding_ids", "phase_trail_binding_mismatch"))
    graph_report = validate_structural_operator_graph(candidate.operator_graph)
    for item in graph_report.issues:
        issues.append(issue(f"operator_graph.{item.field}", item.code, item.detail))
    coverage_report = validate_structural_source_coverage_proof(candidate.source_coverage)
    for item in coverage_report.issues:
        issues.append(issue(f"source_coverage.{item.field}", item.code, item.detail))
    if tuple(trace.trace_ordinal for trace in candidate.rule_application_traces) != tuple(range(len(candidate.rule_application_traces))):
        issues.append(issue("rule_application_traces", "trace_ordinal_sequence_invalid"))
    for index, trace in enumerate(candidate.rule_application_traces):
        report = validate_structural_rule_application_trace(trace)
        if trace.structural_candidate_id != candidate.structural_candidate_id:
            issues.append(issue(f"rule_application_traces[{index}]", "candidate_ancestry_mismatch"))
        for item in report.issues:
            issues.append(issue(f"rule_application_traces[{index}].{item.field}", item.code, item.detail))
    if candidate.attachment_alternative_ids != tuple(item.governed_span_id for item in candidate.attachment_candidates):
        issues.append(issue("attachment_alternative_ids", "attachment_preservation_mismatch"))
    if candidate.reference_alternative_ids != tuple(item.reference_candidate_id for item in candidate.reference_candidates):
        issues.append(issue("reference_alternative_ids", "reference_preservation_mismatch"))
    _must_true(
        issues,
        candidate,
        (
            "exact_ancestry_complete",
            "source_reconstruction_proven",
            "predecessor_records_preserved",
            "candidate_only",
        ),
    )
    _must_false(
        issues,
        candidate,
        (
            "selected_structure",
            "candidate_meaning_created",
            "selected_meaning",
            "concept_resolved",
            "sense_resolved",
            "predicate_identity_created",
            "participant_roles_assigned",
            "truth_determined",
            "evidence_validity_determined",
            "clarification_question_asked",
            "semantic_rejection_performed",
            "permission_inferred",
            "capability_selected",
            "route_created",
            "tool_routing_performed",
            "memory_read_performed",
            "memory_write_performed",
            "protected_memory_retrieved",
            "action_performed",
            "outward_answer_rendered",
            "delivery_performed",
        ),
    )
    expected_complete = candidate.completeness_status is StructuralCompletenessStatus.COMPLETE_BOUNDED_STRUCTURE
    if candidate.structurally_complete != expected_complete:
        issues.append(issue("structurally_complete", "completeness_status_mismatch"))
    return _report(issues)


def validate_structural_non_progress_result(record: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not StructuralNonProgressResult:
        return _report((issue("non_progress", "invalid_type"),))
    if record.non_progress_id != record.expected_id():
        issues.append(issue("non_progress_id", "stable_id_mismatch"))
    _common(issues, record, "non_progress_schema_id", STRUCTURAL_NON_PROGRESS_SCHEMA_ID)
    if not record.reasons or StructuralNonProgressReason.NONE in record.reasons:
        issues.append(issue("reasons", "active_non_progress_reasons_required"))
    if record.primary_reason != record.reasons[0]:
        issues.append(issue("primary_reason", "primary_reason_order_mismatch"))
    _must_true(issues, record, ("valid_result",))
    _must_false(
        issues,
        record,
        (
            "guessed_to_avoid_non_progress",
            "clarification_question_asked",
            "semantic_rejection_performed",
            "candidate_meaning_created",
            "selected_meaning",
        ),
    )
    return _report(issues)


def validate_structural_analysis_candidate_set(record: object) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(record) is not StructuralAnalysisCandidateSet:
        return _report((issue("structural_set", "invalid_type"),))
    if record.structural_set_id != record.expected_id():
        issues.append(issue("structural_set_id", "stable_id_mismatch"))
    _common(issues, record, "structural_set_schema_id", STRUCTURAL_SET_SCHEMA_ID)
    if record.candidate_count != len(record.candidates):
        issues.append(issue("candidate_count", "count_mismatch"))
    expected_status = (
        StructuralDerivationStatus.ZERO_STRUCTURAL_CANDIDATES
        if record.candidate_count == 0
        else (
            StructuralDerivationStatus.ONE_STRUCTURAL_CANDIDATE
            if record.candidate_count == 1
            else StructuralDerivationStatus.MULTIPLE_STRUCTURAL_CANDIDATES
        )
    )
    if record.status is not expected_status:
        issues.append(issue("status", "candidate_count_status_mismatch"))
    if len({item.structural_candidate_id for item in record.candidates}) != len(record.candidates):
        issues.append(issue("candidates", "duplicate_candidate_id"))
    for index, candidate in enumerate(record.candidates):
        report = validate_structural_analysis_candidate(candidate)
        if candidate.structural_set_id != record.structural_set_id:
            issues.append(issue(f"candidates[{index}].structural_set_id", "set_ancestry_mismatch"))
        for item in report.issues:
            issues.append(issue(f"candidates[{index}].{item.field}", item.code, item.detail))
    expected_counts = {
        "complete_candidate_count": sum(item.structurally_complete for item in record.candidates),
        "ambiguous_candidate_count": sum(item.ambiguous for item in record.candidates),
        "incomplete_candidate_count": sum(item.incomplete for item in record.candidates),
        "malformed_candidate_count": sum(item.malformed for item in record.candidates),
        "unsupported_candidate_count": sum(item.unsupported for item in record.candidates),
        "contained_drift_candidate_count": sum(item.contained_drift for item in record.candidates),
        "suspended_recursion_candidate_count": sum(item.suspended_recursion for item in record.candidates),
    }
    for name, expected in expected_counts.items():
        if getattr(record, name) != expected:
            issues.append(issue(name, "count_mismatch"))
    if record.non_progress_result is not None:
        report = validate_structural_non_progress_result(record.non_progress_result)
        if record.non_progress_result.structural_set_id != record.structural_set_id:
            issues.append(issue("non_progress_result", "set_ancestry_mismatch"))
        for item in report.issues:
            issues.append(issue(f"non_progress_result.{item.field}", item.code, item.detail))
    elif record.aggregate_non_progress_reasons != (StructuralNonProgressReason.NONE,):
        issues.append(issue("non_progress_result", "required_for_active_non_progress"))
    _must_true(
        issues,
        record,
        (
            "all_source_ancestry_preserved",
            "all_source_reconstruction_proven",
            "all_phase_trails_preserved",
            "all_scope_occurrences_preserved",
            "all_attachment_candidates_preserved",
            "all_reference_candidates_preserved",
            "structural_candidate_plurality_preserved",
        ),
    )
    _must_false(
        issues,
        record,
        (
            "candidate_meaning_created",
            "selected_meaning",
            "clarification_question_asked",
            "semantic_rejection_performed",
            "hidden_fallback_allowed",
        ),
    )
    if record.selected_structural_candidate_id is not None:
        issues.append(issue("selected_structural_candidate_id", "selection_prohibited"))
    return _report(issues)


def validate_deterministic_structural_derivation_result(
    result: object,
    custody_result: object | None = None,
    projection_result: object | None = None,
    binding_result: object | None = None,
    phase_trail_result: object | None = None,
    constraint_result: object | None = None,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if type(result) is not DeterministicStructuralDerivationResult:
        return _report((issue("result", "invalid_type"),))
    if result.result_id != result.expected_id():
        issues.append(issue("result_id", "stable_id_mismatch"))
    _common(issues, result, "result_schema_id", STRUCTURAL_RESULT_SCHEMA_ID)
    if result.policy is not None:
        for item in validate_structural_derivation_policy(result.policy).issues:
            issues.append(issue(f"policy.{item.field}", item.code, item.detail))
    if result.limits is not None:
        for item in validate_structural_derivation_limits(result.limits).issues:
            issues.append(issue(f"limits.{item.field}", item.code, item.detail))
    if result.structural_set is not None:
        report = validate_structural_analysis_candidate_set(result.structural_set)
        for item in report.issues:
            issues.append(issue(f"structural_set.{item.field}", item.code, item.detail))
        if result.status is not result.structural_set.status:
            issues.append(issue("status", "structural_set_status_mismatch"))
        if not result.structural_set_created:
            issues.append(issue("structural_set_created", "must_be_true_with_set"))
        if result.explicit_non_progress_created != bool(result.structural_set.non_progress_result):
            issues.append(issue("explicit_non_progress_created", "non_progress_flag_mismatch"))
    elif result.structural_set_created:
        issues.append(issue("structural_set_created", "set_missing"))
    _must_false(
        issues,
        result,
        (
            "filesystem_read_performed",
            "filesystem_write_performed",
            "repository_history_search_performed",
            "network_access_performed",
            "environment_access_performed",
            "memory_read_performed",
            "memory_write_performed",
            "protected_memory_retrieval_performed",
            "web_search_performed",
            "embedding_performed",
            "language_model_used",
            "similarity_search_performed",
            "candidate_meaning_created",
            "selected_meaning",
            "intended_meaning_selected",
            "concept_resolved",
            "sense_resolved",
            "predicate_identity_created",
            "participant_roles_assigned",
            "truth_determined",
            "evidence_validity_determined",
            "clarification_question_asked",
            "semantic_rejection_performed",
            "permission_inferred",
            "capability_selected",
            "route_registration_performed",
            "tool_routing_performed",
            "action_performed",
            "outward_answer_rendered",
            "delivery_performed",
        ),
    )
    if result.structural_set is not None:
        if custody_result is not None and result.structural_set.custody_result_id != getattr(custody_result, "result_id", None):
            issues.append(issue("structural_set.custody_result_id", "predecessor_mismatch"))
        if projection_result is not None and result.structural_set.projection_result_id != getattr(projection_result, "result_id", None):
            issues.append(issue("structural_set.projection_result_id", "predecessor_mismatch"))
        if binding_result is not None and result.structural_set.binding_result_id != getattr(binding_result, "result_id", None):
            issues.append(issue("structural_set.binding_result_id", "predecessor_mismatch"))
        if phase_trail_result is not None and result.structural_set.phase_trail_result_id != getattr(phase_trail_result, "result_id", None):
            issues.append(issue("structural_set.phase_trail_result_id", "predecessor_mismatch"))
        if constraint_result is not None and result.structural_set.constraint_result_id != getattr(constraint_result, "result_id", None):
            issues.append(issue("structural_set.constraint_result_id", "predecessor_mismatch"))
    return _report(issues)
