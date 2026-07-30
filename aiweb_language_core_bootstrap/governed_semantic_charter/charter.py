"""Packaged first Forge semantic-charter proposal.

Every registry reference below is an exact reference to the installed
Forge-owned provisional seed.  The package is intentionally a small vertical
slice.  It is not generated from the whole registry and cannot silently grow
when unrelated provisional vocabulary is added.
"""

from __future__ import annotations

from dataclasses import replace
import hashlib
from typing import Final

from .schema import (
    CharterStatus,
    ProposedConceptSense,
    ProposedConstructionContract,
    ProposedPredicate,
    ProposedRole,
    ProposedSemanticCharter,
    SemanticCharterBoundary,
    SemanticReplayFixture,
)


_REGISTRY_REF: Final[str] = (
    "forge_preview_registry:"
    "eba54768ad3c5e10d0e370be39e41c0b77ccc41a2163c5de028b2bd77a4eb770"
)
_REGISTRY_VERSION: Final[str] = "forge-meaning-seed-v0"


# concept key, exact concept ID, sense key, exact sense ID
_CONCEPT_SENSE_ROWS: Final[tuple[tuple[str, str, str, str], ...]] = (
    (
        "forge",
        "forge_preview_concept:44f9be3bf9d2118e3158b22dddad50492452d2bbfa4e76a36610f7daa3f56b91",
        "forge_preview_sense",
        "forge_preview_sense:18ce27d19297706f0e2f45f104d3ba90d13c4a2667ff7e655215a57cc441f3a1",
    ),
    (
        "language_core",
        "forge_preview_concept:9c61313567b6891ca649a487db2a725fff06ef7fed7cb4f4fd8107f303604c6e",
        "language_core_preview_sense",
        "forge_preview_sense:21ad5fb87652637a440218244da3860b76a2105230c6780d5865dd901730fafc",
    ),
    (
        "rmc_memory",
        "forge_preview_concept:7ea34a078fd3dab9539164a727d9214aeff9b453053d078469e094becff25f62",
        "rmc_memory_preview_sense",
        "forge_preview_sense:1ac5e200784743622aaf6d600ed58ab53775d3627b3da18443c6110d3a850768",
    ),
    (
        "vector_memory",
        "forge_preview_concept:381d527ba8096779252e9697e2d04eb00a30e87a0b265548398808eb5ce5a4d2",
        "vector_memory_preview_sense",
        "forge_preview_sense:4dd3e2cd093af2b0722e03b248074ccf61313354f31ae19d7411a6e613e38742",
    ),
    (
        "system",
        "forge_preview_concept:32629574dc534fe1c392946848362cf93542c227527037f9dcf02269a99320e6",
        "system_preview_sense",
        "forge_preview_sense:c9790c8802eb50931deae94cc905188e3fdf92c99993ab7dba521f3493bf7769",
    ),
    (
        "status",
        "forge_preview_concept:1adce55b8c1b5ac6eedf72e573ba2c829c3d25e129a5c2c71dec738aca58c4ec",
        "status_preview_sense",
        "forge_preview_sense:9c831fedb194fbd4b5bdacc1e73061166399ac4170157a961179c88f4ff84765",
    ),
    (
        "manifest",
        "forge_preview_concept:e8c1b7526234442a60c82c5a197e5b8e53d056a9c7bae0ea294ef646b1770a5c",
        "manifest_preview_sense",
        "forge_preview_sense:088943fb25d86ca4718b92266320eb329b66ca34a225df48fc39c6823405784f",
    ),
)


