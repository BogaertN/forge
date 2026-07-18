"""Explicit fixture-only Slice 39H bootstrap integration and closeout."""
from __future__ import annotations
from dataclasses import replace
from typing import Final

from ..boundary import build_bootstrap_boundary_bundle
from ..authority import validate_bootstrap_authority_state
from ..boundary import validate_bootstrap_boundary_record
from ..component_registry import validate_component_registry_record
from ..import_policy import validate_import_policy_record
from ..input_event_custody import capture_input_event, validate_input_event_capture_result
from ..source_field_projection import project_source_field, validate_source_field_projection_result
from ..resonant_operator_candidate_binding import bind_resonant_operator_candidates, validate_resonant_operator_candidate_binding_result
from ..symbolic_grammar_operator_registry import build_default_symbolic_grammar_operator_registry, validate_symbolic_grammar_operator_registry
from ..candidate_resonant_phase_trail import construct_candidate_resonant_phase_trails, validate_candidate_resonant_phase_trail_result
from ..scope_attachment_reference_constraints import apply_scope_attachment_reference_constraints, validate_scope_attachment_reference_constraint_result
from ..deterministic_structural_derivation import derive_deterministic_structural_analysis, validate_deterministic_structural_derivation_result
from ..structural_concept_candidate_proposal import propose_structural_concept_candidates, validate_proposal_result
from ..predicate_role_frame_registry.predicate_role_frame_candidate_proposal import (
    CandidateProposalStatus, build_compatibility_conflict, build_compatibility_snapshot,
    build_exact_compatibility_rule, propose_predicate_role_frame_candidates,
    validate_compatibility_snapshot, validate_result as validate_slice38_result,
)
from ..candidate_meaning_construction.deterministic_constructor import (
    CandidateMeaningConstructorInput, CandidateMeaningConstructorStatus,
    construct_candidate_meanings, validate_result as validate_constructor_result,
)
from ..candidate_meaning_construction.manifest_candidate_integration import (
    ManifestCandidateIntegrationStatus, integrate_candidate_meanings_into_manifest,
    validate_integration_result as validate_manifest_integration_result,
)
from ..schema import stable_record_id
from .fixtures import get_disabled_candidate_meaning_fixture, is_exact_accepted_fixture
from .schema import (
    PRE_SLICE39_COMMIT, PRE_SLICE39_TREE, SLICE39G_ACCEPTED_HEAD,
    SLICE39G_ACCEPTED_TREE, SLICE39G_ACCEPTED_SUBJECT, SLICE39H_COMMIT_SUBJECT,
    SLICE39_INCREMENT_LABELS, SLICE39_ACCEPTED_CHAIN, SLICE39_PERMANENT_BOUNDARIES,
    SLICE39_PROHIBITED_AUTHORITY, SLICE39_ACCEPTED_SCOPE, SLICE39_DEFERRED_SCOPE,
    CloseoutStage, CloseoutStageReceipt, CloseoutStatus,
    DisabledCandidateMeaningBootstrapResult, DisabledCandidateMeaningBootstrapState,
    DisabledCandidateMeaningInvocation, FixtureScenario, Slice39AcceptanceRecord,
    Slice39RollbackMetadata,
)

REQUESTED_OPERATION: Final[str] = "run_exact_slice39_candidate_fixture_chain"
REASON_DISABLED: Final[str] = "slice39h_disabled_by_default_explicit_offline_enable_required"
_STATE_NOT_PROVIDED: Final[object] = object()

def _with_id(record: object, field: str): return replace(record, **{field: record.expected_id()})

