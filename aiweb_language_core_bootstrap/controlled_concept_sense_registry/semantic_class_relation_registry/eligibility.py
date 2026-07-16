"""Pure exact-ID lookup and relation-type eligibility evaluation for Slice 37E.

This module never creates a relation instance or fact.  An eligible result means
only that an admitted relation type permits the explicit class memberships of
the supplied admitted concepts within the exact requested Slice 37E scope.
"""

from __future__ import annotations

from .identity import (
    with_expected_eligibility_request_id,
    with_expected_eligibility_result_id,
)
from .registry import SEMANTIC_CLASS_RELATION_REGISTRY
from .schema import (
    RelationEligibilityRequest,
    RelationEligibilityResult,
    RelationEligibilityState,
    RelationStateKind,
)
from .validation import assert_eligibility_request


def semantic_class_by_id(semantic_class_id: str):
    return next(
        (
            item
            for item in SEMANTIC_CLASS_RELATION_REGISTRY.semantic_classes
            if item.semantic_class_id == semantic_class_id
        ),
        None,
    )


def relation_family_by_id(relation_family_id: str):
    return next(
        (
            item
            for item in SEMANTIC_CLASS_RELATION_REGISTRY.relation_families
            if item.relation_family_id == relation_family_id
        ),
        None,
    )


def relation_type_by_id(relation_type_id: str):
    return next(
        (
            item
            for item in SEMANTIC_CLASS_RELATION_REGISTRY.relation_types
            if item.relation_type_id == relation_type_id
        ),
        None,
    )


def membership_by_id(membership_id: str):
    return next(
        (
            item
            for item in SEMANTIC_CLASS_RELATION_REGISTRY.memberships
            if item.membership_id == membership_id
        ),
        None,
    )


def memberships_for_concept(concept_id: str):
    return tuple(
        item
        for item in SEMANTIC_CLASS_RELATION_REGISTRY.memberships
        if item.concept_ref == concept_id
    )


def relation_state_policy(state_kind: RelationStateKind):
    return next(
        (
            item
            for item in SEMANTIC_CLASS_RELATION_REGISTRY.relation_state_policies
            if item.state_kind is state_kind
        ),
        None,
    )


def make_relation_eligibility_request(
    *,
    relation_type_id: str,
    domain_concept_id: str,
    range_concept_id: str,
    requested_scope_tags: tuple[str, ...],
) -> RelationEligibilityRequest:
    return with_expected_eligibility_request_id(
        RelationEligibilityRequest(
            request_id="",
            relation_type_id=relation_type_id,
            domain_concept_id=domain_concept_id,
            range_concept_id=range_concept_id,
            requested_scope_tags=requested_scope_tags,
        )
    )


def _result(
    request: RelationEligibilityRequest,
    *,
    state: RelationEligibilityState,
    relation_type_ref: str | None,
    domain_membership_refs: tuple[str, ...] = (),
    range_membership_refs: tuple[str, ...] = (),
    eligible: bool,
    reason: str,
) -> RelationEligibilityResult:
    return with_expected_eligibility_result_id(
        RelationEligibilityResult(
            result_id="",
            request_ref=request.request_id,
            state=state,
            relation_type_ref=relation_type_ref,
            matched_domain_membership_refs=domain_membership_refs,
            matched_range_membership_refs=range_membership_refs,
            eligible_for_later_instance_review=eligible,
            relation_instance_created=False,
            relation_fact_asserted=False,
            truth_determined=False,
            evidence_sufficiency_determined=False,
            verified_status_applied=False,
            implementation_determined=False,
            reason=reason,
            prohibited_implication_refs=(
                SEMANTIC_CLASS_RELATION_REGISTRY.manifest.prohibited_implication_refs
            ),
        )
    )


def evaluate_relation_type_eligibility(
    request: RelationEligibilityRequest,
) -> RelationEligibilityResult:
    """Return deterministic type eligibility without creating a relation fact."""

    assert_eligibility_request(request)
    registry = SEMANTIC_CLASS_RELATION_REGISTRY

    relation_type = relation_type_by_id(request.relation_type_id)
    if relation_type is None:
        return _result(
            request,
            state=RelationEligibilityState.UNKNOWN_RELATION_TYPE,
            relation_type_ref=None,
            eligible=False,
            reason="The exact relation-type identity is not in the closed Slice 37E registry.",
        )

    admitted_concept_ids = {
        item.concept_id
        for item in registry.predecessor_registry.concept_registry.admitted_concepts
    }
    if request.domain_concept_id not in admitted_concept_ids:
        return _result(
            request,
            state=RelationEligibilityState.UNKNOWN_DOMAIN_CONCEPT,
            relation_type_ref=relation_type.relation_type_id,
            eligible=False,
            reason="The exact domain concept identity is not admitted in the predecessor registry.",
        )
    if request.range_concept_id not in admitted_concept_ids:
        return _result(
            request,
            state=RelationEligibilityState.UNKNOWN_RANGE_CONCEPT,
            relation_type_ref=relation_type.relation_type_id,
            eligible=False,
            reason="The exact range concept identity is not admitted in the predecessor registry.",
        )

    rule = next(
        item
        for item in registry.relation_type_rules
        if item.relation_type_ref == relation_type.relation_type_id
    )
    if not set(request.requested_scope_tags).issubset(set(rule.scope_tags)):
        return _result(
            request,
            state=RelationEligibilityState.PROHIBITED_SCOPE_EXPANSION,
            relation_type_ref=relation_type.relation_type_id,
            eligible=False,
            reason="The request contains scope outside the exact admitted relation-type rule.",
        )

    domain_memberships = tuple(
        item
        for item in memberships_for_concept(request.domain_concept_id)
        if item.semantic_class_ref in rule.permitted_domain_class_refs
    )
    if not domain_memberships:
        return _result(
            request,
            state=RelationEligibilityState.DOMAIN_CLASS_NOT_PERMITTED,
            relation_type_ref=relation_type.relation_type_id,
            eligible=False,
            reason="No explicit admitted domain membership satisfies the relation-type rule.",
        )

    range_memberships = tuple(
        item
        for item in memberships_for_concept(request.range_concept_id)
        if item.semantic_class_ref in rule.permitted_range_class_refs
    )
    if not range_memberships:
        return _result(
            request,
            state=RelationEligibilityState.RANGE_CLASS_NOT_PERMITTED,
            relation_type_ref=relation_type.relation_type_id,
            domain_membership_refs=tuple(
                item.membership_id for item in domain_memberships
            ),
            eligible=False,
            reason="No explicit admitted range membership satisfies the relation-type rule.",
        )

    return _result(
        request,
        state=RelationEligibilityState.ELIGIBLE_TYPE_ONLY,
        relation_type_ref=relation_type.relation_type_id,
        domain_membership_refs=tuple(
            item.membership_id for item in domain_memberships
        ),
        range_membership_refs=tuple(
            item.membership_id for item in range_memberships
        ),
        eligible=True,
        reason=(
            "The explicit concept memberships satisfy the admitted domain and "
            "range classes. This is type eligibility only; no relation instance "
            "or fact is created or asserted."
        ),
    )