# predicate key, exact predicate ID, currently declared required roles
_PREDICATE_ROWS: Final[tuple[tuple[str, str, tuple[str, ...]], ...]] = (
    (
        "mean",
        "forge_preview_predicate:fbf7bd4a66d6c0223375c58331487ee435004e27b147497c001ba69fef0b433a",
        ("definition_target",),
    ),
    (
        "inspect",
        "forge_preview_predicate:da03082f40b323e569d69c0e3e4e8e5c7fa2424b07c97a0869656788d438bf2d",
        ("object",),
    ),
    (
        "report",
        "forge_preview_predicate:a3d9ce325fa43b0976b8060c305cb3867f536fbcf15d3369529f5e511b6d8d8d",
        ("object",),
    ),
    (
        "use",
        "forge_preview_predicate:e0ac5983d5229f7e45784e5670d4ae44ff32ee0a3c092c3f5498aee4ab1cd2ed",
        ("actor", "object"),
    ),
    (
        "be",
        "forge_preview_predicate:a1a5236c723c11a30dc9aebc135e8affc39f5dedc180906682312bcfed3336c9",
        ("subject", "object"),
    ),
    (
        "compare",
        "forge_preview_predicate:b185de331eeca8b745fb4cd377b8a1dbc9887d8407f144e59195f35b3d8ab679",
        ("comparison_left", "comparison_right"),
    ),
)


_ROLE_ROWS: Final[tuple[tuple[str, str], ...]] = (
    (
        "actor",
        "forge_preview_role:d591038b977c6dfde5c86b61918cf842ce13cfb7f9676f593efbc351a9867431",
    ),
    (
        "subject",
        "forge_preview_role:0e06421c70654e990ca797a2833668be54481a6435f9284d4e8d2b721befadca",
    ),
    (
        "object",
        "forge_preview_role:40504b5b870482cc26ccf9befddf913742a352dead4b1dcab19943a960f3b2bb",
    ),
    (
        "definition_target",
        "forge_preview_role:a19234bdb7644cb0c37d4022d059dcf85fe3040a9e9f76c98a43de969c822aa0",
    ),
    (
        "comparison_left",
        "forge_preview_role:bccc6968ce7b57a7e077097a94a9a9534f85aaba23e61dee368eb01cf242eeaa",
    ),
    (
        "comparison_right",
        "forge_preview_role:efa4ddfda0337b39aec4ff185696296a9bfaefec6823ed999842ddd316ae73f4",
    ),
)


# key, grammar ID, frame, speech act, purport, predicate, effective roles,
# negated, Echo-reparse-only.
_CONSTRUCTION_ROWS: Final[tuple[tuple[object, ...], ...]] = (
    (
        "definition_do",
        "FORGE-GRAMMAR-V0-DEFINITION-DO",
        "definition_question",
        "definition_request",
        "request_provisional_definition",
        "mean",
        ("definition_target",),
        False,
        False,
    ),
    (
        "definition_copula",
        "FORGE-GRAMMAR-V0-DEFINITION-COPULA",
        "definition_question",
        "definition_request",
        "request_provisional_definition",
        "mean",
        ("definition_target",),
        False,
        False,
    ),
    (
        "governed_definition_response",
        "FORGE-GRAMMAR-V0-GOVERNED-DEFINITION-RESPONSE",
        "definition_response",
        "definition_response",
        "provide_governed_provisional_definition",
        "mean",
        ("definition_target",),
        False,
        True,
    ),
    (
        "imperative_inspect",
        "FORGE-GRAMMAR-V0-IMPERATIVE",
        "imperative_request",
        "request",
        "request_read_only_preview",
        "inspect",
        ("object",),
        False,
        False,
    ),
    (
        "modal_report",
        "FORGE-GRAMMAR-V0-MODAL",
        "modal_request",
        "request",
        "request_read_only_preview",
        "report",
        ("actor", "object"),
        False,
        False,
    ),
    (
        "positive_use",
        "FORGE-GRAMMAR-V0-POSITIVE",
        "positive_clause",
        "statement",
        "assert_provisional_relation",
        "use",
        ("actor", "object"),
        False,
        False,
    ),
    (
        "negative_use",
        "FORGE-GRAMMAR-V0-NEGATIVE-DO",
        "negative_clause",
        "statement",
        "assert_provisional_relation",
        "use",
        ("actor", "object"),
        True,
        False,
    ),
    (
        "copula_anchor_positive",
        "FORGE-GRAMMAR-V0-COPULA-ANCHOR",
        "copula_clause",
        "statement",
        "assert_provisional_class_relation",
        "be",
        ("subject", "object"),
        False,
        False,
    ),
    (
        "compare_rmc_designs",
        "FORGE-GRAMMAR-V0-COMPARE",
        "comparison_request",
        "comparison_request",
        "request_bounded_comparison",
        "compare",
        ("comparison_left", "comparison_right"),
        False,
        False,
    ),
)