def build_disabled_candidate_meaning_bootstrap_state(*, explicit_offline_developer_enable: bool = False) -> DisabledCandidateMeaningBootstrapState:
    enabled = explicit_offline_developer_enable is True
    draft = DisabledCandidateMeaningBootstrapState(
        state_id="", enabled=enabled, explicit_offline_developer_enable=enabled,
        disabled_by_default=True, explicit_invocation_required=True,
        accepted_static_fixture_only=True, offline_only=True, standard_library_only=True,
        deterministic=True, read_only=True, in_memory_only=True, exact_profile_bounded=True,
        source_preserving=True, rollback_safe=True, automatic_activation_allowed=False,
        arbitrary_raw_text_allowed=False, filesystem_read_allowed=False,
        filesystem_write_allowed=False, network_allowed=False,
        external_resource_loading_allowed=False, model_authority_allowed=False,
        embedding_authority_allowed=False, vector_authority_allowed=False,
        rag_authority_allowed=False, semantic_similarity_allowed=False,
        nearest_known_substitution_allowed=False, hidden_intent_inference_allowed=False,
        silent_role_filling_allowed=False, silent_referent_resolution_allowed=False,
        automatic_ambiguity_collapse_allowed=False, gate_outcome_allowed=False,
        selected_meaning_allowed=False, truth_determination_allowed=False,
        evidence_validation_allowed=False, permission_allowed=False,
        capability_availability_allowed=False, route_allowed=False, invocation_allowed=False,
        memory_access_allowed=False, tool_allowed=False, action_allowed=False,
        rendering_allowed=False, delivery_allowed=False, runtime_self_acceptance_allowed=False,
        release_authorized=False, production_ready=False,
    )
    return _with_id(draft, "state_id")

def build_slice39_rollback_metadata() -> Slice39RollbackMetadata:
    draft = Slice39RollbackMetadata(
        rollback_id="", pre_slice39_commit=PRE_SLICE39_COMMIT,
        pre_slice39_tree=PRE_SLICE39_TREE, accepted_parent_head=SLICE39G_ACCEPTED_HEAD,
        accepted_parent_tree=SLICE39G_ACCEPTED_TREE,
        accepted_parent_subject=SLICE39G_ACCEPTED_SUBJECT,
        expected_closeout_commit_subject=SLICE39H_COMMIT_SUBJECT,
        exact_commit_checkout_required=True, exact_tree_match_required=True,
        separate_recovery_clone_required=True, exact_staged_path_containment_required=True,
        git_object_verification_required=True, live_repository_mutation_authorized=False,
        runtime_rollback_execution_authorized=False, rollback_proof_external_to_runtime=True,
    )
    return _with_id(draft, "rollback_id")

def build_slice39_acceptance_record(rollback_metadata: Slice39RollbackMetadata | None = None) -> Slice39AcceptanceRecord:
    rollback = rollback_metadata or build_slice39_rollback_metadata()
    draft = Slice39AcceptanceRecord(
        acceptance_record_id="", decision_owner="Nicholas Jacob Bogaert / AI.Web",
        accepted_increment_labels=SLICE39_INCREMENT_LABELS, accepted_chain=SLICE39_ACCEPTED_CHAIN,
        permanent_boundaries=SLICE39_PERMANENT_BOUNDARIES,
        prohibited_authority=SLICE39_PROHIBITED_AUTHORITY,
        accepted_scope=SLICE39_ACCEPTED_SCOPE, deferred_scope=SLICE39_DEFERRED_SCOPE,
        rollback_metadata_id=rollback.rollback_id, accepted_parent_head=SLICE39G_ACCEPTED_HEAD,
        accepted_parent_tree=SLICE39G_ACCEPTED_TREE, pre_slice39_commit=PRE_SLICE39_COMMIT,
        pre_slice39_tree=PRE_SLICE39_TREE, disabled_by_default=True,
        explicitly_invoked_only=True, fixture_only=True, offline_only=True,
        deterministic=True, read_only=True, in_memory_only=True, exact_profile_bounded=True,
        source_preserving=True, zero_candidate_reproducibility_required=True,
        one_candidate_reproducibility_required=True, multi_candidate_reproducibility_required=True,
        missing_role_preservation_required=True, unknown_concept_preservation_required=True,
        unknown_predicate_preservation_required=True, conflicting_role_preservation_required=True,
        exact_staged_path_containment_required=True, pre_slice39_recovery_required=True,
        no_selected_meaning_authority=True, no_gate_outcome_authority=True,
        no_permission_or_execution_authority=True, runtime_self_grants_acceptance=False,
        decision_owner_acceptance_required=True, release_authorized=False, production_ready=False,
    )
    return _with_id(draft, "acceptance_record_id")

def build_fixture_invocation(fixture_name: str) -> DisabledCandidateMeaningInvocation | None:
    fixture = get_disabled_candidate_meaning_fixture(fixture_name)
    if fixture is None: return None
    draft = DisabledCandidateMeaningInvocation(
        invocation_id="", fixture_name=fixture.fixture_name, fixture_id=fixture.fixture_id,
        explicit_invocation=True, requested_operation=REQUESTED_OPERATION,
        raw_text_carried_by_invocation=False,
    )
    return _with_id(draft, "invocation_id")

