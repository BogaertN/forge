"""Exact, non-normalizing Slice 37D registry lookup operations.

The operations are registry inspection only. They accept exact caller-supplied
keys and preserve zero, one, or multiple candidates without ranking or
selection. They never inspect a source occurrence.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

from ..schema import (
    ConceptLifecycleState,
    ControlledLexicalReference,
    ControlledSenseIdentity,
    TermConceptMappingIdentity,
)
from .identity import (
    with_expected_lookup_request_id,
    with_expected_lookup_result_id,
)
from .registry import SENSE_TERM_MAPPING_REGISTRY
from .schema import (
    ExactTermLookupRequest,
    ExactTermLookupResult,
    ExactTermLookupState,
    MappingExpansionRefusal,
    MappingMultiplicity,
    ProhibitedExpansionKind,
)
from .validation import (
    assert_lookup_request,
    assert_lookup_result,
    assert_registry,
    mapping_multiplicity,
)


T = TypeVar("T")


def _unique_preserving_order(values: Iterable[T]) -> tuple[T, ...]:
    return tuple(dict.fromkeys(values))


def make_exact_lookup_request(
    *,
    exact_form: str,
    language_tag: str,
    namespace_id: str,
    namespace_scope: tuple[str, ...],
    domain_scope: tuple[str, ...],
) -> ExactTermLookupRequest:
    """Construct one exact request without trimming or normalizing any field."""

    request = with_expected_lookup_request_id(
        ExactTermLookupRequest(
            request_id="",
            exact_form=exact_form,
            language_tag=language_tag,
            namespace_id=namespace_id,
            namespace_scope=namespace_scope,
            domain_scope=domain_scope,
        )
    )
    return assert_lookup_request(request)


def exact_term_lookup(
    request: ExactTermLookupRequest,
) -> ExactTermLookupResult:
    """Return exact candidate availability without occurrence interpretation."""

    assert_registry(SENSE_TERM_MAPPING_REGISTRY)
    assert_lookup_request(request)

    lexical_references = tuple(
        lexical
        for lexical in SENSE_TERM_MAPPING_REGISTRY.lexical_references
        if (
            lexical.namespace_id == request.namespace_id
            and lexical.exact_form == request.exact_form
            and lexical.language_tag == request.language_tag
            and lexical.case_sensitive is True
        )
    )

    if not lexical_references:
        result = ExactTermLookupResult(
            result_id="",
            request_ref=request.request_id,
            state=ExactTermLookupState.NO_EXACT_LEXICAL_REFERENCE,
            multiplicity=MappingMultiplicity.ZERO,
            lexical_reference_refs=(),
            mapping_refs=(),
            concept_candidate_refs=(),
            sense_candidate_refs=(),
            outward_eligibility_refs=(),
            exact_match=False,
            candidate_order_is_ranked=False,
            occurrence_interpretation_selected=False,
            selected_concept_ref=None,
            selected_sense_ref=None,
            reason=(
                "No controlled lexical reference matches every exact request "
                "field. No normalization or fallback was attempted."
            ),
            prohibited_authorities=(
                SENSE_TERM_MAPPING_REGISTRY.manifest.authority_limitations
            ),
        )
        return assert_lookup_result(
            with_expected_lookup_result_id(result)
        )

    lexical_ids = tuple(
        lexical.lexical_reference_id
        for lexical in lexical_references
    )
    mappings = tuple(
        mapping
        for mapping in SENSE_TERM_MAPPING_REGISTRY.mappings
        if (
            mapping.lexical_reference_id in lexical_ids
            and mapping.namespace_scope == request.namespace_scope
            and mapping.domain_scope == request.domain_scope
        )
    )

    eligibility_refs = tuple(
        item.eligibility_id
        for item in SENSE_TERM_MAPPING_REGISTRY.outward_eligibility_references
        if item.lexical_reference_id in lexical_ids
    )

    if not mappings:
        result = ExactTermLookupResult(
            result_id="",
            request_ref=request.request_id,
            state=ExactTermLookupState.UNMAPPED_TERM,
            multiplicity=MappingMultiplicity.ZERO,
            lexical_reference_refs=lexical_ids,
            mapping_refs=(),
            concept_candidate_refs=(),
            sense_candidate_refs=(),
            outward_eligibility_refs=eligibility_refs,
            exact_match=True,
            candidate_order_is_ranked=False,
            occurrence_interpretation_selected=False,
            selected_concept_ref=None,
            selected_sense_ref=None,
            reason=(
                "The exact controlled lexical reference exists, but no mapping "
                "record is admitted for the exact domain scope."
            ),
            prohibited_authorities=(
                SENSE_TERM_MAPPING_REGISTRY.manifest.authority_limitations
            ),
        )
        return assert_lookup_result(
            with_expected_lookup_result_id(result)
        )

    concept_candidates = _unique_preserving_order(
        reference
        for mapping in mappings
        for reference in mapping.concept_candidate_refs
    )
    sense_candidates = _unique_preserving_order(
        reference
        for mapping in mappings
        for reference in mapping.sense_candidate_refs
    )
    multiplicity = mapping_multiplicity(concept_candidates)

    mapping_states = tuple(mapping.lifecycle_state for mapping in mappings)
    if ConceptLifecycleState.AMBIGUOUS in mapping_states:
        state = ExactTermLookupState.AMBIGUOUS_MAPPING
        reason = (
            "The exact mapping preserves multiple materially supported concept "
            "and sense candidates. No candidate was ranked or selected."
        )
    elif ConceptLifecycleState.UNSUPPORTED in mapping_states:
        state = ExactTermLookupState.UNSUPPORTED_MAPPING
        reason = (
            "The exact lexical reference and reviewed mapping record exist, "
            "but no admitted concept or sense candidates are supported."
        )
    elif multiplicity is MappingMultiplicity.ONE_TO_ONE:
        state = ExactTermLookupState.MAPPED_ONE_TO_ONE
        reason = (
            "The exact mapping exposes one concept candidate and its bounded "
            "sense candidate without selecting occurrence meaning."
        )
    else:
        state = ExactTermLookupState.MAPPED_ONE_TO_MANY
        reason = (
            "The exact mapping exposes multiple concept candidates in "
            "deterministic record order without preference or ranking."
        )

    result = ExactTermLookupResult(
        result_id="",
        request_ref=request.request_id,
        state=state,
        multiplicity=multiplicity,
        lexical_reference_refs=lexical_ids,
        mapping_refs=tuple(mapping.mapping_id for mapping in mappings),
        concept_candidate_refs=concept_candidates,
        sense_candidate_refs=sense_candidates,
        outward_eligibility_refs=eligibility_refs,
        exact_match=True,
        candidate_order_is_ranked=False,
        occurrence_interpretation_selected=False,
        selected_concept_ref=None,
        selected_sense_ref=None,
        reason=reason,
        prohibited_authorities=(
            SENSE_TERM_MAPPING_REGISTRY.manifest.authority_limitations
        ),
    )
    return assert_lookup_result(with_expected_lookup_result_id(result))


def sense_by_id(sense_id: str) -> ControlledSenseIdentity:
    if not isinstance(sense_id, str):
        raise TypeError("sense_id must be str")
    for sense in SENSE_TERM_MAPPING_REGISTRY.senses:
        if sense.sense_id == sense_id:
            return sense
    raise KeyError(sense_id)


def lexical_reference_by_id(
    lexical_reference_id: str,
) -> ControlledLexicalReference:
    if not isinstance(lexical_reference_id, str):
        raise TypeError("lexical_reference_id must be str")
    for lexical in SENSE_TERM_MAPPING_REGISTRY.lexical_references:
        if lexical.lexical_reference_id == lexical_reference_id:
            return lexical
    raise KeyError(lexical_reference_id)


def mapping_by_id(mapping_id: str) -> TermConceptMappingIdentity:
    if not isinstance(mapping_id, str):
        raise TypeError("mapping_id must be str")
    for mapping in SENSE_TERM_MAPPING_REGISTRY.mappings:
        if mapping.mapping_id == mapping_id:
            return mapping
    raise KeyError(mapping_id)


def prohibited_expansion_refusal(
    expansion_kind: ProhibitedExpansionKind,
) -> MappingExpansionRefusal:
    if not isinstance(expansion_kind, ProhibitedExpansionKind):
        raise TypeError("expansion_kind must be ProhibitedExpansionKind")
    for refusal in SENSE_TERM_MAPPING_REGISTRY.prohibited_expansion_refusals:
        if refusal.expansion_kind is expansion_kind:
            return refusal
    raise KeyError(expansion_kind)
