"""Closed deterministic renderer for governed output manifests."""

from __future__ import annotations

from dataclasses import replace
import hashlib

from ..meaning_compiler_preview.registry import forge_seed_registry
from ..meaning_compiler_preview.schema import MeaningCompilerPreviewResult
from ..operator_council.schema import OperatorCouncilResult
from .manifest import validate_governed_output_manifest
from .schema import (
    GOVERNED_OUTPUT_RENDERER_VERSION,
    GOVERNED_OUTPUT_SCHEMA_VERSION,
    GovernedOutputManifest,
    GovernedOutputValidationError,
    RenderedOutputCandidate,
    pure_output_boundary,
)


def _selected_meaning(result: MeaningCompilerPreviewResult) -> object:
    selected = result.selected_meaning
    if selected is None:
        raise ValueError("selected_meaning_required")
    return selected


def _role_map(selected: object) -> dict[str, object]:
    roles = {role.role_key: role for role in selected.roles}
    if len(roles) != len(selected.roles):
        raise ValueError("duplicate_semantic_role")
    return roles


def _concept(concept_ref: str) -> object:
    matches = tuple(
        item
        for item in forge_seed_registry().concepts
        if item.concept_id == concept_ref
    )
    if len(matches) != 1:
        raise ValueError("render_concept_not_unique_in_registry")
    return matches[0]


def _predicate(predicate_key: str) -> object:
    matches = tuple(
        item
        for item in forge_seed_registry().predicates
        if item.predicate_key == predicate_key
    )
    if len(matches) != 1:
        raise ValueError("render_predicate_not_unique_in_registry")
    return matches[0]


def _outward_label(concept_ref: str) -> str:
    concept = _concept(concept_ref)
    if concept.concept_key in {
        "forge",
        "forge_core",
        "language_core",
        "rmc_memory",
    }:
        return concept.preferred_label
    label = concept.preferred_label
    if not label:
        raise ValueError("render_concept_label_empty")
    return label[:1].lower() + label[1:]


def _definite_phrase(concept_ref: str) -> str:
    concept = _concept(concept_ref)
    label = _outward_label(concept_ref)
    if concept.concept_key in {
        "forge",
        "forge_core",
        "language_core",
        "rmc_memory",
    }:
        return label
    return "the " + label


def _indefinite_phrase(concept_ref: str) -> str:
    concept = _concept(concept_ref)
    label = _outward_label(concept_ref)
    if concept.semantic_class in {"quality", "state"}:
        return label
    article = "an" if label[:1].lower() in {"a", "e", "i", "o", "u"} else "a"
    return f"{article} {label}"


def _third_person_present(predicate_key: str) -> str:
    predicate = _predicate(predicate_key)
    if len(predicate.exact_surface_forms) < 2:
        raise ValueError("third_person_predicate_surface_not_declared")
    return predicate.exact_surface_forms[1]


def _require_roles(roles: dict[str, object], expected: frozenset[str]) -> None:
    if frozenset(roles) != expected:
        raise ValueError("renderer_role_contract_mismatch")


def _render_text(selected: object) -> str:
    roles = _role_map(selected)
    if selected.speech_act == "definition_request":
        _require_roles(roles, frozenset({"definition_target"}))
        concept = _concept(roles["definition_target"].concept_ref)
        return f"{concept.preferred_label} means {concept.provisional_definition}."
    if selected.predicate_key == "compare":
        _require_roles(
            roles,
            frozenset({"comparison_left", "comparison_right"}),
        )
        return (
            f"Compare {_outward_label(roles['comparison_left'].concept_ref)} "
            f"and {_outward_label(roles['comparison_right'].concept_ref)}."
        )
    if selected.predicate_key == "be":
        _require_roles(roles, frozenset({"subject", "object"}))
        negation = " not" if selected.negated else ""
        return (
            f"{_outward_label(roles['subject'].concept_ref)} is{negation} "
            f"{_indefinite_phrase(roles['object'].concept_ref)}."
        )
    if selected.speech_act == "request" and "actor" in roles:
        _require_roles(roles, frozenset({"actor", "object"}))
        return (
            f"Can {_outward_label(roles['actor'].concept_ref)} "
            f"{selected.predicate_key} "
            f"{_definite_phrase(roles['object'].concept_ref)}?"
        )
    if selected.speech_act == "request":
        _require_roles(roles, frozenset({"object"}))
        return (
            f"Please {selected.predicate_key} "
            f"{_definite_phrase(roles['object'].concept_ref)}."
        )
    _require_roles(roles, frozenset({"actor", "object"}))
    actor = _outward_label(roles["actor"].concept_ref)
    object_phrase = _definite_phrase(roles["object"].concept_ref)
    if selected.negated:
        return f"{actor} does not {selected.predicate_key} {object_phrase}."
    return f"{actor} {_third_person_present(selected.predicate_key)} {object_phrase}."


