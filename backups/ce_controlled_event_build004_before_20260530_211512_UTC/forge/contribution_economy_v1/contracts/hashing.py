"""Patch 300 - SHA-256 utilities for deterministic contract-only payload previews."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Mapping

from .canonical_json import canonical_utf8_bytes

HASH_ALGORITHM = "sha256"
HASHING_SCHEMA_VERSION = "contribution_economy_contract_hash_v1_patch300"


@dataclass(frozen=True)
class ContractHashPreview:
    """A calculated hash preview; it is not a persisted record or economic action."""

    hash_algorithm: str
    object_hash: str
    schema_version: str
    governed_schema_version: str
    ct_reward_policy_version: str | None
    persisted: bool = False
    economic_action_authorized: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "hash_algorithm": self.hash_algorithm,
            "object_hash": self.object_hash,
            "schema_version": self.schema_version,
            "governed_schema_version": self.governed_schema_version,
            "ct_reward_policy_version": self.ct_reward_policy_version,
            "persisted": self.persisted,
            "economic_action_authorized": self.economic_action_authorized,
        }


def hash_contract_payload(payload: Mapping[str, Any], *, require_policy_version: bool = False) -> ContractHashPreview:
    """Calculate a deterministic SHA-256 preview from canonical in-memory data only."""
    encoded = canonical_utf8_bytes(payload, require_policy_version=require_policy_version)
    return ContractHashPreview(
        hash_algorithm=HASH_ALGORITHM,
        object_hash=hashlib.sha256(encoded).hexdigest(),
        schema_version=HASHING_SCHEMA_VERSION,
        governed_schema_version=str(payload["schema_version"]),
        ct_reward_policy_version=(
            str(payload["ct_reward_policy_version"])
            if payload.get("ct_reward_policy_version") is not None
            else None
        ),
    )
