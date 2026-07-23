"""Lazy exact-source binding for the unchanged GP-014 implementation."""
from __future__ import annotations

from dataclasses import dataclass, replace
import importlib
import sys
from typing import Any, Callable

from .authority import (
    GP014_BUILD_ID,
    GP014_EXPRESSION_LEXICON_AUTHORITY_CLASS,
    GP014_MODULE_NAME,
    GP014_REALIZER_MODULE_NAME,
    GP014_REALIZER_SCHEMA_VERSION,
    GP014_SUPPORTED_OPERATION_FAMILIES,
    GP014_VERTICAL_SLICE_MODULE_NAME,
    GP015_MODULE_NAME,
)
from .canonical import stable_identifier
from .schema import Gp014BindingIdentity
from .validation import validate_binding_identity


@dataclass(frozen=True, slots=True)
class Gp014RuntimeBinding:
    identity: Gp014BindingIdentity
    answer: Callable[[str], Any]


def load_gp014_runtime_binding() -> Gp014RuntimeBinding:
    gp014 = importlib.import_module(GP014_MODULE_NAME)
    vertical = importlib.import_module(GP014_VERTICAL_SLICE_MODULE_NAME)
    realizer = importlib.import_module(GP014_REALIZER_MODULE_NAME)

    activate = getattr(gp014, "activate", None)
    answer = getattr(vertical, "answer_symbolic_math_language_request", None)
    boundary_builder = getattr(realizer, "operator_guided_language_realizer_boundary", None)
    if not callable(activate) or not callable(answer) or not callable(boundary_builder):
        raise RuntimeError("gp014_public_binding_unavailable")

    activation = activate()
    boundary = boundary_builder()
    identity = Gp014BindingIdentity(
        identity_id="pending",
        build_id=str(boundary.get("build_id", "")),
        realizer_schema_version=str(boundary.get("schema_version", "")),
        expression_lexicon_authority_class=str(boundary.get("expression_lexicon_authority_class", "")),
        supported_operation_families=tuple(sorted(str(value) for value in boundary.get("supported_operation_families", ()))),
        meaning_locked_before_phrase_selection=(boundary.get("meaning_locked_before_phrase_selection") is True and activation.get("meaning_locked_before_phrase_selection") is True),
        actual_echo_required_after_selection=(boundary.get("actual_echo_required_after_selection") is True and activation.get("actual_echo_delivery_required") is True),
        realizer_adds_delivery_authority=(boundary.get("delivery_authority_created_here") is True or activation.get("delivery_authority_added") is True),
        route_or_ui_added=(activation.get("adds_route_or_ui") is True),
        corpus_ingestion_added=(boundary.get("corpus_ingestion_added") is True or activation.get("corpus_ingestion_added") is True),
        llm_used=(boundary.get("calls_llm") is True or activation.get("calls_llm") is True),
        memory_write_added=(boundary.get("writes_memory") is True or activation.get("writes_memory") is True),
        gp015_loaded=GP015_MODULE_NAME in sys.modules,
    )
    identity = replace(identity, identity_id=stable_identifier("slice45_gp014_binding_identity", identity, excluded_fields=("identity_id",)))
    report = validate_binding_identity(identity)
    if not report.ok:
        raise RuntimeError("gp014_identity_validation_failed")
    if identity.build_id != GP014_BUILD_ID or identity.realizer_schema_version != GP014_REALIZER_SCHEMA_VERSION:
        raise RuntimeError("gp014_exact_identity_mismatch")
    if identity.expression_lexicon_authority_class != GP014_EXPRESSION_LEXICON_AUTHORITY_CLASS:
        raise RuntimeError("gp014_lexicon_authority_mismatch")
    if identity.supported_operation_families != GP014_SUPPORTED_OPERATION_FAMILIES:
        raise RuntimeError("gp014_operation_scope_mismatch")
    return Gp014RuntimeBinding(identity=identity, answer=answer)


__all__ = ("Gp014RuntimeBinding", "load_gp014_runtime_binding")
