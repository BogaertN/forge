"""Public Slice 38A predicate/action-root schema surface.

The package is schema-only. It does not populate an action-root registry,
select a predicate, assign a participant role, complete a predicate frame,
reference a live capability, invoke a route, perform an action, access memory,
validate evidence, render output, or authorize delivery.
"""

from .authority import (
    build_slice38a_authority_profile,
    build_slice38a_schema_contract,
)
from .identity import with_expected_predicate_resource_id
from .schema import (
    PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES,
    SLICE38A_ACCEPTED_PARENT_HEAD,
    SLICE38A_ACCEPTED_PARENT_SUBJECT,
    SLICE38A_ACCEPTED_PARENT_TREE,
    SLICE38A_DEFERRED_SCOPE,
    SLICE38A_SCHEMA_VERSION,
    SLICE38A_SPEC_ID,
    SLICE38A_SPEC_VERSION,
    ActionRootIdentity,
    PredicateAuthorityProfile,
    PredicateIdentity,
    PredicateLifecycleState,
    PredicateNamespaceIdentity,
    PredicateProvenanceReference,
    PredicateRegistrySchemaContract,
    PredicateResourceKind,
)
from .validation import (
    PredicateSchemaValidationCode,
    PredicateSchemaValidationError,
    PredicateSchemaValidationIssue,
    PredicateSchemaValidationReport,
    validate_action_root_identity,
    validate_predicate_authority_profile,
    validate_predicate_identity,
    validate_predicate_namespace_identity,
    validate_predicate_provenance_reference,
    validate_predicate_registry_schema_contract,
)

__all__ = (
    "PREDICATE_RESOURCE_PROHIBITED_AUTHORITIES",
    "SLICE38A_ACCEPTED_PARENT_HEAD",
    "SLICE38A_ACCEPTED_PARENT_SUBJECT",
    "SLICE38A_ACCEPTED_PARENT_TREE",
    "SLICE38A_DEFERRED_SCOPE",
    "SLICE38A_SCHEMA_VERSION",
    "SLICE38A_SPEC_ID",
    "SLICE38A_SPEC_VERSION",
    "ActionRootIdentity",
    "PredicateAuthorityProfile",
    "PredicateIdentity",
    "PredicateLifecycleState",
    "PredicateNamespaceIdentity",
    "PredicateProvenanceReference",
    "PredicateRegistrySchemaContract",
    "PredicateResourceKind",
    "PredicateSchemaValidationCode",
    "PredicateSchemaValidationError",
    "PredicateSchemaValidationIssue",
    "PredicateSchemaValidationReport",
    "build_slice38a_authority_profile",
    "build_slice38a_schema_contract",
    "validate_action_root_identity",
    "validate_predicate_authority_profile",
    "validate_predicate_identity",
    "validate_predicate_namespace_identity",
    "validate_predicate_provenance_reference",
    "validate_predicate_registry_schema_contract",
    "with_expected_predicate_resource_id",
)
