"""Fail-closed validation for Slice 40D congruity evaluation."""
from __future__ import annotations
import re
from typing import Iterable
from ..governed_lifecycle import GateLifecycleStage, validate_governance_bundle
from ..schema import VerbalCognitionGateFamily
from ..predicate_frame_version_custody import invalid_predicate_frame_version_fields
from .identity import expected_result_digest, with_expected_assertion_id, with_expected_evaluation_input_id, with_expected_finding_id, with_expected_observation_id, with_expected_profile_id
from .schema import *

_IDENTIFIER=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
_SHA256=re.compile(r"^[0-9a-f]{64}$")

def _i(path,code,detail): return CongruityValidationIssue(path,code,detail)
def _ordered(items:Iterable[CongruityValidationIssue]): return CongruityValidationReport(tuple(sorted(items,key=lambda x:(x.path,x.code.value,x.detail))))
def _text(value,path,issues):
    if not isinstance(value,str) or not value or _IDENTIFIER.fullmatch(value) is None: issues.append(_i(path,CongruityValidationCode.INVALID_IDENTIFIER,"controlled identifier required"))
def _tuple(value,path,issues,allow_empty=True):
    if not isinstance(value,tuple) or (not allow_empty and not value): issues.append(_i(path,CongruityValidationCode.TYPE_MISMATCH,"tuple of identifiers required")); return
    if len(set(value))!=len(value): issues.append(_i(path,CongruityValidationCode.DUPLICATE_ID,"duplicate tuple value"))
    for n,v in enumerate(value): _text(v,f"{path}[{n}]",issues)
def _id(actual,expected,field,path,issues):
    if getattr(actual,field)!=getattr(expected,field): issues.append(_i(path,CongruityValidationCode.IDENTITY_MISMATCH,"deterministic identity mismatch"))

def validate_profile(value:object)->CongruityValidationReport:
    q=[]
    if not isinstance(value,CongruityGateRuntimeProfile): return _ordered((_i("profile",CongruityValidationCode.TYPE_MISMATCH,"CongruityGateRuntimeProfile required"),))
    for n in ("profile_id","profile_key","gate_profile_ref"): _text(getattr(value,n),f"profile.{n}",q)
    if value.profile_version!=SLICE40D_PROFILE_VERSION or value.gate_profile_version!="v1.0.0": q.append(_i("profile.profile_version",CongruityValidationCode.INVALID_VERSION,"only v1.0.0 admitted"))
    if value.schema_version!=SLICE40D_SCHEMA_VERSION: q.append(_i("profile.schema_version",CongruityValidationCode.INVALID_VERSION,"Slice 40D schema required"))
    _tuple(value.governing_authority_refs,"profile.governing_authority_refs",q,False)
    if value.permitted_assertion_kinds!=tuple(CongruityAssertionKind): q.append(_i("profile.permitted_assertion_kinds",CongruityValidationCode.CROSS_RECORD_MISMATCH,"all and only Slice 40D assertion kinds required"))
    if value.exact_admitted_assertions_only is not True: q.append(_i("profile.exact_admitted_assertions_only",CongruityValidationCode.NON_EXACT_COMPATIBILITY_PROHIBITED,"must be true"))
    for n in ("raw_text_inspection_allowed","similarity_fallback_allowed","nearest_known_substitution_allowed","hidden_model_judgment_allowed","silent_repair_allowed","frame_rewrite_allowed","role_reassignment_allowed","capability_driven_selection_allowed","gate_composition_allowed","selected_meaning_allowed","route_tool_action_allowed"):
        if getattr(value,n) is not False: q.append(_i(f"profile.{n}",CongruityValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,"must be false"))
    _id(value,with_expected_profile_id(value),"profile_id","profile.profile_id",q)
    return _ordered(q)

