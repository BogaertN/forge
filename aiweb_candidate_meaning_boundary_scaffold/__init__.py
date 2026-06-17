"""Slice 11 candidate meaning construction boundary scaffold.

This package creates deterministic boundary records only. It does not select
final meaning, decide truth, route tools, authorize actions, deliver output,
write memory, validate evidence, admit external resources, or activate live
runtime interpretation.
"""

from .candidate import (
    CandidateMeaningBoundaryRecord,
    candidate_meaning_scope_record,
    demo_candidate_meaning_record,
    demo_no_action_candidate_record,
    demo_unsupported_candidate_record,
    validate_candidate_meaning_record,
)
from .source_custody import (
    SourceExpressionCustodyRecord,
    build_source_expression_custody_record,
    demo_source_expression_custody_record,
    validate_source_expression_custody_record,
)
from .derived_structure import (
    DerivedStructureCustodyRecord,
    demo_derived_structure_custody_record,
    validate_derived_structure_custody_record,
)
from .support_boundary import (
    MissingSupportBoundaryRecord,
    demo_missing_support_boundary_record,
    demo_no_missing_support_boundary_record,
    validate_missing_support_boundary_record,
)
from .competition import (
    CandidateCompetitionSetBoundaryRecord,
    demo_candidate_competition_set_record,
    validate_candidate_competition_set_record,
)

__all__ = [
    "CandidateMeaningBoundaryRecord",
    "candidate_meaning_scope_record",
    "demo_candidate_meaning_record",
    "demo_no_action_candidate_record",
    "demo_unsupported_candidate_record",
    "validate_candidate_meaning_record",
    "SourceExpressionCustodyRecord",
    "build_source_expression_custody_record",
    "demo_source_expression_custody_record",
    "validate_source_expression_custody_record",
    "DerivedStructureCustodyRecord",
    "demo_derived_structure_custody_record",
    "validate_derived_structure_custody_record",
    "MissingSupportBoundaryRecord",
    "demo_missing_support_boundary_record",
    "demo_no_missing_support_boundary_record",
    "validate_missing_support_boundary_record",
    "CandidateCompetitionSetBoundaryRecord",
    "demo_candidate_competition_set_record",
    "validate_candidate_competition_set_record",
]
