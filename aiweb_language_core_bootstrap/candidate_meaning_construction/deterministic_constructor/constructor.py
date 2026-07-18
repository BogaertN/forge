"""Explicit deterministic in-memory CandidateMeaning construction for Slice 39F."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace

from ..candidate_semantic_content import (
    CandidateSemanticContentStatus,
    assemble_candidate_semantic_content,
    validate_assembly_result,
)
from ..candidate_set_preservation import (
    CandidateSetStatus,
    preserve_candidate_set,
    validate_preservation_result,
)
from ..governed_lifecycle import (
    with_expected_candidate_identity,
    with_expected_state_id,
)
from ..governed_lifecycle.identity import (
    with_expected_alternative_reference_id,
    with_expected_construction_receipt_id,
)
from ..predecessor_custody import (
    PredecessorCustodyStatus,
    bind_complete_predecessor_custody,
    validate_binding_result,
)
from ..schema import (
    CandidateMeaningAlternativeReference,
    CandidateMeaningConstructionReceipt,
    CandidateMeaningConstructionStatus,
    CandidateMeaningIdentity,
    CandidateMeaningState,
)
from .authority import (
    SLICE39F_CANDIDATE_VERSION,
    SLICE39F_PROFILE_VERSION,
)
from .canonical import stable_identifier
from .identity import (
    expected_profile_id,
    with_expected_constructed_record_id,
    with_expected_result_identity,
)
from .schema import (
    CandidateMeaningConstructedRecord,
    CandidateMeaningConstructorInput,
    CandidateMeaningConstructorProfile,
    CandidateMeaningConstructorResult,
    CandidateMeaningConstructorStatus,
    CandidateMeaningConstructorValidationCode,
    CandidateMeaningConstructorValidationIssue,
)
from .validation import validate_result


def _default_profile() -> CandidateMeaningConstructorProfile:
    provisional = CandidateMeaningConstructorProfile(
        profile_id="pending",
        profile_key="deterministic_candidate_meaning_constructor",
        profile_version=SLICE39F_PROFILE_VERSION,
        explicitly_invoked=True,
        exact_input_types_required=True,
        offline_only=True,
        standard_library_only=True,
        read_only=True,
        deterministic=True,
        in_memory_only=True,
        source_preserving=True,
        fail_closed=True,
        raw_text_inspection_allowed=False,
        similarity_allowed=False,
        nearest_known_fallback_allowed=False,
        hidden_repair_allowed=False,
        ranking_allowed=False,
        selection_allowed=False,
        ambiguity_resolution_allowed=False,
        gate_outcome_allowed=False,
        manifest_integration_allowed=False,
        bootstrap_integration_allowed=False,
        truth_evidence_permission_allowed=False,
        route_action_memory_rendering_delivery_allowed=False,
    )
    return replace(provisional, profile_id=expected_profile_id(provisional))


DEFAULT_CONSTRUCTOR_PROFILE = _default_profile()


def _issue(path: str, code: CandidateMeaningConstructorValidationCode, detail: str) -> CandidateMeaningConstructorValidationIssue:
    return CandidateMeaningConstructorValidationIssue(path, code, detail)


def _empty_set_result():
    return preserve_candidate_set(())


def _base_result(
    *,
    status: CandidateMeaningConstructorStatus,
    reason_code: str,
    profile: CandidateMeaningConstructorProfile,
    candidate_set_result,
    constructed_records=(),
    issues=(),
    input_count=0,
    source_event_ids=(),
    source_sha256s=(),
    exact_input_types_verified=True,
    exact_ancestry_verified=True,
    exact_snapshots_verified=True,
    source_preserved=True,
) -> CandidateMeaningConstructorResult:
    unique_count = len(constructed_records)
    duplicate_count = candidate_set_result.exact_duplicate_occurrence_count
    receipts = tuple(item.construction_receipt for item in constructed_records)
    record = CandidateMeaningConstructorResult(
        result_id="pending",
        status=status,
        reason_code=reason_code,
        profile=profile,
        candidate_set_result=candidate_set_result,
        constructed_records=tuple(constructed_records),
        construction_receipts=receipts,
        issues=tuple(issues),
        input_count=input_count,
        unique_candidate_count=unique_count,
        exact_duplicate_occurrence_count=duplicate_count,
        source_event_ids=tuple(source_event_ids),
        source_sha256s=tuple(source_sha256s),
        explicitly_invoked=True,
        exact_input_types_verified=exact_input_types_verified,
        exact_ancestry_verified=exact_ancestry_verified,
        exact_snapshots_verified=exact_snapshots_verified,
        source_preserved=source_preserved,
        offline=True,
        standard_library_only=True,
        read_only=True,
        deterministic=True,
        in_memory_only=True,
        fail_closed=True,
        raw_text_inspected=False,
        similarity_used=False,
        nearest_known_fallback_used=False,
        hidden_repair_used=False,
        candidate_ranked=False,
        candidate_selected=False,
        ambiguity_resolved=False,
        gate_outcome_created=False,
        selected_meaning_created=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        route_created=False,
        action_performed=False,
        memory_accessed=False,
        rendered=False,
        delivered=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        external_resource_loaded=False,
        language_model_used=False,
        embedding_used=False,
        vector_used=False,
        rag_used=False,
        semantic_similarity_used=False,
        manifest_integrated=False,
        bootstrap_integrated=False,
        slice39_closeout_created=False,
        canonical_digest="pending",
    )
    return with_expected_result_identity(record)


def _rejected(issues, *, profile=DEFAULT_CONSTRUCTOR_PROFILE, input_count=0):
    result = _base_result(
        status=CandidateMeaningConstructorStatus.REJECTED,
        reason_code="candidate_meaning_construction_rejected",
        profile=profile,
        candidate_set_result=_empty_set_result(),
        issues=tuple(issues),
        input_count=input_count,
        exact_input_types_verified=False,
        exact_ancestry_verified=False,
        exact_snapshots_verified=False,
        source_preserved=False,
    )
    return result


def _construction_status(content) -> tuple[CandidateMeaningConstructionStatus, tuple[str, ...]]:
    if content.conflicting_role_refs:
        return CandidateMeaningConstructionStatus.CONSTRUCTION_CONFLICTED, tuple(sorted(content.conflicting_role_refs))
    if content.unsupported_reason_refs:
        return CandidateMeaningConstructionStatus.CONSTRUCTION_UNSUPPORTED, tuple(sorted(content.unsupported_reason_refs))
    if content.unknown_reason_refs:
        return CandidateMeaningConstructionStatus.CONSTRUCTION_UNKNOWN, tuple(sorted(content.unknown_reason_refs))
    incomplete = tuple(sorted(set(content.missing_role_refs + content.unresolved_referent_refs)))
    if incomplete:
        return CandidateMeaningConstructionStatus.CONSTRUCTION_INCOMPLETE, incomplete
    return CandidateMeaningConstructionStatus.CONSTRUCTED, ("candidate_construction_complete_without_gate_evaluation",)


def _candidate_identity(content, provenance, profile):
    provisional = CandidateMeaningIdentity(
        candidate_meaning_id="pending",
        candidate_key="pending",
        candidate_version=SLICE39F_CANDIDATE_VERSION,
        lineage_id="pending",
        construction_profile_id=profile.profile_id,
        construction_profile_version=profile.profile_version,
    )
    return with_expected_candidate_identity(provisional, content=content, provenance=provenance)


def _alternative_records(candidate_set, identities_by_result):
    by_result: dict[str, list[CandidateMeaningAlternativeReference]] = {key: [] for key in identities_by_result}
    for alternative in candidate_set.material_alternative_references:
        left_identity = identities_by_result[alternative.left_candidate_result_id]
        right_identity = identities_by_result[alternative.right_candidate_result_id]
        reasons = tuple(sorted(set(
            alternative.left_limitation_refs
            + alternative.right_limitation_refs
            + alternative.left_missing_role_refs
            + alternative.right_missing_role_refs
            + alternative.left_conflicting_role_refs
            + alternative.right_conflicting_role_refs
        ))) or ("slice40_material_ambiguity_evaluation_deferred",)
        for source_identity, target_identity, source_result in (
            (left_identity, right_identity, alternative.left_candidate_result_id),
            (right_identity, left_identity, alternative.right_candidate_result_id),
        ):
            provisional = CandidateMeaningAlternativeReference(
                alternative_reference_id="pending",
                source_candidate_meaning_id=source_identity.candidate_meaning_id,
                alternative_candidate_meaning_id=target_identity.candidate_meaning_id,
                alternative_kind="exact_material_alternative",
                shared_ancestry_refs=(alternative.shared_ancestry_ref,),
                differing_content_refs=alternative.exact_difference_dimensions,
                unresolved_reason_refs=reasons,
            )
            record = with_expected_alternative_reference_id(provisional)
            by_result[source_result].append(record)
    return {key: tuple(sorted(value, key=lambda item: item.alternative_reference_id)) for key, value in by_result.items()}


def construct_candidate_meanings(
    candidate_inputs: object,
    *,
    profile: object = DEFAULT_CONSTRUCTOR_PROFILE,
) -> CandidateMeaningConstructorResult:
    """Construct zero, one, or many candidate states from exact typed records."""

    issues: list[CandidateMeaningConstructorValidationIssue] = []
    if type(candidate_inputs) is not tuple:
        issues.append(_issue("candidate_inputs", CandidateMeaningConstructorValidationCode.TYPE_MISMATCH, "exact tuple required; raw text and arbitrary objects are rejected"))
    if type(profile) is not CandidateMeaningConstructorProfile or profile != DEFAULT_CONSTRUCTOR_PROFILE:
        issues.append(_issue("profile", CandidateMeaningConstructorValidationCode.PROFILE_MISMATCH, "exact canonical Slice 39F profile required"))
    if issues:
        return _rejected(issues, input_count=len(candidate_inputs) if type(candidate_inputs) is tuple else 0)
    assert type(candidate_inputs) is tuple and type(profile) is CandidateMeaningConstructorProfile
    if not candidate_inputs:
        result = _base_result(
            status=CandidateMeaningConstructorStatus.ZERO_CANDIDATES,
            reason_code="zero_candidate_inputs_preserved",
            profile=profile,
            candidate_set_result=_empty_set_result(),
            input_count=0,
        )
        return result

    assemblies = []
    source_event_ids: list[str] = []
    source_sha256s: list[str] = []
    for index, item in enumerate(candidate_inputs):
        path = f"candidate_inputs[{index}]"
        if type(item) is not CandidateMeaningConstructorInput:
            issues.append(_issue(path, CandidateMeaningConstructorValidationCode.TYPE_MISMATCH, "exact CandidateMeaningConstructorInput required"))
            continue
        binding = bind_complete_predecessor_custody(
            item.custody,
            item.projection,
            item.binding,
            item.trails,
            item.constraints,
            item.structural,
            item.slice37,
            item.slice38,
        )
        binding_report = validate_binding_result(binding)
        if not binding_report.ok:
            issues.append(_issue(path, CandidateMeaningConstructorValidationCode.PREDECESSOR_REJECTED, "Slice 39C exact predecessor custody rejected input"))
            continue
        source_event_ids.append(binding.source_event_id)
        source_sha256s.append(binding.source_sha256)
        assembly = assemble_candidate_semantic_content(
            binding,
            item.constraints,
            item.slice37,
            item.slice38,
            semantic_relation_references=item.semantic_relation_references,
        )
        assembly_report = validate_assembly_result(assembly)
        if not assembly_report.ok:
            issues.append(_issue(path, CandidateMeaningConstructorValidationCode.CONTENT_ASSEMBLY_REJECTED, "Slice 39D semantic-content assembly rejected input"))
            continue
        if binding.status is PredecessorCustodyStatus.NO_CANDIDATE_PREDECESSOR:
            if assembly.status is not CandidateSemanticContentStatus.NO_CANDIDATE_CONTENT or assembly.assembly is not None:
                issues.append(_issue(path, CandidateMeaningConstructorValidationCode.CONTENT_ASSEMBLY_REJECTED, "lawful no-candidate predecessor did not remain explicit"))
            continue
        if binding.status is not PredecessorCustodyStatus.BOUND or binding.custody is None:
            issues.append(_issue(path, CandidateMeaningConstructorValidationCode.PREDECESSOR_REJECTED, "Slice 39C predecessor status is not constructible"))
            continue
        if assembly.status is not CandidateSemanticContentStatus.ASSEMBLED or assembly.assembly is None:
            issues.append(_issue(path, CandidateMeaningConstructorValidationCode.CONTENT_ASSEMBLY_REJECTED, "Slice 39D semantic-content assembly did not produce candidate content"))
            continue
        assemblies.append(assembly)
    if issues:
        return _rejected(issues, input_count=len(candidate_inputs))
    if len(set(source_event_ids)) > 1 or len(set(source_sha256s)) > 1:
        return _rejected((_issue("candidate_inputs", CandidateMeaningConstructorValidationCode.SOURCE_MISMATCH, "all constructor inputs must share one exact source event and checksum"),), input_count=len(candidate_inputs))
    if not assemblies:
        return _base_result(
            status=CandidateMeaningConstructorStatus.ZERO_CANDIDATES,
            reason_code="typed_predecessors_produced_zero_candidates",
            profile=profile,
            candidate_set_result=_empty_set_result(),
            input_count=len(candidate_inputs),
            source_event_ids=tuple(sorted(set(source_event_ids))),
            source_sha256s=tuple(sorted(set(source_sha256s))),
        )

    candidate_set_result = preserve_candidate_set(tuple(assemblies))
    if not validate_preservation_result(candidate_set_result).ok or candidate_set_result.candidate_set is None or candidate_set_result.status is CandidateSetStatus.SET_REJECTED:
        return _rejected((_issue("candidate_set", CandidateMeaningConstructorValidationCode.CANDIDATE_SET_REJECTED, "Slice 39E candidate-set preservation rejected assembled candidates"),), input_count=len(candidate_inputs))
    candidate_set = candidate_set_result.candidate_set

    primary_members = tuple(item for item in candidate_set.members if item.duplicate_occurrence_index == 1)
    assembly_by_result = {item.result_id: item for item in assemblies}
    identities_by_result = {}
    for member in primary_members:
        assembly = assembly_by_result[member.candidate_result_id].assembly
        assert assembly is not None
        identities_by_result[member.candidate_result_id] = _candidate_identity(
            assembly.candidate_meaning_content,
            assembly.predecessor_custody.provenance,
            profile,
        )
    alternatives_by_result = _alternative_records(candidate_set, identities_by_result)
    occurrence_counts = Counter(item.candidate_result_id for item in candidate_set.members)

    constructed: list[CandidateMeaningConstructedRecord] = []
    for member in primary_members:
        assembly_result = assembly_by_result[member.candidate_result_id]
        assembly = assembly_result.assembly
        assert assembly is not None
        content = assembly.candidate_meaning_content
        provenance = assembly.predecessor_custody.provenance
        identity = identities_by_result[member.candidate_result_id]
        alternatives = alternatives_by_result[member.candidate_result_id]
        status, reasons = _construction_status(content)
        predecessor_ids = tuple(dict.fromkeys(
            assembly.predecessor_custody.predecessor_result_ids
            + tuple(item.receipt_id for item in assembly.predecessor_custody.stage_receipts)
            + (assembly_result.result_id, candidate_set_result.result_id, candidate_set.candidate_set_id, member.member_id)
        ))
        receipt = CandidateMeaningConstructionReceipt(
            receipt_id="pending",
            candidate_meaning_id=identity.candidate_meaning_id,
            identity_ref=identity.candidate_meaning_id,
            content_ref=content.content_id,
            provenance_ref=provenance.provenance_id,
            alternative_reference_ids=tuple(item.alternative_reference_id for item in alternatives),
            predecessor_record_ids=predecessor_ids,
            construction_profile_id=profile.profile_id,
            construction_profile_version=profile.profile_version,
            status=status,
            status_reason_refs=reasons,
            deterministic_construction_required=True,
            source_preservation_required=True,
            immutable_record_set_required=True,
        )
        receipt = with_expected_construction_receipt_id(receipt)
        state = CandidateMeaningState(
            state_id="pending",
            identity=identity,
            content=content,
            provenance=provenance,
            alternative_references=alternatives,
            construction_status=status,
            construction_receipt=receipt,
            status_reason_refs=reasons,
            unresolved_alternative_refs=tuple(item.alternative_reference_id for item in alternatives),
            missing_role_refs=content.missing_role_refs,
            conflicting_role_refs=content.conflicting_role_refs,
            limitations=content.limitations or ("candidate_only_no_gate_evaluation",),
        )
        state = with_expected_state_id(state)
        record = CandidateMeaningConstructedRecord(
            record_id="pending",
            candidate_result_id=member.candidate_result_id,
            predecessor_custody=assembly.predecessor_custody,
            semantic_content_assembly=assembly,
            candidate_set_member=member,
            candidate_meaning_state=state,
            construction_receipt=receipt,
            deterministic_position=member.deterministic_position,
            duplicate_occurrence_count=occurrence_counts[member.candidate_result_id],
            exact_typed_predecessors_verified=True,
            exact_ancestry_verified=True,
            exact_snapshots_verified=True,
            source_preserved=True,
        )
        constructed.append(with_expected_constructed_record_id(record))

    result = _base_result(
        status=CandidateMeaningConstructorStatus.CONSTRUCTED,
        reason_code="candidate_meaning_states_constructed",
        profile=profile,
        candidate_set_result=candidate_set_result,
        constructed_records=tuple(constructed),
        input_count=len(candidate_inputs),
        source_event_ids=tuple(sorted(set(source_event_ids))),
        source_sha256s=tuple(sorted(set(source_sha256s))),
    )
    report = validate_result(result)
    if not report.ok:
        return _rejected(report.issues, input_count=len(candidate_inputs))
    return result


__all__ = ("DEFAULT_CONSTRUCTOR_PROFILE", "construct_candidate_meanings")
