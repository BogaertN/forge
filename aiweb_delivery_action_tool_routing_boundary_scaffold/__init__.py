"""Slice 20 delivery/action/tool-routing boundary scaffold.

This package records a negative authority boundary only. It does not route,
invoke, execute, deliver, send, deploy, or approve any real-world action.
"""

from .core import SLICE_ID, SLICE_TITLE, build_boundary_record, get_boundary_record
from .verify import verify_slice20_boundary

__all__ = [
    "SLICE_ID",
    "SLICE_TITLE",
    "build_boundary_record",
    "get_boundary_record",
    "verify_slice20_boundary",
]