def validate_assertion(value:object)->CongruityValidationReport:
    q=[]
    if not isinstance(value,CongruityAssertion): return _ordered((_i("assertion",CongruityValidationCode.TYPE_MISMATCH,"CongruityAssertion required"),))
    for n in ("assertion_id","candidate_input_ref","predicate_id","frame_id","assertion_key"): _text(getattr(value,n),f"assertion.{n}",q)
    for n in invalid_predicate_frame_version_fields(
        predicate_id=value.predicate_id,
        predicate_version=value.predicate_version,
        frame_id=value.frame_id,
        frame_version=value.frame_version,
    ):
        q.append(
            _i(
                f"assertion.{n}",
                CongruityValidationCode.INVALID_VERSION,
                "exact legacy or registry-custodied predicate/frame version required",
            )
        )
    if not isinstance(value.assertion_kind,CongruityAssertionKind): q.append(_i("assertion.assertion_kind",CongruityValidationCode.TYPE_MISMATCH,"CongruityAssertionKind required"))
    for n in ("subject_refs","object_refs","relation_refs","assertion_source_refs","authority_refs"): _tuple(getattr(value,n),f"assertion.{n}",q,n in ("object_refs","relation_refs"))
    if type(value.required) is not bool: q.append(_i("assertion.required",CongruityValidationCode.TYPE_MISMATCH,"bool required"))
    if value.exact_admitted_assertion is not True: q.append(_i("assertion.exact_admitted_assertion",CongruityValidationCode.NON_EXACT_COMPATIBILITY_PROHIBITED,"must be true"))
    if value.schema_version!=SLICE40D_SCHEMA_VERSION: q.append(_i("assertion.schema_version",CongruityValidationCode.INVALID_VERSION,"Slice 40D schema required"))
    _id(value,with_expected_assertion_id(value),"assertion_id","assertion.assertion_id",q)
    return _ordered(q)

def validate_observation(value:object)->CongruityValidationReport:
    q=[]
    if not isinstance(value,CongruityObservation): return _ordered((_i("observation",CongruityValidationCode.TYPE_MISMATCH,"CongruityObservation required"),))
    for n in ("observation_id","assertion_ref","candidate_input_ref"): _text(getattr(value,n),f"observation.{n}",q)
    if not isinstance(value.authority_state,CongruityAuthorityState): q.append(_i("observation.authority_state",CongruityValidationCode.AUTHORITY_STATE_INVALID,"CongruityAuthorityState required"))
    if not isinstance(value.compatibility_judgment,CongruityCompatibilityJudgment): q.append(_i("observation.compatibility_judgment",CongruityValidationCode.JUDGMENT_INVALID,"CongruityCompatibilityJudgment required"))
    if isinstance(value.authority_state,CongruityAuthorityState) and isinstance(value.compatibility_judgment,CongruityCompatibilityJudgment):
        if value.authority_state is CongruityAuthorityState.ADMITTED and value.compatibility_judgment is CongruityCompatibilityJudgment.NOT_EVALUATED: q.append(_i("observation.compatibility_judgment",CongruityValidationCode.JUDGMENT_INVALID,"admitted authority requires exact judgment"))
        if value.authority_state is not CongruityAuthorityState.ADMITTED and value.compatibility_judgment is not CongruityCompatibilityJudgment.NOT_EVALUATED: q.append(_i("observation.compatibility_judgment",CongruityValidationCode.JUDGMENT_INVALID,"non-admitted authority cannot carry judgment"))
    for n in ("supporting_refs","conflict_refs","trace_refs","provenance_refs"): _tuple(getattr(value,n),f"observation.{n}",q,n in ("supporting_refs","conflict_refs"))
    if value.schema_version!=SLICE40D_SCHEMA_VERSION: q.append(_i("observation.schema_version",CongruityValidationCode.INVALID_VERSION,"Slice 40D schema required"))
    _id(value,with_expected_observation_id(value),"observation_id","observation.observation_id",q)
    return _ordered(q)

