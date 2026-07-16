"""Deterministic identity helpers for Slice 37A schema records.

These helpers construct exact record identifiers from caller-supplied schema
fields. They perform no term normalization, lexical lookup, fuzzy matching,
semantic similarity, mapping, sense selection, graph traversal, or admission.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TypeVar

from .schema import (
    ConceptNamespaceIdentity,
    ConceptProvenanceReference,
    ControlledConceptIdentity,
    ControlledLexicalReference,
    ControlledSenseIdentity,
    SemanticClassIdentity,
    SemanticRelationFamilyIdentity,
    SemanticRelationTypeIdentity,
    TermConceptMappingIdentity,
)


_RecordT = TypeVar(
    "_RecordT",
    ConceptProvenanceReference,
    ConceptNamespaceIdentity,
    ControlledConceptIdentity,
    ControlledSenseIdentity,
    ControlledLexicalReference,
    TermConceptMappingIdentity,
    SemanticClassIdentity,
    SemanticRelationFamilyIdentity,
    SemanticRelationTypeIdentity,
)


def with_expected_resource_id(record: _RecordT) -> _RecordT:
    """Return the same immutable schema record with its exact expected ID.

    The function changes only the record's identity field. It does not alter
    text, select a sense, admit a resource, create a registry entry, or infer
    any semantic relationship.
    """

    field_name = {
        ConceptProvenanceReference: "provenance_id",
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
        raise TypeError(f"unsupported Slice 37A record type: {type(record).__name__}")

    return replace(record, **{field_name: record.expected_id()})
