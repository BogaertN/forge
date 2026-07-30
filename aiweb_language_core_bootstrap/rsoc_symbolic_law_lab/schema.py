"""Typed records for the Forge-owned RSOC law laboratory.

The laboratory is deliberately separate from the exact-glyph reference
preview.  It can validate typed operands and produce successor *preview*
records, but it has no runtime, memory, route, tool, action, or delivery
authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..schema import stable_record_id


RSOC_LAW_LAB_SCHEMA_VERSION: Final[str] = "aiweb-forge-rsoc-law-lab-v0"
MICRO_SCALE: Final[int] = 1_000_000


class RsocLawStatus(str, Enum):
    PREVIEW_READY = "PREVIEW_READY"
    HELD_REFERENCE_CONFLICT = "HELD_REFERENCE_CONFLICT"
    HELD_PRECONDITION = "HELD_PRECONDITION"
    HELD_INVALID = "HELD_INVALID"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True, slots=True)
class SymbolicFieldState:
    field_id: str
    identity_refs: tuple[str, ...]
    phase_index: int
    recursion_depth: int
    drift_micro: int
    resonance_micro: int
    memory_charge_micro: int
    entropy_micro: int
    loop_ref: str
    echo_ancestry_refs: tuple[str, ...]
    lineage_refs: tuple[str, ...]
    locked: bool
    archived: bool
    grace_used: bool
    revision: int
    schema_version: str = RSOC_LAW_LAB_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("field_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("rsoc_lab_field", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RsocLawDefinition:
    law_id: str
    operator_key: str
    glyph: str
    forge_provisional_name: str
    declared_arity: int
    reference_names: tuple[str, ...]
    reference_source_refs: tuple[str, ...]
    typed_operand_kind: str
    admitted_preview_operation: str
    reference_conflict_codes: tuple[str, ...]
    invariant_codes: tuple[str, ...]
    forge_owned: bool
    provisional: bool
    external_reference_authority: bool
    runtime_enabled: bool
    schema_version: str = RSOC_LAW_LAB_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("law_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("rsoc_lab_law", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RsocLawBoundary:
    isolated_lab: bool = True
    preview_only: bool = True
    forge_owned_provisional_law: bool = True
    external_reference_authority: bool = False
    natural_language_tokenization_performed: bool = False
    model_called: bool = False
    embedding_used: bool = False
    vector_used: bool = False
    filesystem_read_performed: bool = False
    filesystem_write_performed: bool = False
    network_access_performed: bool = False
    live_memory_read_performed: bool = False
    live_memory_write_performed: bool = False
    operator_runtime_invoked: bool = False
    tool_routing_performed: bool = False
    action_performed: bool = False
    delivery_performed: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RsocLawPreviewResult:
    result_id: str
    status: RsocLawStatus
    reason_code: str
    law: RsocLawDefinition | None
    input_field_refs: tuple[str, ...]
    output_fields: tuple[SymbolicFieldState, ...]
    echo_valid: bool | None
    issue_codes: tuple[str, ...]
    trace: tuple[str, ...]
    boundary: RsocLawBoundary
    deterministic: bool
    runtime_authority: bool
    memory_authority: bool
    action_authority: bool
    delivery_authority: bool
    schema_version: str = RSOC_LAW_LAB_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("rsoc_lab_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


__all__ = (
    "MICRO_SCALE",
    "RSOC_LAW_LAB_SCHEMA_VERSION",
    "RsocLawBoundary",
    "RsocLawDefinition",
    "RsocLawPreviewResult",
    "RsocLawStatus",
    "SymbolicFieldState",
)
