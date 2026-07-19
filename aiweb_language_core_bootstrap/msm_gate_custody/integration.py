"""Exact additive MSM-v1 projection of accepted Slice 40 gate results."""
from __future__ import annotations
from dataclasses import replace
from ..schema import stable_record_id
from ..meaning_structure_manifest import (
    MeaningStructureManifestV1, NonSelectionOutcomeKind, NonSelectionOutcomeRecord,
    SemanticLifecycleState, SemanticTransitionKind, SemanticTransitionTraceRecord,
)
from ..meaning_structure_manifest.validation import validate_manifest
from ..verbal_cognition_gate_runtime.expectancy_gate import ExpectancyGateResult
from ..verbal_cognition_gate_runtime.congruity_gate import CongruityGateResult
from ..verbal_cognition_gate_runtime.connectedness_gate import ConnectednessGateResult
from ..verbal_cognition_gate_runtime.recoverable_purpose_gate import RecoverablePurposeGateResult
from ..verbal_cognition_gate_runtime.gate_composition import (
    GateCompositionDispositionKind, GateCompositionResult,
)
from .canonical import with_id
from .schema import *
from .validation import validate_result

_MAP = {
    GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED: (ProjectionDisposition.UNRESOLVED, NonSelectionOutcomeKind.UNRESOLVED),
    GateCompositionDispositionKind.CLARIFICATION_RELEVANT: (ProjectionDisposition.COMPANION_ONLY, None),
    GateCompositionDispositionKind.UNSUPPORTED: (ProjectionDisposition.UNSUPPORTED, NonSelectionOutcomeKind.UNSUPPORTED),
    GateCompositionDispositionKind.REFUSAL_RELEVANT: (ProjectionDisposition.REFUSED_CUSTODY, NonSelectionOutcomeKind.REFUSED),
    GateCompositionDispositionKind.HELD: (ProjectionDisposition.UNRESOLVED, NonSelectionOutcomeKind.UNRESOLVED),
    GateCompositionDispositionKind.BLOCKED_PROGRESSION: (ProjectionDisposition.AUTHORITY_BLOCKED, NonSelectionOutcomeKind.AUTHORITY_BLOCKED),
    GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW: (ProjectionDisposition.COMPANION_ONLY, None),
}

def _family(family, result):
    return with_id(GateFamilyCustodyRecord(
        custody_id='', family=family, result_id=result.result_id,
        canonical_digest=result.canonical_digest,
        candidate_input_ref=result.candidate_input_ref,
        overall_state=result.overall_state.value,
        result_schema_version=result.schema_version,
        preserved_exactly=True,
    ), 'slice40h_gate_family_custody', 'custody_id')

