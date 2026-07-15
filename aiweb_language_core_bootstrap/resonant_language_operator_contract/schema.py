"""Immutable Slice 36B0 RSOC/FBSC language-operator contract records.

This module defines contract state only. It does not project source text, bind
language, apply an operator, assign a phase, construct meaning, consult legacy
RMC, route a tool, read or write memory, access a filesystem or network, or
perform an action.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..schema import stable_record_id

CONTRACT_SPEC_ID: Final[str] = "aiweb-rsoc-fbsc-language-operator-contract"
CONTRACT_SPEC_VERSION: Final[str] = (
    "aiweb-rsoc-fbsc-language-operator-contract-v1"
)
CONTRACT_SCHEMA_VERSION: Final[str] = (
    "aiweb-language-core-rsoc-fbsc-operator-contract-v1"
)
FIELD_SCHEMA_ID: Final[str] = "aiweb-resonant-language-field-envelope-v1"
OPERATOR_SCHEMA_ID: Final[str] = "aiweb-rsoc-operator-contract-v1"
REGISTRY_SCHEMA_ID: Final[str] = "aiweb-rsoc-language-operator-registry-v1"
LEGACY_ISOLATION_SCHEMA_ID: Final[str] = (
    "aiweb-language-operator-legacy-isolation-v1"
)
EXPECTED_RSOC_OPERATOR_COUNT: Final[int] = 10

RSOC_AUTHORITY_REF: Final[str] = (
    "Resonant Symbolic Operator Calculus, First Edition, December 2025"
)
FBSC_AUTHORITY_REF: Final[str] = (
    "Frequency-Based Symbolic Calculus Volume II - Symbolic Grammar Operators"
)
RMC_LANGUAGE_LAW_AUTHORITY_REF: Final[str] = (
    "Document 3 of 10 - RMC Language Law v1"
)
SLICE36A_AUTHORITY_REF: Final[str] = (
    "Slice 36A - deterministic input event and source custody"
)


class OperatorArity(str, Enum):
    UNARY = "unary"
    BINARY = "binary"


class OperatorRuntimeStatus(str, Enum):
    CONTRACT_ONLY_DISABLED = "contract_only_disabled"


class LineageIdentityHandling(str, Enum):
    COPY_UNCHANGED = "copy_unchanged"
    CONTROLLED_MASK_ONLY_UNDER_LATER_AUTHORITY = (
        "controlled_mask_only_under_later_authority"
    )


class FieldProjectionStatus(str, Enum):
    UNPROJECTED = "unprojected"


class FieldPhaseStatus(str, Enum):
    UNASSIGNED = "unassigned"


class FieldSupportStatus(str, Enum):
    UNASSESSED = "unassessed"


class FieldContainmentStatus(str, Enum):
    NOT_CONTAINED = "not_contained"


class FieldEnvelopeBuildStatus(str, Enum):
    CREATED_UNPROJECTED = "created_unprojected_field_envelope"
    HELD_UNSUPPORTED_INPUT = "held_unsupported_input"
    REJECTED_INVALID_INPUT_EVENT = "rejected_invalid_input_event"


class OperatorApplicationStatus(str, Enum):
    REFUSED_CONTRACT_ONLY = "refused_operator_contract_only"
    REFUSED_UNKNOWN_OPERATOR = "refused_unknown_operator"
    REFUSED_INVALID_FIELD = "refused_invalid_field"


class LegacySurfaceCategory(str, Enum):
    WITHDRAWN_LEGACY_LANGUAGE = "withdrawn_legacy_language"
    PROHIBITED_DEPENDENCY = "prohibited_dependency"
    SEPARATE_DOMAIN_NOT_LANGUAGE_AUTHORITY = (
        "separate_domain_not_language_authority"
    )
    REFERENCE_ONLY_NOT_RUNTIME_AUTHORITY = (
        "reference_only_not_runtime_authority"
    )


class LegacySurfaceDisposition(str, Enum):
    ISOLATED_NO_IMPORT_OR_CALL = "isolated_no_import_or_call"
    PROHIBITED_NO_IMPORT_OR_CALL = "prohibited_no_import_or_call"
    SEPARATE_DOMAIN_NO_SUBSTITUTION = "separate_domain_no_substitution"
    STATIC_REFERENCE_ONLY = "static_reference_only"


@dataclass(frozen=True, slots=True)
class ResonantLanguageFieldEnvelope:
    """Source-linked field envelope before projection or operator work."""

    field_id: str
    source_event_id: str
    source_sha256: str
    source_utf8_byte_length: int
    source_code_point_length: int
    root_source_span_id: str
    predecessor_field_id: str | None
    applied_operator_trace_ids: tuple[str, ...]
    covered_source_span_ids: tuple[str, ...]
    unresolved_source_span_ids: tuple[str, ...]
    projection_status: FieldProjectionStatus
    phase_status: FieldPhaseStatus
    support_status: FieldSupportStatus
    containment_status: FieldContainmentStatus
    rsoc_lineage_identity_assigned: bool
    source_text_copied_or_replaced: bool
    tokenization_performed: bool
    operator_binding_performed: bool
    operator_application_performed: bool
    phase_assignment_performed: bool
    concept_lookup_performed: bool
    predicate_binding_performed: bool
    meaning_created: bool
    reference_resolution_performed: bool
    legacy_runtime_consulted: bool
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    environment_access_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    route_registration_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    delivery_performed: bool
    contract_spec_id: str = CONTRACT_SPEC_ID
    contract_spec_version: str = CONTRACT_SPEC_VERSION
    schema_version: str = CONTRACT_SCHEMA_VERSION
    field_schema_id: str = FIELD_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("field_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("resonant_language_field", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FieldEnvelopeBuildResult:
    result_id: str
    status: FieldEnvelopeBuildStatus
    reason_code: str
    envelope_created: bool
    structural_progression_allowed: bool
    field: ResonantLanguageFieldEnvelope | None
    validation_issue_codes: tuple[str, ...]
    filesystem_read_performed: bool
    filesystem_write_performed: bool
    network_access_performed: bool
    environment_access_performed: bool
    memory_read_performed: bool
    memory_write_performed: bool
    route_registration_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    delivery_performed: bool
    contract_spec_id: str = CONTRACT_SPEC_ID
    contract_spec_version: str = CONTRACT_SPEC_VERSION
    schema_version: str = CONTRACT_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("result_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("field_envelope_build_result", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RsocOperatorContract:
    contract_id: str
    operator_key: str
    glyph: str
    canonical_name: str
    arity: OperatorArity
    identity_handling: LineageIdentityHandling
    domain_schema_id: str
    range_schema_id: str
    runtime_status: OperatorRuntimeStatus
    source_authority_refs: tuple[str, ...]
    hard_boundaries: tuple[str, ...]
    may_decrease_entropy: bool
    entropy_thresholds_installed: bool
    commutation_table_installed: bool
    numeric_transform_installed: bool
    runtime_enabled: bool
    application_implemented: bool
    automatic_trigger_authorized: bool
    source_binding_authorized: bool
    phase_assignment_authorized: bool
    meaning_authorized: bool
    memory_authorized: bool
    route_authorized: bool
    tool_authorized: bool
    action_authorized: bool
    delivery_authorized: bool
    contract_spec_id: str = CONTRACT_SPEC_ID
    contract_spec_version: str = CONTRACT_SPEC_VERSION
    schema_version: str = CONTRACT_SCHEMA_VERSION
    operator_schema_id: str = OPERATOR_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("contract_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("rsoc_operator_contract", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RsocLanguageOperatorRegistry:
    registry_id: str
    operators: tuple[RsocOperatorContract, ...]
    exact_operator_count: int
    default_runtime_enabled: bool
    operator_application_available: bool
    source_binding_available: bool
    phase_assignment_available: bool
    legacy_imports_allowed: bool
    mea_substitution_allowed: bool
    hidden_fallback_allowed: bool
    contract_spec_id: str = CONTRACT_SPEC_ID
    contract_spec_version: str = CONTRACT_SPEC_VERSION
    schema_version: str = CONTRACT_SCHEMA_VERSION
    registry_schema_id: str = REGISTRY_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("registry_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("rsoc_language_operator_registry", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class OperatorApplicationDecision:
    decision_id: str
    status: OperatorApplicationStatus
    reason_code: str
    requested_operator_key: str
    field_id: str
    operator_found: bool
    application_performed: bool
    successor_field_created: bool
    phase_assigned: bool
    meaning_created: bool
    memory_read_performed: bool
    memory_write_performed: bool
    route_registration_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    delivery_performed: bool
    contract_spec_id: str = CONTRACT_SPEC_ID
    contract_spec_version: str = CONTRACT_SPEC_VERSION
    schema_version: str = CONTRACT_SCHEMA_VERSION

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("decision_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("operator_application_decision", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LegacyIsolationRecord:
    isolation_id: str
    surface_path: str
    category: LegacySurfaceCategory
    disposition: LegacySurfaceDisposition
    reason_code: str
    static_reference_allowed: bool
    import_allowed: bool
    call_allowed: bool
    language_authority_allowed: bool
    semantic_authority_allowed: bool
    runtime_substitution_allowed: bool
    contract_spec_id: str = CONTRACT_SPEC_ID
    contract_spec_version: str = CONTRACT_SPEC_VERSION
    schema_version: str = CONTRACT_SCHEMA_VERSION
    isolation_schema_id: str = LEGACY_ISOLATION_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("isolation_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("legacy_operator_isolation", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LegacyIsolationCatalog:
    catalog_id: str
    records: tuple[LegacyIsolationRecord, ...]
    legacy_imports_allowed: bool
    legacy_calls_allowed: bool
    legacy_language_authority_allowed: bool
    mea_substitution_allowed: bool
    static_reference_only: bool
    contract_spec_id: str = CONTRACT_SPEC_ID
    contract_spec_version: str = CONTRACT_SPEC_VERSION
    schema_version: str = CONTRACT_SCHEMA_VERSION
    isolation_schema_id: str = LEGACY_ISOLATION_SCHEMA_ID

    def canonical_body(self) -> dict[str, object]:
        body = asdict(self)
        body.pop("catalog_id")
        return body

    def expected_id(self) -> str:
        return stable_record_id("legacy_operator_isolation_catalog", self.canonical_body())

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
