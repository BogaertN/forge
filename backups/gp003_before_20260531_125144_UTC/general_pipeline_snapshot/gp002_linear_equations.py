"""General Learning-to-Answer Pipeline — Build GP-002 activation.

Build GP-002 adds the one-unknown linear equation domain. To keep every GP-001
file byte-for-byte untouched, GP-002 wires itself in through this single
activation entry point rather than editing the GP-001 package files.

activate() does two things, both idempotent:
  1. Registers LinearEquationOneUnknownDomain into the live domain registry.
  2. Installs a source-compiler augmentation so that instructional text which
     teaches solving equations compiles a governed procedure authorising the
     linear_equation_one_unknown domain (mirroring how GP-001 authorises its
     own domains from source fingerprints).

After activate(), the existing pipeline (learn / answer_question /
learn_and_answer) handles linear-equation questions with no other change:
parse -> manifest -> exact solve -> governed gate -> seal -> render -> Echo.

Boundaries unchanged: in-memory only, no route/UI/LLM/file-IO/memory-write.
"""

from __future__ import annotations

import re
from typing import List

from . import domains as _domains
from . import source_compiler as _sc
from .domains_equations import LinearEquationOneUnknownDomain, register as _register_domain
from .contracts import CompiledConcept, CompiledProcedure, SemanticSource, canonical_hash

GP002_BUILD_ID = "GENERAL-LEARNING-TO-ANSWER-PIPELINE-LINEAR-EQUATIONS-BUILD-GP-002"
GP002_SCHEMA_VERSION = "general_pipeline_v1_build_gp002"

_EQUATION_FINGERPRINTS = ("equation", "solve", "unknown", "variable", "both sides", "isolate")

_DOMAIN_ID = LinearEquationOneUnknownDomain.domain_id
_RELATION = LinearEquationOneUnknownDomain().relation_text()

# Keep a handle to the original compile_source so we can wrap, not replace.
_ORIGINAL_COMPILE_SOURCE = _sc.compile_source
_ACTIVATED = False


def _augment_source(source: SemanticSource, source_text: str, source_ref: str) -> SemanticSource:
    """If the text teaches equation solving, add a governed equation procedure."""
    norm = " ".join(source_text.lower().split())
    hits = [w for w in _EQUATION_FINGERPRINTS if re.search(r"\b" + re.escape(w), norm)]
    if len(hits) < 2:
        return source
    if source.supports_domain(_DOMAIN_ID):
        return source
    source.procedures.append(
        CompiledProcedure(
            procedure_id=canonical_hash({"d": _DOMAIN_ID, "s": source.source_id})[:16],
            domain=_DOMAIN_ID,
            relation_text=_RELATION,
            source_ref=source_ref,
        )
    )
    for term in hits:
        source.concepts.append(
            CompiledConcept(
                concept_id=canonical_hash({"t": term, "s": source.source_id})[:16],
                term=term,
                definition=f"term used by domain {_DOMAIN_ID}",
                source_ref=source_ref,
            )
        )
    return source


def _wrapped_compile_source(source_text: str, source_ref: str) -> SemanticSource:
    source = _ORIGINAL_COMPILE_SOURCE(source_text, source_ref)
    return _augment_source(source, source_text, source_ref)


def activate() -> bool:
    """Wire GP-002 into the live pipeline. Idempotent. Returns True if newly activated."""
    global _ACTIVATED
    if _ACTIVATED:
        return False
    _register_domain()
    # Install the wrapped compiler in both the source_compiler module and the
    # pipeline module's bound reference, so learn()/learn_and_answer() use it.
    _sc.compile_source = _wrapped_compile_source
    try:
        from . import pipeline as _pl
        _pl.compile_source = _wrapped_compile_source
    except Exception:
        pass
    _ACTIVATED = True
    return True


def is_active() -> bool:
    return _ACTIVATED


__all__ = ["activate", "is_active", "GP002_BUILD_ID", "GP002_SCHEMA_VERSION"]
