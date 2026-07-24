"""Bridge 5 internal deterministic gate and eligibility builders.

The builders use only accepted Slice 40/41 record types. They intentionally
supply absent authority observations where no accepted lexicon or operator
authority exists. That produces an indeterminate eligibility result rather
than manufacturing support, choosing a candidate, or constructing selected
meaning.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any


def _flatten(values):
    result = []
    for value in values:
        for item in tuple(value or ()):
            text = str(item)
            if text and text not in result:
                result.append(text)
    return tuple(result)


def _make_gate_bundle(core, module, family, refs):
    profile = module.with_expected_id(
        core.VerbalCognitionGateProfileIdentity(
            profile_id="gate_profile:placeholder",
            profile_key=f"{family.value}_default_profile",
            profile_version="v1.0.0",
            gate_family=family,
            governing_authority_refs=(
                "canonical_roadmap:slice40b",
                "document6:verbal_cognition_gate_engine:v1",
            ),
            required_schema_refs=(
                "slice39g:manifest_candidate_integration:v1",
                core.SCHEMA_VERSION,
            ),
            exact_profile_only=True,
        )
    )
    identity = module.with_expected_id(
        core.VerbalCognitionGateIdentity(
            gate_id="gate:placeholder",
            gate_key=f"{family.value}_gate",
            gate_version="v1.0.0",
            gate_family=family,
            gate_profile_ref=profile.profile_id,
        )
    )
    candidate = module.with_expected_id(
        core.GateCandidateInputReference(
            candidate_input_ref_id="gate_candidate_input:placeholder",
            candidate_meaning_id=refs["candidate_meaning_id"],
            candidate_state_id=refs["candidate_state_id"],
            candidate_lineage_id=refs["candidate_lineage_id"],
            candidate_identity_ref=refs["candidate_identity_ref"],
            candidate_content_ref=refs["candidate_content_ref"],
            candidate_provenance_ref=refs["candidate_provenance_ref"],
            construction_receipt_ref=refs["construction_receipt_ref"],
            manifest_candidate_record_ref=refs["manifest_candidate_record_ref"],
            manifest_companion_ref=refs["manifest_companion_ref"],
            construction_trace_ref=refs["construction_trace_ref"],
            limitation_reference_ref=refs["limitation_reference_ref"],
            alternative_relationship_refs=refs["alternative_relationship_refs"],
        )
    )
    requirement = module.with_expected_id(
        core.GateRequirementReference(
            requirement_reference_id="gate_requirement:placeholder",
            gate_family=family,
            requirement_key=f"{family.value}_requirement",
            requirement_version="v1.0.0",
            candidate_input_ref=candidate.candidate_input_ref_id,
            subject_record_refs=(refs["manifest_candidate_record_ref"], candidate.candidate_meaning_id),
            required_authority_refs=(
                "document6:verbal_cognition_gate_engine:v1",
            ),
            required_record_refs=(refs["manifest_candidate_record_ref"], refs["manifest_companion_ref"]),
            required_relation_refs=refs["relation_refs"],
            limitation_refs=refs["limitation_refs"],
        )
    )
    reason = module.with_expected_id(
        core.GateReasonGround(
            reason_ground_id="gate_reason:placeholder",
            gate_family=family,
            reason_key=f"{family.value}_validation_ground",
            candidate_input_ref=candidate.candidate_input_ref_id,
            requirement_reference_ids=(requirement.requirement_reference_id,),
            supporting_record_refs=(refs["manifest_candidate_record_ref"], refs["manifest_companion_ref"]),
            conflicting_record_refs=(),
            missing_record_refs=(),
            unknown_record_refs=(),
            authority_refs=(
                "document6:verbal_cognition_gate_engine:v1",
            ),
            limitation_refs=refs["limitation_refs"],
        )
    )
    trace = module.with_expected_id(
        core.GateTraceReference(
            trace_reference_id="gate_trace:placeholder",
            candidate_input_ref=candidate.candidate_input_ref_id,
            source_span_refs=refs["source_span_refs"],
            candidate_trace_refs=refs["candidate_trace_refs"],
            construction_trace_refs=(refs["construction_trace_ref"],),
            structural_trace_refs=(
                *refs["structural_trace_refs"],
                f"bridge5_gate_family_trace:{family.value}",
            ),
            concept_sense_trace_refs=refs["concept_sense_trace_refs"],
            predicate_role_frame_trace_refs=refs["predicate_role_frame_trace_refs"],
            alternative_relationship_refs=candidate.alternative_relationship_refs,
            predecessor_receipt_refs=(refs["construction_receipt_ref"],),
        )
    )
    provenance = module.with_expected_id(
        core.GateProvenanceReference(
            provenance_reference_id="gate_provenance:placeholder",
            candidate_input_ref=candidate.candidate_input_ref_id,
            source_event_id=refs["source_event_id"],
            source_sha256=refs["source_sha256"],
            candidate_provenance_ref=candidate.candidate_provenance_ref,
            gate_profile_ref=profile.profile_id,
            governing_document_refs=(
                "canonical_roadmap:slice40b",
                "document6:verbal_cognition_gate_engine:v1",
            ),
            authority_version_refs=(
                ("canonical_roadmap", "2026-07-12"),
                ("document6", "v1"),
            ),
            schema_version_refs=(
                ("slice39g", "v1"),
                ("slice40a", "v1"),
            ),
            external_resource_refs=(),
        )
    )
    limitation = module.with_expected_id(
        core.GateLimitationReference(
            limitation_reference_id="gate_limitation:placeholder",
            candidate_input_ref=candidate.candidate_input_ref_id,
            limitation_key="bridge5_candidate_specific_gate_evaluation_boundary",
            reason_refs=("bridge5_gate_evaluation_authorized_only_with_explicit_nomination",),
            affected_requirement_refs=(requirement.requirement_reference_id,),
            later_authority_refs=(f"slice40_{family.value}_runtime", "slice40g_gate_composition", "slice41c_eligibility"),
        )
    )
    review = module.with_expected_id(
        core.VerbalCognitionGateReviewRecord(
            review_record_id="gate_review:placeholder",
            identity=identity,
            profile=profile,
            candidate_input=candidate,
            requirement_references=(requirement,),
            reason_grounds=(reason,),
            evaluation_state=core.GateEvaluationState.NOT_EVALUATED,
            trace_references=(trace,),
            provenance_reference=provenance,
            limitation_references=(limitation,),
        )
    )
    custody = module.with_expected_id(
        module.GateVersionCustody(
            custody_id="gate_version_custody:placeholder",
            review_record_id=review.review_record_id,
            gate_id=identity.gate_id,
            gate_version=identity.gate_version,
            gate_profile_id=profile.profile_id,
            gate_profile_version=profile.profile_version,
            gate_family=family,
            core_schema_version=core.SCHEMA_VERSION,
            core_spec_version=core.SPEC_VERSION,
            identity_schema_id=core.GATE_IDENTITY_SCHEMA_ID,
            profile_schema_id=core.GATE_PROFILE_SCHEMA_ID,
            candidate_input_schema_id=core.CANDIDATE_INPUT_REFERENCE_SCHEMA_ID,
            requirement_schema_id=core.REQUIREMENT_REFERENCE_SCHEMA_ID,
            reason_ground_schema_id=core.REASON_GROUND_SCHEMA_ID,
            trace_schema_id=core.TRACE_REFERENCE_SCHEMA_ID,
            provenance_schema_id=core.PROVENANCE_REFERENCE_SCHEMA_ID,
            limitation_schema_id=core.LIMITATION_REFERENCE_SCHEMA_ID,
            review_record_schema_id=core.REVIEW_RECORD_SCHEMA_ID,
            governing_authority_versions=(
                ("canonical_roadmap", "2026-07-12"),
                ("document6", "v1"),
            ),
            predecessor_schema_versions=(
                (core.GATE_IDENTITY_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.GATE_PROFILE_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.CANDIDATE_INPUT_REFERENCE_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.REQUIREMENT_REFERENCE_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.REASON_GROUND_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.TRACE_REFERENCE_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.PROVENANCE_REFERENCE_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.LIMITATION_REFERENCE_SCHEMA_ID, core.SCHEMA_VERSION),
                (core.REVIEW_RECORD_SCHEMA_ID, core.SCHEMA_VERSION),
            ),
            canonical_field_order_version=module.CANONICAL_FIELD_ORDER_VERSION,
            digest_algorithm=module.DIGEST_ALGORITHM,
            non_llm_provenance=True,
            timestamps_in_identity=False,
            randomness_in_identity=False,
            process_identity_in_identity=False,
            filesystem_state_in_identity=False,
            environment_state_in_identity=False,
            hash_table_order_in_identity=False,
            runtime_evaluator_authorized=False,
            gate_evaluation_authorized=False,
            gate_outcome_authorized=False,
            selected_meaning_authorized=False,
            route_authorized=False,
            tool_authorized=False,
            action_authorized=False,
            memory_authorized=False,
            rendering_authorized=False,
            delivery_authorized=False,
        )
    )

    stages = (
        module.GateLifecycleStage.SCHEMA_DECLARED,
        module.GateLifecycleStage.PROFILE_VERSION_BOUND,
        module.GateLifecycleStage.CANDIDATE_REFERENCE_BOUND,
        module.GateLifecycleStage.PROVENANCE_VALIDATED,
        module.GateLifecycleStage.RECORD_VALIDATED,
        module.GateLifecycleStage.RECORD_SEALED,
    )
    lifecycle_records = []
    predecessor = ()
    for stage in stages:
        item = module.with_expected_id(
            module.GateLifecycleRecord(
                lifecycle_record_id="gate_lifecycle:placeholder",
                review_record_id=review.review_record_id,
                gate_id=identity.gate_id,
                gate_profile_id=profile.profile_id,
                candidate_input_ref=candidate.candidate_input_ref_id,
                provenance_reference_id=provenance.provenance_reference_id,
                stage=stage,
                version_custody_ref=custody.custody_id,
                predecessor_lifecycle_record_ids=predecessor,
                reason_refs=(f"lifecycle_reason:{stage.value}",),
                automatic_progression=False,
                validation_performed=stage in (
                    module.GateLifecycleStage.RECORD_VALIDATED,
                    module.GateLifecycleStage.RECORD_SEALED,
                ),
                provenance_validation_performed=stage in (
                    module.GateLifecycleStage.PROVENANCE_VALIDATED,
                    module.GateLifecycleStage.RECORD_VALIDATED,
                    module.GateLifecycleStage.RECORD_SEALED,
                ),
                gate_evaluation_created=False,
                gate_outcome_created=False,
                candidate_disposition_created=False,
                selected_meaning_created=False,
                truth_determined=False,
                evidence_validated=False,
                permission_granted=False,
                execution_authorized=False,
                route_created=False,
                tool_invoked=False,
                action_performed=False,
                memory_accessed=False,
                rendered=False,
                delivered=False,
                external_resource_loaded=False,
            )
        )
        lifecycle_records.append(item)
        predecessor = (item.lifecycle_record_id,)

    kinds = (
        module.GateLifecycleTransitionKind.BIND_PROFILE_VERSION,
        module.GateLifecycleTransitionKind.BIND_CANDIDATE_REFERENCE,
        module.GateLifecycleTransitionKind.VALIDATE_PROVENANCE,
        module.GateLifecycleTransitionKind.VALIDATE_RECORD,
        module.GateLifecycleTransitionKind.SEAL_RECORD,
    )
    lifecycle_transitions = []
    predecessor_transitions = ()
    for source, target, kind in zip(
        lifecycle_records,
        lifecycle_records[1:],
        kinds,
    ):
        item = module.with_expected_id(
            module.GateLifecycleTransitionRecord(
                transition_id="gate_lifecycle_transition:placeholder",
                review_record_id=review.review_record_id,
                source_lifecycle_record_id=source.lifecycle_record_id,
                target_lifecycle_record_id=target.lifecycle_record_id,
                from_stage=source.stage,
                to_stage=target.stage,
                transition_kind=kind,
                version_custody_ref=custody.custody_id,
                reason_refs=(f"transition_reason:{kind.value}",),
                predecessor_transition_refs=predecessor_transitions,
                automatic_transition=False,
                gate_evaluation_created=False,
                gate_outcome_created=False,
                candidate_disposition_created=False,
                selected_meaning_created=False,
                permission_granted=False,
                execution_authorized=False,
                route_created=False,
                tool_invoked=False,
                action_performed=False,
                memory_accessed=False,
                rendered=False,
                delivered=False,
            )
        )
        lifecycle_transitions.append(item)
        predecessor_transitions = (item.transition_id,)

    bundle = module.GateGovernanceBundle(
        bundle_id="gate_governance_bundle:placeholder",
        review_record=review,
        version_custody=custody,
        lifecycle_records=tuple(lifecycle_records),
        lifecycle_transitions=tuple(lifecycle_transitions),
        canonical_digest="0" * 64,
        validation_complete=True,
        provenance_validation_complete=True,
        schema_versions_known=True,
        gate_profile_version_known=True,
        runtime_evaluator_installed=False,
        gate_evaluation_performed=False,
        gate_outcome_created=False,
        candidate_disposition_created=False,
        selected_meaning_created=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_accessed=False,
        rendered=False,
        delivered=False,
        external_resource_loaded=False,
    )
    return module.with_expected_id(bundle)


def _expectancy_profile(core, module, bundle):
    return module.with_expected_profile_id(
        module.ExpectancyGateRuntimeProfile(
            profile_id="expectancy_profile:placeholder",
            profile_key="expectancy_exact_admitted_frame_requirements",
            profile_version="v1.0.0",
            gate_profile_ref=bundle.review_record.profile.profile_id,
            gate_profile_version=bundle.review_record.profile.profile_version,
            governing_authority_refs=(
                "canonical_roadmap:slice40c",
                "document6:expectancy_gate:v1",
            ),
            permitted_requirement_kinds=tuple(module.ExpectancyRequirementKind),
            exact_admitted_requirements_only=True,
            raw_text_inspection_allowed=False,
            hidden_context_allowed=False,
            default_participant_inference_allowed=False,
            unstated_referent_inference_allowed=False,
            automatic_clarification_allowed=False,
            gate_composition_allowed=False,
            selected_meaning_allowed=False,
            route_tool_action_allowed=False,
        )
    )


def _expectancy_requirement(module, bundle, kind, key, *, required=True, minimum_count=1):
    return module.with_expected_requirement_id(
        module.ExpectancyRequirement(
            requirement_id="expectancy_requirement:placeholder",
            candidate_input_ref=bundle.review_record.candidate_input.candidate_input_ref_id,
            predicate_id="predicate:inspect:v1",
            predicate_version="v1.0.0",
            frame_id="predicate_frame:inspect_target:v1",
            frame_version="v1.0.0",
            requirement_key=key,
            requirement_kind=kind,
            requirement_source_refs=(
                "slice38e:predicate_frame:inspect_target:v1",
                f"slice40c:requirement:{key}",
            ),
            authority_refs=(
                "document5:predicate_role_frame_registry:v1",
                "document6:expectancy_gate:v1",
            ),
            subject_record_refs=(f"candidate_subject:{key}",),
            relation_refs=(f"candidate_relation:{key}",),
            minimum_count=minimum_count,
            required=required,
            exact_admitted_requirement=True,
        )
    )


def _expectancy_observation(module, bundle, requirement, *, state=None, count=1):
    authority_state = state or module.ExpectancyAuthorityState.ADMITTED
    records = tuple(
        f"observed_record:{requirement.requirement_key}:{index}"
        for index in range(count)
    ) if authority_state is module.ExpectancyAuthorityState.ADMITTED else ()
    return module.with_expected_observation_id(
        module.ExpectancyObservation(
            observation_id="expectancy_observation:placeholder",
            requirement_ref=requirement.requirement_id,
            candidate_input_ref=bundle.review_record.candidate_input.candidate_input_ref_id,
            authority_state=authority_state,
            observed_record_refs=records,
            observed_relation_refs=(),
            trace_refs=(f"expectancy_trace:{requirement.requirement_key}",),
            provenance_refs=(f"expectancy_provenance:{requirement.requirement_key}",),
        )
    )


def _expectancy_input(module, bundle, requirements, observations):
    return module.with_expected_evaluation_input_id(
        module.ExpectancyEvaluationInput(
            evaluation_input_id="expectancy_evaluation_input:placeholder",
            governance_bundle=bundle,
            runtime_profile=_expectancy_profile(None, module, bundle),
            candidate_input_ref=bundle.review_record.candidate_input.candidate_input_ref_id,
            predicate_id="predicate:inspect:v1",
            predicate_version="v1.0.0",
            frame_id="predicate_frame:inspect_target:v1",
            frame_version="v1.0.0",
            requirements=tuple(requirements),
            observations=tuple(observations),
            trace_refs=("slice39h:candidate_trace", "slice40b:sealed_governance_trace"),
            provenance_refs=("slice39h:candidate_provenance", "slice40b:governance_provenance"),
            limitation_refs=("slice40c:no_clarification_no_selection",),
            raw_text_supplied=False,
            hidden_context_used=False,
            defaults_used=False,
            inferred_participants_created=False,
            inferred_referents_created=False,
        )
    )


def _congruity_profile(module,bundle):
    return module.with_expected_profile_id(module.CongruityGateRuntimeProfile(
        profile_id="congruity_profile:placeholder", profile_key="congruity_exact_admitted_compatibility",
        profile_version="v1.0.0", gate_profile_ref=bundle.review_record.profile.profile_id,
        gate_profile_version=bundle.review_record.profile.profile_version,
        governing_authority_refs=("canonical_roadmap:slice40d","document6:congruity_gate:v1","document4:concept_lexicon:v1","document5:predicate_role_frame_registry:v1"),
        permitted_assertion_kinds=tuple(module.CongruityAssertionKind), exact_admitted_assertions_only=True,
        raw_text_inspection_allowed=False, similarity_fallback_allowed=False, nearest_known_substitution_allowed=False,
        hidden_model_judgment_allowed=False, silent_repair_allowed=False, frame_rewrite_allowed=False,
        role_reassignment_allowed=False, capability_driven_selection_allowed=False, gate_composition_allowed=False,
        selected_meaning_allowed=False, route_tool_action_allowed=False))


def _congruity_assertion(module,bundle,kind,key):
    return module.with_expected_assertion_id(module.CongruityAssertion(
        assertion_id="congruity_assertion:placeholder",
        candidate_input_ref=bundle.review_record.candidate_input.candidate_input_ref_id,
        predicate_id="predicate:inspect:v1", predicate_version="v1.0.0",
        frame_id="predicate_frame:inspect_target:v1", frame_version="v1.0.0",
        assertion_key=key, assertion_kind=kind,
        subject_refs=(f"candidate_subject:{key}",), object_refs=(f"candidate_object:{key}",),
        relation_refs=(f"candidate_relation:{key}",),
        assertion_source_refs=(f"slice38:compatibility:{key}",f"document6:congruity:{key}"),
        authority_refs=("document4:concept_authority:v1","document5:predicate_role_authority:v1"),
        required=True, exact_admitted_assertion=True))


def _congruity_observation(module,bundle,assertion,*,authority=None,judgment=None):
    authority=authority or module.CongruityAuthorityState.ADMITTED
    if judgment is None:
        judgment=(module.CongruityCompatibilityJudgment.COMPATIBLE if authority is module.CongruityAuthorityState.ADMITTED else module.CongruityCompatibilityJudgment.NOT_EVALUATED)
    return module.with_expected_observation_id(module.CongruityObservation(
        observation_id="congruity_observation:placeholder", assertion_ref=assertion.assertion_id,
        candidate_input_ref=bundle.review_record.candidate_input.candidate_input_ref_id,
        authority_state=authority, compatibility_judgment=judgment,
        supporting_refs=((f"support:{assertion.assertion_key}",) if judgment is module.CongruityCompatibilityJudgment.COMPATIBLE else ()),
        conflict_refs=((f"conflict:{assertion.assertion_key}",) if judgment is module.CongruityCompatibilityJudgment.INCOMPATIBLE or authority is module.CongruityAuthorityState.CONFLICTED else ()),
        trace_refs=(f"congruity_trace:{assertion.assertion_key}",),
        provenance_refs=(f"congruity_provenance:{assertion.assertion_key}",)))


def _congruity_input(module,bundle,assertions,observations,**changes):
    value=module.CongruityEvaluationInput(
        evaluation_input_id="congruity_evaluation_input:placeholder", governance_bundle=bundle,
        runtime_profile=_congruity_profile(module,bundle), candidate_input_ref=bundle.review_record.candidate_input.candidate_input_ref_id,
        predicate_id="predicate:inspect:v1", predicate_version="v1.0.0", frame_id="predicate_frame:inspect_target:v1", frame_version="v1.0.0",
        assertions=tuple(assertions), observations=tuple(observations),
        trace_refs=("slice39h:candidate_trace","slice40b:sealed_governance_trace","slice40c:expectancy_trace"),
        provenance_refs=("slice39h:candidate_provenance","slice40b:governance_provenance"),
        limitation_refs=("slice40d:no_composition_no_selection",),
        raw_text_supplied=False, similarity_fallback_used=False, nearest_known_substitution_used=False,
        hidden_model_judgment_used=False, silent_repair_used=False, frame_rewritten=False,
        role_reassigned=False, capability_driven_selection_used=False)
    if changes: value=replace(value,**changes)
    return module.with_expected_evaluation_input_id(value)


def _connectedness_profile(module, bundle):
    return module.with_expected_profile_id(
        module.ConnectednessGateRuntimeProfile(
            profile_id="connectedness_profile:placeholder",
            profile_key="connectedness_exact_admitted_links",
            profile_version="v1.0.0",
            gate_profile_ref=bundle.review_record.profile.profile_id,
            gate_profile_version=bundle.review_record.profile.profile_version,
            governing_authority_refs=(
                "canonical_roadmap:slice40e",
                "document6:connectedness_gate:v1",
                "slice36:source_structural_trace:v1",
                "slice39:candidate_lineage:v1",
            ),
            permitted_assertion_kinds=tuple(module.ConnectednessAssertionKind),
            exact_admitted_connections_only=True,
            cooccurrence_connection_allowed=False,
            same_expression_connection_allowed=False,
            same_manifest_connection_allowed=False,
            implicit_transitivity_allowed=False,
            source_gap_bridge_allowed=False,
            ancestry_gap_bridge_allowed=False,
            scope_rewrite_allowed=False,
            attachment_reassignment_allowed=False,
            operator_trail_rewrite_allowed=False,
            predicate_frame_rewire_allowed=False,
            candidate_lineage_merge_allowed=False,
            raw_text_inspection_allowed=False,
            similarity_fallback_allowed=False,
            hidden_model_judgment_allowed=False,
            gate_composition_allowed=False,
            selected_meaning_allowed=False,
            route_tool_action_allowed=False,
        )
    )


def _connectedness_assertion(module, bundle, kind, key, *, left=None, right=None):
    return module.with_expected_assertion_id(
        module.ConnectednessAssertion(
            assertion_id="connectedness_assertion:placeholder",
            candidate_input_ref=(
                bundle.review_record.candidate_input.candidate_input_ref_id
            ),
            predicate_id="predicate:inspect:v1",
            predicate_version="v1.0.0",
            frame_id="predicate_frame:inspect_target:v1",
            frame_version="v1.0.0",
            assertion_key=key,
            assertion_kind=kind,
            left_record_ref=left or f"candidate_record:left:{key}",
            right_record_ref=right or f"candidate_record:right:{key}",
            connection_basis_refs=(
                f"connection_basis:{kind.value}:{key}",
                f"connection_trace:{kind.value}:{key}",
            ),
            assertion_source_refs=(
                f"slice36:structural_source:{key}",
                f"slice39:candidate_lineage:{key}",
                f"document6:connectedness:{key}",
            ),
            authority_refs=(
                "document6:connectedness_authority:v1",
                f"accepted_authority:{kind.value}:v1",
            ),
            exact_admitted_connection=True,
            same_expression_only=False,
            same_manifest_only=False,
            implicit_transitive_only=False,
        )
    )


def _connectedness_observation(
    module,
    bundle,
    assertion,
    *,
    authority=None,
    judgment=None,
):
    authority = authority or module.ConnectednessAuthorityState.ADMITTED
    if judgment is None:
        judgment = (
            module.ConnectednessJudgment.CONNECTED
            if authority is module.ConnectednessAuthorityState.ADMITTED
            else module.ConnectednessJudgment.NOT_EVALUATED
        )
    return module.with_expected_observation_id(
        module.ConnectednessObservation(
            observation_id="connectedness_observation:placeholder",
            assertion_ref=assertion.assertion_id,
            candidate_input_ref=(
                bundle.review_record.candidate_input.candidate_input_ref_id
            ),
            authority_state=authority,
            connection_judgment=judgment,
            supporting_refs=(
                (f"support:{assertion.assertion_key}",)
                if judgment is module.ConnectednessJudgment.CONNECTED
                else ()
            ),
            disconnection_refs=(
                (f"disconnect:{assertion.assertion_key}",)
                if judgment is module.ConnectednessJudgment.DISCONNECTED
                or authority is module.ConnectednessAuthorityState.CONFLICTED
                else ()
            ),
            trace_refs=(f"connectedness_trace:{assertion.assertion_key}",),
            provenance_refs=(
                f"connectedness_provenance:{assertion.assertion_key}",
            ),
        )
    )


def _connectedness_input(module, bundle, assertions, observations, **changes):
    value = module.ConnectednessEvaluationInput(
        evaluation_input_id="connectedness_evaluation_input:placeholder",
        governance_bundle=bundle,
        runtime_profile=_connectedness_profile(module, bundle),
        candidate_input_ref=(
            bundle.review_record.candidate_input.candidate_input_ref_id
        ),
        predicate_id="predicate:inspect:v1",
        predicate_version="v1.0.0",
        frame_id="predicate_frame:inspect_target:v1",
        frame_version="v1.0.0",
        assertions=tuple(assertions),
        observations=tuple(observations),
        trace_refs=(
            "slice36:source_field_trace",
            "slice39h:candidate_trace",
            "slice40b:sealed_governance_trace",
            "slice40d:congruity_trace",
        ),
        provenance_refs=(
            "slice39h:candidate_provenance",
            "slice40b:governance_provenance",
            "slice40d:congruity_provenance",
        ),
        limitation_refs=(
            "slice40e:no_cooccurrence_no_transitive_invention",
            "slice40e:no_composition_no_selection",
        ),
        raw_text_supplied=False,
        cooccurrence_only_connection_used=False,
        same_expression_only_connection_used=False,
        same_manifest_only_connection_used=False,
        implicit_transitive_connection_used=False,
        source_gap_bridged=False,
        ancestry_gap_bridged=False,
        scope_rewritten=False,
        attachment_reassigned=False,
        operator_trail_rewritten=False,
        predicate_frame_rewired=False,
        candidate_lineage_merged=False,
        similarity_fallback_used=False,
        hidden_model_judgment_used=False,
    )
    if changes:
        value = replace(value, **changes)
    return module.with_expected_evaluation_input_id(value)


def _purpose_profile(module, bundle):
    return module.with_expected_profile_id(
        module.RecoverablePurposeGateRuntimeProfile(
            profile_id="recoverable_purpose_profile:placeholder",
            profile_key="exact_intended_purport_authority",
            profile_version="v1.0.0",
            gate_profile_ref=bundle.review_record.profile.profile_id,
            gate_profile_version=bundle.review_record.profile.profile_version,
            governing_authority_refs=(
                "canonical_roadmap:slice40f",
                "document6:recoverable_purpose:v1",
                "document9:crosswalk_a010:v1",
                "slice39d:candidate_communicative_purpose:v1",
            ),
            permitted_distinction_kinds=tuple(
                module.PurportDistinctionKind
            ),
            exact_candidate_records_required=True,
            approved_discourse_ancestry_only=True,
            authorized_reference_state_only=True,
            exact_active_context_only=True,
            hidden_intent_inference_allowed=False,
            capability_existence_inference_allowed=False,
            prior_conversation_habit_allowed=False,
            assistant_intuition_allowed=False,
            psychological_inference_allowed=False,
            emotional_interpretation_allowed=False,
            raw_text_only_inference_allowed=False,
            purpose_conflation_allowed=False,
            automatic_purpose_collapse_allowed=False,
            gate_composition_allowed=False,
            selected_meaning_allowed=False,
            route_tool_action_allowed=False,
        )
    )


def _purpose_assertion(module, bundle, kind, represented, conflated):
    key = kind.value
    return module.with_expected_assertion_id(
        module.RecoverablePurposeAssertion(
            assertion_id="recoverable_purpose_assertion:placeholder",
            candidate_input_ref=(
                bundle.review_record.candidate_input.candidate_input_ref_id
            ),
            predicate_id="predicate:inspect:v1",
            predicate_version="v1.0.0",
            frame_id="predicate_frame:inspect_target:v1",
            frame_version="v1.0.0",
            assertion_key=key,
            distinction_kind=kind,
            represented_act=represented,
            prohibited_conflation_act=conflated,
            candidate_record_refs=(
                f"candidate_purpose:{key}",
                f"candidate_requested_act:{key}",
            ),
            purpose_support_refs=(
                f"purpose_support:{key}",
                f"candidate_structure:{key}",
            ),
            discourse_ancestry_refs=(
                f"discourse_ancestry:{key}",
            ),
            authorized_reference_state_refs=(
                f"authorized_reference_state:{key}",
            ),
            active_context_refs=(
                f"active_context:{key}",
            ),
            authority_refs=(
                "document6:recoverable_purpose_authority:v1",
                f"accepted_purpose_authority:{key}:v1",
            ),
            exact_candidate_records=True,
            discourse_ancestry_authorized=True,
            reference_state_authorized=True,
            active_context_authorized=True,
            explicit_purpose_only=True,
        )
    )


def _purpose_observation(
    module,
    bundle,
    assertion,
    *,
    authority=None,
    judgment=None,
):
    authority = authority or module.RecoverablePurposeAuthorityState.ADMITTED
    if judgment is None:
        judgment = (
            module.RecoverablePurposeJudgment.RECOVERABLE
            if authority is module.RecoverablePurposeAuthorityState.ADMITTED
            else module.RecoverablePurposeJudgment.NOT_EVALUATED
        )
    return module.with_expected_observation_id(
        module.RecoverablePurposeObservation(
            observation_id="recoverable_purpose_observation:placeholder",
            assertion_ref=assertion.assertion_id,
            candidate_input_ref=(
                bundle.review_record.candidate_input.candidate_input_ref_id
            ),
            authority_state=authority,
            purpose_judgment=judgment,
            supporting_refs=(
                (f"support:{assertion.assertion_key}",)
                if judgment
                is module.RecoverablePurposeJudgment.RECOVERABLE
                else ()
            ),
            missing_authority_refs=(
                (f"missing_authority:{assertion.assertion_key}",)
                if authority
                is module.RecoverablePurposeAuthorityState.ABSENT
                or judgment
                is module.RecoverablePurposeJudgment.UNRECOVERABLE
                else ()
            ),
            conflicting_refs=(
                (f"conflict:{assertion.assertion_key}",)
                if authority
                in (
                    module.RecoverablePurposeAuthorityState.CONFLICTED,
                    module.RecoverablePurposeAuthorityState.AMBIGUOUS,
                )
                else ()
            ),
            trace_refs=(
                f"recoverable_purpose_trace:{assertion.assertion_key}",
            ),
            provenance_refs=(
                f"recoverable_purpose_provenance:{assertion.assertion_key}",
            ),
        )
    )


def _purpose_input(module, bundle, assertions, observations, **changes):
    candidate_refs = tuple(
        ref
        for assertion in assertions
        for ref in assertion.candidate_record_refs
    )
    ancestry_refs = tuple(
        ref
        for assertion in assertions
        for ref in assertion.discourse_ancestry_refs
    )
    reference_refs = tuple(
        ref
        for assertion in assertions
        for ref in assertion.authorized_reference_state_refs
    )
    context_refs = tuple(
        ref
        for assertion in assertions
        for ref in assertion.active_context_refs
    )
    value = module.RecoverablePurposeEvaluationInput(
        evaluation_input_id=(
            "recoverable_purpose_evaluation_input:placeholder"
        ),
        governance_bundle=bundle,
        runtime_profile=_purpose_profile(module, bundle),
        candidate_input_ref=(
            bundle.review_record.candidate_input.candidate_input_ref_id
        ),
        predicate_id="predicate:inspect:v1",
        predicate_version="v1.0.0",
        frame_id="predicate_frame:inspect_target:v1",
        frame_version="v1.0.0",
        assertions=tuple(assertions),
        observations=tuple(observations),
        candidate_record_refs=candidate_refs,
        discourse_ancestry_refs=ancestry_refs,
        authorized_reference_state_refs=reference_refs,
        active_context_refs=context_refs,
        trace_refs=(
            "slice39d:candidate_purpose_trace",
            "slice39h:candidate_lineage_trace",
            "slice40b:sealed_governance_trace",
        ),
        provenance_refs=(
            "slice39h:candidate_provenance",
            "slice40b:governance_provenance",
        ),
        limitation_refs=(
            "slice40f:no_hidden_intent",
            "slice40f:no_purpose_conflation",
            "slice40f:no_composition_no_selection",
        ),
        raw_text_supplied=False,
        hidden_intent_inference_used=False,
        capability_existence_inference_used=False,
        prior_conversation_habit_used=False,
        assistant_intuition_used=False,
        psychological_inference_used=False,
        emotional_interpretation_used=False,
        raw_text_only_inference_used=False,
        purpose_conflation_used=False,
        automatic_purpose_collapse_used=False,
        unauthorized_context_used=False,
        candidate_structure_mutated=False,
    )
    if changes:
        value = replace(value, **changes)
    return module.with_expected_evaluation_input_id(value)


def _composition_profile(module):
    return module.with_expected_profile_id(
        module.GateCompositionRuntimeProfile(
            profile_id="gate_composition_profile:placeholder",
            profile_key="candidate_specific_preservation_composition",
            profile_version="v1.0.0",
            governing_authority_refs=(
                "canonical_roadmap:slice40g",
                "document6:section33:gate_composition",
                "document6:section31:non_selection",
                "slice40a:positive_selection_review_name_boundary",
            ),
            permitted_disposition_kinds=tuple(
                module.GateCompositionDispositionKind
            ),
            exact_family_results_required=True,
            preserve_all_gate_results=True,
            candidate_specific_composition_required=True,
            gate_substitution_allowed=False,
            gate_outcome_erasure_allowed=False,
            generic_flattening_allowed=False,
            global_pass_generalization_allowed=False,
            global_failure_generalization_allowed=False,
            candidate_branch_erasure_allowed=False,
            effect_boundary_rewrite_allowed=False,
            domain_marker_erasure_allowed=False,
            no_action_boundary_conversion_allowed=False,
            automatic_ambiguity_allowed=False,
            automatic_clarification_allowed=False,
            automatic_refusal_allowed=False,
            safest_candidate_selection_allowed=False,
            selected_meaning_allowed=False,
            downstream_authority_allowed=False,
        )
    )


def _composition_assertion(module, candidate_ref, branch_ref, result_refs, kind, *, authority=None, judgment=None):
    authority = authority or module.GateCompositionAuthorityState.ADMITTED
    judgment = judgment or (
        module.GateCompositionJudgment.APPLIES
        if authority is module.GateCompositionAuthorityState.ADMITTED
        else module.GateCompositionJudgment.NOT_EVALUATED
    )
    bases = {
        "ambiguity_refs": (),
        "clarification_refs": (),
        "unsupported_refs": (),
        "refusal_relevance_refs": (),
        "hold_refs": (),
        "blocked_progression_refs": (),
        "later_selection_review_refs": (),
    }
    field_map = {
        module.GateCompositionDispositionKind.MATERIAL_AMBIGUITY_PRESERVED: "ambiguity_refs",
        module.GateCompositionDispositionKind.CLARIFICATION_RELEVANT: "clarification_refs",
        module.GateCompositionDispositionKind.UNSUPPORTED: "unsupported_refs",
        module.GateCompositionDispositionKind.REFUSAL_RELEVANT: "refusal_relevance_refs",
        module.GateCompositionDispositionKind.HELD: "hold_refs",
        module.GateCompositionDispositionKind.BLOCKED_PROGRESSION: "blocked_progression_refs",
        module.GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW: "later_selection_review_refs",
    }
    if judgment is module.GateCompositionJudgment.APPLIES:
        bases[field_map[kind]] = (f"disposition_basis:{kind.value}",)
    if authority is module.GateCompositionAuthorityState.UNSUPPORTED:
        bases["unsupported_refs"] = ("unsupported_authority:composition",)
        kind = module.GateCompositionDispositionKind.UNSUPPORTED
    return module.with_expected_assertion_id(
        module.GateCompositionDispositionAssertion(
            assertion_id="gate_composition_assertion:placeholder",
            candidate_input_ref=candidate_ref,
            candidate_branch_ref=branch_ref,
            disposition_kind=kind,
            authority_state=authority,
            judgment=judgment,
            gate_result_refs=tuple(result_refs),
            supporting_refs=(f"composition_support:{kind.value}",),
            missing_authority_refs=(
                ("missing_authority:composition",)
                if authority is module.GateCompositionAuthorityState.ABSENT
                else ()
            ),
            conflicting_refs=(
                ("conflicting_authority:composition",)
                if authority in (
                    module.GateCompositionAuthorityState.AMBIGUOUS,
                    module.GateCompositionAuthorityState.CONFLICTED,
                )
                else ()
            ),
            ambiguity_refs=bases["ambiguity_refs"],
            clarification_refs=bases["clarification_refs"],
            unsupported_refs=bases["unsupported_refs"],
            refusal_relevance_refs=bases["refusal_relevance_refs"],
            hold_refs=bases["hold_refs"],
            blocked_progression_refs=bases["blocked_progression_refs"],
            later_selection_review_refs=bases["later_selection_review_refs"],
            later_authority_dependency_refs=(
                "later_authority:document7_or_10",
            ) if kind in (
                module.GateCompositionDispositionKind.HELD,
                module.GateCompositionDispositionKind.BLOCKED_PROGRESSION,
            ) else (),
            effect_boundary_refs=("effect_boundary:no_action",),
            domain_marker_refs=("domain_marker:software_sensitive",),
            no_action_boundary_refs=("boundary:no_action",),
            trace_refs=(f"composition_trace:{kind.value}",),
            provenance_refs=(f"composition_provenance:{kind.value}",),
            candidate_specific=True,
        )
    )


def _composition_input(module, bundles, results, assertions, **changes):
    candidate_ref = "candidate_composition:demo:v1"
    branch_ref = "candidate_branch:demo:primary"
    value = module.GateCompositionEvaluationInput(
        evaluation_input_id="gate_composition_evaluation_input:placeholder",
        governance_bundles=tuple(bundles),
        runtime_profile=_composition_profile(module),
        candidate_input_ref=candidate_ref,
        candidate_branch_ref=branch_ref,
        candidate_version="v1.0.0",
        expectancy_result=results[0],
        congruity_result=results[1],
        connectedness_result=results[2],
        recoverable_purpose_result=results[3],
        disposition_assertions=tuple(assertions),
        family_candidate_input_refs=tuple(item.candidate_input_ref for item in results),
        candidate_branch_refs=(branch_ref,),
        material_competing_candidate_refs=(),
        competing_candidate_disposition_refs=(),
        user_suppliable_clarification_refs=(),
        effect_boundary_refs=("effect_boundary:no_action",),
        domain_marker_refs=("domain_marker:software_sensitive",),
        no_action_boundary_refs=("boundary:no_action",),
        authority_boundary_refs=(
            "authority_boundary:meaning_not_action",
            "authority_boundary:gate_supported_not_selected",
        ),
        later_authority_dependency_refs=("later_authority:slice41_selected_meaning",),
        version_refs=(
            "version:expectancy:v1",
            "version:congruity:v1",
            "version:connectedness:v1",
            "version:recoverable_purpose:v1",
            "version:composition:v1",
        ),
        candidate_ancestry_refs=(
            "slice39:candidate_ancestry",
            "slice40c_to_40f:family_result_ancestry",
        ),
        trace_refs=("slice40g:composition_trace",),
        provenance_refs=("slice40g:composition_provenance",),
        limitation_refs=(
            "slice40g:non_selection_only",
            "slice40g:no_downstream_authority",
        ),
        raw_text_used_as_selected_meaning=False,
        gate_substitution_used=False,
        gate_outcome_erased=False,
        generic_flattening_used=False,
        global_pass_generalized=False,
        global_failure_generalized=False,
        candidate_branch_erased=False,
        effect_boundary_rewritten=False,
        domain_marker_erased=False,
        no_action_boundary_converted=False,
        automatic_ambiguity_used=False,
        automatic_clarification_used=False,
        automatic_refusal_used=False,
        safest_candidate_selected=False,
        candidate_structure_mutated=False,
    )
    if changes:
        value = replace(value, **changes)
    return module.with_expected_evaluation_input_id(value)


def _governance_bundle(
    core,
    governed,
    eligibility,
    custody,
    manifest_candidate,
    manifest_companion,
    gate_companion,
    composition_result,
    case_name: str,
    artifacts,
):
    candidate = governed.with_expected_id(core.SelectionCandidateCustodyRecord(
        selection_candidate_custody_id="placeholder",
        candidate_meaning_id=manifest_companion.candidate_meaning_id,
        candidate_state_id=manifest_companion.candidate_state_id,
        candidate_lineage_id=manifest_companion.candidate_lineage_id,
        source_expression_ref=manifest_candidate.source_expression_ref,
        manifest_candidate_record_ref=manifest_candidate.record_id,
        manifest_candidate_companion_ref=manifest_companion.companion_id,
        candidate_identity_ref=manifest_companion.candidate_identity_ref,
        candidate_content_ref=manifest_companion.candidate_content_ref,
        candidate_provenance_ref=manifest_companion.candidate_provenance_ref,
        candidate_construction_receipt_ref=manifest_companion.construction_receipt_ref,
        candidate_set_ref=artifacts["candidate_set_ref"],
        candidate_set_member_ref=artifacts["candidate_set_member_ref"],
        candidate_lifecycle_ref=artifacts["candidate_lifecycle_ref"],
        gate_candidate_input_ref=composition_result.candidate_input_ref,
        predecessor_receipt_refs=artifacts["predecessor_receipt_refs"],
    ))

    family_map = {item.family: item for item in gate_companion.family_custody}
    disposition_ids = tuple(
        item.disposition_id for item in composition_result.dispositions
    )
    gate = governed.with_expected_id(core.GateCustodyReferenceRecord(
        gate_custody_reference_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        msm_gate_custody_companion_ref=gate_companion.companion_id,
        expectancy_family_custody_ref=family_map[
            custody.GateFamilyName.EXPECTANCY
        ].custody_id,
        congruity_family_custody_ref=family_map[
            custody.GateFamilyName.CONGRUITY
        ].custody_id,
        connectedness_family_custody_ref=family_map[
            custody.GateFamilyName.CONNECTEDNESS
        ].custody_id,
        recoverable_purpose_family_custody_ref=family_map[
            custody.GateFamilyName.RECOVERABLE_PURPOSE
        ].custody_id,
        expectancy_result_ref=composition_result.expectancy_result_id,
        congruity_result_ref=composition_result.congruity_result_id,
        connectedness_result_ref=composition_result.connectedness_result_id,
        recoverable_purpose_result_ref=(
            composition_result.recoverable_purpose_result_id
        ),
        composition_result_ref=composition_result.result_id,
        composition_disposition_refs=disposition_ids,
        candidate_specific_disposition_refs=disposition_ids,
        gate_profile_refs=artifacts["gate_profile_refs"],
        gate_trace_refs=artifacts["gate_trace_refs"],
        gate_provenance_refs=artifacts["gate_provenance_refs"],
        gate_limitation_refs=artifacts["gate_limitation_refs"],
    ))

    material = case_name == "materially_unresolved"
    alternative = governed.with_expected_id(core.AlternativeCandidateCustodyRecord(
        alternative_candidate_custody_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        candidate_set_ref=candidate.candidate_set_ref,
        preserved_alternative_candidate_refs=artifacts["alternative_candidate_refs"],
        non_selected_candidate_refs=artifacts["alternative_candidate_refs"],
        alternative_relationship_refs=artifacts["alternative_relationship_refs"],
        alternative_disposition_refs=artifacts["alternative_disposition_refs"],
        material_ambiguity_refs=artifacts["material_ambiguity_refs"] if material else (),
        clarification_relevant_refs=(artifacts["clarification_relevant_refs"] if case_name == "clarification_dependent" else ()),
        shared_ancestry_refs=artifacts["shared_ancestry_refs"],
        exact_duplicate_group_refs=(),
    ))

    unresolved = governed.with_expected_id(core.UnresolvedStateCustodyRecord(
        unresolved_state_custody_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        unresolved_candidate_refs=(
            artifacts["alternative_candidate_refs"] if material else ()
        ),
        unknown_refs=artifacts["unknown_refs"],
        unsupported_refs=(
            artifacts["unsupported_refs"] if case_name == "unsupported" else ()
        ),
        conflicted_refs=(
            artifacts["conflicted_refs"] if case_name == "conflicted" else ()
        ),
        clarification_dependency_refs=(
            artifacts["clarification_dependency_refs"] if case_name == "clarification_dependent" else ()
        ),
        held_refs=(artifacts["held_refs"] if case_name == "held" else ()),
        blocked_progression_refs=(
            artifacts["blocked_progression_refs"] if case_name == "held" else ()
        ),
        refusal_relevant_refs=(
            artifacts["refusal_relevant_refs"] if case_name == "held" else ()
        ),
        missing_authority_refs=(
            artifacts["missing_authority_refs"] if case_name == "held" else artifacts["missing_authority_refs"]
        ),
        missing_structure_refs=artifacts["missing_structure_refs"],
        deferred_dependency_refs=(
            artifacts["deferred_dependency_refs"]
        ),
    ))

    limitation = governed.with_expected_id(core.InheritedLimitationCustodyRecord(
        inherited_limitation_custody_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        source_limitation_refs=artifacts["source_limitation_refs"],
        candidate_limitation_refs=artifacts["candidate_limitation_refs"],
        gate_limitation_refs=artifacts["gate_limitation_refs"],
        effect_boundary_refs=artifacts["effect_boundary_refs"],
        domain_sensitive_refs=(),
        authority_sensitive_distinction_refs=artifacts["authority_sensitive_distinction_refs"],
        evidence_boundary_refs=("evidence_not_validated",),
        memory_boundary_refs=("memory_not_accessed",),
        privacy_boundary_refs=(),
        delivery_boundary_refs=("delivery_not_authorized",),
        execution_boundary_refs=("execution_not_authorized",),
        correction_ancestry_refs=(),
        supersession_ancestry_refs=(),
    ))

    required_dispositions = tuple(
        item.disposition_kind.value for item in composition_result.dispositions
    ) or (composition_result.composition_status.value,)
    requirement = governed.with_expected_id(core.SelectionAuthorityRequirementRecord(
        selection_authority_requirement_id="placeholder",
        requirement_key="strict_candidate_specific_selection_eligibility",
        requirement_version="v1.0.0",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        gate_custody_reference_ref=gate.gate_custody_reference_id,
        governing_document_refs=(
            "canonical_roadmap:slice41c",
            "document6:selection_eligibility",
            "slice40g",
            "slice40h",
            "slice41a",
            "slice41b",
        ),
        required_authority_profile_refs=(
            eligibility.APPROVED_STRICT_PROFILE.profile_id,
        ),
        required_candidate_state_refs=(candidate.candidate_state_id,),
        required_gate_disposition_refs=required_dispositions,
        required_alternative_custody_refs=(
            alternative.alternative_candidate_custody_id,
        ),
        required_unresolved_custody_refs=(
            unresolved.unresolved_state_custody_id,
        ),
        required_limitation_custody_refs=(
            limitation.inherited_limitation_custody_id,
        ),
        required_predecessor_receipt_refs=artifacts["predecessor_receipt_refs"],
        deferred_authority_refs=("slice41d", "slice41e"),
    ))

    prior = governed.with_expected_id(core.SelectionEligibilityStatusRecord(
        selection_eligibility_status_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        gate_custody_reference_ref=gate.gate_custody_reference_id,
        selection_authority_requirement_refs=(
            requirement.selection_authority_requirement_id,
        ),
        alternative_candidate_custody_ref=(
            alternative.alternative_candidate_custody_id
        ),
        unresolved_state_custody_ref=unresolved.unresolved_state_custody_id,
        inherited_limitation_custody_ref=(
            limitation.inherited_limitation_custody_id
        ),
        custody_state=core.SelectionEligibilityCustodyState.READY_FOR_LATER_EVALUATION,
        status_reason_refs=("slice41c_evaluator_ready",),
        later_evaluator_ref="slice41c",
    ))
    decision = governed.with_expected_id(core.SelectedMeaningDecisionStatusRecord(
        selected_meaning_decision_status_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        selection_eligibility_status_ref=prior.selection_eligibility_status_id,
        custody_state=core.SelectedMeaningDecisionCustodyState.NOT_DECIDED,
        decision_reason_refs=("slice41d_deferred",),
        later_constructor_ref="slice41d",
    ))
    trace = governed.with_expected_id(core.SelectionTraceBoundaryRecord(
        selection_trace_boundary_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        gate_custody_reference_ref=gate.gate_custody_reference_id,
        selection_authority_requirement_refs=(
            requirement.selection_authority_requirement_id,
        ),
        alternative_candidate_custody_ref=(
            alternative.alternative_candidate_custody_id
        ),
        unresolved_state_custody_ref=unresolved.unresolved_state_custody_id,
        inherited_limitation_custody_ref=(
            limitation.inherited_limitation_custody_id
        ),
        selection_eligibility_status_ref=prior.selection_eligibility_status_id,
        selected_meaning_decision_status_ref=(
            decision.selected_meaning_decision_status_id
        ),
        source_trace_refs=artifacts["source_trace_refs"],
        candidate_trace_refs=artifacts["candidate_trace_refs"],
        gate_trace_refs=artifacts["gate_trace_refs"],
        composition_trace_refs=artifacts["composition_trace_refs"],
        predecessor_receipt_refs=artifacts["predecessor_receipt_refs"],
        authority_version_refs=(("slice41c_profile", "v1.0.0"),),
        schema_version_refs=(
            ("slice40h", gate_companion.schema_version),
            ("slice40g", composition_result.schema_version),
        ),
    ))
    receipt = governed.with_expected_id(core.SelectionReceiptBoundaryRecord(
        selection_receipt_boundary_id="placeholder",
        selection_candidate_custody_ref=candidate.selection_candidate_custody_id,
        selection_eligibility_status_ref=prior.selection_eligibility_status_id,
        selected_meaning_decision_status_ref=(
            decision.selected_meaning_decision_status_id
        ),
        selection_trace_boundary_ref=trace.selection_trace_boundary_id,
        required_law_refs=("eligibility_is_not_selection",),
        prohibited_consequence_refs=(
            "selected_meaning_creation",
            "msm_mutation",
            "permission",
            "execution",
        ),
        audit_note="Bridge 5 eligibility evaluation only; no Slice 41D construction.",
    ))
    runtime = governed.with_expected_id(core.SelectedMeaningRuntimeSchemaRecord(
        selected_meaning_runtime_schema_record_id="placeholder",
        selection_candidate_custody=candidate,
        gate_custody_reference=gate,
        selection_authority_requirements=(requirement,),
        alternative_candidate_custody=alternative,
        unresolved_state_custody=unresolved,
        inherited_limitation_custody=limitation,
        selection_eligibility_status=prior,
        selected_meaning_decision_status=decision,
        selection_trace_boundary=trace,
        selection_receipt_boundary=receipt,
    ))
    version = governed.with_expected_id(governed.SelectedMeaningVersionCustody(
        custody_id="placeholder",
        runtime_schema_record_id=runtime.selected_meaning_runtime_schema_record_id,
        runtime_schema_version=runtime.schema_version,
        runtime_schema_id=runtime.schema_id,
        runtime_spec_id=runtime.spec_id,
        runtime_spec_version=runtime.spec_version,
        record_schema_versions=governed.expected_record_schema_versions(runtime),
        predecessor_references=governed.expected_predecessor_references(runtime),
        accepted_parent_head=governed.SLICE41B_ACCEPTED_PARENT_HEAD,
        accepted_parent_tree=governed.SLICE41B_ACCEPTED_PARENT_TREE,
        accepted_parent_subject=governed.SLICE41B_ACCEPTED_PARENT_SUBJECT,
        canonical_field_order_version=governed.CANONICAL_FIELD_ORDER_VERSION,
        digest_algorithm=governed.DIGEST_ALGORITHM,
        non_llm_provenance=True,
        timestamps_in_identity=False,
        randomness_in_identity=False,
        process_identity_in_identity=False,
        filesystem_state_in_identity=False,
        environment_state_in_identity=False,
        hash_table_order_in_identity=False,
        eligibility_evaluation_authorized=False,
        candidate_ranking_authorized=False,
        selection_authorized=False,
        selected_meaning_construction_authorized=False,
        msm_v1_mutation_authorized=False,
        bootstrap_integration_authorized=False,
        truth_evidence_permission_execution_authorized=False,
        route_tool_action_memory_rendering_delivery_authorized=False,
    ))
    lifecycle = governed.with_expected_id(governed.SelectedMeaningLifecycleRecord(
        lifecycle_record_id="placeholder",
        runtime_schema_record_id=runtime.selected_meaning_runtime_schema_record_id,
        version_custody_ref=version.custody_id,
        stage=governed.SelectedMeaningLifecycleStage.RECORD_SEALED,
        predecessor_lifecycle_record_ids=(),
        predecessor_reference_ids=tuple(
            value for _, value in version.predecessor_references
        ),
        validation_issue_digest_refs=(),
        reason_refs=("slice41b_record_sealed",),
        automatic_progression=False,
        canonical_serialization_performed=True,
        deterministic_identity_validated=True,
        predecessor_references_validated=True,
        cross_record_consistency_validated=True,
        malformed_record_rejected=True,
        unknown_version_rejected=True,
        duplicate_record_rejected=True,
        identity_collision_rejected=True,
        eligibility_evaluated=False,
        gate_result_created=False,
        candidate_ranked=False,
        selection_performed=False,
        selected_meaning_created=False,
        msm_v1_modified=False,
        bootstrap_integration_enabled=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_written=False,
        rendered=False,
        delivered=False,
    ))
    return governed.with_expected_bundle_identity(governed.SelectedMeaningGovernanceBundle(
        bundle_id="placeholder",
        bundle_digest="0" * 64,
        runtime_schema_record=runtime,
        version_custody=version,
        lifecycle_record=lifecycle,
        lifecycle_transitions=(),
        validation_only=True,
        immutable_successor_records=True,
        exact_predecessor_references_required=True,
        duplicate_and_collision_rejection_required=True,
        unknown_version_rejection_required=True,
        eligibility_evaluated=False,
        gate_result_created=False,
        candidate_ranked=False,
        selection_performed=False,
        selected_meaning_created=False,
        msm_v1_modified=False,
        bootstrap_integration_enabled=False,
        truth_determined=False,
        evidence_validated=False,
        permission_granted=False,
        execution_authorized=False,
        route_created=False,
        tool_invoked=False,
        action_performed=False,
        memory_written=False,
        rendered=False,
        delivered=False,
    ))


def _evaluation_input(
    eligibility,
    bundle,
    manifest_candidate,
    manifest_companion,
    gate_companion,
    composition_result,
    case_name: str,
):
    value = eligibility.SelectionEligibilityEvaluationInput(
        evaluation_input_id="placeholder",
        governance_bundle=bundle,
        manifest_candidate_record=manifest_candidate,
        manifest_candidate_companion=manifest_companion,
        msm_gate_custody_companion=gate_companion,
        gate_composition_result=composition_result,
        authority_profile=eligibility.APPROVED_STRICT_PROFILE,
        candidate_dispositions=composition_result.dispositions,
        explicit_positive_support_refs=(
            tuple(
                disposition.disposition_id
                for disposition in composition_result.dispositions
                if disposition.disposition_kind.value
                == "candidate_supported_for_later_selection_review"
            )
            if case_name in {"eligible", "not_eligible"}
            else ()
        ),
        explicit_not_eligible_refs=(
            ("selection_authority:not_eligible",)
            if case_name == "not_eligible"
            else ()
        ),
        authority_profile_refs=(eligibility.APPROVED_STRICT_PROFILE.profile_id,),
        trace_refs=("slice41c:trace",),
        provenance_refs=("slice41c:provenance",),
        version_refs=("slice41c:v1",),
        candidate_ranking_used=False,
        confidence_scoring_used=False,
        probability_ranking_used=False,
        semantic_similarity_used=False,
        nearest_known_substitution_used=False,
        language_model_used=False,
        hidden_classifier_used=False,
        only_candidate_automatic_eligibility_used=False,
        first_candidate_automatic_eligibility_used=False,
        safest_candidate_automatic_eligibility_used=False,
        refusal_relevance_erased=False,
        blocked_progression_erased=False,
        unresolved_alternatives_erased=False,
        understood_meaning_converted_to_permission=False,
    )
    return eligibility.with_expected_evaluation_input_id(value)



def build_gate_and_eligibility(artifacts: dict[str, Any]) -> dict[str, Any]:
    from aiweb_language_core_bootstrap.verbal_cognition_gate_runtime import (
        VerbalCognitionGateFamily,
    )
    from aiweb_language_core_bootstrap.verbal_cognition_gate_runtime import (
        governed_lifecycle as gate_governed,
    )
    from aiweb_language_core_bootstrap.verbal_cognition_gate_runtime import (
        expectancy_gate,
        congruity_gate,
        connectedness_gate,
        recoverable_purpose_gate,
        gate_composition,
    )
    from aiweb_language_core_bootstrap import verbal_cognition_gate_runtime as gate_core
    from aiweb_language_core_bootstrap import msm_gate_custody
    from aiweb_language_core_bootstrap import selected_meaning_runtime as selected_core
    from aiweb_language_core_bootstrap.selected_meaning_runtime import (
        governed_lifecycle as selected_governed,
    )
    from aiweb_language_core_bootstrap.selected_meaning_runtime import (
        eligibility_evaluation,
    )

    companion = artifacts["manifest_companion"]
    manifest_candidate = artifacts["manifest_candidate"]
    constructed_record = artifacts["constructed_record"]
    state = constructed_record.candidate_meaning_state
    content = state.content
    predicate = artifacts["predicate_candidate"]
    layout = artifacts["role_layout_candidate"]
    all_candidate_ids = tuple(artifacts["all_candidate_ids"])
    alternative_candidate_refs = tuple(
        value for value in all_candidate_ids
        if value != companion.candidate_meaning_id
    )

    relation_refs = tuple(getattr(manifest_candidate, "relation_refs", ()) or ())
    if not relation_refs:
        relation_refs = (predicate.predicate_id,)

    source_span_refs = tuple(getattr(artifacts["slice38"], "source_span_ids", ()) or ())
    if not source_span_refs:
        source_span_refs = (manifest_candidate.source_expression_ref,)

    candidate_refs = {
        "candidate_meaning_id": companion.candidate_meaning_id,
        "candidate_state_id": companion.candidate_state_id,
        "candidate_lineage_id": companion.candidate_lineage_id,
        "candidate_identity_ref": companion.candidate_identity_ref,
        "candidate_content_ref": companion.candidate_content_ref,
        "candidate_provenance_ref": companion.candidate_provenance_ref,
        "construction_receipt_ref": companion.construction_receipt_ref,
        "manifest_candidate_record_ref": manifest_candidate.record_id,
        "manifest_companion_ref": companion.companion_id,
        "construction_trace_ref": companion.construction_trace_reference_id,
        "limitation_reference_ref": companion.limitation_reference_id,
        "alternative_relationship_refs": tuple(
            companion.alternative_relationship_ids
        ),
        "relation_refs": relation_refs,
        "limitation_refs": tuple(state.limitations) or (
            companion.limitation_reference_id,
        ),
        "source_span_refs": source_span_refs,
        "candidate_trace_refs": (
            constructed_record.record_id,
            state.state_id,
            companion.companion_id,
        ),
        "structural_trace_refs": (
            artifacts["structural"].result_id,
            artifacts["slice37"].result_id,
        ),
        "concept_sense_trace_refs": (
            artifacts["slice37"].result_id,
        ),
        "predicate_role_frame_trace_refs": (
            artifacts["slice38"].result_id,
            predicate.candidate_id,
            layout.candidate_id,
        ),
        "source_event_id": artifacts["custody"].event.input_event_id,
        "source_sha256": artifacts["custody"].observed_source_sha256,
    }

    bundles = (
        _make_gate_bundle(
            gate_core,
            gate_governed,
            VerbalCognitionGateFamily.EXPECTANCY,
            candidate_refs,
        ),
        _make_gate_bundle(
            gate_core,
            gate_governed,
            VerbalCognitionGateFamily.CONGRUITY,
            candidate_refs,
        ),
        _make_gate_bundle(
            gate_core,
            gate_governed,
            VerbalCognitionGateFamily.CONNECTEDNESS,
            candidate_refs,
        ),
        _make_gate_bundle(
            gate_core,
            gate_governed,
            VerbalCognitionGateFamily.RECOVERABLE_PURPOSE,
            candidate_refs,
        ),
    )

    requirement_source_refs = (
        layout.candidate_id,
        predicate.candidate_id,
        artifacts["slice38"].result_id,
        manifest_candidate.record_id,
    )
    authority_refs = (
        "document5:predicate_role_frame_registry:v1",
        "document6:verbal_cognition_gate_engine:v1",
    )

    expectancy_requirements = []
    expectancy_observations = []
    for kind in tuple(expectancy_gate.ExpectancyRequirementKind):
        requirement = _expectancy_requirement(
            expectancy_gate,
            bundles[0],
            kind,
            kind.value,
            required=(
                kind
                is not expectancy_gate.ExpectancyRequirementKind.OPTIONAL_DETAIL
            ),
        )
        requirement = expectancy_gate.with_expected_requirement_id(
            replace(
                requirement,
                predicate_id=predicate.predicate_id,
                predicate_version=predicate.predicate_version,
                frame_id=layout.frame_id,
                frame_version=layout.frame_version,
                requirement_source_refs=requirement_source_refs,
                authority_refs=authority_refs,
                subject_record_refs=(
                    manifest_candidate.record_id,
                    companion.candidate_meaning_id,
                ),
                relation_refs=relation_refs,
            )
        )
        observation = _expectancy_observation(
            expectancy_gate,
            bundles[0],
            requirement,
            state=expectancy_gate.ExpectancyAuthorityState.ABSENT,
            count=0,
        )
        expectancy_requirements.append(requirement)
        expectancy_observations.append(observation)

    expectancy_input = _expectancy_input(
        expectancy_gate,
        bundles[0],
        tuple(expectancy_requirements),
        tuple(expectancy_observations),
    )
    expectancy_input = expectancy_gate.with_expected_evaluation_input_id(
        replace(
            expectancy_input,
            predicate_id=predicate.predicate_id,
            predicate_version=predicate.predicate_version,
            frame_id=layout.frame_id,
            frame_version=layout.frame_version,
            requirements=tuple(expectancy_requirements),
            observations=tuple(expectancy_observations),
            trace_refs=(
                artifacts["structural"].result_id,
                artifacts["slice37"].result_id,
                artifacts["slice38"].result_id,
                constructed_record.record_id,
            ),
            provenance_refs=(
                companion.provenance_reference_id,
                companion.candidate_provenance_ref,
            ),
            limitation_refs=tuple(state.limitations) + (
                "bridge5:no_unadmitted_expectancy_authority",
            ),
        )
    )
    expectancy_result = expectancy_gate.evaluate_expectancy(expectancy_input)

    congruity_assertions = []
    congruity_observations = []
    for kind in tuple(congruity_gate.CongruityAssertionKind):
        assertion = _congruity_assertion(
            congruity_gate,
            bundles[1],
            kind,
            kind.value,
        )
        assertion = congruity_gate.with_expected_assertion_id(
            replace(
                assertion,
                predicate_id=predicate.predicate_id,
                predicate_version=predicate.predicate_version,
                frame_id=layout.frame_id,
                frame_version=layout.frame_version,
                subject_refs=(manifest_candidate.record_id,),
                object_refs=(companion.candidate_content_ref,),
                relation_refs=relation_refs,
                assertion_source_refs=requirement_source_refs,
                authority_refs=authority_refs,
            )
        )
        observation = _congruity_observation(
            congruity_gate,
            bundles[1],
            assertion,
            authority=congruity_gate.CongruityAuthorityState.ABSENT,
            judgment=congruity_gate.CongruityCompatibilityJudgment.NOT_EVALUATED,
        )
        congruity_assertions.append(assertion)
        congruity_observations.append(observation)

    congruity_input = _congruity_input(
        congruity_gate,
        bundles[1],
        tuple(congruity_assertions),
        tuple(congruity_observations),
    )
    congruity_input = congruity_gate.with_expected_evaluation_input_id(
        replace(
            congruity_input,
            predicate_id=predicate.predicate_id,
            predicate_version=predicate.predicate_version,
            frame_id=layout.frame_id,
            frame_version=layout.frame_version,
            assertions=tuple(congruity_assertions),
            observations=tuple(congruity_observations),
            trace_refs=(
                artifacts["slice38"].result_id,
                constructed_record.record_id,
            ),
            provenance_refs=(
                companion.provenance_reference_id,
                companion.candidate_provenance_ref,
            ),
            limitation_refs=tuple(state.limitations) + (
                "bridge5:no_unadmitted_congruity_authority",
            ),
        )
    )
    congruity_result = congruity_gate.evaluate_congruity(congruity_input)

    connectedness_assertions = []
    connectedness_observations = []
    for kind in tuple(connectedness_gate.ConnectednessAssertionKind):
        assertion = _connectedness_assertion(
            connectedness_gate,
            bundles[2],
            kind,
            kind.value,
        )
        assertion = connectedness_gate.with_expected_assertion_id(
            replace(
                assertion,
                predicate_id=predicate.predicate_id,
                predicate_version=predicate.predicate_version,
                frame_id=layout.frame_id,
                frame_version=layout.frame_version,
                left_record_ref=manifest_candidate.record_id,
                right_record_ref=companion.companion_id,
                connection_basis_refs=(
                    constructed_record.record_id,
                    companion.construction_trace_reference_id,
                    layout.candidate_id,
                ),
                assertion_source_refs=requirement_source_refs,
                authority_refs=authority_refs,
            )
        )
        observation = _connectedness_observation(
            connectedness_gate,
            bundles[2],
            assertion,
            authority=connectedness_gate.ConnectednessAuthorityState.ABSENT,
            judgment=connectedness_gate.ConnectednessJudgment.NOT_EVALUATED,
        )
        connectedness_assertions.append(assertion)
        connectedness_observations.append(observation)

    connectedness_input = _connectedness_input(
        connectedness_gate,
        bundles[2],
        tuple(connectedness_assertions),
        tuple(connectedness_observations),
    )
    connectedness_input = connectedness_gate.with_expected_evaluation_input_id(
        replace(
            connectedness_input,
            predicate_id=predicate.predicate_id,
            predicate_version=predicate.predicate_version,
            frame_id=layout.frame_id,
            frame_version=layout.frame_version,
            assertions=tuple(connectedness_assertions),
            observations=tuple(connectedness_observations),
            trace_refs=(
                artifacts["structural"].result_id,
                artifacts["slice37"].result_id,
                artifacts["slice38"].result_id,
                constructed_record.record_id,
            ),
            provenance_refs=(
                companion.provenance_reference_id,
                companion.candidate_provenance_ref,
            ),
            limitation_refs=tuple(state.limitations) + (
                "bridge5:no_unadmitted_connectedness_authority",
            ),
        )
    )
    connectedness_result = connectedness_gate.evaluate_connectedness(
        connectedness_input
    )

    purpose_assertions = []
    purpose_observations = []
    for kind in tuple(recoverable_purpose_gate.PurportDistinctionKind):
        represented, conflated = (
            recoverable_purpose_gate.PURPORT_DISTINCTION_PAIRS[kind]
        )
        assertion = _purpose_assertion(
            recoverable_purpose_gate,
            bundles[3],
            kind,
            represented,
            conflated,
        )
        assertion = recoverable_purpose_gate.with_expected_assertion_id(
            replace(
                assertion,
                predicate_id=predicate.predicate_id,
                predicate_version=predicate.predicate_version,
                frame_id=layout.frame_id,
                frame_version=layout.frame_version,
                candidate_record_refs=(
                    manifest_candidate.record_id,
                    companion.companion_id,
                    constructed_record.record_id,
                ),
                purpose_support_refs=(
                    content.communicative_act_candidate,
                ),
                discourse_ancestry_refs=(
                    artifacts["custody"].event.input_event_id,
                    artifacts["slice37"].result_id,
                    artifacts["slice38"].result_id,
                ),
                authorized_reference_state_refs=(),
                active_context_refs=(),
                authority_refs=authority_refs,
                discourse_ancestry_authorized=True,
                reference_state_authorized=False,
                active_context_authorized=False,
            )
        )
        observation = _purpose_observation(
            recoverable_purpose_gate,
            bundles[3],
            assertion,
            authority=(
                recoverable_purpose_gate.RecoverablePurposeAuthorityState.ABSENT
            ),
            judgment=(
                recoverable_purpose_gate.RecoverablePurposeJudgment.NOT_EVALUATED
            ),
        )
        purpose_assertions.append(assertion)
        purpose_observations.append(observation)

    purpose_input = _purpose_input(
        recoverable_purpose_gate,
        bundles[3],
        tuple(purpose_assertions),
        tuple(purpose_observations),
    )
    purpose_input = recoverable_purpose_gate.with_expected_evaluation_input_id(
        replace(
            purpose_input,
            predicate_id=predicate.predicate_id,
            predicate_version=predicate.predicate_version,
            frame_id=layout.frame_id,
            frame_version=layout.frame_version,
            assertions=tuple(purpose_assertions),
            observations=tuple(purpose_observations),
            candidate_record_refs=(
                manifest_candidate.record_id,
                companion.companion_id,
                constructed_record.record_id,
            ),
            discourse_ancestry_refs=(
                artifacts["custody"].event.input_event_id,
                artifacts["slice37"].result_id,
                artifacts["slice38"].result_id,
            ),
            authorized_reference_state_refs=(),
            active_context_refs=(),
            trace_refs=(
                artifacts["structural"].result_id,
                constructed_record.record_id,
            ),
            provenance_refs=(
                companion.provenance_reference_id,
                companion.candidate_provenance_ref,
            ),
            limitation_refs=tuple(state.limitations) + (
                "bridge5:no_unadmitted_purpose_authority",
            ),
        )
    )
    purpose_result = recoverable_purpose_gate.evaluate_recoverable_purpose(
        purpose_input
    )

    family_results = (
        expectancy_result,
        congruity_result,
        connectedness_result,
        purpose_result,
    )
    candidate_input_refs = tuple(
        value.candidate_input_ref for value in family_results
    )
    if len(set(candidate_input_refs)) != 1:
        raise ValueError(
            "candidate-specific family gate inputs did not preserve one exact reference"
        )

    candidate_input_ref = candidate_input_refs[0]
    candidate_branch_ref = companion.candidate_meaning_id
    result_refs = tuple(value.result_id for value in family_results)
    composition_assertion = _composition_assertion(
        gate_composition,
        candidate_input_ref,
        candidate_branch_ref,
        result_refs,
        gate_composition.GateCompositionDispositionKind.CANDIDATE_SUPPORTED_FOR_LATER_SELECTION_REVIEW,
        authority=gate_composition.GateCompositionAuthorityState.ABSENT,
        judgment=gate_composition.GateCompositionJudgment.NOT_EVALUATED,
    )
    composition_assertion = gate_composition.with_expected_assertion_id(
        replace(
            composition_assertion,
            supporting_refs=(),
            missing_authority_refs=(
                "bridge5:missing_admitted_gate_composition_authority",
            ),
            later_selection_review_refs=(),
            later_authority_dependency_refs=(
                "bridge5:accepted_lexicon_or_operator_authority_required",
                "slice41d:selected_meaning_construction_deferred",
            ),
            effect_boundary_refs=(
                layout.effect_boundary_id,
            ),
            domain_marker_refs=(
                predicate.action_root_id,
                predicate.predicate_id,
                layout.frame_id,
            ),
            trace_refs=(
                expectancy_result.result_id,
                congruity_result.result_id,
                connectedness_result.result_id,
                purpose_result.result_id,
            ),
            provenance_refs=(
                companion.provenance_reference_id,
            ),
        )
    )
    composition_input = _composition_input(
        gate_composition,
        bundles,
        family_results,
        (composition_assertion,),
        candidate_input_ref=candidate_input_ref,
        candidate_branch_ref=candidate_branch_ref,
        candidate_version=companion.companion_version,
        family_candidate_input_refs=candidate_input_refs,
        candidate_branch_refs=(candidate_branch_ref,),
        material_competing_candidate_refs=alternative_candidate_refs,
        competing_candidate_disposition_refs=tuple(
            companion.alternative_relationship_ids
        ),
        user_suppliable_clarification_refs=(),
        effect_boundary_refs=(layout.effect_boundary_id,),
        domain_marker_refs=(
            predicate.action_root_id,
            predicate.predicate_id,
            layout.frame_id,
        ),
        no_action_boundary_refs=(
            "bridge5:no_tool_route",
            "bridge5:no_action_execution",
        ),
        authority_boundary_refs=(
            "meaning_is_not_permission",
            "eligibility_is_not_selection",
            "echo_output_is_not_forge_authority",
        ),
        later_authority_dependency_refs=(
            "accepted_lexicon_or_operator_authority_required",
            "slice41d:selected_meaning_construction_deferred",
        ),
        version_refs=(
            predicate.predicate_version,
            layout.frame_version,
            expectancy_result.schema_version,
            congruity_result.schema_version,
            connectedness_result.schema_version,
            purpose_result.schema_version,
        ),
        candidate_ancestry_refs=(
            constructed_record.record_id,
            companion.companion_id,
            manifest_candidate.record_id,
        ),
        trace_refs=(
            artifacts["structural"].result_id,
            artifacts["slice37"].result_id,
            artifacts["slice38"].result_id,
        ),
        provenance_refs=(
            companion.provenance_reference_id,
        ),
        limitation_refs=tuple(state.limitations) + (
            "bridge5:composition_indeterminate_without_admitted_authority",
        ),
    )
    composition_result = gate_composition.evaluate_gate_composition(
        composition_input
    )

    gate_integration = msm_gate_custody.integrate_gate_results_into_manifest(
        artifacts["manifest"],
        manifest_candidate.record_id,
        expectancy_result,
        congruity_result,
        connectedness_result,
        purpose_result,
        composition_result,
    )

    finding_missing_authority = _flatten(
        getattr(finding, "missing_authority_refs", ())
        for result in family_results + (composition_result,)
        for finding in tuple(getattr(result, "findings", ()) or ())
    )
    selection_artifacts = {
        "candidate_set_ref": constructed_record.candidate_result_id,
        "candidate_set_member_ref": constructed_record.candidate_set_member.member_id,
        "candidate_lifecycle_ref": state.state_id,
        "predecessor_receipt_refs": (
            constructed_record.construction_receipt.receipt_id,
            gate_integration.result_id,
        ),
        "gate_profile_refs": tuple(
            bundle.review_record.profile.profile_id for bundle in bundles
        ) + (composition_input.runtime_profile.profile_id,),
        "gate_trace_refs": tuple(
            trace.trace_reference_id
            for bundle in bundles
            for trace in bundle.review_record.trace_references
        ) + (composition_result.result_id,),
        "gate_provenance_refs": tuple(
            bundle.review_record.provenance_reference.provenance_reference_id
            for bundle in bundles
        ),
        "gate_limitation_refs": tuple(
            limitation.limitation_reference_id
            for bundle in bundles
            for limitation in bundle.review_record.limitation_references
        ),
        "alternative_candidate_refs": alternative_candidate_refs,
        "alternative_relationship_refs": tuple(
            companion.alternative_relationship_ids
        ),
        "alternative_disposition_refs": tuple(
            item.disposition_id for item in composition_result.dispositions
        ),
        "material_ambiguity_refs": tuple(state.unresolved_alternative_refs),
        "clarification_relevant_refs": (),
        "shared_ancestry_refs": (
            constructed_record.record_id,
            artifacts["constructor_result"].result_id,
            artifacts["integration_result"].result_id,
        ),
        "unknown_refs": tuple(content.unknown_reason_refs),
        "unsupported_refs": tuple(content.unsupported_reason_refs),
        "conflicted_refs": tuple(state.conflicting_role_refs),
        "clarification_dependency_refs": (),
        "held_refs": (
            composition_result.result_id,
        ),
        "blocked_progression_refs": (
            "slice41d:selected_meaning_construction_deferred",
        ),
        "refusal_relevant_refs": (),
        "missing_authority_refs": finding_missing_authority or (
            "bridge5:missing_admitted_gate_authority",
        ),
        "missing_structure_refs": tuple(state.missing_role_refs),
        "deferred_dependency_refs": (
            "accepted_lexicon_or_operator_authority_required",
            "slice41d:selected_meaning_construction_deferred",
        ),
        "source_limitation_refs": tuple(content.limitations),
        "candidate_limitation_refs": tuple(state.limitations),
        "effect_boundary_refs": tuple(content.effect_boundary_refs) or (
            layout.effect_boundary_id,
        ),
        "authority_sensitive_distinction_refs": tuple(
            manifest_candidate.authority_sensitive_implications
        ),
        "source_trace_refs": (
            artifacts["custody"].event.input_event_id,
            artifacts["projection"].projection.projection_id,
        ),
        "candidate_trace_refs": (
            constructed_record.record_id,
            state.state_id,
            companion.companion_id,
        ),
        "composition_trace_refs": (
            composition_result.result_id,
        ),
    }
    governance_bundle = _governance_bundle(
        selected_core,
        selected_governed,
        eligibility_evaluation,
        msm_gate_custody,
        manifest_candidate,
        companion,
        gate_integration.companion,
        composition_result,
        "indeterminate",
        selection_artifacts,
    )
    evaluation_input = _evaluation_input(
        eligibility_evaluation,
        governance_bundle,
        manifest_candidate,
        companion,
        gate_integration.companion,
        composition_result,
        "indeterminate",
    )
    evaluation_input = eligibility_evaluation.with_expected_evaluation_input_id(
        replace(
            evaluation_input,
            trace_refs=(
                constructed_record.record_id,
                gate_integration.result_id,
                composition_result.result_id,
            ),
            provenance_refs=(
                companion.provenance_reference_id,
            ),
            version_refs=(
                predicate.predicate_version,
                layout.frame_version,
                gate_integration.companion.schema_version,
                composition_result.schema_version,
            ),
        )
    )
    eligibility_result = eligibility_evaluation.evaluate_selection_eligibility(
        evaluation_input
    )

    return {
        "gate_bundles": bundles,
        "expectancy_input": expectancy_input,
        "expectancy_result": expectancy_result,
        "congruity_input": congruity_input,
        "congruity_result": congruity_result,
        "connectedness_input": connectedness_input,
        "connectedness_result": connectedness_result,
        "purpose_input": purpose_input,
        "purpose_result": purpose_result,
        "composition_input": composition_input,
        "composition_result": composition_result,
        "gate_integration": gate_integration,
        "selection_governance_bundle": governance_bundle,
        "eligibility_input": evaluation_input,
        "eligibility_result": eligibility_result,
    }
