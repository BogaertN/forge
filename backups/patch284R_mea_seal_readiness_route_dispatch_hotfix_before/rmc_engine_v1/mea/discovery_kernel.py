"""
forge/rmc_engine_v1/mea/discovery_kernel.py

Patch 283 — MEA / Forge Discovery Kernel Hard Gate Report Identity.

This module exposes the Forge Discovery Kernel as a read-only foundation surface
with deterministic replay support. Patch 283 adds a non-mutating hard-gate report over candidate previews. It still does not
commit live MEA state, seal candidates, promote memory, call an LLM, execute
shell commands, or mutate UI/launcher behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .manifest_schema import (
    MEA_PATCH_ID,
    MEA_SCHEMA_VERSION,
    ProblemManifest,
    build_144hz_test_manifest,
    canonical_hash,
    foundation_boundary,
    validate_manifest,
)
from .unknown_detector import detect_unknowns
from .proof_debt_scorer import score_proof_debt
from .information_gain_scorer import score_information_gain
from .convergence_scorer import score_convergence
from .goal_ancestry_scorer import score_goal_ancestry
from .operator_cost_scorer import score_operator_cost
from .operator_registry import operator_registry_summary
from .replay_engine import replay_candidate, replay_engine_boundary
from .claim_status_classifier import classify_claim_status, claim_status_taxonomy, classifier_boundary
from .seed_manifest_gate import (
    SEED_GATE_POST_ROUTE,
    SEED_GATE_STATUS_ROUTE,
    SEED_GATE_ALIAS_ROUTE,
    SEED_GATE_APPROVAL_TOKEN,
    seed_manifest_gate_boundary,
    build_seed_manifest_gate_preview,
)
from .candidate_set_gate import (
    CANDIDATE_SET_GATE_POST_ROUTE,
    CANDIDATE_SET_GATE_STATUS_ROUTE,
    CANDIDATE_SET_GATE_ALIAS_ROUTE,
    CANDIDATE_SET_PREVIEW_ROUTE,
    CANDIDATE_SET_GATE_APPROVAL_TOKEN,
    candidate_set_gate_boundary,
    build_candidate_set_gate_preview,
)
from .hard_gate_report import (
    HARD_GATE_REPORT_STATUS_ROUTE,
    HARD_GATE_REPORT_PREVIEW_ROUTE,
    HARD_GATE_REPORT_POST_ROUTE,
    HARD_GATE_REPORT_ALIAS_ROUTE,
    HARD_GATE_REPORT_APPROVAL_TOKEN,
    hard_gate_report_boundary,
    build_hard_gate_report_preview,
)

from .seal_readiness import (
    SEAL_READINESS_APPROVAL_TOKEN,
    SEAL_READINESS_ALIAS_ROUTE,
    SEAL_READINESS_POST_ROUTE,
    SEAL_READINESS_PREVIEW_ROUTE,
    SEAL_READINESS_STATUS_ROUTE,
    build_seal_readiness_preview,
    seal_readiness_boundary,
)

KERNEL_NAME = "Forge Discovery Kernel"
KERNEL_STAGE = "seal_readiness_preview_patch284"
KERNEL_PATCH_ID = "Patch 284 — MEA Seal Readiness Preview / Seal Readiness Report"
KERNEL_PACKAGE_PATH = "forge/rmc_engine_v1/mea/"
KERNEL_MODULE_PATH = "forge/rmc_engine_v1/mea/discovery_kernel.py"


@dataclass(frozen=True)
class KernelBoundary:
    """Immutable boundary declaration for the Patch 280 kernel surface."""

    read_only: bool = False
    writes_files: bool = False
    writes_memory: bool = False
    writes_chroma: bool = False
    writes_identity_vault: bool = False
    executes_shell: bool = False
    calls_llm: bool = False
    creates_post_routes: bool = True
    seeds_live_manifests: bool = False
    seals_candidates: bool = False
    promotes_to_memory: bool = False
    mutates_rmc_behavior: bool = False
    mutates_launcher_behavior: bool = False
    mutates_operator_console_ui: bool = False
    renderer_integration: bool = False

    def to_dict(self) -> Dict[str, bool]:
        return {
            "read_only": self.read_only,
            "writes_files": self.writes_files,
            "writes_memory": self.writes_memory,
            "writes_chroma": self.writes_chroma,
            "writes_identity_vault": self.writes_identity_vault,
            "executes_shell": self.executes_shell,
            "calls_llm": self.calls_llm,
            "creates_post_routes": self.creates_post_routes,
            "seeds_live_manifests": self.seeds_live_manifests,
            "seals_candidates": self.seals_candidates,
            "promotes_to_memory": self.promotes_to_memory,
            "mutates_rmc_behavior": self.mutates_rmc_behavior,
            "mutates_launcher_behavior": self.mutates_launcher_behavior,
            "mutates_operator_console_ui": self.mutates_operator_console_ui,
            "renderer_integration": self.renderer_integration,
        }


@dataclass(frozen=True)
class ForgeDiscoveryKernelFoundation:
    """Read-only foundation facade for MEA replay-kernel readiness checks."""

    kernel_name: str = KERNEL_NAME
    kernel_stage: str = KERNEL_STAGE
    patch_id: str = KERNEL_PATCH_ID
    package_path: str = KERNEL_PACKAGE_PATH
    module_path: str = KERNEL_MODULE_PATH
    schema_version: str = MEA_SCHEMA_VERSION
    source_packet_lineage: str = "Claude MEA Foundation Patch A rebased and production-packaged against Patch 274R current-state packet"

    def boundary(self) -> Dict[str, bool]:
        base = foundation_boundary()
        declared = KernelBoundary().to_dict()
        replay_boundary = replay_engine_boundary()
        classifier = classifier_boundary()
        seed_gate = seed_manifest_gate_boundary()
        hard_gate = hard_gate_report_boundary()
        seal_ready = seal_readiness_boundary()
        merged = dict(base)
        merged.update({k: v for k, v in replay_boundary.items() if isinstance(v, bool)})
        merged.update({k: v for k, v in classifier.items() if isinstance(v, bool)})
        merged.update({k: v for k, v in seed_gate.items() if isinstance(v, bool)})
        merged.update({k: v for k, v in hard_gate.items() if isinstance(v, bool)})
        merged.update({k: v for k, v in seal_ready.items() if isinstance(v, bool)})
        merged.update(declared)
        return merged

    def identity(self) -> Dict[str, Any]:
        return {
            "kernel_name": self.kernel_name,
            "kernel_stage": self.kernel_stage,
            "patch_id": self.patch_id,
            "package_path": self.package_path,
            "module_path": self.module_path,
            "schema_version": self.schema_version,
            "mea_patch_id": MEA_PATCH_ID,
            "source_packet_lineage": self.source_packet_lineage,
            "full_runtime_active": False,
            "foundation_visible": True,
            "scoring_foundation_visible": True,
            "scoring_runtime_active": False,
            "convergence_scoring_visible": True,
            "goal_ancestry_scoring_visible": True,
            "operator_cost_scoring_visible": True,
            "operator_registry_visible": True,
            "replay_engine_visible": True,
            "replay_preview_active": True,
            "claim_status_classifier_visible": True,
            "claim_status_classification_active": True,
            "read_only_api_visible": True,
            "operator_console_visibility": "backend_route_manifest_and_read_only_json_payloads_only",
            "api_preview_routes": [
                "/api/mea/problem-manifest-preview",
                "/api/mea/unknown-vector-preview",
                "/api/mea/claim-status-preview",
                "/api/mea/replay-preview",
            ],
            "controlled_seed_gate_visible": True,
            "controlled_seed_gate_active": True,
            "seed_gate_post_route": SEED_GATE_POST_ROUTE,
            "seed_gate_status_route": SEED_GATE_STATUS_ROUTE,
            "seed_gate_alias_route": SEED_GATE_ALIAS_ROUTE,
            "seed_gate_approval_token": SEED_GATE_APPROVAL_TOKEN,
            "live_manifest_seeding_active": False,
            "candidate_set_gate_visible": True,
            "candidate_set_gate_active": True,
            "candidate_set_preview_route": CANDIDATE_SET_PREVIEW_ROUTE,
            "candidate_set_gate_post_route": CANDIDATE_SET_GATE_POST_ROUTE,
            "candidate_set_gate_status_route": CANDIDATE_SET_GATE_STATUS_ROUTE,
            "candidate_set_gate_alias_route": CANDIDATE_SET_GATE_ALIAS_ROUTE,
            "candidate_set_gate_approval_token": CANDIDATE_SET_GATE_APPROVAL_TOKEN,
            "hard_gate_report_visible": True,
            "hard_gate_report_active": True,
            "hard_gate_report_status_route": HARD_GATE_REPORT_STATUS_ROUTE,
            "hard_gate_report_preview_route": HARD_GATE_REPORT_PREVIEW_ROUTE,
            "hard_gate_report_post_route": HARD_GATE_REPORT_POST_ROUTE,
            "hard_gate_report_alias_route": HARD_GATE_REPORT_ALIAS_ROUTE,
            "hard_gate_report_approval_token": HARD_GATE_REPORT_APPROVAL_TOKEN,
            "live_candidate_commit_active": False,
            "sealing_active": False,
            "memory_promotion_active": False,
            "seal_readiness_visible": True,
            "seal_readiness_active": True,
            "seal_readiness_status_route": SEAL_READINESS_STATUS_ROUTE,
            "seal_readiness_preview_route": SEAL_READINESS_PREVIEW_ROUTE,
            "seal_readiness_post_route": SEAL_READINESS_POST_ROUTE,
            "seal_readiness_alias_route": SEAL_READINESS_ALIAS_ROUTE,
            "seal_readiness_approval_token": SEAL_READINESS_APPROVAL_TOKEN,
            "seal_route_available": False,
            "next_runtime_layers": [
                "Patch 276 proof_debt_scorer.py + information_gain_scorer.py — installed read-only",
                "Patch 277 convergence_scorer.py + goal_ancestry_scorer.py + operator_cost_scorer.py — installed read-only",
                "Patch 278 operator_registry.py + replay_engine.py — installed read-only",
                "Patch 279 claim_status_classifier.py — installed read-only",
                "Patch 280 read-only MEA API / Operator Console visibility — installed read-only",
                "Patch 281 controlled seed manifest gate — installed non-mutating approval-token POST",
                "Patch 282 candidate set preview/gate — installed non-mutating approval-token POST",
                "Patch 283R hard gate report — installed non-mutating approval-token POST",
                "Patch 284 seal readiness preview — installed non-mutating approval-token POST",
            ],
            "boundary": self.boundary(),
        }

    def inspect_manifest(self, manifest: ProblemManifest) -> Dict[str, Any]:
        """Return deterministic validation + scoring + replay status for one manifest."""
        validation = validate_manifest(manifest)
        vector = detect_unknowns(manifest)
        proof_score = score_proof_debt(manifest)
        info_score = score_information_gain(manifest, manifest)
        convergence_score = score_convergence(manifest, manifest)
        ancestry_score = score_goal_ancestry(manifest, manifest)
        operator_cost_score = score_operator_cost(manifest)
        replay_score = replay_candidate(manifest, "noop_recall", {}, expected_candidate_hash=canonical_hash(manifest))
        classification = classify_claim_status(
            manifest,
            manifest,
            replay_result=replay_score,
            proof_debt_score=proof_score,
            information_gain_score=info_score,
            convergence_score=convergence_score,
        )
        return {
            "kernel_name": self.kernel_name,
            "kernel_stage": self.kernel_stage,
            "problem_id": manifest.problem_id,
            "manifest_hash": canonical_hash(manifest),
            "validation": {"valid": validation.valid, "errors": list(validation.errors), "warnings": list(validation.warnings)},
            "unknown_vector": vector.to_dict(),
            "claim_status": manifest.claim_status,
            "proof_debt": manifest.proof_debt,
            "proof_debt_score": proof_score.to_dict(),
            "information_gain_self_score": info_score.to_dict(),
            "convergence_self_score": convergence_score.to_dict(),
            "goal_ancestry_self_score": ancestry_score.to_dict(),
            "operator_cost_self_score": operator_cost_score.to_dict(),
            "replay_self_score": replay_score.to_dict(),
            "claim_status_classification": classification.to_dict(),
            "output_permissions": manifest.output_permissions,
            "boundary": self.boundary(),
        }

    def inspect_144hz_fixture(self) -> Dict[str, Any]:
        manifest = build_144hz_test_manifest()
        report = self.inspect_manifest(manifest)
        report["expected_future_classification"] = "hypothesis_not_verified_claim"
        report["anti_confabulation_purpose"] = (
            "The 144 Hz seed must remain test_required/hypothesis-bound until later MEA scoring "
            "and claim classification can prove otherwise. It must not render as verified_claim."
        )
        return report

    def replay_registry_report(self) -> Dict[str, Any]:
        return {
            "operator_registry": operator_registry_summary(),
            "replay_boundary": replay_engine_boundary(),
            "claim_status_taxonomy": claim_status_taxonomy(),
            "seed_manifest_gate_preview": build_seed_manifest_gate_preview(),
            "candidate_set_gate_preview": build_candidate_set_gate_preview(),
            "hard_gate_report_preview": build_hard_gate_report_preview(),
        }


def build_foundation_kernel() -> ForgeDiscoveryKernelFoundation:
    """Factory used by status routes and tests. No side effects."""
    return ForgeDiscoveryKernelFoundation()


def kernel_identity() -> Dict[str, Any]:
    """Return a read-only identity payload for the foundation kernel."""
    return build_foundation_kernel().identity()


def kernel_foundation_probe() -> Dict[str, Any]:
    """Return identity plus the 144 Hz seed probe. No side effects."""
    kernel = build_foundation_kernel()
    return {
        "identity": kernel.identity(),
        "test_fixture": kernel.inspect_144hz_fixture(),
        "replay_foundation": kernel.replay_registry_report(),
    }
