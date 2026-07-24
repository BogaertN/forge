"""Binding authority limits for Slice 48."""
from __future__ import annotations

SLICE_ID = "Slice 48"
BUILD_ID = "AIWEB-SLICE48-LOCAL-RUNTIME-SERVICE-BOUNDARY-V1"
SERVICE_VERSION = "1.0.0"
PROTOCOL_VERSION = "aiweb_local_runtime_service_v1"
SCHEMA_VERSION = "aiweb_local_runtime_service_schema_v1"
TRANSPORT = "unix_domain_socket"
NEXT_LAWFUL_SLICE = 49

BUILD_BASE_HEAD = "1f9070065aad5df11627cbb16732430ca47ded11"
BUILD_BASE_TREE = "2d18842fb938c99ce5616fc713577b7e9f2ea1ae"
BUILD_BASE_SUBJECT = "Slice 47 GP-014 status decision and Phase D closeout"

PUBLIC_COMMANDS = (
    "start",
    "stop",
    "status",
    "health",
    "version",
    "capabilities",
)
PROTOCOL_OPERATIONS = (
    "health",
    "version",
    "capabilities",
    "status",
    "shutdown",
)
LIFECYCLE_STATES = (
    "STOPPED",
    "STARTING",
    "RUNNING",
    "STOPPING",
    "FAILED",
    "STALE",
    "FOREIGN_PROCESS",
    "UNKNOWN",
)

# Every item remains false in Slice 48. The service is a local process boundary,
# not an authority promotion.
PROHIBITED_AUTHORITIES = (
    "general_language_authority",
    "interpretation_authority",
    "selected_meaning_authority",
    "truth_authority",
    "evidence_authority",
    "permission_authority",
    "public_route_authority",
    "remote_network_authority",
    "language_inspection_api_authority",
    "filesystem_repository_write_authority",
    "memory_write_authority",
    "resource_ingestion_authority",
    "tool_authority",
    "action_authority",
    "delivery_authority",
    "gp014_supersession_authority",
    "release_authority",
    "production_authority",
)

MAX_MESSAGE_BYTES = 16_384
STARTUP_TIMEOUT_SECONDS = 15.0
SHUTDOWN_TIMEOUT_SECONDS = 10.0
FALLBACK_TERM_TIMEOUT_SECONDS = 5.0
DEFAULT_STATE_DIRECTORY_NAME = "local-runtime-service-v1"
