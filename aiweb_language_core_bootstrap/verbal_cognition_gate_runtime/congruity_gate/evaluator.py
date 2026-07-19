"""Deterministic exact-authority Slice 40D congruity evaluator."""
from __future__ import annotations
from .identity import with_expected_finding_id, with_expected_result_identity
from .schema import *
from .validation import assert_valid_evaluation_input, assert_valid_result

def _finding(v, assertion, observation, kind):
    return with_expected_finding_id(CongruityFinding(
        finding_id="congruity_finding:placeholder", evaluation_input_ref=v.evaluation_input_id,
        assertion_ref=assertion.assertion_id if assertion else None,
        finding_kind=kind, assertion_kind=assertion.assertion_kind if assertion else None,
        authority_state=observation.authority_state if observation else CongruityAuthorityState.ADMITTED,
        compatibility_judgment=observation.compatibility_judgment if observation else CongruityCompatibilityJudgment.COMPATIBLE,
        supporting_refs=observation.supporting_refs if observation else (),
        conflict_refs=observation.conflict_refs if observation else (),
        trace_refs=observation.trace_refs if observation else v.trace_refs,
        provenance_refs=observation.provenance_refs if observation else v.provenance_refs,
        reason_refs=((f"congruity:{kind.value}",) + (assertion.assertion_source_refs if assertion else ("slice40d:all_assertions_compatible",)))
    ))

def evaluate_congruity(v:CongruityEvaluationInput)->CongruityGateResult:
    assert_valid_evaluation_input(v)
    obs={o.assertion_ref:o for o in v.observations}
    findings=[]; counts={k:0 for k in ("compatible","incompatible","ambiguous","unsupported","conflicted","indeterminate")}
    for a in v.assertions:
        o=obs[a.assertion_id]
        if o.authority_state is CongruityAuthorityState.ADMITTED:
            if o.compatibility_judgment is CongruityCompatibilityJudgment.COMPATIBLE:
                counts["compatible"]+=1; kind=CongruityFindingKind.COMPATIBLE_ASSERTION
            else:
                counts["incompatible"]+=1; kind=CongruityFindingKind.INCOMPATIBLE_ASSERTION
        elif o.authority_state is CongruityAuthorityState.AMBIGUOUS:
            counts["ambiguous"]+=1; kind=CongruityFindingKind.AMBIGUOUS_ASSERTION
        elif o.authority_state is CongruityAuthorityState.UNSUPPORTED:
            counts["unsupported"]+=1; kind=CongruityFindingKind.UNSUPPORTED_ASSERTION
        elif o.authority_state is CongruityAuthorityState.CONFLICTED:
            counts["conflicted"]+=1; kind=CongruityFindingKind.CONFLICTED_ASSERTION
        else:
            counts["indeterminate"]+=1; kind=CongruityFindingKind.INDETERMINATE_AUTHORITY_ABSENT
        findings.append(_finding(v,a,o,kind))
    if counts["conflicted"]: overall=CongruityOverallState.CONFLICTED
    elif counts["unsupported"]: overall=CongruityOverallState.UNSUPPORTED
    elif counts["ambiguous"]: overall=CongruityOverallState.AMBIGUOUS
    elif counts["indeterminate"]: overall=CongruityOverallState.INDETERMINATE
    elif counts["incompatible"]: overall=CongruityOverallState.INCOMPATIBLE
    else:
        overall=CongruityOverallState.COMPATIBLE
        findings.append(_finding(v,None,None,CongruityFindingKind.ALL_ASSERTIONS_COMPATIBLE))
    review=v.governance_bundle.review_record
    result=CongruityGateResult(
        result_id="congruity_result:placeholder", evaluation_input_ref=v.evaluation_input_id,
        review_record_id=review.review_record_id, gate_id=review.identity.gate_id,
        gate_profile_id=review.profile.profile_id, candidate_input_ref=v.candidate_input_ref,
        predicate_id=v.predicate_id,predicate_version=v.predicate_version,frame_id=v.frame_id,frame_version=v.frame_version,
        overall_state=overall,findings=tuple(findings),assertion_count=len(v.assertions),
        compatible_count=counts["compatible"],incompatible_count=counts["incompatible"],ambiguous_count=counts["ambiguous"],unsupported_count=counts["unsupported"],conflicted_count=counts["conflicted"],indeterminate_count=counts["indeterminate"],
        deterministic=True,exact_compatibility_authority_preserved=True,
        candidate_structure_mutated=False,frame_rewritten=False,role_reassigned=False,similarity_fallback_used=False,nearest_known_substitution_used=False,hidden_model_judgment_used=False,silent_repair_used=False,
        clarification_required_created=False,rejection_created=False,refusal_relevant_created=False,blocked_progression_created=False,composed_gate_outcome_created=False,candidate_disposition_created=False,selected_meaning_created=False,
        truth_determined=False,evidence_validated=False,permission_granted=False,execution_authorized=False,route_created=False,tool_invoked=False,action_performed=False,memory_accessed=False,rendered=False,delivered=False,external_resource_loaded=False,language_model_used=False,embedding_used=False,vector_used=False,rag_used=False,semantic_similarity_used=False,
        canonical_digest="0"*64)
    return assert_valid_result(with_expected_result_identity(result))
