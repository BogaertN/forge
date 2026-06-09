"""Patch 300 - Inactive Memory Capsule contract shapes.

These classes preserve Appendix B field obligations without creating a capsule,
validation result, finalization, or mint eligibility.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .enums import ContractObjectType, ContractValueError, MintingStatus, Patch300ActivationState
from .identity_reference_schema import reject_raw_private_identity
from .validation_schema import ValidationRecordContract

CANDIDATE_SCHEMA_VERSION = "memory_capsule_candidate_contract_v1_patch300"
VALIDATED_SCHEMA_VERSION = "validated_memory_capsule_contract_v1_patch300"
FINALIZED_SCHEMA_VERSION = "finalized_memory_capsule_contract_v1_patch300"


@dataclass(frozen=True)
class MemoryCapsuleCandidateContract:
    capsule_contract_id: str
    contribution_event_contract_ids: tuple[str, ...]
    artifact_reference: str
    contribution_metadata: dict[str, Any]
    status: Patch300ActivationState = Patch300ActivationState.CONTRACT_ONLY_NOT_PERSISTED
    schema_version: str = CANDIDATE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.capsule_contract_id or not self.artifact_reference:
            raise ContractValueError("capsule contract identifier and artifact reference are required")
        if not self.contribution_event_contract_ids or any(not item for item in self.contribution_event_contract_ids):
            raise ContractValueError("capsule candidate contract requires Contribution Event contract references")
        if len(set(self.contribution_event_contract_ids)) != len(self.contribution_event_contract_ids):
            raise ContractValueError("duplicate Contribution Event contract references are rejected")
        if self.status is not Patch300ActivationState.CONTRACT_ONLY_NOT_PERSISTED:
            raise ContractValueError("Patch 300 permits capsule candidate contract shape only")
        reject_raw_private_identity(self.contribution_metadata, field_prefix="contribution_metadata")

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "schema_version": self.schema_version,
            "object_type": ContractObjectType.MEMORY_CAPSULE_CANDIDATE.value,
            "capsule_contract_id": self.capsule_contract_id,
            "contribution_event_contract_ids": list(self.contribution_event_contract_ids),
            "artifact_reference": self.artifact_reference,
            "contribution_metadata": dict(self.contribution_metadata),
            "status": self.status.value,
            "finalized": False,
            "finalized_timestamp": None,
            "top_level_hash": None,
            "ct_minting_status": MintingStatus.BLOCKED_NOT_AUTHORIZED.value,
            "persisted": False,
            "validation_executed": False,
            "finalization_authorized": False,
            "mint_authorized": False,
        }
        reject_raw_private_identity(payload)
        return payload


@dataclass(frozen=True)
class ValidatedMemoryCapsuleContract:
    capsule_contract_id: str
    validation_record: ValidationRecordContract
    status: Patch300ActivationState = Patch300ActivationState.VALIDATION_DISABLED
    schema_version: str = VALIDATED_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.capsule_contract_id:
            raise ContractValueError("capsule contract identifier is required")
        if self.status is not Patch300ActivationState.VALIDATION_DISABLED:
            raise ContractValueError("validated Memory Capsule activation is disabled in Patch 300")

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "object_type": ContractObjectType.VALIDATED_MEMORY_CAPSULE.value,
            "capsule_contract_id": self.capsule_contract_id,
            "status": self.status.value,
            "validation_record": self.validation_record.as_dict(),
            "validated": False,
            "validation_executed": False,
            "finalized": False,
            "mint_authorized": False,
            "persisted": False,
        }


@dataclass(frozen=True)
class FinalizedMemoryCapsuleContract:
    capsule_contract_id: str
    status: Patch300ActivationState = Patch300ActivationState.FINALIZATION_DISABLED
    schema_version: str = FINALIZED_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.capsule_contract_id:
            raise ContractValueError("capsule contract identifier is required")
        if self.status is not Patch300ActivationState.FINALIZATION_DISABLED:
            raise ContractValueError("finalized Memory Capsule activation is disabled in Patch 300")

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "object_type": ContractObjectType.FINALIZED_MEMORY_CAPSULE.value,
            "capsule_contract_id": self.capsule_contract_id,
            "status": self.status.value,
            "finalized": False,
            "finalized_timestamp": None,
            "top_level_hash": None,
            "validation_chain_reference": None,
            "ct_minting_status": MintingStatus.BLOCKED_NOT_AUTHORIZED.value,
            "mint_timestamp": None,
            "mint_record_id": None,
            "nullified": False,
            "nullification_timestamp": None,
            "nullification_reason": None,
            "persistence_authorized": False,
            "mint_authorized": False,
        }