def _expected_rendered_output(
    manifest: GovernedOutputManifest,
    compiler_result: MeaningCompilerPreviewResult,
) -> RenderedOutputCandidate:
    selected = _selected_meaning(compiler_result)
    text = _render_text(selected)
    compiler_wording = compiler_result.candidate_wording
    if compiler_wording is None or compiler_wording.text != text:
        raise ValueError("deterministic_renderer_disagrees_with_compiler_preview")
    encoded = text.encode("utf-8")
    value = RenderedOutputCandidate(
        rendered_output_id="pending",
        schema_version=GOVERNED_OUTPUT_SCHEMA_VERSION,
        manifest_ref=manifest.manifest_id,
        compiler_result_ref=compiler_result.result_id,
        selected_meaning_ref=selected.meaning_candidate_id,
        registry_ref=manifest.registry_ref,
        renderer_version=GOVERNED_OUTPUT_RENDERER_VERSION,
        output_purpose=manifest.output_purpose,
        template_key=manifest.render_template_key,
        transition_rule_ref=manifest.transition_rule_ref,
        text=text,
        text_sha256=hashlib.sha256(encoded).hexdigest(),
        code_point_length=len(text),
        utf8_byte_length=len(encoded),
        source_semantic_contract_ref=(
            manifest.source_semantic_contract.semantic_contract_id
        ),
        expected_output_semantic_contract=(
            manifest.expected_output_semantic_contract
        ),
        expected_output_role_bindings=(
            manifest.expected_output_role_bindings
        ),
        expected_output_relation_refs=(
            manifest.expected_output_relation_refs
        ),
        answer_delivery_eligible=manifest.answer_delivery_eligible,
        provisional=True,
        operator_preview_exposed=True,
        answer_delivery_authorized=False,
        answer_delivery_performed=False,
        boundary=pure_output_boundary(),
    )
    return replace(
        value,
        rendered_output_id=value.expected_id(),
    )


def validate_rendered_output_candidate(
    rendered_output: object,
    manifest: object,
    compiler_result: object,
    council_result: object,
) -> tuple[str, ...]:
    """Validate exact deterministic replay; hashes alone are insufficient."""

    if type(rendered_output) is not RenderedOutputCandidate:
        return ("rendered_output_type_not_admitted",)
    issues = list(
        validate_governed_output_manifest(
            manifest,
            compiler_result,
            council_result,
        )
    )
    if issues:
        return tuple(issues)
    assert type(manifest) is GovernedOutputManifest
    assert type(compiler_result) is MeaningCompilerPreviewResult
    assert type(council_result) is OperatorCouncilResult
    if rendered_output.rendered_output_id != rendered_output.expected_id():
        issues.append("rendered_output_content_identity_mismatch")
    try:
        expected = _expected_rendered_output(manifest, compiler_result)
    except Exception:
        issues.append("deterministic_render_failed_closed")
        return tuple(dict.fromkeys(issues))
    if rendered_output != expected:
        issues.append("rendered_output_not_exact_manifest_projection")
    if rendered_output.boundary != pure_output_boundary():
        issues.append("rendered_output_pure_boundary_mismatch")
    if (
        rendered_output.provisional is not True
        or rendered_output.operator_preview_exposed is not True
        or rendered_output.answer_delivery_authorized is not False
        or rendered_output.answer_delivery_performed is not False
    ):
        issues.append("rendered_output_authority_boundary_invalid")
    return tuple(dict.fromkeys(issues))


def render_governed_output(
    manifest: object,
    compiler_result: object,
    council_result: object,
) -> RenderedOutputCandidate:
    """Render only from an exact validated manifest; no free-form slots exist."""

    manifest_issues = validate_governed_output_manifest(
        manifest,
        compiler_result,
        council_result,
    )
    if manifest_issues:
        raise GovernedOutputValidationError(manifest_issues)
    assert type(manifest) is GovernedOutputManifest
    assert type(compiler_result) is MeaningCompilerPreviewResult
    rendered = _expected_rendered_output(manifest, compiler_result)
    issues = validate_rendered_output_candidate(
        rendered,
        manifest,
        compiler_result,
        council_result,
    )
    if issues:
        raise GovernedOutputValidationError(issues)
    return rendered


__all__ = (
    "render_governed_output",
    "validate_rendered_output_candidate",
)
