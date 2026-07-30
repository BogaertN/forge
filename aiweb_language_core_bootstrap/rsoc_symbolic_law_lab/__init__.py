"""Forge-owned, isolated, preview-only RSOC law laboratory."""

from .laws import RSOC_LAW_REGISTRY, law_for_glyph, rsoc_law_registry
from .runtime import build_symbolic_field_state, preview_rsoc_law
from .schema import (
    MICRO_SCALE,
    RSOC_LAW_LAB_SCHEMA_VERSION,
    RsocLawBoundary,
    RsocLawDefinition,
    RsocLawPreviewResult,
    RsocLawStatus,
    SymbolicFieldState,
)

__all__ = (
    "MICRO_SCALE",
    "RSOC_LAW_LAB_SCHEMA_VERSION",
    "RSOC_LAW_REGISTRY",
    "RsocLawBoundary",
    "RsocLawDefinition",
    "RsocLawPreviewResult",
    "RsocLawStatus",
    "SymbolicFieldState",
    "build_symbolic_field_state",
    "law_for_glyph",
    "preview_rsoc_law",
    "rsoc_law_registry",
)
