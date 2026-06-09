"""Hard live gates: fully specified decisions, all economic mutation denied in Build 002."""
from __future__ import annotations
from typing import Any, Mapping
from ..integrated_core.policy import BUILD_ID, LIVE_POLICY

SCHEMA_VERSION = "ce_integrated_economic_gate_decision_v1_build002"

def _deny(operation: str, reason: str, evidence: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "build_id": BUILD_ID, "operation": operation, "allowed": False,
            "reason_code": reason, "evidence_reference_present": bool(evidence), "writes_state": False,
            "mints_ct": False, "writes_influence_ledger": False, "writes_investment_ledger": False}

def evaluate_finalization(validation_record: Mapping[str, Any]) -> dict[str, Any]:
    return _deny("finalize_memory_capsule", "BUILD002_CAPSULE_FINALIZATION_DISABLED_REQUIRES_LATER_CONTROLLED_ACTIVATION", validation_record)

def evaluate_mint(finalized_capsule: Mapping[str, Any] | None) -> dict[str, Any]:
    return _deny("mint_ct", "BUILD002_CT_MINTING_DISABLED_REQUIRES_FINALIZED_VALIDATED_CAPSULE_AND_LATER_ACTIVATION", finalized_capsule)

def evaluate_influence_write(mint_event: Mapping[str, Any] | None) -> dict[str, Any]:
    return _deny("write_influence_ledger", "BUILD002_INFLUENCE_LEDGER_WRITE_DISABLED_NO_AUTHORIZED_MINT", mint_event)

def evaluate_investment_write(investment_event: Mapping[str, Any] | None) -> dict[str, Any]:
    return _deny("write_investment_ledger", "BUILD002_INVESTMENT_LEDGER_WRITE_DISABLED_SEPARATE_LATER_APPROVAL_REQUIRED", investment_event)

def gate_manifest() -> dict[str, Any]:
    return {"schema_version": "ce_integrated_economic_gate_manifest_v1_build002", "build_id": BUILD_ID,
            "live_policy": LIVE_POLICY.as_dict(), "capsule_finalization_enabled": False, "ct_minting_enabled": False,
            "influence_ledger_writes_enabled": False, "investment_ledger_writes_enabled": False,
            "money_creates_ct": False, "authorization_receipt_alone_never_bypasses_live_gate": True}