# key, exact source, construction key, exact current candidate ID, exact stable
# semantic signature, role/concept pairs, negation.
_FIXTURE_ROWS: Final[tuple[tuple[object, ...], ...]] = (
    (
        "define_language_core",
        "What does language core mean?",
        "definition_do",
        "meaning_candidate:d4fce6f6678a79ba91532e5a95a2671a72fdde0d1cb02269746cd1e5820ae715",
        "semantic_signature:4b5abe7d2653afcb692cb196c6779de93a0e25e35aec0d56ce298bf0b3e23049",
        (("definition_target", "language_core"),),
        False,
    ),
    (
        "define_rmc",
        "What is RMC?",
        "definition_copula",
        "meaning_candidate:b3089474198f1da6ef61b904b848b627e0b35abcfa20f3a0d80b8e8ed8121ea3",
        "semantic_signature:31e3548c152150012b3915ebee95c2daadd35f0872b50767a6e30f700905212f",
        (("definition_target", "rmc_memory"),),
        False,
    ),
    (
        "inspect_manifest",
        "Please inspect the manifest.",
        "imperative_inspect",
        "meaning_candidate:c63db486640144eeadb9c466402350ad0ec1658bdafa01c1ddc67b05539de5b6",
        "semantic_signature:c216eae29c67a89f15b3def3f232144535b4059b73a4399cae1f14434f4b5281",
        (("object", "manifest"),),
        False,
    ),
    (
        "report_status",
        "Can Forge report status?",
        "modal_report",
        "meaning_candidate:591c9c041778217da476b13df418d15661a03918b969221e46a7e82505491e63",
        "semantic_signature:869e71b373cb76fb56df627767615892fa91e44eb170375dada8ca740d094543",
        (("actor", "forge"), ("object", "status")),
        False,
    ),
    (
        "forge_uses_rmc",
        "Forge uses RMC memory.",
        "positive_use",
        "meaning_candidate:7ccb3df8f3a0af171b7ac359268c4ffd6ef7883507f7bf253a4c609e68fb261b",
        "semantic_signature:882625dda4cc11a1858c5cad2b54a32fd2a79684fb8ab37f71aba57119c57953",
        (("actor", "forge"), ("object", "rmc_memory")),
        False,
    ),
    (
        "forge_does_not_use_vector_memory",
        "Forge does not use vector memory.",
        "negative_use",
        "meaning_candidate:4965c4138f22c73d02ccbee77471a63edde34ebf7cdd39131e960d8d527047d1",
        "semantic_signature:3e918114605060abd1381d472032794558cd41fc931d69ceca96b6d73fd9463a",
        (("actor", "forge"), ("object", "vector_memory")),
        True,
    ),
    (
        "forge_is_system",
        "Forge is a system.",
        "copula_anchor_positive",
        "meaning_candidate:424cb7124d6884c4ad89ff73ffa68bf5127f76ee783a1fa06cb5af974240954a",
        "semantic_signature:cd8cc11faa355ca1d8232cdcf50acfc92a83def4cd70095f48c0302fb55035b5",
        (("subject", "forge"), ("object", "system")),
        False,
    ),
    (
        "compare_rmc_and_vector_memory",
        "Compare RMC memory and vector memory.",
        "compare_rmc_designs",
        "meaning_candidate:ae0f5c67b645acd714067e9c73693e49a7b4dd310fc72eb8777aa9d1ad886ab9",
        "semantic_signature:37a447191d0fe213c14c7efdfaefd6febe1777144d6db6c4e6a09eabb2f7a0c7",
        (("comparison_left", "rmc_memory"), ("comparison_right", "vector_memory")),
        False,
    ),
)


