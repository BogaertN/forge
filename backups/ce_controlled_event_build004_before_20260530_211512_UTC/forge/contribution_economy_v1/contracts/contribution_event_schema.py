"""Patch 300 - Contract-only Contribution Event schema validation."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .canonical_json import assert_utc_timestamp_z
from .enums import (
    ContractObjectType, ContractValueError, ContributionType, DifficultyClass,
    InfluenceType, Patch300ActivationState, parse_enum,
)
from .identity_reference_schema import ContributorPrincipalReferenceContract, reject_raw_private_identity

SCHEMA_VERSION = "contribution_event_contract_v1_patch300"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class SourceEvidenceReference:
    evidence_type: str
    evidence_reference: str
    evidence_hash: str

    def __post_init__(self) -> None:
        if not self.evidence_type or not self.evidence_reference:
            raise ContractValueError("source evidence type and reference are required")
        if not _SHA256_RE.fullmatch(self.evidence_hash):
            raise ContractValueError("source evidence hash must be a lowercase SHA-256 reference")

    def as_dict(self) -> dict[str, str]:
        return {
            "evidence_type": self.evidence_type,
            "evidence_reference": self.evidence_reference,
            "evidence_hash": self.evidence_hash,
        }


@dataclass(frozen=True)
class ContributionEventContract:
    event_id: str
    contributor: ContributorPrincipalReferenceContract
    timestamp_contributed: str
    proof_hash: str
    contribution_type: ContributionType | str
    difficulty_class: DifficultyClass | str
    influence_type: InfluenceType | str
    source_evidence: tuple[SourceEvidenceReference, ...]
    event_status: Patch300ActivationState = Patch300ActivationState.CONTRACT_ONLY_NOT_PERSISTED
    validation_state: Patch300ActivationState = Patch300ActivationState.VALIDATION_DISABLED
    finalized: bool = False
    mint_requested: bool = False
    ledger_write_requested: bool = False
    public_output_requested: bool = False
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.event_id or not isinstance(self.event_id, str):
            raise ContractValueError("event_id is required for contract validation")
        assert_utc_timestamp_z(self.timestamp_contributed, "timestamp_contributed")
        if not _SHA256_RE.fullmatch(self.proof_hash):
            raise ContractValueError("proof_hash must be a lowercase SHA-256 action-proof reference")
        object.__setattr__(self, "contribution_type", parse_enum(ContributionType, self.contribution_type, "contribution_type"))
        object.__setattr__(self, "difficulty_class", parse_enum(DifficultyClass, self.difficulty_class, "difficulty_class"))
        object.__setattr__(self, "influence_type", parse_enum(InfluenceType, self.influence_type, "influence_type"))
        if not self.source_evidence:
            raise ContractValueError("a Contribution Event contract requires at least one source evidence reference")
        if self.event_status is not Patch300ActivationState.CONTRACT_ONLY_NOT_PERSISTED:
            raise ContractValueError("Patch 300 Contribution Events are contract-only and not persisted")
        if self.validation_state is not Patch300ActivationState.VALIDATION_DISABLED:
            raise ContractValueError("Patch 300 cannot validate a real Contribution Event")
        if self.finalized or self.mint_requested or self.ledger_write_requested or self.public_output_requested:
            raise ContractValueError("Patch 300 rejects finalization, mint, ledger-write, and public-output claims")

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "schema_version": self.schema_version,
            "object_type": ContractObjectType.CONTRIBUTION_EVENT.value,
            "event_id": self.event_id,
            "event_status": self.event_status.value,
            "validation_state": self.validation_state.value,
            "contributor": self.contributor.as_dict(),
            "timestamp_contributed": self.timestamp_contributed,
            "proof_hash": self.proof_hash,
            "contribution_type": self.contribution_type.value,
            "difficulty_class": self.difficulty_class.value,
            "influence_type": self.influence_type.value,
            "source_evidence": [item.as_dict() for item in self.source_evidence],
            "finalized": self.finalized,
            "mint_requested": self.mint_requested,
            "ledger_write_requested": self.ledger_write_requested,
            "public_output_requested": self.public_output_requested,
            "persistence_authorized": False,
            "mint_authorized": False,
            "ledger_write_authorized": False,
            "public_output_authorized": False,
        }
        reject_raw_private_identity(payload)
        return payload
