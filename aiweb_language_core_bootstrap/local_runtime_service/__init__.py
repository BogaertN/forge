"""Slice 48 local-only runtime service boundary."""
from .authority import (
    BUILD_BASE_HEAD,
    BUILD_BASE_SUBJECT,
    BUILD_BASE_TREE,
    BUILD_ID,
    NEXT_LAWFUL_SLICE,
    PROTOCOL_VERSION,
    SERVICE_VERSION,
    SLICE_ID,
    TRANSPORT,
)
from .capabilities import build_capability_report
from .control import cli_main
from .schema import CapabilityState, ProcessRecord, ServiceIdentity

__all__ = (
    "BUILD_BASE_HEAD",
    "BUILD_BASE_SUBJECT",
    "BUILD_BASE_TREE",
    "BUILD_ID",
    "NEXT_LAWFUL_SLICE",
    "PROTOCOL_VERSION",
    "SERVICE_VERSION",
    "SLICE_ID",
    "TRANSPORT",
    "CapabilityState",
    "ProcessRecord",
    "ServiceIdentity",
    "build_capability_report",
    "cli_main",
)