def integrate_gate_results_into_manifest(
    manifest: MeaningStructureManifestV1,
    manifest_candidate_ref: str,
    expectancy: ExpectancyGateResult,
    congruity: CongruityGateResult,
    connectedness: ConnectednessGateResult,
    recoverable_purpose: RecoverablePurposeGateResult,
    composition: GateCompositionResult,
) -> MsmGateIntegrationResult:
    if type(manifest) is not MeaningStructureManifestV1 or not validate_manifest(manifest).ok:
        raise ValueError('exact valid MeaningStructureManifestV1 required')
    typed=((ExpectancyGateResult,expectancy),(CongruityGateResult,congruity),(ConnectednessGateResult,connectedness),(RecoverablePurposeGateResult,recoverable_purpose),(GateCompositionResult,composition))
    if any(type(value) is not cls for cls,value in typed): raise ValueError('exact Slice 40 result types required')
    candidate_ids=tuple(item.record_id for item in manifest.candidate_meanings)
    if manifest_candidate_ref not in candidate_ids: raise ValueError('manifest candidate reference not found')
    family=(expectancy,congruity,connectedness,recoverable_purpose)
    expected_family_refs=tuple(item.candidate_input_ref for item in family)
    if tuple(composition.expectancy_candidate_input_ref for _ in (0,)) + (composition.congruity_candidate_input_ref, composition.connectedness_candidate_input_ref, composition.recoverable_purpose_candidate_input_ref) != expected_family_refs:
        raise ValueError('candidate-specific family result custody mismatch')
    expected=((composition.expectancy_result_id,composition.expectancy_result_digest,expectancy),(composition.congruity_result_id,composition.congruity_result_digest,congruity),(composition.connectedness_result_id,composition.connectedness_result_digest,connectedness),(composition.recoverable_purpose_result_id,composition.recoverable_purpose_result_digest,recoverable_purpose))
    if any(rid!=value.result_id or digest!=value.canonical_digest for rid,digest,value in expected): raise ValueError('composition family result identity mismatch')
    if composition.selected_meaning_created or composition.candidate_accepted: raise ValueError('selection or acceptance prohibited')

    outcomes=[]; traces=[]; projections=[]
    for disposition in composition.dispositions:
        projection_kind, outcome_kind = _MAP[disposition.disposition_kind]
        outcome_ref=None
        if outcome_kind is not None:
            body={'lineage_id':manifest.lineage_root.lineage_id,'kind':outcome_kind.value,'candidate':manifest_candidate_ref,'source':disposition.disposition_id}
            outcome_ref=stable_record_id('slice40h_msm_non_selection_outcome', body)
            outcome=NonSelectionOutcomeRecord(
                record_id=outcome_ref,
                lineage_id=manifest.lineage_root.lineage_id,
                outcome_kind=outcome_kind,
                candidate_refs=(manifest_candidate_ref,),
                reasons=tuple(disposition.reason_refs) or (disposition.disposition_kind.value,),
                required_clarifications=(),
                external_authority_refs=(),
            )
            outcomes.append(outcome)
            trace_id=stable_record_id('slice40h_msm_transition_trace', {'from':manifest_candidate_ref,'to':outcome_ref,'source':disposition.disposition_id})
            traces.append(SemanticTransitionTraceRecord(
                record_id=trace_id, lineage_id=manifest.lineage_root.lineage_id,
                from_record_ref=manifest_candidate_ref, to_record_ref=outcome_ref,
                from_state=SemanticLifecycleState.CANDIDATE_MEANING,
                to_state=outcome.lifecycle_state,
                transition_kind=SemanticTransitionKind.CONTAINMENT,
                reason=f'slice40h projection from {disposition.disposition_kind.value}',
                authority_reference_ref=None,
            ))
        projection=with_id(GateDispositionProjectionRecord(
            projection_id='', source_disposition_id=disposition.disposition_id,
            source_disposition_kind=disposition.disposition_kind.value,
            projection_disposition=projection_kind,
            msm_outcome_record_ref=outcome_ref,
            companion_only=outcome_kind is None,
            selected_meaning_created=False,
        ), 'slice40h_gate_projection', 'projection_id')
        projections.append(projection)

    successor_id=stable_record_id('meaning_structure_manifest_slice40h_successor', {
        'source_manifest_id':manifest.manifest_id,
        'composition_result_id':composition.result_id,
        'outcome_ids':tuple(x.record_id for x in outcomes),
        'trace_ids':tuple(x.record_id for x in traces),
    })
    successor=replace(manifest, manifest_id=successor_id,
        non_selection_outcomes=manifest.non_selection_outcomes+tuple(outcomes),
        semantic_transition_traces=manifest.semantic_transition_traces+tuple(traces))
    if not validate_manifest(successor).ok: raise ValueError('projected MSM successor invalid')
    custody=tuple(_family(f,v) for f,v in zip(GateFamilyName,family))
    companion=with_id(MsmGateCustodyCompanionV1(
        companion_id='', companion_version='v1.0.0', source_manifest_id=manifest.manifest_id,
        successor_manifest_id=successor_id, lineage_id=manifest.lineage_root.lineage_id,
        manifest_candidate_ref=manifest_candidate_ref, candidate_input_ref=composition.candidate_input_ref,
        candidate_branch_ref=composition.candidate_branch_ref, family_custody=custody,
        composition_result_id=composition.result_id, composition_result_digest=composition.canonical_digest,
        composition_status=composition.composition_status.value,
        composition_disposition_refs=tuple(x.disposition_id for x in composition.dispositions),
        projections=tuple(projections), family_results_preserved=True,
        composition_result_preserved=True, candidate_side_only=True, non_selection_only=True,
        exact_adapter=True, lossless_custody=True,
        clarification_relevant_not_required=True,
        positive_selection_review_companion_only=True,
        refusal_relevant_not_outward_refusal=True,
        selected_meaning_created=False,
    ), 'slice40h_msm_gate_custody_companion', 'companion_id')
    result=with_id(MsmGateIntegrationResult(
        result_id='', source_manifest_id=manifest.manifest_id, successor_manifest_id=successor_id,
        manifest_candidate_ref=manifest_candidate_ref, successor_manifest=successor, companion=companion,
        projected_outcome_count=len(outcomes), companion_only_count=sum(x.companion_only for x in projections),
        deterministic=True, additive_only=True, existing_msm_schema_modified=False,
        automatic_migration_performed=False, gate_results_preserved=True,
        selected_meaning_created=False, truth_determined=False, evidence_validated=False,
        permission_granted=False, execution_authorized=False, route_created=False,
        tool_invoked=False, action_performed=False, memory_accessed=False,
        memory_written=False, rendered=False, delivered=False,
    ), 'slice40h_msm_gate_integration_result', 'result_id')
    if not validate_result(result).ok: raise ValueError('Slice 40H result self-validation failed')
    return result