def _receipt(*, state, invocation, fixture_id, ordinal, stage, predecessors, output_id, output_schema_version, output_type, source_event_id, source_sha256):
    draft = CloseoutStageReceipt(
        receipt_id="", state_id=state.state_id, invocation_id=invocation.invocation_id,
        fixture_id=fixture_id, stage_ordinal=ordinal, stage=stage,
        predecessor_record_ids=tuple(predecessors), output_record_id=output_id,
        output_schema_version=output_schema_version, output_exact_type=output_type,
        output_validation_passed=True, source_event_id=source_event_id,
        source_sha256=source_sha256, source_preserved=True, candidate_only=True,
        gate_outcome_created=False, selected_meaning_created=False, truth_determined=False,
        evidence_validated=False, permission_granted=False, route_created=False,
        invocation_created=False, memory_accessed=False, tool_invoked=False,
        action_performed=False, rendered=False, delivered=False,
    )
    return _with_id(draft, "receipt_id")

def _result(*, state, invocation=None, fixture_id="", status, reason_code, receipts=(), source_event_id="", source_sha256="", constructor_result=None, manifest_result=None, zero=False, one=False, multi=False, missing=False, unknown_concept=False, unknown_predicate=False, conflict=False):
    rollback = build_slice39_rollback_metadata(); acceptance = build_slice39_acceptance_record(rollback)
    unique = constructor_result.unique_candidate_count if constructor_result is not None else 0
    manifest_count = manifest_result.manifest_candidate_count if manifest_result is not None else 0
    draft = DisabledCandidateMeaningBootstrapResult(
        result_id="", state_id=state.state_id,
        invocation_id=invocation.invocation_id if type(invocation) is DisabledCandidateMeaningInvocation else "",
        fixture_id=fixture_id, status=status, reason_code=reason_code,
        stage_receipts=tuple(receipts), stage_receipt_count=len(receipts),
        exact_stage_chain_complete=len(receipts) == 4, source_event_id=source_event_id,
        source_sha256=source_sha256, constructor_result=constructor_result,
        manifest_integration_result=manifest_result, acceptance_record=acceptance,
        rollback_metadata=rollback, unique_candidate_count=unique,
        manifest_candidate_count=manifest_count, zero_candidate_reproduced=zero,
        one_candidate_reproduced=one, multi_candidate_reproduced=multi,
        missing_role_preserved=missing, unknown_concept_preserved=unknown_concept,
        unknown_predicate_preserved=unknown_predicate, conflicting_role_preserved=conflict,
        disabled_by_default=True,
        explicitly_invoked=type(invocation) is DisabledCandidateMeaningInvocation and invocation.explicit_invocation,
        fixture_only=True, offline_only=True, standard_library_only=True,
        deterministic=True, read_only=True, in_memory_only=True, exact_profile_bounded=True,
        source_preserved=bool(source_event_id and source_sha256) if receipts else False,
        rollback_safe=True, gate_outcome_created=False, selected_meaning_created=False,
        truth_determined=False, evidence_validated=False, permission_granted=False,
        capability_availability_created=False, route_created=False, invocation_created=False,
        memory_accessed=False, tool_invoked=False, action_performed=False, rendered=False,
        delivered=False, filesystem_read_performed=False, filesystem_write_performed=False,
        network_access_performed=False, external_resource_loaded=False,
        language_model_used=False, model_authority_used=False, embedding_used=False,
        vector_used=False, rag_used=False, semantic_similarity_used=False,
        nearest_known_substitution_used=False, hidden_intent_inference_used=False,
        silent_role_filling_used=False, silent_referent_resolution_used=False,
        automatic_ambiguity_collapse_used=False, technical_acceptance_granted_by_runtime=False,
        release_authorized=False, production_ready=False,
    )
    return _with_id(draft, "result_id")

