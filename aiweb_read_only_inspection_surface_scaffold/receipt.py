"""Receipt builder for Slice 21."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping

from .authority import build_authority_separation_record
from .boundary import check_boundary_integrity
from .core import SLICE_ID, SLICE_TITLE, build_inspection_surface_record, canonical_json, sha256_text


@dataclass(frozen=True, slots=True)
class Slice21Receipt:
    slice_id: str
    title: str
    verdict: str
    inspection_surface_record: Mapping[str, object]
    authority_separation_record: Mapping[str, object]
    repository_effect: str
    runtime_effect: str
    production_effect: str
    receipt_sha256: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_receipt() -> Slice21Receipt:
    result = check_boundary_integrity()
    result.require_pass()

    body: dict[str, object] = {
        "slice_id": SLICE_ID,
        "title": SLICE_TITLE,
        "verdict": "PASS",
        "inspection_surface_record": build_inspection_surface_record().to_dict(),
        "authority_separation_record": build_authority_separation_record().to_dict(),
        "repository_effect": "adds_read_only_inspection_boundary_records_only",
        "runtime_effect": "no_runtime_authority_no_state_change_no_memory_write_no_tool_route_no_delivery",
        "production_effect": "no_live_api_no_route_registration_no_ui_no_config_change_no_deployment",
    }
    digest = sha256_text(canonical_json(body))
    return Slice21Receipt(receipt_sha256=digest, **body)
