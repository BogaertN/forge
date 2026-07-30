"""Immutable records for the deterministic Forge Operator Council.

The Council records recommendations and dissent only.  None of these records
carry truth, permission, tool, action, delivery, or memory-write authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..schema import canonicalize, stable_record_id


OPERATOR_COUNCIL_SCHEMA_VERSION: Final[str] = "aiweb-forge-operator-council-v0"


def _record_dict(value: object) -> dict[str, object]:
    return canonicalize(asdict(value))


class CouncilRole(str, Enum):
    SEMANTIC_STEWARD = "semantic_steward"
    RMC_WITNESS = "rmc_witness"
    AUTHORITY_AUDITOR = "authority_auditor"
    ADVERSARIAL_CHALLENGER = "adversarial_challenger"
    SYNTHESIZER = "synthesizer"


class CouncilStance(str, Enum):
    SUPPORT = "SUPPORT"
    HOLD = "HOLD"
    OPPOSE = "OPPOSE"


class CouncilDisposition(str, Enum):
    RECOMMEND_FOR_OPERATOR_REVIEW = "RECOMMEND_FOR_OPERATOR_REVIEW"
    HOLD_FOR_EVIDENCE = "HOLD_FOR_EVIDENCE"


@dataclass(frozen=True, slots=True)
class SemanticRmcEvidenceEnvelope:
    """Selected semantic and RMC evidence; never a raw-language request."""

    envelope_id: str
    selected_meaning_ref: str
    semantic_signature: str
    speech_act: str
    purport: str
    predicate_ref: str
    concept_refs: tuple[str, ...]
    relation_refs: tuple[str, ...]
    ancestry_refs: tuple[str, ...]
    gate_receipt_refs: tuple[str, ...]
    gates_passed: bool
    echo_receipt_ref: str
    echo_status: str
    rmc_snapshot_ref: str
    rmc_connection_status: str
    selected_meaning_support_status: str
    rmc_evidence_refs: tuple[str, ...]
    authority_evidence_refs: tuple[str, ...]
    contradiction_refs: tuple[str, ...]
    uncertainty_refs: tuple[str, ...]
    selected_meaning_validated: bool
    exact_reference_resonance_only: bool
    read_only: bool
    raw_text_present: bool
    tokenization_performed: bool
    model_called: bool
    embedding_used: bool
    vector_used: bool
    similarity_scoring_used: bool
    memory_write_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    delivery_performed: bool
    schema_version: str = OPERATOR_COUNCIL_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("envelope_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("operator_council_evidence", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class CouncilMemberPosition:
    position_id: str
    envelope_ref: str
    role: CouncilRole
    stance: CouncilStance
    evidence_refs: tuple[str, ...]
    reason_codes: tuple[str, ...]
    material_dissent: bool
    independent_evaluation: bool
    recommendation_only: bool
    decision_authority: bool
    schema_version: str = OPERATOR_COUNCIL_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("position_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("operator_council_position", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class CouncilDissent:
    dissent_id: str
    position_ref: str
    role: CouncilRole
    severity: str
    reason_codes: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    resolved: bool
    blocks_recommendation: bool
    schema_version: str = OPERATOR_COUNCIL_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("dissent_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("operator_council_dissent", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class CouncilRecommendation:
    recommendation_id: str
    envelope_ref: str
    disposition: CouncilDisposition
    participant_roles: tuple[CouncilRole, ...]
    support_roles: tuple[CouncilRole, ...]
    hold_roles: tuple[CouncilRole, ...]
    oppose_roles: tuple[CouncilRole, ...]
    quorum_threshold: int
    participant_count: int
    quorum_reached: bool
    concurrence_threshold: int
    support_count: int
    concurrence_reached: bool
    mandatory_roles_satisfied: bool
    material_dissent_present: bool
    reason_codes: tuple[str, ...]
    recommendation_only: bool
    operator_decision_required: bool
    executable: bool
    authoritative: bool
    schema_version: str = OPERATOR_COUNCIL_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("recommendation_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id(
            "operator_council_recommendation", self.identity_payload()
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class OperatorCouncilBoundary:
    boundary_id: str
    deterministic: bool
    recommendation_only: bool
    selected_semantic_evidence_only: bool
    raw_text_accepted: bool
    tokenization_performed: bool
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
    tool_routing_performed: bool
    action_performed: bool
    delivery_performed: bool
    truth_authority: bool
    evidence_authority: bool
    permission_authority: bool
    decision_authority: bool
    tool_authority: bool
    action_authority: bool
    delivery_authority: bool
    memory_write_authority: bool
    schema_version: str = OPERATOR_COUNCIL_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("boundary_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("operator_council_boundary", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class OperatorCouncilDecisionReceipt:
    """Receipt for a Council disposition, not an executable OS decision."""

    receipt_id: str
    result_digest: str
    envelope_ref: str
    recommendation_ref: str
    position_refs: tuple[str, ...]
    dissent_refs: tuple[str, ...]
    decision_kind: str
    deterministic: bool
    input_validated: bool
    output_validated: bool
    recommendation_only: bool
    operator_decision_required: bool
    council_decision_authorized: bool
    writes_performed: bool
    tools_invoked: bool
    action_performed: bool
    delivery_performed: bool
    schema_version: str = OPERATOR_COUNCIL_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("receipt_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("operator_council_receipt", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class OperatorCouncilResult:
    result_id: str
    evidence: SemanticRmcEvidenceEnvelope
    positions: tuple[CouncilMemberPosition, ...]
    dissents: tuple[CouncilDissent, ...]
    recommendation: CouncilRecommendation
    boundary: OperatorCouncilBoundary
    receipt: OperatorCouncilDecisionReceipt
    schema_version: str = OPERATOR_COUNCIL_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("result_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("operator_council_result", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


class CouncilValidationError(ValueError):
    """Raised before deliberation when an evidence envelope is not admissible."""

    def __init__(self, issues: tuple[str, ...]) -> None:
        self.issues = issues
        super().__init__("; ".join(issues) or "operator_council_validation_failed")


__all__ = (
    "CouncilDisposition",
    "CouncilDissent",
    "CouncilMemberPosition",
    "CouncilRecommendation",
    "CouncilRole",
    "CouncilStance",
    "CouncilValidationError",
    "OPERATOR_COUNCIL_SCHEMA_VERSION",
    "OperatorCouncilBoundary",
    "OperatorCouncilDecisionReceipt",
    "OperatorCouncilResult",
    "SemanticRmcEvidenceEnvelope",
)
