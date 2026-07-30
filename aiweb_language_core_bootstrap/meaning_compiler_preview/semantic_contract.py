"""Canonical exact semantic-contract bindings for RMC evidence.

The contract intentionally excludes source-occurrence ancestry so one approved
meaning may be witnessed across exact alternative source forms.  It includes
every field that can materially change the proposition or communicative act:
semantic signature, speech act, purport, polarity, frame, grammar rule, and
predicate identity.
"""

from __future__ import annotations

from dataclasses import replace
import re

from .schema import (
    FrameCandidate,
    MeaningCandidate,
    SemanticContractBinding,
)


_SEMANTIC_SIGNATURE = re.compile(r"^semantic_signature:[0-9a-f]{64}$")
_PREDICATE_REF = re.compile(r"^forge_preview_predicate:[0-9a-f]{64}$")
_SYMBOLIC_LABEL = re.compile(r"^[a-z][a-z0-9_:-]{0,127}$")
_GRAMMAR_RULE = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{1,191}$")


def _symbolic_label(value: object, field: str) -> str:
    if type(value) is not str or _SYMBOLIC_LABEL.fullmatch(value) is None:
        raise ValueError(f"{field}_invalid")
    return value


def build_semantic_contract_binding(
    *,
    semantic_signature_ref: object,
    speech_act: object,
    purport: object,
    negated: object,
    frame_key: object,
    grammar_rule_ref: object,
    predicate_ref: object,
) -> SemanticContractBinding:
    """Build one immutable exact semantic contract from closed symbolic fields."""

    if (
        type(semantic_signature_ref) is not str
        or _SEMANTIC_SIGNATURE.fullmatch(semantic_signature_ref) is None
    ):
        raise ValueError("semantic_signature_ref_invalid")
    if type(negated) is not bool:
        raise TypeError("negated_must_be_boolean")
    if (
        type(grammar_rule_ref) is not str
        or _GRAMMAR_RULE.fullmatch(grammar_rule_ref) is None
    ):
        raise ValueError("grammar_rule_ref_invalid")
    if (
        type(predicate_ref) is not str
        or _PREDICATE_REF.fullmatch(predicate_ref) is None
    ):
        raise ValueError("predicate_ref_invalid")
    value = SemanticContractBinding(
        semantic_contract_id="pending",
        semantic_signature_ref=semantic_signature_ref,
        speech_act=_symbolic_label(speech_act, "speech_act"),
        purport=_symbolic_label(purport, "purport"),
        negated=negated,
        frame_key=_symbolic_label(frame_key, "frame_key"),
        grammar_rule_ref=grammar_rule_ref,
        predicate_ref=predicate_ref,
    )
    return replace(value, semantic_contract_id=value.expected_id())


def semantic_contract_for_candidate(
    candidate: MeaningCandidate,
    frame_candidates: object,
) -> SemanticContractBinding:
    """Derive a contract only from an exact candidate/frame membership pair."""

    if type(candidate) is not MeaningCandidate:
        raise TypeError("meaning_candidate_type_not_admitted")
    if type(frame_candidates) not in (tuple, list):
        raise TypeError("frame_candidates_must_be_sequence")
    frames = tuple(frame_candidates)
    if any(type(frame) is not FrameCandidate for frame in frames):
        raise TypeError("frame_candidate_type_not_admitted")
    matches = tuple(
        frame
        for frame in frames
        if frame.frame_candidate_id == candidate.frame_candidate_ref
    )
    if len(matches) != 1:
        raise ValueError("candidate_frame_membership_not_unique")
    frame = matches[0]
    if (
        frame.frame_key != candidate.frame_key
        or frame.speech_act != candidate.speech_act
        or frame.purport != candidate.purport
        or frame.predicate_ref != candidate.predicate_ref
        or frame.predicate_key != candidate.predicate_key
        or frame.negated is not candidate.negated
    ):
        raise ValueError("candidate_frame_semantic_contract_mismatch")
    return build_semantic_contract_binding(
        semantic_signature_ref=candidate.semantic_signature,
        speech_act=candidate.speech_act,
        purport=candidate.purport,
        negated=candidate.negated,
        frame_key=candidate.frame_key,
        grammar_rule_ref=frame.grammar_rule_id,
        predicate_ref=candidate.predicate_ref,
    )


__all__ = (
    "build_semantic_contract_binding",
    "semantic_contract_for_candidate",
)
