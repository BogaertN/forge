"""Patch 300 - AI.Web Contribution Economy contract foundation.

This sibling package is deliberately inert: it defines and validates contract-only
shapes and policy arithmetic, exposes no service route, and performs no persistence.
"""
from .contracts import *  # noqa: F401,F403
from .contracts import CT_REWARD_POLICY_VERSION, patch300_boundary_manifest

PATCH_ID = "Patch 300 - Contribution Economy Contract Foundation / No-Write Schema and Policy Kernel"
SCHEMA_KERNEL_VERSION = "contribution_economy_contract_foundation_v1_patch300"
SUBSYSTEM_PATH = "forge/contribution_economy_v1/"


def kernel_identity() -> dict[str, object]:
    boundary = patch300_boundary_manifest()
    return {
        "patch_id": PATCH_ID,
        "schema_kernel_version": SCHEMA_KERNEL_VERSION,
        "ct_reward_policy_version": CT_REWARD_POLICY_VERSION,
        "subsystem_path": SUBSYSTEM_PATH,
        "contract_foundation_only": True,
        "boundary": boundary,
    }


__all__ = ["PATCH_ID", "SCHEMA_KERNEL_VERSION", "SUBSYSTEM_PATH", "kernel_identity"]
