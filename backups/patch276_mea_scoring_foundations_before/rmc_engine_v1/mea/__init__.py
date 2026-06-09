"""
forge/rmc_engine_v1/mea/__init__.py

Manifest Evolution Algebra (MEA) — Forge Discovery Kernel foundation.
Patch 275 adds the first read-only MEA runtime package inside Forge.

Layer boundary:
- RMC compiles meaning for the current utterance or step.
- MEA evolves unresolved problem manifests over multiple cycles.
- This package does not write memory, call an LLM, execute shell commands, or
  alter existing RMC runtime behavior.
"""

from .manifest_schema import (
    MEA_SCHEMA_VERSION,
    MEA_PATCH_ID,
    ProblemManifest,
    CandidateManifest,
    ClaimStatus,
    OutputPermission,
    PhaseState,
    DriftState,
    OperatorTrace,
    MemoryRef,
    Assumption,
    ValidationResult,
    build_manifest,
    build_144hz_test_manifest,
    canonical_hash,
    canonical_dict,
    validate_manifest,
    to_dict,
    from_dict,
    foundation_boundary,
)
from .unknown_detector import (
    detect_unknowns,
    UnknownVector,
    UnknownGap,
    GapType,
)

from .discovery_kernel import (
    KERNEL_NAME,
    KERNEL_STAGE,
    KERNEL_PATCH_ID,
    ForgeDiscoveryKernelFoundation,
    build_foundation_kernel,
    kernel_identity,
    kernel_foundation_probe,
)

MEA_VERSION = MEA_SCHEMA_VERSION
MEA_PATCH = KERNEL_PATCH_ID
MEA_LAYER = "foundation"
MEA_FORGE_BASE = "Patch 274R rebased from uploaded current-state packet"

__all__ = [
    "MEA_VERSION",
    "MEA_PATCH",
    "MEA_LAYER",
    "MEA_FORGE_BASE",
    "MEA_SCHEMA_VERSION",
    "MEA_PATCH_ID",
    "ProblemManifest",
    "CandidateManifest",
    "ClaimStatus",
    "OutputPermission",
    "PhaseState",
    "DriftState",
    "OperatorTrace",
    "MemoryRef",
    "Assumption",
    "ValidationResult",
    "build_manifest",
    "build_144hz_test_manifest",
    "canonical_hash",
    "canonical_dict",
    "validate_manifest",
    "to_dict",
    "from_dict",
    "foundation_boundary",
    "detect_unknowns",
    "UnknownVector",
    "UnknownGap",
    "GapType",
    "KERNEL_NAME",
    "KERNEL_STAGE",
    "KERNEL_PATCH_ID",
    "ForgeDiscoveryKernelFoundation",
    "build_foundation_kernel",
    "kernel_identity",
    "kernel_foundation_probe",
]
