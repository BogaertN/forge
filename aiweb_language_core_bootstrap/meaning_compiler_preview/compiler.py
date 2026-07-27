"""Forge-owned deterministic word-to-meaning compiler preview.

This is a deliberately small v0 language.  It preserves source characters,
projects exact form spans, composes provisional predicate/role structures,
applies four explicit verbal-cognition gates, optionally consults a validated
structured RMC snapshot, derives candidate wording, and reparses that wording
for an Echo comparison.  It performs no external lookup or side effect.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product
from typing import Final

from ..input_event_custody import (
    InputCustodyStatus,
    build_input_custody_limits,
    capture_input_event,
)
from ..schema import stable_record_id
from .character_scan import build_source_forms
from .registry import forge_seed_registry
from .rmc_context import (
    build_rmc_context_snapshot,
    coerce_rmc_context_snapshot,
    evaluate_rmc_context,
)
from .schema import (
    AlgebraTraceStep,
    CandidateWording,
    EchoResult,
    EchoStatus,
    FrameCandidate,
    GateResult,
    LexicalCandidate,
    LexicalCandidateKind,
    MEANING_COMPILER_PREVIEW_SCHEMA_VERSION,
    MeaningCandidate,
    MeaningCompilerPreviewBoundary,
    MeaningCompilerPreviewResult,
    MeaningRole,
    PreviewReceipt,
    PreviewStatus,
    RmcCandidateResonance,
    RmcContextEvaluation,
    RoleBinding,
    SourceCustodySummary,
    SourceForm,
    SourceFormKind,
    StageResult,
)


MAX_SOURCE_CODE_POINTS: Final[int] = 8_192
MAX_SOURCE_UTF8_BYTES: Final[int] = 16_384
MAX_MEANING_CANDIDATES: Final[int] = 32

_FUNCTION_WORDS: Final[frozenset[str]] = frozenset(
    {
        "a",
        "an",
        "and",
        "can",
        "could",
        "did",
        "do",
        "does",
        "not",
        "please",
        "the",
        "what",
        "will",
        "would",
        "you",
    }
)
_DETERMINERS: Final[frozenset[str]] = frozenset({"a", "an", "the"})
_MODALS: Final[frozenset[str]] = frozenset({"can", "could", "will", "would"})
_AUXILIARY_DO: Final[frozenset[str]] = frozenset({"do", "does", "did"})


@dataclass(frozen=True, slots=True)
class _InwardResult:
    source_custody: SourceCustodySummary
    source_forms: tuple[SourceForm, ...]
    lexical_candidates: tuple[LexicalCandidate, ...]
    frame_candidates: tuple[FrameCandidate, ...]
    meaning_candidates: tuple[MeaningCandidate, ...]
    algebra_trace: tuple[AlgebraTraceStep, ...]
    capture_valid: bool
    structural_progression_allowed: bool
    reasons: tuple[str, ...]


def _ascii_key(text: str) -> str:
    """Return an ASCII case key without changing the source record."""

    return "".join(
        chr(ord(character) + 32) if "A" <= character <= "Z" else character
        for character in text
    )


def _boundary_body() -> dict[str, object]:
    return {
        "preview_version": MEANING_COMPILER_PREVIEW_SCHEMA_VERSION,
        "preview_only": True,
        "forge_owned_provisional_registry": True,
        "reference_only_materials": (
            "imported_rsoc_glyph_packet",
            "google_drive_language_documents",
            "panini_research",
            "chomsky_research",
        ),
        "external_reference_authority": False,
        "glyph_reference_authority": False,
        "google_drive_reference_authority": False,
        "panini_reference_authority": False,
        "chomsky_reference_authority": False,
        "normalization_performed": False,
        "tokenization_performed": False,
        "model_token_stream_created": False,
        "subword_token_stream_created": False,
        "numeric_token_ids_created": False,
        "model_called": False,
        "embedding_used": False,
        "vector_used": False,
        "similarity_scoring_used": False,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "network_access_performed": False,
        "environment_access_performed": False,
        "memory_read_performed": False,
        "memory_write_performed": False,
        "route_registration_performed": False,
        "tool_routing_performed": False,
        "action_performed": False,
        "delivery_performed": False,
    }


def meaning_compiler_preview_boundary() -> MeaningCompilerPreviewBoundary:
    body = _boundary_body()
    return MeaningCompilerPreviewBoundary(
        boundary_id=stable_record_id("meaning_compiler_preview_boundary", body),
        **body,
    )


def _custody_summary(capture: object) -> SourceCustodySummary:
    event = getattr(capture, "event", None)
    body = {
        "custody_result_id": getattr(capture, "result_id", ""),
        "input_event_id": event.input_event_id if event is not None else "",
        "custody_status": getattr(getattr(capture, "status", ""), "value", str(getattr(capture, "status", ""))),
        "reason_code": getattr(capture, "reason_code", ""),
        "source_sha256": getattr(capture, "observed_source_sha256", ""),
        "code_point_length": getattr(capture, "observed_code_point_length", None),
        "utf8_byte_length": getattr(capture, "observed_utf8_byte_length", None),
        "source_preserved_exactly": bool(event and event.source_preserved_exactly),
        "structural_progression_allowed": bool(
            getattr(capture, "structural_progression_allowed", False)
        ),
        "normalization_performed": False,
        "tokenization_performed": False,
        "model_token_stream_created": False,
        "subword_token_stream_created": False,
        "numeric_token_ids_created": False,
        "conditions": tuple(
            condition.code.value for condition in getattr(capture, "conditions", ())
        ),
    }
    return SourceCustodySummary(**body)


def _word_forms(forms: tuple[SourceForm, ...]) -> tuple[SourceForm, ...]:
    return tuple(form for form in forms if form.kind is SourceFormKind.WORD)


def _source_phrase(
    source_text: str,
    words: tuple[SourceForm, ...],
    ordinals: tuple[int, ...],
) -> str:
    if not ordinals:
        return ""
    return source_text[
        words[ordinals[0]].code_point_start : words[ordinals[-1]].code_point_end
    ]


def _surface_is_contiguous(
    source_text: str,
    words: tuple[SourceForm, ...],
    start: int,
    length: int,
) -> bool:
    if length <= 1:
        return True
    for ordinal in range(start, start + length - 1):
        gap = source_text[
            words[ordinal].code_point_end : words[ordinal + 1].code_point_start
        ]
        if not gap or not gap.isspace():
            return False
    return True


def _lexical_candidate(
    *,
    kind: LexicalCandidateKind,
    exact_text: str,
    forms: tuple[SourceForm, ...],
    ordinals: tuple[int, ...],
    ambiguity_group: str = "",
    concept_ref: str = "",
    sense_ref: str = "",
    predicate_ref: str = "",
    function_key: str = "",
    known: bool,
) -> LexicalCandidate:
    body = {
        "kind": kind,
        "exact_text": exact_text,
        "source_form_refs": tuple(forms[index].source_form_id for index in ordinals),
        "word_ordinals": ordinals,
        "ambiguity_group": ambiguity_group,
        "concept_ref": concept_ref,
        "sense_ref": sense_ref,
        "predicate_ref": predicate_ref,
        "function_key": function_key,
        "known": known,
        "provisional": True,
    }
    return LexicalCandidate(
        lexical_candidate_id=stable_record_id("lexical_candidate", body),
        **body,
    )


def _build_lexical_candidates(
    source_text: str,
    words: tuple[SourceForm, ...],
) -> tuple[LexicalCandidate, ...]:
    registry = forge_seed_registry()
    keys = tuple(_ascii_key(word.exact_text) for word in words)
    candidates: list[LexicalCandidate] = []
    covered: set[int] = set()

    for ordinal, key in enumerate(keys):
        if key in _FUNCTION_WORDS:
            candidates.append(
                _lexical_candidate(
                    kind=LexicalCandidateKind.FUNCTION,
                    exact_text=words[ordinal].exact_text,
                    forms=words,
                    ordinals=(ordinal,),
                    function_key=key,
                    known=True,
                )
            )
            covered.add(ordinal)

    for predicate in registry.predicates:
        declared = {_ascii_key(form) for form in predicate.exact_surface_forms}
        for ordinal, key in enumerate(keys):
            if key not in declared:
                continue
            candidates.append(
                _lexical_candidate(
                    kind=LexicalCandidateKind.PREDICATE,
                    exact_text=words[ordinal].exact_text,
                    forms=words,
                    ordinals=(ordinal,),
                    predicate_ref=predicate.predicate_id,
                    known=True,
                )
            )
            covered.add(ordinal)

    for sense in registry.senses:
        for surface in sense.exact_surface_forms:
            surface_keys = tuple(_ascii_key(item) for item in surface)
            length = len(surface_keys)
            for start in range(0, len(keys) - length + 1):
                if keys[start : start + length] != surface_keys:
                    continue
                if not _surface_is_contiguous(source_text, words, start, length):
                    continue
                ordinals = tuple(range(start, start + length))
                candidates.append(
                    _lexical_candidate(
                        kind=LexicalCandidateKind.CONCEPT_SENSE,
                        exact_text=_source_phrase(source_text, words, ordinals),
                        forms=words,
                        ordinals=ordinals,
                        ambiguity_group=f"source-words:{start}:{start + length}",
                        concept_ref=sense.concept_ref,
                        sense_ref=sense.sense_id,
                        known=True,
                    )
                )
                covered.update(ordinals)

    for ordinal, word in enumerate(words):
        if ordinal in covered:
            continue
        candidates.append(
            _lexical_candidate(
                kind=LexicalCandidateKind.UNKNOWN,
                exact_text=word.exact_text,
                forms=words,
                ordinals=(ordinal,),
                ambiguity_group=f"unknown-source-word:{ordinal}",
                known=False,
            )
        )
    # Declared spelling variants can collapse to the same ASCII lookup key.
    # Keep one evidence record per stable identity so the receipt never
    # overstates how many lexical alternatives were actually proposed.
    unique = {item.lexical_candidate_id: item for item in candidates}
    return tuple(sorted(unique.values(), key=lambda item: item.lexical_candidate_id))


def _unsupported_source_form_candidate(
    form: SourceForm,
    reason: str,
) -> LexicalCandidate:
    body = {
        "kind": LexicalCandidateKind.UNKNOWN,
        "exact_text": form.exact_text,
        "source_form_refs": (form.source_form_id,),
        "word_ordinals": (),
        "ambiguity_group": f"unsupported-source-form:{reason}:{form.code_point_start}",
        "concept_ref": "",
        "sense_ref": "",
        "predicate_ref": "",
        "function_key": "",
        "known": False,
        "provisional": True,
    }
    return LexicalCandidate(
        lexical_candidate_id=stable_record_id("lexical_candidate", body),
        **body,
    )


def _structural_source_holds(
    forms: tuple[SourceForm, ...],
    frames: tuple[FrameCandidate, ...],
) -> tuple[LexicalCandidate, ...]:
    """Return exact non-word forms that the admitted v0 grammar cannot cover."""

    visible = tuple(
        form for form in forms if form.kind is not SourceFormKind.WHITESPACE
    )
    terminal_id = visible[-1].source_form_id if visible else ""
    expected_terminal: frozenset[str] = frozenset()
    if len(frames) == 1:
        expected_terminal = (
            frozenset({"?"})
            if frames[0].frame_key in {"definition_question", "modal_request"}
            else frozenset({"."})
        )
    held: list[LexicalCandidate] = []
    for form in forms:
        reason = ""
        if form.kind is SourceFormKind.NUMBER:
            reason = "number_not_admitted_by_v0_grammar"
        elif form.kind is SourceFormKind.SYMBOL:
            reason = "symbol_not_admitted_by_v0_grammar"
        elif form.kind is SourceFormKind.PUNCTUATION:
            if (
                form.source_form_id != terminal_id
                or form.exact_text not in expected_terminal
            ):
                reason = "punctuation_not_admitted_for_derived_speech_act"
        if reason:
            held.append(_unsupported_source_form_candidate(form, reason))
    return tuple(sorted(held, key=lambda item: item.lexical_candidate_id))


def _predicate_by_key(key: str):
    return next(
        predicate
        for predicate in forge_seed_registry().predicates
        if predicate.predicate_key == key
    )


def _predicate_key_for_word(key: str) -> str | None:
    for predicate in forge_seed_registry().predicates:
        if key in {_ascii_key(form) for form in predicate.exact_surface_forms}:
            return predicate.predicate_key
    return None


def _binding(
    role_key: str,
    raw_ordinals: tuple[int, ...],
    source_text: str,
    words: tuple[SourceForm, ...],
) -> RoleBinding:
    ordinals = list(raw_ordinals)
    while ordinals and _ascii_key(words[ordinals[0]].exact_text) in _DETERMINERS:
        ordinals.pop(0)
    while ordinals and _ascii_key(words[ordinals[-1]].exact_text) in _DETERMINERS:
        ordinals.pop()
    final = tuple(ordinals)
    body = {
        "role_key": role_key,
        "source_form_refs": tuple(words[index].source_form_id for index in final),
        "word_ordinals": final,
        "exact_text": _source_phrase(source_text, words, final),
    }
    return RoleBinding(
        binding_id=stable_record_id("role_binding", body),
        **body,
    )


def _frame(
    *,
    frame_key: str,
    speech_act: str,
    purport: str,
    predicate_key: str,
    negated: bool,
    bindings: tuple[RoleBinding, ...],
    grammar_rule_id: str,
) -> FrameCandidate:
    predicate = _predicate_by_key(predicate_key)
    complete = bool(bindings) and all(binding.word_ordinals for binding in bindings)
    reasons = () if complete else ("required_role_source_missing",)
    body = {
        "frame_key": frame_key,
        "speech_act": speech_act,
        "purport": purport,
        "predicate_ref": predicate.predicate_id,
        "predicate_key": predicate_key,
        "negated": negated,
        "role_bindings": bindings,
        "grammar_rule_id": grammar_rule_id,
        "complete": complete,
        "reasons": reasons,
    }
    return FrameCandidate(
        frame_candidate_id=stable_record_id("frame_candidate", body),
        **body,
    )


def _build_frame_candidates(
    source_text: str,
    words: tuple[SourceForm, ...],
) -> tuple[FrameCandidate, ...]:
    keys = tuple(_ascii_key(word.exact_text) for word in words)
    if not keys:
        return ()

    # Definition questions share one meaning relation even when externalized
    # as either "what is X" or "what does X mean".
    if len(keys) >= 4 and keys[0] == "what" and keys[1] in _AUXILIARY_DO and keys[-1] in {"mean", "means"}:
        binding = _binding("definition_target", tuple(range(2, len(keys) - 1)), source_text, words)
        return (_frame(
            frame_key="definition_question",
            speech_act="definition_request",
            purport="request_provisional_definition",
            predicate_key="mean",
            negated=False,
            bindings=(binding,),
            grammar_rule_id="FORGE-GRAMMAR-V0-DEFINITION-DO",
        ),)
    if len(keys) >= 3 and keys[0] == "what" and keys[1] in {"is", "are", "was", "were"}:
        binding = _binding("definition_target", tuple(range(2, len(keys))), source_text, words)
        return (_frame(
            frame_key="definition_question",
            speech_act="definition_request",
            purport="request_provisional_definition",
            predicate_key="mean",
            negated=False,
            bindings=(binding,),
            grammar_rule_id="FORGE-GRAMMAR-V0-DEFINITION-COPULA",
        ),)

    if keys[0] == "compare":
        try:
            conjunction = keys.index("and", 1)
        except ValueError:
            conjunction = -1
        left = _binding("comparison_left", tuple(range(1, max(1, conjunction))), source_text, words)
        right = _binding(
            "comparison_right",
            tuple(range(conjunction + 1, len(keys))) if conjunction >= 0 else (),
            source_text,
            words,
        )
        return (_frame(
            frame_key="comparison_request",
            speech_act="comparison_request",
            purport="request_bounded_comparison",
            predicate_key="compare",
            negated=False,
            bindings=(left, right),
            grammar_rule_id="FORGE-GRAMMAR-V0-COMPARE",
        ),)

    start = 1 if keys[0] == "please" else 0
    first_predicate = _predicate_key_for_word(keys[start]) if start < len(keys) else None
    if first_predicate and first_predicate not in {"be", "mean", "compare"}:
        object_binding = _binding("object", tuple(range(start + 1, len(keys))), source_text, words)
        return (_frame(
            frame_key="imperative_request",
            speech_act="request",
            purport="request_read_only_preview",
            predicate_key=first_predicate,
            negated=False,
            bindings=(object_binding,),
            grammar_rule_id="FORGE-GRAMMAR-V0-IMPERATIVE",
        ),)

    if keys[0] in _MODALS:
        predicate_index = next(
            (
                index
                for index in range(1, len(keys))
                if _predicate_key_for_word(keys[index]) not in {None, "be", "mean"}
            ),
            -1,
        )
        if predicate_index >= 0:
            predicate_key = _predicate_key_for_word(keys[predicate_index])
            assert predicate_key is not None
            actor = _binding("actor", tuple(range(1, predicate_index)), source_text, words)
            object_binding = _binding("object", tuple(range(predicate_index + 1, len(keys))), source_text, words)
            return (_frame(
                frame_key="modal_request",
                speech_act="request",
                purport="request_read_only_preview",
                predicate_key=predicate_key,
                negated=False,
                bindings=(actor, object_binding),
                grammar_rule_id="FORGE-GRAMMAR-V0-MODAL",
            ),)

    for auxiliary_index in range(1, len(keys) - 2):
        if keys[auxiliary_index] not in _AUXILIARY_DO or keys[auxiliary_index + 1] != "not":
            continue
        predicate_key = _predicate_key_for_word(keys[auxiliary_index + 2])
        if predicate_key in {None, "be", "mean"}:
            continue
        actor = _binding("actor", tuple(range(0, auxiliary_index)), source_text, words)
        object_binding = _binding("object", tuple(range(auxiliary_index + 3, len(keys))), source_text, words)
        return (_frame(
            frame_key="negative_clause",
            speech_act="statement",
            purport="assert_provisional_relation",
            predicate_key=predicate_key,
            negated=True,
            bindings=(actor, object_binding),
            grammar_rule_id="FORGE-GRAMMAR-V0-NEGATIVE-DO",
        ),)

    for predicate_index, key in enumerate(keys[1:], start=1):
        if key not in {"am", "is", "are", "was", "were", "be"}:
            continue
        negated = predicate_index + 1 < len(keys) and keys[predicate_index + 1] == "not"
        object_start = predicate_index + (2 if negated else 1)
        subject = _binding("subject", tuple(range(0, predicate_index)), source_text, words)
        object_binding = _binding("object", tuple(range(object_start, len(keys))), source_text, words)
        return (_frame(
            frame_key="copula_clause",
            speech_act="statement",
            purport="assert_provisional_class_relation",
            predicate_key="be",
            negated=negated,
            bindings=(subject, object_binding),
            grammar_rule_id="FORGE-GRAMMAR-V0-COPULA",
        ),)

    for predicate_index in range(1, len(keys)):
        predicate_key = _predicate_key_for_word(keys[predicate_index])
        if predicate_key in {None, "be", "mean", "compare"}:
            continue
        actor = _binding("actor", tuple(range(0, predicate_index)), source_text, words)
        object_binding = _binding("object", tuple(range(predicate_index + 1, len(keys))), source_text, words)
        return (_frame(
            frame_key="positive_clause",
            speech_act="statement",
            purport="assert_provisional_relation",
            predicate_key=predicate_key,
            negated=False,
            bindings=(actor, object_binding),
            grammar_rule_id="FORGE-GRAMMAR-V0-POSITIVE",
        ),)
    return ()


def _matching_senses(
    binding: RoleBinding,
    words: tuple[SourceForm, ...],
    source_text: str,
):
    keys = tuple(_ascii_key(words[index].exact_text) for index in binding.word_ordinals)
    if len(binding.word_ordinals) > 1:
        if any(
            right != left + 1
            for left, right in zip(binding.word_ordinals, binding.word_ordinals[1:])
        ):
            return ()
        if not _surface_is_contiguous(
            source_text,
            words,
            binding.word_ordinals[0],
            len(binding.word_ordinals),
        ):
            return ()
    matches = []
    for sense in forge_seed_registry().senses:
        if any(keys == tuple(_ascii_key(item) for item in surface) for surface in sense.exact_surface_forms):
            matches.append(sense)
    return tuple(sorted(matches, key=lambda item: item.sense_id))


def _gate(
    gate_name: str,
    passed: bool,
    rule_id: str,
    reasons: tuple[str, ...],
) -> GateResult:
    body = {
        "gate_name": gate_name,
        "passed": passed,
        "rule_id": rule_id,
        "reasons": reasons,
    }
    return GateResult(
        gate_id=stable_record_id("meaning_gate", body),
        **body,
    )


def _semantic_signature(
    frame: FrameCandidate,
    roles: tuple[MeaningRole, ...],
) -> str:
    body = {
        "speech_act": frame.speech_act,
        "purport": frame.purport,
        "predicate_key": frame.predicate_key,
        "negated": frame.negated,
        "roles": tuple(
            sorted(
                (role.role_key, role.concept_ref, role.sense_ref)
                for role in roles
            )
        ),
    }
    return stable_record_id("semantic_signature", body)


def _build_meaning_candidates(
    frames: tuple[FrameCandidate, ...],
    lexical: tuple[LexicalCandidate, ...],
    words: tuple[SourceForm, ...],
    source_text: str,
    input_event_id: str,
) -> tuple[MeaningCandidate, ...]:
    unknown_refs = tuple(
        candidate.source_form_refs[0]
        for candidate in lexical
        if candidate.kind is LexicalCandidateKind.UNKNOWN
        and candidate.source_form_refs
    )
    known_word_ordinals = {
        ordinal
        for candidate in lexical
        if candidate.known
        for ordinal in candidate.word_ordinals
    }
    registry = forge_seed_registry()
    concepts_by_id = {concept.concept_id: concept for concept in registry.concepts}
    meanings: list[MeaningCandidate] = []

    for frame in frames:
        sense_options = tuple(
            _matching_senses(binding, words, source_text)
            for binding in frame.role_bindings
        )
        product_options = tuple(options if options else (None,) for options in sense_options)
        for choice in product(*product_options):
            if len(meanings) >= MAX_MEANING_CANDIDATES:
                break
            roles = tuple(
                MeaningRole(
                    role_key=binding.role_key,
                    concept_ref=sense.concept_ref if sense is not None else "",
                    sense_ref=sense.sense_id if sense is not None else "",
                    source_form_refs=binding.source_form_refs,
                )
                for binding, sense in zip(frame.role_bindings, choice)
            )
            required = set(_predicate_by_key(frame.predicate_key).required_roles)
            bound = {role.role_key for role in roles if role.concept_ref}
            expectancy_ok = frame.complete and required.issubset(bound)

            congruity_ok = all(role.concept_ref and role.sense_ref for role in roles)
            if congruity_ok and frame.predicate_key in {"use", "remember", "store", "retrieve"}:
                actor = next((role for role in roles if role.role_key == "actor"), None)
                actor_class = concepts_by_id[actor.concept_ref].semantic_class if actor else ""
                congruity_ok = actor_class in {
                    "operator_system",
                    "system_component",
                    "human_role",
                }

            bound_ordinals = {
                ordinal
                for binding in frame.role_bindings
                for ordinal in binding.word_ordinals
            }
            connectedness_ok = not unknown_refs and all(
                ordinal in known_word_ordinals for ordinal in range(len(words))
            ) and bool(bound_ordinals)
            purport_ok = frame.speech_act in {
                "definition_request",
                "comparison_request",
                "request",
                "statement",
            }

            gates = (
                _gate(
                    "expectancy",
                    expectancy_ok,
                    "FORGE-MEANING-GATE-AKANKSHA-V0",
                    () if expectancy_ok else ("required_roles_not_satisfied",),
                ),
                _gate(
                    "congruity",
                    congruity_ok,
                    "FORGE-MEANING-GATE-YOGYATA-V0",
                    () if congruity_ok else ("role_sense_incompatible_or_unknown",),
                ),
                _gate(
                    "connectedness",
                    connectedness_ok,
                    "FORGE-MEANING-GATE-SANNIDHI-V0",
                    () if connectedness_ok else ("source_coverage_or_unknown_form_hold",),
                ),
                _gate(
                    "purport",
                    purport_ok,
                    "FORGE-MEANING-GATE-TATPARYA-V0",
                    () if purport_ok else ("speech_act_purport_not_admitted",),
                ),
            )
            relation_refs = tuple(
                sorted(
                    (f"predicate:{frame.predicate_key}",)
                    + tuple(
                        f"role:{role.role_key}:{role.concept_ref}"
                        for role in roles
                        if role.concept_ref
                    )
                )
            )
            ancestry_refs = tuple(
                sorted(
                    (input_event_id,)
                    + tuple(
                        reference
                        for role in roles
                        for reference in role.source_form_refs
                    )
                )
            )
            signature = _semantic_signature(frame, roles)
            all_passed = all(gate.passed for gate in gates)
            body = {
                "semantic_signature": signature,
                "frame_candidate_ref": frame.frame_candidate_id,
                "frame_key": frame.frame_key,
                "speech_act": frame.speech_act,
                "purport": frame.purport,
                "predicate_ref": frame.predicate_ref,
                "predicate_key": frame.predicate_key,
                "negated": frame.negated,
                "roles": roles,
                "relation_refs": relation_refs,
                "ancestry_refs": ancestry_refs,
                "unknown_source_form_refs": unknown_refs,
                "gates": gates,
                "all_gates_passed": all_passed,
                "provisional": True,
                "preview_only": True,
                "selection_authority": False,
            }
            meanings.append(
                MeaningCandidate(
                    meaning_candidate_id=stable_record_id("meaning_candidate", body),
                    **body,
                )
            )
    return tuple(sorted(meanings, key=lambda item: item.meaning_candidate_id))


def _trace_step(
    sequence: int,
    operation: str,
    rule_id: str,
    operands: tuple[str, ...],
    outputs: tuple[str, ...],
    note: str,
) -> AlgebraTraceStep:
    body = {
        "sequence": sequence,
        "operation": operation,
        "rule_id": rule_id,
        "operands": operands,
        "outputs": outputs,
        "note": note,
    }
    return AlgebraTraceStep(
        trace_step_id=stable_record_id("meaning_algebra_step", body),
        **body,
    )


def _compile_inward(source_text: str) -> _InwardResult:
    limits = build_input_custody_limits(
        max_utf8_bytes=MAX_SOURCE_UTF8_BYTES,
        max_code_points=MAX_SOURCE_CODE_POINTS,
        max_recorded_conditions=256,
        allow_empty=False,
    )
    assert limits is not None
    capture = capture_input_event(
        source_text,
        source_id="forge.operator.ask_forge.language_core_preview",
        channel_id="api.operator.ask_forge.language_core_preview",
        correlation_id="forge-meaning-compiler-preview-v0",
        limits=limits,
    )
    custody = _custody_summary(capture)
    trace: list[AlgebraTraceStep] = [
        _trace_step(
            1,
            "PRESERVE_SOURCE",
            "FORGE-SOURCE-CUSTODY-V0",
            (custody.source_sha256,),
            (custody.input_event_id,) if custody.input_event_id else (),
            "Preserve exact Unicode source and byte/code-point identity.",
        )
    ]
    if capture.event is None:
        return _InwardResult(
            source_custody=custody,
            source_forms=(),
            lexical_candidates=(),
            frame_candidates=(),
            meaning_candidates=(),
            algebra_trace=tuple(trace),
            capture_valid=False,
            structural_progression_allowed=False,
            reasons=(capture.reason_code,),
        )

    forms = build_source_forms(capture.event)
    trace.append(
        _trace_step(
            2,
            "PROJECT_SOURCE_FORMS",
            "FORGE-CHARACTER-SPAN-SCAN-V0",
            (capture.event.input_event_id,),
            tuple(form.source_form_id for form in forms),
            "Project adjacent exact source spans without a model token stream.",
        )
    )
    if not capture.structural_progression_allowed:
        return _InwardResult(
            source_custody=custody,
            source_forms=forms,
            lexical_candidates=(),
            frame_candidates=(),
            meaning_candidates=(),
            algebra_trace=tuple(trace),
            capture_valid=True,
            structural_progression_allowed=False,
            reasons=(capture.reason_code,),
        )

    words = _word_forms(forms)
    lexical = _build_lexical_candidates(source_text, words)
    frames = _build_frame_candidates(source_text, words)
    structural_holds = _structural_source_holds(forms, frames)
    lexical = tuple(
        sorted(
            {item.lexical_candidate_id: item for item in lexical + structural_holds}.values(),
            key=lambda item: item.lexical_candidate_id,
        )
    )
    trace.append(
        _trace_step(
            3,
            "PROPOSE_CONCEPT_SENSES",
            "FORGE-PROVISIONAL-LEXICON-V0",
            tuple(word.source_form_id for word in words),
            tuple(item.lexical_candidate_id for item in lexical),
            "Admit declared provisional forms and retain unknowns without guessing.",
        )
    )
    trace.append(
        _trace_step(
            4,
            "BIND_PREDICATE_ROLES",
            "FORGE-BOUNDED-GRAMMAR-V0",
            tuple(item.lexical_candidate_id for item in lexical),
            tuple(frame.frame_candidate_id for frame in frames),
            "Bind predicate and participant roles under declared v0 rules.",
        )
    )
    meanings = _build_meaning_candidates(
        frames,
        lexical,
        words,
        source_text,
        capture.event.input_event_id,
    )
    trace.append(
        _trace_step(
            5,
            "COMPOSE_AND_GATE_MEANING",
            "FORGE-SYMBOLIC-MEANING-ALGEBRA-V0",
            tuple(frame.frame_candidate_id for frame in frames),
            tuple(item.meaning_candidate_id for item in meanings),
            "Compose roles and apply expectancy, congruity, connectedness, and purport.",
        )
    )
    reasons: tuple[str, ...] = ()
    if not frames:
        reasons = ("unsupported_v0_grammar",)
    elif any(item.kind is LexicalCandidateKind.UNKNOWN for item in lexical):
        reasons = ("unknown_source_forms_held",)
    return _InwardResult(
        source_custody=custody,
        source_forms=forms,
        lexical_candidates=lexical,
        frame_candidates=frames,
        meaning_candidates=meanings,
        algebra_trace=tuple(trace),
        capture_valid=True,
        structural_progression_allowed=True,
        reasons=reasons,
    )


def _mark_rmc_selection(
    evaluation: RmcContextEvaluation,
    selected_id: str,
) -> RmcContextEvaluation:
    resonances = tuple(
        replace(
            resonance,
            used_for_selection=(resonance.meaning_candidate_ref == selected_id),
        )
        for resonance in evaluation.resonances
    )
    body = {
        "snapshot": evaluation.snapshot,
        "resonances": resonances,
        "exact_reference_resonance_only": True,
        "context_used_for_selection": True,
        "memory_read_performed": False,
        "memory_write_performed": False,
    }
    return RmcContextEvaluation(
        evaluation_id=stable_record_id("rmc_context_evaluation", body),
        **body,
    )


def _select_with_context(
    candidates: tuple[MeaningCandidate, ...],
    evaluation: RmcContextEvaluation,
) -> tuple[MeaningCandidate | None, RmcContextEvaluation, str]:
    if len(candidates) == 1:
        return candidates[0], evaluation, "unique_gate_admitted_meaning"
    if len(candidates) < 2:
        return None, evaluation, "no_gate_admitted_meaning"
    totals = {candidate.meaning_candidate_id: 0 for candidate in candidates}
    for resonance in evaluation.resonances:
        if resonance.meaning_candidate_ref in totals:
            totals[resonance.meaning_candidate_ref] += resonance.resonance_count
    maximum = max(totals.values(), default=0)
    winners = tuple(key for key, value in totals.items() if value == maximum)
    if maximum > 0 and len(winners) == 1:
        selected = next(
            candidate
            for candidate in candidates
            if candidate.meaning_candidate_id == winners[0]
        )
        return selected, _mark_rmc_selection(evaluation, selected.meaning_candidate_id), "unique_exact_rmc_resonance"
    return None, evaluation, "ambiguous_meaning_requires_clarification"


def _concept_label(concept_ref: str) -> str:
    for concept in forge_seed_registry().concepts:
        if concept.concept_id == concept_ref:
            return concept.preferred_label
    return "Unknown"


def _render_candidate_wording(meaning: MeaningCandidate) -> CandidateWording:
    roles = {role.role_key: _concept_label(role.concept_ref) for role in meaning.roles}
    predicate = meaning.predicate_key
    template = ""
    text = ""
    if meaning.speech_act == "definition_request":
        template = "definition_request"
        text = f"What does {roles['definition_target']} mean?"
    elif predicate == "compare":
        template = "comparison_request"
        text = f"Compare {roles['comparison_left']} and {roles['comparison_right']}."
    elif predicate == "be":
        template = "copula_statement"
        negation = " not" if meaning.negated else ""
        text = f"{roles['subject']} is{negation} a {roles['object']}."
    elif meaning.speech_act == "request" and "actor" in roles:
        template = "modal_request"
        text = f"Can {roles['actor']} {predicate} {roles['object']}?"
    elif meaning.speech_act == "request":
        template = "imperative_request"
        text = f"Please {predicate} the {roles['object']}."
    else:
        template = "simple_statement"
        if meaning.negated:
            text = f"{roles['actor']} does not {predicate} {roles['object']}."
        else:
            inflected = {
                "use": "uses",
                "remember": "remembers",
                "store": "stores",
                "retrieve": "retrieves",
                "inspect": "inspects",
                "report": "reports",
                "explain": "explains",
                "describe": "describes",
            }.get(predicate, predicate)
            text = f"{roles['actor']} {inflected} {roles['object']}."
    body = {
        "meaning_candidate_ref": meaning.meaning_candidate_id,
        "template_key": template,
        "text": text,
        "outward_semantic_signature": meaning.semantic_signature,
        "provisional": True,
        "delivery_authorized": False,
    }
    return CandidateWording(
        wording_id=stable_record_id("candidate_wording", body),
        **body,
    )


def _echo_result(
    meaning: MeaningCandidate,
    wording_text: str,
    wording_ref: str,
) -> EchoResult:
    reparsed = _compile_inward(wording_text)
    admitted = tuple(
        candidate for candidate in reparsed.meaning_candidates if candidate.all_gates_passed
    )
    matches = tuple(
        candidate
        for candidate in admitted
        if candidate.semantic_signature == meaning.semantic_signature
    )
    passed = len(admitted) == 1 and len(matches) == 1
    reparsed_signature = admitted[0].semantic_signature if len(admitted) == 1 else ""
    body = {
        "status": EchoStatus.PASS if passed else EchoStatus.REJECT,
        "reason_code": (
            "semantic_signature_preserved"
            if passed
            else "candidate_wording_semantic_drift_or_ambiguity"
        ),
        "meaning_candidate_ref": meaning.meaning_candidate_id,
        "candidate_wording_ref": wording_ref,
        "inward_semantic_signature": meaning.semantic_signature,
        "reparsed_semantic_signature": reparsed_signature,
        "exact_signature_match": passed,
        "reparse_performed": True,
        "delivery_authorized": False,
    }
    return EchoResult(
        echo_id=stable_record_id("meaning_echo", body),
        **body,
    )


def validate_candidate_wording(
    *,
    meaning_candidate: MeaningCandidate,
    wording_text: str,
) -> EchoResult:
    """Reparse caller-supplied wording and compare its symbolic signature."""

    if type(meaning_candidate) is not MeaningCandidate:
        raise TypeError("meaning_candidate must be a MeaningCandidate")
    if type(wording_text) is not str:
        raise TypeError("wording_text must be text")
    wording_ref = stable_record_id(
        "candidate_wording_external_preview",
        {
            "meaning_candidate_ref": meaning_candidate.meaning_candidate_id,
            "text": wording_text,
        },
    )
    return _echo_result(meaning_candidate, wording_text, wording_ref)


def _not_run_echo(reason_code: str) -> EchoResult:
    body = {
        "status": EchoStatus.NOT_RUN,
        "reason_code": reason_code,
        "meaning_candidate_ref": "",
        "candidate_wording_ref": "",
        "inward_semantic_signature": "",
        "reparsed_semantic_signature": "",
        "exact_signature_match": False,
        "reparse_performed": False,
        "delivery_authorized": False,
    }
    return EchoResult(
        echo_id=stable_record_id("meaning_echo", body),
        **body,
    )


def _stage(
    sequence: int,
    stage_key: str,
    status: str,
    input_refs: tuple[str, ...],
    output_refs: tuple[str, ...],
    reasons: tuple[str, ...] = (),
) -> StageResult:
    body = {
        "sequence": sequence,
        "stage_key": stage_key,
        "status": status,
        "input_refs": input_refs,
        "output_refs": output_refs,
        "reasons": reasons,
    }
    return StageResult(
        stage_id=stable_record_id("meaning_preview_stage", body),
        **body,
    )


def _build_result(
    *,
    source_text: str,
    inward: _InwardResult,
    status: PreviewStatus,
    selected: MeaningCandidate | None,
    rmc_context: RmcContextEvaluation,
    wording: CandidateWording | None,
    echo: EchoResult,
    trace: tuple[AlgebraTraceStep, ...],
    reasons: tuple[str, ...],
) -> MeaningCompilerPreviewResult:
    boundary = meaning_compiler_preview_boundary()
    stages = (
        _stage(1, "source_custody", "COMPLETE" if inward.capture_valid else "HELD", (), (inward.source_custody.custody_result_id,), inward.reasons if not inward.capture_valid else ()),
        _stage(2, "source_form_projection", "COMPLETE" if inward.source_forms else "HELD", (inward.source_custody.input_event_id,), tuple(item.source_form_id for item in inward.source_forms)),
        _stage(3, "lexical_sense_proposal", "COMPLETE" if inward.lexical_candidates else "HELD", tuple(item.source_form_id for item in inward.source_forms), tuple(item.lexical_candidate_id for item in inward.lexical_candidates)),
        _stage(4, "predicate_role_derivation", "COMPLETE" if inward.frame_candidates else "HELD", tuple(item.lexical_candidate_id for item in inward.lexical_candidates), tuple(item.frame_candidate_id for item in inward.frame_candidates)),
        _stage(5, "symbolic_meaning_gates", "COMPLETE" if inward.meaning_candidates else "HELD", tuple(item.frame_candidate_id for item in inward.frame_candidates), tuple(item.meaning_candidate_id for item in inward.meaning_candidates)),
        _stage(6, "rmc_exact_resonance", "COMPLETE", tuple(item.meaning_candidate_id for item in inward.meaning_candidates), (rmc_context.evaluation_id,), (rmc_context.snapshot.reason_code,)),
        _stage(7, "preview_selection", "COMPLETE" if selected else "HELD", (rmc_context.evaluation_id,), (selected.meaning_candidate_id,) if selected else (), reasons if not selected else ()),
        _stage(8, "reverse_derivation", "COMPLETE" if wording else "NOT_RUN", (selected.meaning_candidate_id,) if selected else (), (wording.wording_id,) if wording else ()),
        _stage(9, "echo_comparison", echo.status.value, (wording.wording_id,) if wording else (), (echo.echo_id,), (echo.reason_code,)),
    )
    digest_body = {
        "schema_version": MEANING_COMPILER_PREVIEW_SCHEMA_VERSION,
        "status": status,
        "source_text": source_text,
        "source_custody": inward.source_custody,
        "source_forms": inward.source_forms,
        "lexical_candidates": inward.lexical_candidates,
        "frame_candidates": inward.frame_candidates,
        "algebra_trace": trace,
        "meaning_candidates": inward.meaning_candidates,
        "selected_meaning": selected,
        "rmc_context": rmc_context,
        "candidate_wording": wording,
        "echo": echo,
        "stages": stages,
        "reasons": reasons,
        "boundary": boundary,
    }
    result_digest = stable_record_id("meaning_preview_digest", digest_body)
    receipt_body = {
        "result_digest": result_digest,
        "source_sha256": inward.source_custody.source_sha256,
        "status": status,
        "deterministic": True,
        "preview_only": True,
        "writes_performed": False,
        "action_performed": False,
        "delivery_performed": False,
    }
    receipt = PreviewReceipt(
        receipt_id=stable_record_id("meaning_preview_receipt", receipt_body),
        **receipt_body,
    )
    body = {**digest_body, "receipt": receipt}
    return MeaningCompilerPreviewResult(
        result_id=stable_record_id("meaning_compiler_preview_result", body),
        **body,
    )


def compile_meaning_preview(
    source_text: str,
    *,
    rmc_snapshot: object = None,
) -> MeaningCompilerPreviewResult:
    """Compile one exact source string into a response-only meaning preview."""

    if type(source_text) is not str:
        source_text = ""
    inward = _compile_inward(source_text)
    snapshot_invalid = False
    try:
        snapshot = coerce_rmc_context_snapshot(rmc_snapshot)
    except (TypeError, ValueError):
        snapshot = build_rmc_context_snapshot()
        snapshot_invalid = True
    evaluation = evaluate_rmc_context(snapshot, inward.meaning_candidates)
    admitted = tuple(
        candidate for candidate in inward.meaning_candidates if candidate.all_gates_passed
    )
    selected: MeaningCandidate | None = None
    selection_reason = ""
    if not snapshot_invalid:
        selected, evaluation, selection_reason = _select_with_context(admitted, evaluation)

    reasons = list(inward.reasons)
    if snapshot_invalid:
        reasons.append("invalid_or_tampered_rmc_snapshot")
        selection_reason = "invalid_or_tampered_rmc_snapshot"
    if selection_reason and selection_reason not in reasons:
        reasons.append(selection_reason)

    wording: CandidateWording | None = None
    echo = _not_run_echo("no_unique_admitted_meaning")
    status = PreviewStatus.HELD
    if not inward.capture_valid:
        status = PreviewStatus.INVALID
    elif not inward.structural_progression_allowed:
        status = PreviewStatus.UNSUPPORTED
    elif not inward.frame_candidates:
        status = PreviewStatus.UNSUPPORTED
    elif selected is not None:
        wording = _render_candidate_wording(selected)
        echo = _echo_result(selected, wording.text, wording.wording_id)
        if echo.status is EchoStatus.PASS:
            status = PreviewStatus.PREVIEW_READY
        else:
            status = PreviewStatus.HELD
            reasons.append("echo_semantic_preservation_failed")
            selected = None
            wording = None
    elif admitted or inward.meaning_candidates:
        status = PreviewStatus.HELD

    trace = list(inward.algebra_trace)
    trace.append(
        _trace_step(
            len(trace) + 1,
            "RESONATE_EXACT_CONTEXT",
            "FORGE-RMC-EXACT-REFERENCE-V0",
            tuple(item.meaning_candidate_id for item in inward.meaning_candidates),
            (evaluation.evaluation_id,),
            "Use exact concept, relation, and ancestry identifiers only.",
        )
    )
    trace.append(
        _trace_step(
            len(trace) + 1,
            "SELECT_OR_HOLD",
            "FORGE-UNIQUE-MEANING-SELECTION-V0",
            (evaluation.evaluation_id,),
            (selected.meaning_candidate_id,) if selected else (),
            selection_reason or "held_before_selection",
        )
    )
    if wording is not None:
        trace.append(
            _trace_step(
                len(trace) + 1,
                "DERIVE_EXPRESSION",
                "FORGE-REVERSE-DERIVATION-V0",
                (selected.meaning_candidate_id,) if selected else (),
                (wording.wording_id,),
                "Derive wording from the selected preview meaning.",
            )
        )
        trace.append(
            _trace_step(
                len(trace) + 1,
                "ECHO_COMPARE",
                "FORGE-ECHO-SIGNATURE-V0",
                (wording.wording_id,),
                (echo.echo_id,),
                echo.reason_code,
            )
        )
    return _build_result(
        source_text=source_text,
        inward=inward,
        status=status,
        selected=selected,
        rmc_context=evaluation,
        wording=wording,
        echo=echo,
        trace=tuple(trace),
        reasons=tuple(dict.fromkeys(reasons)),
    )


__all__ = (
    "compile_meaning_preview",
    "meaning_compiler_preview_boundary",
    "validate_candidate_wording",
)
