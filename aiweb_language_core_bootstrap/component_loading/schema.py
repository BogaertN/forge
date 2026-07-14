"""Typed records for Slice 32 static component loading.

The records describe an explicit, offline, fixture-only import event. They do
not grant runtime, route, UI, memory, resource, delivery, tool, action, or
GP-014 authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from ..schema import (
    ValidationIssue,
    ValidationReport,
    issue,
    require_false,
    require_non_empty_text,
    require_true,
    require_unique_text_tuple,
    stable_record_id,
)

LOADING_SCHEMA_VERSION = "aiweb-language-core-component-loading-v1"

MODE_DISABLED_DEFAULT = "disabled_default"
MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING = "explicit_offline_component_loading"

STATUS_REFUSED_DISABLED = "refused_component_loading_disabled"
STATUS_HELD_INVALID_STATE = "held_invalid_component_loading_state"
STATUS_HELD_INVALID_FIXTURE = "held_invalid_component_loading_fixture"
STATUS_HELD_FIXTURE_NOT_ACCEPTED = "held_component_loading_fixture_not_accepted"
STATUS_HELD_BOUNDARY_INSPECTION_FAILED = "held_slice31_boundary_inspection_failed"
STATUS_HELD_PREEXISTING_UNREGISTERED_COMPONENT = (
    "held_preexisting_unregistered_project_component"
)
STATUS_HELD_STATIC_IMPORT_FAILED = "held_static_component_import_failed"
STATUS_HELD_INTERFACE_MISMATCH = "held_component_interface_mismatch"
STATUS_HELD_UNREGISTERED_COMPONENT = "held_unregistered_project_component"
STATUS_COMPLETED_STATIC_LOADING = "completed_static_component_loading"

OPERATION_LOAD_ACCEPTED_COMPONENTS = "load_accepted_boundary_components"

EXACT_FIXTURE_NAME = "slice32-explicit-static-component-loading-v1"
EXACT_FIXTURE_ID = "component_loading_fixture:1cb2ed164c1c18c61ba202bdeaa1b5e1bb2381414903e1208f9b1f819bbc11a2"
EXACT_SLICE31_FIXTURE_NAME = "slice31-explicit-offline-boundary-inspection-v1"
EXACT_DISABLED_STATE_ID = "component_loading_state:78be102f2a87996ed3c9f4ccbe568c09f10b0a201f7826d9dcc709b660d89f08"
EXACT_ENABLED_STATE_ID = "component_loading_state:2436ea1e5fd118edaf8b2554473c3972d837b90f774b39c60f406e60458e674c"
EXACT_SLICE31_RESULT_ID = "bootstrap_adapter_result:00d28f7da240c9fa23ef6a0f2f19236e9c1e03de82cebb7e61d841ea8ee06efd"
EXACT_BOOTSTRAP_BOUNDARY_ID = "bootstrap_boundary:9a0ac3e201cdd18d7974b4f7af77dbf0bb20ae8d28af4b34893c10ef6866183c"
EXACT_COMPONENT_REGISTRY_ID = "bootstrap_registry:1a771c2ca6bd88e2dc8ce3be555ef5eb86e62d56d460c4f3d30cebc84c04faa5"
EXACT_DISABLED_REASON_CODE = "explicit_component_loading_enable_required"
EXACT_SUCCESS_REASON_CODE = "all_registered_components_loaded_through_static_interfaces"
EXACT_DISABLED_RESULT_ID = "component_loading_result:cee203ebeb1e8764e9d4f5edc66fa359b49fdc9a9c38402bfbd746f31d744c21"
EXACT_SUCCESS_RESULT_ID = "component_loading_result:f4d873441759da615d263fa6483151f5b7323221caf2c75de518bc56ad4a3c84"


@dataclass(frozen=True, slots=True)
class AcceptedLoadedComponentIdentity:
    """Immutable accepted identity for one Slice 32 loaded boundary package."""

    slice_ref: str
    component_registration_id: str
    package_name: str
    package_digest: str
    file_count: int
    accepted_scope: str
    expected_exports: tuple[str, ...]
    export_count: int
    export_digest: str
    interface_contract_id: str
    load_order: int
    loaded_component_id: str


_ACCEPTED_COMPONENT_IDENTITIES = (
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 7',
        component_registration_id='bootstrap_component:5e3792ab323485abdf683b66bad7108fb713e482fe61a9eb2915571294beda56',
        package_name='aiweb_meaning_law_trace_scaffold',
        package_digest='c8ca2f959815d9d4f4b947b635dcd499ce54f30562d204f99aa86e8384568e38',
        file_count=4,
        accepted_scope='Meaning-object and law-trace record boundary; no truth or runtime authority.',
        expected_exports=('MeaningObject',
             'build_meaning_object',
             'meaning_object_scope_record',
             'LawTrace',
             'LawTraceStep',
             'build_law_trace',
             'build_law_trace_step',
             'law_trace_scope_record'),
        export_count=8,
        export_digest='c7f1e619b4489f5e34be24a8ffba312e64729dc05cc21bdd8c5b717359cc8d4f',
        interface_contract_id='component_interface:253f75057fc3aab5bb2a97b9b665f0961b495d87edaccc7850e4f345e83f1739',
        load_order=1,
        loaded_component_id='loaded_component:a806e2c498f9a1e885b75ec5ec55652a6f86065fc7c55f773f3d559e48b1296a',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 8',
        component_registration_id='bootstrap_component:28e802ed024957cebb201200a617d753fc324bc69a0e494ef45a21e88860df71',
        package_name='aiweb_concept_boundary_scaffold',
        package_digest='28843077cf64aeb7f6f455eb6cec313f35ab5004c803ed03a02824f43357de01',
        file_count=4,
        accepted_scope='Concept and relation boundary; concepts are not evidence or selected meaning.',
        expected_exports=('ConceptBoundaryRecord',
             'SenseBoundaryRecord',
             'SemanticRelationBoundaryRecord',
             'ValidationIssue',
             'ValidationReport',
             'concept_scope_record',
             'relation_scope_record',
             'stable_boundary_id',
             'validate_concept_record',
             'validate_sense_record',
             'validate_relation_record'),
        export_count=11,
        export_digest='0e04b97ff1cb856290c9d7df683c4f8e2b0865f962049b45481690b77346e3f6',
        interface_contract_id='component_interface:f6d4beaf719cc9b5096b334e9aaa25d6a23ed29bf1b3305146de06505c1a21e3',
        load_order=2,
        loaded_component_id='loaded_component:c4e6b40a4c401606fcd29f811b707d38c3687f85d43d5d51c04b10c00bf79aa5',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 9',
        component_registration_id='bootstrap_component:adea692896be88cb685895575187d6067e1f304f303c37bfccd924f1caae5970',
        package_name='aiweb_predicate_role_boundary_scaffold',
        package_digest='88feda8338f8b7927ad041886fe1ca99bd211fdc7ea261faf69b2b5333e8faf3',
        file_count=6,
        accepted_scope='Predicate, role, speech-act and effect boundary; frames are not execution.',
        expected_exports=('DEPENDENCY_CHANGE',
             'RUNTIME_EFFECT',
             'SCHEMA_VERSION',
             'SCOPE_STATUS',
             'EffectBoundaryRecord',
             'PredicateFrameBoundaryRecord',
             'RoleBoundaryRecord',
             'SpeechActBoundaryRecord',
             'ValidationIssue',
             'ValidationReport',
             'demo_command_speech_act_record',
             'demo_effect_boundary_record',
             'demo_implementation_request_speech_act_record',
             'demo_memory_request_speech_act_record',
             'demo_missing_role_record',
             'demo_predicate_frame_record',
             'demo_role_record',
             'demo_speech_act_record',
             'demo_unknown_effect_boundary_record',
             'demo_unknown_predicate_frame_record',
             'demo_unknown_role_record',
             'predicate_role_scope_record',
             'stable_boundary_id',
             'validate_effect_boundary_record',
             'validate_predicate_frame_record',
             'validate_role_record',
             'validate_speech_act_record'),
        export_count=27,
        export_digest='f12e338dccc631f0845b9cd5ad7fac7a2b79f53efeb321cf276492f0f5196d94',
        interface_contract_id='component_interface:f81c402f1da42aca075402bc175dfc8b942c3e1323e9c02124aaad455ddfb2f2',
        load_order=3,
        loaded_component_id='loaded_component:527f12b425951438c6bb646d5082791cbd3781e6a0aa2a5c1406e0a005d2a9f5',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 10',
        component_registration_id='bootstrap_component:e2d61bd36146e2b5c017fa6492ae1ed61f0958dbeccc100d7c9613c79b928dc6',
        package_name='aiweb_verbal_cognition_gate_boundary_scaffold',
        package_digest='308385c90974885c5b13b2422f7df1d9253db35717bef80a1e4cd3e9b10b51f5',
        file_count=6,
        accepted_scope='Gate-state record boundary; gate output is not routing or action.',
        expected_exports=('SCHEMA_VERSION',
             'SCOPE_STATUS',
             'ValidationIssue',
             'ValidationReport',
             'GateBoundaryRecord',
             'GateOutcomeBoundaryRecord',
             'ExpectancyBoundaryRecord',
             'GateStateBoundaryRecord',
             'stable_boundary_id',
             'verbal_cognition_gate_scope_record',
             'validate_gate_boundary_record',
             'validate_gate_outcome_record',
             'validate_expectancy_record',
             'validate_gate_state_record',
             'demo_gate_boundary_record',
             'demo_unknown_gate_boundary_record',
             'demo_gate_outcome_record',
             'demo_clarification_required_outcome_record',
             'demo_blocked_action_outcome_record',
             'demo_unknown_gate_outcome_record',
             'demo_expectancy_record',
             'demo_congruity_record',
             'demo_connectedness_record',
             'demo_recoverable_purpose_record',
             'demo_unknown_expectancy_record',
             'demo_ambiguity_state_record',
             'demo_clarification_required_state_record',
             'demo_unsupported_state_record',
             'demo_blocked_action_state_record',
             'demo_deferred_state_record'),
        export_count=30,
        export_digest='d8e8c9710852d266fcc8e588ef7f7f88c526ee43634d618cc1c00aec8adb9f82',
        interface_contract_id='component_interface:ca373743842d5cf30ebd5009eebed2fab8dadb28de22a6ae355d9b4fc7e09bce',
        load_order=4,
        loaded_component_id='loaded_component:7f6af54282b01fd8d2fb49fcdf6856bfceaf818e0ecc856815cd30fb762bd7f5',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 11',
        component_registration_id='bootstrap_component:1b71b5faeab690c1320c0311f08313e0d51f9f52e10395e282a4666c5ba59200',
        package_name='aiweb_candidate_meaning_boundary_scaffold',
        package_digest='3eda1f92198049b1c71ab59878a79587995d29e8508ca5f8780aabaa6dcb7656',
        file_count=7,
        accepted_scope='Source custody and candidate-meaning boundary; candidate is not selected meaning.',
        expected_exports=('CandidateMeaningBoundaryRecord',
             'candidate_meaning_scope_record',
             'demo_candidate_meaning_record',
             'demo_no_action_candidate_record',
             'demo_unsupported_candidate_record',
             'validate_candidate_meaning_record',
             'SourceExpressionCustodyRecord',
             'build_source_expression_custody_record',
             'demo_source_expression_custody_record',
             'validate_source_expression_custody_record',
             'DerivedStructureCustodyRecord',
             'demo_derived_structure_custody_record',
             'validate_derived_structure_custody_record',
             'MissingSupportBoundaryRecord',
             'demo_missing_support_boundary_record',
             'demo_no_missing_support_boundary_record',
             'validate_missing_support_boundary_record',
             'CandidateCompetitionSetBoundaryRecord',
             'demo_candidate_competition_set_record',
             'validate_candidate_competition_set_record'),
        export_count=20,
        export_digest='6ae2df08826c6ebc40fbbbf7660fc8c34f14659c510f7ad3c7ff68a20542f9e4',
        interface_contract_id='component_interface:5ca455979dd5c432c6c6227b3545de7d1ffb6b065d3c57cf41e77a5472bec566',
        load_order=5,
        loaded_component_id='loaded_component:a985112a2e16efddbbf46b79577d6298f62fedb9fac2d24fc7d878bc2a5e1317',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 12',
        component_registration_id='bootstrap_component:f1673fc5e4bd6964f4cdce6f35f77242cb1ea8242a61f3572cdd717b5c0e2af3',
        package_name='aiweb_ambiguity_clarification_boundary_scaffold',
        package_digest='290936f9ffeba047d06a61e32135f580505e6937597cd052dde6ee03d2b29b1f',
        file_count=6,
        accepted_scope='Ambiguity, unknown, unsupported, deferred and clarification states.',
        expected_exports=('AmbiguityStateBoundaryRecord',
             'ClarificationRequirementBoundaryRecord',
             'UnknownSupportBoundaryRecord',
             'StateTraceBoundaryRecord',
             'ambiguity_clarification_scope_record',
             'build_state_boundary_record',
             'build_clarification_requirement_record',
             'build_unknown_support_record',
             'build_state_trace_record',
             'demo_ambiguity_state_record',
             'demo_deferred_state_record',
             'demo_unknown_state_record',
             'demo_unsupported_state_record',
             'demo_clarification_blocked_record',
             'demo_clarification_required_record',
             'demo_unknown_concept_record',
             'demo_unsupported_resource_record',
             'demo_state_trace_record',
             'validate_state_boundary_record',
             'validate_clarification_requirement_record',
             'validate_unknown_support_record',
             'validate_state_trace_record',
             'run_verification'),
        export_count=23,
        export_digest='15f2bb3e69f6e478ac203154e566e402daf7b69f46af2f3cd4d422e37e878e90',
        interface_contract_id='component_interface:848b7d28966b2f068ef9d9df1d662358a0415e746e819d81451c4be74ae1cfb0',
        load_order=6,
        loaded_component_id='loaded_component:d429f1bfafbd7019276588acceb73b78c282c93cacc65c49053c240968aac876',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 13',
        component_registration_id='bootstrap_component:05677832b3339f6587c6fd0c0bbea24b5e9027a53c04f0326551fa952e648268',
        package_name='aiweb_requirements_traceability_scaffold',
        package_digest='0c7872dc5456b807af37fb64260f99d76a94ad4e003be952dc562309f0b8ded9',
        file_count=7,
        accepted_scope='Requirement-to-test traceability records only.',
        expected_exports=('AcceptedScopeRecord',
             'RollbackTriggerRecord',
             'TraceabilityReceiptRecord',
             'RequirementIdentityRecord',
             'RequirementTestCrosswalkRecord',
             'build_accepted_scope_record',
             'build_rollback_trigger_record',
             'build_traceability_receipt_record',
             'build_requirement_identity_record',
             'build_requirement_test_crosswalk_record',
             'demo_accepted_scope_record',
             'demo_rollback_trigger_record',
             'demo_traceability_receipt_record',
             'demo_requirement_identity_record',
             'demo_requirement_test_crosswalk_record',
             'requirements_traceability_scope_record',
             'validate_accepted_scope_record',
             'validate_rollback_trigger_record',
             'validate_traceability_receipt_record',
             'validate_requirement_identity_record',
             'validate_requirement_test_crosswalk_record'),
        export_count=21,
        export_digest='6279fda5c585c6a8bf323e78c5d845d2ccde6bbe5958a91f5184c318efc50b1d',
        interface_contract_id='component_interface:f97d54317df731dd1d320082f6b1086f9b68e9a2e8bec191fe9bc69bc322256b',
        load_order=7,
        loaded_component_id='loaded_component:2e460babfd9a7e006533e6f9f991a42f3c403c668fa3d07c939f6bc15db1a08f',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 14',
        component_registration_id='bootstrap_component:18fff86f369780bd2ead070b4388216a8b71403367de093099894fcfb99bae34',
        package_name='aiweb_external_resource_quarantine_scaffold',
        package_digest='cf22c2744ac28d6af6305b47d7c95ca0b9ae2005c0f4727b7e80fca23fb594fe',
        file_count=9,
        accepted_scope='External-resource quarantine and refusal; no resource is admitted.',
        expected_exports=('ExternalResourceIdentityRecord',
             'LicenseCustodyRecord',
             'ProvenanceCustodyRecord',
             'ResourceAdmissionReceiptRecord',
             'ResourcePurposeBoundaryRecord',
             'ResourceQuarantineDecisionRecord',
             'build_external_resource_identity_record',
             'build_license_custody_record',
             'build_provenance_custody_record',
             'build_resource_admission_receipt_record',
             'build_resource_purpose_boundary_record',
             'build_resource_quarantine_decision_record',
             'demo_license_custody_record',
             'demo_provenance_custody_record',
             'demo_resource_admission_receipt_record',
             'demo_resource_purpose_boundary_record',
             'demo_resource_quarantine_decision_record',
             'demo_sanskrit_wordnet_identity_record',
             'demo_wordnet_identity_record',
             'external_resource_quarantine_scope_record',
             'validate_external_resource_identity_record',
             'validate_license_custody_record',
             'validate_provenance_custody_record',
             'validate_resource_admission_receipt_record',
             'validate_resource_purpose_boundary_record',
             'validate_resource_quarantine_decision_record'),
        export_count=26,
        export_digest='fd81f51b09be2793161fd06fa61ccfc8d65ad9c29e2d4c708af605962c5502fd',
        interface_contract_id='component_interface:f9111a50a522ab5d53445a9463afab824eadd0e4ce54baf9663bce60667952fe',
        load_order=8,
        loaded_component_id='loaded_component:b84e57e37c37a76232efc2fe9fca0b6da687c7d09b3e19b89e78c7c604f034ac',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 15',
        component_registration_id='bootstrap_component:998bbbccfe6a478ed1648d3e79e30483e33f00afca188d077911876a4f3c757f',
        package_name='aiweb_corpus_evidence_memory_trace_scaffold',
        package_digest='76b7e6d15043b6ce64553b87371d2734ab5e8312133d2b569ae21cfa611cfd47',
        file_count=11,
        accepted_scope='Corpus, evidence, memory and trace separation; no persistent authority.',
        expected_exports=('AuthorityReferenceRecord',
             'CategoryBoundaryRecord',
             'CorpusEntryRecord',
             'DOWNSTREAM_FALSE_ONLY_FIELDS',
             'EvidenceRecord',
             'MemoryRecord',
             'MemoryRequestRecord',
             'REQUIRED_SEPARATION_LAWS',
             'SCHEMA_VERSION',
             'SeparationAssertionRecord',
             'SourceMentionRecord',
             'TraceRecord',
             'ValidationIssue',
             'ValidationReport',
             'build_authority_reference_record',
             'build_category_boundary_record',
             'build_corpus_entry_record',
             'build_evidence_record',
             'build_memory_record',
             'build_memory_request_record',
             'build_separation_assertion_record',
             'build_source_mention_record',
             'build_trace_record',
             'corpus_evidence_memory_trace_scope_record',
             'demo_authority_reference_record',
             'demo_category_boundary_record',
             'demo_corpus_entry_record',
             'demo_evidence_not_memory_assertion',
             'demo_evidence_record',
             'demo_memory_not_external_truth_assertion',
             'demo_memory_record',
             'demo_memory_request_no_write_assertion',
             'demo_memory_request_record',
             'demo_required_separation_assertions',
             'demo_source_mention_not_evidence_assertion',
             'demo_source_mention_record',
             'demo_trace_not_unrestricted_corpus_assertion',
             'demo_trace_record',
             'validate_authority_reference_record',
             'validate_category_boundary_record',
             'validate_corpus_entry_record',
             'validate_evidence_record',
             'validate_memory_record',
             'validate_memory_request_record',
             'validate_separation_assertion_record',
             'validate_source_mention_record',
             'validate_trace_record'),
        export_count=47,
        export_digest='ada35af7177c43dc9b64ba290c65852570c887ef4ae311ae5dc31c00149ae9bc',
        interface_contract_id='component_interface:a01fb1575a5583f1845fe1058f72674b4c664b06bac8e16c7e41ee994a726135',
        load_order=9,
        loaded_component_id='loaded_component:db54855906dfb8bbe0634d0118973a585fdd6f5c52f7a131c67536060972401b',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 16',
        component_registration_id='bootstrap_component:7591ba5cf2da189007ac16968b0979e7dbdfc00f37fed5de1dedca38127a5e27',
        package_name='aiweb_selected_meaning_boundary_scaffold',
        package_digest='06950bcdd18bda2be35d9d404ebd15de4248c4fabfc8133367e8057411f42153',
        file_count=9,
        accepted_scope='Selected-meaning custody boundary; selection is not truth.',
        expected_exports=('CandidateSelectionReferenceRecord',
             'build_candidate_selection_reference_record',
             'demo_candidate_selection_reference_record',
             'demo_non_selected_candidate_reference_record',
             'validate_candidate_selection_reference_record',
             'REQUIRED_PRIOR_BOUNDARIES',
             'REQUIRED_SELECTION_LAWS',
             'SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS',
             'selected_meaning_scope_record',
             'SelectionBasisRecord',
             'build_selection_basis_record',
             'demo_selection_basis_record',
             'validate_selection_basis_record',
             'SelectionConstraintRecord',
             'build_selection_constraint_record',
             'demo_selection_constraint_record',
             'validate_selection_constraint_record',
             'SelectionReceiptRecord',
             'build_selection_receipt_record',
             'demo_selection_receipt_record',
             'validate_selection_receipt_record',
             'SelectedMeaningStatusRecord',
             'build_selected_meaning_status_record',
             'demo_selected_meaning_status_record',
             'demo_selection_blocked_status_record',
             'validate_selected_meaning_status_record',
             'SelectionTraceRecord',
             'build_selection_trace_record',
             'demo_selection_trace_record',
             'validate_selection_trace_record',
             'run_verification'),
        export_count=31,
        export_digest='ec7ce122df2c0d029f80d26ab64c02243ad59c5edcbaba40944915d46d17a71a',
        interface_contract_id='component_interface:d9af399e8896902e32c497edf6f07c3a9d1107ac9a324e455a7318753f9f6248',
        load_order=10,
        loaded_component_id='loaded_component:7a477494c3d5a4a0db049d478a49c7d4cef66478f00dfb6bfd5e3ee48e5ce399',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 17',
        component_registration_id='bootstrap_component:85362007318150586fc6be1cb22c866ea0f3e2940a348b5568df6baa84dcee2c',
        package_name='aiweb_output_expression_boundary_scaffold',
        package_digest='6f5d65a97630d14ba2e590bbc219e754fea8ae7698ee01ce2db17be0e65003a1',
        file_count=9,
        accepted_scope='Expression-source and preview boundary; expression is not delivery.',
        expected_exports=('SCHEMA_VERSION',
             'NON_AUTHORITY_DISCLAIMER',
             'REQUIRED_EXPRESSION_LAWS',
             'expression_scope_record',
             'ExpressionSourceRecord',
             'build_expression_source_record',
             'validate_expression_source_record',
             'ExpressionPreservationContractRecord',
             'build_expression_preservation_contract',
             'validate_expression_preservation_contract',
             'ExpressionPlanRecord',
             'build_expression_plan_record',
             'validate_expression_plan_record',
             'ExpressionPreviewRecord',
             'render_expression_preview',
             'validate_expression_preview_record',
             'ExpressionFidelityRecord',
             'evaluate_expression_fidelity',
             'validate_expression_fidelity_record',
             'ExpressionReceiptRecord',
             'build_expression_receipt_record',
             'validate_expression_receipt_record'),
        export_count=22,
        export_digest='d9c7f355782ea25d5a3652dc8b6d97399dbf1014e250031aa04affb4d050e79f',
        interface_contract_id='component_interface:d3bb34d6f378aa916de19fb6c1ed2029ece1520e0a7ab8b41e493a7501c7daf0',
        load_order=11,
        loaded_component_id='loaded_component:7f885a2baa0efe6786602717363820eab6485936fb75640e9ad19e881690d423',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 18',
        component_registration_id='bootstrap_component:0fd6fc718c6df2aa5e58852b5f5468cf67d013cde7b340b6610a7b63cb24c6e2',
        package_name='aiweb_gp014_preservation_decision_scaffold',
        package_digest='dfeb9a016bde775cda62a0835972a3c99f7f86f2dc6eb6780c3641063044fdca',
        file_count=6,
        accepted_scope='GP-014 preservation decision records only; no import, call or wrapper.',
        expected_exports=('SCHEMA_VERSION',
             'BASE_HEAD',
             'SOURCE_AUTHORITY_PACKET_SHA256',
             'GP014_IDENTITY',
             'GP014_STATUS',
             'GP014_RELATIONSHIP',
             'GP014_WRAPPER_DECISION',
             'GP014_PROTECTED_PATH_HASHES',
             'GP015_STATUS',
             'GP015_PROTECTED_PATH_HASHES',
             'REQUIRED_DECISION_LAWS',
             'gp014_decision_scope_record',
             'GP014ReferenceRecord',
             'build_gp014_reference_record',
             'validate_gp014_reference_record',
             'verify_gp014_reference_hashes',
             'GP014WrapperDecisionRecord',
             'build_gp014_wrapper_decision_record',
             'validate_gp014_wrapper_decision_record',
             'GP014PreservationReceiptRecord',
             'build_gp014_preservation_receipt_record',
             'validate_gp014_preservation_receipt_record',
             'run_verification'),
        export_count=23,
        export_digest='f7eabfcbf2bd1df7ccc950b3d008f1baf696bcd7d9c8e5fda5d12a272eeebce5',
        interface_contract_id='component_interface:a1462f1871ba4b73040e24fee547631ad4c59fd3b691b98dd7c685b131be7845',
        load_order=12,
        loaded_component_id='loaded_component:fc2240ec6a7b54d186f3834fff61e6d31ee7010b39138ae37d2a3cc699af8fde',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 19',
        component_registration_id='bootstrap_component:4ca68bb813a3702ed61ff4c9e0c7c4d52a5539979c34805b95a6d3c3ec099c7c',
        package_name='aiweb_rmc_echo_boundary_scaffold',
        package_digest='edf319c1b5044fdf67404a4a129e3d0114658f5aedc6d6d05b4c18323b9da7b3',
        file_count=6,
        accepted_scope='Deterministic Echo validation and non-authority boundary.',
        expected_exports=('BOUNDARY_STATEMENTS',
             'ECHO_AUTHORITY_DENIALS',
             'ECHO_AUTHORITY_LAYER',
             'ECHO_RELATIONSHIP',
             'IMPLEMENTATION_STATE',
             'authority_decision_for_claim',
             'build_authority_report',
             'build_boundary_report',
             'build_slice19_receipt',
             'validate_boundary_report',
             'verify_slice19_invariants'),
        export_count=11,
        export_digest='1d63a78a7cecb9d67d454ffbfaeffce7d47e1e544504571a0de161805e9c0a19',
        interface_contract_id='component_interface:67d1609ff57d26ed31ad3b2ad4641442a4c173d573e00c36b9ce8343369e740b',
        load_order=13,
        loaded_component_id='loaded_component:3cc11a7bb5b3f83c38b39ccba74124965103293c21176448756bf8af323a172a',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 20',
        component_registration_id='bootstrap_component:25f8a47b45bf82d5f785e0ed483356a58b4e913fc9681020947dc8e35ae071d7',
        package_name='aiweb_delivery_action_tool_routing_boundary_scaffold',
        package_digest='bec6e6f1fe84f1641a8d8d2bda93d7fbe2445d8abf312af644610f6d29777a98',
        file_count=6,
        accepted_scope='Delivery, action and tool-routing refusal boundary.',
        expected_exports=('SLICE_ID',
             'SLICE_TITLE',
             'build_boundary_record',
             'get_boundary_record',
             'verify_slice20_boundary'),
        export_count=5,
        export_digest='6bd4175b2fe09778d3953053b74fe5235aa4a097d4ef9095e51c1477d99316bd',
        interface_contract_id='component_interface:75ac82866b20ecdadfff46ad27f70645d8262564f74d12e5e368ad7ceca188d4',
        load_order=14,
        loaded_component_id='loaded_component:4cd78accb1f852a195cef1d7d8519ec1eafa149c2d142459a343ed253eecf75b',
    ),
    AcceptedLoadedComponentIdentity(
        slice_ref='Slice 21',
        component_registration_id='bootstrap_component:7b329aae16f0bc31e70170f514f0d311db4bdde20cfbf114498333e60830424d',
        package_name='aiweb_read_only_inspection_surface_scaffold',
        package_digest='a8639119735f89852ca2ec5d750cfb442a06fdccc1e3a58d0b91d69a6765c42c',
        file_count=6,
        accepted_scope='Read-only inspection boundary; inspection is not runtime authority.',
        expected_exports=('SLICE_ID',
             'SLICE_TITLE',
             'build_inspection_surface_record',
             'get_inspection_surface_record',
             'verify_slice21_boundary'),
        export_count=5,
        export_digest='14f48014416d0acd030cbd5f697f5bb90f725042616aed927c01ff8470a11a9a',
        interface_contract_id='component_interface:6cae37265e3264917c9fd40404af17c67d4489ab68acd81402e7bce50423fd0d',
        load_order=15,
        loaded_component_id='loaded_component:9b99b5dd01ed85dade855f95492cc38a0eae3bbb07b49212323d40209daadf2e',
    ),
)

if len(_ACCEPTED_COMPONENT_IDENTITIES) != 15:
    raise RuntimeError("slice32_accepted_identity_count_mismatch")

_ACCEPTED_IDENTITY_BY_PACKAGE = {
    item.package_name: item for item in _ACCEPTED_COMPONENT_IDENTITIES
}
_ACCEPTED_IDENTITY_BY_LOAD_ORDER = {
    item.load_order: item for item in _ACCEPTED_COMPONENT_IDENTITIES
}
if len(_ACCEPTED_IDENTITY_BY_PACKAGE) != 15 or len(_ACCEPTED_IDENTITY_BY_LOAD_ORDER) != 15:
    raise RuntimeError("slice32_accepted_identity_uniqueness_failure")

_EXACT_PACKAGE_ORDER = tuple(item.package_name for item in _ACCEPTED_COMPONENT_IDENTITIES)
_EXACT_REGISTRATION_ORDER = tuple(
    item.component_registration_id for item in _ACCEPTED_COMPONENT_IDENTITIES
)
_EXACT_INTERFACE_CONTRACT_ORDER = tuple(
    item.interface_contract_id for item in _ACCEPTED_COMPONENT_IDENTITIES
)
_EXACT_LOADED_COMPONENT_ORDER = tuple(
    item.loaded_component_id for item in _ACCEPTED_COMPONENT_IDENTITIES
)


@dataclass(frozen=True, slots=True)
class ComponentLoadingState:
    loading_state_id: str
    enabled: bool
    activation_mode: str
    disabled_by_default: bool
    fixture_only: bool
    offline_only: bool
    deterministic: bool
    static_allowlist_only: bool
    component_loading_authorized: bool
    python_module_import_read_only: bool
    dynamic_loading_allowed: bool
    plugin_discovery_allowed: bool
    hidden_fallback_allowed: bool
    environment_selected_backend: bool
    main_connection_allowed: bool
    route_connection_allowed: bool
    api_connection_allowed: bool
    ui_connection_allowed: bool
    network_allowed: bool
    external_data_filesystem_read_allowed: bool
    filesystem_write_allowed: bool
    external_resource_allowed: bool
    memory_write_allowed: bool
    evidence_mutation_allowed: bool
    delivery_allowed: bool
    tool_routing_allowed: bool
    action_allowed: bool
    gp014_import_allowed: bool
    gp014_call_allowed: bool
    production_ready: bool
    release_authorized: bool
    schema_version: str = LOADING_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("loading_state_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("component_loading_state", self.canonical_body())


@dataclass(frozen=True, slots=True)
class ComponentLoadingFixtureRecord:
    fixture_id: str
    fixture_name: str
    operation: str
    required_activation_mode: str
    required_slice31_fixture_name: str
    expected_result_status: str
    synthetic: bool
    forge_owned: bool
    internal_only: bool
    fixture_only: bool
    offline_only: bool
    runtime_prohibited: bool
    evidence: bool
    memory: bool
    runtime_corpus: bool
    production_data: bool
    public_output: bool
    external_resource_derived: bool
    memory_derived: bool
    trace_derived: bool
    contains_real_personal_data: bool
    contains_live_secret: bool
    contains_executable_command: bool
    contains_tool_invocation: bool
    schema_version: str = LOADING_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("fixture_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("component_loading_fixture", self.canonical_body())


@dataclass(frozen=True, slots=True)
class ComponentInterfaceContract:
    interface_contract_id: str
    slice_ref: str
    component_registration_id: str
    package_name: str
    package_digest: str
    file_count: int
    accepted_scope: str
    expected_exports: tuple[str, ...]
    export_count: int
    export_digest: str
    static_import_required: bool
    component_invocation_allowed: bool
    verifier_invocation_allowed: bool
    runtime_authority_allowed: bool
    schema_version: str = LOADING_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("interface_contract_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("component_interface", self.canonical_body())


@dataclass(frozen=True, slots=True)
class LoadedComponentRecord:
    loaded_component_id: str
    interface_contract_id: str
    component_registration_id: str
    package_name: str
    module_name: str
    load_order: int
    export_count: int
    export_digest: str
    module_loaded: bool
    interface_verified: bool
    component_invoked: bool
    verifier_invoked: bool
    runtime_authority_granted: bool
    persistent_side_effect_performed: bool
    schema_version: str = LOADING_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("loaded_component_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("loaded_component", self.canonical_body())


@dataclass(frozen=True, slots=True)
class ComponentLoadingResult:
    loading_result_id: str
    fixture_id: str
    loading_state_id: str
    slice31_result_id: str
    bootstrap_boundary_id: str
    component_registry_id: str
    status: str
    reason_code: str
    loaded_components: tuple[LoadedComponentRecord, ...]
    loaded_component_count: int
    accepted_component_count: int
    failed_package_name: str
    unregistered_project_roots: tuple[str, ...]
    deterministic: bool
    fixture_only: bool
    offline_only: bool
    static_allowlist_only: bool
    dynamic_discovery_performed: bool
    hidden_fallback_used: bool
    component_invocation_performed: bool
    verifier_invocation_performed: bool
    runtime_connection_performed: bool
    network_access_performed: bool
    external_data_filesystem_read_performed: bool
    filesystem_write_performed: bool
    external_resource_used: bool
    memory_write_performed: bool
    evidence_mutation_performed: bool
    delivery_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    gp014_imported: bool
    gp014_called: bool
    persistent_side_effect_performed: bool
    schema_version: str = LOADING_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("loading_result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("component_loading_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_FALSE_ONLY_STATE_FIELDS = (
    "dynamic_loading_allowed",
    "plugin_discovery_allowed",
    "hidden_fallback_allowed",
    "environment_selected_backend",
    "main_connection_allowed",
    "route_connection_allowed",
    "api_connection_allowed",
    "ui_connection_allowed",
    "network_allowed",
    "external_data_filesystem_read_allowed",
    "filesystem_write_allowed",
    "external_resource_allowed",
    "memory_write_allowed",
    "evidence_mutation_allowed",
    "delivery_allowed",
    "tool_routing_allowed",
    "action_allowed",
    "gp014_import_allowed",
    "gp014_call_allowed",
    "production_ready",
    "release_authorized",
)

_FALSE_ONLY_RESULT_FIELDS = (
    "dynamic_discovery_performed",
    "hidden_fallback_used",
    "component_invocation_performed",
    "verifier_invocation_performed",
    "runtime_connection_performed",
    "network_access_performed",
    "external_data_filesystem_read_performed",
    "filesystem_write_performed",
    "external_resource_used",
    "memory_write_performed",
    "evidence_mutation_performed",
    "delivery_performed",
    "tool_routing_performed",
    "action_performed",
    "gp014_imported",
    "gp014_called",
    "persistent_side_effect_performed",
)


def build_component_loading_state(*, enabled: bool = False) -> ComponentLoadingState:
    body = {
        "enabled": enabled,
        "activation_mode": (
            MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING
            if enabled
            else MODE_DISABLED_DEFAULT
        ),
        "disabled_by_default": True,
        "fixture_only": True,
        "offline_only": True,
        "deterministic": True,
        "static_allowlist_only": True,
        "component_loading_authorized": enabled,
        "python_module_import_read_only": True,
        "dynamic_loading_allowed": False,
        "plugin_discovery_allowed": False,
        "hidden_fallback_allowed": False,
        "environment_selected_backend": False,
        "main_connection_allowed": False,
        "route_connection_allowed": False,
        "api_connection_allowed": False,
        "ui_connection_allowed": False,
        "network_allowed": False,
        "external_data_filesystem_read_allowed": False,
        "filesystem_write_allowed": False,
        "external_resource_allowed": False,
        "memory_write_allowed": False,
        "evidence_mutation_allowed": False,
        "delivery_allowed": False,
        "tool_routing_allowed": False,
        "action_allowed": False,
        "gp014_import_allowed": False,
        "gp014_call_allowed": False,
        "production_ready": False,
        "release_authorized": False,
        "schema_version": LOADING_SCHEMA_VERSION,
    }
    return ComponentLoadingState(
        loading_state_id=stable_record_id("component_loading_state", body),
        **body,
    )


def build_component_loading_fixture_record(**values: object) -> ComponentLoadingFixtureRecord:
    body = dict(values)
    body["schema_version"] = LOADING_SCHEMA_VERSION
    return ComponentLoadingFixtureRecord(
        fixture_id=stable_record_id("component_loading_fixture", body),
        **body,
    )


def build_component_interface_contract(
    *,
    slice_ref: str,
    component_registration_id: str,
    package_name: str,
    package_digest: str,
    file_count: int,
    accepted_scope: str,
    expected_exports: tuple[str, ...],
    export_digest: str,
) -> ComponentInterfaceContract:
    body = {
        "slice_ref": slice_ref,
        "component_registration_id": component_registration_id,
        "package_name": package_name,
        "package_digest": package_digest,
        "file_count": file_count,
        "accepted_scope": accepted_scope,
        "expected_exports": expected_exports,
        "export_count": len(expected_exports),
        "export_digest": export_digest,
        "static_import_required": True,
        "component_invocation_allowed": False,
        "verifier_invocation_allowed": False,
        "runtime_authority_allowed": False,
        "schema_version": LOADING_SCHEMA_VERSION,
    }
    return ComponentInterfaceContract(
        interface_contract_id=stable_record_id("component_interface", body),
        **body,
    )


def build_loaded_component_record(
    *,
    contract: ComponentInterfaceContract,
    module_name: str,
    load_order: int,
) -> LoadedComponentRecord:
    body = {
        "interface_contract_id": contract.interface_contract_id,
        "component_registration_id": contract.component_registration_id,
        "package_name": contract.package_name,
        "module_name": module_name,
        "load_order": load_order,
        "export_count": contract.export_count,
        "export_digest": contract.export_digest,
        "module_loaded": True,
        "interface_verified": True,
        "component_invoked": False,
        "verifier_invoked": False,
        "runtime_authority_granted": False,
        "persistent_side_effect_performed": False,
        "schema_version": LOADING_SCHEMA_VERSION,
    }
    return LoadedComponentRecord(
        loaded_component_id=stable_record_id("loaded_component", body),
        **body,
    )


def build_component_loading_result(
    *,
    fixture_id: str,
    loading_state_id: str,
    status: str,
    reason_code: str,
    slice31_result_id: str = "",
    bootstrap_boundary_id: str = "",
    component_registry_id: str = "",
    loaded_components: tuple[LoadedComponentRecord, ...] = (),
    accepted_component_count: int = 15,
    failed_package_name: str = "",
    unregistered_project_roots: tuple[str, ...] = (),
) -> ComponentLoadingResult:
    body = {
        "fixture_id": fixture_id,
        "loading_state_id": loading_state_id,
        "slice31_result_id": slice31_result_id,
        "bootstrap_boundary_id": bootstrap_boundary_id,
        "component_registry_id": component_registry_id,
        "status": status,
        "reason_code": reason_code,
        "loaded_components": loaded_components,
        "loaded_component_count": len(loaded_components),
        "accepted_component_count": accepted_component_count,
        "failed_package_name": failed_package_name,
        "unregistered_project_roots": unregistered_project_roots,
        "deterministic": True,
        "fixture_only": True,
        "offline_only": True,
        "static_allowlist_only": True,
        "dynamic_discovery_performed": False,
        "hidden_fallback_used": False,
        "component_invocation_performed": False,
        "verifier_invocation_performed": False,
        "runtime_connection_performed": False,
        "network_access_performed": False,
        "external_data_filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "external_resource_used": False,
        "memory_write_performed": False,
        "evidence_mutation_performed": False,
        "delivery_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "gp014_imported": False,
        "gp014_called": False,
        "persistent_side_effect_performed": False,
        "schema_version": LOADING_SCHEMA_VERSION,
    }
    return ComponentLoadingResult(
        loading_result_id=stable_record_id("component_loading_result", body),
        **body,
    )


def _require_exact_value(
    *,
    field: str,
    actual: object,
    expected: object,
    issues: list[ValidationIssue],
    code: str = "accepted_identity_mismatch",
) -> None:
    if actual != expected:
        issues.append(issue(field, code))


def validate_component_loading_state(record: ComponentLoadingState) -> ValidationReport:
    issues: list[ValidationIssue] = []
    if record.schema_version != LOADING_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.activation_mode not in (
        MODE_DISABLED_DEFAULT,
        MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING,
    ):
        issues.append(issue("activation_mode", "unsupported_activation_mode"))
    if record.enabled != record.component_loading_authorized:
        issues.append(issue("component_loading_authorized", "state_mismatch"))
    if record.enabled and record.activation_mode != MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING:
        issues.append(issue("activation_mode", "enabled_mode_mismatch"))
    if not record.enabled and record.activation_mode != MODE_DISABLED_DEFAULT:
        issues.append(issue("activation_mode", "disabled_mode_mismatch"))
    for field in (
        "disabled_by_default",
        "fixture_only",
        "offline_only",
        "deterministic",
        "static_allowlist_only",
        "python_module_import_read_only",
    ):
        require_true(field=field, value=getattr(record, field), issues=issues)
    for field in _FALSE_ONLY_STATE_FIELDS:
        require_false(field=field, value=getattr(record, field), issues=issues)
    if record.loading_state_id != record.expected_id():
        issues.append(issue("loading_state_id", "stable_identifier_mismatch"))

    expected = build_component_loading_state(enabled=record.enabled)
    if record != expected:
        issues.append(issue("loading_state", "accepted_state_identity_mismatch"))
    expected_id = EXACT_ENABLED_STATE_ID if record.enabled else EXACT_DISABLED_STATE_ID
    _require_exact_value(
        field="loading_state_id",
        actual=record.loading_state_id,
        expected=expected_id,
        issues=issues,
        code="accepted_state_identifier_mismatch",
    )
    return ValidationReport(LOADING_SCHEMA_VERSION, not issues, tuple(issues))


def validate_component_loading_fixture_record(
    record: ComponentLoadingFixtureRecord,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field in (
        "fixture_name",
        "operation",
        "required_activation_mode",
        "required_slice31_fixture_name",
        "expected_result_status",
    ):
        require_non_empty_text(field=field, value=getattr(record, field), issues=issues)
    if record.schema_version != LOADING_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    _require_exact_value(
        field="fixture_name",
        actual=record.fixture_name,
        expected=EXACT_FIXTURE_NAME,
        issues=issues,
    )
    _require_exact_value(
        field="operation",
        actual=record.operation,
        expected=OPERATION_LOAD_ACCEPTED_COMPONENTS,
        issues=issues,
    )
    _require_exact_value(
        field="required_activation_mode",
        actual=record.required_activation_mode,
        expected=MODE_EXPLICIT_OFFLINE_COMPONENT_LOADING,
        issues=issues,
    )
    _require_exact_value(
        field="required_slice31_fixture_name",
        actual=record.required_slice31_fixture_name,
        expected=EXACT_SLICE31_FIXTURE_NAME,
        issues=issues,
    )
    _require_exact_value(
        field="expected_result_status",
        actual=record.expected_result_status,
        expected=STATUS_COMPLETED_STATIC_LOADING,
        issues=issues,
    )
    for field in (
        "synthetic",
        "forge_owned",
        "internal_only",
        "fixture_only",
        "offline_only",
        "runtime_prohibited",
    ):
        require_true(field=field, value=getattr(record, field), issues=issues)
    for field in (
        "evidence",
        "memory",
        "runtime_corpus",
        "production_data",
        "public_output",
        "external_resource_derived",
        "memory_derived",
        "trace_derived",
        "contains_real_personal_data",
        "contains_live_secret",
        "contains_executable_command",
        "contains_tool_invocation",
    ):
        require_false(field=field, value=getattr(record, field), issues=issues)
    if record.fixture_id != record.expected_id():
        issues.append(issue("fixture_id", "stable_identifier_mismatch"))
    _require_exact_value(
        field="fixture_id",
        actual=record.fixture_id,
        expected=EXACT_FIXTURE_ID,
        issues=issues,
        code="accepted_fixture_identifier_mismatch",
    )
    return ValidationReport(LOADING_SCHEMA_VERSION, not issues, tuple(issues))


def validate_component_interface_contract(
    record: ComponentInterfaceContract,
) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field in (
        "slice_ref",
        "component_registration_id",
        "package_name",
        "package_digest",
        "accepted_scope",
        "export_digest",
    ):
        require_non_empty_text(field=field, value=getattr(record, field), issues=issues)
    require_unique_text_tuple(
        field="expected_exports",
        value=record.expected_exports,
        issues=issues,
    )
    if record.schema_version != LOADING_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.file_count <= 0:
        issues.append(issue("file_count", "required_positive_integer"))
    if record.export_count != len(record.expected_exports):
        issues.append(issue("export_count", "export_count_mismatch"))
    if len(record.package_digest) != 64 or any(
        character not in "0123456789abcdef" for character in record.package_digest
    ):
        issues.append(issue("package_digest", "invalid_sha256"))
    if len(record.export_digest) != 64 or any(
        character not in "0123456789abcdef" for character in record.export_digest
    ):
        issues.append(issue("export_digest", "invalid_sha256"))
    require_true(
        field="static_import_required",
        value=record.static_import_required,
        issues=issues,
    )
    for field in (
        "component_invocation_allowed",
        "verifier_invocation_allowed",
        "runtime_authority_allowed",
    ):
        require_false(field=field, value=getattr(record, field), issues=issues)
    if record.interface_contract_id != record.expected_id():
        issues.append(issue("interface_contract_id", "stable_identifier_mismatch"))

    expected = _ACCEPTED_IDENTITY_BY_PACKAGE.get(record.package_name)
    if expected is None:
        issues.append(issue("package_name", "unaccepted_component_package"))
    else:
        exact_fields = (
            ("slice_ref", record.slice_ref, expected.slice_ref),
            (
                "component_registration_id",
                record.component_registration_id,
                expected.component_registration_id,
            ),
            ("package_digest", record.package_digest, expected.package_digest),
            ("file_count", record.file_count, expected.file_count),
            ("accepted_scope", record.accepted_scope, expected.accepted_scope),
            ("expected_exports", record.expected_exports, expected.expected_exports),
            ("export_count", record.export_count, expected.export_count),
            ("export_digest", record.export_digest, expected.export_digest),
            (
                "interface_contract_id",
                record.interface_contract_id,
                expected.interface_contract_id,
            ),
        )
        for field, actual, exact in exact_fields:
            _require_exact_value(
                field=field,
                actual=actual,
                expected=exact,
                issues=issues,
            )
    return ValidationReport(LOADING_SCHEMA_VERSION, not issues, tuple(issues))


def validate_loaded_component_record(record: LoadedComponentRecord) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field in (
        "interface_contract_id",
        "component_registration_id",
        "package_name",
        "module_name",
        "export_digest",
    ):
        require_non_empty_text(field=field, value=getattr(record, field), issues=issues)
    if record.schema_version != LOADING_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    if record.load_order <= 0:
        issues.append(issue("load_order", "required_positive_integer"))
    if record.export_count <= 0:
        issues.append(issue("export_count", "required_positive_integer"))
    for field in ("module_loaded", "interface_verified"):
        require_true(field=field, value=getattr(record, field), issues=issues)
    for field in (
        "component_invoked",
        "verifier_invoked",
        "runtime_authority_granted",
        "persistent_side_effect_performed",
    ):
        require_false(field=field, value=getattr(record, field), issues=issues)
    if record.package_name != record.module_name:
        issues.append(issue("module_name", "module_name_mismatch"))
    if record.loaded_component_id != record.expected_id():
        issues.append(issue("loaded_component_id", "stable_identifier_mismatch"))

    expected = _ACCEPTED_IDENTITY_BY_LOAD_ORDER.get(record.load_order)
    if expected is None:
        issues.append(issue("load_order", "unaccepted_component_load_order"))
    else:
        exact_fields = (
            (
                "interface_contract_id",
                record.interface_contract_id,
                expected.interface_contract_id,
            ),
            (
                "component_registration_id",
                record.component_registration_id,
                expected.component_registration_id,
            ),
            ("package_name", record.package_name, expected.package_name),
            ("module_name", record.module_name, expected.package_name),
            ("export_count", record.export_count, expected.export_count),
            ("export_digest", record.export_digest, expected.export_digest),
            (
                "loaded_component_id",
                record.loaded_component_id,
                expected.loaded_component_id,
            ),
        )
        for field, actual, exact in exact_fields:
            _require_exact_value(
                field=field,
                actual=actual,
                expected=exact,
                issues=issues,
            )
    return ValidationReport(LOADING_SCHEMA_VERSION, not issues, tuple(issues))


def validate_component_loading_result(record: ComponentLoadingResult) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for field in ("fixture_id", "loading_state_id", "status", "reason_code"):
        require_non_empty_text(field=field, value=getattr(record, field), issues=issues)
    if record.schema_version != LOADING_SCHEMA_VERSION:
        issues.append(issue("schema_version", "unsupported_schema_version"))
    supported_statuses = (
        STATUS_REFUSED_DISABLED,
        STATUS_HELD_INVALID_STATE,
        STATUS_HELD_INVALID_FIXTURE,
        STATUS_HELD_FIXTURE_NOT_ACCEPTED,
        STATUS_HELD_BOUNDARY_INSPECTION_FAILED,
        STATUS_HELD_PREEXISTING_UNREGISTERED_COMPONENT,
        STATUS_HELD_STATIC_IMPORT_FAILED,
        STATUS_HELD_INTERFACE_MISMATCH,
        STATUS_HELD_UNREGISTERED_COMPONENT,
        STATUS_COMPLETED_STATIC_LOADING,
    )
    if record.status not in supported_statuses:
        issues.append(issue("status", "unsupported_loading_status"))
    if record.loaded_component_count != len(record.loaded_components):
        issues.append(issue("loaded_component_count", "count_mismatch"))
    if record.accepted_component_count != 15:
        issues.append(issue("accepted_component_count", "accepted_count_mismatch"))
    for field in (
        "deterministic",
        "fixture_only",
        "offline_only",
        "static_allowlist_only",
    ):
        require_true(field=field, value=getattr(record, field), issues=issues)
    for field in _FALSE_ONLY_RESULT_FIELDS:
        require_false(field=field, value=getattr(record, field), issues=issues)
    require_unique_text_tuple(
        field="unregistered_project_roots",
        value=record.unregistered_project_roots,
        issues=issues,
        allow_empty=True,
    )
    for loaded in record.loaded_components:
        report = validate_loaded_component_record(loaded)
        for nested in report.issues:
            issues.append(
                issue(
                    f"loaded.{loaded.package_name}.{nested.field}",
                    nested.code,
                    nested.detail,
                )
            )

    if record.status == STATUS_COMPLETED_STATIC_LOADING:
        exact_fields = (
            ("fixture_id", record.fixture_id, EXACT_FIXTURE_ID),
            ("loading_state_id", record.loading_state_id, EXACT_ENABLED_STATE_ID),
            ("slice31_result_id", record.slice31_result_id, EXACT_SLICE31_RESULT_ID),
            (
                "bootstrap_boundary_id",
                record.bootstrap_boundary_id,
                EXACT_BOOTSTRAP_BOUNDARY_ID,
            ),
            (
                "component_registry_id",
                record.component_registry_id,
                EXACT_COMPONENT_REGISTRY_ID,
            ),
            ("reason_code", record.reason_code, EXACT_SUCCESS_REASON_CODE),
            ("loaded_component_count", record.loaded_component_count, 15),
            ("accepted_component_count", record.accepted_component_count, 15),
            ("failed_package_name", record.failed_package_name, ""),
            ("unregistered_project_roots", record.unregistered_project_roots, ()),
            ("loading_result_id", record.loading_result_id, EXACT_SUCCESS_RESULT_ID),
        )
        for field, actual, exact in exact_fields:
            _require_exact_value(
                field=field,
                actual=actual,
                expected=exact,
                issues=issues,
                code="accepted_success_identity_mismatch",
            )
        _require_exact_value(
            field="package_order",
            actual=tuple(item.package_name for item in record.loaded_components),
            expected=_EXACT_PACKAGE_ORDER,
            issues=issues,
            code="accepted_success_order_mismatch",
        )
        _require_exact_value(
            field="registration_order",
            actual=tuple(
                item.component_registration_id for item in record.loaded_components
            ),
            expected=_EXACT_REGISTRATION_ORDER,
            issues=issues,
            code="accepted_success_order_mismatch",
        )
        _require_exact_value(
            field="interface_contract_order",
            actual=tuple(item.interface_contract_id for item in record.loaded_components),
            expected=_EXACT_INTERFACE_CONTRACT_ORDER,
            issues=issues,
            code="accepted_success_order_mismatch",
        )
        _require_exact_value(
            field="loaded_component_order",
            actual=tuple(item.loaded_component_id for item in record.loaded_components),
            expected=_EXACT_LOADED_COMPONENT_ORDER,
            issues=issues,
            code="accepted_success_order_mismatch",
        )
    elif record.status == STATUS_REFUSED_DISABLED:
        exact_fields = (
            ("fixture_id", record.fixture_id, EXACT_FIXTURE_ID),
            ("loading_state_id", record.loading_state_id, EXACT_DISABLED_STATE_ID),
            ("slice31_result_id", record.slice31_result_id, ""),
            ("bootstrap_boundary_id", record.bootstrap_boundary_id, ""),
            ("component_registry_id", record.component_registry_id, ""),
            ("reason_code", record.reason_code, EXACT_DISABLED_REASON_CODE),
            ("loaded_components", record.loaded_components, ()),
            ("loaded_component_count", record.loaded_component_count, 0),
            ("accepted_component_count", record.accepted_component_count, 15),
            ("failed_package_name", record.failed_package_name, ""),
            ("unregistered_project_roots", record.unregistered_project_roots, ()),
            ("loading_result_id", record.loading_result_id, EXACT_DISABLED_RESULT_ID),
        )
        for field, actual, exact in exact_fields:
            _require_exact_value(
                field=field,
                actual=actual,
                expected=exact,
                issues=issues,
                code="accepted_disabled_identity_mismatch",
            )
    elif record.loaded_component_count or record.loaded_components:
        issues.append(
            issue("loaded_components", "noncompletion_must_not_claim_loaded_components")
        )

    if record.loading_result_id != record.expected_id():
        issues.append(issue("loading_result_id", "stable_identifier_mismatch"))
    return ValidationReport(LOADING_SCHEMA_VERSION, not issues, tuple(issues))
