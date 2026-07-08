"""Slice 16 selected meaning boundary scaffold.

This package creates deterministic boundary records only. It can represent a
selected-meaning boundary state, but it does not decide truth, grant permission,
authorize action, invoke tools, deliver output, execute anything, write memory,
validate evidence, admit external resources, or perform final meaning selection.
"""

from .candidate_reference import (
    CandidateSelectionReferenceRecord,
    build_candidate_selection_reference_record,
    demo_candidate_selection_reference_record,
    demo_non_selected_candidate_reference_record,
    validate_candidate_selection_reference_record,
)
from .core import (
    REQUIRED_PRIOR_BOUNDARIES,
    REQUIRED_SELECTION_LAWS,
    SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS,
    selected_meaning_scope_record,
)
from .selection_basis import SelectionBasisRecord, build_selection_basis_record, demo_selection_basis_record, validate_selection_basis_record
from .selection_constraint import SelectionConstraintRecord, build_selection_constraint_record, demo_selection_constraint_record, validate_selection_constraint_record
from .selection_receipt import SelectionReceiptRecord, build_selection_receipt_record, demo_selection_receipt_record, validate_selection_receipt_record
from .selection_status import SelectedMeaningStatusRecord, build_selected_meaning_status_record, demo_selected_meaning_status_record, demo_selection_blocked_status_record, validate_selected_meaning_status_record
from .selection_trace import SelectionTraceRecord, build_selection_trace_record, demo_selection_trace_record, validate_selection_trace_record
from .verify import run_verification

__all__ = [
    "CandidateSelectionReferenceRecord",
    "build_candidate_selection_reference_record",
    "demo_candidate_selection_reference_record",
    "demo_non_selected_candidate_reference_record",
    "validate_candidate_selection_reference_record",
    "REQUIRED_PRIOR_BOUNDARIES",
    "REQUIRED_SELECTION_LAWS",
    "SELECTION_DOWNSTREAM_FALSE_ONLY_FIELDS",
    "selected_meaning_scope_record",
    "SelectionBasisRecord",
    "build_selection_basis_record",
    "demo_selection_basis_record",
    "validate_selection_basis_record",
    "SelectionConstraintRecord",
    "build_selection_constraint_record",
    "demo_selection_constraint_record",
    "validate_selection_constraint_record",
    "SelectionReceiptRecord",
    "build_selection_receipt_record",
    "demo_selection_receipt_record",
    "validate_selection_receipt_record",
    "SelectedMeaningStatusRecord",
    "build_selected_meaning_status_record",
    "demo_selected_meaning_status_record",
    "demo_selection_blocked_status_record",
    "validate_selected_meaning_status_record",
    "SelectionTraceRecord",
    "build_selection_trace_record",
    "demo_selection_trace_record",
    "validate_selection_trace_record",
    "run_verification",
]