def _pipeline(fixture):
    custody = capture_input_event(
        fixture.exact_source_text,
        source_id=fixture.source_id,
        channel_id=fixture.channel_id,
        sequence_number=fixture.sequence_number,
    )
    if custody.event is None or not validate_input_event_capture_result(custody).ok:
        raise ValueError("invalid custody")

    projection = project_source_field(custody.event)
    if not validate_source_field_projection_result(projection).ok:
        raise ValueError("invalid projection")

    registry = build_default_symbolic_grammar_operator_registry()
    if not validate_symbolic_grammar_operator_registry(registry).ok:
        raise ValueError("invalid operator registry")

    binding = bind_resonant_operator_candidates(
        projection,
        registry=registry,
    )
    if not validate_resonant_operator_candidate_binding_result(
        binding,
        projection,
        registry,
    ).ok:
        raise ValueError("invalid binding")

    trails = construct_candidate_resonant_phase_trails(
        projection,
        binding,
        registry=registry,
    )
    if not validate_candidate_resonant_phase_trail_result(
        trails,
        projection,
        binding,
        registry,
    ).ok:
        raise ValueError("invalid trails")

    constraints = apply_scope_attachment_reference_constraints(
        projection,
        binding,
        trails,
    )
    if not validate_scope_attachment_reference_constraint_result(
        constraints,
        projection,
        binding,
        trails,
    ).ok:
        raise ValueError("invalid constraints")

    structural = derive_deterministic_structural_analysis(
        custody,
        projection,
        binding,
        trails,
        constraints,
    )
    if not validate_deterministic_structural_derivation_result(
        structural,
        custody,
        projection,
        binding,
        trails,
        constraints,
    ).ok:
        raise ValueError("invalid structural")

    slice37 = propose_structural_concept_candidates(
        custody,
        projection,
        structural,
    )
    if not validate_proposal_result(slice37).ok:
        raise ValueError("invalid slice37")

    return custody, projection, binding, trails, constraints, structural, slice37

def _rule(slice37, root: str, key: str):
    concept = slice37.concept_candidates[0]; sense = slice37.sense_candidates[0]
    frame = {"inspect": "inspect_read_only", "report": "report_attributed_content"}[root]
    return build_exact_compatibility_rule(rule_key=key, action_root_key=root, concept_id=concept.concept_id, sense_id=sense.sense_id, allowed_frame_keys=(frame,))

def _input(chain, slice38):
    return CandidateMeaningConstructorInput(custody=chain[0], projection=chain[1], binding=chain[2], trails=chain[3], constraints=chain[4], structural=chain[5], slice37=chain[6], slice38=slice38)

def _slice38_inputs(chain, fixture):
    slice37 = chain[6]
    key = fixture.fixture_name
    if fixture.scenario in (FixtureScenario.ZERO_UNKNOWN_PREDICATE, FixtureScenario.UNKNOWN_CONCEPT):
        snapshot = build_compatibility_snapshot(registry_key=f"{key}.empty")
        if not validate_compatibility_snapshot(snapshot).ok: raise ValueError("invalid empty snapshot")
        result = propose_predicate_role_frame_candidates(slice37, compatibility_snapshot=snapshot)
        return (result,), (_input(chain, result),)
    inspect = _rule(slice37, "inspect", f"{key}.inspect")
    inspect_snapshot = build_compatibility_snapshot(rules=(inspect,), registry_key=f"{key}.inspect")
    inspect_result = propose_predicate_role_frame_candidates(slice37, compatibility_snapshot=inspect_snapshot)
    if fixture.scenario is FixtureScenario.ONE_MISSING_ROLE:
        return (inspect_result,), (_input(chain, inspect_result),)
    report = _rule(slice37, "report", f"{key}.report")
    if fixture.scenario is FixtureScenario.MULTI_CANDIDATE:
        report_snapshot = build_compatibility_snapshot(rules=(report,), registry_key=f"{key}.report")
        report_result = propose_predicate_role_frame_candidates(slice37, compatibility_snapshot=report_snapshot)
        return (inspect_result, report_result), (_input(chain, report_result), _input(chain, inspect_result))
    conflict = build_compatibility_conflict(conflict_key=f"{key}.conflict", rules=(inspect, report), conflict_kind="exact_identity_competing_role_layouts", reason="preserve competing exact role-layout candidates without assignment or selection")
    snapshot = build_compatibility_snapshot(rules=(inspect, report), conflicts=(conflict,), registry_key=f"{key}.conflicted")
    result = propose_predicate_role_frame_candidates(slice37, compatibility_snapshot=snapshot)
    return (result,), (_input(chain, result),)

