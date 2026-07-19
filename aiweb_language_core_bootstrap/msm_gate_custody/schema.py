"""Additive Slice 40H MSM gate-custody companion contracts.

The accepted MeaningStructureManifestV1 schema is not modified.  These records
preserve exact Slice 40C-40G results and create only lawful non-selection
projections into an immutable MSM-v1 successor.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Final

SLICE40H_SCHEMA_VERSION: Final[str] = "aiweb-slice40h-msm-gate-custody-v1"
SLICE40H_ACCEPTED_PARENT_HEAD: Final[str] = "3f13618b6e60efdc5c3bfb7b89043c1b9d8a25aa"
SLICE40H_ACCEPTED_PARENT_TREE: Final[str] = "150d9568bd92d7ba98dc8ef02244bf01648732c4"
SLICE40H_ACCEPTED_PARENT_SUBJECT: Final[str] = "Slice 40G deterministic gate composition non-selection disposition runtime"
SLICE40H_COMMIT_SUBJECT: Final[str] = "Slice 40H MSM gate integration disabled bootstrap and Slice 40 closeout"

class GateFamilyName(str, Enum):
    EXPECTANCY = "expectancy"
    CONGRUITY = "congruity"
    CONNECTEDNESS = "connectedness"
    RECOVERABLE_PURPOSE = "recoverable_purpose"

class ProjectionDisposition(str, Enum):
    UNRESOLVED = "unresolved"
    UNSUPPORTED = "unsupported"
    REFUSED_CUSTODY = "refused_custody"
    AUTHORITY_BLOCKED = "authority_blocked"
    COMPANION_ONLY = "companion_only"

@dataclass(frozen=True, slots=True)
class GateFamilyCustodyRecord:
    custody_id: str
    family: GateFamilyName
    result_id: str
    canonical_digest: str
    candidate_input_ref: str
    overall_state: str
    result_schema_version: str
    preserved_exactly: bool
    schema_version: str = SLICE40H_SCHEMA_VERSION

@dataclass(frozen=True, slots=True)
class GateDispositionProjectionRecord:
    projection_id: str
    source_disposition_id: str
    source_disposition_kind: str
    projection_disposition: ProjectionDisposition
    msm_outcome_record_ref: str | None
    companion_only: bool
    selected_meaning_created: bool
    schema_version: str = SLICE40H_SCHEMA_VERSION

@dataclass(frozen=True, slots=True)
class MsmGateCustodyCompanionV1:
    companion_id: str
    companion_version: str
    source_manifest_id: str
    successor_manifest_id: str
    lineage_id: str
    manifest_candidate_ref: str
    candidate_input_ref: str
    candidate_branch_ref: str
    family_custody: tuple[GateFamilyCustodyRecord, ...]
    composition_result_id: str
    composition_result_digest: str
    composition_status: str
    composition_disposition_refs: tuple[str, ...]
    projections: tuple[GateDispositionProjectionRecord, ...]
    family_results_preserved: bool
    composition_result_preserved: bool
    candidate_side_only: bool
    non_selection_only: bool
    exact_adapter: bool
    lossless_custody: bool
    clarification_relevant_not_required: bool
    positive_selection_review_companion_only: bool
    refusal_relevant_not_outward_refusal: bool
    selected_meaning_created: bool
    schema_version: str = SLICE40H_SCHEMA_VERSION

@dataclass(frozen=True, slots=True)
class MsmGateIntegrationResult:
    result_id: str
    source_manifest_id: str
    successor_manifest_id: str
    manifest_candidate_ref: str
    successor_manifest: object
    companion: MsmGateCustodyCompanionV1
    projected_outcome_count: int
    companion_only_count: int
    deterministic: bool
    additive_only: bool
    existing_msm_schema_modified: bool
    automatic_migration_performed: bool
    gate_results_preserved: bool
    selected_meaning_created: bool
    truth_determined: bool
    evidence_validated: bool
    permission_granted: bool
    execution_authorized: bool
    route_created: bool
    tool_invoked: bool
    action_performed: bool
    memory_accessed: bool
    memory_written: bool
    rendered: bool
    delivered: bool
    schema_version: str = SLICE40H_SCHEMA_VERSION
