"""
forge/rmc_engine_v1/mea/discovery_kernel.py

Patch 275R — MEA / Forge Discovery Kernel Foundation Identity.

This module makes the Forge Discovery Kernel visible as a read-only foundation
surface without activating the later MEA runtime. It does not evolve live
problems, write files, call an LLM, execute shell commands, seed manifests, seal
candidates, or promote memory.

The full Discovery Kernel described by the MEA architecture document eventually
instantiates live problem manifests and calls operator registry, candidate
generator, scoring chain, gate engine, seal engine, claim classifier, and memory
writer. Patch 275R is not that full runtime. It is the stable kernel foundation
used to prove that the schema and unknown-vector layer are present and bounded.
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

KERNEL_NAME = "Forge Discovery Kernel"
KERNEL_STAGE = "foundation_identity_only"
KERNEL_PATCH_ID = "Patch 275R — MEA / Forge Discovery Kernel Foundation Visibility"
KERNEL_PACKAGE_PATH = "forge/rmc_engine_v1/mea/"
KERNEL_MODULE_PATH = "forge/rmc_engine_v1/mea/discovery_kernel.py"


@dataclass(frozen=True)
class KernelBoundary:
    """Immutable boundary declaration for the Patch 275R kernel surface."""

    read_only: bool = True
    writes_files: bool = False
    writes_memory: bool = False
    writes_chroma: bool = False
    writes_identity_vault: bool = False
    executes_shell: bool = False
    calls_llm: bool = False
    creates_post_routes: bool = False
    seeds_live_manifests: bool = False
    seals_candidates: bool = False
    promotes_to_memory: bool = False
    mutates_rmc_behavior: bool = False
    mutates_launcher_behavior: bool = False
    mutates_operator_console_ui: bool = False

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
        }


@dataclass(frozen=True)
class ForgeDiscoveryKernelFoundation:
    """Read-only foundation facade for MEA discovery-kernel readiness checks."""

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
        merged = dict(base)
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
            "next_runtime_layers": [
                "Patch 276 proof_debt_scorer.py + information_gain_scorer.py",
                "Patch 277 convergence_scorer.py + goal_ancestry_scorer.py + operator_cost_scorer.py",
                "Patch 278 operator_registry.py + replay_engine.py",
                "Patch 279 claim_status_classifier.py",
                "Patch 280 read-only MEA API / Operator Console visibility",
            ],
            "boundary": self.boundary(),
        }

    def inspect_manifest(self, manifest: ProblemManifest) -> Dict[str, Any]:
        """Return deterministic validation + unknown-vector status for one manifest."""
        validation = validate_manifest(manifest)
        vector = detect_unknowns(manifest)
        return {
            "kernel_name": self.kernel_name,
            "kernel_stage": self.kernel_stage,
            "problem_id": manifest.problem_id,
            "manifest_hash": canonical_hash(manifest),
            "validation": {"valid": validation.valid, "errors": list(validation.errors), "warnings": list(validation.warnings)},
            "unknown_vector": vector.to_dict(),
            "claim_status": manifest.claim_status,
            "proof_debt": manifest.proof_debt,
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
    }