def _concept_sense_proposals() -> tuple[ProposedConceptSense, ...]:
    values: list[ProposedConceptSense] = []
    for concept_key, concept_ref, sense_key, sense_ref in _CONCEPT_SENSE_ROWS:
        value = ProposedConceptSense(
            proposal_id="pending",
            concept_key=concept_key,
            concept_ref=concept_ref,
            sense_key=sense_key,
            sense_ref=sense_ref,
            forge_registry_owned=True,
            source_record_provisional=True,
            operator_approval_required=True,
        )
        values.append(replace(value, proposal_id=value.expected_id()))
    return tuple(values)


def _predicate_proposals() -> tuple[ProposedPredicate, ...]:
    values: list[ProposedPredicate] = []
    for predicate_key, predicate_ref, required_roles in _PREDICATE_ROWS:
        value = ProposedPredicate(
            proposal_id="pending",
            predicate_key=predicate_key,
            predicate_ref=predicate_ref,
            declared_required_role_keys=required_roles,
            forge_registry_owned=True,
            source_record_provisional=True,
            operator_approval_required=True,
        )
        values.append(replace(value, proposal_id=value.expected_id()))
    return tuple(values)


def _role_proposals() -> tuple[ProposedRole, ...]:
    values: list[ProposedRole] = []
    for role_key, role_ref in _ROLE_ROWS:
        value = ProposedRole(
            proposal_id="pending",
            role_key=role_key,
            role_ref=role_ref,
            forge_registry_owned=True,
            source_record_provisional=True,
            operator_approval_required=True,
        )
        values.append(replace(value, proposal_id=value.expected_id()))
    return tuple(values)


def _construction_proposals(
    predicates: tuple[ProposedPredicate, ...],
) -> tuple[ProposedConstructionContract, ...]:
    predicate_refs = {item.predicate_key: item.predicate_ref for item in predicates}
    values: list[ProposedConstructionContract] = []
    for row in _CONSTRUCTION_ROWS:
        (
            construction_key,
            grammar_rule_id,
            frame_key,
            speech_act,
            purport,
            predicate_key,
            effective_roles,
            negated,
            echo_reparse_only,
        ) = row
        value = ProposedConstructionContract(
            construction_id="pending",
            construction_key=str(construction_key),
            grammar_rule_id=str(grammar_rule_id),
            frame_key=str(frame_key),
            speech_act=str(speech_act),
            purport=str(purport),
            predicate_key=str(predicate_key),
            predicate_ref=predicate_refs[str(predicate_key)],
            effective_role_keys=effective_roles,
            negated=bool(negated),
            echo_reparse_only=bool(echo_reparse_only),
            exact_fixture_only=True,
            operator_approval_required=True,
            runtime_active=False,
        )
        values.append(replace(value, construction_id=value.expected_id()))
    return tuple(values)


