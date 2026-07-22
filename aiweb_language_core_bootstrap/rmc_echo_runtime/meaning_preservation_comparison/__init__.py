"""AI.Web Slice 43D deterministic meaning-preservation comparison."""

from .authority import *
from .canonical import *
from .comparison import (
    build_comparison_request,
    build_dimension_finding,
    compare_meaning_preservation,
    make_dimension_snapshot,
)
from .identity import *
from .rules import *
from .schema import *
from .validation import *

__all__ = tuple(name for name in globals() if not name.startswith("_"))
