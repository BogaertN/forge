#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import replace
import importlib, runpy, sys
from pathlib import Path

class Ledger:
    def __init__(self): self.count=0; self.failures=[]
    def check(self, condition, label):
        self.count += 1
        if condition is not True: self.failures.append(label)

def load_script(path: Path): return runpy.run_path(str(path))

def build_fixture(repo: Path):
    closeout_test=load_script(repo/'scripts/test_aiweb_slice41f_disabled_bootstrap_integration_and_slice41_closeout.py')
    integration, integration_input=closeout_test['build_exact_slice41e_input'](repo)
    closeout=importlib.import_module('aiweb_language_core_bootstrap.disabled_selected_meaning_closeout')
    fixture=closeout.list_selected_meaning_closeout_fixtures()[0]
    state=closeout.build_disabled_selected_meaning_closeout_state(explicit_offline_developer_enable=True)
    invocation=closeout.build_selected_meaning_closeout_invocation(fixture.fixture_name)
    result=closeout.run_disabled_selected_meaning_closeout(invocation, state=state, integration_input=integration_input)
    closeout.assert_valid_result(result)

    core=importlib.import_module('aiweb_language_core_bootstrap.outward_expression_runtime')
    gov=importlib.import_module('aiweb_language_core_bootstrap.outward_expression_runtime.governed_lifecycle')
    test42b=load_script(repo/'scripts/test_aiweb_slice42b_deterministic_validation_identity_versioning_lifecycle.py')
    aggregate=test42b['_fixture'](core, gov)
    package=result.integration_input.selected_meaning_package
    integ=result.integration_result
    source=core.SelectedMeaningExpressionSourceCustodyRecord(
        source_custody_id='pending', slice41e_integration_input_ref=result.integration_input.integration_input_id,
        slice41e_integration_result_ref=integ.result_id, slice41e_integration_receipt_ref=integ.receipt.receipt_id,
        source_manifest_ref=integ.source_manifest.manifest_id, successor_manifest_ref=integ.successor_manifest.manifest_id,
        selected_governed_meaning_ref=integ.integrated_selected_meaning_record.record_id,
        selected_candidate_ref=package.selected_candidate_record.record_id,
        selection_authority_reference_ref=integ.authority_reference_record.record_id,
        selection_eligibility_result_ref=package.eligibility_result_ref, selection_decision_ref=package.decision_record.decision_id,
        selection_trace_ref=package.selection_trace.trace_id, selection_receipt_ref=package.selection_receipt.receipt_id,
        content_proof_ref=package.content_proof.proof_id, slice41f_acceptance_record_ref=result.acceptance_record.record_id,
        preserved_alternative_refs=tuple(x.preservation_id for x in package.preserved_alternatives),
        unresolved_alternative_refs=package.unresolved_alternative_refs, ambiguity_ancestry_refs=package.ambiguity_ancestry_refs,
        clarification_ancestry_refs=package.clarification_ancestry_refs, inherited_limitation_refs=package.inherited_limitation_refs,
        blocked_consequence_refs=package.blocked_consequence_refs, refusal_relevant_refs=package.refusal_relevant_refs,
        authority_sensitive_distinction_refs=package.authority_sensitive_distinction_refs,
        preservation_class_refs=tuple(x.value for x in package.selected_meaning_record.preservation_classes),
    )
    source=gov.with_expected_id(source)
    old=aggregate
    authority=gov.with_expected_id(replace(old.outward_expression_authority_requirement,
        authority_requirement_id='pending', selected_meaning_source_custody_ref=source.source_custody_id,
        required_predecessor_receipt_refs=(source.slice41e_integration_receipt_ref, source.selection_receipt_ref)))
    obligations=gov.with_expected_id(replace(old.preservation_obligation_custody, obligation_custody_id='pending',
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=authority.authority_requirement_id,
        inherited_limitation_refs=source.inherited_limitation_refs,
        refusal_relevant_boundary_refs=source.refusal_relevant_refs,
        unresolved_condition_refs=source.unresolved_alternative_refs,
        ambiguity_refs=source.ambiguity_ancestry_refs, preservation_class_refs=source.preservation_class_refs))
    eligibility=gov.with_expected_id(replace(old.expression_eligibility_status, expression_eligibility_status_id='pending',
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=authority.authority_requirement_id,
        preservation_obligation_custody_ref=obligations.obligation_custody_id))
    outward=gov.with_expected_id(replace(old.governed_outward_meaning_boundary, governed_outward_meaning_boundary_id='pending',
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=authority.authority_requirement_id,
        expression_eligibility_status_ref=eligibility.expression_eligibility_status_id,
        preservation_obligation_custody_ref=obligations.obligation_custody_id,
        required_qualification_refs=obligations.required_caveat_refs,
        ancestry_refs=(source.selected_governed_meaning_ref,)))
    plan=gov.with_expected_id(replace(old.expression_plan_boundary, expression_plan_boundary_id='pending',
        governed_outward_meaning_boundary_ref=outward.governed_outward_meaning_boundary_id,
        preservation_obligation_custody_ref=obligations.obligation_custody_id,
        qualification_custody_refs=outward.required_qualification_refs,
        caveat_custody_refs=obligations.required_caveat_refs,
        refusal_custody_refs=obligations.refusal_relevant_boundary_refs,
        unresolved_custody_refs=obligations.unresolved_condition_refs, ancestry_refs=outward.ancestry_refs))
    realized=gov.with_expected_id(replace(old.realized_expression_boundary, realized_expression_boundary_id='pending',
        expression_plan_boundary_ref=plan.expression_plan_boundary_id,
        governed_outward_meaning_boundary_ref=outward.governed_outward_meaning_boundary_id,
        preservation_obligation_custody_ref=obligations.obligation_custody_id))
    trace=gov.with_expected_id(replace(old.expression_trace_boundary, expression_trace_boundary_id='pending',
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=authority.authority_requirement_id,
        preservation_obligation_custody_ref=obligations.obligation_custody_id,
        expression_eligibility_status_ref=eligibility.expression_eligibility_status_id,
        governed_outward_meaning_boundary_ref=outward.governed_outward_meaning_boundary_id,
        expression_plan_boundary_ref=plan.expression_plan_boundary_id,
        realized_expression_boundary_ref=realized.realized_expression_boundary_id,
        predecessor_trace_refs=(source.selection_trace_ref,),
        predecessor_receipt_refs=(source.slice41e_integration_receipt_ref, source.selection_receipt_ref)))
    receipt=gov.with_expected_id(replace(old.expression_receipt_boundary, expression_receipt_boundary_id='pending',
        selected_meaning_source_custody_ref=source.source_custody_id,
        outward_expression_authority_requirement_ref=authority.authority_requirement_id,
        expression_eligibility_status_ref=eligibility.expression_eligibility_status_id,
        governed_outward_meaning_boundary_ref=outward.governed_outward_meaning_boundary_id,
        expression_plan_boundary_ref=plan.expression_plan_boundary_id,
        realized_expression_boundary_ref=realized.realized_expression_boundary_id,
        expression_trace_boundary_ref=trace.expression_trace_boundary_id))
    aggregate=gov.with_expected_id(replace(old, outward_expression_runtime_schema_record_id='pending',
        selected_meaning_source_custody=source, outward_expression_authority_requirement=authority,
        preservation_obligation_custody=obligations, expression_eligibility_status=eligibility,
        governed_outward_meaning_boundary=outward, expression_plan_boundary=plan,
        realized_expression_boundary=realized, expression_trace_boundary=trace, expression_receipt_boundary=receipt))
    version=test42b['_version_custody'](gov, aggregate)
    lifecycle=test42b['_lifecycle'](gov, aggregate, version, gov.OutwardExpressionLifecycleStage.RECORD_SEALED,
        canonical_serialization_performed=True, deterministic_identity_validated=True,
        predecessor_references_validated=True, cross_record_consistency_validated=True)
    bundle=gov.OutwardExpressionGovernanceBundle(
        bundle_id='pending', bundle_digest='0'*64, runtime_schema_record=aggregate, version_custody=version,
        lifecycle_record=lifecycle, lifecycle_transitions=(), validation_only=True, immutable_successor_records=True,
        exact_predecessor_references_required=True, duplicate_and_collision_rejection_required=True,
        unknown_version_rejection_required=True, malformed_record_rejection_required=True,
        cross_record_consistency_required=True, structural_validity_grants_expression_authority=False,
        selected_meaning_chain_admitted=False, outward_expression_authority_admitted=False,
        expression_eligibility_evaluated=False, preservation_obligations_projected=False,
        governed_outward_meaning_created=False, expression_plan_created=False, expression_candidate_created=False,
        human_readable_text_produced=False, msm_v1_modified_or_integrated=False, echo_validation_performed=False,
        bootstrap_integration_enabled=False, delivered=False, truth_determined=False, evidence_validated=False,
        permission_granted=False, execution_authorized=False, route_or_api_created=False, tool_invoked=False,
        action_performed=False, memory_accessed_or_written=False, filesystem_or_network_accessed=False,
        external_resource_loaded=False, model_or_similarity_authority_used=False, gp014_superseded=False)
    bundle=gov.with_expected_bundle_identity(bundle); gov.assert_valid_governance_bundle(bundle)
    return result, source, authority, bundle

