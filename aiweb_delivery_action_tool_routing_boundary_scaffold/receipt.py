"""Receipt builder for Slice 20."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping

from .authority import build_authority_separation_record
from .boundary import check_boundary_integrity
from .core import SLICE_ID, SLICE_TITLE, build_boundary_record

@dataclass(frozen=True, slots=True)
class Slice20Receipt:
    slice_id: str
    title: str
    verdict: str
    boundary_record: Mapping[str, object]
    authority_separation_record: Mapping[str, object]
    repository_effect: str
    runtime_effect: str
    production_effect: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_receipt() -> Slice20Receipt:
    result = check_boundary_integrity()
    result.require_pass()
    return Slice20Receipt(
        slice_id=SLICE_ID,
        title=SLICE_TITLE,
        verdict="PASS",
        boundary_record=build_boundary_record().to_dict(),
        authority_separation_record=build_authority_separation_record().to_dict(),
        repository_effect="adds_boundary_records_only",
        runtime_effect="no_delivery_no_action_no_tool_invocation_no_code_execution",
        production_effect="no_route_no_ui_no_registry_no_daemon_no_network_no_deployment",
    )
