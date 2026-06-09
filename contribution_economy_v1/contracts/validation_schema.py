"""Patch 300 - Inactive validation-record schema and required future gate registry."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .enums import ContractObjectType, ContractValueError, Patch300ActivationState, ValidationGateStatus

SCHEMA_VERSION = "contribution_validation_record_contract_v1_patch300"
REQUIRED_FUTURE_VALIDATION_GATES = (
    "capsule_finalization_check",
    "contribution_validation_check",
    "proof_hash_consistency_check",
    "timestamp_integrity_check",
    "contribution_type_and_difficulty_check",
    "influence_type_validation",
    "drift_pattern_screening",
    "fraud_flag_check",
    "duplicate_contribution_detection",
    "mint_ledger_write_integrity",
    "consent_scope_check",
    "canonical_integrity_check",
)


@dataclass(frozen=True)
class ValidationRecordContract:
    validation_record_id: str
    target_contract_id: str
    status: Patch300ActivationState = Patch300ActivationState.VALIDATION_DISABLED
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.validation_record_id or not self.target_contract_id:
            raise ContractValueError("validation record and target contract identifiers are required")
        if self.status is not Patch300ActivationState.VALIDATION_DISABLED:
            raise ContractValueError("Patch 300 defines validation shape only; validation execution is disabled")

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "object_type": ContractObjectType.VALIDATION_RECORD.value,
            "validation_record_id": self.validation_record_id,
            "target_contract_id": self.target_contract_id,
            "status": self.status.value,
            "required_future_gates": {
                gate: ValidationGateStatus.NOT_EVALUATED.value for gate in REQUIRED_FUTURE_VALIDATION_GATES
            },
            "validation_executed": False,
            "validation_passed": False,
            "mint_eligibility_created": False,
            "persistence_authorized": False,
        }
