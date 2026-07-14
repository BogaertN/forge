"""Static interface contracts and direct imports for Slice 32.

There is no importlib use, plugin discovery, package scanning, entry-point
lookup, environment-selected backend, or hidden fallback. Every accepted
component package is named directly in source code.
"""

from __future__ import annotations

import hashlib

from ..component_registry import ComponentRegistryRecord, validate_component_registry_record
from .schema import (
    ComponentInterfaceContract,
    build_component_interface_contract,
    validate_component_interface_contract,
)

_INTERFACE_SPECS = (
    ('Slice 7', 'aiweb_meaning_law_trace_scaffold', 'c8ca2f959815d9d4f4b947b635dcd499ce54f30562d204f99aa86e8384568e38', 4, 'Meaning-object and law-trace record boundary; no truth or runtime authority.', ('MeaningObject', 'build_meaning_object', 'meaning_object_scope_record', 'LawTrace', 'LawTraceStep', 'build_law_trace', 'build_law_trace_step', 'law_trace_scope_record'), 'c7f1e619b4489f5e34be24a8ffba312e64729dc05cc21bdd8c5b717359cc8d4f'),
    ('Slice 8', 'aiweb_concept_boundary_scaffold', '28843077cf64aeb7f6f455eb6cec313f35ab5004c803ed03a02824f43357de01', 4, 'Concept and relation boundary; concepts are not evidence or selected meaning.', ('ConceptBoundaryRecord', 'SenseBoundaryRecord', 'SemanticRelationBoundaryRecord', 'ValidationIssue', 'ValidationReport', 'concept_scope_record', 'relation_scope_record', 'stable_boundary_id', 'validate_concept_record', 'validate_sense_record', 'validate_relation_record'), '0e04b97ff1cb856290c9d7df683c4f8e2b0865f962049b45481690b77346e3f6'),
    ('Slice 9', 'aiweb_predicate_role_boundary_scaffold', '88feda8338f8b7927ad041886fe1ca99bd211fdc7ea261faf69b2b5333e8faf3', 6, 'Predicate, role, speech-act and effect boundary; frames are not execution.', ('DEPENDENCY_CHANGE', 'RUNTIME_EFFECT', 'SCHEMA_VERSION', 'SCOPE_STATUS', 'EffectBoundaryRecord', 'PredicateFrameBoundaryRecord', 'RoleBoundaryRecord', 'SpeechActBoundaryRecord', 'ValidationIssue', 'ValidationReport', 'demo_command_speech_act_record', 'demo_effect_boundary_record', 'demo_implementation_request_speech_act_record', 'demo_memory_request_speech_act_record', 'demo_missing_role_record', 'demo_predicate_frame_record', 'demo_role_record', 'demo_speech_act_record', 'demo_unknown_effect_boundary_record', 'demo_unknown_predicate_frame_record', 'demo_unknown_role_record', 'predicate_role_scope_record', 'stable_boundary_id', 'validate_effect_boundary_record', 'validate_predicate_frame_record', 'validate_role_record', 'validate_speech_act_record'), 'f12e338dccc631f0845b9cd5ad7fac7a2b79f53efeb321cf276492f0f5196d94'),
    ('Slice 10', 'aiweb_verbal_cognition_gate_boundary_scaffold', '308385c90974885c5b13b2422f7df1d9253db35717bef80a1e4cd3e9b10b51f5', 6, 'Gate-state record boundary; gate output is not routing or action.', ('SCHEMA_VERSION', 'SCOPE_STATUS', 'ValidationIssue', 'ValidationReport', 'GateBoundaryRecord', 'GateOutcomeBoundaryRecord', 'ExpectancyBoundaryRecord', 'GateStateBoundaryRecord', 'stable_boundary_id', 'verbal_cognition_gate_scope_record', 'validate_gate_boundary_record', 'validate_gate_outcome_record', 'validate_expectancy_record', 'validate_gate_state_record', 'demo_gate_boundary_record', 'demo_unknown_gate_boundary_record', 'demo_gate_outcome_record', 'demo_clarification_required_outcome_record', 'demo_blocked_action_outcome_record', 'demo_unknown_gate_outcome_record', 'demo_expectancy_record', 'demo_congruity_record', 'demo_connectedness_record', 'demo_recoverable_purpose_record', 'demo_unknown_expectancy_record', 'demo_ambiguity_state_record', 'demo_clarification_required_state_record', 'demo_unsupported_state_record', 'demo_blocked_action_state_record', 'demo_deferred_state_record'), 'd8e8c9710852d266fcc8e588ef7f7f88c526ee43634d618cc1c00aec8adb9f82'),
    ('Slice 11', 'aiweb_candidate_meaning_boundary_scaffold', '3eda1f92198049b1c71ab59878a79587995d29e8508ca5f8780aabaa6dcb7656', 7, 'Source custody and candidate-meaning boundary; candidate is not selected meaning.', ('CandidateMeaningBoundaryRecord', 'candidate_meaning_scope_record', 'demo_candidate_meaning_record', 'demo_no_action_candidate_record', 'demo_unsupported_candidate_record', 'validate_candidate_meaning_record', 'SourceExpressionCustodyRecord', 'build_source_expression_custody_record', 'demo_source_expression_custody_record', 'validate_source_expression_custody_record', 'DerivedStructureCustodyRecord', 'demo_derived_structure_custody_record', 'validate_derived_structure_custody_record', 'MissingSupportBoundaryRecord', 'demo_missing_support_boundary_record', 'demo_no_missing_support_boundary_record', 'validate_missing_support_boundary_record', 'CandidateCompetitionSetBoundaryRecord', 'demo_candidate_competition_set_record', 'validate_candidate_competition_set_record'), '6ae2df08826c6ebc40fbbbf7660fc8c34f14659c510f7ad3c7ff68a20542f9e4'),
    ('Slice 12', 'aiweb_ambiguity_clarification_boundary_scaffold', '290936f9ffeba047d06a61e32135f580505e6937597cd052dde6ee03d2b29b1f', 6, 'Ambiguity, unknown, unsupported, deferred and clarification states.', ('AmbiguityStateBoundaryRecord', 'ClarificationRequirementBoundaryRecord', 'UnknownSupportBoundaryRecord', 'StateTraceBoundaryRecord', 'ambiguity_clarification_scope_record', 'build_state_boundary_record', 'build_clarification_requirement_record', 'build_unknown_support_record', 'build_state_trace_record', 'demo_ambiguity_state_record', 'demo_deferred_state_record', 'demo_unknown_state_record', 'demo_unsupported_state_record', 'demo_clarification_blocked_record', 'demo_clarification_required_record', 'demo_unknown_concept_record', 'demo_unsupported_resource_record', 'demo_state_trace_record', 'validate_state_boundary_record', 'validate_clarification_requirement_record', 'validate_unknown_support_record', 'validate_state_trace_record', 'run_verification'), '15f2bb3e69f6e478ac203154e566e402daf7b69f46af2f3cd4d422e37e878e90'),
    ('Slice 13', 'aiweb_requirements_traceability_scaffold', '0c7872dc5456b807af37fb64260f99d76a94ad4e003be952dc562309f0b8ded9', 7, 'Requirement-to-test traceability records only.', ('AcceptedScopeRecord', 'RollbackTriggerRecord', 'TraceabilityReceiptRecord', 'RequirementIdentityRecord', 'RequirementTestCrosswalkRecord', 'build_accepted_scope_record', 'build_rollback_trigger_record', 'build_traceability_receipt_record', 'build_requirement_identity_record', 'build_requirement_test_crosswalk_record', 'demo_accepted_scope_record', 'demo_rollback_trigger_record', 'demo_traceability_receipt_record', 'demo_requirement_identity_record', 'demo_requirement_test_crosswalk_record', 'requirements_traceability_scope_record', 'validate_accepted_scope_record', 'validate_rollback_trigger_record', 'validate_traceability_receipt_record', 'validate_requirement_identity_record', 'validate_requirement_test_crosswalk_record'), '6279fda5c585c6a8bf323e78c5d845d2ccde6bbe5958a91f5184c318efc50b1d'),
    ('Slice 14', 'aiweb_external_resource_quarantine_scaffold', 'cf22c2744ac28d6af6305b47d7c95ca0b9ae2005c0f4727b7e80fca23fb594fe', 9, 'External-resource quarantine and refusal; no resource is admitted.', ('ExternalResourceIdentityRecord', 'LicenseCustodyRecord', 'ProvenanceCustodyRecord', 'ResourceAdmissionReceiptRecord', 'ResourcePurposeBoundaryRecord', 'ResourceQuarantineDecisionRecord', 'build_external_resource_identity_record', 'build_license_custody_record', 'build_provenance_custody_record', 'build_resource_admission_receipt_record', 'build_resource_purpose_boundary_record', 'build_resource_quarantine_decision_record', 'demo_license_custody_record', 'demo_provenance_custody_record', 'demo_resource_admission_receipt_record', 'demo_resource_purpose_boundary_record', 'demo_resource_quarantine_decision_record', 'demo_sanskrit_wordnet_identity_record', 'demo_wordnet_identity_record', 'external_resource_quarantine_scope_record', 'validate_external_resource_identity_record', 'validate_license_custody_record', 'validate_provenance_custody_record', 'validate_resource_admission_receipt_record', 'validate_resource_purpose_boundary_record', 'validate_resource_quarantine_decision_record'), 'fd81f51b09be2793161fd06fa61ccfc8d65ad9c29e2d4c708af605962c5502fd'),
    ('Slice 15', 'aiweb_corpus_evidence_memory_trace_scaffold', '76b7e6d15043b6ce64553b87371d2734ab5e8312133d2b569ae21cfa611cfd47', 11, 'Corpus, evidence, memory and trace separation; no persistent authority.', ('AuthorityReferenceRecord', 'CategoryBoundaryRecord', 'CorpusEntryRecord', 'DOWNSTREAM_FALSE_ONLY_FIELDS', 'EvidenceRecord', 'MemoryRecord', 'MemoryRequestRecord', 'REQUIRED_SEPARATION_LAWS', 'SCHEMA_VERSION', 'SeparationAssertionRecord', 'SourceMentionRecord', 'TraceRecord', 'ValidationIssue', 'ValidationReport', 'build_authority_reference_record', 'build_category_boundary_record', 'build_corpus_entry_record', 'build_evidence_record', 'build_memory_record', 'build_memory_request_record', 'build_separation_assertion_record', 'build_source_mention_record', 'build_trace_record', 'corpus_evidence_memory_trace_scope_record', 'demo_authority_reference_record', 'demo_category_boundary_record', 'demo_corpus_entry_record', 'demo_evidence_not_memory_assertion', 'demo_evidence_record', 'demo_memory_not_external_truth_assertion', 'demo_memory_record', 'demo_memory_request_no_write_assertion', 'demo_memory_request_record', 'demo_required_separation_assertions', 'demo_source_mention_not_evidence_assertion', 'demo_source_mention_record', 'demo_trace_not_unrestricted_corpus_assertion', 'demo_trace_record', 'validate_authority_reference_record', 'validate_category_boundary_record', 'validate_corpus_entry_record', 'validate_evidence_record', 'validate_memory_record', 'validate_memory_request_record', 'validate_separation_assertion_record', 'validate_source_mention_record', 'validate_trace_record'), 'ada35af7177c43dc9b64ba290c65852570c887ef4ae311ae5dc31c00149ae9bc'),
    ('Slice 16', 'aiweb_selected_meaning_boundary_scaffold', '06950bcdd18bda2be35d9d404ebd15de4248c4fabfc8133367e8057411f42153', 9, 'Selected-meaning custody boundary; selection is not truth.', ('CandidateSelectionReferenceRecord', 'build_candidate_selection_reference_record', 'demo_candidate_selection_reference_record', 'demo_non_selected_candidate_reference_record', 'validate_candidate_selection_reference_record', 'REQUIRED_PRIOR_BOUNDARIES', 'REQUIRED_SELECTION_LAWS', 'SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS', 'selected_meaning_scope_record', 'SelectionBasisRecord', 'build_selection_basis_record', 'demo_selection_basis_record', 'validate_selection_basis_record', 'SelectionConstraintRecord', 'build_selection_constraint_record', 'demo_selection_constraint_record', 'validate_selection_constraint_record', 'SelectionReceiptRecord', 'build_selection_receipt_record', 'demo_selection_receipt_record', 'validate_selection_receipt_record', 'SelectedMeaningStatusRecord', 'build_selected_meaning_status_record', 'demo_selected_meaning_status_record', 'demo_selection_blocked_status_record', 'validate_selected_meaning_status_record', 'SelectionTraceRecord', 'build_selection_trace_record', 'demo_selection_trace_record', 'validate_selection_trace_record', 'run_verification'), 'ec7ce122df2c0d029f80d26ab64c02243ad59c5edcbaba40944915d46d17a71a'),
    ('Slice 17', 'aiweb_output_expression_boundary_scaffold', '6f5d65a97630d14ba2e590bbc219e754fea8ae7698ee01ce2db17be0e65003a1', 9, 'Expression-source and preview boundary; expression is not delivery.', ('SCHEMA_VERSION', 'NON_AUTHORITY_DISCLAIMER', 'REQUIRED_EXPRESSION_LAWS', 'expression_scope_record', 'ExpressionSourceRecord', 'build_expression_source_record', 'validate_expression_source_record', 'ExpressionPreservationContractRecord', 'build_expression_preservation_contract', 'validate_expression_preservation_contract', 'ExpressionPlanRecord', 'build_expression_plan_record', 'validate_expression_plan_record', 'ExpressionPreviewRecord', 'render_expression_preview', 'validate_expression_preview_record', 'ExpressionFidelityRecord', 'evaluate_expression_fidelity', 'validate_expression_fidelity_record', 'ExpressionReceiptRecord', 'build_expression_receipt_record', 'validate_expression_receipt_record'), 'd9c7f355782ea25d5a3652dc8b6d97399dbf1014e250031aa04affb4d050e79f'),
    ('Slice 18', 'aiweb_gp014_preservation_decision_scaffold', 'dfeb9a016bde775cda62a0835972a3c99f7f86f2dc6eb6780c3641063044fdca', 6, 'GP-014 preservation decision records only; no import, call or wrapper.', ('SCHEMA_VERSION', 'BASE_HEAD', 'SOURCE_AUTHORITY_PACKET_SHA256', 'GP014_IDENTITY', 'GP014_STATUS', 'GP014_RELATIONSHIP', 'GP014_WRAPPER_DECISION', 'GP014_PROTECTED_PATH_HASHES', 'GP015_STATUS', 'GP015_PROTECTED_PATH_HASHES', 'REQUIRED_DECISION_LAWS', 'gp014_decision_scope_record', 'GP014ReferenceRecord', 'build_gp014_reference_record', 'validate_gp014_reference_record', 'verify_gp014_reference_hashes', 'GP014WrapperDecisionRecord', 'build_gp014_wrapper_decision_record', 'validate_gp014_wrapper_decision_record', 'GP014PreservationReceiptRecord', 'build_gp014_preservation_receipt_record', 'validate_gp014_preservation_receipt_record', 'run_verification'), 'f7eabfcbf2bd1df7ccc950b3d008f1baf696bcd7d9c8e5fda5d12a272eeebce5'),
    ('Slice 19', 'aiweb_rmc_echo_boundary_scaffold', 'edf319c1b5044fdf67404a4a129e3d0114658f5aedc6d6d05b4c18323b9da7b3', 6, 'Deterministic Echo validation and non-authority boundary.', ('BOUNDARY_STATEMENTS', 'ECHO_AUTHORITY_DENIALS', 'ECHO_AUTHORITY_LAYER', 'ECHO_RELATIONSHIP', 'IMPLEMENTATION_STATE', 'authority_decision_for_claim', 'build_authority_report', 'build_boundary_report', 'build_slice19_receipt', 'validate_boundary_report', 'verify_slice19_invariants'), '1d63a78a7cecb9d67d454ffbfaeffce7d47e1e544504571a0de161805e9c0a19'),
    ('Slice 20', 'aiweb_delivery_action_tool_routing_boundary_scaffold', 'bec6e6f1fe84f1641a8d8d2bda93d7fbe2445d8abf312af644610f6d29777a98', 6, 'Delivery, action and tool-routing refusal boundary.', ('SLICE_ID', 'SLICE_TITLE', 'build_boundary_record', 'get_boundary_record', 'verify_slice20_boundary'), '6bd4175b2fe09778d3953053b74fe5235aa4a097d4ef9095e51c1477d99316bd'),
    ('Slice 21', 'aiweb_read_only_inspection_surface_scaffold', 'a8639119735f89852ca2ec5d750cfb442a06fdccc1e3a58d0b91d69a6765c42c', 6, 'Read-only inspection boundary; inspection is not runtime authority.', ('SLICE_ID', 'SLICE_TITLE', 'build_inspection_surface_record', 'get_inspection_surface_record', 'verify_slice21_boundary'), '14f48014416d0acd030cbd5f697f5bb90f725042616aed927c01ff8470a11a9a'),
)


