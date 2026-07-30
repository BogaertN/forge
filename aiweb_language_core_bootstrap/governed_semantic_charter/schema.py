"""Immutable records for the first governed Forge semantic-charter proposal.

The charter is an operator-review artifact.  It does not turn provisional
registry records into canon, activate a grammar, select a meaning, write RMC,
or authorize any runtime action.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Final

from ..schema import canonicalize, stable_record_id


GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION: Final[str] = (
    "aiweb-forge-governed-semantic-charter-v0"
)


def _record_dict(value: object) -> dict[str, object]:
    return canonicalize(asdict(value))


class CharterStatus(str, Enum):
    PROPOSED_FOR_OPERATOR_APPROVAL = "PROPOSED_FOR_OPERATOR_APPROVAL"


class CharterReplayStatus(str, Enum):
    PASS = "PASS"
    HELD = "HELD"


class CharterSourceDisposition(str, Enum):
    MATCHED_PROPOSED_FIXTURE = "MATCHED_PROPOSED_FIXTURE"
    HELD_REPLAY_MISMATCH = "HELD_REPLAY_MISMATCH"
    HELD_AMBIGUOUS = "HELD_AMBIGUOUS"
    OUTSIDE_PROPOSED_CHARTER = "OUTSIDE_PROPOSED_CHARTER"
    INVALID_INPUT = "INVALID_INPUT"


@dataclass(frozen=True, slots=True)
class ProposedConceptSense:
    proposal_id: str
    concept_key: str
    concept_ref: str
    sense_key: str
    sense_ref: str
    forge_registry_owned: bool
    source_record_provisional: bool
    operator_approval_required: bool
    schema_version: str = GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("proposal_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("semantic_charter_concept_sense", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class ProposedPredicate:
    proposal_id: str
    predicate_key: str
    predicate_ref: str
    declared_required_role_keys: tuple[str, ...]
    forge_registry_owned: bool
    source_record_provisional: bool
    operator_approval_required: bool
    schema_version: str = GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("proposal_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("semantic_charter_predicate", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class ProposedRole:
    proposal_id: str
    role_key: str
    role_ref: str
    forge_registry_owned: bool
    source_record_provisional: bool
    operator_approval_required: bool
    schema_version: str = GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("proposal_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("semantic_charter_role", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class ProposedConstructionContract:
    construction_id: str
    construction_key: str
    grammar_rule_id: str
    frame_key: str
    speech_act: str
    purport: str
    predicate_key: str
    predicate_ref: str
    effective_role_keys: tuple[str, ...]
    negated: bool
    echo_reparse_only: bool
    exact_fixture_only: bool
    operator_approval_required: bool
    runtime_active: bool
    schema_version: str = GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("construction_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id(
            "semantic_charter_construction", self.identity_payload()
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class SemanticReplayFixture:
    fixture_id: str
    fixture_key: str
    exact_source_text: str
    exact_source_sha256: str
    construction_ref: str
    expected_meaning_candidate_ref: str
    expected_semantic_signature: str
    expected_predicate_ref: str
    expected_role_keys: tuple[str, ...]
    expected_concept_refs: tuple[str, ...]
    expected_sense_refs: tuple[str, ...]
    expected_relation_refs: tuple[str, ...]
    expected_negated: bool
    expected_compiler_status: str
    expected_echo_status: str
    operator_approval_required: bool
    runtime_authority: bool
    schema_version: str = GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("fixture_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("semantic_charter_replay_fixture", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class SemanticCharterBoundary:
    boundary_id: str
    forge_owned: bool
    proposal_only: bool
    operator_approval_required: bool
    operator_approval_present: bool
    active: bool
    canonical_authority: bool
    truth_authority: bool
    selection_authority: bool
    runtime_authority: bool
    route_authority: bool
    tool_authority: bool
    action_authority: bool
    delivery_authority: bool
    memory_write_authority: bool
    external_reference_authority: bool
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
    route_registration_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    delivery_performed: bool
    schema_version: str = GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("boundary_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("semantic_charter_boundary", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class ProposedSemanticCharter:
    charter_id: str
    charter_key: str
    status: CharterStatus
    registry_ref: str
    registry_version: str
    concept_senses: tuple[ProposedConceptSense, ...]
    predicates: tuple[ProposedPredicate, ...]
    roles: tuple[ProposedRole, ...]
    constructions: tuple[ProposedConstructionContract, ...]
    replay_fixtures: tuple[SemanticReplayFixture, ...]
    boundary: SemanticCharterBoundary
    deterministic: bool
    forge_owned: bool
    proposed: bool
    operator_approval_required: bool
    operator_approval_present: bool
    active: bool
    canonical_authority: bool
    runtime_authority: bool
    memory_write_authority: bool
    schema_version: str = GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("charter_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("governed_semantic_charter", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class CharterReplayCaseResult:
    case_result_id: str
    fixture_ref: str
    compiler_result_ref: str
    observed_meaning_candidate_ref: str
    observed_semantic_signature: str
    observed_compiler_status: str
    observed_echo_status: str
    construction_matched: bool
    semantic_identity_matched: bool
    exact_reference_sets_matched: bool
    passed: bool
    reason_codes: tuple[str, ...]
    operator_approval_granted: bool
    runtime_authority: bool
    schema_version: str = GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("case_result_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("semantic_charter_replay_case", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class CharterReplayResult:
    replay_id: str
    charter_ref: str
    status: CharterReplayStatus
    case_results: tuple[CharterReplayCaseResult, ...]
    reason_codes: tuple[str, ...]
    deterministic: bool
    validation_only: bool
    operator_approval_granted: bool
    charter_activated: bool
    filesystem_write_performed: bool
    memory_write_performed: bool
    route_registration_performed: bool
    tool_routing_performed: bool
    action_performed: bool
    delivery_performed: bool
    schema_version: str = GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("replay_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("semantic_charter_replay", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True, slots=True)
class CharterSourceEvaluation:
    evaluation_id: str
    charter_ref: str
    source_sha256: str
    disposition: CharterSourceDisposition
    fixture_ref: str
    compiler_result_ref: str
    compiler_status: str
    compiler_reason_codes: tuple[str, ...]
    meaning_candidate_count: int
    selected_meaning_ref: str
    proposed_match_only: bool
    operator_approval_granted: bool
    runtime_authority: bool
    memory_write_performed: bool
    action_performed: bool
    delivery_performed: bool
    schema_version: str = GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION

    def identity_payload(self) -> dict[str, object]:
        value = self.to_dict()
        value.pop("evaluation_id", None)
        return value

    def expected_id(self) -> str:
        return stable_record_id("semantic_charter_source_evaluation", self.identity_payload())

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


class SemanticCharterValidationError(ValueError):
    """Typed fail-closed rejection of a malformed or drifted proposal."""

    def __init__(self, issues: tuple[str, ...]) -> None:
        self.issues = issues
        super().__init__(";".join(issues))


__all__ = (
    "CharterReplayCaseResult",
    "CharterReplayResult",
    "CharterReplayStatus",
    "CharterSourceDisposition",
    "CharterSourceEvaluation",
    "CharterStatus",
    "GOVERNED_SEMANTIC_CHARTER_SCHEMA_VERSION",
    "ProposedConceptSense",
    "ProposedConstructionContract",
    "ProposedPredicate",
    "ProposedRole",
    "ProposedSemanticCharter",
    "SemanticCharterBoundary",
    "SemanticCharterValidationError",
    "SemanticReplayFixture",
)
