#!/usr/bin/env python3
"""Behavior tests for Slice 37D controlled sense and exact term mapping."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import importlib
import sys


REPOSITORY = Path(__file__).resolve().parents[1]
if str(REPOSITORY) not in sys.path:
    sys.path.insert(0, str(REPOSITORY))

PACKAGE_NAME = (
    "aiweb_language_core_bootstrap.controlled_concept_sense_registry."
    "sense_term_mapping_registry"
)
package = importlib.import_module(PACKAGE_NAME)
star_namespace: dict[str, object] = {}
exec(f"from {PACKAGE_NAME} import *", star_namespace, star_namespace)

from aiweb_language_core_bootstrap.controlled_concept_sense_registry import (
    CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES,
    ConceptLifecycleState,
    ControlledLexicalReference,
    ControlledSenseIdentity,
    LexicalReferenceKind,
    TermConceptMappingIdentity,
)
from aiweb_language_core_bootstrap.controlled_concept_sense_registry.built_in_registry import (
    BUILT_IN_REGISTRY,
    BUILT_IN_CONCEPT_KEYS,
)
from aiweb_language_core_bootstrap.controlled_concept_sense_registry.governed_lifecycle import (
    expected_resource_lineage_id,
    recompute_resource_id,
    resource_id,
    validate_governance_batch,
)
from aiweb_language_core_bootstrap.controlled_concept_sense_registry.sense_term_mapping_registry import (
    CURRENT_LEXICAL_REFERENCES,
    CURRENT_MAPPINGS,
    CURRENT_SENSES,
    GOVERNANCE_BATCH,
    LEXICAL_REFERENCE_DEFINITIONS,
    MAPPING_DEFINITIONS,
    OUTWARD_ELIGIBILITY_REFERENCES,
    OUTWARD_ELIGIBLE_LEXICAL_KEYS,
    PROHIBITED_EXPANSION_REFUSALS,
    SENSE_DEFINITIONS,
    SENSE_TERM_MAPPING_REGISTRY,
    SLICE37D_COMMON_PROHIBITED_USES,
    SLICE37D_DOMAIN_SCOPE,
    SLICE37D_EXPECTED_LEXICAL_REFERENCE_COUNT,
    SLICE37D_EXPECTED_MAPPING_COUNT,
    SLICE37D_EXPECTED_OUTWARD_ELIGIBILITY_COUNT,
    SLICE37D_EXPECTED_SENSE_COUNT,
    SLICE37D_NAMESPACE_SCOPE,
    SLICE37D_PROHIBITED_AUTHORITIES,
    SLICE37D_PROHIBITED_EXPANSION_KINDS,
    SLICE37D_REGISTRY_AUTHORITY_LIMITATIONS,
    SLICE37D_SOURCE_AUTHORITY_PACKET_SHA256,
    ExactTermLookupState,
    MappingMultiplicity,
    OutwardExpressionEligibilityState,
    ProhibitedExpansionKind,
    SenseTermMappingRegistry,
    SenseTermMappingValidationError,
    exact_term_lookup,
    lexical_reference_by_id,
    make_exact_lookup_request,
    mapping_by_id,
    prohibited_expansion_refusal,
    registry_manifest,
    sense_by_id,
    sense_term_mapping_registry,
    validate_expansion_refusal,
    validate_lookup_request,
    validate_lookup_result,
    validate_outward_eligibility_reference,
    validate_registry,
)
from aiweb_language_core_bootstrap.controlled_concept_sense_registry.sense_term_mapping_registry import records


checks: list[str] = []
failures: list[str] = []


def check(name: str, condition: bool) -> None:
    if condition:
        checks.append(name)
    else:
        failures.append(name)


def expect_exception(name: str, expected: type[BaseException], function) -> None:
    try:
        function()
    except expected:
        check(name, True)
    except BaseException:
        check(name, False)
    else:
        check(name, False)


registry = sense_term_mapping_registry()
manifest = registry_manifest()
namespace_id = registry.concept_registry.current_namespace.namespace_id

# Public import and singleton surface.
check("package_all_tuple", isinstance(package.__all__, tuple))
check("package_all_unique", len(package.__all__) == len(set(package.__all__)))
check("package_all_exists", all(hasattr(package, name) for name in package.__all__))
check("star_import_exact", all(star_namespace.get(name) is getattr(package, name) for name in package.__all__))
check("registry_singleton", registry is SENSE_TERM_MAPPING_REGISTRY)
check("registry_accessor_repeat", sense_term_mapping_registry() is registry)
check("manifest_singleton", registry_manifest() is manifest)
check("registry_exact_type", type(registry) is SenseTermMappingRegistry)
check("concept_registry_identity", registry.concept_registry is BUILT_IN_REGISTRY)
check("concept_keys_unchanged", tuple(item.concept_key for item in BUILT_IN_REGISTRY.admitted_concepts) == BUILT_IN_CONCEPT_KEYS)
check("slice37c_concept_count_preserved", len(BUILT_IN_REGISTRY.admitted_concepts) == 4)
check("slice37c_sense_refs_not_rewritten", all(item.sense_refs == () for item in BUILT_IN_REGISTRY.admitted_concepts))

# Manifest boundaries and exact counts.
check("manifest_id_exact", manifest.manifest_id == manifest.expected_id())
check("manifest_packet_hash", manifest.source_authority_packet_sha256 == SLICE37D_SOURCE_AUTHORITY_PACKET_SHA256)
check("manifest_read_only", manifest.read_only is True)
check("manifest_closed", manifest.closed_set is True)
check("manifest_human_approved", manifest.human_approved is True)
check("manifest_registry_population", manifest.registry_population_authorized is True)
check("manifest_sense_population", manifest.sense_population_authorized is True)
check("manifest_lexical_population", manifest.lexical_reference_population_authorized is True)
check("manifest_mapping_population", manifest.mapping_population_authorized is True)
check("manifest_outward_reference_population", manifest.outward_eligibility_reference_population_authorized is True)
check("manifest_exact_term_lookup", manifest.exact_term_lookup_allowed is True)
check("manifest_exact_reference_lookup", manifest.exact_reference_id_lookup_allowed is True)
check("manifest_exact_sense_lookup", manifest.exact_sense_id_lookup_allowed is True)
check("manifest_exact_mapping_lookup", manifest.exact_mapping_id_lookup_allowed is True)
check("manifest_limitations_exact", manifest.authority_limitations == SLICE37D_REGISTRY_AUTHORITY_LIMITATIONS)
check("manifest_sense_refs", manifest.sense_refs == tuple(item.sense_id for item in registry.senses))
check("manifest_lexical_refs", manifest.lexical_reference_refs == tuple(item.lexical_reference_id for item in registry.lexical_references))
check("manifest_mapping_refs", manifest.mapping_refs == tuple(item.mapping_id for item in registry.mappings))
check("manifest_eligibility_refs", manifest.outward_eligibility_refs == tuple(item.eligibility_id for item in registry.outward_eligibility_references))
check("manifest_refusal_refs", manifest.prohibited_expansion_refusal_refs == tuple(item.refusal_id for item in registry.prohibited_expansion_refusals))
check("expected_sense_count_constant", SLICE37D_EXPECTED_SENSE_COUNT == 5)
check("expected_lexical_count_constant", SLICE37D_EXPECTED_LEXICAL_REFERENCE_COUNT == 11)
check("expected_mapping_count_constant", SLICE37D_EXPECTED_MAPPING_COUNT == 10)
check("expected_eligibility_count_constant", SLICE37D_EXPECTED_OUTWARD_ELIGIBILITY_COUNT == 4)
check("sense_count", len(registry.senses) == 5)
check("lexical_count", len(registry.lexical_references) == 11)
check("mapping_count", len(registry.mappings) == 10)
check("eligibility_count", len(registry.outward_eligibility_references) == 4)
check("refusal_count", len(registry.prohibited_expansion_refusals) == 10)
check("sense_definition_count", len(SENSE_DEFINITIONS) == 5)
check("lexical_definition_count", len(LEXICAL_REFERENCE_DEFINITIONS) == 11)
check("mapping_definition_count", len(MAPPING_DEFINITIONS) == 10)
check("registry_digest_repeat", registry.registry_digest() == registry.registry_digest())
check("registry_digest_prefix", registry.registry_digest().startswith("slice37d_sense_term_mapping_registry:"))

# No later authority is installed.
for field_name in (
    "occurrence_interpretation_installed",
    "sense_selection_installed",
    "candidate_meaning_creation_installed",
    "structural_integration_installed",
    "case_fold_expansion_installed",
    "spelling_correction_installed",
    "stemming_installed",
    "synonym_expansion_installed",
    "nearest_match_installed",
    "frequency_ranking_installed",
    "semantic_similarity_installed",
    "embedding_installed",
    "model_inference_installed",
    "ordinary_dictionary_fallback_installed",
    "external_resource_loading_installed",
    "runtime_activation_installed",
    "route_registration_installed",
    "tool_activation_installed",
    "memory_access_installed",
    "action_execution_installed",
    "rendering_installed",
    "delivery_installed",
):
    check(f"manifest_{field_name}_false", getattr(manifest, field_name) is False)
check("classes_deferred", manifest.semantic_classes_deferred_to_slice37e is True)
check("relations_deferred", manifest.semantic_relations_deferred_to_slice37e is True)
check("structural_integration_deferred", manifest.structural_candidate_integration_deferred_to_slice37f is True)

# Full registry and inherited governance validation.
registry_report = validate_registry(registry)
governance_report = validate_governance_batch(GOVERNANCE_BATCH)
check("registry_validation_pass", registry_report.ok)
check("registry_validation_issues_empty", registry_report.issues == ())
check("governance_validation_pass", governance_report.ok)
check("governance_validation_issues_empty", governance_report.issues == ())
check("governance_resources", len(GOVERNANCE_BATCH.resources) == 93)
check("governance_authorities", len(GOVERNANCE_BATCH.authority_records) == 62)
check("governance_transitions", len(GOVERNANCE_BATCH.transitions) == 62)
check("governance_provenance", len(GOVERNANCE_BATCH.provenance_records) == 32)
check("new_resources", len(records.NEW_RESOURCES) == 78)
check("new_authorities", len(records.NEW_AUTHORITIES) == 52)
check("new_transitions", len(records.NEW_TRANSITIONS) == 52)
check("new_provenance", len(records.NEW_PROVENANCE_RECORDS) == 27)

# Exact lifecycle histories and inherited non-authority tuple.
for family_name, histories, expected_type, final_states in (
    (
        "lexical",
        records.LEXICAL_REFERENCE_HISTORIES,
        ControlledLexicalReference,
        {ConceptLifecycleState.ADMITTED},
    ),
    (
        "sense",
        records.SENSE_HISTORIES,
        ControlledSenseIdentity,
        {ConceptLifecycleState.ADMITTED},
    ),
    (
        "mapping",
        records.MAPPING_HISTORIES,
        TermConceptMappingIdentity,
        {
            ConceptLifecycleState.ADMITTED,
            ConceptLifecycleState.AMBIGUOUS,
            ConceptLifecycleState.UNSUPPORTED,
        },
    ),
):
    for index, history in enumerate(histories):
        prefix = f"{family_name}_{index}"
        check(prefix + "_history_length", len(history) == 3)
        check(prefix + "_types", all(type(item) is expected_type for item in history))
        check(prefix + "_versions", tuple(item.version for item in history) == ("v1", "v2", "v3"))
        check(prefix + "_first_state", history[0].lifecycle_state is ConceptLifecycleState.OBSERVED)
        check(prefix + "_second_state", history[1].lifecycle_state is ConceptLifecycleState.CANDIDATE)
        check(prefix + "_final_state", history[2].lifecycle_state in final_states)
        check(prefix + "_lineage_stable", len({expected_resource_lineage_id(item) for item in history}) == 1)
        check(prefix + "_ids_unique", len({recompute_resource_id(item) for item in history}) == 3)
        check(prefix + "_ids_recompute", all(recompute_resource_id(item) == resource_id(item) for item in history))
        check(prefix + "_authority_exact", all(item.prohibited_authorities == CONCEPT_RESOURCE_PROHIBITED_AUTHORITIES for item in history))

# Current sense identities remain distinct and inspectable.
expected_sense_keys = (
    "governed_semantic_resource_identity",
    "source_occurrence_form",
    "metalinguistic_expression_mention",
    "human_approved_semantic_admission_act",
    "missing_admitted_concept_support_condition",
)
check("sense_key_order", tuple(item.sense_key for item in CURRENT_SENSES) == expected_sense_keys)
check("sense_ids_unique", len({item.sense_id for item in CURRENT_SENSES}) == 5)
check("sense_definitions_nonempty", all(item.definition for item in CURRENT_SENSES))
check("sense_differentiation_nonempty", all(item.differentiation_basis for item in CURRENT_SENSES))
check("sense_lexical_refs_nonempty", all(item.lexical_reference_refs for item in CURRENT_SENSES))
check("sense_scope_nonempty", all(item.scope_tags for item in CURRENT_SENSES))
check("sense_permitted_nonempty", all(item.permitted_uses for item in CURRENT_SENSES))
check("sense_prohibited_uses_exact", all(item.prohibited_uses == SLICE37D_COMMON_PROHIBITED_USES for item in CURRENT_SENSES))
for index, sense in enumerate(CURRENT_SENSES):
    check(f"sense_{index}_lookup", sense_by_id(sense.sense_id) is sense)
    check(f"sense_{index}_id", sense.sense_id == recompute_resource_id(sense))
    check(f"sense_{index}_state", sense.lifecycle_state is ConceptLifecycleState.ADMITTED)
    check(f"sense_{index}_concept_exists", any(item.concept_id == sense.concept_id for item in BUILT_IN_REGISTRY.admitted_concepts))

# Exact lexical references: 4 outward, 4 internal, 3 domain; all case-sensitive.
check("lexical_ids_unique", len({item.lexical_reference_id for item in CURRENT_LEXICAL_REFERENCES}) == 11)
check("lexical_all_case_sensitive", all(item.case_sensitive is True for item in CURRENT_LEXICAL_REFERENCES))
check("lexical_outward_count", sum(item.reference_kind is LexicalReferenceKind.CONTROLLED_OUTWARD_EXPRESSION for item in CURRENT_LEXICAL_REFERENCES) == 4)
check("lexical_internal_count", sum(item.reference_kind is LexicalReferenceKind.CONTROLLED_INTERNAL_EXPRESSION for item in CURRENT_LEXICAL_REFERENCES) == 4)
check("lexical_domain_count", sum(item.reference_kind is LexicalReferenceKind.DOMAIN_TERM for item in CURRENT_LEXICAL_REFERENCES) == 3)
check("lexical_namespace_exact", all(item.namespace_id == namespace_id for item in CURRENT_LEXICAL_REFERENCES))
check("lexical_forms_unique", len({(item.exact_form, item.language_tag) for item in CURRENT_LEXICAL_REFERENCES}) == 11)
for index, lexical in enumerate(CURRENT_LEXICAL_REFERENCES):
    check(f"lexical_{index}_lookup", lexical_reference_by_id(lexical.lexical_reference_id) is lexical)
    check(f"lexical_{index}_id", lexical.lexical_reference_id == recompute_resource_id(lexical))
    check(f"lexical_{index}_state", lexical.lifecycle_state is ConceptLifecycleState.ADMITTED)

# Mapping states and candidate integrity.
check("mapping_ids_unique", len({item.mapping_id for item in CURRENT_MAPPINGS}) == 10)
check("mapping_admitted_count", sum(item.lifecycle_state is ConceptLifecycleState.ADMITTED for item in CURRENT_MAPPINGS) == 8)
check("mapping_ambiguous_count", sum(item.lifecycle_state is ConceptLifecycleState.AMBIGUOUS for item in CURRENT_MAPPINGS) == 1)
check("mapping_unsupported_count", sum(item.lifecycle_state is ConceptLifecycleState.UNSUPPORTED for item in CURRENT_MAPPINGS) == 1)
check("mapping_namespace_scope_exact", all(item.namespace_scope == SLICE37D_NAMESPACE_SCOPE for item in CURRENT_MAPPINGS))
check("mapping_domain_scope_exact", all(item.domain_scope == SLICE37D_DOMAIN_SCOPE for item in CURRENT_MAPPINGS))
check("mapping_no_occurrence_selection", all(item.occurrence_interpretation_selected is False for item in CURRENT_MAPPINGS))
check("mapping_no_selected_concept", all(item.selected_concept_ref is None for item in CURRENT_MAPPINGS))
check("mapping_no_selected_sense", all(item.selected_sense_ref is None for item in CURRENT_MAPPINGS))
for index, mapping in enumerate(CURRENT_MAPPINGS):
    check(f"mapping_{index}_lookup", mapping_by_id(mapping.mapping_id) is mapping)
    check(f"mapping_{index}_id", mapping.mapping_id == recompute_resource_id(mapping))
    check(f"mapping_{index}_lexical_exists", any(item.lexical_reference_id == mapping.lexical_reference_id for item in CURRENT_LEXICAL_REFERENCES))
    check(f"mapping_{index}_concepts_exist", all(any(concept.concept_id == ref for concept in BUILT_IN_REGISTRY.admitted_concepts) for ref in mapping.concept_candidate_refs))
    check(f"mapping_{index}_senses_exist", all(any(sense.sense_id == ref for sense in CURRENT_SENSES) for ref in mapping.sense_candidate_refs))

# Exact request helper.
def request(form: str, language: str = "en", *, ns_id: str = namespace_id,
            ns_scope: tuple[str, ...] = SLICE37D_NAMESPACE_SCOPE,
            domain: tuple[str, ...] = SLICE37D_DOMAIN_SCOPE):
    return make_exact_lookup_request(
        exact_form=form,
        language_tag=language,
        namespace_id=ns_id,
        namespace_scope=ns_scope,
        domain_scope=domain,
    )

# Eight one-to-one exact mappings.
one_to_one_cases = (
    ("Forge-Controlled Concept Identity", "en"),
    ("forge_controlled_concept_identity", "und-x-aiweb"),
    ("Source Expression Form", "en"),
    ("source_expression_form", "und-x-aiweb"),
    ("Concept Admission", "en"),
    ("concept_admission", "und-x-aiweb"),
    ("Unknown Concept Condition", "en"),
    ("unknown_concept_condition", "und-x-aiweb"),
)
for index, (form, language) in enumerate(one_to_one_cases):
    req = request(form, language)
    result = exact_term_lookup(req)
    prefix = f"one_to_one_{index}"
    check(prefix + "_request_valid", validate_lookup_request(req).ok)
    check(prefix + "_result_valid", validate_lookup_result(result).ok)
    check(prefix + "_state", result.state is ExactTermLookupState.MAPPED_ONE_TO_ONE)
    check(prefix + "_multiplicity", result.multiplicity is MappingMultiplicity.ONE_TO_ONE)
    check(prefix + "_lexical_count", len(result.lexical_reference_refs) == 1)
    check(prefix + "_mapping_count", len(result.mapping_refs) == 1)
    check(prefix + "_concept_count", len(result.concept_candidate_refs) == 1)
    check(prefix + "_sense_count", len(result.sense_candidate_refs) == 1)
    check(prefix + "_exact", result.exact_match is True)
    check(prefix + "_not_ranked", result.candidate_order_is_ranked is False)
    check(prefix + "_not_selected", result.occurrence_interpretation_selected is False)
    check(prefix + "_no_selected_refs", result.selected_concept_ref is None and result.selected_sense_ref is None)
    check(prefix + "_repeat", exact_term_lookup(req) == result)

# One-to-many ambiguous mapping preserves exact deterministic candidate order.
ambiguous_request = request("concept")
ambiguous = exact_term_lookup(ambiguous_request)
check("ambiguous_state", ambiguous.state is ExactTermLookupState.AMBIGUOUS_MAPPING)
check("ambiguous_multiplicity", ambiguous.multiplicity is MappingMultiplicity.ONE_TO_MANY)
check("ambiguous_concept_count", len(ambiguous.concept_candidate_refs) == 2)
check("ambiguous_sense_count", len(ambiguous.sense_candidate_refs) == 2)
check("ambiguous_order_stable", exact_term_lookup(ambiguous_request).concept_candidate_refs == ambiguous.concept_candidate_refs)
check("ambiguous_no_rank", ambiguous.candidate_order_is_ranked is False)
check("ambiguous_no_selection", ambiguous.occurrence_interpretation_selected is False)
check("ambiguous_selected_refs_none", ambiguous.selected_concept_ref is None and ambiguous.selected_sense_ref is None)
check("ambiguous_result_valid", validate_lookup_result(ambiguous).ok)

# Known exact lexical reference with no mapping.
unmapped = exact_term_lookup(request("mapping"))
check("unmapped_state", unmapped.state is ExactTermLookupState.UNMAPPED_TERM)
check("unmapped_exact", unmapped.exact_match is True)
check("unmapped_lexical_count", len(unmapped.lexical_reference_refs) == 1)
check("unmapped_mapping_empty", unmapped.mapping_refs == ())
check("unmapped_candidates_empty", unmapped.concept_candidate_refs == () and unmapped.sense_candidate_refs == ())
check("unmapped_result_valid", validate_lookup_result(unmapped).ok)

# Reviewed unsupported mapping with zero candidates.
unsupported = exact_term_lookup(request("sense"))
check("unsupported_state", unsupported.state is ExactTermLookupState.UNSUPPORTED_MAPPING)
check("unsupported_exact", unsupported.exact_match is True)
check("unsupported_mapping_count", len(unsupported.mapping_refs) == 1)
check("unsupported_zero_multiplicity", unsupported.multiplicity is MappingMultiplicity.ZERO)
check("unsupported_candidates_empty", unsupported.concept_candidate_refs == () and unsupported.sense_candidate_refs == ())
check("unsupported_result_valid", validate_lookup_result(unsupported).ok)

# No guessing or normalization. Every altered request remains unsupported.
no_exact_cases = (
    request("Concept"),
    request("CONCEPT"),
    request(" concept"),
    request("concept "),
    request("concePt"),
    request("concepts"),
    request("consept"),
    request("notion"),
    request("concept", "fr"),
    request("concept", ns_id=namespace_id.upper()),
    request("concept", ns_scope=("namespace:wrong",)),
    request("concept", domain=("domain:wrong",)),
)
for index, req in enumerate(no_exact_cases):
    result = exact_term_lookup(req)
    check(f"no_exact_{index}_state", result.state is ExactTermLookupState.NO_EXACT_LEXICAL_REFERENCE or result.state is ExactTermLookupState.UNMAPPED_TERM)
    check(f"no_exact_{index}_zero", result.multiplicity is MappingMultiplicity.ZERO)
    check(f"no_exact_{index}_no_candidates", result.concept_candidate_refs == () and result.sense_candidate_refs == ())
    check(f"no_exact_{index}_not_selected", result.occurrence_interpretation_selected is False)

# Wrong namespace/domain scope on an otherwise known lexical form must never use its mapping.
wrong_ns_scope = exact_term_lookup(request("concept", ns_scope=("namespace:wrong",)))
wrong_domain = exact_term_lookup(request("concept", domain=("domain:wrong",)))
check("wrong_namespace_scope_unmapped", wrong_ns_scope.state is ExactTermLookupState.UNMAPPED_TERM)
check("wrong_domain_unmapped", wrong_domain.state is ExactTermLookupState.UNMAPPED_TERM)

# Outward eligibility is reference-only and only for four preferred labels.
check("outward_key_count", len(OUTWARD_ELIGIBLE_LEXICAL_KEYS) == 4)
check("outward_ids_unique", len({item.eligibility_id for item in OUTWARD_ELIGIBILITY_REFERENCES}) == 4)
for index, item in enumerate(OUTWARD_ELIGIBILITY_REFERENCES):
    report = validate_outward_eligibility_reference(item)
    check(f"eligibility_{index}_valid", report.ok)
    check(f"eligibility_{index}_id", item.eligibility_id == item.expected_id())
    check(f"eligibility_{index}_state", item.eligibility_state is OutwardExpressionEligibilityState.ELIGIBLE_REFERENCE_ONLY)
    check(f"eligibility_{index}_no_render", item.rendering_authorized is False)
    check(f"eligibility_{index}_no_delivery", item.delivery_authorized is False)
    check(f"eligibility_{index}_no_runtime", item.runtime_authorized is False)
    lexical = lexical_reference_by_id(item.lexical_reference_id)
    check(f"eligibility_{index}_outward_kind", lexical.reference_kind is LexicalReferenceKind.CONTROLLED_OUTWARD_EXPRESSION)

# Every prohibited expansion has an explicit immutable refusal.
check("expansion_kind_order", SLICE37D_PROHIBITED_EXPANSION_KINDS == tuple(ProhibitedExpansionKind))
check("refusal_kind_order", tuple(item.expansion_kind for item in PROHIBITED_EXPANSION_REFUSALS) == tuple(ProhibitedExpansionKind))
for index, kind in enumerate(ProhibitedExpansionKind):
    refusal = prohibited_expansion_refusal(kind)
    report = validate_expansion_refusal(refusal)
    check(f"refusal_{index}_valid", report.ok)
    check(f"refusal_{index}_id", refusal.refusal_id == refusal.expected_id())
    check(f"refusal_{index}_kind", refusal.expansion_kind is kind)
    check(f"refusal_{index}_not_allowed", refusal.allowed is False)
    check(f"refusal_{index}_reason", bool(refusal.reason))
    check(f"refusal_{index}_authorities", refusal.prohibited_authorities == SLICE37D_PROHIBITED_AUTHORITIES)

# Exact-ID lookup rejects substitutes.
expect_exception("unknown_sense_id", KeyError, lambda: sense_by_id("controlled_sense:not-present"))
expect_exception("unknown_lexical_id", KeyError, lambda: lexical_reference_by_id("controlled_lexical_reference:not-present"))
expect_exception("unknown_mapping_id", KeyError, lambda: mapping_by_id("term_concept_mapping:not-present"))
expect_exception("sense_id_type", TypeError, lambda: sense_by_id(1))
expect_exception("lexical_id_type", TypeError, lambda: lexical_reference_by_id(1))
expect_exception("mapping_id_type", TypeError, lambda: mapping_by_id(1))
expect_exception("expansion_kind_type", TypeError, lambda: prohibited_expansion_refusal("case_fold"))

# Immutable records and fail-closed identity validation.
for name, item, field_name, replacement in (
    ("sense", CURRENT_SENSES[0], "sense_key", "changed"),
    ("lexical", CURRENT_LEXICAL_REFERENCES[0], "exact_form", "changed"),
    ("mapping", CURRENT_MAPPINGS[0], "version", "v99"),
    ("eligibility", OUTWARD_ELIGIBILITY_REFERENCES[0], "version", "v99"),
    ("refusal", PROHIBITED_EXPANSION_REFUSALS[0], "reason", "changed"),
):
    expect_exception(
        f"{name}_frozen",
        FrozenInstanceError,
        lambda item=item, field_name=field_name, replacement=replacement: setattr(item, field_name, replacement),
    )

bad_request = replace(ambiguous_request, request_id="wrong")
check("bad_request_fails", validate_lookup_request(bad_request).ok is False)
expect_exception("bad_request_asserted", SenseTermMappingValidationError, lambda: exact_term_lookup(bad_request))
bad_result = replace(ambiguous, result_id="wrong")
check("bad_result_fails", validate_lookup_result(bad_result).ok is False)
bad_selection = replace(ambiguous, occurrence_interpretation_selected=True)
check("selected_result_fails", validate_lookup_result(bad_selection).ok is False)
bad_rank = replace(ambiguous, candidate_order_is_ranked=True)
check("ranked_result_fails", validate_lookup_result(bad_rank).ok is False)
bad_state = replace(ambiguous, state="not-a-state")
check("invalid_state_type_fails_closed", validate_lookup_result(bad_state).ok is False)
bad_multiplicity = replace(ambiguous, multiplicity="not-a-multiplicity")
check("invalid_multiplicity_type_fails_closed", validate_lookup_result(bad_multiplicity).ok is False)

# No external or hidden authority.
check("prohibited_authorities_nonempty", len(SLICE37D_PROHIBITED_AUTHORITIES) >= 10)
check("prohibited_uses_nonempty", len(SLICE37D_COMMON_PROHIBITED_USES) >= 20)
check("no_external_resource", manifest.external_resource_loading_installed is False)
check("no_candidate_meaning", manifest.candidate_meaning_creation_installed is False)
check("no_structural_consumption", manifest.structural_integration_installed is False)
check("no_runtime", manifest.runtime_activation_installed is False)
check("no_routes", manifest.route_registration_installed is False)
check("no_tools", manifest.tool_activation_installed is False)
check("no_actions", manifest.action_execution_installed is False)
check("no_memory", manifest.memory_access_installed is False)
check("no_rendering", manifest.rendering_installed is False)
check("no_delivery", manifest.delivery_installed is False)

if failures:
    print("AI.WEB SLICE 37D BEHAVIOR TEST: FAIL")
    print(f"check_count={len(checks) + len(failures)}")
    print(f"failure_count={len(failures)}")
    for failure in failures:
        print(f"FAILURE: {failure}")
    raise SystemExit(1)

print("AI.WEB SLICE 37D BEHAVIOR TEST: PASS")
print(f"check_count={len(checks)}")
print(f"sense_count={len(registry.senses)}")
print(f"lexical_reference_count={len(registry.lexical_references)}")
print(f"mapping_count={len(registry.mappings)}")
print(f"outward_eligibility_count={len(registry.outward_eligibility_references)}")
print(f"prohibited_expansion_refusal_count={len(registry.prohibited_expansion_refusals)}")
print(f"governed_resource_versions={len(GOVERNANCE_BATCH.resources)}")
print(f"lifecycle_transitions={len(GOVERNANCE_BATCH.transitions)}")
print(f"registry_digest={registry.registry_digest()}")
print("one_to_one_mappings=8")
print("one_to_many_ambiguous_mappings=1")
print("unmapped_term_states=1")
print("unsupported_mapping_states=1")
print("case_spelling_stemming_synonym_similarity_model_dictionary_expansion=0")
print("occurrence_selection_ranking_candidate_meaning_structural_integration=0")
print("external_resources_routes_tools_memory_actions_rendering_delivery=0")