class StaticComponentImportFailure(ImportError):
    def __init__(self, package_name: str, loaded_package_names: tuple[str, ...]):
        super().__init__(package_name)
        self.package_name = package_name
        self.loaded_package_names = loaded_package_names


def _load_component_01():
    import aiweb_meaning_law_trace_scaffold as module
    return module
def _load_component_02():
    import aiweb_concept_boundary_scaffold as module
    return module
def _load_component_03():
    import aiweb_predicate_role_boundary_scaffold as module
    return module
def _load_component_04():
    import aiweb_verbal_cognition_gate_boundary_scaffold as module
    return module
def _load_component_05():
    import aiweb_candidate_meaning_boundary_scaffold as module
    return module
def _load_component_06():
    import aiweb_ambiguity_clarification_boundary_scaffold as module
    return module
def _load_component_07():
    import aiweb_requirements_traceability_scaffold as module
    return module
def _load_component_08():
    import aiweb_external_resource_quarantine_scaffold as module
    return module
def _load_component_09():
    import aiweb_corpus_evidence_memory_trace_scaffold as module
    return module
def _load_component_10():
    import aiweb_selected_meaning_boundary_scaffold as module
    return module
def _load_component_11():
    import aiweb_output_expression_boundary_scaffold as module
    return module
def _load_component_12():
    import aiweb_gp014_preservation_decision_scaffold as module
    return module
