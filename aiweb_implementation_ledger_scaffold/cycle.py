"""
Deterministic implementation-cycle update records for Slice 5R1.

Boundary:
    A cycle update is evidence organization only. It is not an acceptance
    decision, release grant, production-readiness decision, live ledger write,
    or public claim.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from .ledger import unsafe_phrase

CYCLE_SCHEMA_VERSION = "aiweb.implementation_ledger.cycle_update.v1"

CYCLE_ALLOWED_STATUS = (
    "planned",
    "designed",
    "installed",
    "tested_passed",
    "verified_passed",
    "accepted_within_scope",
    "accepted_with_warnings_within_scope",
    "held",
    "rejected",
    "rolled_back",
)

CYCLE_REQUIRED_FIELDS = (
    "schema_version",
    "record_type",
    "cycle_id",
    "cycle_title",
    "slice_id",
    "slice_name",
    "cycle_status",
    "source_commit",
    "source_branch",
    "working_tree_status",
    "source_packet",
    "patch_design_record",
    "patch_packet",
    "result_packet",
    "result_packet_sha256",
    "verifier_outputs",
    "behavior_test_outputs",
    "decision_record_required",
    "accepted_baseline_update_required",
    "public_claim_boundary",
    "blocked_authorities",
)

CYCLE_BLOCKED_AUTHORITIES = (
    "production_readiness",
    "release_authorization",
    "public_delivery",
    "gp014_supersession",
    "gp014_replacement",
    "gp015_repair",
    "gp015r1_install",
    "general_language_authority",
    "llm_model_vector_authority",
    "memory_evidence_corpus_external_resource_authority",
    "ui_delivery_action_routing_authority",
    "live_ledger_write",
)

_CYCLE_UNSAFE_KEYS = (
    "prod_space_ready",
    "prod_dash_ready",
    "released_public",
    "public_delivery_auth_past",
    "gp014_dash_sup",
    "gp014_dash_repl",
    "gp015_dash_rep",
    "gp015r1_dash_inst",
    "llm_auth_on",
    "vector_auth_on",
    "memory_auth_on",
)

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def _copy_list(value: Optional[Iterable[str]]) -> List[str]:
    if value is None:
        return []
    return [str(item) for item in value]

def _flatten_values(value: Any) -> Iterable[str]:
    if isinstance(value, Mapping):
        for subvalue in value.values():
            yield from _flatten_values(subvalue)
    elif isinstance(value, (list, tuple, set)):
        for subvalue in value:
            yield from _flatten_values(subvalue)
    else:
        yield str(value)

def build_cycle_update_record(
    *,
    cycle_id: str,
    cycle_title: str,
    slice_id: str,
    slice_name: str,
    cycle_status: str,
    source_commit: str,
    source_branch: str,
    working_tree_status: str,
    source_packet: str,
    patch_design_record: str,
    patch_packet: str,
    result_packet: str,
    result_packet_sha256: str,
    verifier_outputs: Iterable[str],
    behavior_test_outputs: Iterable[str],
    public_claim_boundary: str = "no_public_claim_authority",
    created_utc: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a cycle update record that preserves evidence pointers.

    This function does not decide acceptance by itself. Accepted statuses remain
    dependent on separate decision and baseline update records.
    """
    return {
        "schema_version": CYCLE_SCHEMA_VERSION,
        "record_type": "implementation_cycle_update_record",
        "created_utc": created_utc or utc_now_iso(),
        "cycle_id": str(cycle_id),
        "cycle_title": str(cycle_title),
        "slice_id": str(slice_id),
        "slice_name": str(slice_name),
        "cycle_status": str(cycle_status),
        "source_commit": str(source_commit),
        "source_branch": str(source_branch),
        "working_tree_status": str(working_tree_status),
        "source_packet": str(source_packet),
        "patch_design_record": str(patch_design_record),
        "patch_packet": str(patch_packet),
        "result_packet": str(result_packet),
        "result_packet_sha256": str(result_packet_sha256),
        "verifier_outputs": _copy_list(verifier_outputs),
        "behavior_test_outputs": _copy_list(behavior_test_outputs),
        "decision_record_required": True,
        "accepted_baseline_update_required": True,
        "public_claim_boundary": str(public_claim_boundary),
        "production_readiness_status": "not_production_ready",
        "release_status": "not_released",
        "public_delivery_status": "not_authorized",
        "blocked_authorities": list(CYCLE_BLOCKED_AUTHORITIES),
        "claims_production_ready": False,
        "authorizes_release": False,
        "authorizes_public_delivery": False,
        "updates_live_ledger": False,
    }

def validate_cycle_update_record(record: Mapping[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if not isinstance(record, Mapping):
        return False, ["record must be a mapping/dict"]

    for field in CYCLE_REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing required field: {field}")

    if record.get("schema_version") != CYCLE_SCHEMA_VERSION:
        errors.append("schema_version mismatch")
    if record.get("record_type") != "implementation_cycle_update_record":
        errors.append("record_type mismatch")

    status = record.get("cycle_status")
    if status not in CYCLE_ALLOWED_STATUS:
        errors.append("cycle_status is not controlled")

    for key in (
        "cycle_id",
        "cycle_title",
        "slice_id",
        "slice_name",
        "source_commit",
        "source_branch",
        "working_tree_status",
        "source_packet",
        "patch_design_record",
        "patch_packet",
        "result_packet",
        "result_packet_sha256",
        "public_claim_boundary",
    ):
        value = record.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{key} must be a non-empty string")

    if record.get("working_tree_status") != "clean":
        errors.append("working_tree_status must be clean")

    for list_key in ("verifier_outputs", "behavior_test_outputs"):
        value = record.get(list_key)
        if not isinstance(value, list):
            errors.append(f"{list_key} must be a list")
        elif not value or not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"{list_key} must contain non-empty strings")

    if record.get("decision_record_required") is not True:
        errors.append("decision_record_required must be true")
    if record.get("accepted_baseline_update_required") is not True:
        errors.append("accepted_baseline_update_required must be true")

    if record.get("production_readiness_status") != "not_production_ready":
        errors.append("production_readiness_status must remain not_production_ready")
    if record.get("release_status") != "not_released":
        errors.append("release_status must remain not_released")
    if record.get("public_delivery_status") != "not_authorized":
        errors.append("public_delivery_status must remain not_authorized")

    for flag in ("claims_production_ready", "authorizes_release", "authorizes_public_delivery", "updates_live_ledger"):
        if record.get(flag) is True:
            errors.append(f"{flag} must not be true")

    blocked = record.get("blocked_authorities")
    if not isinstance(blocked, list):
        errors.append("blocked_authorities must be a list")
    else:
        missing = sorted(set(CYCLE_BLOCKED_AUTHORITIES) - set(blocked))
        if missing:
            errors.append("blocked_authorities missing: " + ", ".join(missing))

    lowered = " ".join(_flatten_values(record)).lower()
    for key in _CYCLE_UNSAFE_KEYS:
        phrase = unsafe_phrase(key)
        if phrase in lowered:
            errors.append(f"prohibited phrase present: {phrase}")

    return len(errors) == 0, errors
