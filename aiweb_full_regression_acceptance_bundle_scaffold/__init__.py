"""Slice 24 full regression and acceptance bundle scaffold.

This package is intentionally inert unless an operator explicitly runs the
Slice 24 command runner. It does not register routes, write memory, promote
resources, deliver output, or execute user actions.
"""

from .authority import SLICE24_TITLE, SLICE24_VERSION
from .runner import build_acceptance_plan, run_acceptance_bundle
from .verify import verify_slice24_boundary

__all__ = [
    "SLICE24_TITLE",
    "SLICE24_VERSION",
    "build_acceptance_plan",
    "run_acceptance_bundle",
    "verify_slice24_boundary",
]
