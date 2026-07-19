#!/usr/bin/env python3
"""Behavior test for AI.Web Slice 40D congruity-gate runtime."""
from __future__ import annotations
import argparse
from dataclasses import FrozenInstanceError, replace
import importlib
from pathlib import Path
import runpy
import sys

CORE_PACKAGE="aiweb_language_core_bootstrap.verbal_cognition_gate_runtime"
GOV_PACKAGE=f"{CORE_PACKAGE}.governed_lifecycle"
PACKAGE=f"{CORE_PACKAGE}.congruity_gate"

class Ledger:
    def __init__(self): self.check_count=0; self.failures=[]; self.malformed_cases=0
    def check(self, condition, label):
        self.check_count+=1
        if condition is not True: self.failures.append(label)
    def malformed(self, condition, label): self.malformed_cases+=1; self.check(condition,label)

def make_profile(module,bundle):
    return module.with_expected_profile_id(module.CongruityGateRuntimeProfile(
        profile_id="congruity_profile:placeholder", profile_key="congruity_exact_admitted_compatibility",
        profile_version="v1.0.0", gate_profile_ref=bundle.review_record.profile.profile_id,
        gate_profile_version=bundle.review_record.profile.profile_version,
        governing_authority_refs=("canonical_roadmap:slice40d","document6:congruity_gate:v1","document4:concept_lexicon:v1","document5:predicate_role_frame_registry:v1"),
        permitted_assertion_kinds=tuple(module.CongruityAssertionKind), exact_admitted_assertions_only=True,
        raw_text_inspection_allowed=False, similarity_fallback_allowed=False, nearest_known_substitution_allowed=False,
        hidden_model_judgment_allowed=False, silent_repair_allowed=False, frame_rewrite_allowed=False,
        role_reassignment_allowed=False, capability_driven_selection_allowed=False, gate_composition_allowed=False,
        selected_meaning_allowed=False, route_tool_action_allowed=False))

def make_assertion(module,bundle,kind,key):
    return module.with_expected_assertion_id(module.CongruityAssertion(
        assertion_id="congruity_assertion:placeholder",
        candidate_input_ref=bundle.review_record.candidate_input.candidate_input_ref_id,
        predicate_id="predicate:inspect:v1", predicate_version="v1.0.0",
        frame_id="predicate_frame:inspect_target:v1", frame_version="v1.0.0",
        assertion_key=key, assertion_kind=kind,
        subject_refs=(f"candidate_subject:{key}",), object_refs=(f"candidate_object:{key}",),
        relation_refs=(f"candidate_relation:{key}",),
        assertion_source_refs=(f"slice38:compatibility:{key}",f"document6:congruity:{key}"),
        authority_refs=("document4:concept_authority:v1","document5:predicate_role_authority:v1"),
        required=True, exact_admitted_assertion=True))

def make_observation(module,bundle,assertion,*,authority=None,judgment=None):
    authority=authority or module.CongruityAuthorityState.ADMITTED
    if judgment is None:
        judgment=(module.CongruityCompatibilityJudgment.COMPATIBLE if authority is module.CongruityAuthorityState.ADMITTED else module.CongruityCompatibilityJudgment.NOT_EVALUATED)
    return module.with_expected_observation_id(module.CongruityObservation(
        observation_id="congruity_observation:placeholder", assertion_ref=assertion.assertion_id,
        candidate_input_ref=bundle.review_record.candidate_input.candidate_input_ref_id,
        authority_state=authority, compatibility_judgment=judgment,
        supporting_refs=((f"support:{assertion.assertion_key}",) if judgment is module.CongruityCompatibilityJudgment.COMPATIBLE else ()),
        conflict_refs=((f"conflict:{assertion.assertion_key}",) if judgment is module.CongruityCompatibilityJudgment.INCOMPATIBLE or authority is module.CongruityAuthorityState.CONFLICTED else ()),
        trace_refs=(f"congruity_trace:{assertion.assertion_key}",),
        provenance_refs=(f"congruity_provenance:{assertion.assertion_key}",)))

