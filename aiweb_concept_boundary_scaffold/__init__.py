"""Slice 8 concept and semantic relation boundary scaffold.

This package contains deterministic boundary records only. It does not
resolve concepts, traverse graphs, import lexical datasets, assign roles,
select gates, render output, write memory, or route actions.
"""

from .concept import (
    ConceptBoundaryRecord,
    SenseBoundaryRecord,
    ValidationIssue,
    ValidationReport,
    concept_scope_record,
    stable_boundary_id,
    validate_concept_record,
    validate_sense_record,
)
from .relation import (
    SemanticRelationBoundaryRecord,
    relation_scope_record,
    validate_relation_record,
)

__all__ = [
    "ConceptBoundaryRecord",
    "SenseBoundaryRecord",
    "SemanticRelationBoundaryRecord",
    "ValidationIssue",
    "ValidationReport",
    "concept_scope_record",
    "relation_scope_record",
    "stable_boundary_id",
    "validate_concept_record",
    "validate_sense_record",
    "validate_relation_record",
]
