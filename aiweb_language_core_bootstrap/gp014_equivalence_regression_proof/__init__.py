"""Slice 46 GP-014 equivalence and regression proof boundary.

Importing this package is inert. It does not import or call GP-014, register a
runtime component, create a route, connect a UI, write state, or authorize
release. The real proof executes only through an explicit test or verifier.
"""

from .authority import *
from .fixtures import *
from .schema import *
from .validation import *

__all__ = tuple(name for name in globals() if not name.startswith("_"))