def _load_component_13():
    import aiweb_rmc_echo_boundary_scaffold as module
    return module
def _load_component_14():
    import aiweb_delivery_action_tool_routing_boundary_scaffold as module
    return module
def _load_component_15():
    import aiweb_read_only_inspection_surface_scaffold as module
    return module


_STATIC_LOADERS = (
    ('aiweb_meaning_law_trace_scaffold', _load_component_01),
    ('aiweb_concept_boundary_scaffold', _load_component_02),
    ('aiweb_predicate_role_boundary_scaffold', _load_component_03),
    ('aiweb_verbal_cognition_gate_boundary_scaffold', _load_component_04),
    ('aiweb_candidate_meaning_boundary_scaffold', _load_component_05),
    ('aiweb_ambiguity_clarification_boundary_scaffold', _load_component_06),
    ('aiweb_requirements_traceability_scaffold', _load_component_07),
    ('aiweb_external_resource_quarantine_scaffold', _load_component_08),
    ('aiweb_corpus_evidence_memory_trace_scaffold', _load_component_09),
    ('aiweb_selected_meaning_boundary_scaffold', _load_component_10),
    ('aiweb_output_expression_boundary_scaffold', _load_component_11),
    ('aiweb_gp014_preservation_decision_scaffold', _load_component_12),
    ('aiweb_rmc_echo_boundary_scaffold', _load_component_13),
    ('aiweb_delivery_action_tool_routing_boundary_scaffold', _load_component_14),
    ('aiweb_read_only_inspection_surface_scaffold', _load_component_15),
)

