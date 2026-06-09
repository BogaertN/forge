"""Executable candidate validation that never finalizes or mints in Build 002."""
from __future__ import annotations
import hashlib
from typing import Any, Mapping, Iterable
from ..contracts.canonical_json import canonical_json
from ..contracts.ct_reward_policy import calculate_reward_preview
from ..identity_vault.multiuser_authority import require_scopes
from ..integrated_core.policy import BUILD_ID, LIVE_POLICY

SCHEMA_VERSION = "capsule_candidate_validation_record_v1_build002"
VALIDATOR_ID = "ce_integrated_validator_build002"
class ValidationError(RuntimeError): pass

def _hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()

def _verified_hash(payload: Mapping[str, Any], supplied: Any, label: str) -> None:
    if supplied != _hash(payload):
        raise ValidationError(f"{label} integrity hash mismatch")

def validate_capsule_candidate(candidate: Mapping[str, Any], authority_receipt: Mapping[str, Any], *, existing_event_hashes: Iterable[str] = (), drift_flag: bool = False, fraud_flag: bool = False, classification_evidence_verified: bool = False) -> dict[str, Any]:
    if not LIVE_POLICY.execute_candidate_validation: raise ValidationError("candidate validation disabled")
    contributors = candidate.get("contributors")
    event = candidate.get("contribution_event_reference")
    if not isinstance(contributors, list) or len(contributors) != 1 or not isinstance(event, Mapping):
        raise ValidationError("Build 002 validation requires exactly one identity-bound Contribution Event reference")
    contributor = contributors[0]
    if contributor.get("principal_id") != authority_receipt.get("principal_id"): raise ValidationError("capsule contributor does not match authority receipt")
    require_scopes(authority_receipt, "internal_attribution_reference_authorized", "capsule_candidate_reference_authorized")
    event_body = {key: value for key, value in event.items() if key != "event_hash"}
    _verified_hash(event_body, event.get("event_hash"), "Contribution Event")
    _verified_hash(event["proof_body"], event.get("contributor_action_proof_hash"), "contributor action proof")
    if contributor.get("contribution_event_hash") != event.get("event_hash") or contributor.get("contributor_action_proof_hash") != event.get("contributor_action_proof_hash"):
        raise ValidationError("capsule contributor reference does not match the referenced Contribution Event")
    candidate_body = dict(candidate)
    candidate_body["top_level_hash"] = None
    _verified_hash(candidate_body, candidate.get("top_level_hash"), "Memory Capsule Candidate")
    if event.get("source_artifact_proof_hash") != candidate.get("source_artifact_proof_hash"):
        raise ValidationError("source artifact proof reference differs between event and capsule candidate")
    checks = {"identity_authority": "passed", "consent_scope": "passed", "event_hash_integrity": "passed", "action_proof_integrity": "passed", "capsule_hash_integrity": "passed", "source_artifact_consistency": "passed"}
    if event.get("event_hash") in set(existing_event_hashes): status="blocked_duplicate_contribution_event"; checks["duplicate_detection"]="failed"
    elif drift_flag: status="blocked_drift_screening"; checks["drift_screening"]="failed"
    elif fraud_flag: status="blocked_fraud_screening"; checks["fraud_screening"]="failed"
    elif not classification_evidence_verified: status="blocked_classification_evidence_not_verified"; checks["classification_evidence"]="failed"
    else:
        status="integrity_and_classification_validated_not_finalized_not_minted"; checks.update({"duplicate_detection":"passed","drift_screening":"passed","fraud_screening":"passed","classification_evidence":"passed"})
    reward = calculate_reward_preview(contributor["contribution_type"], contributor["difficulty_class"], contributor["influence_type"]).as_dict() if status == "integrity_and_classification_validated_not_finalized_not_minted" else None
    body = {"schema_version": SCHEMA_VERSION,"build_id": BUILD_ID,"validator_id": VALIDATOR_ID,"capsule_id": candidate.get("capsule_id"),"capsule_top_level_hash": candidate.get("top_level_hash"),"principal_id": contributor.get("principal_id"),"contributor_action_proof_hash": contributor.get("contributor_action_proof_hash"),"consent_resolution_hash": authority_receipt.get("consent_resolution_hash"),"validation_status": status,"checks": checks,"reward_calculation_preview_not_minted": reward,"persistence_authorized": False,"finalization_authorized": False,"mint_authorized": False,"influence_ledger_write_authorized": False}
    digest=_hash(body)
    return {**body,"validation_record_id":f"validation_{digest[:24]}","validation_record_hash":digest}
