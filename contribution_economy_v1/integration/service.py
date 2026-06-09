"""Local typed integration service: Identity Vault → Event → Capsule → Validation → Denial gates."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping
from ..capsules.current_mea_adapter import build_current_committed_mea_capsule_preview
from ..capsules.candidate_engine import build_identity_bound_capsule_candidate
from ..events.engine import compile_contribution_event
from ..gates.economic_gates import evaluate_finalization, evaluate_mint, evaluate_influence_write, evaluate_investment_write, gate_manifest
from ..identity_vault.multiuser_authority import resolve_authority_receipt, verify_multiuser_authority_schema
from ..ledgers import verify_dual_ledger_store
from ..storage.core_store import verify_core_store
from ..validation.engine import validate_capsule_candidate
from ..integrated_core.policy import BUILD_ID, integrated_boundary_manifest

class IntegratedContributionEconomyCore:
    def __init__(self, forge_root: Path, identity_vault_root: Path):
        self.forge_root = Path(forge_root).resolve(); self.identity_vault_root = Path(identity_vault_root).resolve()
    def status(self) -> dict[str, Any]:
        return {"schema_version": "ce_integrated_core_status_v1_build002", "build_id": BUILD_ID,
                "boundary": integrated_boundary_manifest(), "identity_authority_schema": verify_multiuser_authority_schema(self.identity_vault_root),
                "dual_ledgers": verify_dual_ledger_store(self.forge_root / "memory" / "contribution_economy_v1" / "ledgers"),
                "core_store": verify_core_store(self.forge_root / "memory" / "contribution_economy_v1" / "core"), "gates": gate_manifest()}
    def mea_compatibility_preview(self) -> dict[str, Any]:
        return build_current_committed_mea_capsule_preview(forge_root=self.forge_root)
    def evaluate_identity_bound_candidate(self, principal_id: str, action: Mapping[str, Any], source_artifact: Mapping[str, Any] | None = None) -> dict[str, Any]:
        authority = resolve_authority_receipt(self.identity_vault_root, principal_id)
        event = compile_contribution_event(authority, action)
        candidate = build_identity_bound_capsule_candidate(event, source_artifact)
        validation = validate_capsule_candidate(candidate, authority)
        return {"schema_version": "ce_integrated_in_memory_evaluation_v1_build002", "build_id": BUILD_ID, "authority_receipt": authority,
                "contribution_event": event, "capsule_candidate": candidate, "validation_record": validation,
                "finalization_gate": evaluate_finalization(validation), "mint_gate": evaluate_mint(None),
                "influence_ledger_gate": evaluate_influence_write(None), "investment_ledger_gate": evaluate_investment_write(None),
                "writes_live_state": False, "mints_ct": False}