def validate_evaluation_input(value:object)->CongruityValidationReport:
    q=[]
    if not isinstance(value,CongruityEvaluationInput): return _ordered((_i("evaluation_input",CongruityValidationCode.TYPE_MISMATCH,"CongruityEvaluationInput required"),))
    for n in ("evaluation_input_id","candidate_input_ref","predicate_id","frame_id"): _text(getattr(value,n),f"evaluation_input.{n}",q)
    for n in invalid_predicate_frame_version_fields(
        predicate_id=value.predicate_id,
        predicate_version=value.predicate_version,
        frame_id=value.frame_id,
        frame_version=value.frame_version,
    ):
        q.append(
            _i(
                f"evaluation_input.{n}",
                CongruityValidationCode.INVALID_VERSION,
                "exact legacy or registry-custodied predicate/frame version required",
            )
        )
    governance=validate_governance_bundle(value.governance_bundle)
    if not governance.ok: q.append(_i("evaluation_input.governance_bundle",CongruityValidationCode.GOVERNANCE_INVALID,"governance bundle invalid"))
    try:
        review=value.governance_bundle.review_record
        if review.identity.gate_family is not VerbalCognitionGateFamily.CONGRUITY: q.append(_i("evaluation_input.governance_bundle.review_record.identity.gate_family",CongruityValidationCode.CONGRUITY_FAMILY_REQUIRED,"congruity family required"))
        if not value.governance_bundle.validation_complete or not any(r.stage is GateLifecycleStage.RECORD_SEALED for r in value.governance_bundle.lifecycle_records): q.append(_i("evaluation_input.governance_bundle",CongruityValidationCode.SEALED_GOVERNANCE_REQUIRED,"sealed governance required"))
        if review.candidate_input.candidate_input_ref_id!=value.candidate_input_ref: q.append(_i("evaluation_input.candidate_input_ref",CongruityValidationCode.CROSS_RECORD_MISMATCH,"candidate reference mismatch"))
        if review.profile.profile_id!=value.runtime_profile.gate_profile_ref or review.profile.profile_version!=value.runtime_profile.gate_profile_version: q.append(_i("evaluation_input.runtime_profile",CongruityValidationCode.CROSS_RECORD_MISMATCH,"gate profile mismatch"))
    except Exception: q.append(_i("evaluation_input.governance_bundle",CongruityValidationCode.TYPE_MISMATCH,"governance shape required"))
    q.extend(validate_profile(value.runtime_profile).issues)
    if not isinstance(value.assertions,tuple) or not value.assertions: q.append(_i("evaluation_input.assertions",CongruityValidationCode.TYPE_MISMATCH,"non-empty tuple required"))
    if not isinstance(value.observations,tuple) or not value.observations: q.append(_i("evaluation_input.observations",CongruityValidationCode.TYPE_MISMATCH,"non-empty tuple required"))
    assertion_ids=[]; observation_refs=[]
    if isinstance(value.assertions,tuple):
        for n,a in enumerate(value.assertions):
            q.extend(validate_assertion(a).issues)
            if isinstance(a,CongruityAssertion):
                assertion_ids.append(a.assertion_id)
                for field in ("candidate_input_ref","predicate_id","predicate_version","frame_id","frame_version"):
                    if getattr(a,field)!=getattr(value,field): q.append(_i(f"evaluation_input.assertions[{n}].{field}",CongruityValidationCode.CROSS_RECORD_MISMATCH,"input mismatch"))
    if len(set(assertion_ids))!=len(assertion_ids): q.append(_i("evaluation_input.assertions",CongruityValidationCode.DUPLICATE_ID,"duplicate assertion"))
    if isinstance(value.observations,tuple):
        for n,o in enumerate(value.observations):
            q.extend(validate_observation(o).issues)
            if isinstance(o,CongruityObservation):
                observation_refs.append(o.assertion_ref)
                if o.candidate_input_ref!=value.candidate_input_ref: q.append(_i(f"evaluation_input.observations[{n}].candidate_input_ref",CongruityValidationCode.CROSS_RECORD_MISMATCH,"candidate mismatch"))
                if o.assertion_ref not in assertion_ids: q.append(_i(f"evaluation_input.observations[{n}].assertion_ref",CongruityValidationCode.REFERENCE_NOT_FOUND,"assertion not found"))
    if len(set(observation_refs))!=len(observation_refs): q.append(_i("evaluation_input.observations",CongruityValidationCode.DUPLICATE_ID,"duplicate observation assertion"))
    if set(observation_refs)!=set(assertion_ids): q.append(_i("evaluation_input.observations",CongruityValidationCode.COUNT_MISMATCH,"exactly one observation per assertion required"))
    for n in ("trace_refs","provenance_refs","limitation_refs"): _tuple(getattr(value,n),f"evaluation_input.{n}",q,False)
    for n in ("raw_text_supplied","similarity_fallback_used","nearest_known_substitution_used","hidden_model_judgment_used","silent_repair_used","frame_rewritten","role_reassigned","capability_driven_selection_used"):
        if getattr(value,n) is not False: q.append(_i(f"evaluation_input.{n}",CongruityValidationCode.REPAIR_PROHIBITED if n in ("silent_repair_used","frame_rewritten","role_reassigned") else CongruityValidationCode.NON_EXACT_COMPATIBILITY_PROHIBITED,"must be false"))
    if value.schema_version!=SLICE40D_SCHEMA_VERSION: q.append(_i("evaluation_input.schema_version",CongruityValidationCode.INVALID_VERSION,"Slice 40D schema required"))
    _id(value,with_expected_evaluation_input_id(value),"evaluation_input_id","evaluation_input.evaluation_input_id",q)
    return _ordered(q)

