"""Immutable schema helpers for Forge language bridge v1."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


SCHEMA_VERSION = "forge-language-bridge-v1"


@dataclass(frozen=True, slots=True)
class BridgeDecision:
    schema_version: str
    bridge_version: str
    bridge_mode: str
    request_id: str
    surface: str
    source_text_sha256: str
    normalized_text: str
    handled: bool
    status: str
    intent: str
    route: str
    args: str
    response_text: str
    action_class: str
    approval_required: bool
    approval_gate: str
    calls_llm: bool
    executes_command: bool
    executes_shell: bool
    executes_simulation: bool
    writes_files: bool
    writes_memory: bool
    grants_permission: bool
    input_custody: dict[str, Any]
    recursive_manifest_preview: dict[str, Any]
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
