"""Binding authority for Slice 46 GP-014 equivalence proof."""
from __future__ import annotations

from typing import Final

SLICE46_SCHEMA_VERSION: Final[str] = "aiweb-slice46-gp014-equivalence-regression-v1"
SLICE46_SPEC_ID: Final[str] = "canonical-roadmap:slice46"
SLICE46_SPEC_VERSION: Final[str] = "v1.0.0"
SLICE46_COMMIT_SUBJECT: Final[str] = 'Slice 46 GP-014 equivalence and regression proof'

ACCEPTED_PARENT_HEAD: Final[str] = '00df51e4b2fe14e437291c5228159820dd1cf139'
ACCEPTED_PARENT_PARENT: Final[str] = 'd374ebb8c09ef0f74df93177ea08bffb5e66791d'
ACCEPTED_PARENT_TREE: Final[str] = '987c08cc797ebe721dc28ab7d03b69a6b1b61f8f'
ACCEPTED_PARENT_SUBJECT: Final[str] = 'Slice 45 bounded GP-014 adapter boundary'

DIRECT_SOURCE_MODULE: Final[str] = "rmc_engine_v1.general_pipeline.symbolic_math_language_vertical_slice"
DIRECT_SOURCE_FUNCTION: Final[str] = "answer_symbolic_math_language_request"
ADAPTER_MODULE: Final[str] = "aiweb_language_core_bootstrap.gp014_adapter_boundary.adapter"
GP014_MODULE: Final[str] = "rmc_engine_v1.general_pipeline.gp014_operator_guided_language_realizer"
GP015_MODULE: Final[str] = "rmc_engine_v1.general_pipeline.gp015_ask_forge_trace_surface"

EXPECTED_POSITIVE_CASES: Final[int] = 8
EXPECTED_NEGATIVE_CASES: Final[int] = 5
EXPECTED_FAILURE_INJECTION_CASES: Final[int] = 3
EXPECTED_TOTAL_EQUIVALENCE_CASES: Final[int] = 13
EXPECTED_PAYLOAD_FILE_COUNT: Final[int] = 16

ALLOWED_DIRECT_STATUSES: Final[tuple[str, ...]] = (
    "ANSWERED",
    "ECHO_REJECTED",
    "GATE_BLOCKED",
    "REFUSED_UNLEARNED",
)

ANSWERED_DIMENSIONS: Final[tuple[str, ...]] = (
    "status",
    "question",
    "question_sha256",
    "answer_text",
    "answer_text_sha256",
    "domain",
    "build_id",
    "schema_version",
    "reasons_digest",
    "source_result_hash",
    "compiled_request_hash",
    "operation_family",
    "operation_manifest_hash",
    "kernel_result_digest",
    "solution_digest",
    "solution_answer_text",
    "verification_strength",
    "meaning_hash",
    "manifest_contract_v2_hash",
    "expression_realization_receipt_hash",
    "rendered_text_sha256",
    "selected_candidate_id",
    "selected_candidate_hash",
    "candidate_set_digest",
    "echo_hash",
    "delivery_authorization_v2_hash",
    "non_delivery_receipt_hash",
    "delivery_present",
)

CONTAINED_DIMENSIONS: Final[tuple[str, ...]] = ANSWERED_DIMENSIONS

PROHIBITED_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "gp014_modified",
    "gp014_superseded",
    "gp015_used",
    "main_modified_or_called",
    "route_created_or_called",
    "api_created_or_called",
    "ui_created_or_called",
    "network_authority_added",
    "filesystem_write_authority_added",
    "memory_authority_added",
    "evidence_authority_added",
    "truth_authority_added",
    "permission_authority_added",
    "delivery_authority_added_by_adapter",
    "tool_authority_added",
    "action_authority_added",
    "external_resource_authority_added",
    "raw_exception_exposed",
)

__all__ = tuple(name for name in globals() if not name.startswith("_"))
