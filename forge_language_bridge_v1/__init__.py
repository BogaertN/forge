"""Forge language-core replacement Bridge 1.

This package provides one bounded deterministic interpretation layer in front
of the historical Qwen/Ollama fallback. It does not replace Forge, grant tool
authority, execute shell, run simulations, or write source or memory.
"""

from .interpreter import (
    BRIDGE_MODE,
    BRIDGE_VERSION,
    bridge_status,
    decision_to_plan,
    interpret_request,
)

__all__ = (
    "BRIDGE_MODE",
    "BRIDGE_VERSION",
    "bridge_status",
    "decision_to_plan",
    "interpret_request",
)
