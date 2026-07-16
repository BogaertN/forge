"""Slice 37C closed read-only built-in concept registry.

Importing this package constructs only immutable in-memory constants.  It does
not inspect source language, select meaning, access storage or networks,
register routes, activate tools, render output, deliver messages, or execute
actions.
"""

from .authority import (
    BUILT_IN_CONCEPT_DEFINITIONS,
    BUILT_IN_CONCEPT_KEYS,
    SLICE37C_NAMESPACE_KEY,
    BuiltInConceptDefinition,
)
from .identity import registry_digest, with_expected_manifest_id
from .records import (
    ADMITTED_CONCEPTS,
    ALL_AUTHORITIES,
    ALL_RESOURCES,
    ALL_TRANSITIONS,
    CONCEPT_HISTORIES,
    CURRENT_NAMESPACE,
    GOVERNANCE_BATCH,
    NAMESPACE_HISTORY,
    PROVENANCE_RECORDS,
)
from .registry import (
    BUILT_IN_REGISTRY,
    all_admitted_concepts,
    built_in_registry,
    concept_by_id,
    concept_by_key,
    contains_concept_id,
    current_namespace,
    registry_manifest,
)
from .schema import (
    SLICE37C_ACCEPTED_PARENT_HEAD,
    SLICE37C_ACCEPTED_PARENT_SUBJECT,
    SLICE37C_ACCEPTED_PARENT_TREE,
    SLICE37C_EXPECTED_CONCEPT_COUNT,
    SLICE37C_EXPECTED_NAMESPACE_COUNT,
    SLICE37C_SCHEMA_VERSION,
    SLICE37C_SOURCE_AUTHORITY_PACKET_SHA256,
    SLICE37C_SPEC_ID,
    SLICE37C_SPEC_VERSION,
    BuiltInConceptRegistry,
    BuiltInConceptRegistryManifest,
    BuiltInRegistryValidationCode,
    BuiltInRegistryValidationError,
    BuiltInRegistryValidationIssue,
    BuiltInRegistryValidationReport,
)
from .validation import (
    assert_built_in_registry,
    validate_built_in_registry,
    validate_registry_manifest,
)

__all__ = (
    "ADMITTED_CONCEPTS",
    "ALL_AUTHORITIES",
    "ALL_RESOURCES",
    "ALL_TRANSITIONS",
    "BUILT_IN_CONCEPT_DEFINITIONS",
    "BUILT_IN_CONCEPT_KEYS",
    "BUILT_IN_REGISTRY",
    "CONCEPT_HISTORIES",
    "CURRENT_NAMESPACE",
    "GOVERNANCE_BATCH",
    "NAMESPACE_HISTORY",
    "PROVENANCE_RECORDS",
    "SLICE37C_ACCEPTED_PARENT_HEAD",
    "SLICE37C_ACCEPTED_PARENT_SUBJECT",
    "SLICE37C_ACCEPTED_PARENT_TREE",
    "SLICE37C_EXPECTED_CONCEPT_COUNT",
    "SLICE37C_EXPECTED_NAMESPACE_COUNT",
    "SLICE37C_NAMESPACE_KEY",
    "SLICE37C_SCHEMA_VERSION",
    "SLICE37C_SOURCE_AUTHORITY_PACKET_SHA256",
    "SLICE37C_SPEC_ID",
    "SLICE37C_SPEC_VERSION",
    "BuiltInConceptDefinition",
    "BuiltInConceptRegistry",
    "BuiltInConceptRegistryManifest",
    "BuiltInRegistryValidationCode",
    "BuiltInRegistryValidationError",
    "BuiltInRegistryValidationIssue",
    "BuiltInRegistryValidationReport",
    "all_admitted_concepts",
    "assert_built_in_registry",
    "built_in_registry",
    "concept_by_id",
    "concept_by_key",
    "contains_concept_id",
    "current_namespace",
    "registry_digest",
    "registry_manifest",
    "validate_built_in_registry",
    "validate_registry_manifest",
    "with_expected_manifest_id",
)
