"""Fail-closed validation for service records and reports."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from .authority import (
    BUILD_BASE_HEAD,
    BUILD_BASE_SUBJECT,
    BUILD_BASE_TREE,
    BUILD_ID,
    LIFECYCLE_STATES,
    PROTOCOL_VERSION,
    SCHEMA_VERSION,
    SERVICE_VERSION,
    TRANSPORT,
)
from .schema import CapabilityState, ProcessRecord, ServiceIdentity

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_CAPABILITY_ID = re.compile(r"^[a-z0-9][a-z0-9_.-]{2,95}$")


def validate_capability_state(value: CapabilityState) -> tuple[str, ...]:
    issues: list[str] = []
    if not _CAPABILITY_ID.fullmatch(value.capability_id):
        issues.append("invalid_capability_id")
    if value.state not in {"ENABLED", "DISABLED", "DEFERRED", "PRESERVED", "NOT_AUTHORIZED"}:
        issues.append("invalid_capability_state")
    if value.authority and value.state != "ENABLED":
        issues.append("authority_state_inconsistent")
    if not value.detail or len(value.detail) > 500:
        issues.append("invalid_capability_detail")
    return tuple(issues)


def validate_process_record(value: ProcessRecord) -> tuple[str, ...]:
    issues: list[str] = []
    if value.schema_version != SCHEMA_VERSION:
        issues.append("schema_version_mismatch")
    if value.service_version != SERVICE_VERSION:
        issues.append("service_version_mismatch")
    if value.pid <= 1:
        issues.append("invalid_pid")
    if value.process_start_ticks <= 0:
        issues.append("invalid_process_start_ticks")
    if not _HEX64.fullmatch(value.command_sha256):
        issues.append("invalid_command_sha256")
    for label, raw in (
        ("entry_script", value.entry_script),
        ("repository_root", value.repository_root),
        ("state_root", value.state_root),
    ):
        if not raw or not Path(raw).is_absolute():
            issues.append(f"{label}_not_absolute")
    return tuple(issues)


def validate_service_identity(value: ServiceIdentity) -> tuple[str, ...]:
    issues: list[str] = []
    if value.schema_version != SCHEMA_VERSION:
        issues.append("schema_version_mismatch")
    if value.build_id != BUILD_ID:
        issues.append("build_id_mismatch")
    if value.service_version != SERVICE_VERSION:
        issues.append("service_version_mismatch")
    if value.protocol_version != PROTOCOL_VERSION:
        issues.append("protocol_version_mismatch")
    if value.transport != TRANSPORT:
        issues.append("transport_mismatch")
    if value.build_base_head != BUILD_BASE_HEAD or not _HEX40.fullmatch(value.build_base_head):
        issues.append("build_base_head_mismatch")
    if value.build_base_tree != BUILD_BASE_TREE or not _HEX40.fullmatch(value.build_base_tree):
        issues.append("build_base_tree_mismatch")
    if value.build_base_subject != BUILD_BASE_SUBJECT:
        issues.append("build_base_subject_mismatch")
    if value.pid <= 1 or value.process_start_ticks <= 0:
        issues.append("invalid_process_identity")
    if not _HEX64.fullmatch(value.command_sha256):
        issues.append("invalid_command_sha256")
    if not _HEX64.fullmatch(value.control_token_sha256):
        issues.append("invalid_control_token_sha256")
    for label, raw in (
        ("socket_path", value.socket_path),
        ("repository_root", value.repository_root),
        ("state_root", value.state_root),
    ):
        if not raw or not Path(raw).is_absolute():
            issues.append(f"{label}_not_absolute")
    if value.identity_id != value.expected_id():
        issues.append("identity_id_mismatch")
    return tuple(issues)


def validate_lifecycle_state(value: str) -> tuple[str, ...]:
    return () if value in LIFECYCLE_STATES else ("invalid_lifecycle_state",)


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label}_must_be_mapping")
    return value


def require_exact_keys(value: Mapping[str, Any], expected: Sequence[str], label: str) -> None:
    if set(value) != set(expected):
        raise ValueError(f"{label}_keys_mismatch")
