"""Public Slice 41E MSM-v1 selected-meaning integration API."""
from dataclasses import replace as _replace

from .authority import *
from .canonical import canonical_json_bytes, canonical_value, deterministic_digest, stable_identifier
from .identity import *
from .integration import integrate_selected_meaning_into_manifest
from .schema import *
from .validation import (
    assert_valid_integration_input,
    assert_valid_integration_result,
    validate_authority_profile,
    validate_integration_input,
    validate_integration_result,
)
from .identity import with_expected_profile_id
from .schema import APPROVED_STRICT_PROFILE as _UNBOUND_PROFILE

APPROVED_STRICT_PROFILE = with_expected_profile_id(_UNBOUND_PROFILE)

__all__ = tuple(name for name in globals() if not name.startswith("_"))