def run_disabled_candidate_meaning_bootstrap(invocation: object = None, *, integration_state: object = _STATE_NOT_PROVIDED) -> DisabledCandidateMeaningBootstrapResult:
    from .validation import validate_fixture, validate_integration_result, validate_integration_state, validate_invocation
    default_state = build_disabled_candidate_meaning_bootstrap_state()
    state = default_state if integration_state is _STATE_NOT_PROVIDED else integration_state
    if not validate_integration_state(state).ok:
        safe = state if type(state) is DisabledCandidateMeaningBootstrapState else default_state
        return _result(state=safe, invocation=invocation, status=CloseoutStatus.HELD_INVALID_STATE, reason_code="exact_slice39h_state_required")
    if not state.enabled:
        return _result(state=state, invocation=invocation, status=CloseoutStatus.REFUSED_DISABLED, reason_code=REASON_DISABLED)
    if not validate_invocation(invocation).ok:
        return _result(state=state, invocation=invocation, status=CloseoutStatus.HELD_INVALID_INVOCATION, reason_code="exact_slice39h_fixture_invocation_required")
    fixture = get_disabled_candidate_meaning_fixture(invocation.fixture_name)
    if fixture is None or fixture.fixture_id != invocation.fixture_id or not is_exact_accepted_fixture(fixture) or not validate_fixture(fixture).ok:
        return _result(state=state, invocation=invocation, fixture_id=getattr(fixture, "fixture_id", ""), status=CloseoutStatus.HELD_FIXTURE_NOT_ACCEPTED, reason_code="exact_static_slice39h_fixture_required")
    try:
        bundle = build_bootstrap_boundary_bundle()
        boundary_ok = all((validate_bootstrap_authority_state(bundle.authority).ok, validate_component_registry_record(bundle.registry).ok, validate_import_policy_record(bundle.import_policy).ok, validate_bootstrap_boundary_record(
            bundle.boundary,
            authority=bundle.authority,
            registry=bundle.registry,
            import_policy=bundle.import_policy,
        ).ok))
        if not boundary_ok or bundle.authority.enabled or bundle.authority.runtime_connected or bundle.boundary.runtime_effect != "none":
            return _result(state=state, invocation=invocation, fixture_id=fixture.fixture_id, status=CloseoutStatus.HELD_INVALID_BOOTSTRAP_BOUNDARY, reason_code="isolated_disabled_bootstrap_boundary_required")
        chain = _pipeline(fixture)
        source_event_id = chain[0].event.input_event_id; source_sha256 = chain[0].event.source_sha256
        receipt1 = _receipt(state=state, invocation=invocation, fixture_id=fixture.fixture_id, ordinal=1, stage=CloseoutStage.ISOLATED_BOOTSTRAP_BOUNDARY, predecessors=(invocation.invocation_id,), output_id=bundle.boundary.bootstrap_boundary_id, output_schema_version=bundle.boundary.schema_version, output_type=type(bundle.boundary).__name__, source_event_id=source_event_id, source_sha256=source_sha256)
        slice38_results, constructor_inputs = _slice38_inputs(chain, fixture)
        if not all(validate_slice38_result(item).ok for item in slice38_results): raise ValueError("invalid slice38")
        predecessor_output_id = stable_record_id("slice39h_typed_predecessor_set", tuple(item.result_id for item in slice38_results))
        receipt2 = _receipt(state=state, invocation=invocation, fixture_id=fixture.fixture_id, ordinal=2, stage=CloseoutStage.ACCEPTED_TYPED_PREDECESSORS, predecessors=(receipt1.output_record_id,), output_id=predecessor_output_id, output_schema_version=slice38_results[0].schema_version, output_type="tuple[PredicateRoleFrameCandidateProposalResult]", source_event_id=source_event_id, source_sha256=source_sha256)
        constructor = construct_candidate_meanings(tuple(constructor_inputs))
        if not validate_constructor_result(constructor).ok or constructor.status is CandidateMeaningConstructorStatus.REJECTED: raise ValueError("invalid constructor")
        receipt3 = _receipt(state=state, invocation=invocation, fixture_id=fixture.fixture_id, ordinal=3, stage=CloseoutStage.CANDIDATE_CONSTRUCTION, predecessors=(predecessor_output_id,), output_id=constructor.result_id, output_schema_version=constructor.schema_version, output_type=type(constructor).__name__, source_event_id=source_event_id, source_sha256=source_sha256)
        manifest = integrate_candidate_meanings_into_manifest(constructor)
        if not validate_manifest_integration_result(manifest).ok or manifest.status is ManifestCandidateIntegrationStatus.REJECTED: raise ValueError("invalid manifest integration")
        receipt4 = _receipt(state=state, invocation=invocation, fixture_id=fixture.fixture_id, ordinal=4, stage=CloseoutStage.MANIFEST_CANDIDATE_INTEGRATION, predecessors=(constructor.result_id,), output_id=manifest.result_id, output_schema_version=manifest.schema_version, output_type=type(manifest).__name__, source_event_id=source_event_id, source_sha256=source_sha256)
        missing_count = sum(len(item.missing_role_refs) for item in manifest.limitation_references)
        conflict_preserved = fixture.scenario is FixtureScenario.CONFLICTING_ROLE and any(getattr(getattr(item, "structural_state", None), "value", None) == "conflicted" for result in slice38_results for item in result.action_predicate_candidates)
        unknown_concept = fixture.scenario is FixtureScenario.UNKNOWN_CONCEPT and chain[6].explicit_unknown_count > 0 and slice38_results[0].status is CandidateProposalStatus.EXPLICIT_UNKNOWN
        unknown_predicate = fixture.scenario is FixtureScenario.ZERO_UNKNOWN_PREDICATE and slice38_results[0].status is CandidateProposalStatus.EXPLICIT_UNSUPPORTED
        expectations = (constructor.status.value == fixture.expected_constructor_status and manifest.status.value == fixture.expected_manifest_status and constructor.unique_candidate_count == fixture.expected_unique_candidate_count and manifest.manifest_candidate_count == fixture.expected_manifest_candidate_count and missing_count >= fixture.expected_missing_role_minimum)
        if not expectations:
            return _result(state=state, invocation=invocation, fixture_id=fixture.fixture_id, status=CloseoutStatus.HELD_EXPECTATION_MISMATCH, reason_code="exact_fixture_expectation_mismatch", receipts=(receipt1, receipt2, receipt3, receipt4), source_event_id=source_event_id, source_sha256=source_sha256, constructor_result=constructor, manifest_result=manifest)
        status = {FixtureScenario.ZERO_UNKNOWN_PREDICATE: CloseoutStatus.COMPLETED_ZERO_CANDIDATES, FixtureScenario.ONE_MISSING_ROLE: CloseoutStatus.COMPLETED_ONE_CANDIDATE, FixtureScenario.MULTI_CANDIDATE: CloseoutStatus.COMPLETED_MULTIPLE_CANDIDATES, FixtureScenario.UNKNOWN_CONCEPT: CloseoutStatus.COMPLETED_ZERO_CANDIDATES, FixtureScenario.CONFLICTING_ROLE: CloseoutStatus.COMPLETED_CONFLICT_PRESERVED}[fixture.scenario]
        result = _result(state=state, invocation=invocation, fixture_id=fixture.fixture_id, status=status, reason_code="exact_slice39_fixture_chain_completed", receipts=(receipt1, receipt2, receipt3, receipt4), source_event_id=source_event_id, source_sha256=source_sha256, constructor_result=constructor, manifest_result=manifest, zero=fixture.scenario in (FixtureScenario.ZERO_UNKNOWN_PREDICATE, FixtureScenario.UNKNOWN_CONCEPT), one=fixture.scenario in (FixtureScenario.ONE_MISSING_ROLE, FixtureScenario.CONFLICTING_ROLE), multi=fixture.scenario is FixtureScenario.MULTI_CANDIDATE, missing=missing_count >= fixture.expected_missing_role_minimum and fixture.expected_missing_role_minimum > 0, unknown_concept=unknown_concept, unknown_predicate=unknown_predicate, conflict=conflict_preserved)
        if not validate_integration_result(result).ok: raise ValueError("self validation")
        return result
    except ValueError:
        return _result(state=state, invocation=invocation, fixture_id=fixture.fixture_id, status=CloseoutStatus.HELD_INVALID_PREDECESSOR_OUTPUT, reason_code="slice39h_typed_predecessor_or_integration_output_invalid")

__all__ = (
    "REQUESTED_OPERATION", "REASON_DISABLED", "build_disabled_candidate_meaning_bootstrap_state",
    "build_fixture_invocation", "build_slice39_acceptance_record", "build_slice39_rollback_metadata",
    "run_disabled_candidate_meaning_bootstrap",
)
