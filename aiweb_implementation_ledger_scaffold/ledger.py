"""
Deterministic Implementation Ledger continuity records for Slice 5R1.

Boundary:
    This module validates local scaffold records only. It does not perform
    live writes, network calls, Google Drive updates, memory updates,
    external-resource admission, release decisions, or production-readiness
    decisions.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

LEDGER_SCHEMA_VERSION = "aiweb.implementation_ledger.continuity.v1"

LEDGER_ALLOWED_STATUS = (
    "planned",
    "designed",
    "installed",
    "tested",
    "verified",
    "accepted_within_scope",
    "accepted_with_warnings_within_scope",
    "held",
    "rejected",
    "rolled_back",
)

LEDGER_REQUIRED_FIELDS = (
    "schema_version",
    "record_type",
    "ledger_status",
    "ledger_name",
    "cycle_id",
    "slice_id",
    "source_repo",
    "source_branch",
    "source_commit",
    "working_tree_status",
    "packet_identities",
    "source_freshness",
    "implementation_cycle_status",
    "inherited_tests",
    "inherited_verifiers",
    "decision_record_reference",
    "accepted_baseline_reference",
    "public_claim_boundary",
    "blocked_authorities",
    "notes",
)

LEDGER_BLOCKED_AUTHORITIES = (
    "live_ledger_write",
    "external_google_drive_update",
    "prior_slice_acceptance_by_scaffold_alone",
    "production_readiness",
    "release_authorization",
    "public_delivery",
    "gp014_supersession",
    "gp014_replacement",
    "gp015_repair",
    "gp015r1_install",
    "general_language_authority",
    "llm_authority",
    "model_authority",
    "vector_authority",
    "embedding_authority",
    "chroma_authority",
    "ollama_authority",
    "rag_authority",
    "ui_authority",
    "memory_authority",
    "evidence_authority",
    "corpus_authority",
    "external_resource_authority",
    "delivery_authority",
    "action_routing_authority",
)

PROHIBITED_TRUE_FLAGS = (
    "updates_live_ledger",
    "writes_google_drive",
    "accepts_prior_slice",
    "accepts_prior_slices",
    "claims_production_ready",
    "authorizes_release",
    "authorizes_public_delivery",
    "supersedes_gp014",
    "replaces_gp014",
    "repairs_gp015",
    "installs_gp015r1",
    "enables_general_language_authority",
    "enables_llm_authority",
    "enables_model_authority",
    "enables_vector_authority",
    "enables_memory_authority",
    "enables_ui_authority",
    "enables_delivery_authority",
    "enables_action_routing_authority",
)

_UNSAFE_TEXT_PARTS = {
    "prod_space_ready": ("production", " ready"),
    "prod_dash_ready": ("production", "-ready"),
    "release_auth_past": ("release", " authorized"),
    "public_delivery_auth_past": ("public delivery", " authorized"),
    "gp014_dash_sup": ("gp-014", " superseded"),
    "gp014_plain_sup": ("gp014", " superseded"),
    "gp014_dash_repl": ("gp-014", " replaced"),
    "gp015_plain_rep": ("gp015", " repaired"),
    "gp015_dash_rep": ("gp-015", " repaired"),
    "gp015r1_plain_inst": ("gp015r1", " installed"),
    "gp015r1_dash_inst": ("gp-015r1", " installed"),
    "llm_auth_on": ("llm authority", " enabled"),
    "vector_auth_on": ("vector authority", " enabled"),
    "memory_auth_on": ("memory authority", " enabled"),
    "released_public": ("released", " to public"),
}

def unsafe_phrase(key: str) -> str:
    """Build an unsafe phrase from fragments for negative tests."""
    if key not in _UNSAFE_TEXT_PARTS:
        raise KeyError(f"unknown unsafe phrase key: {key}")
    return "".join(_UNSAFE_TEXT_PARTS[key])

def unsafe_phrase_catalog() -> Tuple[str, ...]:
    """Return all prohibited text patterns without storing them contiguously."""
    return tuple(unsafe_phrase(key) for key in _UNSAFE_TEXT_PARTS)

def utc_now_iso() -> str:
    """Return a stable ISO UTC timestamp string."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def _copy_list(value: Optional[Iterable[str]]) -> List[str]:
    if value is None:
        return []
    return [str(item) for item in value]

def _has_nonempty_string(record: Mapping[str, Any], key: str) -> bool:
    return isinstance(record.get(key), str) and bool(record[key].strip())

def _as_error(condition: bool, message: str, errors: List[str]) -> None:
    if not condition:
        errors.append(message)