def validate_finding(value:object)->CongruityValidationReport:
    q=[]
    if not isinstance(value,CongruityFinding): return _ordered((_i("finding",CongruityValidationCode.TYPE_MISMATCH,"CongruityFinding required"),))
    for n in ("finding_id","evaluation_input_ref"): _text(getattr(value,n),f"finding.{n}",q)
    if value.assertion_ref is not None: _text(value.assertion_ref,"finding.assertion_ref",q)
    if not isinstance(value.finding_kind,CongruityFindingKind): q.append(_i("finding.finding_kind",CongruityValidationCode.TYPE_MISMATCH,"CongruityFindingKind required"))
    if value.assertion_kind is not None and not isinstance(value.assertion_kind,CongruityAssertionKind): q.append(_i("finding.assertion_kind",CongruityValidationCode.TYPE_MISMATCH,"CongruityAssertionKind required"))
    if not isinstance(value.authority_state,CongruityAuthorityState): q.append(_i("finding.authority_state",CongruityValidationCode.TYPE_MISMATCH,"CongruityAuthorityState required"))
    if not isinstance(value.compatibility_judgment,CongruityCompatibilityJudgment): q.append(_i("finding.compatibility_judgment",CongruityValidationCode.TYPE_MISMATCH,"CongruityCompatibilityJudgment required"))
    for n in ("supporting_refs","conflict_refs","trace_refs","provenance_refs","reason_refs"): _tuple(getattr(value,n),f"finding.{n}",q,n in ("supporting_refs","conflict_refs"))
    if value.schema_version!=SLICE40D_SCHEMA_VERSION: q.append(_i("finding.schema_version",CongruityValidationCode.INVALID_VERSION,"Slice 40D schema required"))
    _id(value,with_expected_finding_id(value),"finding_id","finding.finding_id",q)
    return _ordered(q)

