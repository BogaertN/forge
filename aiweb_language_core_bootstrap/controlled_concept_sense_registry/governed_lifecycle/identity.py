"""Deterministic Slice 37B record, lineage, and version identity helpers.

The helpers use exact caller-supplied record fields.  They do not normalize
language, perform lexical lookup, compare semantic similarity, select a sense,
admit a resource, or mutate any source record.
"""

from __future__ import annotations

from dataclasses import replace
import re
from typing import Final

from ...schema import stable_record_id
from ..schema import (
    ConceptNamespaceIdentity,
    ControlledConceptIdentity,
    ControlledLexicalReference,
    ControlledSenseIdentity,
    SemanticClassIdentity,
    SemanticRelationFamilyIdentity,
    SemanticRelationTypeIdentity,
    TermConceptMappingIdentity,
)
from .schema import (
    ConceptGovernanceBatch,
    ConceptLifecycleAuthorityRecord,
    ConceptLifecycleTransitionRecord,
    GovernedConceptResource,
)


_STRICT_VERSION_RE: Final[re.Pattern[str]] = re.compile(
    r"^v(0|[1-9][0-9]*)(?:\.(0|[1-9][0-9]*))?(?:\.(0|[1-9][0-9]*))?$"
)


def resource_identity_field(record: GovernedConceptResource) -> str:
    field_name = {
        ConceptNamespaceIdentity: "namespace_id",
        ControlledConceptIdentity: "concept_id",
        ControlledSenseIdentity: "sense_id",
        ControlledLexicalReference: "lexical_reference_id",
        TermConceptMappingIdentity: "mapping_id",
        SemanticClassIdentity: "semantic_class_id",
        SemanticRelationFamilyIdentity: "relation_family_id",
        SemanticRelationTypeIdentity: "relation_type_id",
    }.get(type(record))

    if field_name is None:
        raise TypeError(
            "unsupported governed concept resource type: "
            f"{type(record).__name__}"
        )

    return field_name


def resource_id(record: GovernedConceptResource) -> str:
    return getattr(record, resource_identity_field(record))


def recompute_resource_id(record: GovernedConceptResource) -> str:
    """Recompute the exact version-record identity from its canonical body."""

    return record.expected_id()


def with_recomputed_resource_id(
    record: GovernedConceptResource,
) -> GovernedConceptResource:
    """Return an immutable copy carrying its exact version-record identity."""

    return replace(
        record,
        **{
            resource_identity_field(record): recompute_resource_id(record),
        },
    )


def resource_lineage_body(
    record: GovernedConceptResource,
) -> dict[str, object]:
    """Return the exact material identity boundary preserved across versions."""

    if type(record) is ConceptNamespaceIdentity:
        return {
            "resource_kind": record.resource_kind.value,
            "namespace_key": record.namespace_key,
        }

    if type(record) is ControlledConceptIdentity:
        return {
            "resource_kind": record.resource_kind.value,
            "namespace_id": record.namespace_id,
            "concept_key": record.concept_key,
        }

    if type(record) is ControlledSenseIdentity:
        return {
            "resource_kind": record.resource_kind.value,
            "concept_id": record.concept_id,
            "namespace_id": record.namespace_id,
            "sense_key": record.sense_key,
        }

    if type(record) is ControlledLexicalReference:
        return {
            "resource_kind": record.resource_kind.value,
            "namespace_id": record.namespace_id,
            "exact_form": record.exact_form,
            "reference_kind": record.reference_kind.value,
            "language_tag": record.language_tag,
            "case_sensitive": record.case_sensitive,
        }

    if type(record) is TermConceptMappingIdentity:
        return {
            "resource_kind": record.resource_kind.value,
            "lexical_reference_id": record.lexical_reference_id,
            "namespace_scope": record.namespace_scope,
            "domain_scope": record.domain_scope,
        }

    if type(record) is SemanticClassIdentity:
        return {
            "resource_kind": record.resource_kind.value,
            "namespace_id": record.namespace_id,
            "class_key": record.class_key,
        }

    if type(record) is SemanticRelationFamilyIdentity:
        return {
            "resource_kind": record.resource_kind.value,
            "namespace_id": record.namespace_id,
            "family_key": record.family_key,
        }

    if type(record) is SemanticRelationTypeIdentity:
        return {
            "resource_kind": record.resource_kind.value,
            "namespace_id": record.namespace_id,
            "relation_family_id": record.relation_family_id,
            "relation_key": record.relation_key,
        }

    raise TypeError(
        "unsupported governed concept resource type: "
        f"{type(record).__name__}"
    )


def expected_resource_lineage_id(
    record: GovernedConceptResource,
) -> str:
    return stable_record_id(
        "controlled_concept_resource_lineage",
        resource_lineage_body(record),
    )


def parse_resource_version(version: str) -> tuple[int, int, int]:
    """Parse the exact bounded vN, vN.N, or vN.N.N form."""

    if not isinstance(version, str):
        raise TypeError("version must be str")

    match = _STRICT_VERSION_RE.fullmatch(version)

    if match is None:
        raise ValueError(
            "version must use canonical vN, vN.N, or vN.N.N form "
            "without leading zeros"
        )

    values = tuple(
        int(item) if item is not None else 0
        for item in match.groups()
    )

    return values[0], values[1], values[2]


def version_advances(source_version: str, target_version: str) -> bool:
    return (
        parse_resource_version(target_version)
        > parse_resource_version(source_version)
    )


def with_expected_authority_id(
    record: ConceptLifecycleAuthorityRecord,
) -> ConceptLifecycleAuthorityRecord:
    return replace(
        record,
        authority_id=record.expected_id(),
    )


def with_expected_transition_id(
    record: ConceptLifecycleTransitionRecord,
) -> ConceptLifecycleTransitionRecord:
    return replace(
        record,
        transition_id=record.expected_id(),
    )


def with_expected_batch_id(
    batch: ConceptGovernanceBatch,
) -> ConceptGovernanceBatch:
    return replace(
        batch,
        batch_id=batch.expected_id(),
    )
