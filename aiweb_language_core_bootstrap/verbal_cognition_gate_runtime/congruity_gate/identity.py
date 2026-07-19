"""Deterministic Slice 40D identity functions."""
from __future__ import annotations
from dataclasses import replace
from .canonical import deterministic_digest, with_expected_id
from .schema import CongruityAssertion, CongruityEvaluationInput, CongruityFinding, CongruityGateResult, CongruityGateRuntimeProfile, CongruityObservation

def with_expected_profile_id(v: CongruityGateRuntimeProfile)->CongruityGateRuntimeProfile: return with_expected_id(v,"profile_id","congruity_profile")
def with_expected_assertion_id(v: CongruityAssertion)->CongruityAssertion: return with_expected_id(v,"assertion_id","congruity_assertion")
def with_expected_observation_id(v: CongruityObservation)->CongruityObservation: return with_expected_id(v,"observation_id","congruity_observation")
def with_expected_evaluation_input_id(v: CongruityEvaluationInput)->CongruityEvaluationInput: return with_expected_id(v,"evaluation_input_id","congruity_evaluation_input")
def with_expected_finding_id(v: CongruityFinding)->CongruityFinding: return with_expected_id(v,"finding_id","congruity_finding")
def expected_result_digest(v: CongruityGateResult)->str: return deterministic_digest(replace(v,result_id="",canonical_digest=""))
def with_expected_result_identity(v: CongruityGateResult)->CongruityGateResult:
    d=expected_result_digest(v); return replace(v,result_id=f"congruity_result:sha256:{d}",canonical_digest=d)