ACCEPTED_PACKAGE_NAMES = tuple(spec[1] for spec in _INTERFACE_SPECS)


def export_digest(exports: tuple[str, ...]) -> str:
    return hashlib.sha256("\n".join(exports).encode("utf-8")).hexdigest()


def build_interface_contracts(
    registry: ComponentRegistryRecord,
) -> tuple[ComponentInterfaceContract, ...]:
    registry_report = validate_component_registry_record(registry)
    if not registry_report.ok:
        raise ValueError("invalid_component_registry")

    contracts: list[ComponentInterfaceContract] = []
    for registration, spec in zip(registry.components, _INTERFACE_SPECS, strict=True):
        (
            slice_ref,
            package_name,
            package_digest,
            file_count,
            accepted_scope,
            expected_exports,
            expected_export_digest,
        ) = spec
        identity = (
            registration.slice_ref,
            registration.package_name,
            registration.package_digest,
            registration.file_count,
            registration.accepted_scope,
        )
        if identity != (
            slice_ref,
            package_name,
            package_digest,
            file_count,
            accepted_scope,
        ):
            raise ValueError("component_registry_identity_mismatch")
        contract = build_component_interface_contract(
            slice_ref=slice_ref,
            component_registration_id=registration.component_registration_id,
            package_name=package_name,
            package_digest=package_digest,
            file_count=file_count,
            accepted_scope=accepted_scope,
            expected_exports=expected_exports,
            export_digest=expected_export_digest,
        )
        if not validate_component_interface_contract(contract).ok:
            raise ValueError("invalid_component_interface_contract")
        contracts.append(contract)
    return tuple(contracts)


def load_static_component_modules() -> tuple[tuple[str, object], ...]:
    loaded: list[tuple[str, object]] = []
    for package_name, loader in _STATIC_LOADERS:
        try:
            module = loader()
        except ImportError as exc:
            raise StaticComponentImportFailure(
                package_name,
                tuple(name for name, _ in loaded),
            ) from exc
        loaded.append((package_name, module))
    return tuple(loaded)
