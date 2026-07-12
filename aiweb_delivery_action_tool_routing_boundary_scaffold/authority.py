"""Authority separation record for Slice 20.

Recognizing a requested capability is not the same as permission to perform
that capability. This file only records that separation; it does not create any
route, dispatcher, transport, or tool execution path.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Final

_AUTHORITY_LAYERS: Final[tuple[str, ...]] = (
    "language_understanding_layer",
    "capability_reference_layer",
    "permission_gate_layer",
    "action_invocation_layer",
    "delivery_transport_layer",
)

_DENIED_COLLAPSES: Final[tuple[tuple[str, str], ...]] = (
    ("language_understanding_layer", "action_invocation_layer"),
    ("capability_reference_layer", "action_invocation_layer"),
    ("capability_reference_layer", "delivery_transport_layer"),
    ("permission_gate_layer", "delivery_transport_layer_without_explicit_future_authority"),
)

@dataclass(frozen=True, slots=True)
class AuthoritySeparationRecord:
    authority_layers: tuple[str, ...]
    denied_collapses: tuple[tuple[str, str], ...]
    permission_required_for_invocation: bool
    permission_required_for_delivery: bool
    permission_required_for_code_execution: bool
    permission_required_for_sending_drafts: bool
    this_scaffold_grants_permission: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_authority_separation_record() -> AuthoritySeparationRecord:
    return AuthoritySeparationRecord(
        authority_layers=_AUTHORITY_LAYERS,
        denied_collapses=_DENIED_COLLAPSES,
        permission_required_for_invocation=True,
        permission_required_for_delivery=True,
        permission_required_for_code_execution=True,
        permission_required_for_sending_drafts=True,
        this_scaffold_grants_permission=False,
    )
