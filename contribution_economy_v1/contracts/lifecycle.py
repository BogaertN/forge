"""Patch 300 - Lifecycle gate for contract-only Contribution Economy objects."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .enums import ContractObjectType, Patch300ActivationState, parse_enum

SCHEMA_VERSION = "contribution_economy_lifecycle_gate_v1_patch300"

_FORBIDDEN_ACTIVATION_TARGETS = frozenset(
    {
        "persisted", "validated", "finalized", "minted", "ledger_written",
        "publicly_disclosed", "portable", "penalized", "burned", "money_processed",
    }
)


@dataclass(frozen=True)
class LifecycleDecision:
    object_type: ContractObjectType
    from_state: Patch300ActivationState
    requested_target: str
    allowed: bool
    reason_code: str
    schema_version: str = SCHEMA_VERSION

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "object_type": self.object_type.value,
            "from_state": self.from_state.value,
            "requested_target": self.requested_target,
            "allowed": self.allowed,
            "reason_code": self.reason_code,
            "writes_state": False,
            "economic_action_authorized": False,
        }


def evaluate_lifecycle_transition(
    object_type: ContractObjectType | str,
    from_state: Patch300ActivationState | str,
    requested_target: str,
) -> LifecycleDecision:
    """Reject every activation transition while Patch 300 remains contract-only."""
    parsed_type = parse_enum(ContractObjectType, object_type, "object_type")
    parsed_state = parse_enum(Patch300ActivationState, from_state, "from_state")
    target = str(requested_target or "").strip()
    if target in _FORBIDDEN_ACTIVATION_TARGETS:
        reason = "PATCH300_ACTIVATION_TARGET_FORBIDDEN"
    else:
        reason = "PATCH300_CONTRACT_ONLY_NO_LIVE_TRANSITIONS"
    return LifecycleDecision(parsed_type, parsed_state, target, False, reason)


def patch300_boundary_manifest() -> dict[str, Any]:
    """Return the non-mutating Patch 300 authorization boundary."""
    return {
        "schema_version": "contribution_economy_boundary_v1_patch300",
        "patch_id": "Patch 300 - Contribution Economy Contract Foundation / No-Write Schema and Policy Kernel",
        "subsystem_path": "forge/contribution_economy_v1/",
        "contract_foundation_only": True,
        "routes_exposed": False,
        "writes_files": False,
        "writes_runtime_state": False,
        "writes_memory": False,
        "writes_rmc_memory": False,
        "writes_jsonl_ledger": False,
        "writes_chroma": False,
        "writes_identity_vault": False,
        "creates_contribution_event": False,
        "creates_memory_capsule": False,
        "finalizes_memory_capsule": False,
        "mints_contribution_tokens": False,
        "writes_influence_ledger": False,
        "writes_investment_ledger": False,
        "creates_nullification_event": False,
        "applies_penalty_or_burn": False,
        "renders_public_output": False,
        "calls_llm": False,
        "executes_shell": False,
        "performs_network_io": False,
        "modifies_mea": False,
        "modifies_rmc": False,
        "modifies_main_py": False,
    }
