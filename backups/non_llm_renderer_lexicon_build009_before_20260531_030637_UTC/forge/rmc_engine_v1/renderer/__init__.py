"""MEA-specific renderer corridor adapters.

Build 008 introduces the MEA-to-RMC render-admission gate only.  No
language renderer, semantic lexicon, surface realizer, Echo Validator
approval, route, UI action, or write behavior is activated by this package.
"""
from .mea_render_gate import (
    ADAPTER_PACKET_SCHEMA_VERSION,
    BUILD_ID,
    PERMITTED_FUTURE_OUTPUT_MODE,
    SCHEMA_VERSION,
    SOURCE_KIND,
    build_historical_hypothesis_admission_request,
    evaluate_mea_render_admission_request,
    mea_render_gate_boundary,
    mea_render_gate_status,
)

__all__ = [
    "ADAPTER_PACKET_SCHEMA_VERSION",
    "BUILD_ID",
    "PERMITTED_FUTURE_OUTPUT_MODE",
    "SCHEMA_VERSION",
    "SOURCE_KIND",
    "build_historical_hypothesis_admission_request",
    "evaluate_mea_render_admission_request",
    "mea_render_gate_boundary",
    "mea_render_gate_status",
]
