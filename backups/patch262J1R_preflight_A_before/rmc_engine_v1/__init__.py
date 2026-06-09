"""AI.Web Forge RMC Engine v1.

Patch 262I2 creates the first explicit RMC math-kernel boundary. UI and HTTP
routes may display or request RMC state, but formal scoring logic lives here.
"""

from .coherence_math import (
    clamp,
    phase_num,
    gate_thresholds,
    extract_math_terms,
    formal_math_binding,
    score_candidate,
)

__all__ = [
    "clamp",
    "phase_num",
    "gate_thresholds",
    "extract_math_terms",
    "formal_math_binding",
    "score_candidate",
]
