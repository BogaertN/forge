"""Patch 300 - Inactive CT mint and strictly separated ledger contracts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ct_reward_policy import RewardCalculationPreview
from .enums import ContractObjectType, ContractValueError, LedgerType, Patch300ActivationState

MINT_SCHEMA_VERSION = "ct_mint_event_contract_v1_patch300"
INFLUENCE_LEDGER_SCHEMA_VERSION = "influence_ledger_entry_contract_v1_patch300"
INVESTMENT_LEDGER_SCHEMA_VERSION = "investment_ledger_entry_contract_v1_patch300"


@dataclass(frozen=True)
class CTMintEventContract:
    mint_contract_id: str
    capsule_contract_id: str
    reward_preview: RewardCalculationPreview
    status: Patch300ActivationState = Patch300ActivationState.MINT_DISABLED
    schema_version: str = MINT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.mint_contract_id or not self.capsule_contract_id:
            raise ContractValueError("mint and capsule contract identifiers are required")
        if self.status is not Patch300ActivationState.MINT_DISABLED:
            raise ContractValueError("CT mint activation is disabled in Patch 300")

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "ct_reward_policy_version": self.reward_preview.ct_reward_policy_version,
            "object_type": ContractObjectType.CT_MINT_EVENT.value,
            "mint_contract_id": self.mint_contract_id,
            "capsule_contract_id": self.capsule_contract_id,
            "status": self.status.value,
            "reward_calculation_preview": self.reward_preview.as_dict(),
            "ct_minted_milli_ct": 0,
            "mint_timestamp": None,
            "mint_executed": False,
            "mint_authorized": False,
            "ledger_write_authorized": False,
        }


@dataclass(frozen=True)
class InfluenceLedgerEntryContract:
    ledger_entry_contract_id: str
    mint_contract_id: str
    status: Patch300ActivationState = Patch300ActivationState.LEDGER_WRITE_DISABLED
    ledger_type: LedgerType = LedgerType.INFLUENCE
    schema_version: str = INFLUENCE_LEDGER_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.ledger_entry_contract_id or not self.mint_contract_id:
            raise ContractValueError("influence ledger and mint contract identifiers are required")
        if self.ledger_type is not LedgerType.INFLUENCE:
            raise ContractValueError("investment ledger objects cannot substitute for influence ledger objects")
        if self.status is not Patch300ActivationState.LEDGER_WRITE_DISABLED:
            raise ContractValueError("Influence Ledger writes are disabled in Patch 300")

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "object_type": ContractObjectType.INFLUENCE_LEDGER_ENTRY.value,
            "ledger_type": self.ledger_type.value,
            "ledger_entry_contract_id": self.ledger_entry_contract_id,
            "mint_contract_id": self.mint_contract_id,
            "status": self.status.value,
            "ct_delta_milli_ct": 0,
            "entry_written": False,
            "append_only_write_authorized": False,
            "money_activity_permitted": False,
        }


@dataclass(frozen=True)
class InvestmentLedgerEntryContract:
    ledger_entry_contract_id: str
    investment_reference: str
    status: Patch300ActivationState = Patch300ActivationState.LEDGER_WRITE_DISABLED
    ledger_type: LedgerType = LedgerType.INVESTMENT
    schema_version: str = INVESTMENT_LEDGER_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.ledger_entry_contract_id or not self.investment_reference:
            raise ContractValueError("investment ledger contract identifiers are required")
        if self.ledger_type is not LedgerType.INVESTMENT:
            raise ContractValueError("influence ledger objects cannot substitute for investment ledger objects")
        if self.status is not Patch300ActivationState.LEDGER_WRITE_DISABLED:
            raise ContractValueError("Investment Ledger writes are disabled in Patch 300")

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "object_type": ContractObjectType.INVESTMENT_LEDGER_ENTRY.value,
            "ledger_type": self.ledger_type.value,
            "ledger_entry_contract_id": self.ledger_entry_contract_id,
            "investment_reference": self.investment_reference,
            "status": self.status.value,
            "entry_written": False,
            "money_flow_authorized": False,
            "creates_ct": False,
            "creates_contribution_ownership": False,
            "affects_influence_ledger": False,
        }
