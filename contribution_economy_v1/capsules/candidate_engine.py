"""Compose governed Memory Capsule candidates from contributor action proof and optional source evidence."""
from __future__ import annotations
import hashlib
from typing import Any, Mapping
from ..contracts.canonical_json import canonical_json
from ..integrated_core.policy import BUILD_ID, LIVE_POLICY

SCHEMA_VERSION = "memory_capsule_candidate_integrated_v1_build002"

class CapsuleCandidateError(RuntimeError):
    pass

def _hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()

def _require_hash(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise CapsuleCandidateError(f"{field} must be a lowercase SHA-256 hash")
    return value

def build_identity_bound_capsule_candidate(event: Mapping[str, Any], source_artifact: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if not LIVE_POLICY.build_capsule_candidate:
        raise CapsuleCandidateError("capsule candidate construction disabled")
    if event.get("event_status") != "compiled_identity_bound_not_persisted":
        raise CapsuleCandidateError("capsule candidates require an identity-bound compiled Contribution Event")
    event_hash = _require_hash(event.get("event_hash"), "event_hash")
    action_proof = _require_hash(event.get("contributor_action_proof_hash"), "contributor_action_proof_hash")
    principal_id = event.get("principal_id")
    if not isinstance(principal_id, str) or not principal_id:
        raise CapsuleCandidateError("capsule candidate requires opaque contributor principal")
    source_artifact_proof_hash = None
    source_reference = None
    if source_artifact is not None:
        source_artifact_proof_hash = _require_hash(source_artifact.get("source_artifact_proof_hash"), "source_artifact_proof_hash")
        source_reference = {
            "source_system": source_artifact.get("source_system"),
            "source_artifact_proof_hash": source_artifact_proof_hash,
            "source_manifest_hash": source_artifact.get("source_manifest_hash"),
            "claim_status": source_artifact.get("claim_status"),
        }
    body = {
        "schema_version": SCHEMA_VERSION,
        "build_id": BUILD_ID,
        "capsule_status": "identity_bound_candidate_not_persisted_not_finalized",
        "finalized": False,
        "finalized_timestamp": None,
        "contribution_event_reference": event,
        "contributors": [{
            "principal_id": principal_id,
            "contribution_event_id": event["event_id"],
            "contribution_event_hash": event_hash,
            "contributor_action_proof_hash": action_proof,
            "contribution_type": event["contribution_type"],
            "difficulty_class": event["difficulty_class"],
            "influence_type": event["influence_type"],
            "consent_resolution_hash": event["consent_resolution_hash"],
        }],
        "source_artifact_reference": source_reference,
        "source_artifact_proof_hash": source_artifact_proof_hash,
        "proof_hash": action_proof,
        "proof_hash_role": "contributor_action_proof_hash",
        "validation_status": "not_executed",
        "validation_chain_reference": None,
        "ct_reward_calculation_preview": None,
        "ct_minting_status": "blocked_not_finalized_not_minted",
        "influence_ledger_write_authorized": False,
        "investment_ledger_write_authorized": False,
        "persistence_authorized": False,
        "public_output_authorized": False,
        "nullified": False,
        "nullification_reference": None,
        "top_level_hash": None,
    }
    body_hash = _hash(body)
    candidate_id = f"capsule_candidate_{body_hash[:24]}"
    with_id = {**body, "capsule_id": candidate_id}
    return {**with_id, "top_level_hash": _hash(with_id)}
