"""Stable RMC phase entrypoint backed by LC-RMC-001 Language Core.

``parse_phase`` remains the public RMC compatibility entrypoint. Human
language interpretation is delegated to the bounded deterministic Language
Core runtime and then mapped into the historical phase-report shape. The
withdrawn keyword classifier is not retained as a fallback.
"""

from __future__ import annotations

from typing import Any

from rmc_engine_v1.language_core_phase_adapter import (
    ADAPTER_VERSION,
    interpret_phase,
    phase_adapter_boundary,
)


ENGINE_VERSION = "rmc_phase_parser_lc_rmc_001_v1"


def phase_parser_boundary() -> dict[str, Any]:
    """Machine-readable boundary for the stable compatibility entrypoint."""

    adapter = phase_adapter_boundary()
    return {
        "engine_version": ENGINE_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "engine_module_location": "forge/rmc_engine_v1/phase_parser.py",
        "ui_owns_phase_logic": False,
        "main_py_owns_phase_logic": False,
        "engine_module_owns_phase_logic": True,
        "deterministic_language_core_owns_interpretation": True,
        "legacy_keyword_interpretation_active": False,
        "legacy_heuristic_fallback": False,
        "side_effect_free": True,
        "calls_llm": False,
        "queries_chroma": False,
        "reads_db_files": False,
        "writes_files": False,
        "writes_rmc_memory": False,
        "writes_identity_vault": False,
        "calls_main_py_functions": False,
        "source_text_supplied_by_adapter": True,
        "permission_authority": False,
        "route_authority": False,
        "tool_authority": False,
        "execution_authority": False,
        "output_authority": False,
        "delivery_authority": False,
        "adapter_boundary": adapter,
    }


def phase_catalog() -> dict[str, dict[str, Any]]:
    """Preserved read-only Φ1-Φ9 compatibility definitions."""

    return {
        "Φ1": {
            "index": 1,
            "role": "Initiation / seed",
            "routing": "establish_context",
        },
        "Φ2": {
            "index": 2,
            "role": "Polarity / contrast",
            "routing": "identify_poles",
        },
        "Φ3": {
            "index": 3,
            "role": "Desire / vector",
            "routing": "identify_direction",
        },
        "Φ4": {
            "index": 4,
            "role": "Friction / constraint",
            "routing": "surface_constraint",
        },
        "Φ5": {
            "index": 5,
            "role": "Entropy / drift",
            "routing": "drift_analyzer_required",
        },
        "Φ6": {
            "index": 6,
            "role": "Correction / coherence return",
            "routing": "correction_engine",
        },
        "Φ7": {
            "index": 7,
            "role": "Naming / identity lock",
            "routing": "naming_engine",
        },
        "Φ8": {
            "index": 8,
            "role": "Projection / outward expression",
            "routing": "projection_gate",
        },
        "Φ9": {
            "index": 9,
            "role": "Closure / octave transition",
            "routing": "closure_or_archive",
        },
    }


def parse_phase(
    source_text: str,
    source_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Interpret source through LC-RMC-001 and return the RMC phase report."""

    result = interpret_phase(source_text, source_metadata)
    result["engine_boundary"] = phase_parser_boundary()
    return result


__all__ = (
    "ENGINE_VERSION",
    "parse_phase",
    "phase_catalog",
    "phase_parser_boundary",
)
