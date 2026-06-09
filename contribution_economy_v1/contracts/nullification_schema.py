"""Patch 300 - Inactive append-only correction/nullification contract shape."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .enums import ContractObjectType, ContractValueError, Patch300ActivationState

SCHEMA_VERSION = "nullification_correction_event_contract_v1_patch300"


@dataclass(frozen=True)
class NullificationCorrectionEventContract:
    correction_contract_id: str
    target_contract_id: str
    reason_code: str
    status: Patch300ActivationState = Patch300ActivationState.NULLIFICATION_DISABLED
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.correction_contract_id or not self.target_contract_id or not self.reason_code:
            raise ContractValueError("nullification/correction contract fields are required")
        if self.status is not Patch300ActivationState.NULLIFICATION_DISABLED:
            raise ContractValueError("nullification and correction actions are disabled in Patch 300")

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "object_type": ContractObjectType.NULLIFICATION_CORRECTION_EVENT.value,
            "correction_contract_id": self.correction_contract_id,
            "target_contract_id": self.target_contract_id,
            "reason_code": self.reason_code,
            "status": self.status.value,
            "append_only_required_if_activated_later": True,
            "action_executed": False,
            "target_mutated": False,
            "target_deleted": False,
            "penalty_applied": False,
            "burn_applied": False,
        }
