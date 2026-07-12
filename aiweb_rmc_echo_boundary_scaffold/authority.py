"""Authority decisions for Slice 19 RMC Echo.

All runtime-like authority claims are denied in this scaffold. The only positive
claim is that Echo is recorded as a later separate authority layer.
"""

from __future__ import annotations

from .core import ECHO_RELATIONSHIP, IMPLEMENTATION_STATE, SLICE_ID, SLICE_TITLE

ECHO_AUTHORITY_LAYER = "later_separate_authority_layer"

ECHO_AUTHORITY_DENIALS: dict[str, str] = {
    "implementation": "RMC Echo validation is not implemented in Slice 19.",
    "delivery": "Echo validation is not delivery.",
    "public_release": "Echo validation is not public release.",
    "output_approval": "Echo validation is not output approval.",
    "renderer_authority": "Echo validation is not renderer authority.",
    "selected_meaning_authority": "Echo validation is not selected-meaning authority.",
    "source_authority": "Echo validation is not source authority.",
    "predicate_authority": "Echo validation is not predicate authority.",
    "concept_authority": "Echo validation is not concept authority.",
    "gp014": "Echo validation is not GP-014.",
    "gp015_repair": "Echo validation is not GP-015 repair.",
    "production_integration": "Echo validation is not production integration.",
}

_ALLOWED_POSITIVE_CLAIMS: dict[str, str] = {
    "separate_later_authority_layer": "Echo is represented as a separate later authority layer.",
    "boundary_scaffold": "Slice 19 records a boundary scaffold only.",
}


def authority_decision_for_claim(claim_key: str) -> dict[str, object]:
    """Return a deterministic decision for an authority claim.

    This function is a claim classifier for the scaffold. It is not an Echo
    validator and does not approve output.
    """

    normalized = claim_key.strip().lower().replace("-", "_").replace(" ", "_")

    if normalized in ECHO_AUTHORITY_DENIALS:
        return {
            "claim": normalized,
            "allowed": False,
            "decision": "denied_by_slice19_boundary",
            "reason": ECHO_AUTHORITY_DENIALS[normalized],
        }

    if normalized in _ALLOWED_POSITIVE_CLAIMS:
        return {
            "claim": normalized,
            "allowed": True,
            "decision": "allowed_as_boundary_description_only",
            "reason": _ALLOWED_POSITIVE_CLAIMS[normalized],
        }

    return {
        "claim": normalized,
        "allowed": False,
        "decision": "not_authorized_by_slice19",
        "reason": "Unknown Echo authority claims are not authorized by this scaffold.",
    }


def build_authority_report() -> dict[str, object]:
    """Build a deterministic authority report for inspection."""

    return {
        "slice": SLICE_ID,
        "title": SLICE_TITLE,
        "implementation_state": IMPLEMENTATION_STATE,
        "relationship": ECHO_RELATIONSHIP,
        "authority_layer": ECHO_AUTHORITY_LAYER,
        "denied_claims": dict(sorted(ECHO_AUTHORITY_DENIALS.items())),
        "allowed_descriptive_claims": dict(sorted(_ALLOWED_POSITIVE_CLAIMS.items())),
    }
