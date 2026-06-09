"""Patch 300 - Inactive identity and consent reference contracts.

Identity Vault remains the authority for identity and consent. These objects are
shape-only references and cannot enroll, disclose, or authorize a contributor.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping

from .enums import ConsentPermission, ContractObjectType, ContractValueError, Patch300ActivationState

SCHEMA_VERSION = "contributor_identity_consent_reference_contract_v1_patch300"
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")
_RAW_PRIVATE_IDENTITY_KEYS = frozenset(
    {
        "legal_name", "full_name", "first_name", "last_name", "email", "phone",
        "address", "date_of_birth", "ssn", "government_id", "biometric_data",
        "private_identity", "payment_account", "wallet_private_key",
    }
)


def reject_raw_private_identity(payload: Mapping[str, Any], *, field_prefix: str = "payload") -> None:
    """Reject raw private identity fields from public/capsule-shaped data."""
    def walk(value: Any, path: str) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                normalized = str(key).strip().lower()
                if normalized in _RAW_PRIVATE_IDENTITY_KEYS:
                    raise ContractValueError(f"raw private identity field prohibited at {path}.{key}")
                walk(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")
    walk(payload, field_prefix)


@dataclass(frozen=True)
class ConsentScopeReferenceContract:
    consent_record_id: str
    attribution: ConsentPermission = ConsentPermission.NOT_AUTHORIZED
    storage: ConsentPermission = ConsentPermission.NOT_AUTHORIZED
    public_display: ConsentPermission = ConsentPermission.NOT_AUTHORIZED
    portability: ConsentPermission = ConsentPermission.NOT_AUTHORIZED
    economic_processing: ConsentPermission = ConsentPermission.NOT_AUTHORIZED
    lifecycle_status: Patch300ActivationState = Patch300ActivationState.DEFINED_DISABLED
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.consent_record_id or not isinstance(self.consent_record_id, str):
            raise ContractValueError("consent_record_id is required as an opaque reference")
        if self.lifecycle_status is not Patch300ActivationState.DEFINED_DISABLED:
            raise ContractValueError("Patch 300 accepts only disabled consent references")
        permissions = (
            self.attribution, self.storage, self.public_display,
            self.portability, self.economic_processing,
        )
        if any(permission is not ConsentPermission.NOT_AUTHORIZED for permission in permissions):
            raise ContractValueError("Patch 300 cannot authorize a consent permission")

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "object_type": ContractObjectType.CONSENT_SCOPE_REFERENCE.value,
            "consent_record_id": self.consent_record_id,
            "consent_scope": {
                "attribution": self.attribution.value,
                "storage": self.storage.value,
                "public_display": self.public_display.value,
                "portability": self.portability.value,
                "economic_processing": self.economic_processing.value,
            },
            "lifecycle_status": self.lifecycle_status.value,
            "identity_vault_write_authorized": False,
            "consent_enrollment_authorized": False,
        }


@dataclass(frozen=True)
class ContributorPrincipalReferenceContract:
    principal_id: str
    pseudonymous_alias_id: str | None
    identity_proof_reference: str
    consent: ConsentScopeReferenceContract
    lifecycle_status: Patch300ActivationState = Patch300ActivationState.DEFINED_DISABLED
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.principal_id, str) or not self.principal_id:
            raise ContractValueError("principal_id is required as an opaque Identity Vault reference")
        if self.pseudonymous_alias_id is not None and not self.pseudonymous_alias_id:
            raise ContractValueError("pseudonymous_alias_id must be null or a non-empty opaque reference")
        if not _HASH_RE.fullmatch(self.identity_proof_reference):
            raise ContractValueError("identity_proof_reference must be a lowercase SHA-256 reference")
        if self.lifecycle_status is not Patch300ActivationState.DEFINED_DISABLED:
            raise ContractValueError("Patch 300 accepts only disabled principal references")

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "schema_version": self.schema_version,
            "object_type": ContractObjectType.CONTRIBUTOR_PRINCIPAL_REFERENCE.value,
            "principal_id": self.principal_id,
            "pseudonymous_alias_id": self.pseudonymous_alias_id,
            "identity_proof_reference": self.identity_proof_reference,
            "consent": self.consent.as_dict(),
            "lifecycle_status": self.lifecycle_status.value,
            "raw_private_identity_stored": False,
            "identity_vault_write_authorized": False,
            "public_disclosure_authorized": False,
        }
        reject_raw_private_identity(payload)
        return payload