def _replay_fixtures(
    concept_senses: tuple[ProposedConceptSense, ...],
    predicates: tuple[ProposedPredicate, ...],
    constructions: tuple[ProposedConstructionContract, ...],
) -> tuple[SemanticReplayFixture, ...]:
    concepts = {item.concept_key: item for item in concept_senses}
    predicate_refs = {item.predicate_key: item.predicate_ref for item in predicates}
    construction_by_key = {
        item.construction_key: item for item in constructions
    }
    values: list[SemanticReplayFixture] = []
    for row in _FIXTURE_ROWS:
        (
            fixture_key,
            source_text,
            construction_key,
            candidate_ref,
            signature,
            role_concepts,
            negated,
        ) = row
        construction = construction_by_key[str(construction_key)]
        role_pairs = tuple(role_concepts)
        expected_concepts = tuple(
            sorted({concepts[concept_key].concept_ref for _role, concept_key in role_pairs})
        )
        expected_senses = tuple(
            sorted({concepts[concept_key].sense_ref for _role, concept_key in role_pairs})
        )
        relations = tuple(
            sorted(
                (f"predicate:{construction.predicate_key}",)
                + tuple(
                    f"role:{role_key}:{concepts[concept_key].concept_ref}"
                    for role_key, concept_key in role_pairs
                )
            )
        )
        value = SemanticReplayFixture(
            fixture_id="pending",
            fixture_key=str(fixture_key),
            exact_source_text=str(source_text),
            exact_source_sha256=hashlib.sha256(
                str(source_text).encode("utf-8")
            ).hexdigest(),
            construction_ref=construction.construction_id,
            expected_meaning_candidate_ref=str(candidate_ref),
            expected_semantic_signature=str(signature),
            expected_predicate_ref=predicate_refs[construction.predicate_key],
            expected_role_keys=tuple(role for role, _concept in role_pairs),
            expected_concept_refs=expected_concepts,
            expected_sense_refs=expected_senses,
            expected_relation_refs=relations,
            expected_negated=bool(negated),
            expected_compiler_status="PREVIEW_READY",
            expected_echo_status="PASS",
            operator_approval_required=True,
            runtime_authority=False,
        )
        values.append(replace(value, fixture_id=value.expected_id()))
    return tuple(values)


def _boundary() -> SemanticCharterBoundary:
    value = SemanticCharterBoundary(
        boundary_id="pending",
        forge_owned=True,
        proposal_only=True,
        operator_approval_required=True,
        operator_approval_present=False,
        active=False,
        canonical_authority=False,
        truth_authority=False,
        selection_authority=False,
        runtime_authority=False,
        route_authority=False,
        tool_authority=False,
        action_authority=False,
        delivery_authority=False,
        memory_write_authority=False,
        external_reference_authority=False,
        tokenization_performed=False,
        model_called=False,
        embedding_used=False,
        vector_used=False,
        similarity_scoring_used=False,
        filesystem_read_performed=False,
        filesystem_write_performed=False,
        network_access_performed=False,
        environment_access_performed=False,
        memory_read_performed=False,
        memory_write_performed=False,
        route_registration_performed=False,
        tool_routing_performed=False,
        action_performed=False,
        delivery_performed=False,
    )
    return replace(value, boundary_id=value.expected_id())


def build_proposed_semantic_charter() -> ProposedSemanticCharter:
    """Build the exact packaged proposal without approving or activating it."""

    concept_senses = _concept_sense_proposals()
    predicates = _predicate_proposals()
    roles = _role_proposals()
    constructions = _construction_proposals(predicates)
    fixtures = _replay_fixtures(concept_senses, predicates, constructions)
    value = ProposedSemanticCharter(
        charter_id="pending",
        charter_key="forge_first_governed_semantic_vertical_slice",
        status=CharterStatus.PROPOSED_FOR_OPERATOR_APPROVAL,
        registry_ref=_REGISTRY_REF,
        registry_version=_REGISTRY_VERSION,
        concept_senses=concept_senses,
        predicates=predicates,
        roles=roles,
        constructions=constructions,
        replay_fixtures=fixtures,
        boundary=_boundary(),
        deterministic=True,
        forge_owned=True,
        proposed=True,
        operator_approval_required=True,
        operator_approval_present=False,
        active=False,
        canonical_authority=False,
        runtime_authority=False,
        memory_write_authority=False,
    )
    return replace(value, charter_id=value.expected_id())


PROPOSED_SEMANTIC_CHARTER: Final[ProposedSemanticCharter] = (
    build_proposed_semantic_charter()
)


def proposed_semantic_charter() -> ProposedSemanticCharter:
    return PROPOSED_SEMANTIC_CHARTER


__all__ = (
    "PROPOSED_SEMANTIC_CHARTER",
    "build_proposed_semantic_charter",
    "proposed_semantic_charter",
)