def validate_result(value:object)->CongruityValidationReport:
    q=[]
    if not isinstance(value,CongruityGateResult): return _ordered((_i("result",CongruityValidationCode.TYPE_MISMATCH,"CongruityGateResult required"),))
    for n in ("result_id","evaluation_input_ref","review_record_id","gate_id","gate_profile_id","candidate_input_ref","predicate_id","frame_id"): _text(getattr(value,n),f"result.{n}",q)
    for n in invalid_predicate_frame_version_fields(
        predicate_id=value.predicate_id,
        predicate_version=value.predicate_version,
        frame_id=value.frame_id,
        frame_version=value.frame_version,
    ):
        q.append(
            _i(
                f"result.{n}",
                CongruityValidationCode.INVALID_VERSION,
                "exact legacy or registry-custodied predicate/frame version required",
            )
        )
    if not isinstance(value.overall_state,CongruityOverallState): q.append(_i("result.overall_state",CongruityValidationCode.TYPE_MISMATCH,"CongruityOverallState required"))
    if not isinstance(value.findings,tuple) or not value.findings: q.append(_i("result.findings",CongruityValidationCode.TYPE_MISMATCH,"non-empty tuple required"))
    if isinstance(value.findings,tuple):
        for f in value.findings: q.extend(validate_finding(f).issues)
        ids=[f.finding_id for f in value.findings if isinstance(f,CongruityFinding)]
        if len(set(ids))!=len(ids): q.append(_i("result.findings",CongruityValidationCode.DUPLICATE_ID,"duplicate finding"))
    counts=(value.compatible_count,value.incompatible_count,value.ambiguous_count,value.unsupported_count,value.conflicted_count,value.indeterminate_count)
    if any(type(n) is not int or n<0 for n in counts) or type(value.assertion_count) is not int or value.assertion_count<1:
        q.append(_i("result.counts",CongruityValidationCode.TYPE_MISMATCH,"non-negative integer counts required"))
    elif sum(counts)!=value.assertion_count:
        q.append(_i("result.counts",CongruityValidationCode.COUNT_MISMATCH,"counts must equal assertion count"))
    else:
        if value.conflicted_count: expected_overall=CongruityOverallState.CONFLICTED
        elif value.unsupported_count: expected_overall=CongruityOverallState.UNSUPPORTED
        elif value.ambiguous_count: expected_overall=CongruityOverallState.AMBIGUOUS
        elif value.indeterminate_count: expected_overall=CongruityOverallState.INDETERMINATE
        elif value.incompatible_count: expected_overall=CongruityOverallState.INCOMPATIBLE
        else: expected_overall=CongruityOverallState.COMPATIBLE
        if value.overall_state is not expected_overall:
            q.append(_i("result.overall_state",CongruityValidationCode.CROSS_RECORD_MISMATCH,"overall state does not match deterministic count precedence"))
        if isinstance(value.findings,tuple):
            per_assertion=[f for f in value.findings if isinstance(f,CongruityFinding) and f.assertion_ref is not None]
            summary=[f for f in value.findings if isinstance(f,CongruityFinding) and f.assertion_ref is None]
            if len(per_assertion)!=value.assertion_count or len({f.assertion_ref for f in per_assertion})!=value.assertion_count:
                q.append(_i("result.findings",CongruityValidationCode.COUNT_MISMATCH,"exactly one finding per assertion required"))
            expected_summary=1 if expected_overall is CongruityOverallState.COMPATIBLE else 0
            if len(summary)!=expected_summary or any(f.finding_kind is not CongruityFindingKind.ALL_ASSERTIONS_COMPATIBLE for f in summary):
                q.append(_i("result.findings",CongruityValidationCode.CROSS_RECORD_MISMATCH,"compatible summary presence mismatch"))
            kind_counts={
                CongruityFindingKind.COMPATIBLE_ASSERTION:value.compatible_count,
                CongruityFindingKind.INCOMPATIBLE_ASSERTION:value.incompatible_count,
                CongruityFindingKind.AMBIGUOUS_ASSERTION:value.ambiguous_count,
                CongruityFindingKind.UNSUPPORTED_ASSERTION:value.unsupported_count,
                CongruityFindingKind.CONFLICTED_ASSERTION:value.conflicted_count,
                CongruityFindingKind.INDETERMINATE_AUTHORITY_ABSENT:value.indeterminate_count,
            }
            for kind, expected_count in kind_counts.items():
                if sum(f.finding_kind is kind for f in per_assertion)!=expected_count:
                    q.append(_i("result.findings",CongruityValidationCode.COUNT_MISMATCH,f"finding count mismatch for {kind.value}"))
    if value.deterministic is not True or value.exact_compatibility_authority_preserved is not True: q.append(_i("result.determinism",CongruityValidationCode.NON_EXACT_COMPATIBILITY_PROHIBITED,"deterministic exact authority required"))
    for n in ("candidate_structure_mutated","frame_rewritten","role_reassigned","similarity_fallback_used","nearest_known_substitution_used","hidden_model_judgment_used","silent_repair_used","clarification_required_created","rejection_created","refusal_relevant_created","blocked_progression_created","composed_gate_outcome_created","candidate_disposition_created","selected_meaning_created","truth_determined","evidence_validated","permission_granted","execution_authorized","route_created","tool_invoked","action_performed","memory_accessed","rendered","delivered","external_resource_loaded","language_model_used","embedding_used","vector_used","rag_used","semantic_similarity_used"):
        if getattr(value,n) is not False: q.append(_i(f"result.{n}",CongruityValidationCode.DOWNSTREAM_AUTHORITY_PROHIBITED,"must be false"))
    if value.digest_algorithm!=DIGEST_ALGORITHM or _SHA256.fullmatch(value.canonical_digest) is None: q.append(_i("result.canonical_digest",CongruityValidationCode.INVALID_SHA256,"sha256 required"))
    elif value.canonical_digest!=expected_result_digest(value): q.append(_i("result.canonical_digest",CongruityValidationCode.IDENTITY_MISMATCH,"result digest mismatch"))
    if value.result_id!=f"congruity_result:sha256:{value.canonical_digest}": q.append(_i("result.result_id",CongruityValidationCode.IDENTITY_MISMATCH,"result id mismatch"))
    if value.schema_version!=SLICE40D_SCHEMA_VERSION: q.append(_i("result.schema_version",CongruityValidationCode.INVALID_VERSION,"Slice 40D schema required"))
    return _ordered(q)

def assert_valid_evaluation_input(v:CongruityEvaluationInput)->CongruityEvaluationInput:
    r=validate_evaluation_input(v)
    if not r.ok: raise CongruityValidationError(r)
    return v

def assert_valid_result(v:CongruityGateResult)->CongruityGateResult:
    r=validate_result(v)
    if not r.ok: raise CongruityValidationError(r)
    return v
