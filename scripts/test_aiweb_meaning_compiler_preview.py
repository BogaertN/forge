#!/usr/bin/env python3
"""Behavior and adversarial acceptance for the bounded meaning preview."""

from __future__ import annotations

import argparse
import builtins
from contextlib import ExitStack
from dataclasses import FrozenInstanceError, replace
import hashlib
import inspect
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import urllib.request
from unittest.mock import patch


class Ledger:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []

    def check(self, condition: object, label: str, detail: object = "") -> None:
        self.checks += 1
        if condition is not True:
            message = label
            if detail not in (None, ""):
                message += ": " + repr(detail)[:1200]
            self.failures.append(message)
            print("FAIL - " + message)


def _value(value: object, name: str, default: object = None) -> object:
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def _enum_value(value: object) -> str:
    return str(getattr(value, "value", value))


def _dict(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return value
    method = getattr(value, "to_dict", None)
    if callable(method):
        result = method()
        if isinstance(result, dict):
            return result
    raise AssertionError(f"record has no dictionary representation: {type(value).__name__}")


def _sequence(value: object, name: str) -> tuple[object, ...]:
    raw = _value(value, name, ())
    return tuple(raw) if isinstance(raw, (tuple, list)) else ()


def _status(value: object) -> str:
    return _enum_value(_value(value, "status", ""))


def _canonical(value: object) -> str:
    return json.dumps(
        _dict(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _all_keys(value: object) -> set[str]:
    if not isinstance(value, (dict, tuple, list)):
        method = getattr(value, "to_dict", None)
        if callable(method):
            value = method()
    if isinstance(value, dict):
        keys = {str(key) for key in value}
        for nested in value.values():
            keys.update(_all_keys(nested))
        return keys
    if isinstance(value, (tuple, list)):
        keys: set[str] = set()
        for nested in value:
            keys.update(_all_keys(nested))
        return keys
    return set()


def _forbidden(*args: object, **kwargs: object) -> object:
    raise AssertionError("forbidden external side effect attempted")


def _candidate_refs(candidate: object) -> dict[str, tuple[str, ...]]:
    concepts: list[str] = []
    for role in _sequence(candidate, "roles"):
        concept = str(_value(role, "concept_ref", ""))
        if concept and concept not in concepts:
            concepts.append(concept)
    return {
        "concept_refs": tuple(concepts),
        "relation_refs": tuple(str(item) for item in _sequence(candidate, "relation_refs")),
        "ancestry_refs": tuple(str(item) for item in _sequence(candidate, "ancestry_refs")),
    }


def _unique_candidate_refs(
    target: object,
    alternatives: tuple[object, ...],
) -> dict[str, tuple[str, ...]]:
    target_refs = _candidate_refs(target)
    other_refs: dict[str, set[str]] = {
        key: set()
        for key in target_refs
    }
    for candidate in alternatives:
        if candidate is target:
            continue
        values = _candidate_refs(candidate)
        for key in other_refs:
            other_refs[key].update(values[key])
    unique = {
        key: tuple(item for item in values if item not in other_refs[key])
        for key, values in target_refs.items()
    }
    if not any(unique.values()):
        return target_refs
    return unique


def _build_context_record(builder, refs: dict[str, tuple[str, ...]], suffix: str):
    """Call the approved builder while tolerating optional provenance fields."""

    available = inspect.signature(builder).parameters
    proposed: dict[str, object] = {
        "semantic_contract_refs": refs.get("semantic_contract_refs", ()),
        "concept_refs": refs.get("concept_refs", ()),
        "relation_refs": refs.get("relation_refs", ()),
        "ancestry_refs": refs.get("ancestry_refs", ()),
        "phase_refs": (),
        "correction_refs": (),
        "echo_receipt_refs": (),
        "lifecycle_state": "accepted",
        "exact_reference_resonance_only": True,
        "raw_text_present": False,
        "source_record_ref": "meaning-preview-test:" + suffix,
        "record_key": "meaning-preview-test:" + suffix,
    }
    return builder(**{key: value for key, value in proposed.items() if key in available})


def _exercise_echo_drift(package: object, result: object, ledger: Ledger) -> None:
    """Exercise a public Echo helper when the package intentionally exports one."""

    helper = None
    for name in (
        "validate_candidate_wording",
        "validate_echo_wording",
        "evaluate_echo_preservation",
        "run_echo_validation",
    ):
        candidate = getattr(package, name, None)
        if callable(candidate):
            helper = candidate
            break
    if helper is None:
        print("echo_drift_public_helper=not_exposed")
        return

    meaning = _value(result, "selected_meaning")
    wording = _value(result, "candidate_wording")
    original = str(_value(wording, "text", ""))
    if " not " in original:
        changed = original.replace(" not ", " ", 1)
    elif "does not" in original:
        changed = original.replace("does not", "does", 1)
    else:
        changed = original + " This added claim was not in the meaning."

    parameters = inspect.signature(helper).parameters
    values = {
        "meaning": meaning,
        "meaning_candidate": meaning,
        "selected_meaning": meaning,
        "wording": changed,
        "wording_text": changed,
        "candidate_wording": changed,
        "text": changed,
    }
    kwargs = {key: values[key] for key in parameters if key in values}
    try:
        echo = helper(**kwargs)
    except TypeError as error:
        ledger.check(False, "public Echo helper has an unsupported signature", error)
        return
    ledger.check(
        _status(echo) in {"REJECT", "REJECTED", "CONTAINED"},
        "deliberate wording drift rejected",
        _dict(echo),
    )
    ledger.check(
        _value(echo, "delivery_authorized", False) is False,
        "drift rejection grants no delivery",
        _dict(echo),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    sys.path.insert(0, str(repo))
    ledger = Ledger()

    import aiweb_language_core_bootstrap.meaning_compiler_preview as package
    from aiweb_language_core_bootstrap.meaning_compiler_preview import (
        build_rmc_context_record,
        build_rmc_context_snapshot,
        compile_meaning_preview,
        meaning_compiler_preview_boundary,
        validate_forge_seed_registry,
    )
    from aiweb_language_core_bootstrap.meaning_compiler_preview.registry import (
        forge_seed_registry,
    )

    # Exact source custody survives even when the bounded grammar cannot advance.
    exact_source = "  Café\r\nA\u0301  "
    exact = compile_meaning_preview(exact_source)
    exact_custody = _value(exact, "source_custody")
    ledger.check(_value(exact, "source_text") == exact_source, "exact source retained")
    ledger.check(
        _value(exact_custody, "source_sha256")
        == hashlib.sha256(exact_source.encode("utf-8")).hexdigest(),
        "exact UTF-8 source hash",
    )
    ledger.check(
        _value(exact_custody, "code_point_length") == len(exact_source),
        "exact code-point length",
    )
    ledger.check(
        _value(exact_custody, "utf8_byte_length") == len(exact_source.encode("utf-8")),
        "exact UTF-8 byte length",
    )
    ledger.check(_value(exact_custody, "source_preserved_exactly") is True, "custody preservation proof")
    for name in (
        "normalization_performed",
        "tokenization_performed",
        "model_token_stream_created",
        "subword_token_stream_created",
        "numeric_token_ids_created",
    ):
        ledger.check(_value(exact_custody, name) is False, "custody false " + name)

    # Source forms are exact spans, never a hidden model-token stream.
    source_forms = _sequence(exact, "source_forms")
    if source_forms:
        ordered = tuple(sorted(source_forms, key=lambda item: int(_value(item, "code_point_start", -1))))
        ledger.check(_value(ordered[0], "code_point_start") == 0, "source-form coverage starts at zero")
        ledger.check(_value(ordered[-1], "code_point_end") == len(exact_source), "source-form coverage reaches source end")
        for index, form in enumerate(ordered):
            start = int(_value(form, "code_point_start", -1))
            end = int(_value(form, "code_point_end", -1))
            ledger.check(_value(form, "exact_text") == exact_source[start:end], f"source form exact slice {index}")
            ledger.check(
                _value(form, "utf8_byte_start") == len(exact_source[:start].encode("utf-8"))
                and _value(form, "utf8_byte_end") == len(exact_source[:end].encode("utf-8")),
                f"source form exact UTF-8 coordinates {index}",
            )
            if index:
                ledger.check(
                    _value(ordered[index - 1], "code_point_end") == start,
                    f"source forms adjacent {index}",
                )

    nfc = compile_meaning_preview("é")
    nfd = compile_meaning_preview("e\u0301")
    ledger.check(
        _value(_value(nfc, "source_custody"), "source_sha256")
        != _value(_value(nfd, "source_custody"), "source_sha256"),
        "NFC and NFD source identities remain distinct",
    )

    # Accepted v0 fixtures exercise questions, requests, statements and composition.
    ready_sources = (
        "What does language core mean?",
        "What is RMC?",
        "Please inspect the manifest.",
        "Please audit the manifest.",
        "Can Forge report status?",
        "Forge uses RMC memory.",
        "Forge analyzes the artifact.",
        "Forge does not use vector memory.",
        "Forge is a system.",
        "Forge is an authority.",
        "Forge is not a vector memory.",
        "Forge is not an anomaly.",
        "Compare RMC memory and vector memory.",
        "Please begin the batch.",
        "Forge balances the budget.",
        "Please build the blueprint.",
        "Forge blocks the boundary.",
    )
    ready_results: dict[str, object] = {}
    for source in ready_sources:
        result = compile_meaning_preview(source)
        ready_results[source] = result
        ledger.check(_status(result) == "PREVIEW_READY", f"v0 fixture ready: {source}", _dict(result))
        selected = _value(result, "selected_meaning")
        wording = _value(result, "candidate_wording")
        echo = _value(result, "echo")
        ledger.check(selected is not None, f"selected preview meaning exists: {source}")
        ledger.check(wording is not None and bool(_value(wording, "text", "")), f"reverse wording exists: {source}")
        ledger.check(_enum_value(_value(echo, "status", "")) == "PASS", f"Echo passes: {source}", _dict(echo))
        ledger.check(_value(echo, "exact_signature_match") is True, f"Echo exact signature: {source}")
        ledger.check(_value(echo, "reparse_performed") is True, f"Echo reparses wording: {source}")
        ledger.check(_value(echo, "delivery_authorized") is False, f"Echo grants no delivery: {source}")
        ledger.check(_value(wording, "delivery_authorized") is False, f"wording grants no delivery: {source}")
        ledger.check(_value(selected, "selection_authority") is False, f"preview is not selection authority: {source}")

    # Definition requests must answer from the governed provisional registry,
    # not merely paraphrase the incoming question.  Echo admits only the exact
    # generated registry wording.
    definition_result = ready_results["What does language core mean?"]
    definition_wording = _value(definition_result, "candidate_wording")
    definition_concept = next(
        concept
        for concept in forge_seed_registry().concepts
        if concept.concept_key == "language_core"
    )
    definition_sense = next(
        sense
        for sense in forge_seed_registry().senses
        if sense.concept_ref == definition_concept.concept_id
    )
    expected_definition = (
        f"{definition_concept.preferred_label} means "
        f"{definition_concept.provisional_definition}."
    )
    ledger.check(
        _value(definition_wording, "text") == expected_definition,
        "definition request returns the governed provisional definition",
        _dict(definition_wording),
    )
    ledger.check(
        _value(definition_wording, "definition_concept_ref") == definition_concept.concept_id
        and _value(definition_wording, "definition_sense_ref") == definition_sense.sense_id,
        "definition wording carries exact registry grounding",
        _dict(definition_wording),
    )
    ledger.check(
        not str(_value(definition_wording, "text", "")).endswith("?"),
        "definition output is an answer rather than a rephrased question",
    )
    definition_answer_reparse = compile_meaning_preview(expected_definition)
    ledger.check(
        _status(definition_answer_reparse) == "PREVIEW_READY"
        and _enum_value(_value(_value(definition_answer_reparse, "echo"), "status", "")) == "PASS",
        "governed definition answer reparses and Echo-validates",
        _dict(definition_answer_reparse),
    )
    definition_drift = package.validate_candidate_wording(
        meaning_candidate=_value(definition_result, "selected_meaning"),
        wording_text=expected_definition.replace("provisional", "final", 1),
    )
    ledger.check(
        _status(definition_drift) == "REJECT",
        "Echo rejects a definition not exactly grounded in the registry",
        _dict(definition_drift),
    )

    # Reverse wording uses declared predicate morphology and article selection.
    for source, expected_wording in (
        ("Forge analyzes the artifact.", "Forge analyzes the artifact."),
        ("Forge balances the budget.", "Forge balances the budget."),
        ("Forge is an authority.", "Forge is an authority."),
        ("Forge is not an anomaly.", "Forge is not an anomaly."),
    ):
        ledger.check(
            _value(_value(ready_results[source], "candidate_wording"), "text")
            == expected_wording,
            f"governed morphology and articles: {source}",
            _dict(_value(ready_results[source], "candidate_wording")),
        )

    repeated_a = compile_meaning_preview("Please inspect the manifest.")
    repeated_b = compile_meaning_preview("Please inspect the manifest.")
    ledger.check(repeated_a == repeated_b, "deterministic record replay")
    ledger.check(_canonical(repeated_a) == _canonical(repeated_b), "deterministic canonical replay")
    ledger.check(_value(repeated_a, "result_id") == _value(repeated_b, "result_id"), "deterministic result identity")
    ledger.check(_value(_value(repeated_a, "receipt"), "deterministic") is True, "determinism receipt")
    ledger.check(bool(_sequence(repeated_a, "algebra_trace")), "symbolic algebra trace is visible")
    forbidden_stream_fields = {
        "tokens",
        "token_ids",
        "model_tokens",
        "subword_tokens",
        "vocabulary_ids",
        "embeddings",
        "vectors",
        "next_token",
    }
    ledger.check(
        forbidden_stream_fields.isdisjoint(_all_keys(repeated_a)),
        "result contains no model-token, embedding, or vector stream fields",
        sorted(forbidden_stream_fields.intersection(_all_keys(repeated_a))),
    )

    composed_source = "Compare RMC memory and vector memory."
    composed = ready_results[composed_source]
    composed_meaning = _value(composed, "selected_meaning")
    registry = forge_seed_registry()
    registry_errors = validate_forge_seed_registry(registry)
    ledger.check(not registry_errors, "installed registry passes integrity validation", registry_errors)
    ledger.check(
        all(concept.provisional for concept in registry.concepts)
        and all(sense.provisional for sense in registry.senses)
        and all(predicate.provisional for predicate in registry.predicates)
        and all(role.provisional for role in registry.roles),
        "every expanded registry entry remains provisional",
    )
    ledger.check(
        all(not concept.external_reference_authority for concept in registry.concepts)
        and all(not sense.external_reference_authority for sense in registry.senses),
        "expanded entries claim no external reference authority",
    )
    ledger.check(
        all(concept.provisional_definition.strip() for concept in registry.concepts)
        and all(sense.provisional_gloss.strip() for sense in registry.senses),
        "every concept and sense has bounded provisional semantic content",
    )
    ledger.check(
        {"forge", "language_core", "rmc_memory", "authority", "artifact", "manifest", "grammar", "resonance"}
        .issubset({concept.concept_key for concept in registry.concepts}),
        "registry covers the bounded operator-language foundation",
    )
    ledger.check(
        len({concept.concept_key for concept in registry.concepts}) == len(registry.concepts)
        and len({concept.concept_id for concept in registry.concepts}) == len(registry.concepts)
        and len({sense.sense_key for sense in registry.senses}) == len(registry.senses)
        and len({sense.sense_id for sense in registry.senses}) == len(registry.senses)
        and len({predicate.predicate_key for predicate in registry.predicates}) == len(registry.predicates)
        and len({predicate.predicate_id for predicate in registry.predicates}) == len(registry.predicates),
        "registry keys and stable record identities are unique",
    )
    duplicate_predicate_registry = replace(
        registry,
        predicates=registry.predicates + (registry.predicates[0],),
    )
    duplicate_predicate_errors = validate_forge_seed_registry(duplicate_predicate_registry)
    ledger.check(
        any(error.startswith("duplicate_predicate_key:") for error in duplicate_predicate_errors)
        and any(error.startswith("duplicate_predicate_id:") for error in duplicate_predicate_errors),
        "registry validation rejects duplicate predicate keys and identities",
        duplicate_predicate_errors,
    )
    duplicate_form_predicate = replace(
        registry.predicates[0],
        exact_surface_forms=(
            *registry.predicates[0].exact_surface_forms,
            registry.predicates[0].exact_surface_forms[0],
        ),
    )
    duplicate_form_registry = replace(
        registry,
        predicates=(duplicate_form_predicate, *registry.predicates[1:]),
    )
    duplicate_form_errors = validate_forge_seed_registry(duplicate_form_registry)
    ledger.check(
        any(error.startswith("duplicate_predicate_surface_form:") for error in duplicate_form_errors),
        "registry validation rejects duplicate predicate forms",
        duplicate_form_errors,
    )
    core_senses = tuple(
        sense
        for sense in registry.senses
        if ("core",) in {
            tuple(str(word).lower() for word in form)
            for form in sense.exact_surface_forms
        }
    )
    ledger.check(
        len(core_senses) == 2,
        "declared core polysemy remains explicit and validation-safe",
        tuple(sense.sense_key for sense in core_senses),
    )
    manifest_surface = ("manifest",)
    foreign_surface_index = next(
        index
        for index, sense in enumerate(registry.senses)
        if sense.sense_key == "authority_preview_sense"
    )
    foreign_surface_sense = replace(
        registry.senses[foreign_surface_index],
        exact_surface_forms=(
            *registry.senses[foreign_surface_index].exact_surface_forms,
            manifest_surface,
        ),
    )
    undeclared_polysemy_registry = replace(
        registry,
        senses=(
            *registry.senses[:foreign_surface_index],
            foreign_surface_sense,
            *registry.senses[foreign_surface_index + 1 :],
        ),
    )
    undeclared_polysemy_errors = validate_forge_seed_registry(
        undeclared_polysemy_registry
    )
    ledger.check(
        any(
            error.startswith("undeclared_polysemous_surface_form:manifest:")
            for error in undeclared_polysemy_errors
        ),
        "registry validation rejects undeclared duplicate sense forms",
        undeclared_polysemy_errors,
    )
    declared_surface_phrases = {
        " ".join(form)
        for sense in registry.senses
        for form in sense.exact_surface_forms
    }
    declared_surface_phrases.update(
        form
        for predicate in registry.predicates
        for form in predicate.exact_surface_forms
    )
    ledger.check(
        composed_source.rstrip(".").lower() not in {
            phrase.lower() for phrase in declared_surface_phrases
        },
        "composed fixture is not a memorized whole-sentence registry entry",
    )
    ledger.check(len(_sequence(composed_meaning, "roles")) >= 2, "unseen composition binds multiple semantic roles")
    ledger.check(len(_sequence(composed, "algebra_trace")) >= 2, "unseen composition exposes multi-step algebra")

    # Polysemy must hold both Forge-owned senses until exact context distinguishes one.
    ambiguous_source = "What does core mean?"
    ambiguous = compile_meaning_preview(ambiguous_source)
    alternatives = _sequence(ambiguous, "meaning_candidates")
    ledger.check(_status(ambiguous) == "HELD", "polysemy held", _dict(ambiguous))
    ledger.check(len(alternatives) >= 2, "polysemy alternatives preserved", len(alternatives))
    ledger.check(_value(ambiguous, "selected_meaning") is None, "polysemy not guessed")
    ledger.check(_value(ambiguous, "candidate_wording") is None, "polysemy not rendered as selected answer")
    ledger.check(_enum_value(_value(_value(ambiguous, "echo"), "status", "")) == "NOT_RUN", "polysemy stops before Echo")
    ledger.check(all(_value(item, "selection_authority") is False for item in alternatives), "alternatives have no selection authority")

    # Exact unknowns and misspellings remain unsupported instead of being corrected.
    for source, unknown_text in (
        ("What does bank mean?", "bank"),
        ("What does languge core mean?", "languge"),
    ):
        held = compile_meaning_preview(source)
        unknowns = tuple(
            item
            for item in _sequence(held, "lexical_candidates")
            if _enum_value(_value(item, "kind", "")) == "unknown"
            or _value(item, "known") is False
        )
        ledger.check(_status(held) in {"HELD", "UNSUPPORTED"}, f"unknown held: {source}", _dict(held))
        ledger.check(any(str(_value(item, "exact_text", "")).lower() == unknown_text for item in unknowns), f"exact unknown span retained: {unknown_text}", tuple(_dict(item) for item in unknowns))
        ledger.check(_value(held, "selected_meaning") is None, f"unknown receives no selected meaning: {source}")
        ledger.check(_value(held, "candidate_wording") is None, f"unknown receives no wording: {source}")
    unsupported = compile_meaning_preview("purple quickly maybe")
    ledger.check(_status(unsupported) in {"HELD", "UNSUPPORTED"}, "unsupported grammar held")
    ledger.check(_value(unsupported, "selected_meaning") is None, "unsupported grammar not guessed")

    # Separate known words do not silently become an undeclared compound or
    # adjective+noun relation.  Composition remains held until a typed rule is
    # installed for it.
    unadmitted_composition = compile_meaning_preview(
        "Please inspect the active manifest."
    )
    composition_gate_reasons = tuple(
        str(reason)
        for candidate in _sequence(unadmitted_composition, "meaning_candidates")
        for gate in _sequence(candidate, "gates")
        for reason in _sequence(gate, "reasons")
    )
    ledger.check(
        _status(unadmitted_composition) == "HELD",
        "unadmitted adjective-noun composition is held",
        _dict(unadmitted_composition),
    )
    ledger.check(
        "unadmitted_compositional_phrase:object" in composition_gate_reasons,
        "composition hold has an explicit symbolic gate reason",
        composition_gate_reasons,
    )
    ledger.check(
        _value(unadmitted_composition, "selected_meaning") is None
        and _value(unadmitted_composition, "candidate_wording") is None,
        "unadmitted composition is neither selected nor worded",
    )

    # Every visible non-whitespace source form must participate in the hold
    # decision; numbers, symbols, and speech-act punctuation cannot disappear.
    for source, exact_hold in (
        ("Please inspect 999 the manifest.", "999"),
        ("Please inspect the ⟁ manifest.", "⟁"),
        ("Forge is a system?", "?"),
        ("Forge uses RMC memory?", "?"),
    ):
        held = compile_meaning_preview(source)
        exact_unknowns = tuple(
            str(_value(item, "exact_text", ""))
            for item in _sequence(held, "lexical_candidates")
            if _value(item, "known") is False
        )
        ledger.check(_status(held) == "HELD", f"non-word structure held: {source}", _dict(held))
        ledger.check(exact_hold in exact_unknowns, f"exact non-word hold retained: {source}", exact_unknowns)
        ledger.check(_value(held, "selected_meaning") is None, f"non-word hold cannot select: {source}")
        ledger.check(_value(held, "candidate_wording") is None, f"non-word hold cannot render: {source}")

    negative = ready_results["Forge does not use vector memory."]
    negative_meaning = _value(negative, "selected_meaning")
    ledger.check(_value(negative_meaning, "negated") is True, "negation retained in meaning")
    ledger.check("not" in str(_value(_value(negative, "candidate_wording"), "text", "")).lower(), "negation retained in reverse wording")
    ledger.check(
        _value(_value(negative, "echo"), "reparsed_semantic_signature")
        == _value(negative_meaning, "semantic_signature"),
        "negation survives reverse-wording reparse",
    )
    _exercise_echo_drift(package, negative, ledger)
    inspect_ready = ready_results["Please inspect the manifest."]
    invented = package.validate_candidate_wording(
        meaning_candidate=_value(inspect_ready, "selected_meaning"),
        wording_text="Please inspect the manifest 999 ⟁.",
    )
    ledger.check(_status(invented) == "REJECT", "Echo rejects invented number and symbol", _dict(invented))
    ledger.check(_value(invented, "exact_signature_match") is False, "invented non-word structure cannot Echo-match")

    for invalid_context_fields in (
        {"lifecycle_state": "revoked"},
        {"phase_refs": ("phase:not-admitted-v0",)},
        {"correction_refs": ("correction:not-admitted-v0",)},
        {"echo_receipt_refs": ("echo:not-admitted-v0",)},
    ):
        try:
            build_rmc_context_record(**invalid_context_fields)
            context_rejected = False
        except (TypeError, ValueError):
            context_rejected = True
        ledger.check(context_rejected, "ineligible RMC control record rejected: " + repr(invalid_context_fields))

    # RMC exact-relation context may resolve the held pair without raw-word scoring.
    if alternatives:
        target = alternatives[0]
        unique_refs = _unique_candidate_refs(target, alternatives)
        target_contract = package.semantic_contract_for_candidate(
            target,
            _sequence(ambiguous, "frame_candidates"),
        )
        unique_refs["semantic_contract_refs"] = (
            _value(target_contract, "semantic_contract_id"),
        )
        ledger.check(any(unique_refs.values()), "ambiguous candidates expose distinguishable structured references", unique_refs)
        support = _build_context_record(build_rmc_context_record, unique_refs, "support")
        inert = _build_context_record(
            build_rmc_context_record,
            {
                "concept_refs": ("concept:meaning-preview-inert",),
                "relation_refs": ("relation:meaning-preview-inert",),
                "ancestry_refs": ("ancestry:meaning-preview-inert",),
            },
            "inert",
        )
        snapshot_a = build_rmc_context_snapshot(records=(support, inert))
        snapshot_b = build_rmc_context_snapshot(records=(inert, support))
        ledger.check(snapshot_a == snapshot_b, "RMC snapshot canonicalizes record order")
        ledger.check(_value(snapshot_a, "read_only") is True, "RMC snapshot read only")
        ledger.check(_value(snapshot_a, "exact_reference_resonance_only") is True, "RMC exact-reference resonance only")
        for name in (
            "filesystem_access_performed",
            "raw_word_overlap_used",
            "embedding_used",
            "vector_used",
            "similarity_scoring_used",
        ):
            ledger.check(_value(snapshot_a, name) is False, "RMC snapshot false " + name)

        contextual_a = compile_meaning_preview(ambiguous_source, rmc_snapshot=snapshot_a)
        contextual_b = compile_meaning_preview(ambiguous_source, rmc_snapshot=snapshot_b)
        ledger.check(contextual_a == contextual_b, "RMC input order cannot change meaning result")
        ledger.check(_status(contextual_a) == "PREVIEW_READY", "exact RMC relation resolves bounded ambiguity", _dict(contextual_a))
        selected = _value(contextual_a, "selected_meaning")
        ledger.check(
            _value(selected, "meaning_candidate_id") == _value(target, "meaning_candidate_id"),
            "RMC selects only the exactly supported candidate",
            _dict(contextual_a),
        )
        context = _value(contextual_a, "rmc_context")
        ledger.check(_value(context, "context_used_for_selection") is True, "RMC selection influence visible")
        ledger.check(_value(context, "memory_write_performed") is False, "RMC evaluation performs no write")
        ledger.check(
            any(_value(item, "used_for_selection") is True for item in _sequence(context, "resonances")),
            "exact supporting resonance identified",
            _dict(context),
        )

        tampered_support = replace(support, record_id="rmc-context-record:tampered")
        tampered_snapshot = replace(snapshot_a, records=(tampered_support, inert))
        tampered = compile_meaning_preview(ambiguous_source, rmc_snapshot=tampered_snapshot)
        ledger.check(_status(tampered) in {"HELD", "INVALID"}, "tampered RMC context fails closed", _dict(tampered))
        ledger.check(_value(tampered, "selected_meaning") is None, "tampered RMC context cannot select")

        contradictory_snapshot = snapshot_a.to_dict()
        contradictory_snapshot["exact_reference_resonance_only"] = False
        contradictory = compile_meaning_preview(
            ambiguous_source,
            rmc_snapshot=contradictory_snapshot,
        )
        ledger.check(_status(contradictory) in {"HELD", "INVALID"}, "contradictory RMC metadata fails closed", _dict(contradictory))
        ledger.check(_value(contradictory, "selected_meaning") is None, "contradictory RMC metadata cannot select")

    # Every result advertises the same zero-authority boundary.
    boundary = meaning_compiler_preview_boundary()
    ledger.check(_value(boundary, "preview_only") is True, "preview-only boundary")
    for name in (
        "external_reference_authority",
        "glyph_reference_authority",
        "google_drive_reference_authority",
        "panini_reference_authority",
        "chomsky_reference_authority",
        "normalization_performed",
        "tokenization_performed",
        "model_token_stream_created",
        "subword_token_stream_created",
        "numeric_token_ids_created",
        "model_called",
        "embedding_used",
        "vector_used",
        "similarity_scoring_used",
        "filesystem_read_performed",
        "filesystem_write_performed",
        "network_access_performed",
        "environment_access_performed",
        "memory_read_performed",
        "memory_write_performed",
        "route_registration_performed",
        "tool_routing_performed",
        "action_performed",
        "delivery_performed",
    ):
        ledger.check(_value(boundary, name) is False, "boundary false " + name)
    for result in tuple(ready_results.values()) + (ambiguous, unsupported):
        ledger.check(_dict(_value(result, "boundary")) == _dict(boundary), "result carries exact boundary", _status(result))
        receipt = _value(result, "receipt")
        ledger.check(_value(receipt, "writes_performed") is False, "receipt records zero writes")
        ledger.check(_value(receipt, "action_performed") is False, "receipt records zero action")
        ledger.check(_value(receipt, "delivery_performed") is False, "receipt records zero delivery")

    # Imported runtime must still work when every external effect is booby-trapped.
    with ExitStack() as stack:
        stack.enter_context(patch.object(builtins, "open", _forbidden))
        stack.enter_context(patch.object(Path, "open", _forbidden))
        stack.enter_context(patch.object(Path, "read_text", _forbidden))
        stack.enter_context(patch.object(Path, "read_bytes", _forbidden))
        stack.enter_context(patch.object(Path, "write_text", _forbidden))
        stack.enter_context(patch.object(Path, "write_bytes", _forbidden))
        stack.enter_context(patch.object(socket, "socket", _forbidden))
        stack.enter_context(patch.object(socket, "create_connection", _forbidden))
        stack.enter_context(patch.object(subprocess, "run", _forbidden))
        stack.enter_context(patch.object(subprocess, "Popen", _forbidden))
        stack.enter_context(patch.object(urllib.request, "urlopen", _forbidden))
        stack.enter_context(patch.object(os, "getenv", _forbidden))
        trapped = compile_meaning_preview("Please inspect the manifest.")
    ledger.check(_status(trapped) == "PREVIEW_READY", "pure preview runs under external-effect traps")

    try:
        trapped.status = "HELD"  # type: ignore[misc]
        immutable = False
    except (FrozenInstanceError, AttributeError, TypeError):
        immutable = True
    ledger.check(immutable, "preview result immutable")

    print("AI.WEB MEANING COMPILER PREVIEW BEHAVIOR")
    print(f"checks={ledger.checks}")
    print(f"failures={len(ledger.failures)}")
    print("exact_source_custody=1")
    print("normalization_and_model_token_stream=0")
    print("polysemy_and_unknown_guessing=0")
    print("rmc_exact_relation_read_only=1")
    print("reverse_wording_echo=1")
    print("model_embedding_vector_similarity=0")
    print("filesystem_network_write_tool_action_delivery=0")
    print("RESULT=" + ("PASS" if not ledger.failures else "FAIL"))
    return 0 if not ledger.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
