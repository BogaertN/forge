"""Deterministic schema definitions for AI.Web Slice 1 proof scaffold.

Authority boundary:
This module defines receipt shapes and validation rules only. It creates no runtime
language authority and performs no side effects.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping

SCHEMA_VERSION = "aiweb.slice01.proof_scaffold.v1"
SLICE_ID = "SLICE01"
SLICE_NAME = "Proof Inventory, Result Packet and Receipt Scaffold"

REQUIRED_RECEIPT_FIELDS = (
    "schema_version",
    "slice_id",
    "receipt_type",
    "created_utc",
    "status",
    "authority_basis",
    "fresh_packet_identity",
    "target_repo",
    "head_commit",
    "changed_files",
    "behavior_tests",
    "verifier_gates",
    "rollback",
    "accepted_scope",
    "blocked_authorities",
    "notes",
)

ALLOWED_STATUSES = ("PASS", "FAIL", "BLOCKED", "NOT_APPLICABLE")

BLOCKED_AUTHORITIES = (
    "language_interpretation",
    "concept_resolution",
    "predicate_role_resolution",
    "outward_expression",
    "ui_authority",
    "memory_operation",
    "evidence_validation",
    "corpus_ingestion",
    "external_resource_ingestion",
    "delivery_authority",
    "action_routing",
    "gp014_supersession",
    "gp015_repair",
    "gp015r1_install",
    "production_readiness",
    "llm_authority",
    "learned_model_authority",
    "embedding_authority",
    "vector_authority",
    "similarity_authority",
    "chroma_authority",
    "ollama_authority",
    "rag_authority",
)

LIST_FIELDS = (
    "authority_basis",
    "changed_files",
    "behavior_tests",
    "verifier_gates",
    "blocked_authorities",
    "notes",
)

MAPPING_FIELDS = (
    "fresh_packet_identity",
    "rollback",
    "accepted_scope",
)


def _missing_fields(receipt: Mapping[str, Any], required: Iterable[str]) -> List[str]:
    return [field for field in required if field not in receipt]


def validate_receipt(receipt: Mapping[str, Any]) -> List[str]:
    """Return a deterministic list of validation failures for a receipt mapping."""
    failures: List[str] = []

    if not isinstance(receipt, Mapping):
        return ["receipt is not a mapping"]

    for field in _missing_fields(receipt, REQUIRED_RECEIPT_FIELDS):
        failures.append(f"missing required field: {field}")

    if receipt.get("schema_version") != SCHEMA_VERSION:
        failures.append("schema_version mismatch")

    if receipt.get("slice_id") != SLICE_ID:
        failures.append("slice_id mismatch")

    if receipt.get("status") not in ALLOWED_STATUSES:
        failures.append("status is not an allowed status")

    for field in LIST_FIELDS:
        if field in receipt and not isinstance(receipt[field], list):
            failures.append(f"{field} must be a list")

    for field in MAPPING_FIELDS:
        if field in receipt and not isinstance(receipt[field], dict):
            failures.append(f"{field} must be a mapping")

    blocked = receipt.get("blocked_authorities")
    if isinstance(blocked, list):
        missing_blocked = [item for item in BLOCKED_AUTHORITIES if item not in blocked]
        if missing_blocked:
            failures.append("blocked_authorities missing required Slice 1 exclusions: " + ", ".join(missing_blocked))

    accepted_scope = receipt.get("accepted_scope")
    if isinstance(accepted_scope, dict):
        claim = str(accepted_scope.get("claim", "")).lower()
        forbidden_claim_terms = (
            "production ready",
            "general language",
            "memory authorized",
            "delivery authorized",
            "gp-014 superseded",
            "gp015 repaired",
            "gp-015 repaired",
            "gp-015r1 installed",
            "gp015r1 installed",
        )
        for term in forbidden_claim_terms:
            if term in claim:
                failures.append(f"accepted_scope contains prohibited claim: {term}")

    return failures
