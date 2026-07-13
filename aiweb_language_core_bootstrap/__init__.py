"""AI.Web isolated deterministic language-core bootstrap boundary.

Slice 30 exports inert records, builders and validators only. It does not load
accepted components, connect to main.py, execute language interpretation, or
create route, UI, network, memory, delivery, tool, action, GP-014, release or
production authority.
"""

from .authority import (
    BootstrapAuthorityState,
    build_bootstrap_authority_state,
    validate_bootstrap_authority_state,
)
from .boundary import (
    BootstrapBoundaryBundle,
    BootstrapBoundaryRecord,
    build_bootstrap_boundary_bundle,
    build_bootstrap_boundary_record,
    validate_bootstrap_boundary_record,
)
from .component_registry import (
    ComponentRegistrationRecord,
    ComponentRegistryRecord,
    build_component_registration_record,
    build_component_registry_record,
    validate_component_registration_record,
    validate_component_registry_record,
)
from .import_policy import (
    ImportPolicyRecord,
    build_import_policy_record,
    validate_import_policy_record,
)
from .schema import (
    SCHEMA_VERSION,
    ValidationIssue,
    ValidationReport,
    canonical_json,
    canonicalize,
    stable_record_id,
)

__all__ = (
    "BootstrapAuthorityState",
    "BootstrapBoundaryBundle",
    "BootstrapBoundaryRecord",
    "ComponentRegistrationRecord",
    "ComponentRegistryRecord",
    "ImportPolicyRecord",
    "SCHEMA_VERSION",
    "ValidationIssue",
    "ValidationReport",
    "build_bootstrap_authority_state",
    "build_bootstrap_boundary_bundle",
    "build_bootstrap_boundary_record",
    "build_component_registration_record",
    "build_component_registry_record",
    "build_import_policy_record",
    "canonical_json",
    "canonicalize",
    "stable_record_id",
    "validate_bootstrap_authority_state",
    "validate_bootstrap_boundary_record",
    "validate_component_registration_record",
    "validate_component_registry_record",
    "validate_import_policy_record",
)