def main():
    repo=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve(); sys.path.insert(0,str(repo))
    pkg=importlib.import_module('aiweb_language_core_bootstrap.outward_expression_runtime.expression_eligibility')
    gov=importlib.import_module('aiweb_language_core_bootstrap.outward_expression_runtime.governed_lifecycle')
    ledger=Ledger(); closeout, source, requirement, bundle=build_fixture(repo)
    auth=pkg.with_expected_id(pkg.OutwardExpressionAuthorityRecord(
        authority_record_id='pending', authority_key=requirement.required_outward_expression_authority_ref,
        authority_version='v1.0.0', selected_meaning_source_custody_ref=source.source_custody_id,
        authority_requirement_ref=requirement.authority_requirement_id,
        authority_scope_refs=requirement.required_authority_scope_refs,
        expression_purpose_refs=requirement.required_expression_purpose_refs,
        predecessor_receipt_refs=requirement.required_predecessor_receipt_refs,
        version_refs=requirement.required_version_refs,
        disposition_authority_ref='authority-disposition:fixture:explicit',
        authority_receipt_ref='authority-receipt:fixture:explicit', authority_active=True,
        eligibility_evaluation_authorized=True, expression_planning_progression_authorized=True,
        preservation_obligation_projection_authorized=False, governed_outward_meaning_construction_authorized=False,
        expression_plan_construction_authorized=False, surface_realization_authorized=False,
        msm_v1_mutation_or_integration_authorized=False, echo_validation_authorized=False,
        delivery_authorized=False, truth_evidence_permission_execution_authorized=False,
        route_api_network_filesystem_memory_tool_action_authorized=False,
        external_resource_or_model_authority=False, gp014_supersession_authorized=False))
    value=pkg.with_expected_id(pkg.ExpressionEligibilityEvaluationInput(
        evaluation_input_id='pending', selected_meaning_closeout_result=closeout,
        selected_meaning_source_custody=source, outward_expression_authority_requirement=requirement,
        outward_expression_governance_bundle=bundle, outward_expression_authority_record=auth,
        evaluation_reason_refs=('slice42c:exact-evaluation',), trace_refs=(source.selection_trace_ref,),
        provenance_refs=(closeout.result_id,bundle.bundle_id), version_refs=(pkg.SLICE42C_SCHEMA_VERSION,),
        selected_meaning_alone_claimed_sufficient=False, authority_inference_requested=False,
        record_repair_requested=False, scope_expansion_requested=False, purpose_expansion_requested=False,
        refusal_softening_requested=False, unresolved_resolution_requested=False,
        blocked_consequence_erasure_requested=False, downstream_authority_requested=False))
    ledger.check(pkg.validate_evaluation_input(value).ok, 'valid exact input')
    result=pkg.evaluate_expression_eligibility(value)
    ledger.check(pkg.validate_result(result,evaluation_input=value).ok,'valid result')
    ledger.check(result.selected_meaning_chain_admitted,'chain admitted')
    ledger.check(result.outward_expression_authority_admitted,'authority admitted')
    ledger.check(not result.selected_meaning_alone_sufficient,'selected meaning alone insufficient')
    ledger.check(not result.structural_validity_grants_expression_authority,'structural validity insufficient')
    ledger.check(sum((result.eligible_for_expression_planning,result.held_pending_authority,result.blocked,result.refusal_preserving,result.unresolved_preserving,result.indeterminate))==1,'exclusive outcome')
    for name in ('preservation_obligations_projected','governed_outward_meaning_created','expression_plan_created','human_readable_text_produced','echo_validation_performed','delivered','tool_invoked','action_performed','memory_accessed_or_written','model_or_similarity_authority_used','gp014_superseded'):
        ledger.check(getattr(result,name) is False, f'zero downstream {name}')
    inactive=pkg.with_expected_id(replace(auth, authority_record_id='pending', authority_active=False, eligibility_evaluation_authorized=False, expression_planning_progression_authorized=False))
    held_input=pkg.with_expected_id(replace(value,evaluation_input_id='pending',outward_expression_authority_record=inactive))
    held=pkg.evaluate_expression_eligibility(held_input)
    ledger.check(held.outcome is pkg.ExpressionEligibilityOutcome.HELD_PENDING_AUTHORITY or held.blocked or held.refusal_preserving or held.unresolved_preserving,'selected meaning alone never permits')
    fabricated=gov.with_expected_id(replace(source,source_custody_id='pending',selected_candidate_ref='candidate:fabricated'))
    bad_input=pkg.with_expected_id(replace(value,evaluation_input_id='pending',selected_meaning_source_custody=fabricated))
    ledger.check(not pkg.validate_evaluation_input(bad_input).ok,'fabricated recomputed source rejected')
    wrong_auth=pkg.with_expected_id(replace(auth,authority_record_id='pending',authority_key='outward-authority:wrong'))
    bad_auth_input=pkg.with_expected_id(replace(value,evaluation_input_id='pending',outward_expression_authority_record=wrong_auth))
    ledger.check(not pkg.validate_evaluation_input(bad_auth_input).ok,'mismatched authority rejected')
    wrong_receipt=pkg.with_expected_id(replace(auth,authority_record_id='pending',predecessor_receipt_refs=('receipt:wrong',)))
    bad_receipt_input=pkg.with_expected_id(replace(value,evaluation_input_id='pending',outward_expression_authority_record=wrong_receipt))
    ledger.check(not pkg.validate_evaluation_input(bad_receipt_input).ok,'wrong receipt rejected')
    ledger.check(tuple(x.value for x in pkg.ExpressionEligibilityOutcome)==pkg.SLICE42C_OUTCOME_VALUES,'exact outcomes')
    print('AI.WEB SLICE 42C AUTHORIZED MEANING ADMISSION EXPRESSION ELIGIBILITY TEST')
    print(f'check_count={ledger.count}')
    print('result_outcome='+result.outcome.value)
    print('selected_meaning_alone_grants_expression_authority=0')
    print('structural_validity_grants_expression_authority=0')
    print('failure_count='+str(len(ledger.failures)))
    for failure in ledger.failures: print('FAIL: '+failure)
    if ledger.failures: print('AI.WEB SLICE 42C BEHAVIOR TEST: FAIL'); return 1
    print('AI.WEB SLICE 42C BEHAVIOR TEST: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