def make_input(module,bundle,assertions,observations,**changes):
    value=module.CongruityEvaluationInput(
        evaluation_input_id="congruity_evaluation_input:placeholder", governance_bundle=bundle,
        runtime_profile=make_profile(module,bundle), candidate_input_ref=bundle.review_record.candidate_input.candidate_input_ref_id,
        predicate_id="predicate:inspect:v1", predicate_version="v1.0.0", frame_id="predicate_frame:inspect_target:v1", frame_version="v1.0.0",
        assertions=tuple(assertions), observations=tuple(observations),
        trace_refs=("slice39h:candidate_trace","slice40b:sealed_governance_trace","slice40c:expectancy_trace"),
        provenance_refs=("slice39h:candidate_provenance","slice40b:governance_provenance"),
        limitation_refs=("slice40d:no_composition_no_selection",),
        raw_text_supplied=False, similarity_fallback_used=False, nearest_known_substitution_used=False,
        hidden_model_judgment_used=False, silent_repair_used=False, frame_rewritten=False,
        role_reassigned=False, capability_driven_selection_used=False)
    if changes: value=replace(value,**changes)
    return module.with_expected_evaluation_input_id(value)

def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("repository",nargs="?",default="."); args=parser.parse_args()
    repository=Path(args.repository).resolve(); sys.path.insert(0,str(repository))
    core=importlib.import_module(CORE_PACKAGE); gov=importlib.import_module(GOV_PACKAGE); module=importlib.import_module(PACKAGE)
    make_bundle=runpy.run_path(str(repository/"scripts/test_aiweb_slice40b_deterministic_validation_identity_versioning_lifecycle.py"))["make_bundle"]
    ledger=Ledger(); bundle=make_bundle(core,gov,core.VerbalCognitionGateFamily.CONGRUITY)
    assertions=tuple(make_assertion(module,bundle,k,k.value) for k in module.CongruityAssertionKind)
    observations=tuple(make_observation(module,bundle,a) for a in assertions)
    valid_input=make_input(module,bundle,assertions,observations); original=valid_input
    result=module.evaluate_congruity(valid_input)

    ledger.check(module.SLICE40D_ACCEPTED_PARENT_HEAD=="e803ad8870c542298e878a04b6b6d39b94e25dbe","parent head")
    ledger.check(module.SLICE40D_ACCEPTED_PARENT_TREE=="df6cf2f9e862c466abebfb0bd23a1d6d59748e48","parent tree")
    ledger.check(module.validate_evaluation_input(valid_input).ok,"valid input")
    ledger.check(module.validate_result(result).ok,"valid result")
    ledger.check(valid_input==original,"input unchanged")
    ledger.check(result.overall_state is module.CongruityOverallState.COMPATIBLE,"compatible overall")
    ledger.check(result.assertion_count==14,"assertion count")
    ledger.check(result.compatible_count==14,"compatible count")
    ledger.check(result.incompatible_count==0,"incompatible zero")
    ledger.check(module.CongruityFindingKind.ALL_ASSERTIONS_COMPATIBLE in tuple(f.finding_kind for f in result.findings),"all compatible finding")
    ledger.check(result==module.evaluate_congruity(valid_input),"deterministic repeat")
    for _ in range(20): ledger.check(module.evaluate_congruity(valid_input)==result,"repeat determinism")

    for index,assertion in enumerate(assertions):
        altered=list(observations); altered[index]=make_observation(module,bundle,assertion,judgment=module.CongruityCompatibilityJudgment.INCOMPATIBLE)
        item=module.evaluate_congruity(make_input(module,bundle,assertions,altered))
        ledger.check(item.overall_state is module.CongruityOverallState.INCOMPATIBLE,f"{assertion.assertion_kind.value} incompatible")
        ledger.check(item.incompatible_count==1,f"{assertion.assertion_kind.value} count")
        exact=[f for f in item.findings if f.assertion_ref==assertion.assertion_id]
        ledger.check(len(exact)==1 and exact[0].finding_kind is module.CongruityFindingKind.INCOMPATIBLE_ASSERTION,f"{assertion.assertion_kind.value} exact finding")
        ledger.check(not item.rejection_created,f"{assertion.assertion_kind.value} no automatic rejection")

    state_cases=(
        (module.CongruityAuthorityState.AMBIGUOUS,module.CongruityOverallState.AMBIGUOUS,module.CongruityFindingKind.AMBIGUOUS_ASSERTION),
        (module.CongruityAuthorityState.UNSUPPORTED,module.CongruityOverallState.UNSUPPORTED,module.CongruityFindingKind.UNSUPPORTED_ASSERTION),
        (module.CongruityAuthorityState.CONFLICTED,module.CongruityOverallState.CONFLICTED,module.CongruityFindingKind.CONFLICTED_ASSERTION),
        (module.CongruityAuthorityState.ABSENT,module.CongruityOverallState.INDETERMINATE,module.CongruityFindingKind.INDETERMINATE_AUTHORITY_ABSENT),)
    for state,overall,finding in state_cases:
        altered=list(observations); altered[0]=make_observation(module,bundle,assertions[0],authority=state)
        item=module.evaluate_congruity(make_input(module,bundle,assertions,altered))
        ledger.check(item.overall_state is overall,f"{state.value} overall")
        ledger.check(finding in tuple(f.finding_kind for f in item.findings),f"{state.value} finding")
        ledger.check(not item.clarification_required_created and not item.candidate_disposition_created,f"{state.value} no disposition")

    role_index=tuple(module.CongruityAssertionKind).index(module.CongruityAssertionKind.PARTICIPANT_ROLE)
    altered=list(observations); altered[role_index]=make_observation(module,bundle,assertions[role_index],judgment=module.CongruityCompatibilityJudgment.INCOMPATIBLE)
    role_result=module.evaluate_congruity(make_input(module,bundle,assertions,altered))
    ledger.check(role_result.overall_state is module.CongruityOverallState.INCOMPATIBLE,"role incompatible not missing")
    ledger.check(not role_result.clarification_required_created,"role incompatible no clarification")

    def rejected(call,label):
        try: call()
        except module.CongruityValidationError: ledger.malformed(True,label)
        except Exception: ledger.malformed(False,label+" wrong exception")
        else: ledger.malformed(False,label+" accepted")

    for flag in ("raw_text_inspection_allowed","similarity_fallback_allowed","nearest_known_substitution_allowed","hidden_model_judgment_allowed","silent_repair_allowed","frame_rewrite_allowed","role_reassignment_allowed","capability_driven_selection_allowed","gate_composition_allowed","selected_meaning_allowed","route_tool_action_allowed"):
        bad=replace(valid_input.runtime_profile,**{flag:True}); bad=module.with_expected_profile_id(bad)
        rejected(lambda bad=bad: module.assert_valid_evaluation_input(module.with_expected_evaluation_input_id(replace(valid_input,runtime_profile=bad))),f"profile {flag}")
    for flag in ("raw_text_supplied","similarity_fallback_used","nearest_known_substitution_used","hidden_model_judgment_used","silent_repair_used","frame_rewritten","role_reassigned","capability_driven_selection_used"):
        rejected(lambda flag=flag: module.assert_valid_evaluation_input(make_input(module,bundle,assertions,observations,**{flag:True})),f"input {flag}")
    rejected(lambda: module.assert_valid_evaluation_input(replace(valid_input,evaluation_input_id="bad id")),"bad input id")
    rejected(lambda: module.assert_valid_evaluation_input(module.with_expected_evaluation_input_id(replace(valid_input,predicate_version="v9"))),"unknown predicate version")
    rejected(lambda: module.assert_valid_evaluation_input(module.with_expected_evaluation_input_id(replace(valid_input,assertions=assertions+(assertions[0],)))),"duplicate assertion")
    rejected(lambda: module.assert_valid_evaluation_input(module.with_expected_evaluation_input_id(replace(valid_input,observations=observations[:-1]))),"missing observation")
    rejected(lambda: module.assert_valid_evaluation_input(module.with_expected_evaluation_input_id(replace(valid_input,observations=observations+(observations[0],)))),"duplicate observation")
    bad_assert=module.with_expected_assertion_id(replace(assertions[0],exact_admitted_assertion=False))
    rejected(lambda: module.assert_valid_evaluation_input(make_input(module,bundle,(bad_assert,*assertions[1:]),observations)),"non exact assertion")
    bad_obs=module.with_expected_observation_id(replace(observations[0],authority_state=module.CongruityAuthorityState.ABSENT,compatibility_judgment=module.CongruityCompatibilityJudgment.COMPATIBLE))
    rejected(lambda: module.assert_valid_evaluation_input(make_input(module,bundle,assertions,(bad_obs,*observations[1:]))),"absent authority judgment")
    expectancy_bundle=make_bundle(core,gov,core.VerbalCognitionGateFamily.EXPECTANCY)
    rejected(lambda: module.assert_valid_evaluation_input(make_input(module,expectancy_bundle,assertions,observations)),"wrong gate family")
    unsealed=replace(bundle,validation_complete=False)
    rejected(lambda: module.assert_valid_evaluation_input(make_input(module,unsealed,assertions,observations)),"unsealed governance")
    for flag in ("candidate_structure_mutated","frame_rewritten","role_reassigned","similarity_fallback_used","nearest_known_substitution_used","hidden_model_judgment_used","silent_repair_used","clarification_required_created","rejection_created","composed_gate_outcome_created","candidate_disposition_created","selected_meaning_created","truth_determined","permission_granted","route_created","tool_invoked","action_performed","memory_accessed","rendered","delivered","language_model_used","embedding_used","vector_used","rag_used","semantic_similarity_used"):
        rejected(lambda flag=flag: module.assert_valid_result(module.with_expected_result_identity(replace(result,**{flag:True},canonical_digest="0"*64,result_id="congruity_result:placeholder"))),f"result {flag}")
    rejected(lambda: module.assert_valid_result(replace(result,compatible_count=13)),"count mismatch")
    rejected(lambda: module.assert_valid_result(module.with_expected_result_identity(replace(result,overall_state=module.CongruityOverallState.INCOMPATIBLE,canonical_digest="0"*64,result_id="congruity_result:placeholder"))),"overall state mismatch")
    rejected(lambda: module.assert_valid_result(module.with_expected_result_identity(replace(result,findings=result.findings[:-1],canonical_digest="0"*64,result_id="congruity_result:placeholder"))),"summary finding missing")
    rejected(lambda: module.assert_valid_result(replace(result,canonical_digest="f"*64)),"digest mismatch")

    try:
        result.overall_state=module.CongruityOverallState.INCOMPATIBLE
        ledger.check(False,"frozen result")
    except FrozenInstanceError: ledger.check(True,"frozen result")

    zero_flags=(result.candidate_structure_mutated,result.frame_rewritten,result.role_reassigned,result.similarity_fallback_used,result.nearest_known_substitution_used,result.hidden_model_judgment_used,result.silent_repair_used,result.clarification_required_created,result.rejection_created,result.composed_gate_outcome_created,result.candidate_disposition_created,result.selected_meaning_created,result.truth_determined,result.evidence_validated,result.permission_granted,result.execution_authorized,result.route_created,result.tool_invoked,result.action_performed,result.memory_accessed,result.rendered,result.delivered)
    ledger.check(not any(zero_flags),"all downstream zero")

    print("AI.WEB SLICE 40D CONGRUITY GATE BEHAVIOR TEST")
    print(f"check_count={ledger.check_count}")
    print(f"malformed_validation_cases={ledger.malformed_cases}")
    print(f"assertion_kinds={len(module.CongruityAssertionKind)}")
    print(f"finding_kinds={len(module.CongruityFindingKind)}")
    print(f"overall_states={len(module.CongruityOverallState)}")
    print("congruity_evaluator_installed=1")
    print("compatible_result=1")
    print("incompatible_result=1")
    print("ambiguous_result=1")
    print("unsupported_result=1")
    print("conflicted_result=1")
    print("indeterminate_result=1")
    print("role_incompatibility_not_missing=1")
    print("exact_compatibility_authority=1")
    print("candidate_structure_mutated=0")
    print("similarity_fallback_used=0")
    print("nearest_known_substitution_used=0")
    print("hidden_model_judgment_used=0")
    print("silent_repair_used=0")
    print("frame_rewritten=0")
    print("role_reassigned=0")
    print("clarification_required_created=0")
    print("rejection_created=0")
    print("composed_gate_outcome_created=0")
    print("candidate_disposition_created=0")
    print("selected_meaning_created=0")
    print("truth_evidence_permission_execution=0")
    print("route_tool_action_memory_rendering_delivery=0")
    print(f"failure_count={len(ledger.failures)}")
    for f in ledger.failures: print(f"FAIL: {f}")
    if ledger.failures:
        print("AI.WEB SLICE 40D CONGRUITY GATE BEHAVIOR TEST: FAIL"); return 1
    print("AI.WEB SLICE 40D CONGRUITY GATE BEHAVIOR TEST: PASS"); return 0

if __name__=="__main__": raise SystemExit(main())
