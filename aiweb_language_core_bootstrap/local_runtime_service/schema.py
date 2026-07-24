"""Typed records used by the Slice 48 service boundary."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .canonical import canonical_sha256


@dataclass(frozen=True, slots=True)
class CapabilityState:
    capability_id: str
    state: str
    authority: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ProcessRecord:
    schema_version: str
    service_version: str
    pid: int
    process_start_ticks: int
    command_sha256: str
    entry_script: str
    repository_root: str
    state_root: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def expected_id(self) -> str:
        return "slice48-process:" + canonical_sha256(self.to_dict())


@dataclass(frozen=True, slots=True)
class ServiceIdentity:
    schema_version: str
    build_id: str
    service_version: str
    protocol_version: str
    transport: str
    socket_path: str
    repository_root: str
    state_root: str
    pid: int
    process_start_ticks: int
    command_sha256: str
    control_token_sha256: str
    build_base_head: str
    build_base_tree: str
    build_base_subject: str
    identity_id: str = ""

    def identity_payload(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("identity_id", None)
        return data

    def expected_id(self) -> str:
        return "slice48-service:" + canonical_sha256(self.identity_payload())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
