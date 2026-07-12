"""Core immutable records for Slice 20.

Slice 20 creates a boundary record between language understanding and actual
real-world action. The module is intentionally data-only. It has no router,
no tool dispatcher, no transport client, no shell bridge, no send operation,
and no execution operation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Final, Mapping

SLICE_ID: Final[str] = "Slice 20"
SLICE_TITLE: Final[str] = "Delivery, Action, and Tool-Routing Boundary Scaffold"
REQUIRED_BASE_HEAD_FOR_APPLICATION: Final[str] = "ba50a5147acd098a28772c2cb9b5101f37c3f57f"
REQUIRED_BASE_SUBJECT_FOR_APPLICATION: Final[str] = "Slice 19 RMC Echo boundary scaffold"
EXPECTED_COMMIT_SUBJECT: Final[str] = "Slice 20 delivery action tool-routing boundary scaffold"

_BOUNDARY_SENTINELS: Final[tuple[str, ...]] = (
    "understanding_is_not_doing",
    "capability_reference_is_not_invocation",
    "route_existence_is_not_permission",
    "draft_is_not_sent",
    "implementation_request_is_not_code_execution",
    "delivery_is_not_implemented",
    "action_execution_is_not_implemented",
    "tool_routing_is_not_implemented",
    "transport_is_not_implemented",
    "output_approval_is_not_granted",
    "renderer_authority_is_not_granted",
    "echo_validation_is_not_delivery",
    "echo_validation_is_not_public_release",
    "gp014_not_modified_imported_called_wrapped_or_promoted",
    "gp015_not_repaired",
)

_PROHIBITED_PROMOTIONS: Final[tuple[str, ...]] = (
    "delivery_implementation",
    "action_execution_implementation",
    "tool_invocation_implementation",
    "tool_router_activation",
    "transport_activation",
    "public_release_activation",
    "draft_send_activation",
    "code_execution_activation",
    "permission_grant_from_route_existence",
    "permission_grant_from_capability_reference",
)

@dataclass(frozen=True, slots=True)
class BoundaryRecord:
    """Immutable Slice 20 boundary record."""

    slice_id: str
    title: str
    understanding_request_boundary: str
    capability_reference_boundary: str
    route_existence_boundary: str
    draft_boundary: str
    implementation_request_boundary: str
    delivery_boundary: str
    action_boundary: str
    tool_routing_boundary: str
    transport_boundary: str
    output_approval_boundary: str
    renderer_authority_boundary: str
    echo_delivery_boundary: str
    gp014_boundary: str
    gp015_boundary: str
    prohibited_promotions: tuple[str, ...]
    sentinel_count: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_boundary_record() -> BoundaryRecord:
    """Build the canonical Slice 20 boundary record without side effects."""
    return BoundaryRecord(
        slice_id=SLICE_ID,
        title=SLICE_TITLE,
        understanding_request_boundary="understanding_is_not_doing",
        capability_reference_boundary="capability_reference_is_not_invocation",
        route_existence_boundary="route_existence_is_not_permission",
        draft_boundary="draft_is_not_sent",
        implementation_request_boundary="implementation_request_is_not_code_execution",
        delivery_boundary="delivery_is_not_implemented",
        action_boundary="action_execution_is_not_implemented",
        tool_routing_boundary="tool_routing_is_not_implemented",
        transport_boundary="transport_is_not_implemented",
        output_approval_boundary="output_approval_is_not_granted",
        renderer_authority_boundary="renderer_authority_is_not_granted",
        echo_delivery_boundary="echo_validation_is_not_delivery;echo_validation_is_not_public_release",
        gp014_boundary="gp014_not_modified_imported_called_wrapped_or_promoted",
        gp015_boundary="gp015_not_repaired",
        prohibited_promotions=_PROHIBITED_PROMOTIONS,
        sentinel_count=len(_BOUNDARY_SENTINELS),
    )


def get_boundary_record() -> Mapping[str, object]:
    return build_boundary_record().to_dict()


def get_required_sentinels() -> tuple[str, ...]:
    return _BOUNDARY_SENTINELS


def get_prohibited_promotions() -> tuple[str, ...]:
    return _PROHIBITED_PROMOTIONS
