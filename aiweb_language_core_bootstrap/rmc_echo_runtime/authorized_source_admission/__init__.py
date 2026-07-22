"""AI.Web Slice 43C exact authorized source admission."""

from .admission import (
    admit_authorized_meaning_and_proposed_expression,
    build_source_admission_request,
)
from .authority import *
from .canonical import *
from .identity import *
from .rules import *
from .schema import *
from .validation import *

__all__ = tuple(name for name in globals() if not name.startswith("_"))
