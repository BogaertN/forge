"""Immutable records for governed Language Core output previews.

These records describe deterministic evidence only.  They grant no answer,
tool, action, route, filesystem, network, environment, or memory authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..meaning_compiler_preview.schema import (
    MeaningCompilerPreviewResult,
    SemanticContractBinding,
)
from ..schema import canonicalize, stable_record_id


GOVERNED_OUTPUT_SCHEMA_VERSION: Final[str] = (
    "aiweb-forge-governed-output-delivery-v1"
)
GOVERNED_OUTPUT_RENDERER_VERSION: Final[str] = (
    "aiweb-forge-deterministic-output-renderer-v1"
)
DEFINITION_RESPONSE_TRANSITION: Final[str] = (
    "FORGE-OUTPUT-TRANSITION-V1-DEFINITION-REQUEST-TO-RESPONSE"
)
CONTROLLED_RESTATEMENT_TRANSITION: Final[str] = (
    "FORGE-OUTPUT-TRANSITION-V1-CONTROLLED-RESTATEMENT"
)


def _record_dict(value: object) -> dict[str, object]:
    return canonicalize(asdict(value))


class OutputPurpose(str, Enum):
    DEFINITION_ANSWER = "definition_answer"
    CONTROLLED_RESTATEMENT_PREVIEW = "controlled_restatement_preview"


class ExactEchoStatus(str, Enum):
    PASS = "PASS"
    REJECT = "REJECT"
    CONTAIN = "CONTAIN"


class ClarificationReentryStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    HELD = "HELD"


@dataclass(frozen=True, slots=True)
class PureOutputBoundary:
    boundary_id: str
    deterministic: bool
    source_forms_preserved: bool
    normalization_performed: bool
    tokenization_performed: bool
    model_token_stream_created: bool
    subword_token_stream_created: bool
    numeric_token_ids_created: bool
    model_called: bool
    embedding_used: bool
    vector_used: bool
    similarity_scoring_used: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    environment_access_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    route_registration_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    answer_delivery_authorized: bool
    answer_delivery_performed: bool
    schema_version: str = GOVERNED_OUTPUT_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("boundary_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("governed_output_boundary", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


def pure_output_boundary() -> PureOutputBoundary:
    value = PureOutputBoundary(
        boundary_id="pending",
        deterministic=True,
        source_forms_preserved=True,
        normalization_performed=False,
        tokenization_performed=False,
        model_token_stream_created=False,
        subword_token_stream_created=False,
        numeric_token_ids_created=False,
        model_called=False,
        embedding_used=False,
        vector_used=False,
        similarity_scoring_used=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        environment_access_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        route_registration_performed=False,
        tool_routing_performed=False,
        action_performed=False,
        answer_delivery_authorized=False,
        answer_delivery_performed=False,
    )
    return PureOutputBoundary(
        **{**value.to_dict(), "boundary_id": value.expected_id()}
    )


@dataclass(frozen=True, slots=True)
class ExactSemanticRole:
    role_id: str
    role_key: str
    concept_ref: str
    sense_ref: str
    schema_version: str = GOVERNED_OUTPUT_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("role_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("governed_output_semantic_role", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class GovernedOutputManifest:
    manifest_id: str
    schema_version: str
    status: str
    output_purpose: OutputPurpose
    compiler_result_ref: str
    compiler_receipt_ref: str
    source_custody_ref: str
    source_sha256: str
    registry_ref: str
    selected_meaning_ref: str
    source_semantic_contract: SemanticContractBinding
    source_role_bindings: tuple[ExactSemanticRole, ...]
    source_relation_refs: tuple[str, ...]
    meaning_gate_refs: tuple[str, ...]
    rmc_evaluation_ref: str
    rmc_snapshot_ref: str
    rmc_resonance_refs: tuple[str, ...]
    compiler_candidate_wording_ref: str
    compiler_echo_ref: str
    algebra_trace_refs: tuple[str, ...]
    compiler_stage_refs: tuple[str, ...]
    council_result_ref: str
    council_evidence_ref: str
    council_recommendation_ref: str
    council_receipt_ref: str
    council_disposition: str
    render_template_key: str
    transition_rule_ref: str
    expected_output_semantic_contract: SemanticContractBinding
    expected_output_role_bindings: tuple[ExactSemanticRole, ...]
    expected_output_relation_refs: tuple[str, ...]
    answer_delivery_eligible: bool
    operator_review_required: bool
    council_recommendation_only: bool
    preview_only: bool
    delivery_authorized: bool
    delivery_performed: bool
    boundary: PureOutputBoundary

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("manifest_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("governed_output_manifest", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class RenderedOutputCandidate:
    rendered_output_id: str
    schema_version: str
    manifest_ref: str
    compiler_result_ref: str
    selected_meaning_ref: str
    registry_ref: str
    renderer_version: str
    output_purpose: OutputPurpose
    template_key: str
    transition_rule_ref: str
    text: str
    text_sha256: str
    code_point_length: int
    utf8_byte_length: int
    source_semantic_contract_ref: str
    expected_output_semantic_contract: SemanticContractBinding
    expected_output_role_bindings: tuple[ExactSemanticRole, ...]
    expected_output_relation_refs: tuple[str, ...]
    answer_delivery_eligible: bool
    provisional: bool
    operator_preview_exposed: bool
    answer_delivery_authorized: bool
    answer_delivery_performed: bool
    boundary: PureOutputBoundary

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("rendered_output_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("governed_rendered_output", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class DecodedOutput:
    decoded_output_id: str
    schema_version: str
    rendered_output_ref: str
    rendered_text_sha256: str
    decoder_compiler_result_ref: str
    decoder_source_custody_ref: str
    admitted_candidate_count: int
    decoded_meaning_ref: str
    decoded_semantic_contract: SemanticContractBinding | None
    decoded_role_bindings: tuple[ExactSemanticRole, ...]
    decoded_relation_refs: tuple[str, ...]
    decoded_gate_refs: tuple[str, ...]
    unknown_source_form_refs: tuple[str, ...]
    unique_gate_admitted_decode: bool
    full_source_coverage: bool
    deterministic: bool
    boundary: PureOutputBoundary

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("decoded_output_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("governed_decoded_output", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class ExactOutputEcho:
    echo_id: str
    schema_version: str
    status: ExactEchoStatus
    reason_codes: tuple[str, ...]
    manifest_ref: str
    rendered_output_ref: str
    decoded_output: DecodedOutput
    source_semantic_contract_ref: str
    expected_output_semantic_contract_ref: str
    decoded_output_semantic_contract_ref: str
    transition_rule_ref: str
    transition_admitted: bool
    exact_contract_match: bool
    exact_role_match: bool
    exact_relation_match: bool
    unique_decode: bool
    full_source_coverage: bool
    answer_delivery_eligible: bool
    operator_approval_required: bool
    answer_delivery_authorized: bool
    answer_delivery_performed: bool
    boundary: PureOutputBoundary

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("echo_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("governed_exact_output_echo", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class ClarificationReentryReceipt:
    receipt_id: str
    schema_version: str
    status: str
    clarification_request_ref: str
    original_compiler_result_ref: str
    original_compiler_receipt_ref: str
    original_source_custody_ref: str
    original_source_sha256: str
    original_rmc_evaluation_ref: str
    original_rmc_snapshot_ref: str
    original_option_refs: tuple[str, ...]
    original_alternative_meaning_refs: tuple[str, ...]
    original_alternative_semantic_contract_refs: tuple[str, ...]
    clarified_compiler_result_ref: str
    clarified_compiler_receipt_ref: str
    clarified_source_custody_ref: str
    clarified_source_sha256: str
    clarified_rmc_evaluation_ref: str
    clarified_rmc_snapshot_ref: str
    clarified_selected_meaning_ref: str
    matched_option_ref: str
    matched_original_meaning_ref: str
    matched_semantic_contract_ref: str
    all_original_alternatives_preserved: bool
    clarification_response_consumed: bool
    compiler_selection_performed: bool
    operator_option_selection_performed: bool
    answer_delivery_authorized: bool
    answer_delivery_performed: bool
    action_performed: bool
    tool_routing_performed: bool
    memory_write_performed: bool
    boundary: PureOutputBoundary

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("receipt_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id(
            "governed_clarification_reentry_receipt",
            self.identity_payload(),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class ClarificationReentryResult:
    result_id: str
    schema_version: str
    status: ClarificationReentryStatus
    reason_codes: tuple[str, ...]
    clarification_request_ref: str
    clarified_compiler_result: MeaningCompilerPreviewResult
    receipt: ClarificationReentryReceipt | None
    live_clarification_session_started: bool
    clarification_response_consumed: bool
    compiler_selection_performed: bool
    operator_option_selection_performed: bool
    answer_delivery_authorized: bool
    answer_delivery_performed: bool
    action_performed: bool
    tool_routing_performed: bool
    memory_write_performed: bool
    boundary: PureOutputBoundary

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("result_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id(
            "governed_clarification_reentry_result",
            self.identity_payload(),
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


class GovernedOutputValidationError(ValueError):
    """Typed fail-closed rejection for an untrusted output evidence chain."""

    def __init__(self, issues: tuple[str, ...]) -> None:
        self.issues = tuple(issues)
        super().__init__(";".join(self.issues) or "governed_output_validation_failed")


__all__ = (
    "CONTROLLED_RESTATEMENT_TRANSITION",
    "DEFINITION_RESPONSE_TRANSITION",
    "GOVERNED_OUTPUT_RENDERER_VERSION",
    "GOVERNED_OUTPUT_SCHEMA_VERSION",
    "ClarificationReentryReceipt",
    "ClarificationReentryResult",
    "ClarificationReentryStatus",
    "DecodedOutput",
    "ExactEchoStatus",
    "ExactOutputEcho",
    "ExactSemanticRole",
    "GovernedOutputManifest",
    "GovernedOutputValidationError",
    "OutputPurpose",
    "PureOutputBoundary",
    "RenderedOutputCandidate",
    "pure_output_boundary",
)
