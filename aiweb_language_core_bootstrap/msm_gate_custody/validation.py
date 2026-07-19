"""Fail-closed Slice 40H validation."""
from __future__ import annotations
from dataclasses import dataclass
from .schema import *
from ..meaning_structure_manifest import MeaningStructureManifestV1

@dataclass(frozen=True, slots=True)
class ValidationReport:
    issues: tuple[str, ...]
    @property
    def ok(self) -> bool: return not self.issues

def _text(value): return type(value) is str and bool(value.strip())
def _digest(value): return type(value) is str and len(value)==64 and all(c in '0123456789abcdef' for c in value)

def validate_companion(value: object) -> ValidationReport:
    issues=[]
    if type(value) is not MsmGateCustodyCompanionV1: return ValidationReport(('type',))
    for name in ('companion_id','source_manifest_id','successor_manifest_id','lineage_id','manifest_candidate_ref','candidate_input_ref','candidate_branch_ref','composition_result_id'):
        if not _text(getattr(value,name,None)): issues.append(name)
    if not _digest(value.composition_result_digest): issues.append('composition_result_digest')
    if len(value.family_custody)!=4 or tuple(x.family for x in value.family_custody)!=tuple(GateFamilyName): issues.append('family_custody')
    if any(not x.preserved_exactly or not _digest(x.canonical_digest) for x in value.family_custody): issues.append('family_exact')
    if tuple(x.source_disposition_id for x in value.projections)!=value.composition_disposition_refs: issues.append('projection_refs')
    for name in ('family_results_preserved','composition_result_preserved','candidate_side_only','non_selection_only','exact_adapter','lossless_custody','clarification_relevant_not_required','positive_selection_review_companion_only','refusal_relevant_not_outward_refusal'):
        if getattr(value,name) is not True: issues.append(name)
    if value.selected_meaning_created is not False: issues.append('selected_meaning_created')
    return ValidationReport(tuple(issues))

def validate_result(value: object) -> ValidationReport:
    issues=[]
    if type(value) is not MsmGateIntegrationResult: return ValidationReport(('type',))
    if not isinstance(value.successor_manifest, MeaningStructureManifestV1): issues.append('successor_manifest')
    if not validate_companion(value.companion).ok: issues.append('companion')
    if value.successor_manifest_id != value.successor_manifest.manifest_id: issues.append('manifest_id')
    if value.projected_outcome_count != len(value.successor_manifest.non_selection_outcomes): issues.append('projection_count')
    for name in ('deterministic','additive_only','gate_results_preserved'):
        if getattr(value,name) is not True: issues.append(name)
    for name in ('existing_msm_schema_modified','automatic_migration_performed','selected_meaning_created','truth_determined','evidence_validated','permission_granted','execution_authorized','route_created','tool_invoked','action_performed','memory_accessed','memory_written','rendered','delivered'):
        if getattr(value,name) is not False: issues.append(name)
    if value.successor_manifest.selected_governed_meanings: issues.append('selected_manifest_state')
    return ValidationReport(tuple(issues))
