"""Compile identity-bound Contribution Events without live persistence in Build 002."""
from __future__ import annotations
import hashlib
from typing import Any, Mapping
from ..contracts.canonical_json import assert_utc_timestamp_z, canonical_json
from ..contracts.enums import ContributionType, DifficultyClass, InfluenceType, parse_enum
from ..contracts.identity_reference_schema import reject_raw_private_identity
from ..identity_vault.multiuser_authority import require_scopes
from ..integrated_core.policy import BUILD_ID, LIVE_POLICY

SCHEMA_VERSION = "contribution_event_compiled_candidate_v1_build002"

class ContributionEventError(RuntimeError):
    pass

def _hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()

def _hash_value(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise ContributionEventError(f"{field} must be a lowercase SHA-256 value")
    return value

def compile_contribution_event(authority_receipt: Mapping[str, Any], action: Mapping[str, Any]) -> dict[str, Any]:
    if not LIVE_POLICY.compile_contribution_event:
        raise ContributionEventError("contribution event compilation disabled by policy")
    reject_raw_private_identity(action)
    require_scopes(authority_receipt, "internal_attribution_reference_authorized", "capsule_candidate_reference_authorized")
    principal_id = authority_receipt.get("principal_id")
    consent_hash = authority_receipt.get("consent_resolution_hash")
    if not isinstance(principal_id, str) or not principal_id or not isinstance(consent_hash, str):
        raise ContributionEventError("authority receipt lacks opaque principal or consent-resolution hash")
    action_id = str(action.get("action_id") or "").strip()
    action_type = str(action.get("action_type") or "").strip()
    if not action_id or not action_type:
        raise ContributionEventError("action_id and action_type are required")
    timestamp = assert_utc_timestamp_z(action.get("timestamp_utc"), "timestamp_utc")
    ctype = parse_enum(ContributionType, action.get("contribution_type"), "contribution_type")
    difficulty = parse_enum(DifficultyClass, action.get("difficulty_class"), "difficulty_class")
    influence = parse_enum(InfluenceType, action.get("influence_type"), "influence_type")
    payload_hash = _hash_value(action.get("action_payload_hash"), "action_payload_hash")
    source_hash = action.get("source_artifact_proof_hash")
    if source_hash is not None:
        source_hash = _hash_value(source_hash, "source_artifact_proof_hash")
    proof_body = {
        "schema_version": "contributor_action_proof_body_v1_build002",
        "principal_id": principal_id,
        "consent_resolution_hash": consent_hash,
        "action_id": action_id,
        "action_type": action_type,
        "action_payload_hash": payload_hash,
        "source_artifact_proof_hash": source_hash,
        "contribution_type": ctype.value,
        "difficulty_class": difficulty.value,
        "influence_type": influence.value,
        "classification_status": "asserted_candidate_requires_evidence_validation",
        "timestamp_utc": timestamp,
    }
    proof_hash = _hash(proof_body)
    event_body = {
        "schema_version": SCHEMA_VERSION,
        "build_id": BUILD_ID,
        "event_id": f"ce_event_{proof_hash[:24]}",
        "principal_id": principal_id,
        "consent_resolution_hash": consent_hash,
        "action_id": action_id,
        "action_type": action_type,
        "contribution_type": ctype.value,
        "difficulty_class": difficulty.value,
        "influence_type": influence.value,
        "classification_status": "asserted_candidate_requires_evidence_validation",
        "action_payload_hash": payload_hash,
        "source_artifact_proof_hash": source_hash,
        "contributor_action_proof_hash": proof_hash,
        "timestamp_utc": timestamp,
        "event_status": "compiled_identity_bound_not_persisted",
        "proof_body": proof_body,
        "persistence_authorized": False,
        "capsule_finalization_authorized": False,
        "ct_minting_authorized": False,
        "ledger_write_authorized": False,
        "public_attribution_authorized": False,
    }
    return {**event_body, "event_hash": _hash(event_body)}
