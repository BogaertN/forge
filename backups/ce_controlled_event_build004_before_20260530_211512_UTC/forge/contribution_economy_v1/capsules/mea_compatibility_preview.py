"""Pure MEA evidence to Memory Capsule compatibility-preview mapping.

A sealed/committed MEA hypothesis is evidence of an internal cognitive transition.  It is
not contributor-action proof and is not a finalized Memory Capsule.  This module therefore
compiles an in-memory, deterministic capsule-compatible preview while keeping contributor
proof, validation, persistence, ledger writing, and CT minting explicitly blocked.
"""
from __future__ import annotations

import hashlib
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Mapping

from ..contracts.canonical_json import canonical_json

BUILD_ID = "CE-IV-LEDGER-CAPSULE-BUILD-001"
SCHEMA_VERSION = "mea_memory_capsule_compatibility_preview_v1_build001"
SOURCE_EVIDENCE_SCHEMA_VERSION = "mea_source_artifact_evidence_reference_v1_build001"
_REQUIRED_HASH_FIELDS = (
    "candidate_hash",
    "source_manifest_hash",
    "source_state_content_hash",
    "committed_manifest_hash",
    "committed_state_content_hash",
    "transaction_intent_hash",
    "transaction_seal_packet_hash",
    "transaction_audit_chain_hash",
    "advance_receipt_hash",
    "rollback_record_hash",
    "memory_record_hash",
)
_REQUIRED_TEXT_FIELDS = ("candidate_id", "claim_status", "transaction_id", "memory_record_id", "memory_tier")
_ALLOWED_CLAIM_STATUS = {"recall", "hypothesis", "derived_claim", "verified_claim", "rejected"}


class CapsuleCompatibilityError(ValueError):
    """Raised when MEA evidence cannot lawfully produce a capsule compatibility preview."""


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _hash_payload(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _proof_debt_milli(value: Any) -> int:
    try:
        debt = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise CapsuleCompatibilityError("MEA proof_debt must be numeric") from exc
    if debt < Decimal("0") or debt > Decimal("1"):
        raise CapsuleCompatibilityError("MEA proof_debt must remain between zero and one")
    return int((debt * Decimal("1000")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def build_mea_capsule_compatibility_preview(evidence: Mapping[str, Any]) -> dict[str, Any]:
    """Build a non-persisted capsule-compatible object from replay-verified MEA evidence."""
    missing = [field for field in _REQUIRED_TEXT_FIELDS + _REQUIRED_HASH_FIELDS if not evidence.get(field)]
    if missing:
        raise CapsuleCompatibilityError("MEA evidence is missing required fields: " + ", ".join(missing))
    invalid_hashes = [field for field in _REQUIRED_HASH_FIELDS if not _is_sha256(evidence.get(field))]
    if invalid_hashes:
        raise CapsuleCompatibilityError("MEA evidence contains invalid SHA-256 fields: " + ", ".join(invalid_hashes))
    if evidence["claim_status"] not in _ALLOWED_CLAIM_STATUS:
        raise CapsuleCompatibilityError("MEA claim_status is outside the typed claim-status set")
    if evidence.get("replay_verified") is not True or evidence.get("all_replay_checks_passed") is not True:
        raise CapsuleCompatibilityError("MEA evidence must be replay verified before capsule compatibility preview")
    if evidence.get("source_state_integrity_verified") is not True:
        raise CapsuleCompatibilityError("MEA committed source-state integrity must be verified")
    proof_debt_milli = _proof_debt_milli(evidence.get("proof_debt"))
    source_evidence = {
        "schema_version": SOURCE_EVIDENCE_SCHEMA_VERSION,
        "source_system": "MEA",
        "candidate_id": evidence["candidate_id"],
        "candidate_hash": evidence["candidate_hash"],
        "claim_status": evidence["claim_status"],
        "proof_debt_milli": proof_debt_milli,
        "source_manifest_hash": evidence["source_manifest_hash"],
        "source_state_content_hash": evidence["source_state_content_hash"],
        "committed_manifest_hash": evidence["committed_manifest_hash"],
        "committed_state_content_hash": evidence["committed_state_content_hash"],
        "transaction_id": evidence["transaction_id"],
        "transaction_intent_hash": evidence["transaction_intent_hash"],
        "seal_packet_hash": evidence["transaction_seal_packet_hash"],
        "transaction_audit_chain_hash": evidence["transaction_audit_chain_hash"],
        "advance_receipt_hash": evidence["advance_receipt_hash"],
        "rollback_record_hash": evidence["rollback_record_hash"],
        "memory_record_id": evidence["memory_record_id"],
        "memory_record_hash": evidence["memory_record_hash"],
        "memory_tier": evidence["memory_tier"],
        "replay_verified": True,
        "all_replay_checks_passed": True,
        "source_state_integrity_verified": True,
    }
    source_artifact_proof_hash = _hash_payload(source_evidence)
    capsule_id = f"capsule_preview_mea_{source_artifact_proof_hash[:24]}"
    preview_body = {
        "schema_version": SCHEMA_VERSION,
        "build_id": BUILD_ID,
        "capsule_id": capsule_id,
        "capsule_status": "compatibility_preview_only_not_persisted",
        "finalized": False,
        "finalized_timestamp": None,
        "claim_status": evidence["claim_status"],
        "source_system": "MEA",
        "source_manifest_hash": evidence["source_manifest_hash"],
        "committed_manifest_hash": evidence["committed_manifest_hash"],
        "seal_packet_hash": evidence["transaction_seal_packet_hash"],
        "source_artifact_proof_hash": source_artifact_proof_hash,
        "proof_hash": None,
        "proof_hash_role": "contributor_action_proof_hash_unavailable_until_identity_bound_contribution_event",
        "validation_chain_reference": {
            "transaction_id": evidence["transaction_id"],
            "transaction_intent_hash": evidence["transaction_intent_hash"],
            "transaction_audit_chain_hash": evidence["transaction_audit_chain_hash"],
            "advance_receipt_hash": evidence["advance_receipt_hash"],
            "rollback_record_hash": evidence["rollback_record_hash"],
            "memory_record_id": evidence["memory_record_id"],
            "memory_record_hash": evidence["memory_record_hash"],
        },
        "source_artifact_evidence": source_evidence,
        "contributors": [],
        "contributor_binding_status": "pending_identity_bound_contribution_event_and_action_proof",
        "contributor_action_metadata": None,
        "breath_validation": {
            "status": "not_executed",
            "validation_time": None,
            "validator_id": None,
        },
        "ct_minting_status": "blocked",
        "mint_timestamp": None,
        "mint_record_id": None,
        "influence_ledger_write_authorized": False,
        "investment_ledger_write_authorized": False,
        "nullified": False,
        "nullification_timestamp": None,
        "nullification_reason": None,
        "persistence_authorized": False,
        "writes_memory_capsule": False,
        "writes_ledgers": False,
        "writes_identity_vault": False,
        "mints_ct": False,
        "public_output_authorized": False,
        "top_level_hash": None,
        "top_level_hash_scope": "unfinalized_compatibility_preview_body_only",
        "integrity_rule": "MEA source artifact evidence is not contributor action proof and cannot authorize capsule finalization, CT minting, or ledger writing.",
    }
    top_level_hash = _hash_payload(preview_body)
    return {**preview_body, "top_level_hash": top_level_hash}
