"""Patch 300 - Controlled enumerations for the Contribution Economy contract kernel.

This module declares types only. It performs no I/O and authorizes no live
Contribution Economy operation.
"""
from __future__ import annotations

from enum import Enum
from typing import TypeVar


class ContractValueError(ValueError):
    """Raised when a contract value fails a locked Patch 300 rule."""


class _StringEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class ContributionType(_StringEnum):
    CRT = "CRT"
    CPT = "CPT"
    BLD = "BLD"


class DifficultyClass(_StringEnum):
    LIGHT = "light"
    STANDARD = "standard"
    HEAVY = "heavy"
    MONUMENT = "monument"


class InfluenceType(_StringEnum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    COLLABORATIVE = "collaborative"


class LedgerType(_StringEnum):
    INFLUENCE = "influence_ledger"
    INVESTMENT = "investment_ledger"


class ContractObjectType(_StringEnum):
    CONTRIBUTOR_PRINCIPAL_REFERENCE = "contributor_principal_reference"
    CONSENT_SCOPE_REFERENCE = "consent_scope_reference"
    CONTRIBUTION_EVENT = "contribution_event"
    VALIDATION_RECORD = "validation_record"
    MEMORY_CAPSULE_CANDIDATE = "memory_capsule_candidate"
    VALIDATED_MEMORY_CAPSULE = "validated_memory_capsule"
    FINALIZED_MEMORY_CAPSULE = "finalized_memory_capsule"
    CT_MINT_EVENT = "ct_mint_event"
    INFLUENCE_LEDGER_ENTRY = "influence_ledger_entry"
    INVESTMENT_LEDGER_ENTRY = "investment_ledger_entry"
    NULLIFICATION_CORRECTION_EVENT = "nullification_correction_event"


class Patch300ActivationState(_StringEnum):
    CONTRACT_ONLY_NOT_PERSISTED = "contract_only_not_persisted"
    DEFINED_DISABLED = "defined_disabled"
    VALIDATION_DISABLED = "validation_disabled"
    FINALIZATION_DISABLED = "finalization_disabled"
    MINT_DISABLED = "mint_disabled"
    LEDGER_WRITE_DISABLED = "ledger_write_disabled"
    NULLIFICATION_DISABLED = "nullification_disabled"
    PUBLIC_OUTPUT_DISABLED = "public_output_disabled"


class ValidationGateStatus(_StringEnum):
    NOT_EVALUATED = "not_evaluated_patch300"
    DISABLED = "disabled_patch300"


class MintingStatus(_StringEnum):
    BLOCKED_NOT_AUTHORIZED = "blocked_not_authorized"


class ConsentPermission(_StringEnum):
    NOT_AUTHORIZED = "not_authorized_patch300"


E = TypeVar("E", bound=Enum)


def parse_enum(enum_type: type[E], value: E | str, field_name: str) -> E:
    """Coerce a locked enum value or reject it with a field-specific error."""
    if isinstance(value, enum_type):
        return value
    try:
        return enum_type(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        allowed = ", ".join(item.value for item in enum_type)
        raise ContractValueError(f"{field_name} must be one of: {allowed}") from exc
