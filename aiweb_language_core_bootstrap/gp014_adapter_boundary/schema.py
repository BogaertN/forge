"""Typed immutable records for the Slice 45 bounded GP-014 adapter."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from .authority import SLICE45_SCHEMA_VERSION
from .canonical import canonical_value, stable_identifier

if TYPE_CHECKING:
    from rmc_engine_v1.general_pipeline.symbolic_math_language_vertical_slice import NaturalLanguageMathPipelineResult


@dataclass(frozen=True, slots=True)
class Gp014AdapterState:
    state_id: str
    enabled: bool
    explicit_offline_developer_enable: bool
    disabled_by_default: bool
    explicit_invocation_required: bool
    exact_question_forwarding_required: bool
    unchanged_gp014_required: bool
    existing_gp014_scope_only: bool
    deterministic: bool
    local_only: bool
    adapter_read_only: bool
    adapter_in_memory_only: bool
    runtime_registration_allowed: bool
    main_registration_allowed: bool
    route_allowed: bool
    api_allowed: bool
    ui_allowed: bool
    network_authority_added: bool
    filesystem_write_authority_added: bool
    memory_authority_added: bool
    evidence_authority_added: bool
    truth_authority_added: bool
    permission_authority_added: bool
    delivery_authority_added: bool
    tool_authority_added: bool
    action_authority_added: bool
    external_resource_authority_added: bool
    gp014_import_allowed: bool
    gp014_call_allowed: bool
    gp014_modification_allowed: bool
    gp014_supersession_allowed: bool
    gp015_reuse_allowed: bool
    production_ready: bool
    release_authorized: bool
    schema_version: str = SLICE45_SCHEMA_VERSION

    def expected_id(self) -> str:
        return stable_identifier("slice45_gp014_adapter_state", self, excluded_fields=("state_id",))

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


@dataclass(frozen=True, slots=True)
class Gp014AdapterRequest:
    request_id: str
    question: str
    question_sha256: str
    requested_operation: str
    adapter_scope: str
    explicit_invocation: bool
    preserve_question_byte_for_byte: bool
    permit_normalization_or_rewrite: bool
    permit_scope_broadening: bool
    permit_route_or_ui_use: bool
    permit_gp015_reuse: bool
    schema_version: str = SLICE45_SCHEMA_VERSION

    def expected_id(self) -> str:
        return stable_identifier("slice45_gp014_adapter_request", self, excluded_fields=("request_id",))

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


@dataclass(frozen=True, slots=True)
class Gp014BindingIdentity:
    identity_id: str
    build_id: str
    realizer_schema_version: str
    expression_lexicon_authority_class: str
    supported_operation_families: tuple[str, ...]
    meaning_locked_before_phrase_selection: bool
    actual_echo_required_after_selection: bool
    realizer_adds_delivery_authority: bool
    route_or_ui_added: bool
    corpus_ingestion_added: bool
    llm_used: bool
    memory_write_added: bool
    gp015_loaded: bool
    schema_version: str = SLICE45_SCHEMA_VERSION

    def expected_id(self) -> str:
        return stable_identifier("slice45_gp014_binding_identity", self, excluded_fields=("identity_id",))

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


@dataclass(frozen=True, slots=True)
class Gp014AdapterReceipt:
    receipt_id: str
    request_id: str
    state_id: str
    binding_identity_id: str | None
    source_status: str | None
    source_result_hash: str | None
    source_question_sha256: str | None
    operation_family: str | None
    answer_text_sha256: str | None
    expression_realization_receipt_hash: str | None
    echo_hash: str | None
    delivery_authorization_v2_hash: str | None
    question_forwarded_byte_for_byte: bool
    source_result_returned_unchanged: bool
    source_status_rewritten: bool
    source_answer_rewritten: bool
    source_trace_mutated: bool
    gp014_imported: bool
    gp014_called: bool
    gp014_modified: bool
    gp014_superseded: bool
    gp015_used: bool
    main_modified_or_called: bool
    route_created_or_called: bool
    api_created_or_called: bool
    ui_created_or_called: bool
    network_authority_added: bool
    filesystem_write_authority_added: bool
    memory_authority_added: bool
    evidence_authority_added: bool
    truth_authority_added: bool
    permission_authority_added: bool
    delivery_authority_added_by_adapter: bool
    existing_gp014_delivery_receipt_observed: bool
    tool_authority_added: bool
    action_authority_added: bool
    external_resource_authority_added: bool
    raw_exception_exposed: bool
    schema_version: str = SLICE45_SCHEMA_VERSION

    def expected_id(self) -> str:
        return stable_identifier("slice45_gp014_adapter_receipt", self, excluded_fields=("receipt_id",))

    def to_dict(self) -> dict[str, Any]:
        return canonical_value(self)


@dataclass(frozen=True, slots=True)
class Gp014AdapterResult:
    result_id: str
    status: str
    reason_code: str
    request_id: str | None
    state_id: str | None
    binding_identity: Gp014BindingIdentity | None
    receipt: Gp014AdapterReceipt
    source_result: "NaturalLanguageMathPipelineResult | None"
    adapter_completed: bool
    source_answered: bool
    source_contained: bool
    schema_version: str = SLICE45_SCHEMA_VERSION

    def expected_id(self) -> str:
        body = {
            "status": self.status,
            "reason_code": self.reason_code,
            "request_id": self.request_id,
            "state_id": self.state_id,
            "binding_identity_id": None if self.binding_identity is None else self.binding_identity.identity_id,
            "receipt_id": self.receipt.receipt_id,
            "adapter_completed": self.adapter_completed,
            "source_answered": self.source_answered,
            "source_contained": self.source_contained,
            "schema_version": self.schema_version,
        }
        return stable_identifier("slice45_gp014_adapter_result", body)

    def to_dict(self) -> dict[str, Any]:
        source = self.source_result
        source_dict = None
        if source is not None and callable(getattr(source, "to_dict", None)):
            source_dict = source.to_dict()
        return {
            "result_id": self.result_id,
            "status": self.status,
            "reason_code": self.reason_code,
            "request_id": self.request_id,
            "state_id": self.state_id,
            "binding_identity": None if self.binding_identity is None else self.binding_identity.to_dict(),
            "receipt": self.receipt.to_dict(),
            "source_result": source_dict,
            "adapter_completed": self.adapter_completed,
            "source_answered": self.source_answered,
            "source_contained": self.source_contained,
            "schema_version": self.schema_version,
        }


__all__ = tuple(name for name in globals() if not name.startswith("_"))
