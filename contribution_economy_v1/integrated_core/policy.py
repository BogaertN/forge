"""Activation policy for the integrated multi-user Contribution Economy core.

Build 002 installs real multi-user authority, proof compilation, candidate construction,
validation, and empty persistence structures.  Economic and contribution-bearing live
writes remain deny-by-default until later controlled approvals exist.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

BUILD_ID = "CE-INTEGRATED-MULTIUSER-CORE-BUILD-002"
SCHEMA_VERSION = "ce_integrated_multiuser_activation_policy_v1_build002"


@dataclass(frozen=True)
class ActivationPolicy:
    build_id: str = BUILD_ID
    schema_version: str = SCHEMA_VERSION
    initialize_identity_authority_schema: bool = True
    initialize_core_store_schema: bool = True
    resolve_identity_authority: bool = True
    register_approved_existing_identity_principal: bool = True
    append_limited_internal_consent_event: bool = True
    compile_contribution_event: bool = True
    build_capsule_candidate: bool = True
    execute_candidate_validation: bool = True
    persist_live_contribution_event: bool = False
    persist_live_capsule_candidate: bool = False
    persist_live_validation_record: bool = False
    finalize_memory_capsule: bool = False
    mint_ct: bool = False
    write_influence_ledger: bool = False
    write_investment_ledger: bool = False
    create_nullification_or_penalty_event: bool = False
    public_identity_disclosure: bool = False
    identity_portability: bool = False
    expose_api_routes: bool = False
    write_mea_state: bool = False
    write_rmc_output_memory: bool = False
    write_chroma: bool = False
    call_llm: bool = False
    perform_network_io: bool = False
    economic_consent_may_be_granted_in_this_build: bool = False
    public_display_consent_may_be_granted_in_this_build: bool = False

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["policy_class"] = "live_build002_deny_by_default_integrated_core"
        return payload


LIVE_POLICY = ActivationPolicy()


def integrated_boundary_manifest() -> dict[str, Any]:
    return {
        "schema_version": "ce_integrated_multiuser_boundary_manifest_v1_build002",
        "build_id": BUILD_ID,
        "subsystem_path": "forge/contribution_economy_v1/",
        "integration_authorities": {
            "identity_and_consent": "Identity Vault canonical SQLite database",
            "source_artifact_evidence": "MEA typed evidence adapter only",
            "contribution_governance": "Contribution Economy integrated core",
            "ct_policy": "Patch 300 integer milli-CT reward policy",
            "economic_endpoints": ["Influence Ledger", "Investment Ledger"],
        },
        "live_activation_policy": LIVE_POLICY.as_dict(),
        "forbidden_substitutions": [
            "MEA hypothesis is not a contribution",
            "MEA source-artifact proof is not contributor-action proof",
            "Identity Vault principal is not CT eligibility",
            "Memory Capsule candidate is not a finalized capsule",
            "validation is not minting",
            "investment is not CT and not authorship",
        ],
    }
