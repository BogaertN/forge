"""AI.Web Slice 25 repository-hygiene scaffold.

The package is read-only verification support.  Importing it does not move,
delete, patch, stage, commit, run, or accept anything.
"""

from .authority import SLICE25_TITLE, SLICE25_VERSION
from .verify import Slice25VerificationResult, verify_slice25_boundary

__all__ = [
    "SLICE25_TITLE",
    "SLICE25_VERSION",
    "Slice25VerificationResult",
    "verify_slice25_boundary",
]
