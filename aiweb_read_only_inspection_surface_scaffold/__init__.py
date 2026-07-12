"""Slice 21 read-only inspection surface boundary scaffold.

This package records inspection visibility rules only. It does not register
routes, integrate UI, modify configuration, widen accepted scope, create
acceptance, write memory, invoke tools, deliver output, fetch resources, or
grant runtime authority.
"""

from .core import SLICE_ID, SLICE_TITLE, build_inspection_surface_record, get_inspection_surface_record
from .verify import verify_slice21_boundary

__all__ = [
    "SLICE_ID",
    "SLICE_TITLE",
    "build_inspection_surface_record",
    "get_inspection_surface_record",
    "verify_slice21_boundary",
]