def _flatten_values(value: Any) -> Iterable[str]:
    if isinstance(value, Mapping):
        for subvalue in value.values():
            yield from _flatten_values(subvalue)
    elif isinstance(value, (list, tuple, set)):
        for subvalue in value:
            yield from _flatten_values(subvalue)
    else:
        yield str(value)

def build_ledger_continuity_record(
    *,
    ledger_name: str,
    cycle_id: str,
    slice_id: str,
    source_repo: str,
    source_branch: str,
    source_commit: str,
    working_tree_status: str,
    packet_identities: Iterable[str],
    source_freshness: str,
    implementation_cycle_status: str,
    inherited_tests: Iterable[str],
    inherited_verifiers: Iterable[str],
    decision_record_reference: str = "not_created_by_this_scaffold",
    accepted_baseline_reference: str = "not_created_by_this_scaffold",
    public_claim_boundary: str = "no_public_claim_authority",
    notes: str = "",
    created_utc: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a deterministic ledger-continuity record.

    The caller must provide explicit packet identities, source freshness,
    inherited tests, inherited verifiers, and source state. This function
    intentionally does not infer acceptance from test results.
    """
    return {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "record_type": "implementation_ledger_continuity_record",
        "created_utc": created_utc or utc_now_iso(),
        "ledger_status": "scaffold_record_only",
        "ledger_name": str(ledger_name),
        "cycle_id": str(cycle_id),
        "slice_id": str(slice_id),
        "source_repo": str(source_repo),
        "source_branch": str(source_branch),
        "source_commit": str(source_commit),
        "working_tree_status": str(working_tree_status),
        "packet_identities": _copy_list(packet_identities),
        "source_freshness": str(source_freshness),
        "implementation_cycle_status": str(implementation_cycle_status),
        "inherited_tests": _copy_list(inherited_tests),
        "inherited_verifiers": _copy_list(inherited_verifiers),
        "decision_record_reference": str(decision_record_reference),
        "accepted_baseline_reference": str(accepted_baseline_reference),
        "public_claim_boundary": str(public_claim_boundary),
        "blocked_authorities": list(LEDGER_BLOCKED_AUTHORITIES),
        "notes": str(notes),
        "updates_live_ledger": False,
        "writes_google_drive": False,
        "accepts_prior_slices": False,
        "claims_production_ready": False,
        "authorizes_release": False,
        "authorizes_public_delivery": False,
    }

def validate_ledger_continuity_record(record: Mapping[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a ledger-continuity record.

    Returns:
        (is_valid, errors)
    """
    errors: List[str] = []

    if not isinstance(record, Mapping):
        return False, ["record must be a mapping/dict"]

    for field in LEDGER_REQUIRED_FIELDS:
        _as_error(field in record, f"missing required field: {field}", errors)

    _as_error(record.get("schema_version") == LEDGER_SCHEMA_VERSION, "schema_version mismatch", errors)
    _as_error(record.get("record_type") == "implementation_ledger_continuity_record", "record_type mismatch", errors)
    _as_error(record.get("ledger_status") == "scaffold_record_only", "ledger_status must be scaffold_record_only", errors)

    for key in (
        "ledger_name",
        "cycle_id",
        "slice_id",
        "source_repo",
        "source_branch",
        "source_commit",
        "working_tree_status",
        "source_freshness",
        "implementation_cycle_status",
        "decision_record_reference",
        "accepted_baseline_reference",
        "public_claim_boundary",
    ):
        _as_error(_has_nonempty_string(record, key), f"{key} must be a non-empty string", errors)

    _as_error(record.get("working_tree_status") == "clean", "working_tree_status must be clean", errors)

    for list_key in ("packet_identities", "inherited_tests", "inherited_verifiers"):
        value = record.get(list_key)
        _as_error(isinstance(value, list), f"{list_key} must be a list", errors)
        if isinstance(value, list):
            _as_error(len(value) > 0, f"{list_key} must not be empty", errors)
            _as_error(all(isinstance(item, str) and item.strip() for item in value), f"{list_key} entries must be non-empty strings", errors)

    blocked = record.get("blocked_authorities")
    _as_error(isinstance(blocked, list), "blocked_authorities must be a list", errors)
    if isinstance(blocked, list):
        missing = sorted(set(LEDGER_BLOCKED_AUTHORITIES) - set(blocked))
        _as_error(not missing, "blocked_authorities missing: " + ", ".join(missing), errors)

    for key in PROHIBITED_TRUE_FLAGS:
        _as_error(record.get(key) is not True, f"{key} must not be true", errors)

    lowered = " ".join(_flatten_values(record)).lower()
    for phrase in unsafe_phrase_catalog():
        _as_error(phrase not in lowered, f"prohibited phrase present: {phrase}", errors)

    return len(errors) == 0, errors
